# Hit Hunters Ltd — Year-End Accounts Prep: Agent Process Log
Purpose: exact, repeatable steps + the prompts/decision rules used to roll forward a
year-end accounts workbook from a prior-year file + a bank-transaction CSV.
Target agent should follow these steps in order.

> **Received from Faraz 26 Sep 2026** with the comparative file, 2026 CSV, and
> completed 2026 workbook. This log **is** the SOP / “Claude prompts” extract.
> Do not treat it as a dump — Bridgit should follow it in order.
> Files: [28-client-files-hithunters.md](./28-client-files-hithunters.md).
> How this changes the build: [29-sep26-hithunters-and-job-catalog.md](./29-sep26-hithunters-and-job-catalog.md).
> Job catalog: [27-job-types-catalog.md](./27-job-types-catalog.md).

## Context / inputs
- **Prior-year file**: `Hit_Hunters_Ltd_Accounts_28_02_2025_...xlsx` — full statutory pack, 21 tabs.
  The ETB is the engine: Opening balances + Bank movements + Journals + Accruals -> P&L + Balance Sheet.
- **Current-year data**: `..._Transactions_2025-03-01_to_2026-02-28.csv` — one Countingup bank account,
  168 rows, columns incl. Date, Description, Category, Reference, Paid in (£), Paid out (£), Balance (£).
- **Deliverable**: new file `Hit_Hunters_Ltd_Accounts_28_02_2026.xlsx`, same 21 tabs, dates rolled,
  2025 actuals moved into comparative columns, opening balances = prior-year closing.

## Global rules (confirmed with client)
1. **Code by PAYEE, mirroring exactly how each payee was treated in the prior year.** The CSV's own
   `Category` column is unreliable (it lumps unlike items) — use it only as a hint for brand-new payees.
2. A £1,000+ round receipt is only a director deposit if it is in the **director's own name**. A receipt
   carrying an **invoice reference / sort code / Ltd company name** is genuine sales income.
3. Director's remuneration follows the client instruction for the year (this year: **NIL — no payroll**).
4. Any legacy bank reconciling difference is cleared **via a journal**, not by touching the bank listing.
5. Personal Tax (property element) is **estimated by rolling forward** the prior year unless data supplied.

## PHASE 1 — Banking & Bank Payment listings (this deliverable)

### Step 1 — Inspect prior-year workbook structure
- Prompt: "Enumerate every tab; dump each tab's populated cells (values) to learn the layout and the ETB flow."
- Note the two analysis tabs:
  - **Banking** (money IN): cols A Date, B Details, C Amount, then category echo cols
    D Income · E Refund · F Contra · G Grant · H Suspense · I Copyright · J PRS · K Director;
    L = per-row check `=SUM(D:K)-C`. Month-marker rows (1st of month, fmt `mmm-yy`, bold) precede each
    month's transactions; transaction rows carry the full date (fmt `mm-dd-yy`). TOTAL row = SUM per column.
  - **Bank Pay** (money OUT): cols A Day, B Details, C Amount, then 26 category echo cols D..AC
    (D Bank Charges, E Acc Fees, F Barclays, G Utilities, H Prof Fees, I financial serv, J Mortgage,
    K Website/Subscription, L Equipment Expensed, M Premises, N Equipment Assets, O Work Clothing,
    P Insurance, Q Phone, R Advertising, S Staff, T Council Tax, U Suspense, V Private, W DirectorSA HMRC,
    X Corp HMRC, Y Contra, Z Travel, AA Director, AB Charity, AC Motor Expense);
    AD = per-row check `=SUM(D:AC)-C`. Month-marker rows (1st of month, `mmm-yy`, bold);
    transaction rows carry day-of-month integer in col A. TOTAL row = SUM per column.
- Coding mechanic: the Amount (col C) is a literal; the assigned category cell holds `=C{row}` (echo).

### Step 2 — Extract the prior-year payee->column map (money out)
- Prompt: "For each Bank Pay data row, find the column holding `=C{row}` and map Details -> that column;
  aggregate to the dominant column per payee."
- Store the resulting dictionary (normalise payee: take text before ';', strip, lower-case).

### Step 3 — Reconcile the opening balance BEFORE coding
- CSV is newest-first; sort ascending. The earliest row's running balance + that row's movement gives the
  opening balance. Confirm it equals the prior-year **bank-statement** closing (here £24,704.55). ✔ matched.
- Compute expected close = opening + total in − total out, and confirm it equals the CSV's latest balance
  (here £32,945.01). ✔ ties to the penny.

