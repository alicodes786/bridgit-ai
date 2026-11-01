"""Exception kinds for the Phase 1 review loop."""

from __future__ import annotations

import re

_PERSONAL = re.compile(r"\s*\(personal\??\)", re.IGNORECASE)
_REVIEW_DASH = re.compile(r"\s*[\u2013\u2014-]\s*REVIEW\b.*$", re.IGNORECASE)
_REVIEW_WORD = re.compile(r"\s+REVIEW\b.*$", re.IGNORECASE)


def is_duplicate_question(question: str | None) -> bool:
    q = (question or "").lower()
    return "matches line" in q or "keep both" in q or "repeat?" in q


def exception_kind(question: str | None, source: str | None) -> str:
    q = (question or "").lower()
    if q.startswith("missing document") or q.startswith("usually useful") or "missing days in the period" in q:
        return "missing_document"
    if is_duplicate_question(question):
        return "duplicate"
    if source == "mapping":
        return "mapping_review"
    if source == "llm":
        return "llm"
    return "unknown"


def clean_account_name(name: str | None) -> str:
    """Drop workbook REVIEW flags so an Accept cannot silent-apply a review code later."""
    text = (name or "").strip()
    text = _PERSONAL.sub("", text)
    text = _REVIEW_DASH.sub("", text)
    text = _REVIEW_WORD.sub("", text)
    return " ".join(text.split())
