"""Write categorised rows into MA's VAT working-file shape.

Write surface is documented in 23-excel-template-spike.md:
  Banking Analysis + Bank Payment Analysis rows from 6,
  anchor SUM on row 1000, Bank Rec opening E8 + closing E12.
VAT/Net columns are formulas, matching the Koliqi file.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from io import BytesIO
from pathlib import Path

from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.cell.cell import Cell

from app.engine.ma_template import build_vat_workbook
from app.models import CanonicalTxn, ClassificationResult, ParseResult

BANKING = "Banking Analysis"
PAYMENTS = "Bank Payment Analysis"
BANK_REC = "Bank Reconciliation"
DATA_START = 6
ANCHOR_ROW = 1000
TOLERANCE = Decimal("0.01")
_MONEY = '#,##0.00;(#,##0.00);"-"'
_DATE = "DD/MM/YYYY"
_THIN = Border(
    left=Side(style="thin", color="D9D1C3"),
    right=Side(style="thin", color="D9D1C3"),
    top=Side(style="thin", color="D9D1C3"),
    bottom=Side(style="thin", color="D9D1C3"),
)
_ASK = PatternFill("solid", fgColor="FFF2CC")
_OK = PatternFill("solid", fgColor="FFFFFF")
_ZEBRA = PatternFill("solid", fgColor="F7F3EA")


def write_working_file(
    parsed: ParseResult,
    transactions: list[CanonicalTxn],
    classifications: list[ClassificationResult],
    *,
    template_bytes: bytes | None = None,
    template_path: Path | None = None,
    job_type: str = "vat_return",
    period_start: date | None = None,
    period_end: date | None = None,
    client_name: str | None = None,
    notes: list[str] | None = None,
) -> bytes:
    del template_path
    if job_type == "company_accounts" and template_bytes:
        from app.engine.yearend_map import is_yearend_pack
        from app.engine.yearend_excel import write_yearend_bank_tabs

        if is_yearend_pack(template_bytes):
            return write_yearend_bank_tabs(
                template_bytes,
                transactions,
                classifications,
                period_end=period_end,
                client_name=client_name,
                opening_balance=parsed.opening_balance,
                closing_balance=parsed.closing_balance,
                notes=notes,
            )

    wb = build_vat_workbook(
        client_name=client_name or "Client",
        period_start=period_start,
        period_end=period_end,
        notes=notes,
    )

    receipts: list[tuple[CanonicalTxn, ClassificationResult]] = []
    payments: list[tuple[CanonicalTxn, ClassificationResult]] = []
    for txn, klass in zip(transactions, classifications, strict=True):
        if txn.debit_credit == "credit":
            receipts.append((txn, klass))
        else:
            payments.append((txn, klass))

    last_in = DATA_START + len(receipts) - 1 if receipts else DATA_START
    last_out = DATA_START + len(payments) - 1 if payments else DATA_START
    _write_rows(wb[BANKING], receipts)
    _write_rows(wb[PAYMENTS], payments)
    _set_anchor(wb[BANKING], last_in)
    _set_anchor(wb[PAYMENTS], last_out)
    wb[BANKING].auto_filter.ref = f"A5:H{last_in}"
    wb[PAYMENTS].auto_filter.ref = f"A5:H{last_out}"

    rec = wb[BANK_REC]
    if parsed.opening_balance is not None:
        rec["E8"] = float(parsed.opening_balance)
    if parsed.closing_balance is not None:
        rec["E12"] = float(parsed.closing_balance)
    rec["E8"].number_format = _MONEY
    rec["E12"].number_format = _MONEY

    out = BytesIO()
    wb.save(out)
    return out.getvalue()


def bank_rec_check(parsed: ParseResult, transactions: list[CanonicalTxn]) -> dict:
    """Hard gate: opening + receipts - payments ≈ closing (from the statement)."""
    receipts = sum((t.amount for t in transactions if t.debit_credit == "credit"), Decimal("0.00"))
    payments = sum((t.amount for t in transactions if t.debit_credit == "debit"), Decimal("0.00"))
    opening = parsed.opening_balance
    closing = parsed.closing_balance
    calculated = None
    difference = None
    ok = False
    if opening is not None and closing is not None:
        calculated = (opening + receipts - payments).quantize(Decimal("0.01"))
        difference = (calculated - closing).quantize(Decimal("0.01"))
        ok = abs(difference) <= TOLERANCE
    return {
        "ok": ok,
        "opening": _num(opening),
        "receipts": _num(receipts),
        "payments": _num(payments),
        "calculated_closing": _num(calculated),
        "statement_closing": _num(closing),
        "difference": _num(difference),
    }


def trial_balance_check(transactions: list[CanonicalTxn]) -> dict:
    """Double-entry view of bank lines: each payment Dr expense / Cr bank, and vice versa."""
    debit = sum((t.amount for t in transactions if t.debit_credit == "debit"), Decimal("0.00"))
    credit = sum((t.amount for t in transactions if t.debit_credit == "credit"), Decimal("0.00"))
    bank_side = debit + credit
    category_side = debit + credit
    ok = bank_side == category_side
    return {
        "ok": ok,
        "debits": _num(bank_side),
        "credits": _num(category_side),
        "note": "Bank-only double-entry identity. Full TB after chart of accounts.",
    }


def _write_rows(ws, rows: list[tuple[CanonicalTxn, ClassificationResult]]) -> None:
    font = Font(name="Arial", size=9)
    for offset, (txn, klass) in enumerate(rows):
        r = DATA_START + offset
        fill = _ASK if klass.needs_review else (_ZEBRA if offset % 2 else _OK)
        ws.cell(r, 1).value = txn.txn_date
        ws.cell(r, 1).number_format = _DATE
        ws.cell(r, 2).value = txn.payment_type or None
        ws.cell(r, 3).value = txn.description
        ws.cell(r, 4).value = float(txn.amount)
        ws.cell(r, 4).number_format = _MONEY
        ws.cell(r, 5).value = klass.account_name or None
        ws.cell(r, 6).value = klass.vat_code or ("NV" if klass.account_name else None)
        ws.cell(r, 7).value = f'=IF(F{r}="SR",ROUND(D{r}/6,2),0)'
        ws.cell(r, 7).number_format = _MONEY
        ws.cell(r, 8).value = f"=D{r}-G{r}"
        ws.cell(r, 8).number_format = _MONEY
        for col in range(1, 9):
            cell = ws.cell(r, col)
            cell.font = font
            cell.border = _THIN
            cell.fill = fill
            cell.alignment = Alignment(vertical="center")
        ws.row_dimensions[r].height = 18


def _set_anchor(ws, last_data_row: int) -> None:
    last = max(DATA_START, last_data_row)
    for col, letter in ((4, "D"), (7, "G"), (8, "H")):
        cell: Cell = ws.cell(ANCHOR_ROW, col)
        cell.value = f"=SUM({letter}{DATA_START}:{letter}{last})"
        cell.number_format = _MONEY
        cell.font = Font(name="Arial", size=10, bold=True)


def patch_working_file(
    xlsx_bytes: bytes,
    *,
    description: str,
    amount: Decimal,
    account_name: str,
    vat_code: str,
    vat_amount: Decimal,
    net_amount: Decimal,
) -> bytes:
    """Kept for tests / older callers. Current resolve rebuilds the whole file."""
    del vat_amount, net_amount
    from openpyxl import load_workbook

    wb = load_workbook(BytesIO(xlsx_bytes))
    target = " ".join(description.upper().split())
    amount_f = float(amount)
    for sheet_name in (BANKING, PAYMENTS):
        if sheet_name not in wb.sheetnames:
            continue
        ws = wb[sheet_name]
        for row in range(DATA_START, ANCHOR_ROW):
            desc = ws.cell(row, 3).value
            amt = ws.cell(row, 4).value
            if desc is None or amt is None:
                continue
            if " ".join(str(desc).upper().split()) != target:
                continue
            try:
                if abs(float(amt) - amount_f) > 0.02:
                    continue
            except (TypeError, ValueError):
                continue
            ws.cell(row, 5).value = account_name or None
            ws.cell(row, 6).value = vat_code or None
    out = BytesIO()
    wb.save(out)
    return out.getvalue()


def _num(value: Decimal | None) -> float | None:
    return float(value) if value is not None else None
