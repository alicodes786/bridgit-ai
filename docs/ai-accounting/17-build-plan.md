# 17. Bridgit Build Plan — Track This

> **This is the working plan.** Tick boxes as work lands. Do not start Week 2 items
> before the Week 1 engine can process the first real bank file.
>
> **Repo:** `bridgit-ai` (separate from the MA dashboard). Host API on Railway. Host
> UI on its own Vercel project. Do not write into the live MA dashboard repo until
> the engine is proven.
>
> **Scope of Works (client-facing, live):** https://bridgit-scope-works.netlify.app/
> — this is the link sent to Faraz. Reference this when checking anything against
> what he's actually agreed to (see
> [26-faraz-scope-tension-message.md](./26-faraz-scope-tension-message.md)).
>
> **Last updated:** 25 Oct 2026 (evening) — Queued/Bank Rec/chat-bar uploads:
> [36-oct25-session.md](./36-oct25-session.md). Faraz catalog + Hit Hunters pack
> still the training job ([27-job-types-catalog.md](./27-job-types-catalog.md)).
> Prior 26 Sep note: Faraz sent the official job-type catalog + top 5
> ([27-job-types-catalog.md](./27-job-types-catalog.md)) and the **Hit Hunters Ltd**
> year-end pack (comparative + 2026 CSV + completed file + process log). That is the
> first company-accounts training job. Full analysis:
> [29-sep26-hithunters-and-job-catalog.md](./29-sep26-hithunters-and-job-catalog.md).
> Decisions 25–27 in [08-decisions-log.md](./08-decisions-log.md).
>
> **19 Sep:** Qasim/Carson walkthrough. Koliqi 16 questions = correct (no comparative).
> Week 1b items still apply but **re-ordered**: Hit Hunters bank analysis before VAT
> box totals. See [25-sep19-meeting-analysis.md](./25-sep19-meeting-analysis.md).
>
> **18 Sep:** **Accept / Override live** on the internal board, plus one-page PDF summary. First live Koliqi Starling job (Aug PDF, 40 lines, 16 questions) can now be answered on-screen. Answers write `ai_mappings`.

---

## Rules (do not drift)

- [x] Bridgit is its own app and GitHub repo for now
- [x] Accounting-only assistant in Phase 1
- [x] OneDrive is not a start-gate
- [x] Engine before pretty UI — **internal live board on FastAPI `/` is allowed.** That is not the Faraz product UI. Next.js exception table still comes after the engine can process a file.
- [ ] Zero silent guesses: every line is coded with a reason, or asked as a real question
- [ ] Scorecards stay internal. Do not send a % number to Faraz
- [ ] Do not add WhatsApp, Nylon, FreeAgent, or MTD in Week 1
- [ ] Every approved job writes back into mappings (and later into the vector store)
- [ ] Real client files stay out of Slack, personal Claude/ChatGPT, and the MA dashboard repo

---

## Already done

- [x] NDA signed
- [x] Phase 1 payment received
- [x] Product named Bridgit
- [x] First client bank statement received
- [x] Completed working file received
- [x] Invoices for first client received
- [x] Bookkeeping Excel template confirmed
- [x] Planning docs copied into this repo
- [x] New `bridgit-ai` GitHub repo created

---

## Day 1 — Repo, stack, accounts

### Repo and stack

- [x] Create private GitHub repo `bridgit-ai`
- [x] Copy `docs/ai-accounting/` into this repo
- [x] Initialise FastAPI backend (`apps/api`)
- [x] Initialise Next.js frontend (`apps/web`)
- [x] Add `.env.example` and `.gitignore`
- [x] Add starter SQL schema (`supabase/schema.sql`)
- [x] Confirm this repo is **not** connected to the MA Vercel project

### Accounts and safety (before any real file hits an API)

