# 25. Analysis — 19 Sep 2026 Qasim/Carson Walkthrough Call

> Source: `meeting_transcript_19sept.md` (raw), `meeting_summary_19sept.md` (Fireflies),
> `meeting_summary_readAI_19sept.md` (Read AI). Cross-checked against Faraz's step-by-step
> message (below) and the current plan (`13-scope-phase1.md`, `14-scope-phase2.md`,
> `17-build-plan.md`, `09-data-request-for-ma.md`).
>
> Call ran long and didn't follow the [24-sep19-meeting-agenda.md](./24-sep19-meeting-agenda.md)
> script closely, but produced more real process detail than the script would have.
> This doc is the distillation. Nothing below is guessed — every point traces to a
> specific moment in the transcript.

**Who was on the call:** Mirza — WhatsApp display name **Ali Kabeer**, which resolves
the "Ali" addressed throughout the raw transcript (confirmed 19 Sep from the WhatsApp
messages sent to Faraz after the call) — building Bridgit; Qasim (senior accountant,
walked through the SOP); and Carson (accountant, jumped in with the "source docs are
always the same" framing and the materiality idea). Speaker labels in the raw
transcript are unreliable (Fireflies mislabels), so this doc reports **what was
said**, not exactly **who** said each line, except where it's unambiguous (e.g. Qasim
narrating his own Claude workflow).

---

## 1. Faraz's message, checked line by line against the call

Faraz sent this yesterday:

> 1) check for the data — request if anything is missing
> 2) check previous quarter file for comparison (where one doesn't exist, a generic
>    template is created based on similar jobs done for other clients)
> 3) execute — do the banking and bank payment and purchase and sales analysis
> 4) execute — use analysis and finalise calculation
> 5) ensure accuracy — checking comparatives and formatting
> 6) send to human for review

**Verdict: this is accurate.** Qasim and Carson independently described the same
six-stage shape, in the same order, without having seen Faraz's message. That's a
strong signal the sequence is real and not a simplification.

| Faraz step | Confirmed on call | Bridgit today |
|---|---|---|
| 1. Check data, request missing | Yes — Carson: source docs are always bank statements + purchase invoices/receipts + sales invoices (+ P60/mortgage statements for individuals). "The first thing this agent needs to know is... we received this, this, this is missing." Also: job type + accounting **period** must be confirmed first (see §3). | **Not built.** Bridgit processes whatever file is uploaded. No job-type/period intake step, no explicit "what's missing" check before processing starts. |
| 2. Comparative file, or generic template if none | Yes, in detail (see §2). No comparative → more questions is *expected*, not a bug. | **Partially built.** Prior mappings are used, but there's no explicit "opening balance must tie to last year's closing" check, and no fallback library of generic templates per job type when there's no comparative. |
| 3. Banking, bank payment, purchase, sales analysis | Yes — this is literally "the bookkeeping part," the foundation for every job type. | **Bank side built** (Banking Analysis, Bank Payment Analysis, Bank Rec). **Purchase/sales invoice analysis not built** — currently filed under Phase 2 ("invoice OCR/matching"), but Faraz's step 3 treats it as core, day-one, not a later enhancement. |
| 4. Finalise calculation | Yes — Qasim: after bookkeeping, "that's the basis of all accounts... VAT, property, personal company... from where then the variations start." VAT needs the actual Box figures; company accounts need trial balance → P&L → balance sheet. | **Not built.** Bridgit stops at coded lines + Excel write. It does not compute the actual VAT return figures or a trial balance/P&L/balance sheet. **This is a real scope gap — see §7.** |
| 5. Accuracy — comparatives + formatting | Yes — materiality/proportional review (§4), trial balance = debits/credits check, matching previous file's shape. | **Partially built.** Bank rec hard gate exists. Materiality-based flagging does **not** exist — only confidence-based flagging does. |
| 6. Human review | Yes — "reviewer" role is explicit and separate from "bookkeeper" and "accounts finalizer." | **Built.** `ready_for_review` state, PDF summary, exception loop. |

