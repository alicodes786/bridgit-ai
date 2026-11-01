"""Write Banking + Bank Pay into a copy of a prior-year statutory pack.

Process-log Phase 1 only. Does not touch ETB / P&L / balance sheet (Pg 9 trap).
Formatting follows the uploaded comparative (Arial, number formats, month markers).
"""

from __future__ import annotations

from copy import copy
from datetime import date
from decimal import Decimal
from io import BytesIO

from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from app.engine.ma_template import replace_bank_rec_sheet
from app.engine.yearend_map import (
    BANK_PAY_FIRST_DATA,
    BANKING_FIRST_DATA,
    bank_pay_headers,
    banking_headers,
)
from app.models import CanonicalTxn, ClassificationResult

_TITLE_YEAR = "FOR THE YEAR ENDED 28TH FEBRUARY"
_MONEY = "0.00"
_MONTH = "mmm-yy"
_DATE = "DD/MM/YYYY"


def write_yearend_bank_tabs(
    template_bytes: bytes,
    transactions: list[CanonicalTxn],
    classifications: list[ClassificationResult],
    *,
    period_end: date | None = None,
    client_name: str | None = None,
    opening_balance: Decimal | float | None = None,
    closing_balance: Decimal | float | None = None,
    notes: list[str] | None = None,
) -> bytes:
    wb = load_workbook(BytesIO(template_bytes))
    receipts = [(t, k) for t, k in zip(transactions, classifications, strict=True) if t.debit_credit == "credit"]
    payments = [(t, k) for t, k in zip(transactions, classifications, strict=True) if t.debit_credit == "debit"]
    banking_total = _rewrite_banking(wb["Banking"], receipts, period_end=period_end)
    pay_total = _rewrite_bank_pay(wb["Bank Pay"], payments, period_end=period_end)
    _retarget_bank_rec(
        wb,
        banking_total=banking_total,
        pay_total=pay_total,
        opening=opening_balance,
        closing=closing_balance,
        period_end=period_end,
        client_name=client_name,
    )
    _write_bridgit_sheet(
        wb,
        client_name=client_name,
        period_end=period_end,
        receipts=len(receipts),
        payments=len(payments),
        opening=opening_balance,
        closing=closing_balance,
        notes=notes or [],
        uncoded=[
            (t, k)
            for t, k in zip(transactions, classifications, strict=True)
            if k.needs_review or not (k.account_name or k.account_code)
        ],
    )
    out = BytesIO()
    wb.save(out)
    return out.getvalue()


def _set_year_title(ws: Worksheet, period_end: date | None) -> None:
    if period_end is None:
        return
    cell = ws["A3"]
    val = str(cell.value or "")
    if _TITLE_YEAR in val.upper() or "FOR THE YEAR ENDED" in val.upper():
        cell.value = f"FOR THE YEAR ENDED {period_end.strftime('%dTH %B %Y').upper()}"
        cell.font = Font(name="Arial", size=10, bold=True)


def _clear_block(ws: Worksheet, start: int, end: int, last_col: int) -> None:
    for row in range(start, end + 1):
        for col in range(1, last_col + 1):
            ws.cell(row, col).value = None


def _sample_row(ws: Worksheet, start: int, amount_col: int) -> int | None:
    for row in range(start, start + 40):
        val = ws.cell(row, amount_col).value
        if isinstance(val, (int, float)) or (isinstance(val, str) and val.startswith("=")):
            return row
    return None


def _copy_style(src, dest) -> None:
    dest.font = copy(src.font)
    dest.border = copy(src.border)
    dest.fill = copy(src.fill)
    dest.alignment = copy(src.alignment)
    dest.number_format = src.number_format


def _apply_row_style(ws: Worksheet, row: int, last_col: int, sample: int | None, *, month: bool) -> None:
    src_row = sample or row
    for col in range(1, last_col + 1):
        dest = ws.cell(row, col)
        src = ws.cell(src_row, col)
        try:
            _copy_style(src, dest)
        except Exception:
            dest.font = Font(name="Arial", size=10, bold=month)
    if month:
        ws.cell(row, 1).font = Font(name="Arial", size=10, bold=True)
        ws.cell(row, 1).number_format = _MONTH
        ws.cell(row, 1).fill = PatternFill("solid", fgColor="D9E2F3")
    else:
        if ws.cell(row, 1).value and not isinstance(ws.cell(row, 1).value, int):
            ws.cell(row, 1).number_format = _DATE
        ws.cell(row, 3).number_format = _MONEY


