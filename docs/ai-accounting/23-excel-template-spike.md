# 23. Excel Template Spike — Koliqi & Sons

> **Purpose:** Understand the exact write surface before building the output writer.
> Do this before writing output code — not after.
> **Date:** 15 Sep 2026
> **Workbook:** `data/client/koliqi-sons/Koliqi_Sons_VAT_File_May-Jun_2026 (FN CL).xlsx`

---

## Sheets in the template

| Sheet | Role | Bridgit writes? |
|---|---|---|
| Notes & Queries | Free-text notes for the accountant | No |
| Bank Reconciliation | Auto-calculates from Banking Analysis totals | Opening + closing balance only |
| Banking Analysis | Money IN — one row per receipt | ✅ Yes — data rows from row 6 + update anchor |
| Bank Payment Analysis | Money OUT — one row per payment | ✅ Yes — data rows from row 6 + update anchor |
| Sales Invoices | Invoice listing (output VAT) | No (Phase 2) |
| Purchase Invoices | Invoice listing (input VAT) | No (Phase 2) |
| VAT Calculation | Draft VAT return boxes 1–9 | No — fully formula-driven |

---

## What Bridgit writes into Banking Analysis (money in)

**Columns A–H, starting at row 6:**

| Col | Field | Notes |
|---|---|---|
| A | Date | `date` — format as DD/MM/YYYY |
| B | Type | Payment type (CHAPS, FASTER PAYMENT, CHIP & PIN, etc.) |
| C | Detail | Transaction description |
| D | Received (£) | Amount in |
| E | Category | Account category name from `ai_mappings` |
| F | Code | VAT code (SR / ZR / EX / NV / OS) |
| G | Output VAT | VAT amount (0 for NV/OS/EX) |
| H | Net (ex VAT) | Net amount |

**Also update row 1000 (anchor row):**
```
D1000 = =SUM(D6:D{last_row})
G1000 = =SUM(G6:G{last_row})
H1000 = =SUM(H6:H{last_row})
```
This row is what Bank Reconciliation and VAT Calculation pull their totals from.

---

## What Bridgit writes into Bank Payment Analysis (money out)

**Identical column structure. Columns A–H, starting at row 6:**

| Col | Field | Notes |
|---|---|---|
| A | Date | |
| B | Type | |
| C | Detail | |
| D | Paid (£) | Amount out (positive) |
| E | Category | |
| F | Code | VAT code |
| G | Input VAT | VAT amount recoverable |
| H | Net (ex VAT) | |

**Update row 1000 anchor:**
```
D1000 = =SUM(D6:D{last_row})
G1000 = =SUM(G6:G{last_row})
H1000 = =SUM(H6:H{last_row})
```

---

## Bank Reconciliation — manual input cells only

**Bridgit writes 2 cells:**
- `E8` — Opening balance (from bank statement)
- `E12` — Closing balance (from bank statement)

Everything else is formula-driven:
- `E9` = `='Banking Analysis'!D1000` (total receipts — auto)
- `E10` = `=-'Bank Payment Analysis'!D1000` (total payments — auto)
- `E11` = `=E8+E9+E10` (calculated closing — auto)
- `E13` = `=E11-E12` (difference — must be nil)

**Bank rec is the hard gate.** Bridgit reads `E13` after writing. If not nil (within £0.01 rounding), job does not proceed to review.

---

## VAT Calculation — fully formula-driven, do not touch

All 9 VAT return boxes calculate automatically from the anchor rows and SUMIF across data:
- Box 1: `='Banking Analysis'!G1000+'Sales Invoices'!G1000`
- Box 4: `=('Bank Payment Analysis'!G1000+'Purchase Invoices'!F1000)*E5`
- Boxes 6/7: SUMIF across `F6:F200` / `F6:F400` for SR/ZR/EX codes

Bridgit does not write here. It reads Box 5 (Net VAT to pay/reclaim) for the job summary.

---

## Capacity limits (existing formulas)

| Sheet | SUMIF range covers | Max rows before formula update needed |
|---|---|---|
| Banking Analysis | `F6:F200` | 195 receipt rows |
| Bank Payment Analysis | `F6:F400` | 395 payment rows |

For typical MA clients these limits are fine. Flag in code if row count approaches limit.

---

## What Bridgit's output writer must do — in order

1. Load the blank template from Supabase Storage
2. Write receipt rows into Banking Analysis (A6:H{N})
3. Update anchor formula: Banking Analysis row 1000, cols D/G/H
4. Write payment rows into Bank Payment Analysis (A6:H{M})
5. Update anchor formula: Bank Payment Analysis row 1000, cols D/G/H
6. Write opening balance into Bank Rec `E8`
7. Write closing balance into Bank Rec `E12`
8. Read Bank Rec `E13` — must be ≈ 0 (bank rec gate)
9. Read VAT Calc `E12` (Box 5) for the PDF summary
10. Save as new file, upload to Supabase Storage, attach to job

**Python library:** `openpyxl` — already in requirements.

**Writer status (17 Sep):** `app/engine/excel_writer.py` implements this write surface. It uses the Koliqi workbook as the template until a blank official file is stored in Supabase. Duplicates are not written as extra rows.

---

## Bottom line

The template is well-structured. Bridgit writes into two data sheets + 2 manual cells
in Bank Rec. Everything else is formula-linked and auto-calculates. No formula surgery
needed — just update the anchor SUM row after writing data. Simpler than the risk implied.

**The only genuine complexity:** the anchor row formula range (`D6:D{N}`) must match
the actual data row count. The output writer must track this and update it.
