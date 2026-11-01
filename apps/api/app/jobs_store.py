from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone

from app.constants import JOB_STATUSES, STORAGE_BUCKET
from app.db import get_supabase
from app.models import CanonicalTxn, ClassificationResult

_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")


def download_filename(name: str | None, fallback: str) -> str:
    safe = _SAFE_NAME.sub("_", name or "").strip("._")
    return safe or fallback


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_bucket() -> None:
    client = get_supabase()
    try:
        client.storage.get_bucket(STORAGE_BUCKET)
        return
    except Exception:
        pass
    try:
        client.storage.create_bucket(
            STORAGE_BUCKET,
            options={"public": False, "file_size_limit": 52428800},
        )
    except Exception:
        # Bucket may already exist, or SQL insert is required — upload will fail loudly.
        pass


def normalize_client_name(name: str) -> str:
    return " ".join((name or "").split())


def match_client_row(name: str, rows: list[dict]) -> dict | None:
    needle = normalize_client_name(name).casefold()
    if not needle:
        return None
    for row in rows:
        if normalize_client_name(row.get("name") or "").casefold() == needle:
            return row
    return None


def get_or_create_client(name: str) -> dict:
    name = normalize_client_name(name) or "Unknown client"
    sb = get_supabase()
    found = sb.table("ai_clients").select("*").execute()
    existing = match_client_row(name, found.data or [])
    if existing:
        return existing
    created = sb.table("ai_clients").insert({"name": name}).execute()
    return created.data[0]


def _log_event(job_id: str, to_status: str, *, from_status: str | None, reason: str) -> None:
    get_supabase().table("ai_job_events").insert(
        {
            "job_id": job_id,
            "from_status": from_status,
            "to_status": to_status,
            "reason": reason,
        }
    ).execute()


def create_job(
    *,
    title: str,
    client_name: str,
    period: str | None = None,
    job_type: str | None = None,
    period_start: str | None = None,
    period_end: str | None = None,
) -> dict:
    if not title.strip():
        title = "Untitled job"
    client = get_or_create_client(client_name or "Unknown client")
    row = {
        "client_id": client["id"],
        "title": title.strip(),
        "status": "queued",
    }
    if period:
        row["period"] = period
    elif period_start or period_end:
        row["period"] = " / ".join(p for p in (period_start, period_end) if p)
    extra = {}
    if job_type:
        extra["job_type"] = job_type
    if period_start:
        extra["period_start"] = period_start
    if period_end:
        extra["period_end"] = period_end
    created = _insert_job({**row, **extra}) if extra else None
    if created is None and extra:
        # Keep job_type even if date columns are missing on an old schema.
        slim = {**row}
        if job_type:
            slim["job_type"] = job_type
        created = _insert_job(slim)
    if created is None:
        created = _insert_job(row)
    if created is None:
        raise RuntimeError("could not create job")
    job = created
    if job_type and not job.get("job_type"):
        set_job_type(job["id"], job_type)
        job["job_type"] = job_type
    _log_event(job["id"], "queued", from_status=None, reason="job created")
    shaped = _shape_job(job, client_name=client["name"], documents=[])
    shaped["job_type"] = job.get("job_type") or job_type
    shaped["job_type_label"] = _job_type_label(shaped.get("job_type"))
    shaped["period_start"] = job.get("period_start") or period_start
    shaped["period_end"] = job.get("period_end") or period_end
    return shaped


def _insert_job(row: dict) -> dict | None:
    try:
        created = get_supabase().table("ai_jobs").insert(row).execute()
        return (created.data or [None])[0]
    except Exception:
        return None


def set_job_type(job_id: str, job_type: str) -> None:
    try:
        get_supabase().table("ai_jobs").update(
            {"job_type": job_type, "updated_at": _now()}
        ).eq("id", job_id).execute()
    except Exception:
        pass


def delete_job(job_id: str) -> bool:
    job = get_job(job_id)
    if not job:
        return False
    sb = get_supabase()
    for doc in job.get("documents") or []:
        path = doc.get("storage_path")
        if not path:
            continue
        try:
            sb.storage.from_(STORAGE_BUCKET).remove([path])
        except Exception:
            pass
    sb.table("ai_jobs").delete().eq("id", job_id).execute()
    return True


def attach_bank_file(job_id: str, *, file_name: str, content: bytes) -> dict:
    return attach_job_file(job_id, file_name=file_name, content=content, kind="bank")


