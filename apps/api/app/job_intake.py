"""Job-type catalog, required documents, and the start-of-job missing-doc check.

Week 1b: know the job (client, type, period), then say what is present vs missing.
Do not hard-block — gaps become questions; processing continues if a bank file exists.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from app.models import CanonicalTxn

# Faraz official top 5 + the rest we may see on the board. Keys are stored on ai_jobs.job_type.
JOB_TYPES = (
    ("company_accounts", "Company Accounts (statutory year-end)"),
    ("vat_return", "VAT Return"),
    ("property_lettings", "Property Lettings Accounts"),
    ("sole_trader", "Sole Trader / Self Employed Accounts"),
    ("cis_accounts", "CIS Accounts"),
    ("self_assessment", "Self Assessment (employed)"),
    ("partnership_accounts", "Partnership Accounts"),
    ("management_accounts", "Management Accounts"),
    ("other", "Other"),
)

# What MA said source packs are made of. Job type decides which of these are expected.
DOC_KIND_LABELS = {
    "bank": "Bank statement / CSV covering the period",
    "comparative": "Previous period working file (comparatives / last year)",
    "purchase_invoice": "Purchase invoices / receipts",
    "sales_invoice": "Sales invoices",
    "supporting": "Other supporting documents (P60, mortgage, CIS vouchers, …)",
}

_REQUIRED = {
    "company_accounts": ("bank", "comparative"),
    "vat_return": ("bank", "comparative"),
    "property_lettings": ("bank",),
    "sole_trader": ("bank",),
    "cis_accounts": ("supporting",),  # often vouchers, sometimes no bank
    "self_assessment": ("supporting",),
    "partnership_accounts": ("bank",),
    "management_accounts": ("comparative",),
    "other": ("bank",),
}

_OPTIONAL = {
    "company_accounts": ("purchase_invoice", "sales_invoice", "supporting"),
    "vat_return": ("purchase_invoice", "sales_invoice", "comparative", "supporting"),
    "property_lettings": ("purchase_invoice", "supporting", "comparative"),
    "sole_trader": ("purchase_invoice", "sales_invoice", "comparative", "supporting"),
    "cis_accounts": ("bank", "comparative", "purchase_invoice"),
    "self_assessment": ("bank", "comparative"),
    "partnership_accounts": ("purchase_invoice", "comparative", "supporting"),
    "management_accounts": ("bank", "supporting"),
    "other": ("comparative", "purchase_invoice", "sales_invoice", "supporting"),
}


@dataclass
class MissingItem:
    kind: str
    label: str
    required: bool
    question: str


@dataclass
class IntakeResult:
    job_type: str
    period_start: date | None
    period_end: date | None
    present_kinds: list[str]
    missing: list[MissingItem] = field(default_factory=list)
    coverage_question: str | None = None

    @property
    def required_missing(self) -> list[MissingItem]:
        return [m for m in self.missing if m.required]

    def as_dict(self) -> dict:
        return {
            "job_type": self.job_type,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "present_kinds": self.present_kinds,
            "missing": [
                {
                    "kind": m.kind,
                    "label": m.label,
                    "required": m.required,
                    "question": m.question,
                }
                for m in self.missing
            ],
            "coverage_question": self.coverage_question,
            "hard_block": False,
        }


def normalize_job_type(value: str | None) -> str:
    raw = (value or "").strip().lower().replace(" ", "_").replace("-", "_")
    aliases = {
        "vat": "vat_return",
        "vat_returns": "vat_return",
        "year_end": "company_accounts",
        "yearend": "company_accounts",
        "statutory": "company_accounts",
        "company": "company_accounts",
        "lettings": "property_lettings",
        "property": "property_lettings",
        "self_employed": "sole_trader",
        "sole_trader_accounts": "sole_trader",
        "cis": "cis_accounts",
    }
    key = aliases.get(raw, raw)
    known = {k for k, _ in JOB_TYPES}
    return key if key in known else "other"


def job_type_label(value: str | None) -> str:
    key = normalize_job_type(value)
    return next((label for k, label in JOB_TYPES if k == key), key)


def effective_job_type(declared: str | None, *, yearend_pack: bool = False) -> str:
    """Year-end Excel (Banking + Bank Pay) is company accounts even if the form said VAT."""
    if yearend_pack:
        return "company_accounts"
    return normalize_job_type(declared)


def required_kinds(job_type: str) -> tuple[str, ...]:
    return _REQUIRED.get(normalize_job_type(job_type), ("bank",))


def optional_kinds(job_type: str) -> tuple[str, ...]:
    return _OPTIONAL.get(normalize_job_type(job_type), ())


def present_kinds(documents: list[dict] | None) -> list[str]:
    kinds = []
    for doc in documents or []:
        kind = (doc.get("kind") or "").strip()
        if kind and kind not in kinds and kind not in {"working_file", "summary_pdf"}:
            kinds.append(kind)
    return kinds


def check_missing_documents(
    *,
    job_type: str,
    documents: list[dict] | None,
    period_start: date | None = None,
    period_end: date | None = None,
) -> IntakeResult:
    """Ask for gaps. Never hard-block. Required items are still listed as questions."""
    job_type = normalize_job_type(job_type)
    present = present_kinds(documents)
    missing: list[MissingItem] = []
    for kind in required_kinds(job_type):
        if kind in present:
            continue
        label = DOC_KIND_LABELS[kind]
        period_bit = ""
        if kind == "bank" and (period_start or period_end):
            period_bit = (
                f" for {period_start.isoformat() if period_start else '?'} to "
                f"{period_end.isoformat() if period_end else '?'}"
            )
        missing.append(
            MissingItem(
                kind=kind,
                label=label,
                required=True,
                question=(
                    f"Missing document: {label}{period_bit}. "
                    "Can you send it, or should Bridgit carry on with what we have?"
                ),
            )
        )
    for kind in optional_kinds(job_type):
        if kind in present or kind in required_kinds(job_type):
            continue
        label = DOC_KIND_LABELS[kind]
        missing.append(
            MissingItem(
                kind=kind,
                label=label,
                required=False,
                question=(
                    f"Usually useful, not on this job yet: {label}. "
                    "Send it if you have it — Bridgit will carry on without it."
                ),
            )
        )
    return IntakeResult(
        job_type=job_type,
        period_start=period_start,
        period_end=period_end,
        present_kinds=present,
        missing=missing,
    )


def period_coverage_question(
    transactions: list[CanonicalTxn],
    *,
    period_start: date | None,
    period_end: date | None,
) -> str | None:
    """Qasim's example: statement ends 18 Aug, VAT quarter needs 31 Aug."""
    if not transactions or period_end is None:
        return None
    last = max(t.txn_date for t in transactions)
    first = min(t.txn_date for t in transactions)
    parts = []
    if last < period_end:
        parts.append(
            f"Bank lines end {last:%d %b %Y} but this job's period ends {period_end:%d %b %Y}."
        )
    if period_start is not None and first > period_start:
        parts.append(
            f"Bank lines start {first:%d %b %Y} but this job's period starts {period_start:%d %b %Y}."
        )
    if not parts:
        return None
    return (
        " ".join(parts)
        + " Missing days in the period — send the rest of the statement, or confirm Bridgit should continue?"
    )


