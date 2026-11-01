# 1. Context and Requirements Log

Everything gathered so far about the project, organized. This is the reference doc —
if a decision seems to come from nowhere later, it traces back to something here.

Source material used to build this: your written project brief (the most complete and
reliable source), `flowchart.jpeg` (read directly), `plans_by_gpt.md` (read fully), the
MA Associates codebase itself (read directly). `transcript.txt` only contained
pre-meeting small talk and added nothing. `meeting_transcript.png` /
`meeting_transcript_2.png` are long screenshots whose content is already reflected in
your written brief, which reads as a clean synthesis of that meeting — so the brief was
treated as the authoritative record rather than re-deriving it from the screenshots.

---

## 1.1 Business goal

Build an **AI accounting operations system** capable of progressively automating a
large part of MA Associates' accounting workflow. Not a chatbot. The long-term picture
is a small team of specialised AI accounting agents working together, with human
accountants reviewing/approving important stages.

The system should eventually:

- receive accounting jobs
- understand which client/job it relates to
- ingest accounting data and documents
- analyse transactions
- perform bookkeeping
- prepare accounts
- check/review accounts
- raise queries
- generate client-facing reports
- access data from accounting systems/APIs
- use historical client/accounting knowledge
- monitor deadlines and missing information
- interact with staff through the existing MA Associates dashboard

Automate routine accounting work while retaining human approval and full traceability.

## 1.2 The existing MA Associates application

Read directly from the codebase (`job-dashboard-master`), this is what already exists:

**Stack:** Next.js 15 (App Router), React 19, TypeScript, Tailwind, Supabase/Postgres,
Vercel hosting, Companies House API, Resend (email), Cloudinary (uploads).

**Two relevant Supabase projects:**
- **CB DB** — shared `users` table used for login across both products in the
  monorepo, plus an unrelated property-management product.
- **MA DB** — all MA Associates accounting data (companies, WIP, VAT, personal tax,
  clients, staff).

**Auth is custom and currently weak:**
- Login checks username + **plaintext password** against the CB `users` table.
- Session = a JSON blob in `localStorage` + a cookie (~7 days).
- Route protection is **client-side only** — there is no `middleware.ts`.
- Permissions are string arrays (`ma_permissions`, `access_to`) checked inside React
  components.
- Most MA data access happens **directly from the browser** via the Supabase anon key
  (`lib/ma-supabase.ts`, `wip-supabase.ts`, `vat-supabase.ts`, etc.), not through
  server-side API routes.

**Data already modeled in the MA database:**
- `companies` — company number/name, accounting year end, Companies House/HMRC due
  dates, submission flags, VAT registration + VAT number/next-due, confirmation
  statement due/submitted, CH auth code, email-automation status fields.
- `wip_jobs` — job number, client name, job type/period, pipeline + notes, fees/net/VAT/
  gross due/amount paid/balance due, which brand the client belongs to (MA/Mantax/JMP),
  staff assignment, submitted flag, plus a full `wip_audit_events` audit trail.
- `vat_clients` / `vat_submissions` — VAT quarter groups (A/B/C), submission history.
- `clients`, `personal_tax_clients`, `personal_tax_returns`, `personal_tax_submissions`
  — UTR, tax year, MTD flag, CIS fields.
- `ma_dd_enrolments` — direct debit collections.
- `staff_profiles`, `staff_notes`, `staff_submissions`.
- `directors`, `company_documents`, `filing_history`,
  `confirmation_statement_audit_log`.

**Existing integrations:** Companies House API (already live — search, company
profile, officers, filings), Resend (year-end/VAT chase emails), Cloudinary,
Slack webhooks. **FreeAgent, Xero, and Nylon are not integrated today** — they are
aspirational, and API access to them (especially Nylon) is not yet confirmed.

**No AI/LLM code exists anywhere in the app today.** This is a greenfield addition.

**Frontend surface today:** `/ma` (executive dashboard), `/ma/companies`, `/ma/wip`,
`/ma/vat`, `/ma/personal-tax`, `/ma/clients`, `/ma/confirmation-statements`,
`/ma/staff`, `/ma/users`, `/ma/settings/email-automation`. The natural place for the
new AI area is something like `/ma/ai` or an "AI Accountant" item in the sidebar.