So Faraz's message is a correct compression of MA's real process. The gaps are in
**steps 3 (purchase/sales) and 4 (finalise calculation)** — those are the two places
where Bridgit currently stops short of what MA (and Faraz) actually expect day one.

---

## 2. The real SOP, in order (confirmed, more detail than the agenda assumed)

1. **Know the job.** Client, job type (VAT / personal tax / company accounts / etc.),
   and the **exact accounting period**. Qasim gave a concrete failure example: a
   statement ended 18 Aug but the VAT quarter needed to run to 31 Aug, and Claude
   didn't catch the gap on its own — it only surfaced it when directly asked. This
   needs to be **hardwired**, not left to the LLM to notice.

2. **Check what's provided vs what's needed**, and ask for what's missing *before*
   or *alongside* starting — but partial data is fine, work with what exists and
   flag gaps rather than blocking entirely.

3. **Comparative file** (previous year/quarter):
   - Used for **opening balance continuity** — last period's closing balance must
     equal this period's opening balance. This is a discrete tie-out check, not just
     "reuse the mapping table."
   - Used for **prior coding of known suppliers** — this is what Bridgit's mapping
     table already does.
   - Used for **anomaly spotting** — comparing this year's figures to last year's to
     catch things that look wrong (e.g. a cost that vanished, revenue that doubled).
   - **If no comparative exists** (new client, first quarter — this is exactly the
     Koliqi & Sons situation): use a **similar client/job as a template**, and expect
     **more manual refinement and more exception questions**. Qasim: *"Without a
     comparative, it should ask questions because it won't know."* This directly
     explains the 16 open questions on the live Koliqi Aug job — **it is correct
     behaviour, not a defect.** Worth saying explicitly back to Qasim/Carson so they
     don't read question volume as a quality signal.

4. **Bank analysis / bank payment analysis** (the "bookkeeping" stage — this is what
   Bridgit does today):
   - List every transaction, split money in vs money out.
   - Categorise by **nature/type only** at this stage (Vodafone → telephone, TfL →
     travel) — **not** personal vs business yet. That classification happens later
     (see point 6).
   - Anything uncertain goes to a question, or into a **Suspense** account as a
     temporary holding category — Qasim explicitly offers both as acceptable options,
     not just "ask a question every time."
   - **Multiple raw categories roll up into one chart-of-accounts line at the trial
     balance stage** — e.g. Microsoft + Adobe + a marketing subscription might be
     three separate bank-payment columns but all become "software" as a single trial
     balance line. This rollup happens later, not at ingestion.

5. **Missing invoice against a bank payment — two distinct cases, not one:**
   - **(a)** The invoice was raised last quarter, paid this quarter → it should
     already exist as an opening debtor/creditor balance carried forward. This nets
     out and is *not* an exception once the opening balance is right.
   - **(b)** There's genuinely no invoice anywhere linked to that payment → this
     *is* a real exception and should be flagged.
   - Bridgit currently has no concept of (a) — no debtor/creditor carry-forward
     tracking across periods. Worth a note for later; not urgent while invoice
     ingestion itself is still Phase 2.

6. **Personal vs business / allowable-expense decision** happens at the **accounts
   stage**, not the bank stage, informed by:
   - Prior-period treatment of the same category for this client (main driver).
   - Materiality (see point 7) — this is where a human double-checks anything large.

7. **Materiality review (new, not currently in Bridgit):** flag transactions that are
   unusually large — either an **absolute threshold** or a **proportional threshold**
   (Carson's example: a single transaction that's more than ~2.5–5% of total
   transaction value is "worth double checking and confirming"). Thresholds are
   **client-specific** — "for some clients, above £500 is a big transaction, for some
   clients above £10,000 is." This is explicitly the **reviewer's** job, separate from
   the bookkeeper/accounts-finalizer stages.

