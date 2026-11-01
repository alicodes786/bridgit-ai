# 32. Call Prep — Joseph (Zenas Security / MA IT) × Mirza

> **Who:** Joseph (joseph@zenasecurity.nl, based in Holland/Europe timezone),
> Faraz (MA Associates), Mirza (and/or devs)
> **Subject:** Azure VM hosting for Bridgit + MA dashboard, OneDrive integration,
> Microsoft server security
> **Contact:** joseph@zenasecurity.nl — send calendar invite when confirming time
>
> **Call happened (~10 Oct 2026).** Notes, speakers, and actions:
> [33-joseph-call-notes.md](./33-joseph-call-notes.md). Decision 28 in
> [08-decisions-log.md](./08-decisions-log.md). This prep file stays as what we
> walked in with; do not treat “OneDrive” below as the live design — Joseph
> corrected it to **SharePoint**.

---

## What Joseph Already Knows (From Faraz)

- MA Associates is building an AI tool called Bridgit
- It will integrate with their database
- He wants to assess security before anything goes to production
- He is proposing an Azure Virtual Server to host the whole thing under one roof
- He wants to discuss OneDrive connectivity

---

## What Bridgit Is — Your One-Minute Explainer for Joseph

> "Bridgit is an AI bookkeeping assistant. MA accountants upload a client's bank
> statement. Bridgit reads every transaction, codes it automatically using MA's
> own prior accounting history, and produces MA's working Excel file plus a
> PDF summary. Anything it's not sure about it flags as a question for the
> accountant to answer. Nothing is filed or posted anywhere — it's a working
> paper tool. A human reviews and approves every output."

