# 14. Scope of Works — Phase 2: Bridgit AI (Documents, Intelligence, Monitoring)

> **Status:** Expected scope. Finalised after Phase 1 sign-off.
> **Last updated:** 15 Sep 2026 — Tofu research added email ingestion to Phase 2,
> auto-split bulk PDFs added, Xero confirmed used by MA Associates.
> **Depends on:** Phase 1 complete and signed off by MA Associates.
> **Note on scope flexibility:** Some items in Phase 2 may be pulled forward into
> late Phase 1 if the engine is ahead of schedule — specifically FreeAgent read
> integration and basic document ingestion. This will be confirmed during Phase 1
> Week 5 review. Nothing here is delayed for delay's sake; it moves forward as
> soon as Phase 1 is stable.

---

## What Phase 2 Is

Phase 2 is the step change from Bridgit **reading bank lines** to Bridgit **reading
the evidence behind bank lines**. In Phase 1, Bridgit sees a bank transaction and
decides what account it belongs to. In Phase 2, it also reads the invoice behind that
transaction, verifies the net and VAT split, matches them together, and flags anything
that does not add up.

This is where Bridgit starts genuinely replacing the manual bookkeeping pass rather
than just assisting it. The accountant's job shifts from chasing documents and
cross-checking to reviewing Bridgit's structured output and approving.

Phase 2 also introduces "always-on" behaviour: Bridgit watches deadlines, surfaces
missing documents proactively, and nudges the right person before anyone has to ask.

---

## What Phase 2 Adds

### 1. Document Ingestion (Invoices and Receipts)

Bridgit reads invoices and receipts uploaded by the team or the client. It extracts:
- Supplier name
- Invoice date and reference
- Net amount, VAT amount, gross total
- VAT treatment

It then matches each extracted invoice to the corresponding bank line. Where they
agree: the transaction is coded with high confidence, net and VAT split confirmed by
the actual document. Where they disagree or where no matching invoice exists: the
discrepancy is surfaced clearly in the exception table — not hidden.

**Supported formats:** PDF invoices, scanned receipts (OCR), Excel/CSV schedules,
email attachments where the client provides them via the drop zone.

**Auto-split bulk PDFs** — clients frequently send a single PDF containing multiple
invoices, receipts, and statements jumbled together. Phase 2 adds auto-detection of
document boundaries so Bridgit splits the pack before extraction, not after.
(Tofu confirmed this is a real day-to-day pain point at scale.)

**Email ingestion** — clients email invoices and receipts directly to an MA inbox.
Phase 2 Bridgit reads that inbox, extracts attachments, and feeds them into the same
document pipeline without manual forwarding. Moved from Phase 3 based on Tofu research
(15 Sep 2026) — lower complexity than WhatsApp, higher daily value.

**Quality bar:** Tofu (gotofu.com) is the market reference for document extraction
quality. Faraz has a Tofu trial running. Bridgit's Phase 2 invoice extraction must
match Tofu's line-item accuracy on standard UK supplier invoices. Where Bridgit
differs: output goes to MA's Excel template, not to Xero/QBO.

**What this means for the accountant:** far fewer manual "find the invoice for this
payment" tasks. Bridgit has already located and read it before the job reaches review.

---

### 2. FreeAgent and Xero as Read Sources

MA Associates uses both FreeAgent and Xero across their client base (confirmed 15 Sep 2026).
In Phase 2, Bridgit can pull invoices and contacts directly from both via their
read-only APIs. This removes the need to upload documents manually for clients
already on these platforms.

Where FreeAgent data is available, it is used in exactly the same invoice-matching
pipeline as uploaded documents. The accountant does not need to do anything different —
Bridgit handles the pull in the background when the job starts.

> **Important:** FreeAgent's API is read-only. Bridgit cannot submit returns or file
> anything via FreeAgent. Submission pathways are Phase 3.

This item may be pulled forward into late Phase 1 depending on progress.

---

### 3. Nylon Integration for UK Tax Edge Cases

MA Associates already holds a Nylon subscription. Nylon is a UK tax and law research
platform with access to HMRC case law, legislation, and allowable expense rulings.

In Phase 2, Bridgit can call Nylon before deciding to flag a transaction. When a
transaction hits a genuine UK tax ambiguity — not the common cases (those are already
handled by the firm rules and HMRC category list from Phase 1) — Bridgit queries Nylon,
gets a referenced answer, and either resolves the categorisation with that context or
frames the exception question to include Nylon's reasoning.

**Result:** the exception list gets shorter. Bridgit resolves more edge cases itself,
and the questions it does ask are better framed with the relevant HMRC reference
already included.