### Step 4 — Classify current-year lines by payee
- Money OUT: apply the Step-2 map (exact, then prefix, then keyword match).
- Money IN: `Mechanical Copyrig` -> I (Copyright); every other Sales receipt -> D (Income).
  (Note: prior year deliberately labels the Copyright column as "PRS Royalty Income" in the P&L and puts
  actual PRS receipts into "Other Production Fees" — mirror this.)
- List any UNMATCHED payee (new this year) for a human decision; never silently guess into Suspense.

### Step 5 — Build the two tabs into a copy of the prior-year file
- Prompt: "shutil.copy the prior-year file to the new name (preserves all tabs/formatting); rewrite only
  Banking and Bank Pay; update the A3 title to 'FOR THE YEAR ENDED 28TH FEBRUARY 2026'."
- Preserve formatting by copying each template cell's `_style` (Arial 10; accounting number format
  `_-* #,##0.00_-;...`; month markers bold `mmm-yy`). Write month-marker rows + transaction rows +
  the echo formula in the mapped column + the per-row check formula, then a bold TOTAL row of SUMs.

### Step 6 — Recalculate and validate (mandatory)
- Run `recalc.py` (LibreOffice) -> must report `status: success`, `total_errors: 0`.
- Validate: every per-row check (AD / L) = 0; each column TOTAL sums correctly; allocated = amount total;
  and opening + in − out = statement close. All must tie before sign-off.

### Phase-1 result (28.02.2026)
- Money in £20,001.01 = Income £19,656.99 + Copyright £344.02.
- Money out £11,760.55, fully allocated across 10 category columns; all checks = 0.
- Bank ties: £24,704.55 + £20,001.01 − £11,760.55 = £32,945.01. ✔

## PHASE 2 — roll forward ETB → P&L → Balance Sheet → Notes → Corp Tax → Personal Tax

**Golden rule of this file:** the ETB is the ONLY engine. Every statement/note/tax page pulls its
*current-year* column from the ETB by formula; only the *comparative* columns are hardcoded. So the
roll-forward is four moves: (a) reset ETB openings, (b) re-point ETB inputs to the new bank-tab total
rows, (c) post this year's journals, (d) overwrite comparatives with last year's actuals + roll dates.
Do NOT re-key current-year statement figures — they compute themselves once the ETB is right.

### Step 7 — Map the dependency chain first (before editing anything)
- Dump every formula in ETB, Pg 6–11, Corp Tax, Personal Tax, Bank Rec, Director Ctrl, Journal enties.
- Confirm which column on each page is current vs comparative:
  Pg6 F/H · Pg7 G/I · Pg8 G/I · Pg9 **E&G both current** (Equipment/Total) for the fixed-asset note rows
  8–18, then E/G current/comparative for debtors–creditors rows 21–38 · Pg10 G/I · Pg11 D&C/F ·
  Corp Tax I/L · Personal Tax E/G.  ⚠️ Pg 9 is the trap: rows 8–18 column G is a live `=E..` total, NOT a
  comparative. Overwriting it silently breaks the balance sheet by the depreciation charge.

### Step 8 — Reset ETB opening balances (2026 opening = 2025 closing)
- Equipment cost B42 14724.17; acc-dep C42 11725.9412; Bank B44 24908.55; B Card B46 2290.26;
  DLA C52 57664.88; Retained C54 −29663.843394520034; Corp tax C55 0.

### Step 9 — Re-point ETB inputs to the rebuilt bank tabs
- Phase-1 moved the totals (Banking 37→39, Bank Pay 287→169). Regex every ETB formula:
  `Banking!<col>37`→`39`, `'Bank Pay'!<col>287`→`169`. Also re-point Bank Rec B11/C13.

### Step 10 — Post 2026 journals (must self-balance in ETB F/G columns)
- **Director remuneration NIL** (was £9,600): Journal E20 = 0 → ETB F19 & DLA G52 fall to 0; the
  £9,600 employment line on Personal Tax auto-drops to £0.
- **Clear legacy £204 bank difference** [default, no P&L impact]: Cr Bank (ETB G44 = 204, and
  K44 = `B44+D44-E44-G44`) / Dr DLA (ETB F52 = `G55+204`). Documented in Journal enties block.
  Result: ETB bank c/f ties to statement £32,945.01; ETB M44 shows opening gap 204, O44 closing 0.