def attach_job_file(
    job_id: str,
    *,
    file_name: str,
    content: bytes,
    kind: str,
    content_type: str = "application/octet-stream",
) -> dict:
    ensure_bucket()
    safe = _SAFE_NAME.sub("_", file_name).strip("._") or "file"
    path = f"{job_id}/{kind}-{uuid.uuid4().hex[:8]}-{safe}"
    sb = get_supabase()
    sb.storage.from_(STORAGE_BUCKET).upload(
        path,
        content,
        file_options={"content-type": content_type, "upsert": "true"},
    )
    doc = (
        sb.table("ai_documents")
        .insert(
            {
                "job_id": job_id,
                "kind": kind,
                "file_name": file_name,
                "storage_path": path,
            }
        )
        .execute()
    )
    return doc.data[0]


def get_job(job_id: str) -> dict | None:
    sb = get_supabase()
    result = (
        sb.table("ai_jobs")
        .select("*, ai_clients(name), ai_documents(id, kind, file_name, storage_path, created_at)")
        .eq("id", job_id)
        .limit(1)
        .execute()
    )
    if not result.data:
        return None
    job = _shape_job_row(result.data[0])
    job["transactions"] = _job_transactions(job_id)
    job["exceptions"] = _job_exceptions(job_id)
    return _enrich_job(job)


def list_jobs() -> list[dict]:
    result = (
        get_supabase()
        .table("ai_jobs")
        .select("*, ai_clients(name), ai_documents(id, kind, file_name, storage_path, created_at)")
        .order("created_at", desc=True)
        .execute()
    )
    return [_shape_job_row(row) for row in (result.data or [])]


def list_client_names() -> list[str]:
    result = (
        get_supabase()
        .table("ai_clients")
        .select("name")
        .order("name")
        .execute()
    )
    return [row["name"] for row in (result.data or []) if row.get("name")]


def suggested_accounts_for_job(job_id: str) -> list[str]:
    job = get_job(job_id)
    if not job:
        return []
    counts: dict[str, int] = {}
    for row in job.get("transactions") or []:
        klass = (row.get("ai_transaction_classifications") or [{}])[0]
        if klass.get("needs_review"):
            continue
        name = (klass.get("account_name") or klass.get("account_code") or "").strip()
        if not name:
            continue
        counts[name] = counts.get(name, 0) + 1
    return sorted(counts.keys(), key=lambda k: (-counts[k], k.lower()))


def allowed_statuses() -> tuple[str, ...]:
    return JOB_STATUSES


def download_storage_bytes(storage_path: str) -> bytes:
    return get_supabase().storage.from_(STORAGE_BUCKET).download(storage_path)


def list_client_mappings(client_id: str | None) -> list[dict]:
    if not client_id:
        return []
    result = (
        get_supabase()
        .table("ai_mappings")
        .select("*")
        .eq("client_id", client_id)
        .execute()
    )
    return result.data or []


def seed_client_mappings(client_id: str | None, rows: list[dict]) -> int:
    """Insert comparative payee maps that this client does not already have.

    Never overwrites an accountant-approved row.
    """
    if not client_id or not rows:
        return 0
    from app.engine.payee import payee_key

    existing = list_client_mappings(client_id)
    have = {payee_key(r.get("description_pattern") or "") for r in existing}
    have.discard("")
    inserted = 0
    sb = get_supabase()
    for row in rows:
        mk = payee_key(row.get("description_pattern") or "")
        if not mk or mk in have:
            continue
        sb.table("ai_mappings").insert(
            {
                "client_id": client_id,
                "description_pattern": row.get("description_pattern"),
                "account_code": row.get("account_code") or row.get("account_name"),
                "account_name": row.get("account_name") or row.get("account_code"),
                "vat_code": row.get("vat_code") or "NV",
                "status": "approved",
            }
        ).execute()
        have.add(mk)
        inserted += 1
    return inserted


def list_client_rules(client_id: str | None, *, job_type: str | None = None) -> list[dict]:
    if not client_id:
        return []
    try:
        q = get_supabase().table("client_rules").select("*").eq("client_id", client_id)
        result = q.execute()
    except Exception:
        return []
    rows = result.data or []
    if job_type:
        rows = [r for r in rows if not r.get("job_type") or r.get("job_type") == job_type]
    return rows


def rule_flag(rules: list[dict], key: str) -> bool:
    for row in rules:
        if (row.get("rule_key") or "") == key:
            val = str(row.get("rule_value") or "").strip().lower()
            return val in {"1", "true", "yes", "on"}
    return False


def insert_job_questions(job_id: str, questions: list[str]) -> None:
    if not questions:
        return
    payload = [
        {"job_id": job_id, "transaction_id": None, "question": q, "status": "open"}
        for q in questions
    ]
    get_supabase().table("ai_exceptions").insert(payload).execute()


