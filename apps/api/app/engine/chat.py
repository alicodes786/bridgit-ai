"""Accountant chat on a job: answer questions in prose, or ask Bridgit.

Order: (1) interpret as a coding answer against open questions
(2) answer from this job's mappings / rec / lines
(3) Claude, grounded on that same context. Never invent a coding action
without an open exception id that still exists.
"""

from __future__ import annotations

import json
import logging
import re

from app.config import settings
from app.constants import VAT_CODES
from app.engine.payee import payee_key
from app.engine.resolve import ResolveError, resolve_exception
from app.jobs_store import (
    append_job_chat,
    get_job,
    list_client_mappings,
    suggested_accounts_for_job,
)

log = logging.getLogger(__name__)

_MODEL = "claude-sonnet-4-5"
_MAX_MESSAGE = 4000

BRIDGIT_IDENTITY = """You are Bridgit, the bookkeeping agent for MA Associates.
You talk to the accountants on that team (including Faraz). You are a colleague, not a chatbot and not a form.
Your job is bank coding: read the bank file, reuse payees this client already taught you, ask only where you are unsure, and keep the working Excel up to date.
The download is the bank working file (Banking, Bank Pay, Bank Rec). It is not the statutory pack, the extended trial balance, or a filed return.
Rules:
- Use only the facts in this message and the recent turns. If a number, payee, or status is not there, say you do not have it.
- Never invent amounts, line counts, payees, accounts, or exception ids.
- Do not guess a coding in silence. An open question is answered only when the accountant is clearly deciding it.
- Coding one bank line happens inside that job. On the home desk, point them to the job.
- Stay on this bookkeeping work. If they ask something outside it, say that is outside what you can see and bring them back to the jobs.
- ASCII hyphen only. Never an em dash.
"""

_KEEP_BOTH = re.compile(r"\b(keep both|both are (real|ok)|not a (repeat|duplicate))\b", re.I)
_REPEAT = re.compile(r"\b(repeat|duplicate|exclude)\b", re.I)
_CARRY = re.compile(r"\b(carry on|continue without|skip (it|this)|don'?t have it)\b", re.I)


class ChatError(ValueError):
    pass


def handle_chat(job_id: str, message: str) -> dict:
    text = (message or "").strip()
    if not text:
        raise ChatError("Type a message first.")
    if len(text) > _MAX_MESSAGE:
        raise ChatError("Message is too long.")

    job = get_job(job_id)
    if not job:
        raise ChatError("job not found")

    append_job_chat(job_id, role="user", text=text)

    accounts = suggested_accounts_for_job(job_id)
    mappings = list_client_mappings(job.get("client_id"))
    exceptions = list(job.get("exceptions") or [])

    intent = match_resolve_intent(text, exceptions, accounts)
    if intent is None:
        intent = _llm_intent(text, job, exceptions, accounts, mappings)

    reply = ""
    source = "job"
    if intent and intent.get("intent") == "resolve" and intent.get("exception_id"):
        try:
            job = resolve_exception(
                job_id,
                intent["exception_id"],
                action=intent.get("action") or "override",
                account_name=intent.get("account_name"),
                vat_code=intent.get("vat_code"),
            )
            left = len(job.get("exceptions") or [])
            account = (intent.get("account_name") or "").strip()
            payee = ""
            for ex in exceptions:
                if ex.get("id") == intent["exception_id"]:
                    payee = (ex.get("description") or "").split(";")[0].strip()[:48]
                    break
            left_bit = f"{left} question{'s' if left != 1 else ''} left."
            if intent.get("action") == "exclude_repeat":
                reply = f"Marked as a repeat. {left_bit}"
            elif account and payee:
                reply = (
                    f"Saved. I will remember {payee} as {account} for this client. {left_bit}"
                )
            else:
                reply = (intent.get("reply") or "Saved.") + " " + left_bit
            source = "resolve"
        except ResolveError as exc:
            reply = str(exc)
            source = "resolve_error"
            job = get_job(job_id)
    else:
        grounded = answer_from_job(text, job, mappings, accounts)
        if grounded:
            reply = grounded
            source = "knowledge"
        elif intent and intent.get("reply"):
            reply = intent["reply"]
            source = "llm"
        else:
            reply = _llm_answer(text, job, exceptions, accounts, mappings) or (
                "I can talk through this job with you: what is coded, what is still open, "
                "the files on it, and whether the working Excel is ready. "
                "If you want a line coded, name the payee and the column."
            )
            source = "llm" if reply else "fallback"
        job = get_job(job_id)

    reply = _no_em(reply)
    append_job_chat(job_id, role="assistant", text=reply, extra={"source": source})
    fresh = get_job(job_id)
    return {"reply": reply, "source": source, "job": fresh}


