# 12. Meeting Analysis — August 2026

> Notes from two client meetings with Qasim (also called **Cass** — same person) and
> **Faraz, labelled "S FA"** in the transcripts (the other MA Associates owner).
> Documents what changed, what is new, and what needs updating across the plan. Do NOT
> treat this as the final state — use it as a working list to drive doc updates.
>
> - **Meeting 1** (~24 Aug 2026): Phase 1 scope, weekly sprints, categorisation
>   difficulty, Nylon/FreeAgent/MTD phasing, initial continuity concern, initial data
>   security asks.
> - **Meeting 2** (23 Aug 2026, short follow-up — see
>   [meeting-transcript2.md](./meeting-transcript2.md)): reframes Phase 1, sets a
>   concrete accuracy target, makes the continuity plan concrete, corrects the
>   FreeAgent/MTD assumption, further deprioritises Nylon, raises the assistant-scope
>   question, and works through workflow/UI ideas in detail.

---

## What is new or changed vs our existing plan

### Phase 1 scope — tighter and clearer
- Bank statement → trial balance ONLY. Emails, handwritten notes, unidentifiable receipts = future phases.
- The repeatable, time-consuming task is bank data entry and trial balance prep. That is Phase 1.
- Consistent with our docs but now explicitly agreed with the client.

### Weekly sprints — not one big reveal
- Client does NOT want 6 weeks of silence then a demo.
- Weekly scorecard updates showing accuracy progress each sprint.
- Phase 1 is incremental tests → scorecard each week → tune → repeat → then UI.

### Categorisation is harder than described
- Emirates flight for a car wash business — travel or personal? AI has to ask, not guess.
- Mirza committed to refine the Phase 1 categorisation plan within 1 day of the meeting.
- This is outstanding. Needs to be done before Phase 1 "starts."

### Data pipeline must be set up before Phase 1 is declared started
- OneDrive drop zone → API → Railway server → Supabase → parsed data.
- Must be tested for speed and reliability first.
- New pre-condition — not in existing docs.

### Nylon API — new integration to investigate
- MA already has a Nylon subscription.
- Nylon = UK accounting manual + all HMRC cases, queryable.
- Idea: AI bounces off Nylon to validate categorisation decisions against UK rules.
- If uncertain → flag for human with Nylon's reasoning.
- Qasim to confirm if Nylon has a developer API.
- Was not in our plan at all — open item.

### FreeAgent API — should be earlier than Phase 3
- S FA's point: large proportion of self-employed clients already on MTD software.
- Waiting until Phase 3 to connect FreeAgent repeats the Xero/WIP dashboard mistake.
- At minimum, plan FreeAgent for Phase 2. Investigate API availability.

### MTD (Making Tax Digital)
- Named explicitly as Phase 3 requirement.
- AI must eventually communicate with MTD software, not just produce Excel.
- Should be in Phase 3 scope as a named deliverable.

### Key person continuity / risk
- S FA raised: what if Mirza is unavailable, something urgent breaks?
- Need fallback plan in writing — second developer or handover documentation.
- Goes in the contract, not the proposal. Acknowledge in proposal FAQ.

### Liability boundary
- AI must complete ALL checks before presenting to human for sign-off.
- Human approval should not mean re-checking basic bank rec and analysis.
- Strict SOP inside the system: AI confirms it has done every step before stage transitions.
- Systematic bug = developer responsibility, not MA's.
- Already in our architecture (deterministic checks, validation gates) — needs to be surfaced in contract language too.

### Agent naming — open
- AI agent needs a name. OneDrive folder naming convention also needed.
- Action: S FA to propose options.

### Self-hosted LLM — 4-5 month vision
- Mirza floated as future goal for tighter security.
- Own GPU or rented server running the model entirely under their control.
- Not relevant to Phase 1. Noted in 05-hosting already.

### Data security — key asks from S FA
- GDPR and ICO compliance — ACCA registered firm, serious obligations.
- Zero retention confirmed for LLMs (Claude, Llama).
- MFA on Supabase / vector database.
- Client portal to review and delete their own data from the database (MA can do this from MA dashboard).
- Restricted team access to database — even Mirza's team has limited access.
- Retention policy needed in contract (raw bank data can be deleted after processing; training/knowledge data retained).
- All details to be written into proposal and contract.