def _rewrite_banking(ws: Worksheet, rows: list[tuple[CanonicalTxn, ClassificationResult]], *, period_end: date | None) -> int:
    _set_year_title(ws, period_end)
    headers = banking_headers(ws)
    name_to_col = {name.lower(): col for col, name in headers.items()}
    old_total = _find_total_row(ws, 2, 80) or 37
    sample = _sample_row(ws, BANKING_FIRST_DATA, 3)
    _clear_block(ws, BANKING_FIRST_DATA, old_total, 12)
    r = BANKING_FIRST_DATA
    last_month = None
    for txn, klass in rows:
        month = (txn.txn_date.year, txn.txn_date.month)
        if month != last_month:
            ws.cell(r, 1).value = date(txn.txn_date.year, txn.txn_date.month, 1)
            _apply_row_style(ws, r, 12, sample, month=True)
            last_month = month
            r += 1
        ws.cell(r, 1).value = txn.txn_date
        ws.cell(r, 2).value = txn.description.split(";")[0].strip()
        ws.cell(r, 3).value = float(txn.amount)
        col = _column_for(klass.account_name, name_to_col)
        if col:
            ws.cell(r, col).value = f"=C{r}"
        ws.cell(r, 12).value = f"=SUM(D{r}:K{r})-C{r}"
        _apply_row_style(ws, r, 12, sample, month=False)
        if klass.needs_review or not col:
            ws.cell(r, 2).fill = PatternFill("solid", fgColor="FFF2CC")
        r += 1
    total_row = r
    ws.cell(total_row, 2).value = "TOTAL"
    ws.cell(total_row, 2).font = Font(name="Arial", size=10, bold=True)
    for col, letter in enumerate(["C", "D", "E", "F", "G", "H", "I", "J", "K"], start=3):
        cell = ws.cell(total_row, col)
        cell.value = f"=SUM({letter}{BANKING_FIRST_DATA}:{letter}{total_row - 1})"
        cell.font = Font(name="Arial", size=10, bold=True)
        cell.number_format = _MONEY
        cell.fill = PatternFill("solid", fgColor="DDEBF7")
    return total_row


def _rewrite_bank_pay(ws: Worksheet, rows: list[tuple[CanonicalTxn, ClassificationResult]], *, period_end: date | None) -> int:
    _set_year_title(ws, period_end)
    headers = bank_pay_headers(ws)
    name_to_col = {name.lower(): col for col, name in headers.items()}
    old_total = _find_total_row(ws, 2, 400) or 287
    sample = _sample_row(ws, BANK_PAY_FIRST_DATA, 3)
    _clear_block(ws, BANK_PAY_FIRST_DATA, min(old_total + 5, 400), 30)
    r = BANK_PAY_FIRST_DATA
    last_month = None
    for txn, klass in rows:
        month = (txn.txn_date.year, txn.txn_date.month)
        if month != last_month:
            ws.cell(r, 1).value = date(txn.txn_date.year, txn.txn_date.month, 1)
            _apply_row_style(ws, r, 30, sample, month=True)
            last_month = month
            r += 1
        ws.cell(r, 1).value = txn.txn_date.day
        ws.cell(r, 2).value = txn.description.split(";")[0].strip()
        ws.cell(r, 3).value = float(txn.amount)
        col = _column_for(klass.account_name, name_to_col)
        if col:
            ws.cell(r, col).value = f"=C{r}"
        ws.cell(r, 30).value = f"=SUM(D{r}:AC{r})-C{r}"
        _apply_row_style(ws, r, 30, sample, month=False)
        ws.cell(r, 1).number_format = "0"
        if klass.needs_review or not col:
            ws.cell(r, 2).fill = PatternFill("solid", fgColor="FFF2CC")
        r += 1
    total_row = r
    ws.cell(total_row, 2).value = "TOTAL"
    ws.cell(total_row, 2).font = Font(name="Arial", size=10, bold=True)
    for col in range(3, 30):
        letter = get_column_letter(col)
        cell = ws.cell(total_row, col)
        cell.value = f"=SUM({letter}{BANK_PAY_FIRST_DATA}:{letter}{total_row - 1})"
        cell.font = Font(name="Arial", size=10, bold=True)
        cell.number_format = _MONEY
        cell.fill = PatternFill("solid", fgColor="DDEBF7")
    return total_row