8. **Judgement calls are not permanently "learned."** Example given: a £10,000 vehicle
   purchase might be capitalised one year (low profit, no need to claim the expense)
   and expensed the next year (high profit) for the *same client, same transaction
   type*. Qasim: *"If it assumes that last year he said capitalise, this year you must
   capitalise again... that may need work."* **This means Bridgit's "exact match →
   auto-apply forever" rule needs an exception for capital/judgement-heavy items** —
   these should re-confirm with the accountant rather than silently repeating, even
   with a prior mapping on file.

9. **Trial balance / bank reconciliation check, in order:** debits must equal credits.
   First thing to check when it doesn't balance: **has everything from the bank been
   captured** — a missing line or a duplicate is the most likely cause. This is
   exactly the check Bridgit's bank-rec hard gate already does — **confirmed correct,
   no change needed.**

10. **Job type determines what happens after the bookkeeping stage:**
    - **VAT**: sales/banking figures go straight into the VAT calculation (Box totals).
      No trial balance, no P&L, no balance sheet needed — "too time consuming" for the
      volume of VAT jobs they run.
    - **Company accounts**: full fan-out — trial balance (which is also where the
      **P&L vs balance sheet decision is made**, not before), then profit & loss and
      balance sheet pages.
    - **Property letting / individual**: simple income & expenditure, feeds the
      person's tax computation. No balance sheet complexity at all.

---

## 3. Pre-meeting questions — what actually got answered

We went in with three asks (`17-build-plan.md` → "Ask MA this week", `09-data-request-for-ma.md`
Tier 1). Here's the real outcome:

| Ask | Outcome |
|---|---|
| **Chart of accounts (codes + names)** | **Answered — and the answer changes the plan.** Qasim, directly: *"No, not really... on Xero, which is not many... on FreeAgent... we don't really use those codes to be honest."* **MA does not have a formal chart of accounts with codes.** There is nothing to wait for here. Qasim's own view: *"I don't think you need that for chart of accounts. I think Claude/Bridget should have enough knowledge to do that."* → **Close this ask out.** Bridgit should rely on standard UK chart-of-accounts categories (already implicit in how it prompts the LLM) validated against the category names actually used in client workbooks, not a firm-supplied codes file that doesn't exist. |
| **VAT codes and decision rules** | **Half-answered.** The five codes are confirmed exactly as Bridgit already has them: **SR** (standard 20%), **ZR** (zero-rated), **EX** (exempt), **NV** (no VAT/outside), **OS** (outside scope). The *decision rules* — when to use which, beyond the label — were **not** covered; ran out of time. **Still open**, carry to the Wednesday/Saturday catch-up. |
| **P&L vs Balance Sheet classification / new-account rule** | **Answered, but differently than expected.** It's not a lookup table — it's a **structural fact of the trial balance stage**: the decision is made *when a line is linked into the trial balance*, based on standard accounting classification (asset/liability vs income/expense), not a per-account firm rule. New-account creation wasn't given a firm rule either — same "Claude/Bridget should already know this" answer as chart of accounts. |

**Net effect:** two of three "hard dependency" asks in `13-scope-phase1.md`
(chart of accounts, P&L/BS rules) turn out to not be firm-specific data we're
waiting on — they're standard accounting knowledge Bridgit needs to already carry.
Only the **VAT decision rules** (the "when," not the "what") remain a genuine
outstanding ask. This meaningfully de-risks the "waiting on MA data" blocker that's
been sitting in the plan since Day 1.

---

## 4. New requirements surfaced (not previously in the plan)

1. **Job-context intake stage.** Before processing: client, job type, accounting
   period start/end. Validate that the supplied documents actually cover that period
   (catch the "statement ends 18th, period needs to end 31st" class of bug). Ask
   before/while processing if something's missing, but don't hard-block on partial data.

2. **Comparative-file-aware opening balance check.** Distinct from "reuse prior
   mapping" — explicitly check this period's opening balance against last period's
   closing balance from the comparative file, and surface a discrepancy as its own
   exception type.

3. **Generic-template fallback.** When no comparative file exists, use a similar
   client/job's workbook shape as a starting template rather than starting from
   nothing. Needs a small library of "shape by job type" (VAT / company accounts /
   property letting / etc.), not full firm-wide chart of accounts.

