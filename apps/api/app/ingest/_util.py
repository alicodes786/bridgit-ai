from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

_DATE_FORMATS = (
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%Y-%m-%d",
    "%d/%m/%y",
    "%d %b %Y",
    "%d %B %Y",
    "%Y/%m/%d",
)

_MONEY = re.compile(r"-?[\d,]+\.\d{2}")


def parse_date(value: object) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text:
        return None
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(text[:32], fmt).date()
        except ValueError:
            continue
    return None


def parse_money(value: object) -> Decimal | None:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float, Decimal)):
        try:
            return Decimal(str(value)).quantize(Decimal("0.01"))
        except InvalidOperation:
            return None
    text = str(value).strip().replace("\u00a3", "").replace("£", "").replace(",", "")
    match = _MONEY.search(text.replace(" ", ""))
    if not match:
        # last token might be 10.65 without commas
        compact = re.sub(r"[^\d.\-]", "", text)
        if not _MONEY.search(compact):
            return None
        text = compact
    else:
        text = match.group(0).replace(",", "")
    try:
        return Decimal(text).quantize(Decimal("0.01"))
    except InvalidOperation:
        return None


def looks_like_money(text: str) -> bool:
    return parse_money(text) is not None


def normalize_description(text: str) -> str:
    return " ".join(str(text).upper().split())