def save_job_intake(job_id: str, intake: dict) -> None:
    try:
        get_supabase().table("ai_jobs").update({"intake": intake, "updated_at": _now()}).eq("id", job_id).execute()
    except Exception:
        pass


def save_job_engine(job_id: str, engine: dict) -> None:
    try:
        get_supabase().table("ai_jobs").update({"engine": engine, "updated_at": _now()}).eq("id", job_id).execute()
    except Exception:
        pass


def save_job_chat(job_id: str, messages: list[dict]) -> None:
    clipped = messages[-200:]
    try:
        get_supabase().table("ai_jobs").update({"chat": clipped, "updated_at": _now()}).eq("id", job_id).execute()
        return
    except Exception:
        pass
    # Column missing: keep a copy on engine so chat still works after process.
    job = (
        get_supabase()
        .table("ai_jobs")
        .select("engine")
        .eq("id", job_id)
        .limit(1)
        .execute()
    )
    engine = dict((job.data or [{}])[0].get("engine") or {})
    engine["chat"] = clipped
    save_job_engine(job_id, engine)


def append_job_chat(job_id: str, *, role: str, text: str, extra: dict | None = None) -> None:
    job = get_job(job_id)
    if not job:
        return
    messages = list(job.get("chat") or [])
    if not messages:
        eng = job.get("engine") or {}
        messages = list(eng.get("chat") or [])
    item = {"role": role, "text": text, "at": _now()}
    if extra:
        item.update(extra)
    messages.append(item)
    save_job_chat(job_id, messages)


def set_job_status(job_id: str, status: str, *, reason: str) -> None:
    if status not in JOB_STATUSES:
        raise ValueError(f"invalid status {status}")
    sb = get_supabase()
    current = sb.table("ai_jobs").select("status").eq("id", job_id).limit(1).execute()
    from_status = (current.data or [{}])[0].get("status")
    sb.table("ai_jobs").update({"status": status, "updated_at": _now()}).eq("id", job_id).execute()
    _log_event(job_id, status, from_status=from_status, reason=reason)


def attach_output_file(
    job_id: str,
    *,
    file_name: str,
    content: bytes,
    kind: str,
    content_type: str = "application/octet-stream",
) -> dict:
    ensure_bucket()
    safe = _SAFE_NAME.sub("_", file_name).strip("._") or "output"
    path = f"{job_id}/{kind}-{uuid.uuid4().hex[:8]}-{safe}"
    sb = get_supabase()
    sb.storage.from_(STORAGE_BUCKET).upload(
        path,
        content,
        file_options={"content-type": content_type, "upsert": "true"},
    )
    doc = (
        sb.table("ai_documents")
        .insert(
            {
                "job_id": job_id,
                "kind": kind,
                "file_name": file_name,
                "storage_path": path,
            }
        )
        .execute()
    )
    return doc.data[0]


def replace_job_results(
    job_id: str,
    *,
    transactions: list[CanonicalTxn],
    classifications: list[ClassificationResult],
) -> None:
    sb = get_supabase()
    existing = sb.table("ai_transactions").select("id").eq("job_id", job_id).execute()
    ids = [row["id"] for row in (existing.data or [])]
    sb.table("ai_exceptions").delete().eq("job_id", job_id).execute()
    if ids:
        sb.table("ai_transaction_classifications").delete().in_("transaction_id", ids).execute()
        sb.table("ai_transactions").delete().eq("job_id", job_id).execute()

    if not transactions:
        return

    payload = [_txn_row(job_id, txn) for txn in transactions]
    inserted = _insert_transactions(payload)
    class_rows = []
    exception_rows = []
    for row, klass in zip(inserted, classifications, strict=True):
        class_rows.append(
            {
                "transaction_id": row["id"],
                "account_code": klass.account_code or None,
                "account_name": klass.account_name or None,
                "vat_code": klass.vat_code or None,
                "confidence": float(klass.confidence) if klass.confidence is not None else None,
                "source": klass.source if klass.source in {"mapping", "firm_rule", "llm", "human"} else "human",
                "reason": klass.reason,
                "needs_review": klass.needs_review,
            }
        )
        if klass.needs_review and klass.question:
            exception_rows.append(
                {
                    "job_id": job_id,
                    "transaction_id": row["id"],
                    "question": klass.question,
                    "status": "open",
                }
            )
    if class_rows:
        sb.table("ai_transaction_classifications").insert(class_rows).execute()
    if exception_rows:
        sb.table("ai_exceptions").insert(exception_rows).execute()


