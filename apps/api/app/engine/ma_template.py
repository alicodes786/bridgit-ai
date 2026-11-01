"""Blank MA VAT working file (Koliqi shape). No live client data.

Sheets and formulas follow docs/ai-accounting/23-excel-template-spike.md.
"""

from __future__ import annotations

from datetime import date

from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

NAVY = "1F4E78"
GOLD = "C8A84B"
YELLOW = "FFF2CC"
BLUE_ROW = "DDEBF7"
WHITE = "FFFFFF"
INK = "1A1A1A"
MUTED = "5C6570"
TIE_GREEN = "C6EFCE"
TIE_INK = "006100"
GAP_AMBER = "FCE4D6"

_THIN = Border(
    left=Side(style="thin", color="D9D1C3"),
    right=Side(style="thin", color="D9D1C3"),
    top=Side(style="thin", color="D9D1C3"),
    bottom=Side(style="thin", color="D9D1C3"),
)
_THICK_BOTTOM = Border(
    left=Side(style="thin", color="D9D1C3"),
    right=Side(style="thin", color="D9D1C3"),
    top=Side(style="thin", color="D9D1C3"),
    bottom=Side(style="medium", color=NAVY),
)
_MONEY = '#,##0.00;(#,##0.00);"-"'
_DATE = "DD/MM/YYYY"


def _font(size=10, bold=False, color=INK, name="Arial"):
    return Font(name=name, size=size, bold=bold, color=color)


def _fill(hex_color: str) -> PatternFill:
    return PatternFill("solid", fgColor=hex_color)


def _title_block(ws: Worksheet, company: str, subtitle: str, period: str, last_col: int) -> None:
    last = get_column_letter(last_col)
    ws.merge_cells(f"A1:{last}1")
    ws.merge_cells(f"A2:{last}2")
    ws.merge_cells(f"A3:{last}3")
    ws["A1"] = company
    ws["A1"].font = _font(16, True, NAVY)
    ws["A2"] = subtitle
    ws["A2"].font = _font(12, True, NAVY)
    ws["A3"] = period
    ws["A3"].font = _font(9, False, "5C6570")
    ws.row_dimensions[1].height = 22
    ws.row_dimensions[2].height = 18
    ws.sheet_properties.tabColor = NAVY


def _header_row(ws: Worksheet, row: int, labels: list[str]) -> None:
    for col, label in enumerate(labels, start=1):
        cell = ws.cell(row, col, label)
        cell.font = _font(10, True, WHITE)
        cell.fill = _fill(NAVY)
        cell.alignment = Alignment(horizontal="center", wrap_text=True, vertical="center")
        cell.border = _THIN
    ws.row_dimensions[row].height = 22
    ws.freeze_panes = f"A{row + 1}"
    ws.auto_filter.ref = f"A{row}:{get_column_letter(len(labels))}{row}"


def _widths(ws: Worksheet, widths: dict[str, float]) -> None:
    for letter, width in widths.items():
        ws.column_dimensions[letter].width = width


def _period_label(period_start: date | None, period_end: date | None) -> str:
    if period_start and period_end:
        return f"Period: {period_start.strftime('%d %b %Y')} to {period_end.strftime('%d %b %Y')}"
    if period_end:
        return f"Period ending {period_end.strftime('%d %b %Y')}"
    return "Period: (set on the job)"