4. **Decouple "categorise by nature" from "personal vs business."** Bank-stage
   categorisation should not ask "personal or business?" — it should categorise by
   type (travel, food, software, etc.) and defer the personal/business/allowable
   decision to the accounts-finalisation stage, informed by prior-period treatment
   for the same client + category.

5. **Materiality-based reviewer flag.** A distinct check from LLM-confidence: flag
   any line above a client-specific absolute threshold, or above a proportional
   threshold (e.g. >2.5–5% of total transaction value), for human confirmation —
   regardless of how confident the categorisation was.

6. **Capital/judgement items don't auto-repeat.** For transaction types where
   treatment is a year-by-year judgement call (capitalise vs expense being the
   concrete example given), don't silently reapply a prior mapping — re-confirm with
   the accountant even on an exact description match.

7. **Debtor/creditor carry-forward (lower priority, note for later).** Distinguish
   "invoice raised last period, paid this period" (expected, nets out via opening
   balance) from "genuinely no invoice anywhere" (real exception). Depends on
   invoice ingestion, which is already Phase 2 — just flag the nuance for when that
   work starts.

8. **"Finalise calculation" stage is missing entirely.** Bridgit currently stops at
   coded lines + Excel write. It does not compute VAT box totals, nor build a full
   trial balance / P&L / balance sheet for company accounts. This is the single
   biggest gap relative to both Faraz's message (step 4) and Qasim's description
   ("that's the basis... from where then the variations start"). **See §7 for the
   scope question this raises.**

---

## 5. Job-type roadmap (priority signal from MA, not just from us)

> **Superseded as the official ranking on 26 Sep.** Faraz sent a written catalog and
> **top 5:** (1) Company Accounts, (2) VAT Returns, (3) Property Lettings, (4) Sole
> Trader / Self Employed, (5) CIS. Full list and what is out of engine:
> [27-job-types-catalog.md](./27-job-types-catalog.md). The 19 Sep verbal ranking
> below is kept for the meeting record only.

MA's own ranking **on the 19 Sep call**, in order of volume/priority:

1. **Company accounts** — "probably the most common" job type at MA. Not previously
   the plan's focus (we've been VAT-first because that's what we had a live example
   for).
2. **Self-assessment** (personal tax, multiple income sources / P60s).
3. **VAT** — current Bridgit focus. 4 per year per registered client.
4. **CIS accounts** — lower volume, ~30/year, often incomplete data (roughly half
   have no bank statements at all — vouchers only).
5. Property letting, self-employed accounts, partnership accounts — simpler variants
   of the above, lower engineering cost once company accounts / self-assessment work.
6. **Management accounts** — fundamentally different (forward-looking estimates, not
   historical fact) — needs explicit assumption inputs from the accountant
   (revenue growth %, expense growth %), not inferable from data alone.
7. **Capital gains tax** — could be a **questionnaire-driven** template rather than
   document parsing — structured Q&A with the client, then Bridgit calculates.
8. **Specialist tax advisory** (e.g. sole trader → limited company scenario modelling)
   — mentioned as an interesting idea, not scoped.