def _txn_row(job_id: str, txn: CanonicalTxn) -> dict:
    row = {
        "job_id": job_id,
        "txn_date": txn.txn_date.isoformat(),
        "description": txn.description,
        "reference": txn.reference or txn.payment_type or None,
        "amount": float(txn.amount),
        "debit_credit": txn.debit_credit,
        "source_row": txn.source_row,
        "source_page": txn.source_page,
    }
    return row


def _insert_transactions(payload: list[dict]) -> list[dict]:
    sb = get_supabase()
    try:
        result = sb.table("ai_transactions").insert(payload).execute()
        return result.data or []
    except Exception:
        stripped = [{k: v for k, v in row.items() if k != "source_page"} for row in payload]
        result = sb.table("ai_transactions").insert(stripped).execute()
        return result.data or []


def _job_transactions(job_id: str) -> list[dict]:
    result = (
        get_supabase()
        .table("ai_transactions")
        .select("*, ai_transaction_classifications(*)")
        .eq("job_id", job_id)
        .order("source_row")
        .execute()
    )
    return result.data or []


def _job_exceptions(job_id: str) -> list[dict]:
    result = (
        get_supabase()
        .table("ai_exceptions")
        .select("*")
        .eq("job_id", job_id)
        .eq("status", "open")
        .order("created_at")
        .execute()
    )
    return result.data or []


def _shape_job_row(row: dict) -> dict:
    client = row.get("ai_clients") or {}
    docs = row.get("ai_documents") or []
    return _shape_job(
        row,
        client_name=client.get("name"),
        documents=docs,
    )


def _shape_job(row: dict, *, client_name: str | None, documents: list) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "client_id": row.get("client_id"),
        "client_name": client_name,
        "status": row["status"],
        "period": row.get("period"),
        "job_type": row.get("job_type"),
        "job_type_label": _job_type_label(row.get("job_type")),
        "period_start": row.get("period_start"),
        "period_end": row.get("period_end"),
        "intake": row.get("intake"),
        "engine": row.get("engine"),
        "chat": row.get("chat") or [],
        "created_at": row.get("created_at") or _now(),
        "updated_at": row.get("updated_at"),
        "documents": documents,
    }


def _job_type_label(value: str | None) -> str:
    from app.job_intake import job_type_label

    return job_type_label(value) if value else ""


def latest_document(job: dict, kind: str) -> dict | None:
    docs = [d for d in (job.get("documents") or []) if d.get("kind") == kind]
    if not docs:
        return None
    docs.sort(key=lambda d: d.get("created_at") or "")
    return docs[-1]


def latest_working_file(job_id: str) -> dict | None:
    job = get_job(job_id)
    if not job:
        return None
    return latest_document(job, "working_file")


def load_exception_context(job_id: str, exception_id: str) -> dict | None:
    sb = get_supabase()
    found = (
        sb.table("ai_exceptions")
        .select("*")
        .eq("id", exception_id)
        .eq("job_id", job_id)
        .limit(1)
        .execute()
    )
    if not found.data:
        return None
    exception = found.data[0]
    job = get_job(job_id)
    if not job:
        return None
    txn = next(
        (row for row in job.get("transactions") or [] if row.get("id") == exception.get("transaction_id")),
        None,
    )
    klass = None
    if txn:
        classes = txn.get("ai_transaction_classifications") or []
        klass = classes[0] if classes else None
    return {
        "job": job,
        "exception": exception,
        "transaction": txn,
        "classification": klass,
    }


def approve_reason(status: str, open_count: int) -> str | None:
    """None means approve is allowed (or already approved)."""
    if status == "approved":
        return None
    if status != "ready_for_review":
        return "job is not ready for review"
    if open_count:
        return "open questions remain"
    return None


def approve_job(job_id: str) -> dict:
    job = get_job(job_id)
    if not job:
        raise ValueError("job not found")
    err = approve_reason(job.get("status") or "", count_open_exceptions(job_id))
    if err:
        raise ValueError(err)
    if job.get("status") != "approved":
        set_job_status(job_id, "approved", reason="accountant approved working file")
    approved = get_job(job_id)
    if not approved:
        raise ValueError("job not found")
    return approved


def count_open_exceptions(job_id: str) -> int:
    result = (
        get_supabase()
        .table("ai_exceptions")
        .select("id")
        .eq("job_id", job_id)
        .eq("status", "open")
        .execute()
    )
    return len(result.data or [])