## 1.3 The client's real accounting workflow (from the flowchart)

This is the actual process the AI needs to eventually replicate. It is the backbone of
the whole design.

1. Receive source document (bank statement, invoice, receipt, email).
2. Already Excel/CSV? If not → is it a readable PDF? → convert via Adobe, or manual
   entry if it's an unreadable scan/photo/email.
3. Add to working file.
4. Does a prior file exist? → yes: roll forward prior file (duplicate, bring
   comparatives) / no: use a similar client's file as a template.
5. Take the next transaction line from the bank/source data.
6. Does the account already exist? → no: create a new account, add it to the TB and
   P&L/Balance Sheet structure.
7. Assign the transaction to a P&L or Balance Sheet category (based on transaction
   type).
8. Is the client VAT registered? → yes: apply the appropriate VAT treatment/code.
9. Transaction categorised → posts toward the trial balance.
10. Match the transaction to supporting documentation (invoices/receipts).
11. Post to trial balance / balance sheet.
12. Validation checks, in order: debits = credits? → bank reconciliation agrees? → do
    accounts/pages agree to the trial balance? Any "no" sends it back (recheck coding /
    investigate difference / recheck TB links).
13. Internal review — reviewer checks the file. If queries are raised, the
    preparer/process makes amendments and review continues.
14. Send to client for approval.

**This is a mostly linear pipeline with a handful of binary branches** — not a
free-form negotiation between independent agents. That single fact should drive the
entire orchestration design (see [02-architecture.md](./02-architecture.md)).

## 1.4 The originally proposed agent structure

1. **Bookkeeping Agent** (build first) — reads transactions, selects accounts,
   categorises P&L/BS, applies VAT, matches evidence, flags uncertain transactions,
   produces structured output.
2. **Accounts Preparation Agent** — turns bookkeeping output into the appropriate
   accounts format (year-end company accounts, self-employed, property, etc.); rolls
   forward templates; populates schedules/comparatives. Human approval expected here.
3. **Review Agent** — AI second-check before senior human review: DR/CR balance, bank
   reconciliation, opening/closing balances, control accounts, comparatives, TB-to-
   accounts links, checklist items. Raises exceptions rather than guessing or silently
   fixing.
4. **Reporting Agent** — after final human approval, produces client-facing outputs
   (email summary, PDF, meeting briefing) covering revenue, profit, major expenditure,
   tax liability, deadlines, and year-over-year comparison.

## 1.5 Human approval requirements

The client explicitly does **not** want fully autonomous accounting. Proposed
structure:

```
Bookkeeping → Accounts Preparation → junior/first human review → AI Review →
senior/final human approval → Reporting → Client
```

During the initial transition, bookkeepers may also review raw AI bookkeeping output
even though the long-term goal is to automate more of that stage. The exact number and
placement of approval gates is expected to be tuned as the system is tested — it
should not be hardcoded as immovable.

## 1.6 Orchestration requirements

The orchestrator needs to know: client, job, job type, accounting period, current
stage, previous agent output, required next step, exceptions, approvals, and available
tools. The client deliberately did not want to assume LangGraph is the answer and asked
for an independent evaluation of router vs. supervisor vs. state-machine patterns.

## 1.7 Critical principle — the LLM is not the source of truth

Sources of truth are:

- **Operational data** — the MA Postgres/Supabase database.
- **Accounting evidence** — original Excel/CSV, bank statements, invoices, prior
  accounts, uploaded documents, and later FreeAgent/Xero data.
- **Firm knowledge** — approved MA accounting rules, bookkeeping rules, VAT rules,
  chart of accounts, templates, review checklists, historical decisions, SOPs.
- **External knowledge** — HMRC/tax data, Nylon (if it exposes an API), Companies
  House, FreeAgent, Xero.

The LLM reasons over and retrieves from these. It must never invent accounting facts.

## 1.8 RAG requirements

