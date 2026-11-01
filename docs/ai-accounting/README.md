# MA Associates — AI Accounting System: Project Documentation

This folder is the **single source of truth** for planning and building the AI/LLM
multi-agent accounting system for **MA Associates**. It is fully self-contained —
copy this entire folder into the real production repository and it carries everything
discussed, decided, and designed so far, including the original source materials.

The standalone app now lives in this repo (`apps/api`, `apps/web`). Track what is
done vs next in [17-build-plan.md](./17-build-plan.md).

## Start here if you are building

**[17-build-plan.md](./17-build-plan.md)** — day-by-day checklist. Tick boxes as
work lands. This is the live build tracker for the standalone `bridgit-ai` repo.

**[20-client-files-koliqi.md](./20-client-files-koliqi.md)** — first client pack
(Starling PDFs, invoices, VAT workbook). Come back after Day 2 health is green.

**[24-sep19-meeting-agenda.md](./24-sep19-meeting-agenda.md)** — 19 Sep call with
Qasim: walkthrough, chart of accounts, VAT codes, questions to ask. Do not code
the job on the call.

**[27-job-types-catalog.md](./27-job-types-catalog.md)** — official list of jobs
Bridgit will eventually do, plus the **top 5** (company accounts, VAT, property
lettings, sole trader, CIS).

**[28-client-files-hithunters.md](./28-client-files-hithunters.md)** — second client
pack: Hit Hunters Ltd statutory year-end (comparative + CSV + completed file).

**[29-sep26-hithunters-and-job-catalog.md](./29-sep26-hithunters-and-job-catalog.md)** —
26 Sep analysis: Faraz job list, process log, revised next steps.

**[30-hithunters-excel-spike.md](./30-hithunters-excel-spike.md)** — Banking / Bank Pay
layout + Countingup rec numbers. Do not touch ETB yet.

**[32-joseph-call-prep.md](./32-joseph-call-prep.md)** — prep for Joseph (Zenas /
MA Microsoft security).

**[33-joseph-call-notes.md](./33-joseph-call-notes.md)** — ~10 Oct call: SharePoint
(not OneDrive), read-only Man Tax bridge, Railway PoC then Azure VM. Decision 28.

**[34-oct12-trial-status.md](./34-oct12-trial-status.md)** — 12 Oct night pause:
`/app` Cards+Chat, dummy Northbridge pack, what is still needed for Faraz.

**[35-oct25-faraz-trial.md](./35-oct25-faraz-trial.md)** — 25 Oct: Railway-ready
`/app`, background process, supporting uploads, mappings as knowledgebase.
Faraz gets `/app` only. Not ETB.

**[38-live-test-playbook.md](./38-live-test-playbook.md)** — **start here** for
Railway: Meridian Studio Ltd pack + exact click-by-click tests.

**[37-live-demo-northbridge.md](./37-live-demo-northbridge.md)** — legacy Northbridge
demo files (`/static/demo/*`).

**[36-oct25-session.md](./36-oct25-session.md)** — 25 Oct evening: Queued vs
failed, MA Bank Rec, Dummy Test Client deleted, chat-bar uploads after the
job exists. **Pick up here.**

---

## Read in this order

0. **[00-glossary.md](./00-glossary.md)** — plain-English definitions of every term
   used elsewhere in these docs (agent, orchestration, RAG, spike, fine-tuning, etc.).
   Read this first if any term elsewhere is unclear.

1. **[01-context-and-requirements.md](./01-context-and-requirements.md)** —
   everything we know: the business goal, the existing MA Associates app (stack,
   database, auth, what it already does), the client's real accounting workflow
   (flowchart), the original 4-agent idea, human approval requirements, RAG/memory/tool
   requirements, and what data we still need from MA.

2. **[02-architecture.md](./02-architecture.md)** — the actual system design: every
   piece explained — UI layer, orchestration layer, agent/execution layer, data model,
   tools, RAG, memory, security, observability. This is "what it looks like" and "what
   it contains."

3. **[03-review-of-gpt-plan.md](./03-review-of-gpt-plan.md)** — an honest,
   point-by-point review of the plan ChatGPT gave you (`plans_by_gpt.md`): what it got
   right, what I pushed back on, and why.

4. **[04-roadmap-and-deliverables.md](./04-roadmap-and-deliverables.md)** — the
   phased build plan: POC → MVP → Production, with concrete deliverables, what
   you/MA need to do at each phase vs. what engineering does, and a realistic timeline.

5. **[05-hosting-and-tech-stack.md](./05-hosting-and-tech-stack.md)** — answers "do
   we need to host this somewhere," clarifies what "LLM hosting" actually means, and
   gives a decisive platform recommendation (Railway) for the agent backend.

6. **[06-next-steps-checklist.md](./06-next-steps-checklist.md)** — the concrete,
   ordered checklist of what happens right now, step by step, fully trackable.

7. **[07-quick-wins-for-client.md](./07-quick-wins-for-client.md)** — the sequence of
   demo moments to show the client at each stage, what makes each one land, and what
   not to lead with.

8. **[08-decisions-log.md](./08-decisions-log.md)** — a running record of every real
   decision made on this project (orchestration engine, UI approach, hosting, data
   availability) with the reasoning behind each, so nothing gets re-litigated.