- [x] Create a **new** Supabase project named Bridgit (do not add `ai_*` tables to live MA DB yet)
- [x] Turn on MFA on that Supabase project
- [x] Create Anthropic API account (business / API, not claude.ai)
- [ ] OpenAI API — **skipped for Phase 1.** Not required. Anthropic only. Revisit if we want a second model for comparison.
- [x] Anthropic ZDR — requested 14 Sep, **confirmed on by Anthropic 17 Sep.** Real client files may go through the API.
- [x] Put Anthropic key only in local `.env` / Railway. Never commit it
- [ ] Create Railway project for the FastAPI service (can wait until first deploy — see `19-day1-accounts-guide.md`)

**Stack lock**

| Piece | Use |
|---|---|
| Frontend | Next.js in `apps/web` |
| Agent backend | Python FastAPI in `apps/api` on Railway |
| Database | New Supabase project (Bridgit) |
| Files | Supabase Storage |
| RAG | pgvector on that same Supabase (Week 2, not Day 1) |
| Models | Anthropic (Claude) primary. OpenAI optional later. Abstraction stays switchable. |

---

## Day 2 — Empty engine and schema

- [x] Apply `supabase/schema.sql` on the Bridgit Supabase project
- [x] Enable `pgvector` extension (in that SQL file; unused until Week 2)
- [x] FastAPI create job in `ai_jobs` — verified dummy POST 14 Sep (`queued`)
- [x] Bank file upload to Storage + `ai_documents` — verified (`dummy-bank.csv`)
- [x] GET job status from DB — verified
- [x] Job states exist: `queued` → `processing` → `needs_input` → `ready_for_review` → `approved`
- [x] No LLM calls yet. Prove the pipe only

---

## Day 2–3 — Load the first client's knowledge

Highest-value work this week. Use the completed working file already in hand.

- [x] Extract description → account code → VAT code from the completed workbook
- [x] Save those pairs into `ai_mappings` for that client (77 rows: 29 approved, 48 proposed) — `scripts/load_koliqi_mappings.py`
- [x] **Excel template spike** — mapped every tab, column, and formula in `23-excel-template-spike.md`. Summary: Bridgit writes transaction rows into Banking Analysis + Bank Payment Analysis (col A-H, row 6+), updates anchor SUM formula in row 1000, writes opening/closing balance into Bank Rec. Everything else is formula-driven. Simpler than feared.
- [ ] Store the blank Excel template in Supabase Storage as the output base
- [ ] Attach the invoices we already have to the first job as supporting files
- [ ] Do not block the first bank run on OCR / invoice matching

After this, Bridgit already knows last year's Amazon, Dell, and similar lines for this client.

---

## Day 3–5 — Week 1 engine (the real start)

Build in this order. Do not jump to UI polish.

- [x] **PDF bank statement parser** — **not Starling-only.** Shared ingest entry (`app/ingest`): detect PDF vs CSV vs Excel. PDF tries (1) UK current-account layout DATE/TYPE/IN/OUT (first proven on Koliqi Starling PDFs), (2) table extraction, (3) dated text lines. CSV/Excel uses column aliases so Lloyds/Barclays/etc. exports work without a Starling-specific product.
- [x] Parse bank CSV / Excel into clean rows: date, description, amount, debit/credit
- [x] Categorisation chain, **no RAG yet**
  - [x] 1. Exact prior mapping (approved rows auto-code; proposed/REVIEW rows ask, do not silent-apply)
  - [ ] 2. Firm rule (skipped until Saturday Qasim call — CoA + VAT rules)
  - [x] 3. LLM propose + confidence — **on 17 Sep.** ZDR confirmed (Decision 20). Unknown lines go to Claude; high confidence auto-codes, low confidence asks a specific question.
  - [x] 4. **Duplicate detection** — before mapping, same date + amount + description on this job. Flag, never auto-resolve.
  - [x] 5. Else exception with a **specific** question
