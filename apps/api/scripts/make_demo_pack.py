"""Fictional Northbridge Demo Ltd pack. Not a real MA client.

Shape matches Faraz's workflow: Countingup CSV + prior-year Banking/Bank Pay.
Known payees auto-code. New payees, Private, and one duplicate become questions.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from io import BytesIO
from pathlib import Path

from openpyxl import Workbook

OUT = Path(__file__).resolve().parents[1] / "app" / "static" / "demo"


def _csv() -> str:
    # Newest-first, like Countingup. Opening 12,000; movements must tie.
    rows = [
        ("2026-02-27", "Bright Forge Ltd", "", "1000.00", "10948.40"),
        ("2026-02-20", "HMRC VAT", "", "420.00", "11948.40"),
        ("2026-02-18", "Uber Eats", "", "24.60", "12368.40"),
        ("2026-02-14", "Tesco Stores", "", "86.20", "12393.00"),
        ("2026-02-14", "Tesco Stores", "", "86.20", "12479.20"),
        ("2026-02-10", "O2", "", "51.91", "12565.40"),
        ("2026-02-05", "Client ABC Ltd", "2500.00", "", "12617.31"),
        ("2026-02-03", "Sage Payroll", "", "1800.00", "10117.31"),
        ("2026-02-01", "Castles Estates", "", "95.00", "11917.31"),
        ("2026-01-22", "Lime Cycle Hire", "", "18.00", "12012.31"),
        ("2026-01-15", "NCP Car Parks", "", "12.40", "12030.31"),
        ("2026-01-08", "HMRC PAYE", "", "310.00", "12042.71"),
        ("2026-01-04", "Client ABC Ltd", "1800.00", "", "12352.71"),
        ("2025-12-18", "Tesco Stores", "", "64.10", "10552.71"),
        ("2025-12-12", "O2", "", "51.91", "10616.81"),
        ("2025-12-02", "Directors Draw", "", "500.00", "10668.72"),
    ]
    # Verify rec from last (oldest) balance.
    lines = [
        "Date,Cleared date,Description,Category,Reference,Paid in (£),Paid out (£),Balance (£)"
    ]
    for d, desc, inn, out, bal in rows:
        lines.append(f"{d},{d},{desc},Misc,,{inn},{out},{bal}")
    return "\n".join(lines) + "\n"


def _comparative() -> bytes:
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    navy = "1F4E78"
    header = Font(name="Arial", size=10, bold=True, color="FFFFFF")
    title = Font(name="Arial", size=16, bold=True, color=navy)
    sub = Font(name="Arial", size=11, bold=True)
    body = Font(name="Arial", size=10)
    fill_navy = PatternFill("solid", fgColor=navy)
    thin = Border(
        left=Side(style="thin", color="D9D1C3"),
        right=Side(style="thin", color="D9D1C3"),
        top=Side(style="thin", color="D9D1C3"),
        bottom=Side(style="thin", color="D9D1C3"),
    )

    wb = Workbook()

    notes = wb.active
    notes.title = "Notes and queries"
    notes["A1"] = "NORTHBRIDGE DEMO LTD"
    notes["A1"].font = title
    notes["A2"] = "Notes and Queries"
    notes["A2"].font = sub
    notes["A3"] = "FOR THE YEAR ENDED 28TH FEBRUARY 2025"
    notes["A5"] = "Fictional pack for Bridgit trials. Not a real MA client."
    notes["A5"].font = body
    notes.column_dimensions["A"].width = 88

    idx = wb.create_sheet("Index")
    idx["A1"] = "NORTHBRIDGE DEMO LTD"
    idx["A1"].font = title
    idx["A2"] = "INDEX"
    idx["A2"].font = sub
    idx["A4"] = "Banking / Bank Pay / Bank Rec are the working tabs Bridgit rewrites."
    idx["A4"].font = body

    from app.engine.ma_template import paint_bank_rec

    rec = wb.create_sheet("Bank Rec")
    paint_bank_rec(
        rec,
        company="NORTHBRIDGE DEMO LTD",
        period="FOR THE YEAR ENDED 28TH FEBRUARY 2025",
        receipts_formula="=Banking!C10",
        payments_formula="=-'Bank Pay'!C16",
        opening=11168.72,
        closing=10668.72,
        receipts_label="Add: Receipts in the year (Banking tab total)",
        payments_label="Less: Payments in the year (Bank Pay tab total)",
    )

    banking = wb.create_sheet("Banking")
    banking["A1"] = "NORTHBRIDGE DEMO LTD"
    banking["A1"].font = title
    banking["A2"] = "Summary of Bankings"
    banking["A2"].font = sub
    banking["A3"] = "FOR THE YEAR ENDED 28TH FEBRUARY 2025"
    for col, name in enumerate(
        [
            "Date",
            "Details",
            "Amount",
            "Sales",
            "Refund",
            "Contra",
            "Grant",
            "Suspense",
            "Other income",
            "PRS",
            "Director",
        ],
        start=1,
    ):
        cell = banking.cell(6, col, name)
        cell.font = header
        cell.fill = fill_navy
        cell.alignment = Alignment(horizontal="center")
        cell.border = thin
    banking.cell(7, 3).value = "£"
    banking.cell(7, 3).font = Font(name="Arial", size=10, bold=True)
    banking.cell(8, 1).value = date(2025, 2, 1)
    banking.cell(8, 1).number_format = "mmm-yy"
    banking.cell(8, 1).font = Font(name="Arial", size=10, bold=True)
    banking.cell(9, 1).value = date(2025, 2, 5)
    banking.cell(9, 1).number_format = "DD/MM/YYYY"
    banking.cell(9, 2).value = "Client ABC Ltd"
    banking.cell(9, 3).value = 1800
    banking.cell(9, 3).number_format = "0.00"
    banking.cell(9, 4).value = "=C9"
    banking.cell(10, 2).value = "TOTAL"
    banking.cell(10, 2).font = Font(name="Arial", size=10, bold=True)
    banking.cell(10, 3).value = "=SUM(C8:C9)"
    banking.freeze_panes = "C8"
    banking.column_dimensions["A"].width = 12
    banking.column_dimensions["B"].width = 28
    banking.column_dimensions["C"].width = 12

    pay = wb.create_sheet("Bank Pay")
    pay["A1"] = "NORTHBRIDGE DEMO LTD"
    pay["A1"].font = title
    pay["A2"] = "Summary of Bank Payments"
    pay["A2"].font = sub
    pay["A3"] = "FOR THE YEAR ENDED 28TH FEBRUARY 2025"
    pay.cell(4, 4).value = "Cost of"
    pay.cell(5, 1).value = "Date"
    pay.cell(5, 2).value = "Details"
    pay.cell(5, 3).value = "Amount"
    pay.cell(5, 4).value = "sales"
    pay.cell(5, 5).value = "Phone"
    pay.cell(5, 6).value = "Motor"
    pay.cell(5, 7).value = "Salaries"
    pay.cell(5, 8).value = "Private"
    pay.cell(5, 9).value = "Accountancy"
    pay.cell(5, 10).value = "Directors Remuneration"
    for col in range(1, 11):
        pay.cell(5, col).font = header
        pay.cell(5, col).fill = fill_navy
    pay.cell(6, 3).value = "£"

    def pay_row(row, desc, amount, col):
        pay.cell(row, 1).value = row - 6
        pay.cell(row, 2).value = desc
        pay.cell(row, 2).font = body
        pay.cell(row, 3).value = amount
        pay.cell(row, 3).number_format = "0.00"
        pay.cell(row, col).value = f"=C{row}"

    pay_row(8, "O2", 51.91, 5)
    pay_row(9, "Tesco Stores", 64.10, 6)
    pay_row(10, "Sage Payroll", 1800.00, 7)
    pay_row(11, "Uber Eats", 18.40, 8)
    pay_row(12, "Castles Estates", 95.00, 9)
    pay_row(13, "Directors Draw", 500.00, 10)
    pay_row(14, "HMRC VAT", 400.00, 4)
    pay_row(15, "HMRC PAYE", 310.00, 7)
    pay.cell(16, 2).value = "TOTAL"
    pay.cell(16, 2).font = Font(name="Arial", size=10, bold=True)
    pay.cell(16, 3).value = "=SUM(C8:C15)"
    pay.freeze_panes = "C7"
    pay.column_dimensions["B"].width = 28

    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUT / "northbridge-bank.csv"
    xlsx_path = OUT / "northbridge-comparative.xlsx"
    csv_path.write_text(_csv(), encoding="utf-8")
    xlsx_path.write_bytes(_comparative())
    from app.engine.yearend_map import mappings_from_workbook_bytes
    from app.ingest.tabular import parse_csv

    parsed = parse_csv(csv_path.read_bytes(), file_name=csv_path.name)
    maps = mappings_from_workbook_bytes(xlsx_path.read_bytes())
    rec_ok = parsed.opening_balance is not None
    print("wrote", csv_path)
    print("wrote", xlsx_path)
    print("bank lines", len(parsed.transactions), "opening", parsed.opening_balance, "close", parsed.closing_balance)
    print("payee maps", {m["description_pattern"]: m["account_name"] for m in maps})
    if not rec_ok:
        raise SystemExit("demo CSV has no opening balance")
    in_amt = sum((t.amount for t in parsed.transactions if t.debit_credit == "credit"), Decimal("0"))
    out_amt = sum((t.amount for t in parsed.transactions if t.debit_credit == "debit"), Decimal("0"))
    calc = (parsed.opening_balance + in_amt - out_amt).quantize(Decimal("0.01"))
    print("rec calc", calc, "diff", (calc - parsed.closing_balance).quantize(Decimal("0.01")))


if __name__ == "__main__":
    main()
