# 15. Scope of Works — Phase 3: Bridgit AI (Full Pipeline, Presence and Team Integration)

> **Status:** Expected scope. Subject to revision based on Phase 1 and 2 learnings,
> new ideas, and pivots. Treat as directional, not contractually fixed.
> **Last updated:** 15 Sep 2026 — WhatsApp prioritised to early Phase 3 (Tofu
> research, 15 Sep). Xero confirmed used by MA Associates → read source moves
> up to early Phase 3 alongside FreeAgent.
> **Depends on:** Phase 2 complete and signed off.

---

## What Phase 3 Is

Phase 3 is where Bridgit stops being a job-processing tool and becomes a **team
member**. The accounting engine from Phases 1 and 2 is the foundation. Phase 3 builds
on top of it: Bridgit is present in WhatsApp, aware of the firm's live workflow, able
to handle the full accounts pipeline from source documents to filed returns, and
eventually coordinating a small team of specialist AI agents rather than doing
everything itself.

Faraz's framing from the project kickoff: *"Right now it's a 'do a job AI.' Later it
becomes a 'chat AI.'"* Phase 3 is where that transition happens.

---

## What Phase 3 Adds

### 1. WhatsApp and Meta Integration ⚡ *Early Phase 3 Priority*

> **Note (15 Sep 2026):** Tofu's research confirms WhatsApp is a primary channel for
> UK accounting clients sending documents. Bridgit's WhatsApp integration is therefore
> bumped to early Phase 3 Block A — not a nice-to-have. The daily briefing and
> "send invoice via WhatsApp" features both land here, before the full accounts prep
> pipeline.

Bridgit joins the MA Associates WhatsApp group as a participant. This means:

- **Listening:** Bridgit reads messages in the group and extracts anything relevant —
  a client mentioned, a job update, a deadline raised, a question asked. It adds this
  context to the relevant job or client record automatically.
- **Reporting:** Each morning (or on a schedule the team sets), Bridgit sends a
  message to the group: jobs due this week, jobs waiting on client information, jobs
  ready for review, approaching deadlines. A proper daily briefing without anyone
  having to pull up the dashboard.
- **Answering questions in WhatsApp:** "Bridgit, what's the status on ABC Limited?"
  or "Bridgit, when is XYZ's VAT due?" — answered directly in the group chat or DM.
- **Bridgit's number / account:** Bridgit has its own WhatsApp presence. Staff and
  eventually clients can message it directly.

**Technical route:** WhatsApp Business API via Meta's Cloud API or a provider like
360dialog / Twilio. Meta Business account required on MA's side. This is a real
integration, not a workaround — Meta provides official API access for business
accounts and verified providers.

**Future extension:** Bridgit in a client-facing WhatsApp group. Client sends
"when are my accounts due?" and Bridgit answers. MA team sees the conversation. This
is a client communication layer, handled carefully and with MA's approval per client.

---

### 2. Full Workflow Integration (WIP Awareness)

Bridgit becomes aware of the existing MA Associates WIP job board. It knows:
- Which jobs are assigned to which staff member
- What stage each job is at in the firm's pipeline
- What is overdue, what is coming up, what is blocked

This is a two-way integration with the existing `wip_jobs` table in the MA database.
Bridgit can surface WIP information in chat, in WhatsApp, and in the dashboard. When
an AI job completes, it automatically links to the relevant WIP job. The team no
longer needs to manually update two systems.

**What this enables:** "Who is working on ABC Limited?" answered in WhatsApp.
"What jobs are at partner review stage?" surfaced in the Bridgit dashboard. "Bridgit,
mark the ABC Limited year-end as complete" — updates the WIP board.

---

### 3. Full Accounts Preparation Pipeline

Phase 1 covers bank to trial balance. Phase 2 covers documents and invoice matching.
Phase 3 completes the pipeline:

- **Year-end accounts preparation** — from trial balance to draft statutory accounts,
  with AI-assisted narrative sections (directors' report, notes to accounts) generated
  from the numbers and reviewed by the accountant before use
- **VAT return preparation** — Bridgit calculates the VAT return from the categorised
  transactions, applies the correct VAT scheme (standard, flat rate, cash accounting),
  produces the return for human review and sign-off
- **Personal tax returns** — self-assessment return populated from the client's income
  sources, with supporting schedules, ready for review
- **Making Tax Digital (MTD)** — the submission pathway for VAT and income tax.
  FreeAgent's API is read-only and cannot file; Bridgit will test and use the route
  that actually works, including where necessary operating the software directly to
  submit. This will be tested and confirmed in Phase 3, not assumed.

All statutory submissions remain human-approved. Bridgit prepares and checks.
The accountant signs off and submits (or Bridgit submits with explicit accountant
authorisation, depending on the tested route).

---

### 4. Per-Client Portal

The "little portal for each client" Faraz described. A view inside the MA dashboard
(and optionally accessible to the client directly) showing:

- Every AI run for this client: date, job type, status, output files
- Current year accounts status vs last year
- Outstanding document requests and their status
- Upcoming deadlines
- Approved mappings and rules for this client (the standing knowledge Bridgit has built)

This is not a new system. It is the existing Bridgit job list, filtered to one client,
with a historical view and deadline context added. Building blocks exist from Phase 1.

---

### 5. Multi-Agent Architecture

Rather than one Bridgit doing everything, Phase 3 introduces specialist agents that
Bridgit coordinates:

- **Bookkeeping Agent** (core from Phase 1 — matures here)
- **VAT Agent** — specialised in VAT scheme rules, return calculation, MTD filing
- **Personal Tax Agent** — self-assessment, CIS, rental income, dividends
- **Accounts Prep Agent** — statutory accounts, notes, Companies House filing
- **Deadlines Agent** — always-on monitoring, proactive alerts, client chasing

Bridgit acts as the coordinator. When a staff member starts a job, Bridgit routes it
to the right agent or combination of agents, tracks progress, and brings results back
to the accountant in one place.

This mirrors how a real accounting team works: one partner-level coordinator routing
work to juniors with specific expertise.

---

### 6. General Assistant and Expanded Scope

Phase 3 is where Bridgit can begin answering questions beyond the immediate job at
hand. This is Faraz's vision of Bridgit as an account assistant that is always in
the room:

- General accounting questions from the team ("what's the current corporation tax rate?")
- Client query drafting ("write a chaser email to ABC Limited about missing invoices")
- Internal knowledge base ("what is MA's rule on when to create a new account code?")
- Staff onboarding ("Bridgit, explain how we handle CIS clients")

The scope of what Bridgit answers versus what it passes to a human can be configured
and adjusted by MA. This is a guardrail decision, not a build decision.

---

### 7. Additional Integrations (Pipeline for Phase 3+)

The following are on the roadmap for Phase 3 or beyond, depending on priorities
agreed at the Phase 2 review:

- **Xero** as a read source — **confirmed MA Associates uses Xero (15 Sep 2026)**.
  Moves from "optional" to "planned for early Phase 3." Implementation behind the
  same `get_supporting_documents()` interface as FreeAgent — no agent rewrite.
- **Companies House** — Bridgit already has access to the Companies House API in the
  MA dashboard. In Phase 3, it uses this proactively: confirmation statement due dates,
  filing history, officer changes relevant to a job
- **HMRC APIs** — where available for MTD, agent services, and VAT
- **Email integration** — Bridgit reads client emails (with permission) to extract
  documents, answer queries, and update job records without manual forwarding
- **Microsoft Teams / Slack** — same presence as WhatsApp but for firms using Teams
  internally (relevant if MA expands its team)
- **Self-hosted LLM (longer term)** — Faraz mentioned the idea of running the model
  entirely under MA's control on a dedicated server. Not Phase 3, but the architecture
  supports it — the LLM abstraction layer from Phase 1 means switching the underlying
  model requires no changes to the rest of the system

---

## What MA Associates Provides for Phase 3

| What | Why |
|---|---|
| Meta Business account verification | WhatsApp Business API access |
| WhatsApp group for Bridgit to join | Integration setup and testing |
| Decision on client-facing WhatsApp | Which clients, what permissions |
| FreeAgent / Xero API credentials | Additional read sources |
| MTD agent services credentials | HMRC submission pathway testing |
| Agreed accounts preparation workflow | Year-end, VAT, personal tax SOPs |
| Decision on which agents the team wants first | Prioritisation of the multi-agent build |

---

## Definition of Done — Phase 3

Phase 3 is done in stages, not as one release. Each block below is a separate
sign-off point:

- [ ] Bridgit active in MA WhatsApp group: daily briefing sent, questions answered
- [ ] WIP job board linked: Bridgit knows who is working on what and surfaces it on request
- [ ] VAT return prepared end-to-end by Bridgit, reviewed and approved by accountant
- [ ] At least one personal tax return prepared by Bridgit ready for human review
- [ ] MTD submission route tested and working (or confirmed workaround documented)
- [ ] Per-client portal live with historical job view and upcoming deadlines
- [ ] At least two specialist agents (e.g. VAT + Deadlines) running alongside the
      core Bookkeeping Agent under Bridgit's coordination
- [ ] Faraz and Qasim sign off each block as it ships