def parse_iso_date(value: str | None) -> date | None:
    text = (value or "").strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
_EXCEL_EXT = {".xlsx", ".xlsm"}
_BANK_NAME = re.compile(
    r"\b(bank|statement|countingup|starling|transactions|paid.?in)\b", re.I
)
_COMP_NAME = re.compile(
    r"(comparative|year.?end|prior.?year|last.?year|working.?file)", re.I
)


def classify_upload(file_name: str, content: bytes) -> str:
    """Same kinds as New job: bank, comparative, or supporting.

    Chat-bar files after the job exists use this so Bridgit processes a late
    bank CSV / last-year Excel the same way as the first upload. Extra papers
    are stored; they are not OCR'd yet.
    """
    name = file_name or "file"
    suffix = Path(name).suffix.lower()
    if suffix in _IMAGE_EXT:
        return "supporting"
    if suffix in _EXCEL_EXT or (content[:2] == b"PK"):
        from app.engine.yearend_map import is_yearend_pack

        if is_yearend_pack(content):
            return "comparative"
        if _COMP_NAME.search(name):
            return "comparative"
    if suffix in {".csv", ".txt"} or suffix in _EXCEL_EXT or suffix == ".pdf" or content[:4] == b"%PDF":
        if _looks_like_bank_bytes(name, content):
            return "bank"
    if _BANK_NAME.search(name):
        return "bank"
    if _COMP_NAME.search(name):
        return "comparative"
    return "supporting"


def _looks_like_bank_bytes(file_name: str, content: bytes) -> bool:
    try:
        from app.ingest import parse_bank_file

        parsed = parse_bank_file(file_name, content)
    except Exception:
        return False
    txns = parsed.transactions or []
    if not txns:
        return False
    if parsed.opening_balance is not None or parsed.closing_balance is not None:
        return True
    if any(getattr(t, "running_balance", None) is not None for t in txns):
        return True
    return len(txns) >= 3


def kind_label(kind: str) -> str:
    return {
        "bank": "bank statement",
        "comparative": "last year / comparative Excel",
        "supporting": "supporting paper",
        "purchase_invoice": "purchase invoice",
        "sales_invoice": "sales invoice",
    }.get(kind, kind)
