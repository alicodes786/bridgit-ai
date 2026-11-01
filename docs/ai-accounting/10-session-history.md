# 10. Session History — How This Documentation Came to Be

This is a chronological log of the planning conversation that produced everything in
this folder. It exists so that if this folder is copied into a different repository,
whoever reads it (including a future AI assistant) understands the full arc of how we
got here, not just the final documents.

## Turn 1 — Initial codebase context request

**Ask:** get full context of the existing MA Associates app from the codebase, to hand
to another agent for LLM project planning.

**What happened:** a full exploration of the `job-dashboard-master` repository was
run, covering project structure, tech stack, database schema, API routes, auth
mechanism, frontend pages, backend services, config/env vars, integrations, and
confirming no existing AI/LLM code exists. The findings from this turn are what
populate [01-context-and-requirements.md](./01-context-and-requirements.md) §1.2.

## Turn 2 — The full project brief

**Ask:** a long, detailed brief was provided covering: the overall AI accounting
project goal, the existing app, the UI vision (chat inside the MA dashboard), the
client's real accounting workflow (a flowchart), the originally proposed 4-agent
structure (Bookkeeping, Accounts Preparation, Review, Reporting), human approval
requirements, orchestration requirements, the "LLM is not the source of truth"
principle, RAG/memory/tool architecture requirements, external integrations
(FreeAgent/Xero/Nylon/Companies House/Excel), a clarification that "training the LLM"
does not mean training a foundation model from scratch, evaluation strategy using
historical jobs as a golden dataset, POC scope, the data needed from MA before the POC
can start, a tentative tech stack, a security concern about the existing app's weak
auth, and the long-term target experience. Two supporting artifacts were referenced:
`plans_by_gpt.md` (a prior plan from ChatGPT) and `flowchart.jpeg` (the client's actual
accounting process diagram), plus meeting transcript materials.

**Ask specifically:** independently propose an architecture and development plan,
explicitly challenge assumptions rather than agree by default, address 23 specific
architecture questions, and separate the answer into POC → MVP → Production.

**What happened:** switched into Plan mode (appropriate given the scale and
architectural trade-offs involved). Read `plans_by_gpt.md` in full, `flowchart.jpeg`
directly, and the meeting transcript images/text (noting the images' content was
already reflected in the written brief, and `transcript.txt` was just pre-meeting small
talk with no substantive content). Produced a full plan covering:
- A context log organizing every piece of the brief (now
  [01-context-and-requirements.md](./01-context-and-requirements.md)).
- An honest review of `plans_by_gpt.md` (now
  [03-review-of-gpt-plan.md](./03-review-of-gpt-plan.md)) — verdict: roughly 80% of its
  architectural instincts were correct (deterministic-vs-LLM split, structured output,
  golden-dataset evaluation, tool narrowness, audit schema, flagging the weak auth), but
  pushed back on: adopting LangGraph without the same rigor applied to LLM vendor
  choice, an unrealistic 10-14 day POC timeline given the plan's own stated data
  dependencies, under-specifying how ambiguous flowchart decisions should resolve,
  under-weighting Excel template fidelity, and treating LLM confidence scores as
  meaningful without calibration.
- An independent architecture addressing all 23 requested points (now
  [02-architecture.md](./02-architecture.md) and
  [04-roadmap-and-deliverables.md](./04-roadmap-and-deliverables.md)) — key calls: a
  deterministic state-machine backbone (not a free-roaming agent supervisor) mirroring
  the client's flowchart; one real AI agent at POC (Bookkeeping only), growing to more
  agents only as each proves itself; a line-by-line mapping of every flowchart decision
  point to "always code" / "code first, LLM fallback" / "LLM primary, retrieval-first";
  a concrete `ai_*` Postgres schema reusing the existing `companies`/`wip_jobs` tables
  by foreign key rather than duplicating client data; a three-tier memory system
  (job/client/firm) with an explicit propose→approve governance step so corrections
  never automatically become permanent knowledge; a narrow tool architecture with a
  hard rule that no AI tool writes directly to core MA tables; no fine-tuning for
  POC/MVP; a realistic 6-9 month total timeline to a full production system, with a
  4-6 week POC (not 10-14 days); and named risks (data availability from MA as the
  single biggest schedule risk, confidence-score miscalibration, Excel template
  fragility, scope creep toward all 4 agents before agent 1 is trustworthy, and the
  existing app's security debt).
- Ended with three open decisions needing the user's confirmation: orchestration
  engine choice, POC UI location/polish level, and whether a data channel to MA already
  existed.

This plan was first produced inside Cursor's Plan Mode artifact (a `.plan.md` file
outside this repository, at `.cursor/plans/`), then the user asked for it to be written
into proper repo documentation instead.

## Turn 3 — Turning the plan into documentation

