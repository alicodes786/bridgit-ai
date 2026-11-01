"""CSV and Excel bank exports → canonical rows. Bank-agnostic column detection."""

from __future__ import annotations

from io import BytesIO

import openpyxl

from app.ingest._util import parse_date, parse_money
from app.models import CanonicalTxn, ParseResult

_HEADER_ALIASES = {
    "date": ("date", "txn date", "transaction date", "posted", "value date"),
    "description": (
        "description",
        "narrative",
        "details",
        "detail",
        "transaction",
        "payee",
        "merchant",
        "reference",
    ),
    "amount": ("amount", "value", "txn amount"),
    "in": ("money in", "paid in", "credit", "in", "received", "deposits"),
    "out": ("money out", "paid out", "debit", "out", "payments", "withdrawals"),
    "type": ("type", "payment type", "transaction type"),
    "balance": ("balance", "running balance", "closing balance"),
}


def parse_csv(content: bytes, *, file_name: str = "") -> ParseResult:
    import csv

    text = content.decode("utf-8-sig", errors="replace")
    rows = list(csv.reader(text.splitlines()))
    return _from_rows(rows, parser="csv", file_name=file_name)


def parse_xlsx(content: bytes, *, file_name: str = "") -> ParseResult:
    wb = openpyxl.load_workbook(BytesIO(content), data_only=True)
    ws = wb.active
    rows = [[cell for cell in row] for row in ws.iter_rows(values_only=True)]
    return _from_rows(rows, parser="xlsx", file_name=file_name)


def _from_rows(rows: list, *, parser: str, file_name: str) -> ParseResult:
    header_i, mapping = _find_header(rows)
    if mapping is None:
        return ParseResult(
            transactions=[],
            parser=parser,
            warnings=[f"could not detect date/description columns in {file_name or parser}"],
        )
    txns: list[CanonicalTxn] = []
    warnings: list[str] = []
    row_no = 0
    for raw in rows[header_i + 1 :]:
        cells = ["" if c is None else c for c in raw]
        parsed = _txn_from_row(cells, mapping)
        if parsed is None:
            continue
        row_no += 1
        parsed.source_row = row_no
        txns.append(parsed)
    if not txns:
        warnings.append(f"no transaction rows in {file_name or parser}")
        return ParseResult(transactions=txns, parser=parser, warnings=warnings)
    txns = _chronological(txns)
    opening, closing = _opening_and_close(txns)
    return ParseResult(
        transactions=txns,
        parser=parser,
        opening_balance=opening,
        closing_balance=closing,
        warnings=warnings,
    )


def _find_header(rows: list) -> tuple[int, dict[str, int] | None]:
    for i, raw in enumerate(rows[:30]):
        labels = [str(c or "").strip().lower() for c in raw]
        mapping: dict[str, int] = {}
        for key, aliases in _HEADER_ALIASES.items():
            for idx, label in enumerate(labels):
                if _alias_matches(label, aliases):
                    mapping[key] = idx
                    break
        if "date" in mapping and ("description" in mapping or "amount" in mapping or "in" in mapping):
            return i, mapping
    return 0, None


def _alias_matches(label: str, aliases: tuple[str, ...]) -> bool:
    if label in aliases:
        return True
    for alias in aliases:
        if len(alias) <= 3:
            continue
        if alias in label:
            return True
    return False


def _txn_from_row(cells: list, mapping: dict[str, int]) -> CanonicalTxn | None:
    def col(key: str):
        idx = mapping.get(key)
        if idx is None or idx >= len(cells):
            return None
        return cells[idx]

    txn_date = parse_date(col("date"))
    if txn_date is None:
        return None
    desc = str(col("description") or "").strip()
    if not desc:
        return None
    in_amt = parse_money(col("in"))
    out_amt = parse_money(col("out"))
    amount = parse_money(col("amount"))
    if in_amt and in_amt != 0:
        value, debit_credit = abs(in_amt), "credit"
    elif out_amt and out_amt != 0:
        value, debit_credit = abs(out_amt), "debit"
    elif amount is not None:
        value = abs(amount)
        debit_credit = "debit" if amount < 0 else "credit"
    else:
        return None
    payment_type = str(col("type") or "").strip()
    balance = parse_money(col("balance"))
    return CanonicalTxn(
        txn_date=txn_date,
        description=desc,
        amount=value,
        debit_credit=debit_credit,
        payment_type=payment_type,
        reference=payment_type,
        running_balance=balance,
    )


def _chronological(txns: list[CanonicalTxn]) -> list[CanonicalTxn]:
    """Countingup (and many exports) are newest-first. Process log: sort ascending."""
    newest_first = False
    if len(txns) >= 2 and txns[0].txn_date > txns[-1].txn_date:
        newest_first = True
    if newest_first:
        ordered = sorted(txns, key=lambda t: (t.txn_date, -(t.source_row or 0)))
    else:
        ordered = sorted(txns, key=lambda t: (t.txn_date, t.source_row or 0))
    for i, txn in enumerate(ordered, start=1):
        txn.source_row = i
    return ordered


def _opening_and_close(txns: list[CanonicalTxn]) -> tuple:
    """Earliest running balance ± that row's movement = opening; latest balance = close."""
    from decimal import Decimal

    first = next((t for t in txns if t.running_balance is not None), None)
    last = None
    for t in txns:
        if t.running_balance is not None:
            last = t
    if first is None or last is None:
        return None, None
    if first.debit_credit == "credit":
        opening = (first.running_balance - first.amount).quantize(Decimal("0.01"))
    else:
        opening = (first.running_balance + first.amount).quantize(Decimal("0.01"))
    return opening, last.running_balance
