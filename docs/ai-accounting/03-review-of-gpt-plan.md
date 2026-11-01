# 3. Honest Review of the ChatGPT Plan (`plans_by_gpt.md`)

You asked directly: was ChatGPT's plan good, and where would I differ. Here's the
honest answer, point by point.

**Overall verdict:** ChatGPT's *architectural instincts* are largely sound — I'd
estimate roughly 80% of it is correct and worth keeping. Its main weaknesses are (a)
adopting a specific framework (LangGraph) without applying the same "don't lock in
early" rigor it correctly demands for the LLM choice, (b) a timeline that ignores its
own stated data dependencies, and (c) treating Excel fidelity and confidence-score
calibration as minor details when they're actually load-bearing for whether accountants
will trust the output at all.

---

## 3.1 What it got right — keep these

- **The flowchart as the backbone, not an abstract multi-agent system forced onto the
  process.** Correct. This is a regulated, mostly-linear business process — the
  architecture should serve it, not the other way around.
- **The deterministic-vs-LLM split.** Correct, and it's the single most important idea
  in the entire document. Debits==credits, VAT-registered, account-exists, file-exists
  are code. Deciding which account an ambiguous transaction belongs to is genuine
  judgement.
- **Structured JSON output per transaction, not prose.** Correct and non-negotiable —
  this is what makes the pipeline testable and diffable against real historical
  outcomes.
- **Starting the POC on XLSX/CSV and deferring PDF/OCR.** Correct scope discipline —
  OCR/PDF extraction is its own large engineering problem and would swamp the first
  sprint if tackled up front.
- **Golden-dataset evaluation against real historical jobs, rerun on every change.**
  Correct, and should be treated as close to mandatory as anything in this whole
  project.
- **Model-provider abstraction, benchmark before committing.** Correct.
- **A dedicated audit schema** (`ai_jobs`, `ai_agent_runs`, `ai_tool_calls`,
  `ai_exceptions`, etc.). Correct instinct — full traceability is a hard requirement
  here, not a nice-to-have.
- **Flagging the current app's auth model as inadequate for production AI access.**
  Correct, and independently confirmed by reading the actual codebase (plaintext
  password comparison, client-side-only route guards, direct browser-to-Postgres
  access via the anon key).
- **Separating "operational Q&A" from "start/run a job" as two different code paths.**
  Correct — conflating these is a common and costly mistake in multi-agent systems.
- **The tool abstraction idea** — `get_bank_transactions()` reading Excel today and
  FreeAgent tomorrow without the agent's code changing. Correct and important; this is
  what avoids rewriting the agent later when a new data source is added.

## 3.2 Where I'd push back

**1. LangGraph is adopted almost by default, without the same skepticism applied to
the LLM vendor choice.**
The plan says (correctly) "don't lock in the LLM yet, benchmark it" — but then treats
"LangGraph fits better than a loose router" as close to settled fact. The actual
workflow here (per the flowchart) is a **linear pipeline with binary branches** — there
is no point where agents need to freely negotiate or discover their own next step. A
plain state machine backed by a Postgres table (a `current_stage` column plus an
explicit transition function) can deliver the same persistence and pause/resume
behaviour LangGraph is credited for, using infrastructure the team already owns and
understands, without adding a second framework with its own checkpointer storage,
versioning, and learning curve. My recommendation: spend 2–3 days spiking both before
committing to either — treat it exactly like the LLM choice, don't freeze it on faith.

**2. The 10–14 day POC schedule is not realistic against the plan's own stated
dependencies.**
The plan lists roughly 13 unresolved accounting-rule questions and requires 2–3
historical jobs from MA *before* meaningful engineering can start — and none of that
exists yet. A day-by-day 14-day schedule that assumes clean chart-of-accounts, VAT
rules, and historical ground truth are already in hand on day 1 describes an idealized
world, not the current one. I'd present the 10–14 day figure to the client as
aspirational framing from the meeting, not an engineering estimate, and plan for a
realistic **4–6 weeks** instead — see
[04-roadmap-and-deliverables.md](./04-roadmap-and-deliverables.md).

**3. It says "go define every diamond with Qasim/Faroz" but doesn't propose *how* each
one should resolve.**
Correctly identifies that the flowchart's decision points need real rules, but doesn't
commit to a resolution pattern. I've made this concrete in
[02-architecture.md](./02-architecture.md) §2.5 — most of these should be
deterministic-first with an LLM fallback, not LLM-first.

**4. Excel output generation is under-weighted.**
"Produce a structured Excel workbook" is a single bullet point in the plan, but the
flowchart's "pages agree to TB" implies the firm's real files are **formula-linked,
templated workbooks**, not flat data dumps. Reproducing that faithfully with openpyxl
(preserving formulas, cloning the firm's real templates, mapping cells) is a real
workstream, not an afterthought — I've given it its own section
([02-architecture.md](./02-architecture.md) §2.12).

**5. Confidence scores are treated as meaningful without ever being calibrated.**
An LLM stating "confidence: 0.94" is a plausible-sounding number, not a statistically
validated probability. Without checking it against real historical outcomes (does
"0.9+" actually correspond to ~90% real-world correctness?), a confidence threshold
gives false comfort. This needs a calibration step against the golden dataset — see
[02-architecture.md](./02-architecture.md) §2.9.

**6. The correction-to-memory feedback loop is asserted, not designed.**
"Approved corrections become future knowledge" is stated without a governance
mechanism, even though the original brief explicitly worries about "bad AI outputs
automatically becoming permanent memory." I've made this a first-class piece of the
architecture (a `proposed` → `approved` promotion workflow, never automatic) rather
than a side effect — see [02-architecture.md](./02-architecture.md) §2.7.

**7. Slightly over-designs for multi-tenancy that probably isn't needed yet.**
The plan's memory metadata includes `firm_id`, implying multi-firm design, but MA
Associates appears to be a single firm. Designing for multi-tenancy now is premature
generalization — worth keeping the field for future-proofing, but not worth spending
real engineering effort on isolation-by-firm today.

**8. Recommends embedding into the MA dashboard immediately, even for the very first
POC.**
I don't fully disagree, but I'd nuance it: a full workflow UI (exception queues,
polished approval screens) is premature before you even know the agent is accurate,
but a *thin* real entry point (a nav item, a job-creation form, a basic chat) is cheap
enough with the Vercel AI SDK that it's worth building from day one anyway — mainly for
stakeholder trust, so this doesn't look like a disconnected demo. See
[04-roadmap-and-deliverables.md](./04-roadmap-and-deliverables.md) for where the line
is drawn.

## 3.3 Net recommendation

Don't throw out the ChatGPT plan — its core instincts on determinism, structured
output, and evaluation are the right foundation, and I've kept them. The changes that
matter most are: don't freeze on LangGraph without testing the alternative, don't
promise a two-week timeline the plan's own prerequisites contradict, and give Excel
fidelity and confidence calibration the engineering weight they actually need.