- [x] Store `source_page` per transaction (PDF page). Run `ALTER TABLE ai_transactions ADD COLUMN IF NOT EXISTS source_page int;` on Bridgit Supabase if the column is missing (also in `supabase/schema.sql`).
- [x] Hard gate: trial balance must balance — bank-only double-entry identity for now (full TB after chart of accounts)
- [x] Hard gate: bank rec must agree — opening + receipts − payments vs statement closing. Verified **£0.00** on both Koliqi Starling PDFs locally (17 Sep).
- [x] If either gate fails, job does not go to review (`needs_input`)
- [x] Write output into MA's Excel template (Banking Analysis + Bank Payment Analysis + Bank Rec E8/E12 + row 1000 anchors). Uses the Koliqi workbook as the write surface until a blank official template is stored.
- [x] One-page PDF summary
- [x] Internal run on the first client file — **18 Sep, live dashboard.** Job "Dashboard test": `StarlingStatement_2026-08_2026-08.pdf`, 40 lines, 16 open questions, status `needs_input`, working Excel generated. (Local parse of both Starling PDFs was 17 Sep.)
- [ ] You review the score internally. Client does not see the %

**Local proof (17 Sep, disk only):**
| File | Rows | Bank rec |
|---|---|---|
| `StarlingStatement_2026-04_2026-07.pdf` | 259 | difference £0.00 |
| `StarlingStatement_2026-08_2026-08.pdf` | 40 | difference £0.00 |

**Live dashboard proof (18 Sep):**
| Job | File | Lines | Open questions | Status |
|---|---|---|---|---|
| Dashboard test | Aug Starling PDF | 40 | 16, now answerable on-screen | `needs_input` until Accept/Override |

16 questions mix: REVIEW/personal mappings (do not silent-apply), real duplicates (parking/Experian), new LLM asks (Trip.com, Booking.com, bakeries, HMCTS). 24 lines auto-coded. Do not send Faraz a %.

**How to test the exception loop:** `http://localhost:8000/` → the `needs_input` job opens with cards. Accept confirms the proposed account (REVIEW wording is stripped before the mapping is saved). Override types account + VAT (SR / ZR / EX / NV / OS). Duplicates: Keep both or This is a repeat — no mapping. When 0 questions remain, status becomes `ready_for_review`; download Excel + PDF. That is Phase 1: bank file → coded lines → questions → answers that stick → MA Excel + rec gate → human review.

**Next (do not drift):** you click through those 16. Saturday Qasim call still owns chart of accounts + VAT firm rules. Do not start Week 2 RAG, invoices, WhatsApp, or Faraz Next.js until this loop has been used on the live job.

Apr–Jul vs 77 mappings (exact description, 17 Sep local): 79 auto-coded, 126 proposed/review, 8 duplicates, 46 unknown.

---

## End of Week 1 — Tiny Bridgit UI (separate site)

> **Internal board:** `/board` on the FastAPI process (local often
> `http://127.0.0.1:8001/board`). `/` redirects to `/app` for Faraz.
>
> **Interactive-first.** This is the "same as Claude but better" moment.
> Faraz should be able to drop a real file, see it categorised, answer exceptions
> on-screen, and download the Excel — all in Week 1. Not Week 4.
> Every exception they answer is saved permanently as a client mapping.
> That IS the "teach it as we go" loop. No pretty UI needed for this to land.

- [x] Upload bank file — works on the internal board (`localhost:8000`)
- [x] See job status badge (Queued → Processing → Needs input → Ready → Approved) — board shows status; not a polished badge yet
- [x] **Exception table — interactive (internal board).** Each flagged line shows: description,
      proposed account, specific question. One-click Accept / Override (duplicates: Keep both / This is a repeat).
      Accept/Override saves to `ai_mappings` (REVIEW flags stripped so they cannot silent-apply later).
      Same description on this job is coded in the same click. Last open question → `ready_for_review`.
      **This is the teach-as-we-go loop.** Faraz Next.js table is still later; this board is how we test it.
- [x] Download Excel when job has a working file (board link).
- [x] One-page PDF summary (board link + regenerated after each answer).
- [x] Download Excel + PDF when job is Ready for review (same board links; status flips after the last answer).
- [x] Client UI at FastAPI `/app` (password gate, questions, new job, Approve, retry, Chat)
- [x] Chat-bar / Cards **Add files** after the job exists (`POST /jobs/{id}/files`).
      Bank or last-year Excel re-runs process; extra papers are stored, not OCR'd.