**Tech stack (current, what he'll ask about):**
- **Backend:** Python / FastAPI — currently running locally, intended for Railway
  or Azure
- **Database:** Supabase (hosted Postgres) — a separate project from MA's main
  Supabase DB, specifically for Bridgit
- **File storage:** Supabase Storage (uploaded bank files, output Excel/PDFs)
- **AI model:** Anthropic Claude API — **with Zero Data Retention (ZDR)
  confirmed**. Client data is not stored or used to train any model.
- **Frontend (Phase 1):** static HTML served from the FastAPI process (internal
  tool). Eventually moves into the existing MA Next.js / Vercel dashboard.
- **No client data is in the browser.** All processing is server-side.

---

## Questions Joseph Will Likely Ask You — Your Answers

### 1. "Does client financial data go outside MA?"

**Yes — two places:**
1. **Anthropic API (Claude)** — transaction descriptions and amounts are sent
   as part of the categorisation prompt. We have **Anthropic ZDR enabled**
   (confirmed 17 Sep 2026) — data is not stored, not logged, not used for
   training. Covered by Anthropic's Data Processing Addendum for business API
   accounts. Consumer claude.ai is never used.
2. **Supabase** — our Postgres database and file storage. EU hosting available
   (Supabase lets you pick region at project creation). All traffic is TLS.

**What does NOT leave:** the raw Excel/PDF files are stored in Supabase Storage
only. Only the extracted transaction rows are sent to the AI, not the original
files.

### 2. "Where is the database hosted, which region?"

Current: Supabase — we can select EU (London/Frankfurt) at project level.
If moving to Azure: Azure Postgres Flexible Server (managed) or Azure SQL,
in UK South / West Europe — MA's call.

### 3. "What data does the AI actually see?"

Each transaction: date, description, amount, debit/credit flag. That's it.
The AI does NOT see: client names, UTR/NI numbers, Companies House auth codes,
raw bank file metadata. Sensitive fields are excluded from prompts by design
(architecture doc §2.13).

### 4. "How do staff authenticate to Bridgit?"

Currently: a shared password via the `/app` UI (Phase 1 internal tool).
This is explicitly not production-grade auth — it's a dev/test gate.

For production (which is what Joseph is scoping): **we need proper auth**.
Options:
- Azure Active Directory (Entra ID) SSO — ideal if MA is on Microsoft 365,
  which they are. Staff log in with their MA Microsoft account. No separate
  passwords.
- This is actually the right answer for an Azure-hosted setup.

### 5. "Who has access to production data?"

- Faraz and Qasim (MA owners) — full access via the Bridgit UI
- Mirza and devs — only when debugging, with MFA on the Supabase/Azure console,
  access logged. Not standing access.
- No one else.

### 6. "What's the audit trail?"

Every AI decision is logged: which mapping fired, what the model proposed,
what confidence score, what the accountant accepted or overrode. Stored in
`ai_audit_log` in the database. Full traceability — "why was this transaction
coded as Motor?" can be answered from the DB alone.

### 7. "Can everything move to Azure?"

**Yes — this is a good idea and we're open to it.** See section below.

### 8. "GDPR / data protection?"

- MA Associates = Data Controller
- Bridgit / Mirza's team = Data Processor (covered by DPA in the contract)
- Anthropic = Sub-processor (ZDR, no training on client data)
- Supabase = Sub-processor (EU hosting available)
- Raw uploaded files: proposed 30-day deletion after sign-off; MA can delete
  sooner from a Data Centre screen in the app
- NDA signed before any real client files were shared with developers

### 9. "What's in the Azure VM proposal?"

Faraz mentioned ring-fencing everything under one roof. For Bridgit, that means:
- FastAPI service → Azure VM or Azure App Service
- Database → Azure Postgres Flexible Server (or keep Supabase and connect over
  private endpoint)
- File storage → Azure Blob Storage instead of Supabase Storage
- LLM calls → still Anthropic API (or Azure OpenAI Service — see below)
- Frontend → still Vercel/Next.js, or also host static files on Azure

This is achievable. It would mean migrating from Supabase + Railway to a
Microsoft-native stack — doable, and actually cleaner for an organisation
already on Microsoft 365.

---

## Questions to Ask Joseph

### OneDrive / Microsoft 365

1. **Which Microsoft 365 tenant is MA on?** (Need the tenant ID or domain for
   Graph API app registration)
2. **What's the intended OneDrive use?** Drop-zone: accountants drop a client's
   bank file → Bridgit picks it up automatically? Or just a backup/storage?
3. **Will you create an App Registration in Azure AD for us?** We need:
   - `Files.Read` or `Files.ReadAll` scope on the Graph API
   - Either a Service Principal (app-to-app, recommended) or delegated OAuth
   - Client ID + Client Secret for the app registration
4. **Which SharePoint site / OneDrive folder should Bridgit watch?** Is there
   an existing folder structure, or do we design one together?
5. **Is there a SharePoint Site rather than personal OneDrive?** A shared
   SharePoint team site is more robust for a multi-user firm than individual
   OneDrive folders.

### Azure VM / Infrastructure

6. **What size/spec is the proposed VM?** (Bridgit's FastAPI service is not
   compute-heavy — a B2s or B2ms is plenty. Heavy lifting is in the LLM API.)
7. **Windows or Linux VM?** (Linux preferred for Python/FastAPI; easier to
   containerise with Docker.)
8. **Will the VM be in a private VNet?** Can the Postgres database be on a
   private endpoint (no public IP)?
9. **Will Azure Active Directory / Entra ID SSO be set up for Bridgit?**
   (We strongly recommend this instead of a shared password.)
10. **Which Azure region?** UK South or West Europe for GDPR / data residency.
11. **Is Azure OpenAI Service on the table?** (Runs same Claude/GPT models but
    inside MA's Azure tenant — stronger data isolation than calling Anthropic
    directly. Requires Microsoft approval process, ~2–4 weeks.)
12. **Networking: will there be a VPN or ExpressRoute back to MA's on-premises
    network?** (Not needed for Phase 1, but good to know for Phase 2+.)
13. **Who manages the VM day-to-day?** Joseph's team, or handed to Mirza/devs
    after setup?
14. **Backup / snapshot policy?** Azure handles VM-level backups — what is the
    RPO/RTO expectation?

### MA's Existing Stack

15. **What is MA's main Supabase database used for today?** (We want to confirm
    whether Bridgit should share that DB or stay separate. Current decision:
    separate — but worth revisiting if Azure SQL is the new target.)
