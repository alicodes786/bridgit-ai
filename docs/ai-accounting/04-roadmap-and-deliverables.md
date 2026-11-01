# 4. Roadmap and Deliverables — POC → MVP → Production

> ⚠️ **HISTORICAL — context preserved, not the live working plan.**
> This document was written before the 14 Sep 2026 build decisions were locked.
> Key things that have changed since this was written:
> - The Phase 1 UI is a **standalone Bridgit app** first, embedded into MA dashboard
>   later (not inside MA from day one as originally planned).
> - **Anthropic only** for Phase 1 (Decision 18). OpenAI dropped.
> - **OneDrive is NOT a start-gate** (Decision 6). Files are uploaded directly.
> - The `bridgit-ai` repo is a **separate repo**, not inside the MA codebase.
>
> **For the live working plan, use [17-build-plan.md](./17-build-plan.md).**
>
> The detailed thinking below is still valid as background context. Do not act
> on the week-by-week timelines here — see 17-build-plan.md instead.

---

> **Decisions confirmed (see [08-decisions-log.md](./08-decisions-log.md) for full
> detail):**
> 1. Orchestration = custom Postgres-backed state machine. No LangGraph, no spike
>    needed — decided directly.
> 2. POC/MVP entry point lives inside the real MA app from day one, with a genuinely
>    polished, professional UI — not a bare-bones internal tool. This is reflected in
>    Phase 1 below (extra UI time budgeted).
> 3. Multiple real historical job sources are available from MA (Qasim and Faraz) —
>    see [09-data-request-for-ma.md](./09-data-request-for-ma.md) for the exact ask to
>    send them.
> 4. August 2026 client meetings (23–24 Aug, Qasim/Cass + Faraz "S FA"): Phase 1 is
>    bank → trial balance only; weekly scorecard sprints; OneDrive drop-zone
>    pipeline must work before Phase 1 is declared started. Nylon and FreeAgent are
>    not Phase 1. Phase 1 is a **learning/sandbox phase, not a kill-gate** — the
>    project has started, not paused pending Phase 1's verdict. Target 90%+
>    transaction accuracy before relying on it. FreeAgent's API is read-only;
>    MTD submission needs a separate technical approach, still to be tested. See
>    [12-meeting-aug2026-analysis.md](./12-meeting-aug2026-analysis.md).

This is the phased build plan. Each phase has: what gets delivered, what **you/MA**
need to provide, what **engineering** does, and how you'll know it's actually done
(not just "looks like it works in a demo").

How many agents exist at each phase is deliberately **not** fixed at 4 from day one —
see the reasoning in [02-architecture.md](./02-architecture.md) §2.5. It grows as each
piece proves itself:

- **POC:** 1 real AI agent (Bookkeeping). Everything else is plain code.
- **MVP:** still ~1 AI agent, hardened, plus a much lighter deterministic
  reconciliation validator.
- **Post-MVP / early Production:** Accounts Preparation joins — likely mostly templated
  code with an LLM assist for prose, not a full peer agent (needs the real historical
  jobs to confirm).
- **Production:** Review Agent and Reporting Agent added once the above are proven.

---

## Phase 0 — Discovery (before any code)

**Duration:** 1–2 weeks, but gated by MA's responsiveness, not an engineering estimate.

**What MA/you need to provide** (this is the actual blocker right now):
1. 2–3 fully completed historical accounting jobs (before-and-after: raw
   transactions + supporting docs + prior-year file → final reviewed file).
2. Chart of accounts.
3. VAT codes and the exact VAT decision rules.
4. The exact rules for P&L vs. Balance Sheet classification.
5. The rule for when a new account should be created.
6. The bookkeeping template(s) currently used.
7. The exact bank reconciliation procedure.
8. What "pages agree to TB" means concretely in their Excel files (which tabs, which
   links).
9. The internal review checklist.
10. Examples of real reviewer queries/corrections.
11. Ideally: a recorded walkthrough of one real job end-to-end with an MA accountant
    narrating every decision.

**What engineering does in parallel:** set up the base repo structure, Postgres schema
migration for the new `ai_*` tables, the model-provider abstraction, and the ingestion
skeleton — none of this strictly needs MA's data yet, but the *real* work (Week 1
onward below) does.

**Hard pre-condition before Phase 1 is declared started (agreed Aug 2026 meeting):**
the OneDrive drop-zone pipeline must be set up and tested — drop a file in the
shared Agent folder, confirm the Railway backend copies it, confirm it lands in
Supabase Storage / `ai_documents`, confirm parse speed. Until that path is reliable,
Phase 1 has not started. See [06-next-steps-checklist.md](./06-next-steps-checklist.md)
Step 1b.