9. **[09-data-request-for-ma.md](./09-data-request-for-ma.md)** — the exact,
   prioritized list of what to request from Qasim and Faraz, plus a ready-to-send
   WhatsApp message.

10. **[10-session-history.md](./10-session-history.md)** — a chronological log of the
    planning conversation itself, turn by turn, so the full reasoning trail is
    preserved even outside this chat session.

11. **[12-meeting-aug2026-analysis.md](./12-meeting-aug2026-analysis.md)** — analysis
    of **two** August 2026 client meetings with Qasim (also "Cass" — same person) and
    Faraz ("S FA" in transcripts): Phase 1 reframed as a learning phase, 90%+ accuracy
    target, concrete continuity plan, corrected MTD/FreeAgent understanding, Nylon
    deprioritised further, assistant-scope decision, workflow/UI ideas, and a full
    action-items list split by owner (Mirza / Qasim / Faraz).

12. **[source-materials/](./source-materials/)** — the original files this whole plan
    was built from: `flowchart.jpeg`, `plans_by_gpt.md`, transcripts, and
    `meeting-transcript.md` (latest client meeting).

13. **[proposal.html](./proposal.html)** — client-facing proposal (3 phases). Update
    this when the plan changes; do not treat it as internal-only.

> **[11-commercial-proposal-and-pricing.md](./11-commercial-proposal-and-pricing.md) —
> INTERNAL ONLY, do not share with the client.** Pricing strategy and negotiation
> notes. Every other file above is safe to show MA Associates; this one is not — strip
> it out first if this folder is ever handed over.

---

## One-paragraph summary

We are not building a chatbot. We are building an **AI accounting operations system**
embedded inside the existing MA Associates Next.js/Supabase app, structured as a
**deterministic workflow (state machine)** that mirrors MA's real accounting process
(the flowchart), with **narrow AI agents** doing the parts that genuinely require
judgement (which account does this transaction belong to, what VAT treatment applies),
**plain code** doing everything that has a definite answer (debits=credits, VAT
registered, account exists), and **humans approving** every meaningful step before
anything becomes final. The LLM is never the source of truth — the database, the
original documents, and MA's approved rules are. We start by proving **one agent**
(Bookkeeping) against MA's own historical completed jobs before building anything else.

## Where things stand right now

- Architecture is designed (this doc set). August meetings:
  [12-meeting-aug2026-analysis.md](./12-meeting-aug2026-analysis.md).
  Decisions through **28** in [08-decisions-log.md](./08-decisions-log.md).
  **~10 Oct:** Joseph call — SharePoint Graph read-only to Man Tax, then Azure;
  [33-joseph-call-notes.md](./33-joseph-call-notes.md).
  **12 Oct:** `/app` trial UI (Cards/Chat) + dummy pack —
  [34-oct12-trial-status.md](./34-oct12-trial-status.md).
  **25 Oct evening:** [36-oct25-session.md](./36-oct25-session.md).
- Engine exists in `apps/api` (Koliqi VAT board job). Tracker:
  [17-build-plan.md](./17-build-plan.md).
- **26 Sep:** job catalog + Hit Hunters year-end pack in hand. Next build:
  process-log Phase 1 (bank analysis) for that client — see
  [29-sep26-hithunters-and-job-catalog.md](./29-sep26-hithunters-and-job-catalog.md).
- Live tracker and checkboxes: [17-build-plan.md](./17-build-plan.md). Do not treat
  older “blockers” in this README (OneDrive, CoA, no engine yet) as current — they
  are superseded.

## Key confirmed decisions (see file 08 for full detail)

- **Orchestration:** custom Postgres-backed state machine (no LangGraph).
- **POC/MVP UI:** lives inside the real MA app from day one, built to a genuinely
  professional/production-quality standard.
- **Data access:** confirmed available via Qasim and Faraz (MA Associates' owners).
- **Agent backend hosting:** Railway.
- **LLM strategy:** use API providers (OpenAI, Anthropic) — not a self-hosted model.
- **Phase 1 shape:** bank → TB only; weekly scorecards; pipeline first; a learning
  phase (not pass/fail), targeting 90%+ accuracy; Nylon/FreeAgent not in Phase 1.
- **MTD/FreeAgent:** FreeAgent API is read-only — MTD submission needs a separate
  technical approach (computer-use style automation is the leading candidate),
  still to be spiked and tested, not assumed.
- **Continuity:** three concrete scenarios agreed (full access handover, formal KT,
  or ongoing named developer contact) — see Decision 14.
- **Open decisions still owed:** assistant scope (Faraz, Decision 13), agent name +
  folder convention (Faraz, Decision 9), raw-file retention period (Faraz, Decision
  16 — 30 days proposed).
- **Data protection:** Data Centre page in MA, ZDR on Anthropic/OpenAI APIs, no extra
  vector DB, MFA, restricted developer access. Presented to the client as ideas to
  agree, not commitments. See Decision 16.
- **Workflow/UI:** chat for starting jobs/ad-hoc questions, a separate exception
  review table, a five-state job status (Queued/Processing/Needs your
  input/Ready for review/Approved), email + in-app notifications, Excel + PDF
  output, per-client history view kept for Phase 3. See Decision 17 and
  [02-architecture.md](./02-architecture.md) §2.1.1.
