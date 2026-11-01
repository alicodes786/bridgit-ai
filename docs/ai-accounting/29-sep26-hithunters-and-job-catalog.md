# 29. Analysis — 26 Sep 2026 Hit Hunters pack + job catalog

> Faraz sent: (1) the official job-type list and top 5, (2) a voice note about two
> year-end CSVs, (3) the Hit Hunters process log, (4) comparative + 2026 CSV +
> completed 2026 file, (5) what he wants Bridgit to do with it.
>
> Catalog: [27-job-types-catalog.md](./27-job-types-catalog.md).
> Files: [28-client-files-hithunters.md](./28-client-files-hithunters.md).
> SOP: [Hit_Hunters_Accounts_Prep_Process_Log.md](./Hit_Hunters_Accounts_Prep_Process_Log.md).
> Prior plan: [25-sep19-meeting-analysis.md](./25-sep19-meeting-analysis.md) §9,
> [17-build-plan.md](./17-build-plan.md) Week 1b.

---

## 1. What Faraz actually said

**Voice note (transcribed, next day after 19 Sep call):**

- Two clients: **28 Feb year-end** (this is Hit Hunters) and **31 Mar year-end**.
- He has their statements as **CSV**.
- He was about to do the whole process in **Claude**.
- He asked: use Bridgit now, or send last-year file + CSVs + how he would do it,
  or finish in Claude and extract the **exact prompts**?
- These are **year-end accounts**.

**Then he sent the pack anyway**, and:

> This is a very easy case tbf. But this is what I'd liked to have done on
> Bridgit directly. Then it learns and remembers for the future.
>
> Tricky part — it will need to differentiate between **company by company**
> rules [and] **job type by job type** rules and the only way you can do that
> is by storing a record specifically related to that client because certain
> clients have certain performers, certain formatting, certain rules, certain
> application of expenses.

**What that means:**

1. He is **not** waiting for Bridgit to be “ready” before sending year-ends. He
   wants this job *on Bridgit*, then memory sticks.
2. The process log **is** the Claude-prompt extract. Do not ask him to re-run
   Hit Hunters in Claude for us.
3. Bridgit is **not** ready for him to sit on the board and finish a statutory
   pack end-to-end today. Next move is: we train on this pack (bank analysis
   first), then he uses Bridgit on the next easy year-end.
4. Client-scoped memory is now an explicit product requirement, not a nice extra.
   Architecture already had `client_memory` vs `firm_rules`
   ([02-architecture.md](./02-architecture.md) §2.7) — it is not implemented as
   first-class **rules** yet, only as `ai_mappings` per client.

---

## 2. How the process log maps to Bridgit (and Faraz's 6 steps)

Faraz's 18 Sep steps vs this log:

| Faraz step | Hit Hunters log | Bridgit today |
|---|---|---|
| 1. Check data / missing | Inputs named: prior-year xlsx + CSV. Period 01.03.2025–28.02.2026 | **Not built** (job type + period intake still open from 19 Sep) |
| 2. Comparative / template | Copy the 21-tab 2025 file; do not start from a blank | **Partially** — Koliqi VAT shape only. No year-end template path |
| 3. Banking / bank payment analysis | **Log Phase 1** (steps 1–6) | **Built for VAT workbook shape**, not this 21-tab Banking / Bank Pay layout |
| 4. Finalise calculation | **Log Phase 2** — ETB is the only engine; journals; corp tax; personal tax roll-forward | **Not built** |
| 5. Accuracy / formatting | Log Phase 2 identities + **Phase 3** formatting and Notes & queries | Bank rec gate exists. Formatting / query page not built |
| 6. Human review | Judgment items listed (depreciation method, £204 clearance, accountancy accrual, Private→query) | Exception loop exists; not wired to these judgment types |

**This pack does not need invoices to finish bank analysis.** Hit Hunters is a
clean bank-CSV year-end. That is why Faraz called it easy — and why it is the
right first company-accounts job, even though Qasim was right that *many*
company accounts also need purchase/sales listings.

Log Phase 2 still needs journals, depreciation judgment, DLA, corp-tax losses —
that is real accounts work, **not** “add up Box 1.” Do not pretend Phase 2 of
this log is a small add-on this week.

---

## 3. Decision rules we must store (client vs job type)

**Job-type (any statutory year-end using this MA pack):**

- Copy prior-year workbook; rewrite Banking + Bank Pay; ETB is the only engine
  for statements.
- Opening bank: earliest CSV balance + that row's movement = prior-year
  statement close. Expected close = opening + in − out = latest CSV balance.
- Amount in col C is literal; category cell is `=C{row}` echo.
- Month-marker rows + TOTAL row with check columns.
- Recalc must be clean before sign-off.
- Private / Suspense are **query buckets**, not dumping grounds — list on
  Notes and queries before absorbing to DLA.
- Do not silently guess unmatched payees into Suspense.

**Client (Hit Hunters only):**

- Code by **payee**, mirroring prior year. CSV `Category` is a hint for **new**
  payees only.
- £1,000+ round receipt is a director deposit **only if it is in the director's
  own name**; invoice ref / sort code / Ltd name = genuine sales.
- Director remuneration this year: **NIL — no payroll** (was £9,600). This is
  a **this-year instruction**, not a forever mapping — same class as the £10k
  van capitalise-vs-expense warning from 19 Sep.
- Copyright column: `Mechanical Copyrig` → Copyright; other sales → Income.
  Prior year labels Copyright as “PRS Royalty Income” in the P&L but puts
  actual PRS receipts in “Other Production Fees” — **mirror this quirk**.
