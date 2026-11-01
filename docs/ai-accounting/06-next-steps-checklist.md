# 6. Next Steps Checklist

> ⚠️ **SUPERSEDED — do not use as the working plan.**
> This document was written before the `bridgit-ai` repo was created and before the
> 14 Sep 2026 decisions. It references the MA Supabase project (Bridgit has its own),
> OpenAI alongside Anthropic (Decision 18: Anthropic only for Phase 1), and OneDrive
> as a pre-condition (Decision 6: not a start-gate).
>
> **For the live working plan, use [17-build-plan.md](./17-build-plan.md).**
>
> This file is kept for historical context only — it shows the thinking and the ordered
> reasoning before the build started. Do not act on it.

---

## Step 0 — Decisions (done)

All three decisions that were blocking Step 0 are now confirmed — full detail and
reasoning in [08-decisions-log.md](./08-decisions-log.md):

- [x] **Orchestration engine** — custom Postgres-backed state machine. No LangGraph, no
  spike needed.
- [x] **POC location and quality bar** — inside the real MA app from day one, built to
  a genuinely professional/production-quality UI standard (not a bare internal tool).
- [x] **Discovery data channel** — confirmed available via Qasim and Faraz (MA
  Associates' owners) on an existing WhatsApp group. The actual data still needs to be
  requested and sent — see Step 1.

## Step 1 — Get the Phase 0 data from MA (the actual blocker)

The exact ask, prioritized, plus a ready-to-send message, is now in
[09-data-request-for-ma.md](./09-data-request-for-ma.md). Send that today — it's the
single most important thing standing between "we have a plan" and "we have a working
system." Summary of what's being requested:

1. [ ] 2–3 fully completed historical accounting jobs — raw transactions + supporting
  documents + prior-year working file + the final human-reviewed working file, for
   each.
2. [ ] Chart of accounts.
3. [ ] VAT codes and exact VAT decision rules.
4. [ ] Exact rules for P&L vs. Balance Sheet classification.
5. [ ] Rule for when a new account should be created.
6. [ ] The bookkeeping template(s) currently in use.
7. [ ] The exact bank reconciliation procedure.
8. [ ] What "pages agree to TB" means concretely in their real Excel files.
9. [ ] Internal review checklist.
10. [ ] Examples of real reviewer queries/corrections.
11. [ ] Ideally: record an MA accountant walking through one real job end-to-end,
  narrating every decision as they make it.

**Practical tip:** don't wait for all 11 before starting engineering — Step 1b and
Step 2 below can begin with partial data. Items 1, 2, and 3 are the minimum before
the Bookkeeping Agent itself can be scored properly.

**Also agree in writing before the first scored run:**
- [ ] Accuracy target: 90%+ (agreed 23 Aug meeting) — write this into the
  agreed criteria, not just TB/rec hard gates. Owner: Faraz + Mirza.

**Added after the 23 Aug follow-up meeting:**
- [ ] Send an NDA before MA shares sensitive client job data. Owner: Mirza.
- [ ] Dedicated SOP walkthrough call with Qasim (Cass) through one real job,
  step by step (comparatives, opening balances, bank analysis, sales invoice
  listing) — not just the general flowchart. Owner: Mirza to schedule, Qasim
  to walk through.
- [ ] Where possible, include one job that is still in progress (not only
  finished jobs) so the AI can be trained on mid-job patterns too. Owner: S FA
  / Qasim.

## Step 1b — Drop-zone pipeline (Phase 1 has not started until this works)

Agreed in the Aug 2026 meeting. OneDrive is a human drop zone, not a live desktop
mount.

1. [ ] Agree Agent folder name and client/job subfolder convention with S FA.
2. [ ] MA creates the shared OneDrive/SharePoint Agent folder (same pattern as
  the remote-contractor drop zone).
3. [ ] Connect ingest: Graph API (or equivalent) copies new files into Supabase
  Storage + `ai_documents`, tagged by client/job from folder path.
4. [ ] Measure speed: drop → copy → parse-ready. Fix if slow or flaky.
5. [ ] Parser turns bank CSV/Excel into canonical transaction rows. LLM is not
  in this path yet.

## Step 2 — Engineering setup (can start in parallel with Step 1)

1. [ ] Add the new `ai_`* tables to the existing MA Supabase project (schema in
  [02-architecture.md](./02-architecture.md) §2.6).
2. [ ] Build the model-provider abstraction (a single internal interface, no vendor
  SDK hardcoded everywhere) — start with OpenAI and Anthropic API keys side by side.
3. [ ] Deploy the FastAPI agent backend skeleton to Railway (see
  [05-hosting-and-tech-stack.md](./05-hosting-and-tech-stack.md) §5.0.1).
4. [ ] Build the CSV/XLSX ingestion + normalisation layer (canonical transaction
  shape).
5. [ ] Build the polished, real entry point inside the MA app (new nav item,
  professional job-creation flow with client picker + file upload, streaming chat via
  the Vercel AI SDK, five-state job status badge) — using the app's existing
  component library/theme so it matches the rest of the product. This is Win 1 in
  [07-quick-wins-for-client.md](./07-quick-wins-for-client.md) — worth demoing to the
  client as soon as it's ready, even before the agent itself is built.
6. [ ] Enable MFA on the MA Supabase project. Confirm Anthropic + OpenAI accounts
  are business/API with **zero data retention switched on** before any real client
  file is sent. Do not use consumer chat apps for client work.
7. [ ] Data Centre page in MA (`/ma/ai/data`): list raw files, working data, and
  approved mappings per client, with delete. See
  [02-architecture.md](./02-architecture.md) §2.13.1.
8. [ ] Build the exception-review table as its own screen, separate from the chat
  thread (see [02-architecture.md](./02-architecture.md) §2.1.1). Wire up email
  (Resend) + in-app notification when a job moves to "Needs your input" or
  "Ready for review."
9. [ ] Excel + one-page PDF summary output, both downloadable from the job page
  and stored in `ai_documents`.
10. [ ] Once the job-creation flow and exception table exist, capture real
  screenshots and send to Faraz/Qasim for layout feedback — this was explicitly
  requested, do not treat the proposal mockup as final.

## Step 3 — Build and test the Bookkeeping Agent against real historical data

1. [ ] Implement categorisation chain (prior mapping → firm rule → LLM with a
  question → exception queue). Keep refining this until it is solid — see
  [02-architecture.md](./02-architecture.md) §2.5.1. Nylon is not in this phase.
2. [ ] Implement the deterministic trial-balance assembly and validation checks
  (debits=credits, bank reconciliation). Job cannot reach human approval until
  these SOP checks pass (liability boundary).
3. [ ] Weekly sprint: run against the first real historical job with the answer
  withheld; produce a scorecard; share it; fix the right layer.
4. [ ] Repeat against a second historical job when available.
5. [ ] Benchmark 2 candidate LLMs against the golden set on accuracy, cost, and
  latency.
6. [ ] Investigate Nylon developer API (Qasim) — if it exists, design as Phase 2
  optional `validate_categorisation()` fallback. Low priority — do not block
  Phase 1 or Phase 2 delivery on this.
7. [ ] Confirm FreeAgent read-only API scope for Phase 2 invoice/contact
  reading. Do not design Phase 2 document tools in a way that makes it hard
  to add. Not Phase 1.
8. [ ] Technical spike (before Phase 3 MTD scope is locked): test approaches
  for the agent to operate FreeAgent for MTD submission — computer-use style
  automation is the leading candidate (Qasim's suggestion). Confirmed: the
  FreeAgent API cannot do this, it is read-only.
9. [ ] Decide assistant scope (Faraz) — accounting-only via guardrails, or
  general-purpose. Implement whichever is chosen via prompt + knowledge-base
  boundary, not a separate system.
10. [ ] Send workflow screenshots (dashboard view + chat view) to the client —
  owed from the 23 Aug meeting.
11. [ ] Start limited R&D on a simpler component while the main proposal is
  being refined (Mirza's team, in parallel).

## Step 4 — POC demo and decision point

1. [ ] Produce the quantified scorecard (accuracy %, exception count, trial balance
  balanced yes/no, bank reconciliation agreed yes/no, processing time, estimated
   review time saved).
2. [ ] Demo to stakeholders using a real historical job, not a synthetic example.
3. [ ] Decide, based on the real numbers: proceed to MVP as scoped, adjust scope, or
  pause and get more data first.

## What you can tell someone else about this project, in one paragraph

"We're building an AI accounting system inside MA Associates' existing dashboard, not a
separate chatbot. It follows MA's real accounting workflow as a controlled process —
code handles anything with a definite answer (does this balance, is the client VAT
registered), and AI is only used for genuine judgement calls (which account does this
transaction belong to). Every decision, tool call, and approval is logged for
traceability. We're proving this with one agent (bookkeeping) against MA's own real
historical jobs before building anything else, and a human has to approve results
before they're treated as final. The current blocker is getting real historical job
data and accounting rules from MA — engineering setup can start in parallel, but the
actual agent can't be properly tested without it."

## Where everything lives

- Glossary (plain-English definitions, including "what is a spike"): [00-glossary.md](./00-glossary.md)
- Full context/requirements: [01-context-and-requirements.md](./01-context-and-requirements.md)
- Architecture in detail: [02-architecture.md](./02-architecture.md)
- Review of the ChatGPT plan: [03-review-of-gpt-plan.md](./03-review-of-gpt-plan.md)
- Roadmap and deliverables: [04-roadmap-and-deliverables.md](./04-roadmap-and-deliverables.md)
- Hosting and tech stack: [05-hosting-and-tech-stack.md](./05-hosting-and-tech-stack.md)
- This checklist: [06-next-steps-checklist.md](./06-next-steps-checklist.md)
- Quick wins to show the client: [07-quick-wins-for-client.md](./07-quick-wins-for-client.md)
- Decisions log: [08-decisions-log.md](./08-decisions-log.md)
- Data request for MA (Qasim/Faraz): [09-data-request-for-ma.md](./09-data-request-for-ma.md)
- Full session history (how this all came together): [10-session-history.md](./10-session-history.md)
- Aug 2026 client meetings analysis (both meetings): [12-meeting-aug2026-analysis.md](./12-meeting-aug2026-analysis.md)
- Original source materials (flowchart, transcripts, prior plan): [source-materials/](./source-materials/)