- [x] Year-end **Bank Rec** rebuilt as opening + in − out = close, with TIES status
- [x] Deploy API to Railway (`BRIDGIT_PASSWORD` required). Dockerfile is in the repo.
      Run `003_engine_summary.sql` **and** `004_job_chat.sql` on Bridgit Supabase first.
      Live smoke test: [37-live-demo-northbridge.md](./37-live-demo-northbridge.md).
- [ ] **Decision 31** — job-aware chat summaries + exportable transcript/data (Claude-like)
- [x] **Decision 34** — Test badge on jobs/clients with test/demo in the name
- [~] **Decision 33** — working-file updated toasts + last-updated line (partial in `/app`)
- [~] **Decision 32** — supporting `.txt` on New job; fuller supporting-doc UX still to build
- [ ] Vercel Next.js — not needed for this trial (`/app` is the Faraz UI)

This is Bridgit v0. Still not inside the MA dashboard.
**The goal at end of Week 1:** Faraz uploads a real bank file and it feels
noticeably better than Claude — because it remembered last year's mappings,
it wrote his Excel template, and every question he answers sticks permanently.

---

## Week 1b — From the 19 Sep walkthrough (do before Week 2 RAG)

New requirements from the Qasim/Carson call. Full context:
[25-sep19-meeting-analysis.md](./25-sep19-meeting-analysis.md).
**26 Sep reorder:** Hit Hunters year-end pack is in hand — do the **1b foundation
slice** (intake + missing docs + client-scoped rules) **then immediately prove it
on Hit Hunters (1c)**. Do not finish every 1b checkbox before 1c. Parked 1b items
stay parked: VAT boxes, materiality flag, generic templates, decouple personal vs
nature.

### This session (26 Sep) — landed

- [x] Job-type + accounting-period intake before processing
- [x] **Missing-document check at job start** (required docs become questions;
      optional invoices stay on the intake list; **do not hard-block**)
- [x] Client rules table + `code_by_payee` (Decision 25, Hit Hunters seed in
      `scripts/load_hithunters_mappings.py`)
- [x] Comparative opening-balance tie-out from Countingup running balance
      (Hit Hunters: £24,704.55 / £32,945.01, rec £0.00 on disk)
- [x] Code by **payee** from prior year; CSV Category ignored
- [x] Unmatched payees = questions; never auto-Suspense / never LLM-guess on year-end
- [ ] Judgment items re-confirm (director rem, depreciation, £204) — **after** bank
      tabs match
- [ ] Materiality-based reviewer flag — later 1b
- [ ] Decouple nature vs personal — later 1b
- [ ] Generic-template fallback — later 1b
- [ ] VAT box totals — parked
- [ ] May 2026 VAT blind job — do not wait

---

## Week 1c — Hit Hunters year-end (process-log Phase 1 only)

First company-accounts training job. Files:
[28-client-files-hithunters.md](./28-client-files-hithunters.md).
SOP: [Hit_Hunters_Accounts_Prep_Process_Log.md](./Hit_Hunters_Accounts_Prep_Process_Log.md).
Do **not** start ETB roll-forward until this list is green.

- [x] Spike the 21-tab 2025 workbook (write Banking / Bank Pay only; list ETB/Pg9
      traps) — [30-hithunters-excel-spike.md](./30-hithunters-excel-spike.md)
- [x] Extract 2025 payee → column map (`app.engine.yearend_map` + script
      `load_hithunters_mappings.py`) — run the script against Bridgit Supabase
- [x] Countingup CSV ingest (Paid in / Paid out / Balance); sort oldest-first
- [x] Opening + in − out = close gate on this file (£0.00 on disk 26 Sep)
- [x] Classify 2026 lines from payee map; unmatched = questions
- [x] Write Banking + Bank Pay into a copy of the 2025 file (when comparative
      uploaded on the job)
- [ ] Internal compare vs completed 2026 file on a live board job (run mappings
      script, then upload CSV + comparative on localhost:8000)
- [ ] Only then: process-log Phase 2 (ETB, journals, comparatives) as its own chunk

Koliqi VAT board job stays live. Two clients, two job types, two mapping sets.

