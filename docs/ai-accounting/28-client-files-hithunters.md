# 28. Client files — Hit Hunters Ltd (year-end accounts)

> **Received:** 26 Sep 2026, from Faraz.
> **Job type:** Company Accounts (statutory year ended **28 February 2026**).
> **Why it matters:** first complete **year-end** pack with a comparative file, a
> current-year CSV, a completed answer-key workbook, **and** a written process log
> of every step Faraz took (the thing he offered to extract as Claude prompts —
> we already have it, better than prompts).
> Analysis: [29-sep26-hithunters-and-job-catalog.md](./29-sep26-hithunters-and-job-catalog.md).
> Process log: [Hit_Hunters_Accounts_Prep_Process_Log.md](./Hit_Hunters_Accounts_Prep_Process_Log.md).

## Where they go

`d:\bridgit-ai\data\client\HitHunters\`

That folder is gitignored (`data/client/`). Never commit. Never Slack / WhatsApp /
claude.ai / this chat.

## What MA sent (26 Sep 2026)

On disk (names as labelled):

| File on disk | Role |
|---|---|
| `Hit Hunters Ltd Transactions 2025-03-01 to 2026-02-28-Transactions_2026.csv` | **2026 transactions.** Countingup export, 168 data rows, newest-first. Columns: Date, Cleared date, Description, Category, Reference, Sort code, Account number, FX…, Paid in (£), Paid out (£), Balance (£). |
| `Hit Hunters Ltd Accounts 28.02.2025_Comparative_File_2025 (AA)-(OK)(VK).xlsx` | **2025 comparative file.** Full statutory pack, 21 tabs. Payee→column map + opening balances + last year's treatment. |
| `Hit_Hunters_Ltd_Accounts_28_02_2026-Completed_File_2026.xlsx` | **2026 complete file.** Answer key. Same 21 tabs, dates rolled, bank analysis done, ETB rolled forward. |

In docs (safe to keep in git — process only, no bank lines):

| File | Role |
|---|---|
| `Hit_Hunters_Accounts_Prep_Process_Log.md` | Exact repeatable steps + decision rules Faraz used. **This is the SOP for this job type.** |

Faraz also mentioned a **second** year-end (31 March) with CSVs. Not in this folder
yet. Do not block Hit Hunters on it.

## Numbers from the process log (do not re-derive until you open the files)

- Opening bank (must match 2025 statement close): **£24,704.55**
- Money in: **£20,001.01** (Income £19,656.99 + Copyright £344.02)
- Money out: **£11,760.55**
- Closing: **£32,945.01** — ties: 24,704.55 + 20,001.01 − 11,760.55
- CSV's own `Category` column is **unreliable** — code by **payee**, mirroring 2025

## Rules when we come back

1. **Do not paste these files into chat.** Work on disk / dashboard only.
2. Process-log **Phase 1 first** (Banking + Bank Pay + rec). Do not start ETB /
   P&L / balance sheet (process-log Phase 2) until Bridgit's bank tabs match the
   completed 2026 file internally.
3. Extract payee→column map from the **2025** file, store as **Hit Hunters**
   mappings only — never as firm-wide or Koliqi mappings.
4. Internal scorecard only. Do not send Faraz a %.
5. Countingup CSV is a new ingest format (Paid in / Paid out / Balance). Add
   column aliases; do not write a one-off Hit Hunters parser.