**Ask:** don't build yet — make the architecture, what it contains, what's needed from
the user, hosting, and deliverables fully clear; document all context in `.md` files;
make it clear enough that someone else could understand it; include the opinion on the
ChatGPT plan.

**What happened:** switched to Agent mode and wrote the first version of this
`docs/ai-accounting/` folder: `README.md`,
[01-context-and-requirements.md](./01-context-and-requirements.md),
[02-architecture.md](./02-architecture.md),
[03-review-of-gpt-plan.md](./03-review-of-gpt-plan.md),
[04-roadmap-and-deliverables.md](./04-roadmap-and-deliverables.md),
[05-hosting-and-tech-stack.md](./05-hosting-and-tech-stack.md), and
[06-next-steps-checklist.md](./06-next-steps-checklist.md) — turning the Plan Mode
content into a structured, cross-linked documentation set inside the actual
repository.

## Turn 4 — Confirming decisions and centralizing everything

**Ask:** confirmed the three open decisions (custom Postgres-backed state machine;
polished/professional in-app UI from day one; confirmed multiple real historical data
sources available via Qasim and Faraz on WhatsApp); asked for a concrete LLM hosting
platform recommendation (with clarification needed on what "LLM hosting" actually
means); asked for every step to be clear and trackable, and for the "biggest wins" to
show the client; asked what "spiking" means; asked exactly what to request from Qasim
and Faraz; and asked for **everything** related to this project — including the
original source materials and this conversation itself — to be centralized into one
folder that could be copied wholesale into the real production repository.

**What happened (this turn):**
- Recorded the three decisions in [08-decisions-log.md](./08-decisions-log.md).
- Updated [04-roadmap-and-deliverables.md](./04-roadmap-and-deliverables.md) to reflect
  the confirmed orchestration choice and the polished-UI decision (moving the POC
  timeline from 4-6 weeks to a more honest 5-7 weeks to account for the real frontend
  work that decision implies).
- Clarified in [05-hosting-and-tech-stack.md](./05-hosting-and-tech-stack.md) that "LLM
  hosting" isn't really a thing you do (you call a provider's API and pay per token);
  the actual hosting decision is for the agent backend service, and gave a decisive
  recommendation: **Railway**.
- Added [00-glossary.md](./00-glossary.md), including a plain-English definition of
  "spike" (a short, time-boxed technical experiment to answer one question before
  committing — not needed here anymore since the orchestration decision was made
  directly).
- Added [07-quick-wins-for-client.md](./07-quick-wins-for-client.md) — a sequenced list
  of demo moments mapped to the roadmap, with guidance on what to lead with and what
  not to.
- Added [09-data-request-for-ma.md](./09-data-request-for-ma.md) — the exact,
  prioritized data ask for Qasim and Faraz, plus a ready-to-send WhatsApp message.
- Copied all original source materials (`flowchart.jpeg`, `plans_by_gpt.md`,
  `transcript.txt`, `meeting_transcript.png`, `meeting_transcript_2.png`) into
  `docs/ai-accounting/source-materials/` so the whole folder is self-contained.
- Wrote this file, so the reasoning behind every document in this folder is traceable
  back to the actual conversation that produced it.

## Later — August 2026 client meeting (Point 1 docs pass)

Meeting transcript: [meeting-transcript.md](./meeting-transcript.md). Analysis:
[12-meeting-aug2026-analysis.md](./12-meeting-aug2026-analysis.md).

Point 1 documentation updates (not Point 2 data protection):
- Phase 1 locked to bank → TB, weekly scorecards, drop-zone pipeline as a
  start gate.
- Categorisation chain documented as working/live in architecture §2.5.1.
- Nylon = Phase 2 optional fallback. FreeAgent = Phase 2 read source. MTD =
  named Phase 3.
- Client proposal HTML updated to match. Continuity FAQ added. Contract
  continuity wording and data-protection section still outstanding.

## Later still — 23 Aug 2026 follow-up meeting (Cass confirmed = Qasim)

Meeting transcript: [meeting-transcript2.md](./meeting-transcript2.md). Analysis
appended to: [12-meeting-aug2026-analysis.md](./12-meeting-aug2026-analysis.md)
("Meeting 2" section).

User confirmed Cass and Qasim are the same person, and S FA in the transcripts is
Faraz, the other MA Associates owner. Documentation updates made this pass:
- Phase 1 reframed as a learning/sandbox phase, not a pass/fail kill-gate — the
  project has started at Phase 1, not paused pending its outcome. Hard software
  gates (TB, bank rec) unchanged.
- Concrete accuracy target set: 90%+ transaction scoring before human approval
  becomes a fast check rather than a full re-check.
- Nylon further deprioritised — Qasim's own view is that a plain LLM already
  handles most of HMRC's ~500 allowable-expense categories without it.
