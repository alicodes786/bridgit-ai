# 13. Scope of Works — Phase 1: Bridgit AI (Bookkeeping Engine + Dashboard)

> **Status:** Agreed internally. Ready for client review.
> **Last updated:** 15 Sep 2026 — updated for 14 Sep decisions (Anthropic-only, OneDrive
> not a start-gate, separate Vercel site for Phase 1) and Tofu research (15 Sep).
> **Covers:** Phase 1 only. Phase 2 and Phase 3 scopes are in separate documents.
> **Working tracker:** See [17-build-plan.md](./17-build-plan.md) for day-by-day progress.

---

## What Phase 1 Is

Phase 1 builds **Bridgit** — an AI bookkeeping assistant that lives inside the MA
Associates dashboard. It takes a client's bank statement, categorises every
transaction using MA's own rules and prior client history, builds the trial balance,
runs the bank reconciliation, and produces MA's working Excel file plus a one-page PDF
summary — all ready for a human accountant to review and approve.

This is the "do the job" phase. Bridgit processes a job from start to finish. The
accountant approves the output, not the process. Every transaction is either
categorised with a logged reason or flagged with a specific question. Nothing is
posted silently.

---

## What Bridgit Does in Phase 1

### The categorisation chain — in order

1. **Known prior mapping** — has this supplier or description already been coded for
   this client? If yes, use it. No AI involved. Exact match wins immediately.

2. **Firm rules** — if no prior mapping exists, check MA's coded rules: VAT treatment,
   P&L vs Balance Sheet, when to create a new account. Software answers these. No LLM.

3. **Semantic search + LLM** — for lines that pass through both steps above, Bridgit
   searches prior year transactions for semantically similar entries, uses those as
   examples, and asks the LLM to propose an account code and VAT code with a
   confidence score. Context includes: MA's chart of accounts, VAT rules, and HMRC's
   allowable expense categories.