**Deliverable:** "Bookkeeping Agent Specification v1" — a written document with every
flowchart decision point mapped to an exact rule, plus the 2–3 historical jobs staged
and ready to use as test data. Also: written success/failure criteria for the blind
accuracy test, agreed with MA *before* the first scored run.

---

## Phase 1 — POC (Bookkeeping Agent only)

**What it is (locked after Aug 2026 meetings):** one agent, one job type. Bank
statements in, trial balance out. Not documents, emails, handwritten notes,
FreeAgent, Nylon, or MTD. The AI categorises lines, flags what it does not
understand with a real question, code builds the TB and bank rec, humans approve.

**Reframed after the 23 Aug follow-up meeting — this matters:** Phase 1 is a
**learning and sandbox-testing phase**, not a pass/fail gate that can end the
project. In Mirza's own words: "it's not like, oh, it's not working, phase one
is gone, finished, we're not going ahead with the project." The project starts
at Phase 1 — it uses sandbox testing and real (including in-progress) jobs to
learn how the AI performs on different data patterns, so Phase 2 is easier and
more reliable. Do not present this to the client as "if it fails we stop" —
present it as "this is where we train and tune before you rely on it." The hard
software gates (TB balances, bank rec agrees) do not change — those are still
binary checks. What changes is the framing around AI accuracy: it is expected to
improve over the weeks, not to pass or fail on day one.

**Duration:** 5–7 weeks after the drop-zone pipeline is working and at least one
complete historical job (raw + final file) is in hand. Not 10–14 days. Weekly
scorecards throughout — no six-week silence then a demo. MA may also be asked for
data on jobs that are still in progress (mid-job), not only finished ones, to
widen the range of patterns the AI is trained on.

**Scope:**
- Year-end bookkeeping only. Inputs: current-year bank CSV/XLSX, previous-year
  working file if available, MA client/job context from `companies` / `wip_jobs`.
- No PDF/OCR. No FreeAgent/Xero/Nylon in this phase. Nylon is a Phase 2 fallback
  in the categorisation chain if a developer API exists. FreeAgent is planned for
  Phase 2 as an optional invoice data source.
- Orchestration: custom Postgres-backed state machine (decided).
- Categorisation logic is a live workstream, not a one-off. Current working chain
  is in [02-architecture.md](./02-architecture.md) §2.5.1. Keep tightening it until
  it is solid; do not treat the first prompt as finished.

**How delivery works (weekly sprints):**
- Each week: run against the golden historical job(s), produce a scorecard, share
  it, tune the right layer (data / mapping / rule / prompt / model / threshold),
  repeat.
- Proof engine first (ingestion, classify, TB, rec, exceptions with questions).
- Polished AI Accountant UI inside MA follows once the scorecard is real and
  moving — still production-quality, still inside the real app, just not before
  numbers exist. (This slightly sequences Decision 2: UI still in MA, not first.)

**UI (once scorecards are running):** job-creation flow (client picker, file
upload), streaming chat for starting jobs and ad-hoc questions, a **separate
exception-review table** (not mixed into the chat) with per-row reason and the
question the AI is asking, a five-state job status badge (Queued → Processing →
Needs your input → Ready for review → Approved), and both email + in-app
notifications when a job needs input or is ready. Output is MA's Excel template
plus a one-page PDF summary, both downloadable from the job. A **Data Centre**
page (list/delete what the AI holds) is a protection idea to agree with MA, not
assumed in the first build. Same MA design system as the rest of the app. Real
screenshots are owed to MA before the layout is treated as final. See
[02-architecture.md](./02-architecture.md) §2.1.1 (workflow/UI design) and §2.13.1
(data protection).

**Week-by-week (indicative, starts after pipeline + data):**
- **Week 1:** `ai_*` schema; model-provider abstraction; CSV/XLSX ingestion;
  state machine; first categorisation chain (prior mapping → firm rule → LLM →
  exception with a question).
- **Week 2:** First blind run on historical job 1; first weekly scorecard; fix
  the right layer; agree written pass/fail criteria with MA if not already locked.
- **Week 3:** Second historical job if available; confidence-threshold tuning;
  exception questions must be specific (not "unsure"); TB and bank rec as hard
  software gates.
- **Week 4:** Exception-review table (separate from chat) + job view inside MA
  with the five-state status badge + email/in-app notifications; keep weekly
  scorecard. Data Centre page only if MA has chosen that idea.