def match_resolve_intent(
    message: str,
    exceptions: list[dict],
    accounts: list[str],
) -> dict | None:
    """Map accountant prose onto one open exception. None if it is a question."""
    if not exceptions:
        return None
    text = message.strip()
    low = text.lower()

    if _looks_like_question(low):
        return None

    mentioned = [ex for ex in exceptions if _mentions_exception(low, ex)]
    target = None
    if len(mentioned) == 1:
        target = mentioned[0]
    elif len(mentioned) == 0:
        target = _first_compatible(exceptions, low, accounts)
    else:
        return None
    if not target:
        return None

    kind = target.get("kind") or "unknown"
    eid = target.get("id")
    if kind == "duplicate":
        if _KEEP_BOTH.search(text):
            return {"intent": "resolve", "exception_id": eid, "action": "accept", "reply": "Keeping both lines."}
        if _REPEAT.search(text):
            return {
                "intent": "resolve",
                "exception_id": eid,
                "action": "exclude_repeat",
                "reply": "Marked as a repeat. Left out of the working file.",
            }
        return None
    if kind == "missing_document":
        if _CARRY.search(text) or low in {"ok", "yes", "skip", "continue"}:
            return {
                "intent": "resolve",
                "exception_id": eid,
                "action": "accept",
                "reply": "Noted. Carrying on without that paper.",
            }
        return None

    account = _match_account(text, accounts, target)
    if not account:
        return None
    vat = _match_vat(text) or (target.get("proposed_vat") or "NV")
    action = "accept" if account == (target.get("proposed_account") or "").strip() else "override"
    return {
        "intent": "resolve",
        "exception_id": eid,
        "action": action,
        "account_name": account,
        "vat_code": vat,
        "reply": f"Coded to {account} ({vat}).",
    }


def answer_from_job(
    message: str,
    job: dict,
    mappings: list[dict],
    accounts: list[str],
) -> str | None:
    low = message.lower()
    eng = job.get("engine") or {}
    rec = eng.get("bank_rec") or {}
    open_ex = job.get("exceptions") or []

    if any(
        w in low
        for w in (
            "working file",
            "excel ready",
            "processed yet",
            "not started",
            "is it ready",
        )
    ) or (low.startswith("is our") and "ready" in low):
        err = eng.get("last_error")
        status = job.get("status")
        n = job.get("transaction_count") or len(job.get("transactions") or [])
        if err or (status == "queued" and not n):
            if err:
                return (
                    "Not yet. Processing did not finish, so there is no working file. "
                    "Open Cards and click Retry process."
                )
            return (
                "Not yet. The bank file is uploaded but Bridgit has not coded the lines. "
                "Open Cards and click Process now."
            )
        if status == "processing":
            return "Still working through the bank file. Refresh in a moment."
        if n:
            return (
                f"Yes - {n} bank lines are on this job. Download Excel from the header. "
                "That file is the bank working file, not a finished statutory pack."
            )
        return "No working file yet. Upload the bank file and click Process now."

    if any(
        w in low
        for w in (
            "what files",
            "what did i upload",
            "what have i uploaded",
            "which files",
        )
    ):
        papers = [
            d
            for d in (job.get("documents") or [])
            if d.get("kind") not in {"working_file", "summary_pdf"}
        ]
        if not papers:
            return "No source files on this job yet. Attach the bank CSV (and last year Excel for year-end) in the chat bar."
        bits = [
            f"{d.get('file_name') or d.get('kind')} ({d.get('kind')})"
            for d in papers[-12:]
        ]
        return "On this job: " + "; ".join(bits) + "."

    if any(w in low for w in ("what do you know", "how many mapping", "remembered", "what have you learned")):
        n = len(mappings)
        if not n:
            return "Nothing saved for this client yet. Each coding answer you give is stored and reused on the next job."
        sample = [
            f"{m.get('description_pattern')} → {m.get('account_name') or m.get('account_code')}"
            for m in mappings[:8]
        ]
        extra = " Examples: " + "; ".join(sample) + "." if sample else ""
        return (
            f"I have {n} saved payee coding{'s' if n != 1 else ''} for this client. "
            f"Answers you give here are added to that list.{extra}"
        )

    if any(w in low for w in ("how many question", "what's left", "whats left", "still open", "left to answer")):
        n = len(open_ex)
        if not n:
            return "No open questions on this job. You can download the Excel."
        labels = [_short_label(e) for e in open_ex[:8]]
        extra = " " + "; ".join(labels) if labels else ""
        return f"{n} question{'s' if n != 1 else ''} still open.{extra}"

    if "bank rec" in low or "reconcil" in low or "does it tie" in low:
        if rec.get("difference") is None:
            return "I do not have a bank rec figure stored on this job yet."
        diff = rec.get("difference")
        if rec.get("ok"):
            return f"Bank rec ties. Difference £{diff}."
        return (
            f"Bank rec does not tie. Difference £{diff}. "
            f"Opening £{rec.get('opening')}, receipts £{rec.get('receipts')}, "
            f"payments £{rec.get('payments')}, statement close £{rec.get('statement_closing')}."
        )

    if any(w in low for w in ("what did you code", "auto-cod", "matched last year", "how many lines")):
        n = job.get("transaction_count") or len(job.get("transactions") or [])
        coded = eng.get("coded")
        asked = eng.get("exceptions")
        return (
            f"{n} bank lines. "
            + (f"{coded} coded automatically. " if coded is not None else "")
            + (f"{asked} needed a decision when I last processed." if asked is not None else "")
        ).strip()

    needle = payee_key(message) or ""
    if needle and len(needle) >= 3:
        hits = [
            m
            for m in mappings
            if needle in payee_key(m.get("description_pattern") or "")
            or payee_key(m.get("description_pattern") or "") in needle
        ]
        if len(hits) == 1:
            m = hits[0]
            return (
                f"Last saved coding for {m.get('description_pattern')} is "
                f"{m.get('account_name') or m.get('account_code')} "
                f"({m.get('vat_code') or 'NV'})."
            )

    if "which account" in low or "what columns" in low or "chart" in low:
        if not accounts:
            return "No accounts collected on this job yet. Code a few lines and I will reuse those names."
        return "Accounts already used on this job: " + ", ".join(accounts[:20]) + "."

    return None