16. **Is FreeAgent hosted by FreeAgent Ltd, or does MA have an on-prem / private
    cloud FreeAgent instance?** (Affects Phase 2 FreeAgent API integration.)

---

## Azure Hosting — The Positive Case (Say This)

> "An Azure VM under MA's own tenant is actually the right long-term answer for
> a firm handling client financial data. It means:
> - All data stays in MA's own Azure subscription — you can see every byte
> - Private networking between the app, database, and OneDrive — no public
>   internet hops for internal traffic
> - Azure AD SSO — staff log in with their MA Microsoft account, no separate
>   Bridgit password
> - Azure OpenAI Service as an option — same frontier AI models but running
>   inside MA's own tenant, with Microsoft's data processing agreement
> - OneDrive integration via Microsoft Graph API becomes much simpler when your
>   app is already registered in the same Azure AD tenant
>
> For Phase 1, Railway was fine for speed. For production with real client
> financial data, Azure is the right home."

---

## Current vs Azure Architecture — Side by Side

| Component | Current (Phase 1) | Azure option |
|---|---|---|
| FastAPI API | Railway (PaaS) | Azure App Service / VM |
| Database | Supabase Postgres (EU) | Azure Postgres Flexible Server |
| File storage | Supabase Storage | Azure Blob Storage |
| AI model | Anthropic Claude API (ZDR) | Azure OpenAI Service or same |
| Frontend | Vercel (Next.js) | Vercel stays, or Azure Static Web Apps |
| Auth | Shared password (dev only) | Azure AD SSO (Entra ID) |
| OneDrive | Not connected yet | Microsoft Graph API (same tenant) |
| Secrets | Railway env vars | Azure Key Vault |

---

## Things to Confirm / Agree on the Call

- [ ] Azure subscription owner (Joseph's team or MA?) and who pays the hosting bill
- [ ] VM region (UK South or West Europe)
- [ ] App Registration for OneDrive Graph API — who creates it?
- [ ] Azure AD SSO setup — will Joseph's team configure Entra ID?
- [ ] Will Bridgit DB be on Azure Postgres or can Supabase stay (private endpoint)?
- [ ] Timeline — when can VM be ready?
- [ ] Azure OpenAI Service vs Anthropic API — preference?
- [ ] Standing developer access policy — how do Mirza/devs SSH/access for
      deployments?

---

## What to Send Joseph Before the Call

Email joseph@zenasecurity.nl with a calendar invite + this brief:

> Subject: Bridgit AI — technical overview for our call
>
> Hi Joseph,
>
> Looking forward to the call. Here's a brief technical overview of Bridgit so
> you can prepare your questions:
>
> Bridgit is an AI bookkeeping assistant for MA Associates. It's a Python/
> FastAPI backend that processes client bank statements, uses the Anthropic
> Claude API (with zero data retention — client data is never stored or used for
> training), and writes into MA's existing Excel working-file format. Currently
> it runs in a dev/test environment. We have not connected it to real client
> financial data at scale.
>
> We're fully supportive of the Azure VM proposal — it's the right move for a
> production environment. Key things we'll want to discuss:
> 1. Azure VM spec and region
> 2. App Registration for OneDrive / Microsoft Graph API access
> 3. Azure Active Directory SSO for staff authentication
> 4. Whether to use Azure OpenAI Service or stay with Anthropic directly
> 5. Database migration from Supabase to Azure Postgres (if preferred)
>
> Happy to share any technical documentation before the call if helpful.
>
> Best,
> Mirza