**Point 2 design (locked 25 Aug 2026):** see [02-architecture.md](./02-architecture.md)
§2.13.1 and [08-decisions-log.md](./08-decisions-log.md) Decision 16.

- **Not** a separate vector database. `pgvector` stays in the existing MA Supabase
  project so there is one place to lock down and one place to delete from.
- **Not** the Supabase admin console for staff. A **Data Centre** page inside the
  MA dashboard lists files, working data, and approved mappings per client, with
  delete. Raw admin access is how tables get dropped by accident.
- LLM path is Anthropic + OpenAI **business APIs** with ZDR **switched on**. Llama
  / consumer Claude chat is not the production path. ZDR is not automatic on a
  free account.
- Proposed retention: raw files deletable 30 days after sign-off (Faraz to
  confirm the number). Approved mappings + audit trail stay.
- MFA on Supabase. Developer production access is not standing.
- NDA + DPA in the contract. Local/email copies deleted after that piece of work.
- Written into [proposal.html](./proposal.html) (Data protection section).

---

## Meeting 2 (23 Aug 2026 follow-up) — what's new

### Phase 1 reframed: learning phase, not a kill-gate
- Mirza, verbatim: "it's not like, oh, it's not working, phase one is gone, finished,
  we're not going ahead with the project." Phase 1 = sandbox testing to learn how the
  AI performs across different data patterns (including mid-job data, not only
  finished jobs) so Phase 2 is easier. The project has started, not paused pending
  Phase 1's verdict.
- Hard gates (TB balances, bank rec agrees) are unaffected — this only changes the
  framing around AI accuracy, not the software checks.
- See [08-decisions-log.md](./08-decisions-log.md) Decision 10.

### Concrete accuracy target set: 90%+
- Plan: rate every transaction in the early weeks for accuracy. Once the AI
  consistently hits 90%+ transaction scoring, human approval becomes a fast final
  check rather than a full re-check.
- S FA's concern (HMRC-facing liability): need strong confidence levels built in
  before the AI makes any assumption. Answered by the rating/scoring process plus the
  hard gates.
- See [08-decisions-log.md](./08-decisions-log.md) Decision 11.

### Categorisation risk lower than first feared
- Qasim: HMRC publishes a defined list of ~500 allowable expense categories; most
  transactions map onto one cleanly. A plain LLM chat already gets close to this
  right without Nylon.
- Nylon further deprioritised — nice-to-have for complex/edge cases only ("we're not
  there yet"), not a Phase 1 or even a confirmed Phase 2 dependency.
- The real hard edge case is **personal vs. business** classification (e.g. Emirates
  flight for a car-wash business), which needs company/industry context awareness in
  the prompt design, not a lookup table.
- S FA: the agent should ask when genuinely unsure — this is expected and wanted, as
  long as questions are accurate and not "stupid."

### Continuity plan made concrete — three scenarios
1. Mirza unavailable long-term → MA gets full code/Railway/infrastructure access to
   migrate or bring in another developer.
2. Faraz steps back, Qasim/Cass takes over → Mirza's team runs a formal
   knowledge-transfer (KT) session.
3. Project continues, occasional support needed → a named developer from Mirza's
   team (not only Mirza) stays as point of contact.
- Reason given (S FA): this may become one of the firm's largest investments, and
  usage will span multiple people/offices around the clock (Pakistan, Dubai, London).
- See [08-decisions-log.md](./08-decisions-log.md) Decision 14.

### MTD/FreeAgent — corrected understanding
- Confirmed: FreeAgent's API is **read-only**. All MTD prep, review, and HMRC
  submission happens inside FreeAgent's own software — there is no Excel step to
  intercept. A read-only pull into a spreadsheet adds a step, it doesn't help.
- Qasim's proposed alternative: a **computer-use style approach** (like Claude's
  computer-use feature), possibly from a dedicated office machine, to operate
  FreeAgent directly.
- Mirza's position (correct one): don't commit to an approach until tested — run a
  technical spike, use whichever route actually works.
- See [08-decisions-log.md](./08-decisions-log.md) Decision 12.