def _first_compatible(exceptions: list[dict], low: str, accounts: list[str]) -> dict | None:
    if _KEEP_BOTH.search(low) or _REPEAT.search(low):
        dups = [e for e in exceptions if e.get("kind") == "duplicate"]
        return dups[0] if len(dups) == 1 else None
    if _CARRY.search(low):
        docs = [e for e in exceptions if e.get("kind") == "missing_document"]
        return docs[0] if docs else None
    if _match_account(low, accounts, None):
        coding = [e for e in exceptions if e.get("kind") not in {"duplicate", "missing_document"}]
        return coding[0] if coding else None
    return None


def _mentions_exception(low: str, ex: dict) -> bool:
    desc = (ex.get("description") or "") + " " + (ex.get("question") or "")
    key = payee_key(ex.get("description") or "")
    tokens = [t for t in re.split(r"[^a-z0-9]+", (key or desc).lower()) if len(t) >= 4]
    if key and len(key) >= 3 and key.lower() in low:
        return True
    hits = sum(1 for t in tokens if t in low)
    return hits >= 2 or (hits == 1 and len(tokens) <= 2)


def _match_account(text: str, accounts: list[str], target: dict | None) -> str | None:
    low = text.lower()
    ranked = sorted({a.strip() for a in accounts if a and a.strip()}, key=len, reverse=True)
    proposed = ((target or {}).get("proposed_account") or "").strip()
    if proposed and proposed not in ranked:
        ranked = [proposed] + ranked
    for name in ranked:
        if name.lower() in low:
            return name
    # Whole message is the account (Faraz types just "Motor")
    compact = " ".join(low.split())
    for name in ranked:
        if compact == name.lower():
            return name
    return None


def _match_vat(text: str) -> str | None:
    up = text.upper()
    for code in VAT_CODES:
        if re.search(rf"\b{code}\b", up):
            return code
    if "standard" in text.lower() or "20%" in text:
        return "SR"
    return None


def _looks_like_question(low: str) -> bool:
    if low.endswith("?"):
        return True
    return bool(re.match(r"^(why|what|who|how|when|where|can you|could you|explain|tell me)\b", low))


def _short_label(ex: dict) -> str:
    desc = (ex.get("description") or "").strip()
    if desc:
        return desc.split(";")[0][:40]
    q = (ex.get("question") or "")[:40]
    return q or "item"


def _no_em(text: str) -> str:
    return (text or "").replace("\u2014", "-").replace("\u2013", "-")