---

### 4. Client Memory Compounds

Every correction and exception answer from Phase 1 has been building each client's
mapping database. By Phase 2, clients who went through Phase 1 already have a
real knowledge base. Recurring suppliers are mapped. Known patterns are rules.

Phase 2 hardens the correction-to-rule workflow:
- Accountant answers an exception question
- Bridgit proposes: "Save this as a standing rule for this client?"
- Senior accountant approves the rule — it applies to every future job for that client
  automatically
- Nothing becomes a permanent rule without human sign-off

The system measurably improves job over job. This is not a promise — it is a natural
consequence of the mapping database growing with each approved answer.

---

### 5. Always-On Monitoring

Phase 1 Bridgit runs when asked. Phase 2 Bridgit also watches in the background.

**What it monitors:**
- **Approaching deadlines** — VAT quarters, year-end filing dates, personal tax
  deadlines. Bridgit sends an alert when a deadline is approaching and no job has been
  started for that client yet.
- **Missing documents** — when a job is in progress, Bridgit tracks which bank lines
  have no matching invoice and surfaces the list before the accountant even asks.
- **Stale jobs** — a job that has been in "Needs your input" for more than a defined
  number of days triggers a nudge to the right person.

This uses the same email (Resend) and in-app notification infrastructure built in
Phase 1. No new notification system.

---

### 6. Output Matures

Phase 2 output goes beyond Phase 1's categorised transaction list and trial balance.
The working file now includes:

- **Prior year comparatives** — current year figures alongside last year's for the same
  accounts, pulled from the prior year file
- **Net and VAT verified per line** — each line shows whether the invoice confirmed the
  split or whether it was AI-proposed
- **Unmatched transactions clearly separated** — lines with no invoice match are in
  their own section, not mixed into the categorised output
- **Invoice reference logged per line** — for every matched line, the document it was
  matched against is recorded and accessible in the audit trail
- **Output genuinely ready for senior review** — the accountant opens the file and it
  is complete, not a starting point for further document chasing

---

## What Phase 2 Does Not Include

The following remain Phase 3. They are not being deprioritised — they are sequenced
deliberately so Phase 2 is stable before they are added.

- MTD / HMRC submission
- Full accounts preparation pipeline (year-end, VAT returns, personal tax)
- WhatsApp integration
- Per-client history portal
- Multi-agent workflow (Bridgit coordinates with specialist agents)
- General assistant / non-accounting questions

---

## What We Deliver — Phase 2 Shape

Phase 2 is structured in three blocks, not a rigid week-by-week at this stage (those
will be confirmed at the Phase 1 sign-off review):

**Block A — Document pipeline**
Invoice and receipt ingestion, OCR extraction, invoice-to-bank-line matching,
discrepancy flagging, auto-split bulk PDFs, email ingestion, FreeAgent + Xero pull
for eligible clients.

**Block B — Intelligence layer**
Nylon integration for UK tax edge cases, client memory rule approval workflow,
confidence threshold refinement based on Phase 1 real-world data, prior year
comparatives in output.

**Block C — Always-on monitoring**
Deadline alerts, missing document surfacing, stale-job nudges, enhanced notification
templates. Dashboard view showing which clients have approaching deadlines and which
jobs are waiting.

---

## What MA Associates Provides for Phase 2

| What | Why |
|---|---|
| List of clients already on FreeAgent | FreeAgent API setup and connection |
| FreeAgent API credentials (read-only) | Pulling invoices for eligible clients |
| Sample invoice PDFs and scanned receipts | Testing OCR extraction quality |
| Nylon API access details | Integration setup (MA already has a subscription) |
| Agreed threshold for "stale job" nudge | How many days before Bridgit chases |
| Approval: which rules become standing rules | Senior accountant sign-off workflow |

---

## Definition of Done — Phase 2

Phase 2 is complete when:

- [ ] Invoice matched to bank line end-to-end: PDF in → net/VAT extracted → matched →
      Excel output shows confirmed split
- [ ] FreeAgent pull working for at least one live client (read-only)
- [ ] Nylon query fires on a real edge-case transaction and the result informs the
      exception question
- [ ] Client memory rule approval workflow working: answer → propose rule → senior
      approves → rule active on next job
- [ ] At least one deadline alert fired and delivered correctly (email + in-app)
- [ ] Missing document list surfaced before accountant asked for it
- [ ] Prior year comparatives in the Excel output
- [ ] Faraz and Qasim complete an end-to-end walkthrough of a Phase 2 job and sign off