def build_vat_workbook(
    *,
    client_name: str,
    period_start: date | None = None,
    period_end: date | None = None,
    notes: list[str] | None = None,
) -> Workbook:
    company = (client_name or "Client").strip() or "Client"
    period = _period_label(period_start, period_end)
    wb = Workbook()

    notes_ws = wb.active
    notes_ws.title = "Notes & Queries"
    _build_notes(notes_ws, company, period, notes or [])

    rec = wb.create_sheet("Bank Reconciliation")
    _build_rec(rec, company, period)

    banking = wb.create_sheet("Banking Analysis")
    _build_analysis(
        banking,
        company,
        period,
        subtitle="Banking Analysis - Receipts (money in)",
        headers=["Date", "Type", "Detail", "Received (£)", "Category", "Code", "Output VAT", "Net (ex VAT)"],
    )

    payments = wb.create_sheet("Bank Payment Analysis")
    _build_analysis(
        payments,
        company,
        period,
        subtitle="Bank Payment Analysis - Payments (money out)",
        headers=["Date", "Type", "Detail", "Paid (£)", "Category", "Code", "Input VAT", "Net (ex VAT)"],
    )

    sales = wb.create_sheet("Sales Invoices")
    _build_placeholder(
        sales,
        company,
        period,
        "Sales Invoices (output VAT)",
        "Invoice listing is Phase 2. Bank receipts on Banking Analysis already feed Box 1 / Box 6.",
        ["Date", "Invoice", "Customer", "Net (£)", "VAT code", "VAT (£)", "Gross (£)", "Notes"],
    )

    purchases = wb.create_sheet("Purchase Invoices")
    _build_placeholder(
        purchases,
        company,
        period,
        "Purchase Invoices (input VAT)",
        "Invoice listing is Phase 2. Bank payments on Bank Payment Analysis already feed Box 4 / Box 7.",
        ["Date", "Invoice", "Supplier", "Net (£)", "VAT code", "VAT (£)", "Gross (£)", "Notes"],
    )

    vat = wb.create_sheet("VAT Calculation")
    _build_vat_calc(vat, company, period)
    return wb


def _build_notes(ws: Worksheet, company: str, period: str, notes: list[str]) -> None:
    _title_block(ws, company, "VAT Working File - Notes, Assumptions & Queries", period, 8)
    _widths(ws, {"A": 22, "B": 88, "C": 14, "D": 14, "E": 14, "F": 14, "G": 14, "H": 14})
    ws["A5"] = "HOW TO READ THIS FILE"
    ws["A5"].font = _font(11, True, WHITE)
    ws["A5"].fill = _fill(NAVY)
    ws.merge_cells("A5:H5")
    lines = [
        "Banking Analysis = money IN (deposits / receipts). Bank Payment Analysis = money OUT (payments).",
        "Category is the column / account. Code is VAT: SR 20%, ZR zero, EX exempt, NV no VAT, OS outside scope.",
        "Output/Input VAT and Net are formulas. Change the Code and they recalculate.",
        "Bank Reconciliation opening and closing come from the statement. Difference must be nil.",
        "VAT Calculation boxes 1-9 are formulas from the analysis tabs. This is a working file, not a filed return.",
        "Yellow cells are inputs. Everything else should be left as formula.",
        "Bridgit codes known payees from last year and asks the accountant where it is new or unclear.",
    ]
    for i, text in enumerate(lines, start=6):
        ws.merge_cells(start_row=i, start_column=1, end_row=i, end_column=8)
        ws.cell(i, 1, text).font = _font(10)
        ws.row_dimensions[i].height = 18
    ws["A14"] = "BRIDGIT NOTES"
    ws["A14"].font = _font(11, True, WHITE)
    ws["A14"].fill = _fill(NAVY)
    ws.merge_cells("A14:H14")
    if not notes:
        notes = ["Processed by Bridgit. Answered coding questions are saved for this client."]
    for i, text in enumerate(notes[:12], start=15):
        ws.merge_cells(start_row=i, start_column=1, end_row=i, end_column=8)
        ws.cell(i, 1, text).font = _font(10)
        ws.row_dimensions[i].height = 18
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 1
    ws.print_title_rows = "1:3"
    ws.sheet_view.showGridLines = False