### New open decision: assistant scope
- Faraz asked: should the assistant answer general questions (e.g. "100 + 100") like
  a normal chatbot, or be restricted to accounting topics only?
- Mirza: negligible cost/speed difference either way; if restricted, done via prompt
  instructions + a knowledge-base boundary, not a separate system.
- Faraz to decide. See [08-decisions-log.md](./08-decisions-log.md) Decision 13.

### Workflow / UI ideas discussed in detail
- Two experiences, not one: a **chat experience** (already in the proposal) and a
  **dashboard experience** — drop files for a client/job, it processes in the
  background, then shows numbers on screen plus a downloadable file (Excel/PDF),
  all also saved in the database.
- **Idea for later (Faraz explicitly placed this in Phase 3):** a separate section
  from the chat — a company/client list similar to MA's existing one, but for AI
  job history — where you can see every process the AI has run for that client, the
  status, and the output files. Faraz called it "a little portal for each client."
  This is **not Phase 1 or 2.**
- Faraz asked for actual screenshots before committing to a specific layout ("until
  we're actually sitting there using it... it's hard for me to say one way is
  correct") — Mirza owes these.
- See [04-roadmap-and-deliverables.md](./04-roadmap-and-deliverables.md) Phase 3 for
  where the per-client portal now lives.

### Point 3 design locked (25 Aug 2026) — see Decision 17
Discussed directly with Mirza and settled into a concrete design, not left as an
open idea:
- **Chat vs. exception review split:** chat starts jobs and answers ad-hoc
  questions; a **separate structured table** handles exception review. A
  1,200-transaction job with 100+ flags is unusable as a chat log.
- **Five-state job status**, shown everywhere a job appears: Queued → Processing
  → Needs your input → Ready for review → Approved.
- **Notifications: both** email (reusing existing Resend infra) and an in-app
  badge, firing when a job needs input or is ready — answers Faraz's "we come
  back an hour later" scenario directly.
- **Output: Excel template + one-page PDF summary**, both downloadable and stored
  in `ai_documents` — answers "Adobe, PDF, an Excel workbook? Where do we
  download that?"
- **Per-client portal confirmed Phase 3**, framed as the same job-list UI scoped
  to one client, not a new build.
- Full design in [02-architecture.md](./02-architecture.md) §2.1.1.

### NDA and SOP walkthrough — before deeper data sharing
- Mirza will send an NDA before MA shares sensitive job data.
- Faraz's framing: this is like being "a trainee accountant" — Mirza needs an actual
  walkthrough of the firm's SOP (comparatives → opening balances → bank analysis →
  sales invoice listing, etc.), not just the general flowchart, because real jobs
  deviate client by client (missing invoices, need to estimate). Qasim/Cass to walk
  Mirza through one real job on a call.
- See [08-decisions-log.md](./08-decisions-log.md) Decision 15.

### Immediate next actions agreed on the call
- Mirza to post in the WhatsApp group exactly what data/files are needed; S FA/Qasim
  to send them.
- Mirza's team to start limited R&D on "something simpler" in parallel while the
  proposal is refined.
- Mirza to send screenshots of the workflow (dashboard view + chat view).
- Budget/payment breakdown to be discussed directly between Faraz and Mirza
  separately (not on this call).

---

## What needs updating