def _retarget_bank_rec(
    wb,
    *,
    banking_total: int,
    pay_total: int,
    opening,
    closing,
    period_end: date | None,
    client_name: str | None = None,
) -> None:
    name = "Bank Rec" if "Bank Rec" in wb.sheetnames else (
        "Bank Reconciliation" if "Bank Reconciliation" in wb.sheetnames else "Bank Rec"
    )
    if period_end:
        period = f"FOR THE YEAR ENDED {period_end.strftime('%dTH %B %Y').upper()}"
    else:
        period = "Year-end working file"
    replace_bank_rec_sheet(
        wb,
        name=name,
        company=(client_name or "Client").upper(),
        period=period,
        receipts_formula=f"=Banking!C{banking_total}",
        payments_formula=f"=-'Bank Pay'!C{pay_total}",
        opening=float(opening) if opening is not None else None,
        closing=float(closing) if closing is not None else None,
        receipts_label="Add: Receipts in the year (Banking tab total)",
        payments_label="Less: Payments in the year (Bank Pay tab total)",
    )


def _write_bridgit_sheet(
    wb,
    *,
    client_name: str | None,
    period_end: date | None,
    receipts: int,
    payments: int,
    opening,
    closing,
    notes: list[str],
    uncoded: list,
) -> None:
    title = "Bridgit"
    if title in wb.sheetnames:
        del wb[title]
    ws = wb.create_sheet(title)
    ws.sheet_properties.tabColor = "C8A84B"
    ws["A1"] = (client_name or "Client").upper()
    ws["A1"].font = Font(name="Arial", size=16, bold=True, color="1F4E78")
    ws["A2"] = "Bridgit bank working file"
    ws["A2"].font = Font(name="Arial", size=12, bold=True)
    ws["A3"] = f"Year ended {period_end.strftime('%d %B %Y')}" if period_end else "Year-end pack"
    ws["A3"].font = Font(name="Arial", size=9, color="5C6570")
    blurb = [
        "This workbook is last year's statutory pack with this year's Banking and Bank Pay rewritten.",
        "ETB, P&L, balance sheet and notes still show last year until process-log Phase 2.",
        "Yellow cells on Banking / Bank Pay still need a column. Totals and check columns are formulas.",
        f"Money in lines: {receipts}. Money out lines: {payments}.",
        f"Opening {opening if opening is not None else '-'}  Closing {closing if closing is not None else '-'}.",
    ]
    for i, line in enumerate(blurb + notes, start=5):
        ws.cell(i, 1, line).font = Font(name="Arial", size=10)
        ws.merge_cells(start_row=i, start_column=1, end_row=i, end_column=6)
        ws.row_dimensions[i].height = 18
    start = 5 + len(blurb) + len(notes) + 2
    ws.cell(start, 1, "Still open / uncoded").font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    ws.cell(start, 1).fill = PatternFill("solid", fgColor="1F4E78")
    ws.merge_cells(start_row=start, start_column=1, end_row=start, end_column=4)
    ws.cell(start + 1, 1, "Date")
    ws.cell(start + 1, 2, "Payee")
    ws.cell(start + 1, 3, "In / out")
    ws.cell(start + 1, 4, "Amount")
    for col in range(1, 5):
        ws.cell(start + 1, col).font = Font(name="Arial", size=9, bold=True)
    r = start + 2
    for txn, klass in uncoded[:80]:
        ws.cell(r, 1, txn.txn_date).number_format = _DATE
        ws.cell(r, 2, txn.description.split(";")[0].strip())
        ws.cell(r, 3, "Money in" if txn.debit_credit == "credit" else "Money out")
        ws.cell(r, 4, float(txn.amount)).number_format = _MONEY
        r += 1
    if not uncoded:
        ws.cell(r, 1, "All bank lines have a column.").font = Font(name="Arial", size=10)
    ws.column_dimensions["A"].width = 16
    ws.column_dimensions["B"].width = 42
    ws.column_dimensions["C"].width = 14
    ws.column_dimensions["D"].width = 14
    ws.sheet_view.showGridLines = False


def _column_for(account_name: str | None, name_to_col: dict[str, int]) -> int | None:
    key = (account_name or "").strip().lower()
    if not key:
        return None
    if key in name_to_col:
        return name_to_col[key]
    for name, col in name_to_col.items():
        if key in name or name in key:
            return col
    return None


def _find_total_row(ws: Worksheet, detail_col: int, max_row: int) -> int | None:
    for row in range(max_row, 1, -1):
        val = ws.cell(row, detail_col).value
        if str(val or "").strip().upper() == "TOTAL":
            return row
    return None