def paint_bank_rec(
    ws: Worksheet,
    *,
    company: str,
    period: str,
    receipts_formula: str,
    payments_formula: str,
    opening: float | None = None,
    closing: float | None = None,
    receipts_label: str = "Add: Receipts in the period (Banking Analysis)",
    payments_label: str = "Less: Payments in the period (Bank Payment Analysis)",
) -> None:
    """MA movement rec: opening + money in - money out = statement close.

    Write surface (kept stable for formulas and tests):
      E8 opening (yellow), E9 receipts, E10 payments (negative),
      E11 calculated close, E12 statement close (yellow), E13 difference.
    """
    _title_block(ws, company, "Bank Reconciliation", period, 5)
    _widths(ws, {"A": 64, "B": 12, "C": 12, "D": 12, "E": 18, "F": 52})
    ws.row_dimensions[4].height = 6
    ws.merge_cells("A4:E4")
    ws["A4"].fill = _fill(GOLD)

    ws["A5"] = "Bank account"
    ws["A5"].font = _font(10, True)
    ws.merge_cells("B5:E5")
    ws["B5"] = "As on the uploaded statement (Countingup / bank CSV)."
    ws["B5"].font = _font(10, False, MUTED)

    ws.merge_cells("A7:D7")
    ws["A7"] = "1. Movement on the account"
    ws["A7"].font = _font(11, True, WHITE)
    ws["A7"].fill = _fill(NAVY)
    ws["E7"] = "£"
    ws["E7"].font = _font(11, True, WHITE)
    ws["E7"].fill = _fill(NAVY)
    ws["E7"].alignment = Alignment(horizontal="right")
    for c in range(1, 6):
        ws.cell(7, c).fill = _fill(NAVY)

    rows = [
        (8, "Opening balance per bank statement", True, False, "From the statement / CSV running balance."),
        (9, receipts_label, False, False, "Formula: total money in on the Banking tab."),
        (10, payments_label, False, False, "Formula: total money out on the Bank Pay tab (shown as negative)."),
        (11, "Calculated closing balance", False, True, "Opening + receipts + payments."),
        (12, "Closing balance per bank statement", True, False, "Latest running balance on the statement."),
        (13, "Difference  -  must be nil", False, True, "Calculated close minus statement close."),
    ]
    for r, label, _yellow, emphasis, hint in rows:
        ws.cell(r, 1, label).font = _font(10, emphasis)
        ws.cell(r, 1).alignment = Alignment(wrap_text=True, vertical="center")
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
        ws.cell(r, 5).number_format = _MONEY
        ws.cell(r, 5).alignment = Alignment(horizontal="right", vertical="center")
        ws.row_dimensions[r].height = 20
        for c in range(1, 6):
            ws.cell(r, c).border = _THICK_BOTTOM if r in (11, 13) else _THIN
        ws.cell(r, 1).font = _font(10, emphasis)
        ws.cell(r, 6, hint).font = _font(8, False, MUTED)

    ws["E8"] = float(opening) if opening is not None else 0
    ws["E9"] = receipts_formula
    ws["E10"] = payments_formula
    ws["E11"] = "=E8+E9+E10"
    ws["E12"] = float(closing) if closing is not None else 0
    ws["E13"] = "=E11-E12"
    for addr in ("E8", "E12"):
        ws[addr].fill = _fill(YELLOW)
        ws[addr].font = _font(10)
        ws[addr].number_format = _MONEY
    for addr in ("E9", "E10"):
        ws[addr].font = _font(10)
        ws[addr].number_format = _MONEY
        ws[addr].fill = _fill(WHITE)
    ws["E11"].font = _font(10, True)
    ws["E11"].number_format = _MONEY
    ws["E11"].fill = _fill(BLUE_ROW)
    ws["E13"].font = _font(10, True)
    ws["E13"].number_format = _MONEY
    ws["E13"].fill = _fill(BLUE_ROW)

    ws.merge_cells("A14:D14")
    ws["A14"] = "Status"
    ws["A14"].font = _font(10, True)
    ws["E14"] = '=IF(ABS(E13)<0.01,"TIES","DOES NOT TIE")'
    ws["E14"].font = _font(10, True, TIE_INK)
    ws["E14"].alignment = Alignment(horizontal="right")
    for c in range(1, 6):
        ws.cell(14, c).border = _THIN
        ws.cell(14, c).fill = _fill("E8F5E9")

    green = _fill(TIE_GREEN)
    amber = _fill(GAP_AMBER)
    ws.conditional_formatting.add("E13", FormulaRule(formula=["ABS($E$13)<0.01"], fill=green))
    ws.conditional_formatting.add("E13", FormulaRule(formula=["ABS($E$13)>=0.01"], fill=amber))
    ws.conditional_formatting.add("E14", FormulaRule(formula=['$E$14="TIES"'], fill=green))
    ws.conditional_formatting.add("E14", FormulaRule(formula=['$E$14="DOES NOT TIE"'], fill=amber))

    ws.merge_cells("A16:E16")
    ws["A16"] = "2. How to read this"
    ws["A16"].font = _font(11, True, WHITE)
    ws["A16"].fill = _fill(NAVY)
    how = [
        "Yellow cells come from the bank statement. Do not type over the blue formula rows.",
        "Opening + money in - money out must equal the statement closing. Status must read TIES.",
        "If it does not tie: missing line, duplicate, or the wrong opening balance. Fix the bank file, then retry process.",
        "This is the bank working file. It is not a finished statutory pack (ETB / P&L still last year on year-end jobs).",
    ]
    for i, line in enumerate(how, start=17):
        ws.merge_cells(start_row=i, start_column=1, end_row=i, end_column=5)
        ws.cell(i, 1, line).font = _font(9, False, MUTED)
        ws.row_dimensions[i].height = 16

    ws.merge_cells("A22:E22")
    ws["A22"] = "3. Linked totals (same figures as the analysis tabs)"
    ws["A22"].font = _font(11, True, WHITE)
    ws["A22"].fill = _fill(NAVY)
    ws["A23"] = "Receipts total used above"
    ws["E23"] = "=E9"
    ws["A24"] = "Payments total used above (absolute)"
    ws["E24"] = "=ABS(E10)"
    for r in (23, 24):
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
        ws.cell(r, 1).font = _font(10)
        ws.cell(r, 5).number_format = _MONEY
        ws.cell(r, 5).font = _font(10)
        for c in range(1, 6):
            ws.cell(r, c).border = _THIN

    ws["A26"] = "Prepared by Bridgit for MA Associates. Yellow = input from the statement. Navy header = section."
    ws["A26"].font = _font(8, False, MUTED)
    ws.merge_cells("A26:E26")

    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = 9
    ws.page_setup.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 1
    ws.print_title_rows = "1:3"
    ws.page_setup.leftMargin = 0.4
    ws.page_setup.rightMargin = 0.4
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 110
    ws.sheet_properties.tabColor = GOLD


