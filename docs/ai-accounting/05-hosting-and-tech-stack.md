# 5. Hosting and Tech Stack

Direct answer to "do we need to host it somewhere": **yes, one new thing needs
hosting** — the AI/agent backend service. Everything else either already exists or
doesn't need separate hosting. Here's the breakdown.

## 5.0 Important clarification — "LLM hosting" is a bit of a misnomer

There are actually **two different things** that sound similar but aren't:

1. **The LLM itself (GPT / Claude / Gemini)** — you never host this. You call the
   provider's API over the internet and pay per token used. There is no server for you
   to set up, choose a region for, or scale — the provider (OpenAI/Anthropic/Google)
   does all of that. This is true in POC, MVP, and Production alike, unless a much
   later decision is made to self-host an open-source model for cost reasons at very
   high scale — not relevant now.
2. **Your agent backend service** — the Python/FastAPI code *you* write, which calls
   the LLM's API, talks to your Postgres database, processes Excel files, and runs the
   deterministic checks. **This is the thing that needs a host** (Railway/Render/
   DigitalOcean/etc., see §5.3 below). It's not "LLM hosting" — it's hosting *your own
   glue code that happens to call an LLM*.

So the concrete decision you're actually making is: where does the FastAPI service run?
Not: where does the AI model run (that's already answered — on OpenAI's/Anthropic's/
Google's servers, via API).

## 5.0.1 Decisive pick for right now

**Use Railway for the agent backend service, starting immediately.** Reasoning:
fastest to get a FastAPI service live from a git repo, simplest way to add a Postgres
connection (or just point it at the existing Supabase Postgres connection string),
doesn't aggressively cold-start mid-demo the way some free tiers do (important since
you want a professional-looking POC to show the client), and it's cheap at this stage
(roughly $5–20/month for a small always-on service). Moving off Railway later, if
needed, is low-cost — it's a standard containerized Python service with no
Railway-specific lock-in.

For the LLM provider (the actual model calls), start with an **OpenAI API key** and an
**Anthropic API key** side by side behind the model abstraction (§5.4) so you can
benchmark both on the golden dataset per
[02-architecture.md](./02-architecture.md) §2.11 before picking a default — this is a
billing/API-key decision, not a hosting decision.

## 5.1 What does NOT need new hosting

- **The MA frontend** — stays exactly where it is, on **Vercel**. The new "AI
  Accountant" page/chat is just more pages/components in the same Next.js app.
- **The database** — stays in the **existing MA Supabase project**. The new `ai_*`
  tables are just more tables in the same Postgres instance MA already pays for.
- **The vector store (RAG)** — `pgvector` runs as a Postgres extension inside that same
  Supabase database. No separate vector database service needed.
- **Document storage** — Supabase Storage (already used elsewhere in the app) can hold
  uploaded Excel/CSV/PDF files.
- **The LLM itself** — you never host a model. You call a provider's API (OpenAI,
  Anthropic, Google, etc.) and pay per request/token. This is true at every phase,
  including production, unless a much later decision is made to self-host an
  open-source model for cost reasons — not something to plan for now.

## 5.2 What DOES need new hosting

- **The AI/agent backend service** — the Python (FastAPI) service that runs the actual
  agent logic: ingesting Excel/CSV, calling the LLM, running deterministic checks,
  talking to Postgres and the vector store. This is a new, small backend service that
  doesn't exist today and needs somewhere to run continuously (or on-demand).

### Why this can't just live inside the existing Next.js/Vercel app

Vercel is excellent for the frontend and light API routes, but the agent service needs:
Python (for pandas/openpyxl — genuinely better tooling for spreadsheet-heavy work than
the JS equivalents), potentially longer-running requests than serverless function
timeouts comfortably allow (processing hundreds/thousands of transactions), and a
stable place to hold model-provider credentials server-side. A small dedicated service
is simpler than fighting those constraints inside Vercel's serverless model.

## 5.3 Hosting options, by phase

**POC / early MVP — optimize for speed and low cost, not scale:**
- **Decision: Railway** (see §5.0.1 above). Render and DigitalOcean App Platform remain
  reasonable fallback options if you hit a Railway-specific limitation, but there's no
  need to evaluate further right now — start building.
- Keep it in a network-isolated / staging setup, not exposed with real client data,
  until the security work in
  [02-architecture.md](./02-architecture.md) §2.13 is done — this matters more than
  which host you pick.

**MVP → Production — optimize for reliability, security, and cost control as usage
grows:**
- Move to a proper cloud provider if/when you need: private networking to the
  database, background job queues (for longer-running jobs), autoscaling, or stronger
  compliance controls. Reasonable candidates: **DigitalOcean** (droplets/App Platform
  with managed databases, simplest step up from the POC setup), **AWS** (most
  flexible, more operational overhead), or **Fly.io** (good middle ground, easy global
  deployment).