9. **Out of scope, confirmed by MA themselves:** dormant account filings ("don't think
   it can do that"), company formations ("I don't think Bridget would engage here").

**Action taken on the call:** MA is sending one new test job — a **quarter-ending-May
2026 VAT return** for a different client, in **two parts**: (a) previous-quarter file
+ this quarter's paperwork only, and (b) the completed final workbook, sent
separately, to be used as a blind-test answer key. Also confirmed: **Koliqi & Sons is
genuinely a first-quarter job with no comparative** — the 16 questions are expected.

---

## 6. New feature requests (log for later, not immediate)

- **Template bank.** Reusable workbook shapes per job type (VAT, company accounts,
  personal tax, property letting, self-employment, capital gains). We already have
  this implicitly for VAT (the Koliqi shape); this asks for it to be generalised and
  explicit.
- **Letter / document generation.** Store example correspondence (HMRC letters,
  Companies House letters, client engagement letters, "taking over a client from
  another accountant" letters) and generate new drafts from client-specific details.
  Compared by Faraz to his own ChatGPT project for Airbnb guest replies — a persistent
  context that improves from corrections over time. This is a genuinely new,
  self-contained feature, not part of the bookkeeping engine — good candidate for
  **Phase 3**, not urgent.
- **Meeting/process knowledge capture.** Fireflies is already connected and captures
  call content. Worth being explicit with the team: that's meeting-notes tooling
  today, not literally training Bridgit's model. If they expect process rules
  mentioned in calls (like this one) to become part of Bridgit's actual rule base,
  that has to happen through us writing it into the plan/rules — which is exactly
  what this document does.

---

## 7. Scope tension to raise with Faraz (do not resolve unilaterally)

Faraz's step 4 — **"use analysis and finalise calculation"** — means Bridgit should
produce the actual VAT return figures (or full TB/P&L/balance sheet for company
accounts), not just categorised bank lines.

But our own scope docs currently say:

- `13-scope-phase1.md` → "What Is Out of Scope for Phase 1" lists **"VAT return
  preparation"**.
- `14-scope-phase2.md` → "What Phase 2 Does Not Include" lists **"Full accounts
  preparation pipeline (year-end, VAT returns, personal tax)"** as **Phase 3**.

So today's plan pushes the actual calculation step to Phase 3, while Faraz's message
and this call both describe it as a core, early-loop step (step 4 of 6, immediately
after the bookkeeping analysis). **This is a real scope inconsistency, not a small
one** — it affects what "Phase 1 done" means. Two ways to resolve, need Faraz's call:

- **Option A:** Keep Phase 1 as "bookkeeping analysis only" (categorise + trial
  balance + bank rec + Excel write). Explicitly tell Faraz/Qasim/Carson that the final
  VAT-box number and full P&L/balance sheet are a Phase 1.5/2 step, so nobody expects
  a submission-ready VAT figure out of the current engine.
- **Option B:** Pull "finalise calculation" forward into Phase 1 for VAT jobs
  specifically (it's a small, mechanical step for VAT — sum coded lines into Box 1/4 —
  much smaller than full invoice OCR/matching), while leaving full company-accounts
  TB/P&L/BS for Phase 2+.

**Recommendation: Option B for VAT only.** Computing VAT box totals from already-coded
lines is arithmetic, not a new subsystem — it's a natural, cheap extension of what
exists, and it closes the exact gap Faraz flagged. Full company-accounts finalisation
(trial balance → P&L → balance sheet) is a much bigger lift and can stay later,
especially since company accounts wasn't the job we've been building against anyway.

**Message drafted for Faraz, 19 Sep (WhatsApp):** see
[26-faraz-scope-tension-message.md](./26-faraz-scope-tension-message.md) for the
ready-to-send text, with exact references back to the Scope of Works doc so Faraz can
check it against what he already agreed to.

**Update, same day, before the message was even sent:** Faraz reacted to a related
comment with *"Phase 1 should be very quick then... the analysis part is the easy
part"* and *"I don't fully get all these phases."* This is bigger than the VAT-only
framing above — he's rejecting phase language altogether and expecting fast
finalisation for **any** job type, including company accounts. Company accounts
finalisation genuinely cannot happen without invoice data (confirmed by Qasim/Carson
on the call — trial balance needs banking *and* purchase/sales invoices), which isn't
built yet.

**Final version, as actually sent:** kept a brief pointer to the Scope of Works link
(rather than dropping phase language outright), falls back to the job-by-job
breakdown (VAT fast / company accounts needs invoice reading first) if that doesn't
land, and explicitly extends the same logic to the **other job types** from §5
(self-assessment, CIS, property letting, management accounts) — each needs its own
"finish it" step built once, but none start from zero once the shared
categorisation/learning layer is solid. Full text and reasoning:
[26-faraz-scope-tension-message.md](./26-faraz-scope-tension-message.md).

---

## 8. Scorecard — how much of the plan was on track

**On track, confirmed correct, no change needed:**
- Duplicate detection: never auto-resolve, always ask. ✓ (matches "first check:
  missing line or duplicate" directly)
- Bank reconciliation as a hard gate, checked before trial balance issues are chased. ✓
- Mappings persist per client and get reused automatically (with the capital-item
  caveat above). ✓
- VAT codes SR/ZR/EX/NV/OS. ✓ exact match.
- OneDrive not a Phase 1 blocker. ✓
- WhatsApp/Nylon/FreeAgent/MTD out of scope for now. ✓ (Nylon explicitly confirmed by
  MA as more useful for specialist expense/tax-advisory edge cases than routine
  chart-of-accounts work — validates the "Phase 2, not Phase 1" call)
- Internal engine-first board instead of polished UI for Week 1 testing. ✓ — this is
  literally what got demoed on the call and it worked as the teaching tool it was
  meant to be.
- Not sending Faraz an accuracy %. ✓ no change.

**Needs to change or get added:**
- Split the pipeline into explicit stages (intake/context → bookkeeping → finalise
  calculation → materiality review → human review) rather than one pass that ends at
  "coded lines + Excel."
- Add job-type + accounting-period intake/validation before processing.
- Add comparative-file opening-balance tie-out as its own check.
- Add generic-template fallback for no-comparative jobs (small library by job type).
- Decouple nature-categorisation from personal/business decisioning.
- Add materiality-based flagging (client-specific + proportional threshold),
  independent of LLM confidence.
- Add re-confirmation instead of silent auto-repeat for capital/judgement-call items.
- Drop the "wait for MA's chart of accounts" blocker — it doesn't exist; rely on
  built-in accounting knowledge instead.
- Keep chasing VAT decision rules specifically (the one real outstanding data ask).
- Resolve the Phase 1 vs Phase 2/3 "finalise calculation" scope tension with Faraz
  (§7) — recommend pulling VAT box calculation into Phase 1, leaving full
  TB/P&L/balance sheet for later.
- Re-rank job-type roadmap: company accounts and self-assessment are MA's actual
  highest-volume work, ahead of CIS — worth knowing even though VAT stays the Phase 1
  focus.
- Log template bank + letter generation as Phase 3 candidates.
- Process the two incoming test jobs (Koliqi & Sons Q1 no-comparative; new
  quarter-ending-May job with/without final workbook) as concrete near-term work.

---

## 9. Next steps, in order

1. **Tell Qasim/Carson the 16 questions on Koliqi Aug are correct behaviour** — no
   comparative file exists for that job, more questions is expected. Closes a loop
   they were confused about mid-call.
2. **Raise the §7 scope decision with Faraz** — is VAT box calculation in Phase 1 or
   later? Get this answered before doing more engine work so effort isn't wasted in
   the wrong place.
3. **Update `13-scope-phase1.md` / `09-data-request-for-ma.md`** to drop the chart-of-
   accounts dependency (done as part of this session — see diffs) and note the VAT
   decision-rules ask as the one real remaining Tier 1 gap.
4. **Build job-type + period intake step** — smallest, highest-leverage new piece;
   directly fixes the "statement ends 18th, period should end 31st" class of bug and
   gives Bridgit the context it needs before anything else runs.
5. **Build materiality-based flagging** — client-specific absolute + proportional
   threshold, separate from confidence-based exceptions.
6. **Decouple personal/business decisioning from bank-stage categorisation** in the
   categorisation chain.
7. **Add capital/judgement-item re-confirmation** instead of blind mapping reuse.
8. **If Faraz confirms Option B (§7):** build VAT box total calculation as the
   "finalise calculation" stage for VAT jobs.
9. **Process the two incoming MA test jobs** once received (Koliqi & Sons Q1;
   quarter-ending-May comparative job) — use the with/without-final-workbook pair as
   an internal blind-accuracy check.
10. **Keep chasing VAT decision rules** and, longer-term, an opening-balance tie-out
    check against comparative files.
11. **Log template bank + letter generation** as Phase 3 scope, no build yet.