def replace_bank_rec_sheet(
    wb,
    *,
    name: str,
    company: str,
    period: str,
    receipts_formula: str,
    payments_formula: str,
    opening: float | None = None,
    closing: float | None = None,
    receipts_label: str | None = None,
    payments_label: str | None = None,
):
    idx = wb.sheetnames.index(name) if name in wb.sheetnames else min(2, len(wb.sheetnames))
    if name in wb.sheetnames:
        del wb[name]
    ws = wb.create_sheet(name, idx)
    kwargs = dict(
        company=company,
        period=period,
        receipts_formula=receipts_formula,
        payments_formula=payments_formula,
        opening=opening,
        closing=closing,
    )
    if receipts_label:
        kwargs["receipts_label"] = receipts_label
    if payments_label:
        kwargs["payments_label"] = payments_label
    paint_bank_rec(ws, **kwargs)
    return ws


def _build_rec(ws: Worksheet, company: str, period: str) -> None:
    paint_bank_rec(
        ws,
        company=company,
        period=period,
        receipts_formula="='Banking Analysis'!D1000",
        payments_formula="=-'Bank Payment Analysis'!D1000",
        opening=0,
        closing=0,
    )


def _build_analysis(ws: Worksheet, company: str, period: str, *, subtitle: str, headers: list[str]) -> None:
    _title_block(ws, company, subtitle, period, 8)
    _header_row(ws, 5, headers)
    _widths(ws, {"A": 12, "B": 16, "C": 42, "D": 14, "E": 32, "F": 10, "G": 14, "H": 14})
    ws["A1000"] = "(total anchors - do not delete)"
    ws["A1000"].font = _font(8, False, "8B96A8")
    for col, letter in ((4, "D"), (7, "G"), (8, "H")):
        ws.cell(1000, col, f"=SUM({letter}6:{letter}6)")
        ws.cell(1000, col).font = _font(10, True)
        ws.cell(1000, col).number_format = _MONEY
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 1
    ws.print_title_rows = "1:5"
    ws.sheet_view.showGridLines = False


def _build_placeholder(
    ws: Worksheet,
    company: str,
    period: str,
    subtitle: str,
    blurb: str,
    headers: list[str],
) -> None:
    _title_block(ws, company, subtitle, period, 8)
    ws.merge_cells("A6:H6")
    ws["A6"] = blurb
    ws["A6"].font = _font(10, False, "5C6570")
    ws["A6"].alignment = Alignment(wrap_text=True)
    ws.row_dimensions[6].height = 32
    _header_row(ws, 8, headers)
    _widths(ws, {"A": 12, "B": 16, "C": 28, "D": 14, "E": 12, "F": 12, "G": 14, "H": 28})
    ws["G1000"] = "=SUM(G9:G9)"
    ws["F1000"] = "=SUM(F9:F9)"
    ws.sheet_view.showGridLines = False