- MTD/FreeAgent understanding corrected: FreeAgent's API is read-only, so it
  cannot be the MTD submission path. Submission needs a separate technical
  approach (computer-use style automation is the leading candidate) — logged
  as an open R&D spike, not assumed solved.
- Continuity plan made concrete: three named scenarios (full handover access,
  formal KT session, or a named ongoing developer contact).
- New open decision logged: assistant scope (accounting-only vs. general
  chatbot) — owned by Faraz.
- Workflow/UI ideas captured: chat + dashboard experiences, and a "per-client
  portal" idea explicitly placed in Phase 3, not earlier.
- NDA + a dedicated SOP walkthrough call with Qasim logged as next actions.
- Updated: [04-roadmap-and-deliverables.md](./04-roadmap-and-deliverables.md),
  [08-decisions-log.md](./08-decisions-log.md) (Decisions 10–15),
  [02-architecture.md](./02-architecture.md) §2.5.1 and §2.10,
  [01-context-and-requirements.md](./01-context-and-requirements.md) §1.12,
  [06-next-steps-checklist.md](./06-next-steps-checklist.md),
  [12-meeting-aug2026-analysis.md](./12-meeting-aug2026-analysis.md), and
  [README.md](./README.md).
- `proposal.html` later received the Meeting 2 Phase 1 framing, 90%+ target,
  continuity scenarios, and Nylon/MTD corrections.

## Point 2 — Data protection (25 Aug 2026)

Client ask (Faraz): write model retention into the proposal, and give MA a
"data centre" they control from the dashboard (what stays, what goes).

Design locked as Decision 16:
- Existing MA Supabase only (`pgvector` in the same Postgres). No extra vector DB.
- **Data Centre** page in MA, not the Supabase admin console.
- Anthropic + OpenAI business APIs with zero data retention enabled. Not consumer
  chat apps. Not Llama as the production path.
- Raw files deletable (proposed 30 days after sign-off). Approved mappings and
  audit trail kept.
- MFA, restricted developer access, NDA + DPA, local copies deleted after use.

Updated: [proposal.html](./proposal.html) (new Data protection section),
[02-architecture.md](./02-architecture.md) §2.13.1,
[08-decisions-log.md](./08-decisions-log.md) Decision 16,
[04-roadmap-and-deliverables.md](./04-roadmap-and-deliverables.md),
[06-next-steps-checklist.md](./06-next-steps-checklist.md).

## Point 3 — Workflow / UI (25 Aug 2026)

Discussed openly first (recap of both meetings + new ideas), then four concrete
decisions confirmed with Mirza before writing anything:

- Chat and exception review are **separate surfaces** — chat starts jobs and
  answers ad-hoc questions; exceptions live in their own review table.
- Job status is a fixed **five-state lifecycle**: Queued → Processing → Needs
  your input → Ready for review → Approved.
- Notifications: **both** email (existing Resend infra) and in-app.
- Output: MA's **Excel template + a one-page PDF summary**, both downloadable.
- The per-client "portal" idea (Faraz's phrase) stays **Phase 3**, framed as the
  same job-list UI scoped to one client, not a new build.

Updated: [02-architecture.md](./02-architecture.md) §2.1.1 (new, full design),
[08-decisions-log.md](./08-decisions-log.md) Decision 17,
[04-roadmap-and-deliverables.md](./04-roadmap-and-deliverables.md) (Phase 1 UI +
Phase 3 portal wording), [06-next-steps-checklist.md](./06-next-steps-checklist.md)
(build tasks + screenshot follow-up), [12-meeting-aug2026-analysis.md](./12-meeting-aug2026-analysis.md),
[README.md](./README.md), and [proposal.html](./proposal.html) (status badge strip,
exception-review table mockup, notification/output feature cards, Phase 3 idea
card).

All three of Mirza's post-meeting points (Phase 1/categorisation reframing, data
protection, workflow/UI) are now reflected in the client-facing proposal.

## 25 Oct 2026 evening — Queued, Bank Rec, chat uploads

Mirza tested dummy Northbridge on `/app`. Queued after a crash was unclear
(Chat hid the fail). Bank Rec on the working Excel was too thin. Dummy Test
Client job was deleted. Chat bar now accepts files after the job exists.
Write-up: [36-oct25-session.md](./36-oct25-session.md). Decision 29 in
[08-decisions-log.md](./08-decisions-log.md).

## How to use this when moving to the real repository

Copy the entire `docs/ai-accounting/` folder as-is. Nothing in it depends on anything
else in this specific copy of the codebase except the file paths referenced in
[01-context-and-requirements.md](./01-context-and-requirements.md) §1.2 (which describe
the existing MA app's structure — those descriptions remain accurate as long as the
real repository is the same MA Associates codebase, which it is). Start any future
conversation about this project by pointing an assistant at
[README.md](./README.md) first.