- **Week 5:** Benchmark 2 LLMs on the golden set; quantified scorecard; decide
  whether Phase 2 is unlocked.
- **Weeks 6–7 (buffer):** messy bank exports, data delays, categorisation
  edge cases (personal vs business). Contingency, not padding.

**Deliverable — what "done" looks like:** weekly scorecards against real MA
jobs, then a demo inside the real MA app. Example: "1,247 transactions, X%
auto-classified, Y exceptions with a question, trial balance balanced yes/no,
bank rec agreed yes/no." Not "look, a chatbot." See
[07-quick-wins-for-client.md](./07-quick-wins-for-client.md).

**Hard gates (code, not AI):** trial balance must balance; bank rec must agree
or the job does not reach human approval. Liability boundary: the AI/SOP layer
must finish those checks before a human is asked to sign off. Humans do not
re-do basic rec as the approval step.

**What you/MA need to do:** send raw + final historical files (including at least
one job that is still in progress, if possible — helps train on mid-job patterns,
not only finished ones); sign the NDA before sharing sensitive client data; do a
dedicated walkthrough call (Qasim/Cass) through one real job step by step
(comparatives, opening balances, bank analysis, sales invoice listing — the
firm's actual SOP, not just the general flowchart); agree success criteria in
writing before the first scored run; be available weekly to answer the AI's
exception questions; review the exception list.

**Continuity plan (agreed 23 Aug meeting) — three concrete scenarios:**
1. **Mirza becomes unavailable long-term:** MA gets full access to the code
   repository, Railway hosting, and all infrastructure to migrate or bring in
   another developer.
2. **Responsibility moves from Faraz to Qasim/Cass internally:** Mirza's team
   runs a formal knowledge-transfer (KT) session with whoever takes over.
3. **Project continues, occasional support needed:** a specific developer from
   Mirza's team stays on as point of contact for issues, not just Mirza personally.

This should be written into the contract, and summarised in the proposal so the
client sees it is already designed, not an afterthought.

**Honesty on "100% success":** TB and rec can be guaranteed by code. Silent
guessing can be forbidden by design. Line-level categorisation accuracy cannot
be guaranteed at 100% — it depends on the jobs MA sends and on how well the
exception questions are designed.

**Accuracy target (set in 23 Aug meeting): 90%+.** Mirza's own framing: "we know
that we are able to hit like 90% plus transaction ratings or scores, then it just
comes to the human approval." This is the number to communicate — a per-transaction
rating/scoring process runs in the early weeks specifically to measure this, not
just a single end-of-phase test. Below 90%, keep tuning before treating output as
reliable; above it, human approval becomes a fast final check rather than a full
re-check.

**Why the categorisation risk is lower than first feared:** Qasim's own
assessment (23 Aug meeting) — HMRC publishes a defined list of roughly 500
allowable expense categories, and most transactions map cleanly onto one. A
plain LLM chat already gets close to this right without extra tooling. Nylon
is not needed for the common case — only potentially for edge cases, and "we're
not there yet." This does not remove the need for the AI to ask when genuinely
unsure (personal vs business is the real edge case, not the tax category
itself) — see the exception-question requirement below.

**Assistant scope (open decision, not yet resolved):** should the assistant
answer general questions (e.g. "what is 100 + 100") like a normal chatbot, or
stay restricted to accounting topics only? Raised by Faraz (S FA), 23 Aug
meeting. Negligible cost/speed difference either way. If restriction is wanted,
implement via prompt instructions plus a knowledge-base scope check — do not
build a second system for this. **Owner: Faraz to decide.**

---

## Phase 2 — MVP

**Duration:** 6–10 weeks after the POC is accepted.

**Scope:**
- Bookkeeping agent hardened against multiple real clients, not just the 2–3 POC
  examples — client memory (approved mappings) starts actually improving results job
  over job.
- Full integration into the MA dashboard: an AI job is tied to a real `wip_job_id`,
  exception review becomes a proper workflow (not just a bare table), stage-level
  approval buttons with the "why" trace visible.
- Excel output matches the firm's real template structure (formulas preserved, tabs
  linked) — this graduates from the POC's flat export.
- Documents / invoices / OCR matching (client-facing Phase 2).
- **FreeAgent API (planned here, not Phase 1):** optional data source for clients
  already on FreeAgent — pull invoices/contacts so matching does not wait on email
  PDFs. Design Phase 2 document tools so FreeAgent can sit behind the same
  `get_supporting_documents()` / invoice interfaces. Confirm API access first.