def write_human_classification(
    transaction_id: str,
    *,
    exception_id: str | None,
    account_name: str,
    vat_code: str,
    reason: str,
    answer: str,
) -> None:
    sb = get_supabase()
    payload = {
        "account_code": account_name or None,
        "account_name": account_name or None,
        "vat_code": vat_code or None,
        "confidence": 1.0,
        "source": "human",
        "reason": reason,
        "needs_review": False,
    }
    existing = (
        sb.table("ai_transaction_classifications")
        .select("id")
        .eq("transaction_id", transaction_id)
        .execute()
    )
    rows = existing.data or []
    if rows:
        for row in rows:
            sb.table("ai_transaction_classifications").update(payload).eq("id", row["id"]).execute()
    else:
        payload["transaction_id"] = transaction_id
        sb.table("ai_transaction_classifications").insert(payload).execute()

    if exception_id:
        sb.table("ai_exceptions").update(
            {
                "status": "resolved",
                "answer": answer,
                "resolved_at": _now(),
            }
        ).eq("id", exception_id).execute()


def close_job_question(exception_id: str, *, answer: str) -> None:
    get_supabase().table("ai_exceptions").update(
        {
            "status": "resolved",
            "answer": answer,
            "resolved_at": _now(),
        }
    ).eq("id", exception_id).execute()


def upsert_approved_mapping(
    *,
    client_id: str,
    description: str,
    account_name: str,
    vat_code: str,
) -> None:
    from app.engine.payee import payee_key

    pattern = (description or "").split(";")[0].strip() or description.strip()
    key = payee_key(pattern)
    if not key or not account_name:
        return
    sb = get_supabase()
    existing = (
        sb.table("ai_mappings")
        .select("id, description_pattern")
        .eq("client_id", client_id)
        .execute()
    )
    matches = [
        row
        for row in (existing.data or [])
        if payee_key(row.get("description_pattern") or "") == key
    ]
    payload = {
        "account_code": account_name,
        "account_name": account_name,
        "vat_code": vat_code,
        "status": "approved",
    }
    if matches:
        for row in matches:
            sb.table("ai_mappings").update(payload).eq("id", row["id"]).execute()
        return
    payload.update(
        {
            "client_id": client_id,
            "description_pattern": pattern,
        }
    )
    sb.table("ai_mappings").insert(payload).execute()


def log_audit(job_id: str, transaction_id: str | None, event_type: str, detail: dict) -> None:
    try:
        get_supabase().table("ai_audit_log").insert(
            {
                "job_id": job_id,
                "transaction_id": transaction_id,
                "event_type": event_type,
                "detail": detail,
            }
        ).execute()
    except Exception:
        pass


def _enrich_job(job: dict) -> dict:
    from app.engine.exceptions import exception_kind
    from app.engine.payee import payee_key
    from app.ingest._util import normalize_description

    tx_by_id = {row.get("id"): row for row in job.get("transactions") or []}
    payee_counts: dict[str, int] = {}
    for row in job.get("transactions") or []:
        key = payee_key(row.get("description") or "") or normalize_description(
            row.get("description") or ""
        )
        if key:
            payee_counts[key] = payee_counts.get(key, 0) + 1

    enriched = []
    for ex in job.get("exceptions") or []:
        txn = tx_by_id.get(ex.get("transaction_id")) or {}
        klass = (txn.get("ai_transaction_classifications") or [{}])[0]
        key = payee_key(txn.get("description") or "") or normalize_description(
            txn.get("description") or ""
        )
        kind = exception_kind(ex.get("question"), klass.get("source"))
        item = dict(ex)
        item["kind"] = kind
        item["description"] = txn.get("description")
        item["amount"] = txn.get("amount")
        item["txn_date"] = txn.get("txn_date")
        item["debit_credit"] = txn.get("debit_credit")
        item["source_page"] = txn.get("source_page")
        item["proposed_account"] = klass.get("account_name") or klass.get("account_code") or ""
        item["proposed_vat"] = klass.get("vat_code") or ""
        item["confidence"] = klass.get("confidence")
        item["source"] = klass.get("source")
        item["reason"] = klass.get("reason")
        item["sibling_count"] = max(0, payee_counts.get(key, 1) - 1) if kind != "duplicate" else 0
        enriched.append(item)
    job["exceptions"] = enriched
    job["open_exception_count"] = len(enriched)
    job["transaction_count"] = len(job.get("transactions") or [])
    if not job.get("chat"):
        eng = job.get("engine") or {}
        job["chat"] = list(eng.get("chat") or [])
    try:
        job["mapping_count"] = len(list_client_mappings(job.get("client_id")))
    except Exception:
        job["mapping_count"] = 0
    return job