| What | Where | Status |
|---|---|---|
| Weekly sprints added to Phase 1 description | `proposal.html` + `04-roadmap` | Done (Point 1) |
| Data pipeline setup as pre-condition to Phase 1 | `04-roadmap` + `06-checklist` | Done (Point 1) |
| Categorisation refinement (working chain, keep tightening) | `02-architecture` §2.5.1 + `04-roadmap` | Done as working design; logic still live |
| Nylon API investigation | `06-checklist` | Done as Phase 2 optional fallback, not Phase 1 |
| FreeAgent moved earlier (Phase 2 mention) | `04-roadmap` + `proposal.html` | Done (Point 1) |
| MTD named explicitly in Phase 3 | `04-roadmap` + `proposal.html` | Done (Point 1) |
| Key person continuity mention | `proposal.html` FAQ + `04-roadmap` (3 concrete scenarios) + `08-decisions-log` Decision 14 | Docs done; contract wording + proposal FAQ update still pending |
| Liability boundary / AI SOP checks | `proposal.html` + `02-architecture` | Done (Point 1) |
| Phase 1 reframed as learning phase, not kill-gate | `04-roadmap` + `08-decisions-log` Decision 10 | Done |
| 90%+ accuracy target | `04-roadmap` + `08-decisions-log` Decision 11 | Done |
| MTD/FreeAgent read-only correction + computer-use spike | `01-context-and-requirements` + `02-architecture` + `04-roadmap` + `08-decisions-log` Decision 12 | Done |
| Nylon further deprioritised | `01-context-and-requirements` + `02-architecture` §2.5.1 | Done |
| Assistant scope open decision | `04-roadmap` + `08-decisions-log` Decision 13 | Logged; decision owed by Faraz |
| Workflow/UI ideas (chat + dashboard, per-client portal in Phase 3) | `04-roadmap` Phase 3 + `02-architecture` §2.1.1 + Decision 17 | **Design done (Point 3)**; `proposal.html` update still pending |
| Meeting 2 Phase 1 framing, 90%+, continuity, Nylon/MTD | `proposal.html` | Done (before Point 2) |
| NDA + SOP walkthrough call | `04-roadmap` + `06-checklist` + `08-decisions-log` Decision 15 | Logged; action still pending both sides |
| Data protection section | `proposal.html` + `02-architecture` §2.13.1 + Decision 16 | **Done (Point 2)** |
| Agent naming TBD | `08-decisions-log` Decision 9 | Open |
| Self-hosted LLM vision | `05-hosting` already covered | Done |

---

## Action items by owner (both meetings combined, current as of 24 Aug 2026)

### Mirza
- [ ] Send NDA to MA before deeper data sharing.
- [ ] Post the exact data/file request in the WhatsApp group (see
  [09-data-request-for-ma.md](./09-data-request-for-ma.md)).
- [ ] Set up and test the OneDrive drop-zone pipeline (speed + reliability).
- [ ] Schedule the SOP walkthrough call with Qasim (Cass).
- [ ] Refine and re-send the Phase 1 categorisation plan (the personal-vs-business
  context-awareness design).
- [ ] Send workflow screenshots (dashboard view + chat view) once the job-creation
  flow and exception table actually exist — owed from Meeting 2.
- [x] Update `proposal.html` for Point 2 (data protection) and Point 3 (workflow/UI).
- [ ] Build the exception-review table, five-state status badges, email + in-app
  notifications, and Excel + PDF output as described in
  [02-architecture.md](./02-architecture.md) §2.1.1.
- [ ] Enable Anthropic + OpenAI zero-data-retention on the API accounts before real client files are sent.
- [ ] Write the continuity plan (3 scenarios) into the actual contract, not just the
  proposal FAQ. Include DPA, ZDR, local-copy deletion, and the 30-day (or agreed)
  raw-file retention period.
- [ ] Assign one team member to start limited R&D on a simpler component in parallel.
- [ ] Run the MTD/FreeAgent technical spike (computer-use style automation vs.
  alternatives) once FreeAgent access exists — not urgent, Phase 3 item.

### Qasim (Cass)
- [ ] Confirm whether Nylon has a developer API (low priority, not blocking).
- [ ] Walk Mirza through one real job step by step (SOP call).
- [ ] Send working papers for at least one completed job (raw + final file), ideally
  plus one job still in progress.
- [ ] Continue as the go-to for categorisation/accounting-logic questions as Mirza's
  team builds the prompts.

### Faraz (S FA)
- [ ] Decide assistant scope: accounting-only vs. general-purpose (Decision 13).
- [ ] Confirm raw-file retention period for the contract: proposed default is 30 days after sign-off (or longer if you prefer).
- [ ] Review the Data Centre idea in the proposal (delete from MA dashboard, not via a raw database login).
- [ ] Propose agent name + OneDrive folder naming convention (Decision 9).
- [ ] Send/help send the requested historical job data.
- [ ] Agree success/failure criteria for the accuracy test in writing, alongside
  Mirza.
- [ ] Discuss budget/payment breakdown directly with Mirza (separate conversation).
- [ ] Review workflow screenshots once sent and give feedback (per-client portal
  idea, chat vs. dashboard preferences).