- **Nylon (optional fallback, not required):** if a developer API exists, add
  `validate_categorisation(...)` between LLM judgement and the exception queue
  (see [02-architecture.md](./02-architecture.md) §2.5.1). System works without it.
- Accounts Preparation stage added for year-end accounts specifically (scope to be
  confirmed once Phase 0/1 data shows how much of it is templated vs. genuinely
  agentic), gated by one human approval.
- Server-side auth hardening scoped specifically to the new AI-facing endpoints (see
  [02-architecture.md](./02-architecture.md) §2.13) — even if the rest of the app's
  auth isn't rewritten yet.

**What you/MA need to do:** provide more historical jobs if available (more test
coverage = more confidence), start using the system on a real (low-risk) client
alongside the normal manual process so results can be compared side by side, and assign
someone to own the "approve proposed client/firm memory rules" review queue.

**Deliverable:** the AI Accountant is a real, usable feature inside the MA dashboard
for year-end bookkeeping, running against real (not just historical) clients, with a
human approving results before anything is treated as final.

---

## Phase 3 — Production

**Duration:** 3–6 months of iterative work after MVP, not a single phase.

**Scope:**
- Add Review Agent (LLM-based second check for genuine judgement calls the
  deterministic validators can't make) and Reporting Agent (mostly templated
  generation, LLM for the prose summary only) — informed by what MVP actually revealed
  about where AI judgement adds real value.
- Support additional job types (VAT, personal tax) using the same state-machine
  pattern with different stage graphs.
- **Making Tax Digital (MTD)** is a named Phase 3 requirement, not an add-on: VAT
  and personal tax outputs must be able to talk to MTD-enabled software, not only
  produce Excel.
- **MTD/FreeAgent submission approach — corrected 23 Aug, this is an open R&D
  item, not a solved integration:** the FreeAgent API is **read-only**. All MTD
  work (preparation, review, and HMRC submission) happens inside the FreeAgent
  software itself — there is no Excel step to hook into. A read-only API pull
  into a spreadsheet does not help; it adds a step. Qasim's proposed alternative:
  a **computer-use style approach** (the AI operates the FreeAgent software
  directly, the way Claude's computer-use feature drives a browser/desktop),
  possibly from a dedicated machine in the office. Mirza's position, and the
  right one: do not commit to an approach until it is actually tested — "we can
  test some of these routes and whichever one works, we go for that." Budget an
  explicit technical spike for this before Phase 3 MTD scope is locked.
- FreeAgent/Xero appear as new implementations behind the existing tool interfaces
  for **read access** (invoices, contacts, P&L data) — no agent rewrite required.
  Phase 2 already starts FreeAgent as a read source. The write/submission path for
  MTD is the open R&D item above, not assumed to be API-based.
- Proactive deadline/missing-information alerting, built on the app's existing Resend
  email-automation infrastructure rather than a new notification system.
- Full firm-wide security hardening — this may require addressing the whole app's auth
  model, not just the AI-facing surface; flag this to the wider MA engineering roadmap
  as a real dependency, not something the AI project alone can fully own.
- Revisit fine-tuning only if the accumulated real-job dataset and cost profile justify
  it (unlikely to be necessary before this phase, if ever).
- **Per-client portal** (separate section from the chat, showing every AI job run
  for that client, statuses, downloadable outputs) — explicitly placed in Phase 3
  by Mirza in the 23 Aug meeting, confirmed 25 Aug 2026. Not a new build: the same
  job-list UI from Phase 1, scoped to one client and kept historically, plus a
  filter. Not Phase 1 or 2.

**Deliverable:** the full pipeline (Bookkeeping → Accounts Prep → human approval →
Review → senior approval → Reporting → client) running for real clients across more
than one job type, with full audit trail, proper security, and measurable time saved
per job.

---

## Realistic total timeline

- Discovery: 1–2 weeks (gated by MA's responsiveness).
- POC: 5–7 weeks (includes the confirmed polished in-app UI, see Phase 1 above).
- MVP: 6–10 weeks after POC.
- Production: 3–6 months of iterative work after MVP.
- **Total to a genuinely production-grade multi-agent system: realistically 6–9
  months** of focused work from when clean historical data starts flowing — not the
  10–14 days floated in early discussions. That number describes a demo, not a system
  accountants would actually rely on for real client work.

---

All three open decisions from the previous version of this document are now confirmed
— see [08-decisions-log.md](./08-decisions-log.md). Next: [06-next-steps-checklist.md](./06-next-steps-checklist.md)
for the exact ordered actions starting now, and
[07-quick-wins-for-client.md](./07-quick-wins-for-client.md) for how to present progress
to the client at each stage.
