# 21. Tofu Analysis — 15 Sep 2026

> **Context:** Faraz shared gotofu.com and has started a trial. Meeting called to assess
> overlap with Bridgit and decide what changes. Analysis below.
> Decisions that come out of this belong in [08-decisions-log.md](./08-decisions-log.md).

---

## What Tofu is

AI bookkeeping SaaS. Core loop:
**Upload invoice / receipt / bank PDF → AI extracts every line item → codes against chart of accounts → posts to Xero / QBO / others.**

Scale: 5,000+ companies, 50+ countries, 1.33M documents processed, $5.7B in value.
Awards: Xero Practice App of the Year Asia 2026, UK + South Africa finalist.

Competitors they position against: AutoEntry, Dext, Hubdoc (legacy OCR tools).

---

## Full feature list (from their site, 15 Sep 2026)

- Self-learning AI (zero configuration — learns from historical GL)
- Line item extraction (every line on every invoice)
- AI bank statement extraction (any PDF, any bank, any country)
- Auto-split bulk PDFs
- Click-to-verify with auto-zoom (click extracted value → see source in document)
- Duplicate detection before posting
- AI custom rules in plain English ("tell Tofu your exceptions")
- Email ingestion
- WhatsApp: clients send receipts, Tofu extracts and posts
- SharePoint / Dropbox / Google Drive integrations
- 200+ language translation
- Handwriting recognition
- Xero, QBO, Zoho, AutoCount, Bukku, Dynamics 365, Sage, MYOB, FreeAgent, MoneyForward, freee, Odoo integrations
- CSV exports for 20+ others
- Multi-receipt snippet extraction
- Search and filter past documents

Security: ISO 27001:2022, PCI-DSS SAQ-A, GDPR, AWS Frankfurt, AES-256, TLS 1.2+.
No customer data used to train LLMs. Per-customer knowledge segregated.

Pricing: Flat monthly. No per-user or per-client limits.

---

## Where Tofu stops

**Tofu's pipeline ends at: extract → code → post to accounting software.**

It does NOT do:
- Trial balance assembly or balance check
- Bank reconciliation as a hard gate
- MA's Excel working file template output
- UK-specific ACCA / HMRC VAT treatment at firm level
- Accounts preparation (year-end, comparatives, schedules)
- AI review agent
- Reporting to client
- Embedded inside a custom dashboard
- WIP board / job management integration
- The full pipeline from bookkeeping to final accounts

**Tofu feeds into the pipeline. Bridgit IS the pipeline.**

---

## Honest overlap with Bridgit

Both do:
- Bank statement parsing (PDF → coded transactions)
- Self-learning from historical coding (our `ai_mappings`)
- Exception review with specific questions
- Rules that stick permanently per client

These are things we were building from scratch. Tofu has built them well and at scale. We should learn from their UX and implementation without rebuilding what they've proven.

---

## Does Tofu threaten Bridgit?

**As a direct replacement: No.** MA Associates uses FreeAgent and their own Excel working files — not Xero as the final destination for their workflow. Tofu's core output is posting to Xero/QBO. That is not MA's workflow.

**As a UX reference: Yes** — it sets Faraz's expectation of what "good" looks and feels like on document extraction and exception review.

**As a potential component: Possibly** — Tofu already integrates with FreeAgent. If MA clients send invoices via Tofu → FreeAgent, Bridgit could pick up from there. An integration rather than a competitor.

---

## What Bridgit MUST take from Tofu

### Phase 1 — add now, not later

| Feature | Tofu does it | What Bridgit does |
|---|---|---|
| **PDF bank statement extraction** | Any PDF, any bank | Build Starling PDF parser properly. Non-optional for Week 1 given client files are PDF-only. |
| **Click-to-verify (source linking)** | Click value → zooms to document location | Add `source_page` to `ai_transactions`. Exception table links each line back to the source PDF page. This is a trust feature — Faraz can see exactly where the AI found it. |
| **Duplicate detection** | Before posting | Before categorisation step, check for (date + amount + description) match on this job. Flag, never auto-post. |
| **Exception questions read like plain English** | "Tell Tofu your rules" phrasing | Our exception questions must be specific and natural, not "confidence: 0.42". Already planned but Tofu shows the bar. |

### Phase 2 — Tofu confirms the priority

| Feature | What changes |
|---|---|
| **Line item extraction from invoices/receipts** | Already Phase 2 but Tofu shows the bar for quality. Faraz's trial sets his expectation. |
| **Auto-split bulk PDFs** | Add to Phase 2 — when clients dump mixed packs (invoices + statements), split before parsing. |
| **Email ingestion** | Clients email invoices to MA. Move from Phase 3 to Phase 2. Low complexity relative to value. |

### Phase 3 — WhatsApp moves up in priority

Tofu already has WhatsApp receipt ingestion. We had it as late Phase 3. It should now be **early Phase 3**, not last. Faraz has seen it done. It's a competitive expectation, not a future idea.

---

## What we do NOT need to replicate

- 200+ language translation — UK ACCA firm, not needed
- AutoCount / Bukku / MYOB / Sage integrations — not MA's stack
- Handwriting recognition — not their client base
- Xero direct posting — Tofu can handle this for Xero clients; Bridgit outputs to MA's Excel first

---

## What Faraz's trial means — confirmed 15 Sep 2026

**B) He is studying Tofu to understand what "good" looks like.** Faraz is actively
trialling Tofu and will send specific UX moments, nooks, and features back for Bridgit to match.
Each screenshot or feature he calls out sets the bar for Bridgit's exception table and document UX.

**C) Future integration — also on the table.** Faraz is open to Tofu becoming a document
extraction component in later phases if its API allows. This is not Phase 1 scope — evaluate when
MA confirms Tofu API availability.

(Option A — replace Bridgit with Tofu — is not the direction. Confirmed.)

---

## Confirmed answers — 15 Sep 2026

1. **MA Associates uses Xero** — yes, confirmed. Affects Phase 3 Xero read source (Decision 23).
2. **Tofu's role is reference + potential integration** — Decision 21 logged.
3. **Tofu screenshot from Faraz** — document upload screen (4-step: Organisation → Entities → Integrations → Documents). Confirms drag-and-drop, PDF/images/Word/Excel/HTML/text support, 20MB max.
4. **Tofu public API** — unknown at this stage. Evaluate during trial.

---

## Outstanding from Faraz as trial continues

1. What specific UX moments does he find impressive? Screenshots / feature names.
2. Does Tofu have a public API? (Check in trial dashboard.)
3. FreeAgent: does this change how MA thinks about FreeAgent within Bridgit?

---

## Plan changes — confirmed

- Phase 1 engine: PDF bank statement extraction is Week 1 requirement (non-optional — confirmed client files are PDF-only).
- Phase 1 UI: exception table lines link to source document page (click-to-verify).
- Phase 1 engine: duplicate detection added to categorisation chain.
- Phase 2: auto-split PDFs added.
- Phase 2: email ingestion moved from Phase 3.
- Phase 3: WhatsApp moved to early Phase 3.
- Phase 3: Xero read source confirmed (MA uses Xero).

---

## Decisions logged

- **Decision 21** — Tofu is reference + future integration (08-decisions-log.md)
- **Decision 22** — WhatsApp moves to early Phase 3
- **Decision 23** — Xero confirmed, read source moves to Phase 3 Block A