def _build_vat_calc(ws: Worksheet, company: str, period: str) -> None:
    _title_block(ws, company, "VAT Calculation - Draft VAT Return", period, 5)
    _widths(ws, {"A": 14, "B": 48, "C": 14, "D": 14, "E": 18})
    ws["A5"] = "Input VAT recoverable (%)"
    ws["A5"].font = _font(10, True)
    ws["E5"] = 1
    ws["E5"].fill = _fill(YELLOW)
    ws["E5"].number_format = "0%"
    ws["A8"] = "VAT Return - Boxes 1 to 9"
    ws["A8"].font = _font(11, True, WHITE)
    ws["A8"].fill = _fill(NAVY)
    ws.merge_cells("A8:E8")
    boxes = [
        (9, "Box 1", "VAT due on sales and other outputs", "='Banking Analysis'!G1000+'Sales Invoices'!G1000"),
        (10, "Box 2", "VAT due on acquisitions (NI/EU)", "0"),
        (11, "Box 3", "Total VAT due (Box 1 + Box 2)", "=E9+E10"),
        (12, "Box 4", "VAT reclaimed on purchases and other inputs", "=('Bank Payment Analysis'!G1000+'Purchase Invoices'!F1000)*E5"),
        (13, "Box 5", "Net VAT to pay / (reclaim)", "=E11-E12"),
        (14, "Box 6", "Total value of sales & outputs ex VAT", "=ROUND(SUMIF('Banking Analysis'!F6:F500,\"SR\",'Banking Analysis'!H6:H500)+SUMIF('Banking Analysis'!F6:F500,\"ZR\",'Banking Analysis'!H6:H500)+SUMIF('Banking Analysis'!F6:F500,\"EX\",'Banking Analysis'!H6:H500)+SUMIF('Banking Analysis'!F6:F500,\"OS\",'Banking Analysis'!H6:H500)+SUMIF('Banking Analysis'!F6:F500,\"NV\",'Banking Analysis'!H6:H500),0)"),
        (15, "Box 7", "Total value of purchases & inputs ex VAT", "=ROUND(SUMIF('Bank Payment Analysis'!F6:F800,\"SR\",'Bank Payment Analysis'!H6:H800)+SUMIF('Bank Payment Analysis'!F6:F800,\"ZR\",'Bank Payment Analysis'!H6:H800)+SUMIF('Bank Payment Analysis'!F6:F800,\"EX\",'Bank Payment Analysis'!H6:H800)+SUMIF('Bank Payment Analysis'!F6:F800,\"NV\",'Bank Payment Analysis'!H6:H800)+SUMIF('Bank Payment Analysis'!F6:F800,\"OS\",'Bank Payment Analysis'!H6:H800),0)"),
        (16, "Box 8", "Total value of dispatches (NI/EU) ex VAT", "0"),
        (17, "Box 9", "Total value of acquisitions (NI/EU) ex VAT", "0"),
    ]
    for r, box, label, formula in boxes:
        ws.cell(r, 1, box).font = _font(10, True)
        ws.cell(r, 2, label).font = _font(10)
        ws.cell(r, 5, formula).font = _font(10, r in (11, 13))
        ws.cell(r, 5).number_format = _MONEY
        for c in range(1, 6):
            ws.cell(r, c).border = _THIN
        if r in (11, 13):
            ws.cell(r, 5).fill = _fill(BLUE_ROW)
    ws.merge_cells("A19:E21")
    ws["A19"] = (
        "Boxes are formula-driven from the bank analysis tabs. "
        "This is a draft working file for the accountant, not a submission to HMRC. "
        "Sales/purchase invoice tabs are placeholders until invoice matching is in scope."
    )
    ws["A19"].font = _font(9, False, "5C6570")
    ws["A19"].alignment = Alignment(wrap_text=True, vertical="top")
    ws.sheet_view.showGridLines = False