- Legacy £204 bank difference: **journal**, not by editing the bank listing.
  Default: Cr Bank / Dr DLA (no P&L). Accountant may flip to sundry.
- Personal tax property element: roll prior year unless data supplied.
- Depreciation: default mirror 2025 (18% SL on cost) but **flag as judgment**.

---

## 4. What this changes in the 19 Sep next-steps list

Those steps are **not discarded**. They are re-ordered because we now have a
second complete job of a **different type**.

| 19 Sep item | Still true? | Change |
|---|---|---|
| Tell MA Koliqi 16 questions are expected | Yes | Still worth saying; not blocking Hit Hunters |
| Faraz VAT-box / “full pipeline” scope | Still open in WhatsApp | **Do not wait.** He just handed a year-end and said do it on Bridgit. Bank analysis for year-end is the next proof. Full ETB stays after that. VAT box calc stays queued, not the front of the queue |
| Drop CoA blocker | Done | Unchanged |
| Job-type + period intake | **More urgent** | We now have VAT (Koliqi) and year-end (Hit Hunters). Intake must name the type and the period before processing |
| Materiality flag | Yes | After bank analysis works on Hit Hunters; judgment items in the log are the first test cases |
| Decouple personal vs nature | Yes | Hit Hunters: Private vs expense is explicit; still query before DLA |
| Capital/judgment re-confirm | **Confirmed by this pack** | Director rem NIL, depreciation method, £204 destination — do not freeze last year's treatment as law |
| Opening-balance tie-out | **Now specified to the penny** | Process-log Step 3. Build this as part of the Hit Hunters run, not a vague later item |
| Generic template fallback | Lower priority | Hit Hunters **has** a comparative. Koliqi still does not |
| VAT box totals | Park | After year-end bank analysis is in flight |
| May 2026 VAT blind job | Still incoming if they send it | **Hit Hunters is in hand.** Train on what we have |
| Template bank + letters | Phase 3 | Unchanged |

**Week 3 “second historical job” is no longer hypothetical.** Hit Hunters is it.

---

## 5. Next steps (do in this order)

### A. Memory / schema (so Faraz's “client record” is real)

1. Add `job_type` (+ period start/end) on `ai_jobs`. Intake before process.
   Then **missing-document check** (Faraz step 1): ask for gaps, do not hard-block
   on partial packs. Same for year-end and VAT. Was easy to lose inside “intake”.
2. Add a **client_rules** store (or use `client_memory` as designed in §2.7):
   key, value, client_id, optional job_type, status proposed/approved.
   First Hit Hunters rules: code-by-payee, director-rem-NIL-this-year,
   copyright-column quirk, £204-via-journal.
3. Keep mappings **per client**. Add payee-normalisation (text before `;`,
   lower-case) as the Hit Hunters match key — exact full-description match will
   miss CSV vs workbook wording.
4. Do **not** write Hit Hunters columns into Koliqi mappings.

### B. Train on Hit Hunters — process-log Phase 1 only

5. Spike the 21-tab workbook the way we spiked the VAT file
   (`23-excel-template-spike.md`). Output: which cells Bridgit may write
   (Banking, Bank Pay, titles, Bank Rec pointers) vs ETB/formulas it must not
   overwrite (especially Pg 9 col G trap).
6. Script: extract payee → Bank Pay / Banking column from the **2025** file
   → `ai_mappings` for client **Hit Hunters Ltd**.
7. Extend CSV ingest for Countingup (Paid in / Paid out / Balance). Sort
   oldest-first. Prove opening £24,704.55 and close £32,945.01 before coding.
8. Classify 2026 lines by payee map. Unmatched = questions. Never auto-Suspense.
9. Write Banking + Bank Pay into a **copy** of the 2025 file (process-log Step 5).
10. Internal compare vs completed 2026 file. No % to Faraz.

### C. Only after B ties

11. Process-log Phase 2 (ETB roll-forward, journals, comparatives, identities).
    This is the real “finalise calculation” for company accounts. Separate
    chunk — do not start it while bank tabs still disagree.
12. Judgment exceptions: depreciation, £204, accountancy accrual, Private
    (Snap 247 × 10).

### D. Parallel, do not drop

13. Koliqi VAT engine stays the first live board job. Hit Hunters is the
    second client / second job type — not a replacement.
14. When Faraz sends the 31 Mar year-end, it is the **repeat test** of B
    (new client mappings, same job-type rules).
15. VAT decision rules (when SR vs NV) still open — ask on next catch-up.

### E. What to tell Faraz (when you reply)

- Thank him: this pack + the process log is exactly what Bridgit needs to
  learn a year-end. He does **not** need to re-do it in Claude for prompts.
- Bridgit will take Hit Hunters next as a training job: remember payees and
  this client's rules, write the bank tabs, then we look at rolling the ETB.
- He should keep using Claude for live year-ends until that loop is on the
  board — then the *next* easy year-end goes through Bridgit.
- 31 Mar client: send when ready (comparative + CSV; completed file later
  as answer key if he has it).

---

## 6. Do not

- Mix Hit Hunters and Koliqi knowledge.
- Let CSV Category drive coding.
- Auto-post to Suspense or Private.
- Overwrite Pg 9 total-column formulas (process-log Step 7 trap).
- Promise Faraz a finished statutory pack this week.
- Send an accuracy %.
- Commit anything under `data/client/`.
