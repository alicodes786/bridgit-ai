"""Resolve an exception: Accept, Override, or mark a duplicate as a repeat.

Phase 1 goal: every coding answer becomes a permanent client mapping.
Duplicates are a keep-both / repeat flag — they do not create a mapping.
Same description on this job is updated in the same click.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from app.constants import VAT_CODES
from app.engine.categorise import vat_split
from app.engine.excel_writer import write_working_file
from app.engine.exceptions import clean_account_name, exception_kind, is_duplicate_question
from app.engine.pdf_summary import build_summary_pdf
from app.ingest._util import normalize_description
from app.job_intake import parse_iso_date
from app.jobs_store import (
    attach_output_file,
    count_open_exceptions,
    download_storage_bytes,
    get_job,
    latest_document,
    load_exception_context,
    log_audit,
    set_job_status,
    upsert_approved_mapping,
    write_human_classification,
)
from app.models import CanonicalTxn, ClassificationResult, ParseResult

_ACTIONS = frozenset({"accept", "override", "exclude_repeat"})
_EXCLUDED_REASON = "excluded as repeat posting"


class ResolveError(ValueError):
    """User-facing validation error for Accept / Override."""


def resolve_exception(
    job_id: str,
    exception_id: str,
    *,
    action: str,
    account_name: str | None = None,
    vat_code: str | None = None,
) -> dict:
    action = (action or "").strip().lower()
    if action not in _ACTIONS:
        raise ResolveError("action must be accept, override, or exclude_repeat")

    ctx = load_exception_context(job_id, exception_id)
    if ctx is None:
        raise ResolveError("exception not found")
    if ctx["exception"]["status"] != "open":
        raise ResolveError("exception already resolved")

    kind = exception_kind(ctx["exception"].get("question"), (ctx["classification"] or {}).get("source"))
    if ctx["transaction"] is None:
        if kind != "missing_document":
            raise ResolveError("exception has no transaction")
        from app.jobs_store import close_job_question

        close_job_question(
            exception_id,
            answer="Carry on with the papers we have." if action == "accept" else (account_name or "noted"),
        )
        from app.engine.remember import record_resolve

        record_resolve(
            job_id,
            kind=kind,
            action=action,
            question=ctx["exception"].get("question"),
        )
        log_audit(job_id, None, "exception_resolved", {"action": action, "kind": kind, "mapping_saved": False})
        _maybe_ready(job_id)
        return get_job(job_id)

    txn = ctx["transaction"]
    klass = ctx["classification"] or {}
    job = ctx["job"]

    if action == "exclude_repeat":
        if kind != "duplicate":
            raise ResolveError("exclude_repeat is only for duplicate flags")
        write_human_classification(
            txn["id"],
            exception_id=exception_id,
            account_name="",
            vat_code="",
            reason=_EXCLUDED_REASON,
            answer="Repeat posting — left out of the working file.",
        )
        from app.engine.remember import record_resolve

        record_resolve(job_id, kind=kind, action=action, txn=txn)
        log_audit(
            job_id,
            txn["id"],
            "exception_resolved",
            {"action": action, "kind": kind, "mapping_saved": False},
        )
        _refresh_outputs(job_id)
        _maybe_ready(job_id)
        return get_job(job_id)

    name, code, save_mapping = _coding_for_action(
        action=action,
        kind=kind,
        job=job,
        txn=txn,
        klass=klass,
        account_name=account_name,
        vat_code=vat_code,
    )

    write_human_classification(
        txn["id"],
        exception_id=exception_id,
        account_name=name,
        vat_code=code,
        reason=f"Human {action}: {name} / {code}.".strip(),
        answer=f"{action}: {name} / {code}",
    )
    if kind == "duplicate":
        from app.engine.remember import record_resolve

        record_resolve(job_id, kind=kind, action=action, txn=txn)

    sibling_ids: list[str] = []
    if kind != "duplicate":
        sibling_ids = _apply_same_payee(job, txn["id"], txn["description"], name, code)

    mapping_saved = False
    if save_mapping and job.get("client_id") and name:
        upsert_approved_mapping(
            client_id=job["client_id"],
            description=txn["description"],
            account_name=name,
            vat_code=code,
        )
        mapping_saved = True

    log_audit(
        job_id,
        txn["id"],
        "exception_resolved",
        {
            "action": action,
            "kind": kind,
            "account_name": name,
            "vat_code": code,
            "mapping_saved": mapping_saved,
            "siblings": sibling_ids,
        },
    )
    _refresh_outputs(job_id)
    _maybe_ready(job_id)
    return get_job(job_id)


def _coding_for_action(
    *,
    action: str,
    kind: str,
    job: dict,
    txn: dict,
    klass: dict,
    account_name: str | None,
    vat_code: str | None,
) -> tuple[str, str, bool]:
    if action == "override":
        name = (account_name or "").strip()
        code = (vat_code or "NV").strip().upper()
        if not name:
            raise ResolveError("override needs account_name")
        if code not in VAT_CODES:
            raise ResolveError(f"vat_code must be one of {', '.join(VAT_CODES)}")
        return clean_account_name(name) or name, code, True

    if kind == "duplicate":
        name, code = _coding_from_twin(job, txn)
        if not name:
            name = (klass.get("account_name") or klass.get("account_code") or "").strip()
        if (code or "").upper() not in VAT_CODES:
            code = (klass.get("vat_code") or "NV").upper()
        if code not in VAT_CODES:
            code = "NV"
        return clean_account_name(name), code, False

    name = (klass.get("account_name") or klass.get("account_code") or "").strip()
    code = (klass.get("vat_code") or "").upper()
    if not name:
        raise ResolveError("nothing to accept — use override and type the account")
    if code not in VAT_CODES:
        code = "NV"
    cleaned = clean_account_name(name)
    return cleaned or name, code, True


def _coding_from_twin(job: dict, txn: dict) -> tuple[str, str]:
    key = (
        str(txn.get("txn_date") or "")[:10],
        str(txn.get("amount")),
        normalize_description(txn.get("description") or ""),
    )
    for row in job.get("transactions") or []:
        if row.get("id") == txn.get("id"):
            continue
        other = (
            str(row.get("txn_date") or "")[:10],
            str(row.get("amount")),
            normalize_description(row.get("description") or ""),
        )
        if other != key:
            continue
        klass = (row.get("ai_transaction_classifications") or [{}])[0]
        name = (klass.get("account_name") or klass.get("account_code") or "").strip()
        code = (klass.get("vat_code") or "NV").upper()
        if name:
            return name, code if code in VAT_CODES else "NV"
    return "", "NV"


def _apply_same_payee(
    job: dict,
    current_txn_id: str,
    description: str,
    account_name: str,
    vat_code: str,
) -> list[str]:
    from app.engine.payee import payee_key

    key = payee_key(description) or normalize_description(description)
    if not key:
        return []
    applied: list[str] = []
    ex_by_txn = {
        ex.get("transaction_id"): ex
        for ex in (job.get("exceptions") or [])
        if ex.get("transaction_id")
    }
    for row in job.get("transactions") or []:
        if row.get("id") == current_txn_id:
            continue
        other = payee_key(row.get("description") or "") or normalize_description(
            row.get("description") or ""
        )
        if other != key:
            continue
        ex = ex_by_txn.get(row["id"])
        if ex and is_duplicate_question(ex.get("question")):
            continue
        write_human_classification(
            row["id"],
            exception_id=ex["id"] if ex else None,
            account_name=account_name,
            vat_code=vat_code,
            reason="Same payee as an answer on this job.",
            answer=f"sibling of {current_txn_id}: {account_name} / {vat_code}",
        )
        applied.append(row["id"])
    return applied


def _refresh_outputs(job_id: str) -> None:
    job = get_job(job_id)
    if not job:
        return
    _refresh_excel(job)
    job = get_job(job_id) or job
    pdf = build_summary_pdf(job)
    attach_output_file(
        job_id,
        file_name=f"bridgit-summary-{job_id[:8]}.pdf",
        content=pdf,
        kind="summary_pdf",
        content_type="application/pdf",
    )


def _refresh_excel(job: dict) -> None:
    job_id = job["id"]
    doc = latest_document(job, "working_file")
    if not doc:
        return
    raw = download_storage_bytes(doc["storage_path"])
    txns, klasses = _excel_rows(job)
    rec = (job.get("engine") or {}).get("bank_rec") or {}
    opening = rec.get("opening")
    closing = rec.get("statement_closing")
    parsed = ParseResult(
        transactions=txns,
        parser="rebuild",
        opening_balance=Decimal(str(opening)) if opening is not None else None,
        closing_balance=Decimal(str(closing)) if closing is not None else None,
    )
    still = sum(1 for k in klasses if k.needs_review)
    content = write_working_file(
        parsed,
        txns,
        klasses,
        template_bytes=raw,
        job_type=job.get("job_type") or "vat_return",
        period_start=parse_iso_date(str(job.get("period_start") or "") or None),
        period_end=parse_iso_date(str(job.get("period_end") or "") or None),
        client_name=job.get("client_name"),
        notes=[
            "Updated after an accountant answer. Yellow rows still need a column."
            if still
            else "All bank lines coded. Download this file for review.",
        ],
    )
    attach_output_file(
        job_id,
        file_name=doc["file_name"],
        content=content,
        kind="working_file",
    )


def _excel_rows(job: dict) -> tuple[list[CanonicalTxn], list[ClassificationResult]]:
    txns: list[CanonicalTxn] = []
    klasses: list[ClassificationResult] = []
    for row in job.get("transactions") or []:
        klass_row = (row.get("ai_transaction_classifications") or [{}])[0]
        reason = (klass_row.get("reason") or "").lower()
        if _EXCLUDED_REASON in reason:
            continue
        txn = _txn_from_row(row)
        vat_code = klass_row.get("vat_code") or ""
        vat_amt, net_amt = vat_split(txn.amount, vat_code)
        name = klass_row.get("account_name") or klass_row.get("account_code") or ""
        conf = klass_row.get("confidence")
        klasses.append(
            ClassificationResult(
                account_code=klass_row.get("account_code") or name,
                account_name=name,
                vat_code=vat_code,
                source=klass_row.get("source") or "human",
                reason=klass_row.get("reason") or "",
                confidence=Decimal(str(conf)) if conf is not None else None,
                needs_review=bool(klass_row.get("needs_review")),
                vat_amount=vat_amt,
                net_amount=net_amt,
            )
        )
        txns.append(txn)
    return txns, klasses


def _txn_from_row(row: dict) -> CanonicalTxn:
    raw_date = row.get("txn_date")
    if isinstance(raw_date, datetime):
        txn_date = raw_date.date()
    elif isinstance(raw_date, date):
        txn_date = raw_date
    else:
        txn_date = date.fromisoformat(str(raw_date or "1970-01-01")[:10])
    return CanonicalTxn(
        txn_date=txn_date,
        description=row.get("description") or "",
        amount=Decimal(str(row.get("amount") or "0")),
        debit_credit=row.get("debit_credit") or "debit",
        payment_type=row.get("reference") or "",
        source_page=row.get("source_page"),
        source_row=row.get("source_row"),
        reference=row.get("reference") or "",
    )


def _maybe_ready(job_id: str) -> None:
    if count_open_exceptions(job_id) == 0:
        set_job_status(job_id, "ready_for_review", reason="all exceptions answered")
