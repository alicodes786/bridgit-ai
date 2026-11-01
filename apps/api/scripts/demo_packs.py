"""Shared helpers + pack definitions for fictional Bridgit demo clients."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from io import BytesIO
from pathlib import Path

from openpyxl import Workbook


@dataclass(frozen=True)
class DemoPack:
    slug: str
    legal_name: str
    story: str
    opening: Decimal
    txns: tuple[tuple[str, str, str, str], ...]
    prior_open: float
    prior_close: float
    banking_total_row: int
    pay_total_row: int
    banking_rows: tuple[tuple[str, float, int], ...]  # desc, amount, sales col=4
    pay_rows: tuple[tuple[str, float, int], ...]  # desc, amount, col index


def csv_from_pack(pack: DemoPack) -> str:
    bal = pack.opening
    rows: list[tuple[str, str, str, str, str]] = []
    for d, desc, inn, out in pack.txns:
        inn_d = Decimal(inn or "0")
        out_d = Decimal(out or "0")
        bal = (bal + inn_d - out_d).quantize(Decimal("0.01"))
        rows.append((d, desc, inn, out, str(bal)))
    lines = [
        "Date,Cleared date,Description,Category,Reference,Paid in (£),Paid out (£),Balance (£)"
    ]
    for d, desc, inn, out, b in reversed(rows):
        lines.append(f"{d},{d},{desc},Misc,,{inn},{out},{b}")
    return "\n".join(lines) + "\n"


def comparative_from_pack(pack: DemoPack) -> bytes:
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    from app.engine.ma_template import paint_bank_rec

    name = pack.legal_name.upper()
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
    notes["A1"] = name
    notes["A1"].font = title
    notes["A2"] = "Notes and Queries"
    notes["A2"].font = sub
    notes["A3"] = "FOR THE YEAR ENDED 28TH FEBRUARY 2025"
    notes["A5"] = "Fictional pack for Bridgit live trials. Not a real MA client."
    notes["A5"].font = body
    notes.column_dimensions["A"].width = 88

    rec = wb.create_sheet("Bank Rec")
    paint_bank_rec(
        rec,
        company=name,
        period="FOR THE YEAR ENDED 28TH FEBRUARY 2025",
        receipts_formula=f"=Banking!C{pack.banking_total_row}",
        payments_formula=f"=-'Bank Pay'!C{pack.pay_total_row}",
        opening=pack.prior_open,
        closing=pack.prior_close,
        receipts_label="Add: Receipts in the year (Banking tab total)",
        payments_label="Less: Payments in the year (Bank Pay tab total)",
    )

    banking = wb.create_sheet("Banking")
    banking["A1"] = name
    banking["A1"].font = title
    banking["A2"] = "Summary of Bankings"
    banking["A2"].font = sub
    banking["A3"] = "FOR THE YEAR ENDED 28TH FEBRUARY 2025"
    headers = [
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
    ]
    for col, h in enumerate(headers, start=1):
        cell = banking.cell(6, col, h)
        cell.font = header
        cell.fill = fill_navy
        cell.alignment = Alignment(horizontal="center")
        cell.border = thin
    banking.cell(7, 3).value = "£"
    row = 8
    for desc, amount, sales_col in pack.banking_rows:
        banking.cell(row, 1).value = date(2025, 2, 10 + row)
        banking.cell(row, 1).number_format = "DD/MM/YYYY"
        banking.cell(row, 2).value = desc
        banking.cell(row, 3).value = amount
        banking.cell(row, 3).number_format = "0.00"
        banking.cell(row, sales_col).value = f"=C{row}"
        row += 1
    total_row = row
    banking.cell(total_row, 2).value = "TOTAL"
    banking.cell(total_row, 2).font = Font(name="Arial", size=10, bold=True)
    banking.cell(total_row, 3).value = f"=SUM(C8:C{total_row - 1})"
    banking.freeze_panes = "C8"

    pay = wb.create_sheet("Bank Pay")
    pay["A1"] = name
    pay["A1"].font = title
    pay["A2"] = "Summary of Bank Payments"
    pay["A2"].font = sub
    pay["A3"] = "FOR THE YEAR ENDED 28TH FEBRUARY 2025"
    pay_headers = [
        "Date",
        "Details",
        "Amount",
        "Cost of sales",
        "Phone",
        "Motor",
        "Salaries",
        "Private",
        "Accountancy",
        "Directors Remuneration",
        "IT and software",
        "Rent",
        "Subcontractors",
    ]
    for col, h in enumerate(pay_headers, start=1):
        pay.cell(5, col).value = h
        pay.cell(5, col).font = header
        pay.cell(5, col).fill = fill_navy
    pay.cell(6, 3).value = "£"
    prow = 8
    for desc, amount, col in pack.pay_rows:
        pay.cell(prow, 1).value = prow - 6
        pay.cell(prow, 2).value = desc
        pay.cell(prow, 2).font = body
        pay.cell(prow, 3).value = amount
        pay.cell(prow, 3).number_format = "0.00"
        pay.cell(prow, col).value = f"=C{prow}"
        prow += 1
    pay_total = prow
    pay.cell(pay_total, 2).value = "TOTAL"
    pay.cell(pay_total, 2).font = Font(name="Arial", size=10, bold=True)
    pay.cell(pay_total, 3).value = f"=SUM(C8:C{pay_total - 1})"
    pay.freeze_panes = "C7"
    pay.column_dimensions["B"].width = 28

    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


NORTHBRIDGE = DemoPack(
    slug="northbridge",
    legal_name="Northbridge Demo Ltd",
    story="Small brand-design consultancy (legacy demo name).",
    opening=Decimal("11168.72"),
    txns=(
        ("2025-11-15", "Stationery World Ltd", "", "45.20"),
        ("2025-11-28", "Canva Subscription", "", "12.99"),
        ("2025-12-02", "Directors Draw", "", "500.00"),
        ("2025-12-12", "O2", "", "51.91"),
        ("2025-12-18", "Tesco Stores", "", "64.10"),
        ("2025-12-20", "Client ABC Ltd", "1295.19", ""),
        ("2026-01-02", "MA Associates Ltd", "", "180.00"),
        ("2026-01-04", "Client ABC Ltd", "1800.00", ""),
        ("2026-01-08", "HMRC PAYE", "", "310.00"),
        ("2026-01-15", "NCP Car Parks", "", "12.40"),
        ("2026-01-22", "Lime Cycle Hire", "", "18.00"),
        ("2026-01-28", "Amazon Web Services", "", "89.00"),
        ("2026-02-01", "Castles Estates", "", "95.00"),
        ("2026-02-03", "Sage Payroll", "", "1800.00"),
        ("2026-02-05", "Client ABC Ltd", "2500.00", ""),
        ("2026-02-08", "Client XYZ Design Ltd", "3200.00", ""),
        ("2026-02-10", "O2", "", "51.91"),
        ("2026-02-12", "Github Inc", "", "18.00"),
        ("2026-02-14", "Tesco Stores", "", "86.20"),
        ("2026-02-14", "Tesco Stores", "", "86.20"),
        ("2026-02-18", "Uber Eats", "", "24.60"),
        ("2026-02-20", "HMRC VAT", "", "420.00"),
        ("2026-02-27", "Bright Forge Ltd", "", "1000.00"),
    ),
    prior_open=11168.72,
    prior_close=10668.72,
    banking_total_row=10,
    pay_total_row=21,
    banking_rows=(
        ("Client ABC Ltd", 1800, 4),
        ("Client XYZ Design Ltd", 2100, 4),
    ),
    pay_rows=(
        ("O2", 51.91, 5),
        ("Tesco Stores", 64.10, 6),
        ("Sage Payroll", 1800.00, 7),
        ("Uber Eats", 18.40, 8),
        ("Castles Estates", 95.00, 9),
        ("MA Associates Ltd", 175.00, 9),
        ("Directors Draw", 500.00, 10),
        ("HMRC VAT", 400.00, 4),
        ("HMRC PAYE", 310.00, 7),
        ("Canva Subscription", 10.99, 11),
        ("Amazon Web Services", 72.00, 11),
        ("Stationery World Ltd", 38.50, 12),
        ("Bright Forge Ltd", 850.00, 13),
    ),
)

MERIDIAN = DemoPack(
    slug="meridian-studio",
    legal_name="Meridian Studio Ltd",
    story="Architecture visualisation studio — use this name for fresh live tests.",
    opening=Decimal("9420.50"),
    txns=(
        ("2025-11-10", "Office Depot UK", "", "62.40"),
        ("2025-11-22", "Adobe Systems", "", "54.99"),
        ("2025-12-01", "Directors Draw", "", "400.00"),
        ("2025-12-09", "Vodafone Ltd", "", "48.50"),
        ("2025-12-14", "Sainsbury's", "", "71.30"),
        ("2025-12-19", "Apex Interiors Ltd", "1100.00", ""),
        ("2026-01-03", "MA Associates Ltd", "", "195.00"),
        ("2026-01-06", "Horizon Architects", "2400.00", ""),
        ("2026-01-11", "HMRC PAYE", "", "285.00"),
        ("2026-01-17", "ParkBee Parking", "", "9.80"),
        ("2026-01-24", "WeWork Rent", "", "420.00"),
        ("2026-01-29", "Figma Inc", "", "15.00"),
        ("2026-02-02", "BrightPay Payroll", "", "1650.00"),
        ("2026-02-06", "Render Hive Ltd", "", "750.00"),
        ("2026-02-09", "Horizon Architects", "3100.00", ""),
        ("2026-02-11", "Vodafone Ltd", "", "48.50"),
        ("2026-02-13", "Sainsbury's", "", "71.30"),
        ("2026-02-13", "Sainsbury's", "", "71.30"),
        ("2026-02-16", "Deliveroo", "", "22.45"),
        ("2026-02-19", "HMRC VAT", "", "380.00"),
        ("2026-02-26", "Slate Creative Ltd", "1850.00", ""),
        ("2026-02-28", "Render Hive Ltd", "", "920.00"),
    ),
    prior_open=9420.50,
    prior_close=8910.50,
    banking_total_row=10,
    pay_total_row=21,
    banking_rows=(
        ("Apex Interiors Ltd", 1100.0, 4),
        ("Horizon Architects", 2400, 4),
    ),
    pay_rows=(
        ("Vodafone Ltd", 48.50, 5),
        ("Sainsbury's", 71.30, 6),
        ("BrightPay Payroll", 1650.00, 7),
        ("Deliveroo", 22.45, 8),
        ("WeWork Rent", 420.00, 12),
        ("MA Associates Ltd", 190.00, 9),
        ("Directors Draw", 400.00, 10),
        ("HMRC VAT", 380.00, 4),
        ("HMRC PAYE", 285.00, 7),
        ("Adobe Systems", 54.99, 11),
        ("Figma Inc", 12.00, 11),
        ("Office Depot UK", 55.00, 6),
        ("Render Hive Ltd", 800.00, 13),
    ),
)

ALL_PACKS = (NORTHBRIDGE, MERIDIAN)


def write_pack(out_dir: Path, pack: DemoPack) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = pack.slug
    (out_dir / f"{slug}-bank.csv").write_text(csv_from_pack(pack), encoding="utf-8")
    (out_dir / f"{slug}-comparative.xlsx").write_bytes(comparative_from_pack(pack))


def brief_meridian() -> str:
    return """MERIDIAN STUDIO LTD — Bridgit live trial pack (fictional) ★ use this on Railway
================================================================================

Client story
  Architecture visualisation studio. Countingup-style CSV + last-year MA Excel.
  Period: 1 Mar 2025 – 28 Feb 2026. Company accounts (year-end).

Files (New job — upload bank + comparative together)
  1. meridian-studio-bank.csv
  2. meridian-studio-comparative.xlsx
  3. Optional later: meridian-studio-insurance-note.txt (Chat → Add files)

Auto-code from last year (after first process)
  Vodafone → Phone, Sainsbury's → Motor, BrightPay → Salaries, WeWork → Rent,
  Adobe/Figma → IT and software, Render Hive → Subcontractors, HMRC, MA Associates,
  Directors Draw, Apex / Horizon → Sales.

Questions you should see
  • Duplicate Sainsbury's on 13 Feb (same amount) — choose Keep both once
  • ParkBee, Deliveroo, Slate Creative Ltd — new payee or Private / Sales
  • Period coverage — answer once if asked; re-upload same CSV should remember

Full step-by-step live checklist: docs/ai-accounting/38-live-test-playbook.md
"""


def brief_northbridge() -> str:
    return """NORTHBRIDGE DEMO LTD — older demo name (same engine, different payees)
See meridian-studio-demo-brief.txt for the recommended live pack.
"""