Not "vector search for everything." Structured facts (transactions, amounts, dates,
WIP status, VAT status, account codes) go through **SQL**. Unstructured knowledge
(SOPs, notes, historical commentary, client-specific knowledge, tax guidance, long
documents, policies, reviewer notes) goes through **RAG/vector retrieval**. Supabase
already supports pgvector directly in Postgres, so it's the natural fit — no separate
vector database needed initially. Knowledge must be isolated by client/job. Proposed
metadata: `firm_id`, `client_id`, `job_id`, `accounting_period`, `document_id`,
`source`, `approved_by`, `confidence`, `timestamp`.

## 1.9 Memory requirements

Three tiers:

- **Job memory** — temporary/stateful context for one specific job (e.g. "ABC Ltd —
  Year End Accounts — 2025/26"): current stage, documents, exceptions, decisions,
  outputs, previous agent results.
- **Client memory** — longer-term: recurring suppliers, historical account mappings,
  prior accounting treatment, client-specific rules, approved human corrections.
- **Firm memory** — MA-wide: bookkeeping methodology, chart of accounts, VAT rules,
  review procedures, templates, reporting style.

Human-approved corrections should eventually become future knowledge, but through a
**controlled process** — bad AI outputs must not automatically become permanent
memory. (See [02-architecture.md](./02-architecture.md) §2.6 for how this is designed.)

## 1.10 Deterministic logic vs. LLM reasoning

**Do not use an LLM when normal software can reliably answer the question.**

- **Deterministic/code:** debits==credits, client VAT registered?, account exists?,
  file exists?, accounting period, bank totals, status checks, workflow transitions,
  permission checks.
- **LLM/reasoning:** what does this ambiguous transaction represent?, which existing
  account best fits it?, does supporting evidence explain it?, what accounting
  treatment is most likely?, is a reviewer query required?, summarising accounts for
  the client.

## 1.11 Tool architecture requirement

Agents get narrow, named tools/functions — never unrestricted database access:
`get_client()`, `get_job()`, `get_transactions()`, `get_previous_accounts()`,
`get_vat_status()`, `lookup_account()`, `lookup_previous_mapping()`,
`retrieve_firm_rules()`, `retrieve_client_memory()`,
`retrieve_supporting_documents()`, `calculate_trial_balance()`,
`request_human_review()`, `save_draft_output()`. External systems (FreeAgent, Xero)
should eventually appear as swappable implementations behind the same tool interface
(e.g. `get_bank_transactions()` reads Excel today, FreeAgent tomorrow — the agent's
reasoning code doesn't change).

## 1.12 External integrations (phased — not all Phase 1)

- **FreeAgent** — not Phase 1. Planned Phase 2 as an optional invoice/contact
  data source for clients already on FreeAgent (avoids waiting on emailed PDFs).
  **API confirmed read-only (23 Aug 2026 meeting)** — cannot be used for MTD
  submission. See MTD note below.
- **Xero** — same pattern as FreeAgent if used. Not Phase 1.
- **Nylon** — MA already has a subscription. UK accounting rules / HMRC case
  knowledge. **Not required for Phase 1, and lower priority than first thought.**
  Qasim's own view (23 Aug meeting): most transactions map cleanly onto HMRC's
  ~500 allowable-expense categories and a plain LLM already handles this well —
  Nylon is a nice-to-have for edge cases, not a dependency. If a developer API
  exists, optional Phase 2 fallback in the categorisation chain (see
  [02-architecture.md](./02-architecture.md) §2.5.1).
- **MTD (Making Tax Digital)** — named Phase 3 requirement for VAT and personal
  tax. **Correction (23 Aug meeting):** all MTD work happens inside the
  FreeAgent software itself, with no Excel step, and FreeAgent's API is
  read-only. Submission cannot be done via API. The submission approach
  (leading candidate: computer-use style automation of the FreeAgent UI) is an
  open technical spike, not a solved integration — see
  [08-decisions-log.md](./08-decisions-log.md) Decision 12.
- **Companies House** — already integrated into the existing app.
- **Excel** — extremely important. The firm's existing accounting processes and
  templates are Excel-based, with linked tabs/formulas ("pages agree to TB").
- **OneDrive drop zone** — human copy/paste into a dedicated Agent folder
  (client/job subfolders). Backend copies via Microsoft Graph (or equivalent)
  into Supabase. Not a live desktop mount. Pipeline must work before Phase 1
  is declared started.

## 1.13 "Training the LLM" — terminology clarification

Not currently planning to train a foundation model from scratch. Making the system
"learn MA accounting" means:

```
foundation model + agent instructions + MA workflows + RAG + tools +
historical completed jobs + client memory + firm rules + human corrections +
evaluation datasets
```

Fine-tuning could be evaluated later if there's a clear reason for it. The model
provider should be abstracted so multiple models (GPT, Claude, Gemini, Llama, etc.) can
be benchmarked rather than permanently locking the project to one.

## 1.14 Evaluation requirement

Historical completed accounting jobs become a **golden evaluation dataset**: give the
AI previous-year accounts + current-year raw transactions + supporting documents —
**without** the completed human answer — let it process the job, then compare its
output to the real completed MA accounting job. Metrics: transaction categorisation
accuracy, VAT treatment accuracy, P&L/BS classification accuracy, missing/incorrect
transactions, reconciliation success, trial balance differences, number of AI
exceptions, number of human corrections, processing time, model/token cost, accountant
review time saved. Rerun this suite whenever the model, prompt, retrieval, tools, or
accounting rules change.

## 1.15 Data required from the accounting team before the POC can really start

1. 2–3 fully completed historical accounting jobs.
2. Raw/input transaction data for those jobs.
3. Previous-year working files.
4. Final human-reviewed working files.
5. Chart of accounts.
6. VAT codes.
7. VAT decision rules.
8. P&L vs. Balance Sheet classification rules.
9. Rules for creating new accounts.
10. Bookkeeping templates.
11. Bank reconciliation process.
12. Trial-balance linking/checking process.
13. Internal review checklist.
14. Examples of reviewer queries/corrections.
15. Supporting invoices/documents where possible.

A particularly useful exercise: have an MA accountant walk through one real job from
source documents all the way to client approval, explaining every decision, recorded.

**This is currently the single biggest blocker to the whole project.** See
[06-next-steps-checklist.md](./06-next-steps-checklist.md).

## 1.16 Security concern (explicitly flagged, confirmed independently in the codebase)

The current MA app's authentication is not strong enough to give an AI system
unrestricted access to sensitive accounting information. Production AI work will
require: server-side authentication/authorization, proper role permissions, secure
secret handling, audit logging, client-level isolation, tool-level permissions,
protection of sensitive fields, controlled AI write operations, and human approval for
risky actions. The AI must never simply receive an unrestricted database service
credential and be allowed to execute arbitrary operations.

## 1.17 Long-term target experience

```
AI Accountant: "ABC Ltd's year end is approaching. We have received the bank
statements but are missing two requested documents."

User: "Start the accounts with what we have."

System: opens an AI job → gathers MA client context → retrieves prior accounts →
imports transactions → runs Bookkeeping Agent → identifies exceptions → prepares
accounting schedules → requests human approval → runs Review Agent → requests senior
approval → produces final client report.
```

Meanwhile all state, agent actions, tool calls, source evidence, decisions, confidence
levels, approvals, and corrections are recorded and auditable.

## 1.18 Tentative tech stack as originally discussed (not final — see architecture doc)

- Frontend: existing Next.js/React MA application, chat interface inside MA.
- Database: existing Supabase/Postgres.
- Vector retrieval: pgvector or another suitable vector store.
- Agent backend: Python, FastAPI.
- Orchestration: LangGraph or a custom workflow/state engine — to be evaluated, not
  assumed.
- Accounting file manipulation: pandas, openpyxl, possibly specialised Excel tooling.
- LLM: model/provider abstraction, benchmark candidate models before choosing.
- Hosting: MA frontend stays on Vercel; AI backend hosting choice (DigitalOcean/AWS/
  other) should be based on cost, security, and workload — see
  [05-hosting-and-tech-stack.md](./05-hosting-and-tech-stack.md).