- **Corp-tax writeback** journal (2025's £4,536.17) not needed — 2026 opening corp tax is nil.
- Retained-reserve link: ETB J54 = `=-'Pg 11'!D47` (year result flows in automatically).

### Step 11 — Comparatives = 2025 actuals; then roll dates
- Read each page's 2025 *current-year* values and write them into the 2026 *comparative* column
  (Pg6 H, Pg7 I, Pg8 I, Pg9 G rows 21–38 only, Pg10 I, Pg11 F, Corp Tax L, Personal Tax G).
- Corp Tax loss chain: I15 (losses b/f) = `=+L16`, so set L16 = 2025 losses c/f (−27,250.96).
- Dates: string-replace titles/labels (`28TH FEBRUARY 2025→2026`, `01.03.2024→2025`, `2024-25→2025-26`,
  POA `2026→2027`, etc.) applied high-year-first to avoid cascade; set integer year headers
  (current 2026 / comparative 2025) on Pg6–11.

### Step 12 — Recalc + prove it balances
- `recalc.py` → success, 0 errors. Then assert every identity:
  ETB opening TB Dr=Cr; ETB K56=L56; Bank Rec D17=0 & gap G13=0; Director Ctrl E28=0;
  **Balance sheet Pg7 G19 (net) = G25 (capital+reserves)**; Pg11 D47 = Pg6 F24.
  A non-zero balance-sheet gap that equals the depreciation charge ⇒ the Pg 9 Total-column formulas
  were overwritten (Step 7 trap) — restore G8/G9/G10/G12/G13/G14/G16/G18 to `=E..`.

### Phase-2 result (28.02.2026)
- **Turnover £20,001.01** (2025 £15,223.55) · gross profit £19,799.01 · admin £13,151.12 ·
  **profit before tax £6,533.66** (2025 loss £12,224.75) — swing driven by higher turnover + nil director
  remuneration + no one-off £1,800 accountancy payment.
- Balance sheet: fixed assets £347.88 · debtors £2,290.26 · cash £32,946.01 · creditors £58,713.33 ·
  **net liabilities £23,129.18** (balances to capital + reserves). DLA c/f £56,517.33.
- Corp tax £0 (b/f losses £27,250.96 absorb the profit; losses c/f £18,834.95).
- Personal tax: employment £0 (nil remuneration), property net £17,644.27 (2025 estimate rolled).

### Judgment items surfaced for the accountant (defaults applied, easily flipped)
1. **Depreciation** — mirrored 2025 method (18% straight-line on cost) = £2,650.35, leaving NBV £347.88.
   Reducing-balance on NBV would be £539.68 (NBV £2,458.55); ~£2,111 profit swing. Method choice = judgment.
2. **£204 clearance** destination = DLA (no P&L hit) vs sundry expenses (P&L).
3. **Accountancy** — £2,448 P&L (GoCardless only) + £2,196 accrual carried unchanged from 2025.
4. Company now **profitable**; confirm nil corp tax given b/f losses.

## PHASE 3 — review refinements (formatting + query discipline)

### Rule: Private / Suspense are QUERY buckets, not dumping grounds
- Any transaction coded to **Private** or **Suspense** must be *queried with the client before* it is
  finalised to the Director's Loan Account (or left in suspense). Do not silently absorb them.
- Provisionally code them as before (so the file still balances), but list every such item on the
  **Notes and queries** page — payee, count, amount, where it is currently sitting, and the decision
  needed (business → reallocate to P&L; personal → confirm to DLA).
- This year: Private = 10 × "Snap 247" @ £34.99 = £349.90 (→ query 6). Suspense: none.

### Notes and queries page — column layout
- Query **number in column B, wording in column C** (column A stays empty). Continuation text runs on
  in column C on the next row. Match the style of existing rows (copy B13 / C13 cell styles). New items
  were added as queries 6–8 (Private items; £204 clearance treatment; accountancy accrual).

### Formatting standards to carry forward
- **Bank listing TOTAL row** = bold, with a thin top+bottom rule spanning the full table width (A:L),
  keeping the accounting number format. When the total row moves (because the transaction count changed),
  re-apply this to the new total row AND strip the leftover total-formatting from the row the template's
  total used to sit on (here row 37 carried stray bold/borders in cols E:K).
- **ETB header (rows 5–8)** = one clean grouped-box grid. Vertical rules only at the six group
  boundaries (Opening Bal | Bank | Journals | Accruals | P&L | Balance Sheet), a top rule on the first
  header row and a bottom rule under the Dr/Cr row — no stray internal verticals. Group-label cells are
  merged pairs (B:C, D:E, F:G, I:J, K:L); H (Accruals) is a single boxed column. The header verticals
  must line up with the vertical rules already running down the body.