---

## Week 2 — Semantic search, tuning, and interactive loop improvement

Do not start until Week 1 has produced an internal Excel on the real file.

- [ ] Embed the completed / approved job into pgvector
- [ ] Similarity search runs before the LLM step
- [ ] Re-run Job 1 and compare internally
- [ ] Tighten exception questions (specific, not "unsure")
- [ ] Calibrate confidence threshold from real errors
- [ ] **Interactive improvement:** exception table shows *why* a line was flagged
      (which mapping fired, what the LLM proposed, at what confidence) so the
      accountant understands every decision — not just a "?" button
- [ ] **Feedback loop visible:** after answering 10+ exceptions, show the
      accountant how many lines are now auto-resolving that weren't before.
      The "it's getting smarter" moment Faraz wants from Claude — but permanently.

---

## Week 3 — Harden

- [x] Second historical job if MA sends one — **Hit Hunters year-end received 26 Sep.**
      Bank-analysis run is Week 1c (not “done” until that run ties)
- [ ] Extra bank export formats if needed
- [ ] TB and bank rec clean on all test jobs
- [ ] Internal accuracy at target before more UI work

---

## Week 4 — UI good enough for Faraz and Qasim

- [ ] Client / job picker
- [ ] Chat only to start a job or ask operational questions
- [ ] Exception table as its own screen
- [ ] Five-state badges
- [ ] Email if they are not on the page; question on-screen if they are
- [ ] Screenshots to MA for layout feedback (do not treat the old proposal mock as final)

---

## Week 5 — Demo

- [ ] They upload a real file
- [ ] They answer exceptions
- [ ] They download the working file
- [ ] Phase 1 walkthrough sign-off

**After this**, discuss embedding Bridgit into the existing MA dashboard repo.

---

## Ask MA this week (not blockers)

**Updated 19 Sep** after the Qasim/Carson walkthrough call — full analysis in
[25-sep19-meeting-analysis.md](./25-sep19-meeting-analysis.md). Two of the three
original asks are resolved, not received:

1. ~~Chart of accounts (codes and names)~~ — **resolved, not incoming.** MA confirmed
   on the call they do not use a formal coded chart of accounts. Bridgit relies on its
   own standard accounting knowledge instead, validated against the category names
   actually used in client workbooks. Remove as a blocker.
2. **VAT codes and how they choose them** — codes confirmed (SR / ZR / EX / NV / OS,
   matches what Bridgit already has), but the **decision rules** (when to use which)
   were not covered on the call. **Still open** — carry to the next Wed/Sat catch-up.
3. ~~P&L vs balance sheet, and when to create a new account~~ — **resolved, structural
   answer, not a firm rule.** The decision happens at the trial-balance stage based on
   standard asset/liability vs income/expense classification, not a per-account lookup
   MA maintains. No file incoming.

**26 Sep:** official top 5 in [27-job-types-catalog.md](./27-job-types-catalog.md).
Company accounts pack **received** (Hit Hunters). Still useful later: property
lettings, sole trader, CIS examples; 31 Mar year-end Faraz mentioned; May VAT blind
job if it still arrives.

Later, not needed to start: OneDrive Agent folder, letter/document template bank
(Phase 3 candidate).

- [x] Message sent / walkthrough call held (19 Sep)
- [x] Chart of accounts — resolved (doesn't exist; not a blocker)
- [ ] VAT decision rules received (codes only so far)
- [x] P&L / new-account rule — resolved (structural, trial-balance stage)
- [ ] OneDrive access (optional)
- [ ] Quarter-ending-May test job received (in progress via OneDrive link, 19 Sep)
- [x] Qasim walkthrough held (19 Sep) — see analysis doc for full findings
- [x] Company accounts sample job received (Hit Hunters, 26 Sep)
- [ ] 31 Mar year-end (second CSV client Faraz mentioned) — not received yet

---

## Out of scope until later

- WhatsApp / Meta
- Nylon
- FreeAgent write / MTD
- Per-client portal
- General (non-accounting) assistant
- Writing into the live MA dashboard codebase