4. **Flag with a specific question** — if confidence falls below the threshold, Bridgit
   does not guess. It places the line in the exception table with a real, specific
   question (e.g. "Emirates flight for £612 on 14 Jan — this client runs a car wash.
   Business trip or personal?"). The accountant's answer is saved as a permanent
   mapping for that client. It will not be asked again.

5. **Duplicate detection** — before any categorisation, Bridgit checks whether an
   identical transaction (same date + amount + description) already exists for this
   job. Flagged, never silently posted. Simple check, high trust value.

### Hard software gates (not AI — guaranteed by code)

- **Trial balance must balance.** Checked arithmetically after categorisation. If it
  does not balance, the job does not proceed. The accountant never sees an unbalanced
  output.
- **Bank reconciliation must agree.** Same principle. Hard check, not an AI judgement.
  Both gates must pass before the job moves to "Ready for review."

### Output

- MA's existing Excel working file template, populated with categorised transactions,
  trial balance, and bank rec — in the exact format the team already uses.
- A one-page PDF summary: total transactions, auto-categorised count, exception count,
  TB status, bank rec status.
- Both files downloadable from the Bridgit job page and stored in the database.
- **Source linking on every exception line** — click any flagged transaction to see
  exactly which page and section of the source document the AI read it from.
  (Inspired by Tofu's click-to-verify — this is a core trust feature, not a nice-to-have.)

---

## What We Deliver — Week by Week

### Pre-work (before Week 1 engine starts)
- Railway FastAPI backend stood up, connected to Supabase
- Database schema: `ai_jobs`, `ai_transactions`, `ai_mappings`, `ai_documents`, `ai_audit_log`
- pgvector set up in Supabase (semantic search ready for Week 2)
- **LLM provider: Anthropic (Claude) only for Phase 1** (Decision 18, 14 Sep 2026).
  OpenAI is not required. Abstraction layer stays switchable for later.
- **OneDrive drop zone is NOT a start-gate for Phase 1** (Decision 6 / build plan rule,
  confirmed 14 Sep 2026). Files are uploaded directly for now. OneDrive ingest is built
  when the engine is proven, not before.
- Prior year workbook parsed: transaction descriptions and account codes loaded into
  `ai_mappings` as the client's starting knowledge base

### Week 1 — The Engine
- **PDF bank statement extraction** — required in Week 1. **Not Starling-only**
  (Decision 24). First proven layout is the Koliqi Starling PDFs (DATE / TYPE / IN / OUT).
  Other PDFs try table extraction then dated text. CSV/Excel covers Lloyds/Barclays/HSBC/NatWest
  style exports via column aliases. Same canonical row for every bank.
- Bank CSV and Excel ingestion with normalised parsing (handles multiple formats)
- Categorisation chain: prior mapping → firm rules → LLM → exception flag
- **Duplicate detection** before categorisation (same date + amount + description)
- LLM prompt: chart of accounts, MA VAT rules, HMRC allowable categories as context
- Exception question generator: specific per-line question, not a generic "unsure"
- **Source page stored per transaction** — every parsed line records which page of the
  source document it came from (foundation for click-to-verify in the UI)
- Trial balance builder with hard balance check
- Bank reconciliation checker with hard agree check
- MA Excel template output (populated from categorised data)
- PDF summary output
- First internal test run on historical job

### Week 2 — Semantic Search and Tuning
- pgvector semantic search active: prior year transactions embedded, similarity search
  runs before the LLM step — matching past entries become few-shot examples in the
  prompt
- Confidence threshold calibrated against Week 1 internal results
- Exception question quality reviewed and tightened
- Second test run, improvement measured internally

### Week 3 — Hardening
- Second historical job run (if provided by MA)
- Multiple bank format edge cases handled
- Exception questions confirmed specific and actionable
- TB and bank rec running cleanly on all test jobs
- Internal accuracy at target before UI work begins

### Week 4 — Bridgit UI (standalone site, not inside MA dashboard yet)
**Note (14 Sep 2026):** Phase 1 Bridgit is a **standalone app** on its own Vercel
project. It does not live inside the MA dashboard until the engine is proven on a
real file. The MA dashboard embed happens after Phase 1 sign-off.

- Job creation: client picker, file upload
- Five-state job lifecycle badge: `Queued → Processing → Needs your input → Ready for review → Approved`
- Exception review table as a separate surface (not inside chat):
  per-row reason + specific question + one-click Accept/Override buttons
  + **link to source document page** (click-to-verify, inspired by Tofu)
- Email notification when a job needs input or is ready for review
- Download page: Excel working file + PDF summary, both stored in the database

### Week 5 — End-to-End Demo
- Complete workflow tested: bank file uploaded → Bridgit processes → exceptions served
  to table → accountant answers → output downloaded
- Bridgit name and branding applied to the tab, emails, and UI
- Demo ready for Faraz and Qasim: they upload a real client file and walk through it

### Weeks 6–7 (Contingency)
- Additional client jobs, different bank formats, edge cases
- Feedback from demo incorporated
- Phase 1 signed off

---

## What MA Associates Provides

The following are hard dependencies. Engineering cannot move forward without them.

| What | When needed | Why |
|---|---|---|
| Raw bank statement(s) for 1-2 historical jobs | Before Week 1 | First test run |
| Completed final workbook for the same jobs | Before Week 1 | Accuracy baseline |
| Blank MA bookkeeping Excel template | Before Week 1 | Output format |
| ~~Chart of accounts (codes, names, types)~~ | ~~Before Week 1~~ | **Resolved 19 Sep — MA has no formal coded chart of accounts. Not incoming. Bridgit uses standard accounting knowledge instead.** |
| VAT codes and decision rules | Before Week 1 | **Codes confirmed 19 Sep (SR/ZR/EX/NV/OS). Decision rules still open.** |
| ~~P&L vs Balance Sheet classification rules~~ | ~~Before Week 1~~ | **Resolved 19 Sep — structural trial-balance-stage decision, not a firm-specific rule set. Not incoming.** |
| One job walkthrough call (Qasim) | Week 1 | SOP, comparatives, opening balances |
| Weekly availability to answer exception questions | Every week | Accuracy improvement |
| A second historical job (ideally mid-job or in-progress) | By Week 3 | Widens test coverage |
| NDA signed | Before any client data moves | Data protection |

---

## Self-Improving Knowledge Base

Every job that is approved by a senior accountant feeds back into Bridgit's knowledge
base automatically. This is not a manual step — it happens as part of the approval
flow.

**What gets saved on approval:**

- Every transaction and its confirmed account code, VAT code, and reason gets written
  to the client's `ai_mappings` table. Future exact matches are resolved instantly
  without any AI involved.
- The entire approved job — transaction descriptions paired with their confirmed codings
  — is embedded into the pgvector store. Future semantic searches can find this job as
  a reference and use it as a real example in LLM prompts.
- Every exception answer given mid-job is confirmed and locked as a permanent client
  rule. It will not be asked again.

**The compounding effect:**
- Job 1: relies on prior year file and firm rules. More exceptions flagged.
- Job 3: two approved jobs as reference. Fewer exceptions, faster processing.
- Job 10: deep pattern knowledge for this client. Most lines are exact mapping hits.
  AI involvement minimal.

This is the core reason Bridgit outperforms a general AI tool over time. A general
tool starts from scratch every session. Bridgit's knowledge base grows with every
approved job, permanently, per client.

---

## What Is Guaranteed

- Every transaction exits Bridgit in one of two states: **categorised with a logged
  reason**, or **flagged with a specific question**. There is no third state. Silent
  wrong answers are not possible by design.
- Trial balance and bank reconciliation are verified by software before any job is
  presented for review. A human accountant never re-checks basic arithmetic as their
  approval step.
- Every decision — which mapping fired, which rule applied, what the LLM proposed and
  at what confidence — is stored in the audit log. Any line can be clicked to see
  exactly why it was coded that way.
- Nothing is submitted to HMRC or Companies House. Phase 1 output is a working file
  for human review and approval. All statutory submissions remain human-authorised.

---

> **Open scope question, raised 19 Sep 2026** (see
> [25-sep19-meeting-analysis.md](./25-sep19-meeting-analysis.md) §7): the "What Is Out
> of Scope" list below still says VAT return preparation is out of Phase 1. Faraz's
> own step-by-step message and the Qasim/Carson call both describe "finalise the
> calculation" as step 4 of the core loop. **WhatsApp thread still open.**
>
> **26 Sep update:** Faraz sent a full **company accounts** pack (Hit Hunters) and
> asked for it on Bridgit directly. That does **not** mean ETB/P&L/BS is now Phase 1
> in one jump. Next engine work is year-end **bank analysis** (process-log Phase 1)
> with client-scoped memory. Statutory finalisation (process-log Phase 2) stays a
> separate chunk after bank tabs tie. VAT box totals remain parked behind that.
> See [29-sep26-hithunters-and-job-catalog.md](./29-sep26-hithunters-and-job-catalog.md).

---

## What Is Out of Scope for Phase 1

The following are explicitly not in Phase 1. They are planned for Phase 2 or Phase 3.

- Invoice and receipt processing (OCR, document matching)
- FreeAgent API integration
- Nylon UK tax research integration
- MTD / HMRC submission
- Multi-agent workflow (Bridgit coordinates with other agents)
- WhatsApp integration
- Per-client history portal
- VAT return preparation
- Personal tax and year-end accounts preparation (Phase 3)
- General assistant / non-accounting questions (Phase 3+)

---

## Continuity and Handover (written into the engagement)

Three scenarios are covered in writing:

1. **Lead developer unavailable long-term:** MA Associates receives full access to the
   code repository, Railway hosting, and all infrastructure. You can migrate to another
   developer without losing anything.
2. **Internal handover (Faraz to Qasim or similar):** A formal knowledge-transfer
   session is run with whoever takes over.
3. **Ongoing support:** A named developer remains the point of contact — not just one
   person with no backup.

---

## Definition of Done — Phase 1

Phase 1 is complete when:

- [ ] At least two historical MA jobs have been processed end-to-end by Bridgit
- [ ] Trial balance balances on both jobs (hard check)
- [ ] Bank reconciliation agrees on both jobs (hard check)
- [ ] Every flagged exception has a specific, actionable question (not "unsure")
- [ ] MA Excel template output is in the correct format with tabs and formulas intact
- [ ] PDF summary generated and downloadable
- [ ] Bridgit AI tab is live inside the real MA dashboard
- [ ] Exception review table is working and separate from chat
- [ ] Email and in-app notifications fire correctly
- [ ] Faraz and Qasim complete an end-to-end walkthrough and sign off