def _job_facts(job: dict, exceptions: list[dict], accounts: list[str], mappings: list[dict]) -> dict:
    eng = job.get("engine") or {}
    rec = eng.get("bank_rec") or {}
    return {
        "client": job.get("client_name"),
        "title": job.get("title"),
        "job_type": job.get("job_type_label") or job.get("job_type"),
        "status": job.get("status"),
        "last_error": eng.get("last_error"),
        "processed": bool(eng.get("processed_at")),
        "lines": job.get("transaction_count") or len(job.get("transactions") or []),
        "coded": eng.get("coded"),
        "bank_rec": rec,
        "open_questions": [
            {
                "id": e.get("id"),
                "kind": e.get("kind"),
                "question": e.get("question"),
                "description": e.get("description"),
                "proposed_account": e.get("proposed_account"),
                "proposed_vat": e.get("proposed_vat"),
            }
            for e in exceptions[:20]
        ],
        "accounts_on_this_job": accounts[:30],
        "saved_mappings": [
            {
                "payee": m.get("description_pattern"),
                "account": m.get("account_name") or m.get("account_code"),
                "vat": m.get("vat_code"),
            }
            for m in mappings[:40]
        ],
        "mapping_count": len(mappings),
        "recent_chat": [
            {"role": m.get("role"), "text": (m.get("text") or "")[:400]}
            for m in (job.get("chat") or [])[-8:]
        ],
        "uploaded": [
            {"kind": d.get("kind"), "file": d.get("file_name")}
            for d in (job.get("documents") or [])
            if d.get("kind") not in {"working_file", "summary_pdf"}
        ],
    }


def _parse_json(text: str) -> dict:
    raw = (text or "").strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    return json.loads(raw)