- The actual decision should be driven by three things once you're at this stage: (1)
  measured real cost per accounting job at the transaction volumes you're actually
  seeing (don't estimate this in advance — measure it during the POC/MVP), (2) whatever
  security/compliance requirements come out of hardening MA's auth, and (3) whether you
  need background workers/queues yet (a 2,000-transaction job may need one; a 50-
  transaction job doesn't).

**Don't decide the final production host now.** It's a low-cost-to-defer decision — the
FastAPI service is portable across all of the above with minimal changes if it's built
cleanly from the start.

## 5.4 Full tech stack, phase by phase

**Frontend (all phases):**
- Existing Next.js 15 / React 19 / TypeScript app.
- Vercel AI SDK for the chat interface (fits the existing frontend, has built-in
  support for streaming responses and tool-call/approval UX).

**Data (all phases):**
- Existing Supabase/Postgres project (new `ai_*` tables added to it).
- `pgvector` extension for RAG.
- Supabase Storage for uploaded documents.

**Agent backend (POC onward):**
- Python + FastAPI.
- `pandas` + `openpyxl` for Excel/CSV ingestion and generation.
- A small internal model-provider abstraction (not a specific vendor SDK baked in
  everywhere).

**Orchestration (confirmed — see [08-decisions-log.md](./08-decisions-log.md)):**
- Custom Postgres-backed state machine. No LangGraph.

**LLM provider (benchmark before choosing a default):**
- Candidates to benchmark: OpenAI (GPT), Anthropic (Claude), Google (Gemini). Pick
  based on the golden-dataset scorecard, not marketing.

**Observability (from POC onward, lightweight at first):**
- Structured logging into the `ai_agent_runs`/`ai_tool_calls` tables is the minimum,
  from day one.
- Add a dedicated tracing tool (Langfuse, or OpenTelemetry) once there's enough volume
  that reading raw table rows isn't enough.

**Not needed yet, revisit later if justified:**
- Fine-tuning infrastructure (see [02-architecture.md](./02-architecture.md) — not
  needed for POC/MVP).
- FreeAgent/Xero/Nylon SDKs (FreeAgent planned Phase 2 as optional invoice
  source; Nylon optional Phase 2 categorisation fallback if API confirmed; neither
  in Phase 1).
- Background job queue / worker infrastructure (add only once job volume or size
  actually requires it).

## 5.4.1 Self-hosted LLM vs. API — should MA run its own model server?

**Decided: no — use provider APIs (OpenAI + Anthropic), not a self-hosted model.** See
[08-decisions-log.md](./08-decisions-log.md) Decision 5 for the log entry. Reasoning:

- **Quality gap.** Open-weight models you could self-host (Llama, Mistral, Qwen, etc.)
  still generally lag frontier proprietary models on complex judgement/reasoning tasks
  — and judgement quality is the entire value proposition of the Bookkeeping Agent.
  Not the place to trade accuracy for infrastructure control.
- **Cost, at actual current scale.** A GPU capable of running a decent model well costs
  real money 24/7 whether or not it's in use (roughly $1-2+/hour reserved) — hundreds
  of dollars a month before processing a single transaction. API costs at POC/MVP
  volume are tens of dollars total (§5.5 below). Self-hosting only becomes
  cost-competitive at sustained high volume, which doesn't exist yet.
- **Operational burden.** Running inference infrastructure reliably (scaling, security
  patching, model upgrades, uptime) is a specialized ongoing job that would compete
  with engineering time better spent on the actual accounting agent.
- **The privacy concern is already handled.** OpenAI, Anthropic, and Google all offer
  enterprise/business API tiers with zero data retention and a contractual guarantee
  data isn't used for training — this is what actually addresses the legitimate worry
  about sending client financial data to a third party, without the cost/complexity of
  self-hosting. **This must be switched on with the provider** (Anthropic ZDR is a
  sales/org setting, not the default on a free Claude account). Consumer ChatGPT /
  claude.ai are not used for client jobs. See [02-architecture.md](./02-architecture.md)
  §2.13.1.
- **Middle ground, if ever needed:** Azure OpenAI Service, AWS Bedrock, or Google
  Vertex AI provide the same frontier models via API but running inside MA's own cloud
  tenant/region with enterprise data-processing agreements — worth knowing about if a
  specific compliance requirement demands it later, but not needed for POC/MVP.
- **This is a reversible decision.** Because the model-provider interface is already
  designed to be swappable (§2.11 in [02-architecture.md](./02-architecture.md)),
  choosing API now doesn't lock out self-hosting later if the cost math or compliance
  requirements change.

**Revisit only if**, after Production, there's sustained high transaction volume that
flips the cost math, or a specific compliance mandate an API provider's enterprise tier
genuinely can't satisfy. Neither applies today.

## 5.5 Rough cost expectations (order of magnitude, to set expectations only)

- **POC hosting (agent service):** roughly $5–25/month for a small instance on
  Railway/Render/DigitalOcean App Platform.
- **LLM API costs during POC:** small — a handful of historical jobs, tens of thousands
  of tokens per job at most for classification tasks. Expect low tens of dollars total
  for the whole POC, not a meaningful budget line yet.
- **Production LLM costs:** this is the number that actually matters at scale (a
  year-end job can have 500–2,000+ transactions), and it should be **measured during
  the POC**, not guessed now — per-transaction LLM cost times real job volume is the
  real driver, and it depends heavily on which model wins the benchmark and whether
  transactions get batched into fewer, larger LLM calls versus one call per
  transaction. Budget time in Phase 1 specifically to measure and report this number
  before it becomes a Phase 3 surprise.
