"""Keep accountant answers when a job is processed again.

Re-uploading the same bank file used to wipe duplicates and period-coverage
questions. Those are not payee mappings, so they have to live on the job.
"""

from __future__ import annotations

from decimal import Decimal

from app.ingest._util import normalize_description
from app.job_intake import DOC_KIND_LABELS
from app.jobs_store import get_job, save_job_engine
from app.models import CanonicalTxn

_EXCLUDED = "excluded as repeat posting"


def amount_key(amount) -> str:
    return str(Decimal(str(amount or "0")).quantize(Decimal("0.01")))


def duplicate_key(txn: CanonicalTxn) -> str:
    return f"{txn.txn_date.isoformat()}|{amount_key(txn.amount)}|{normalize_description(txn.description)}"


def duplicate_key_row(row: dict) -> str:
    raw = str(row.get("txn_date") or "")[:10]
    return f"{raw}|{amount_key(row.get('amount'))}|{normalize_description(row.get('description') or '')}"


def load(job: dict | None) -> dict:
    rem = dict(((job or {}).get("engine") or {}).get("remembered") or {})
    rem.setdefault("coverage_ok", False)
    rem.setdefault("waived_kinds", [])
    rem.setdefault("duplicates", {})
    return rem


def persist(job_id: str, remembered: dict) -> None:
    job = get_job(job_id) or {}
    engine = dict(job.get("engine") or {})
    engine["remembered"] = {
        "coverage_ok": bool(remembered.get("coverage_ok")),
        "waived_kinds": list(remembered.get("waived_kinds") or []),
        "duplicates": dict(remembered.get("duplicates") or {}),
    }
    save_job_engine(job_id, engine)


def record_resolve(
    job_id: str,
    *,
    kind: str,
    action: str,
    question: str | None = None,
    txn: dict | None = None,
) -> None:
    rem = load(get_job(job_id))
    if kind == "missing_document":
        q = (question or "").lower()
        if "missing days in the period" in q:
            rem["coverage_ok"] = True
        else:
            waived = list(rem.get("waived_kinds") or [])
            for doc_kind, label in DOC_KIND_LABELS.items():
                if label.lower() in q and doc_kind not in waived:
                    waived.append(doc_kind)
            rem["waived_kinds"] = waived
    if kind == "duplicate" and txn:
        dups = dict(rem.get("duplicates") or {})
        dups[duplicate_key_row(txn)] = (
            "exclude_repeat" if action == "exclude_repeat" else "keep_both"
        )
        rem["duplicates"] = dups
    persist(job_id, rem)


def duplicate_decision(remembered: dict | None, txn: CanonicalTxn) -> str | None:
    dups = (remembered or {}).get("duplicates") or {}
    return dups.get(duplicate_key(txn))