def _llm_intent(
    message: str,
    job: dict,
    exceptions: list[dict],
    accounts: list[str],
    mappings: list[dict],
) -> dict | None:
    if not settings.anthropic_api_key.strip():
        return None
    facts = _job_facts(job, exceptions, accounts, mappings)
    prior = []
    for turn in (job.get("chat") or [])[-8:]:
        bit = (turn.get("text") or "").strip()
        if not bit or bit == message.strip():
            continue
        prior.append({"role": turn.get("role") or "user", "text": bit[:600]})
    prompt = f"""This message is about ONE open job. Talk naturally about it.
saved_mappings are permanent for this client and are reused next time.
If they are clearly answering one open question, set intent=resolve and copy that exception id.
Otherwise intent=answer and put the reply in reply.
VAT codes: SR ZR EX NV OS.

Recent turns:
{json.dumps(prior, ensure_ascii=True)}

Facts:
{json.dumps(facts, ensure_ascii=True)}

Accountant:
{message}

Return JSON only:
{{"intent":"resolve"|"answer","exception_id":null,"action":"accept"|"override"|"exclude_repeat"|null,"account_name":"","vat_code":"NV","reply":""}}
"""
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key.strip())
        message_out = client.messages.create(
            model=_MODEL,
            max_tokens=800,
            system=BRIDGIT_IDENTITY,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(
            block.text for block in message_out.content if getattr(block, "type", "") == "text"
        )
        data = _parse_json(text)
    except Exception:
        log.exception("chat llm intent failed")
        return None
    if not isinstance(data, dict):
        return None
    intent = (data.get("intent") or "answer").strip().lower()
    eid = data.get("exception_id")
    open_ids = {e.get("id") for e in exceptions}
    if intent == "resolve":
        if eid not in open_ids:
            return {"intent": "answer", "reply": data.get("reply") or ""}
        action = (data.get("action") or "override").strip().lower()
        if action not in {"accept", "override", "exclude_repeat"}:
            action = "override"
        return {
            "intent": "resolve",
            "exception_id": eid,
            "action": action,
            "account_name": (data.get("account_name") or "").strip() or None,
            "vat_code": (data.get("vat_code") or "NV").strip().upper(),
            "reply": data.get("reply") or "",
        }
    return {"intent": "answer", "reply": data.get("reply") or ""}


def portfolio_digest(jobs: list[dict]) -> list[dict]:
    """Short facts for a conversation that is not pinned to one job."""
    rows = []
    for job in jobs[:30]:
        eng = job.get("engine") or {}
        rec = eng.get("bank_rec") or {}
        papers = [
            d.get("file_name") or d.get("kind")
            for d in (job.get("documents") or [])
            if d.get("kind") not in {"working_file", "summary_pdf"}
        ]
        rows.append({
            "id": job.get("id"),
            "title": job.get("title"),
            "client": job.get("client_name"),
            "status": job.get("status"),
            "type": job.get("job_type_label") or job.get("job_type"),
            "period_start": job.get("period_start"),
            "period_end": job.get("period_end"),
            "coded": eng.get("coded"),
            "open_questions": eng.get("exceptions"),
            "bank_rec_ok": rec.get("ok"),
            "bank_rec_difference": rec.get("difference"),
            "files": papers[:8],
        })
    return rows


def workspace_fallback(message: str, jobs: list[dict]) -> str:
    digest = portfolio_digest(jobs)
    if not digest:
        return (
            "There are no jobs yet. Start one with a bank file and, for year-end, last year's Excel. "
            "You can keep talking here even before a job exists."
        )
    low = (message or "").lower()
    waiting = [r for r in digest if r.get("status") == "needs_input"]
    ready = [r for r in digest if r.get("status") in {"ready_for_review", "approved"}]
    if any(w in low for w in ("how are", "summary", "summar", "where are we", "what's going", "whats going", "status")):
        bits = [
            f"{len(digest)} job{'s' if len(digest) != 1 else ''} on the desk.",
            f"{len(waiting)} still need an answer." if waiting else "Nothing is waiting on a question.",
            f"{len(ready)} working file{'s' if len(ready) != 1 else ''} ready to download." if ready else "No working file is ready yet.",
        ]
        names = ", ".join(f"{r.get('client') or 'Client'} ({r.get('title')})" for r in digest[:5])
        return " ".join(bits) + " Recent: " + names + "."
    for row in digest:
        client = (row.get("client") or "").lower()
        title = (row.get("title") or "").lower()
        if client and client in low or (title and title in low):
            open_n = row.get("open_questions")
            rec = "ties" if row.get("bank_rec_ok") else (
                f"difference {row.get('bank_rec_difference')}" if row.get("bank_rec_difference") is not None else "not checked"
            )
            files = ", ".join(row.get("files") or []) or "none listed"
            return (
                f"{row.get('title')} for {row.get('client')} is {row.get('status')}. "
                f"Coded lines recorded: {row.get('coded') if row.get('coded') is not None else 'unknown'}. "
                f"Open questions recorded: {open_n if open_n is not None else 'unknown'}. "
                f"Bank check: {rec}. Files: {files}. "
                "Open that job in the sidebar if you want to code a line or download the working Excel."
            )
    return (
        f"I can see {len(digest)} job{'s' if len(digest) != 1 else ''}. "
        "Ask how things are going, or name a client. "
        "Coding a single line happens inside that job. "
        "The download is the bank working file, not the statutory pack."
    )


def handle_workspace_chat(message: str, history: list[dict] | None = None) -> str:
    """Conversation across the desk. Does not require a job to be open."""
    from app.jobs_store import list_jobs

    text = (message or "").strip()
    if not text:
        raise ChatError("Type a message first.")
    if len(text) > _MAX_MESSAGE:
        raise ChatError("Message is too long.")
    jobs = list_jobs()
    digest = portfolio_digest(jobs)
    if not settings.anthropic_api_key.strip():
        return _no_em(workspace_fallback(text, jobs))
    prior = []
    for turn in (history or [])[-10:]:
        bit = (turn.get("text") or "").strip()
        role = turn.get("role") or "user"
        if bit:
            prior.append({"role": role, "text": bit[:600]})
    prompt = f"""No single job is open. This is the whole desk.
Talk about any of these jobs. If they want a line coded, tell them to open that job.

Recent turns:
{json.dumps(prior, ensure_ascii=True)}

Jobs:
{json.dumps(digest, ensure_ascii=True)}

Accountant:
{text}
"""
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key.strip())
        message_out = client.messages.create(
            model=_MODEL,
            max_tokens=900,
            system=BRIDGIT_IDENTITY,
            messages=[{"role": "user", "content": prompt}],
        )
        out = "".join(
            block.text for block in message_out.content if getattr(block, "type", "") == "text"
        ).strip()
        if out:
            return _no_em(out)
    except Exception:
        log.exception("workspace chat failed")
    return _no_em(workspace_fallback(text, jobs))


def _llm_answer(
    message: str,
    job: dict,
    exceptions: list[dict],
    accounts: list[str],
    mappings: list[dict],
) -> str | None:
    parsed = _llm_intent(message, job, exceptions, accounts, mappings)
    if parsed and parsed.get("reply"):
        return str(parsed["reply"])
    return None


