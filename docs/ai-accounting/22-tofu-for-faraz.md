# 22. Our Take on Tofu — Summary for Faraz

> **Who this is for:** Faraz / Qasim and anyone at MA Associates who wants to understand
> how Tofu fits into (or doesn't fit into) the Bridgit project.
> **Written:** 15 Sep 2026

---

## What we looked at

We reviewed Tofu (gotofu.com) — its website, feature list, integrations, pricing model,
and security posture. Faraz shared a screenshot from the trial (document upload screen).

---

## What Tofu does well

Tofu is genuinely impressive at one specific job:

> **Take a document (invoice, receipt, bank statement PDF) → extract every line item
> from it → code it against your chart of accounts → post it to Xero or QBO.**

It has done this at real scale (1.33M documents, 5,000+ companies, Xero Practice App
of the Year). The UX is clean. Key features worth noting:

- **PDF bank statement extraction** — any format, any bank, any country.
- **Click-to-verify** — click any extracted value and it zooms straight to where it
  came from in the source document. This is a great trust feature.
- **Duplicate detection** — flags before posting, never silently posts twice.
- **Auto-split bulk PDFs** — clients dump a mixed pack of invoices and statements;
  Tofu splits and processes each one.
- **WhatsApp receipt ingestion** — clients photograph receipts and send via WhatsApp.
  Tofu picks them up automatically.
- **Self-learning** — learns from how you've coded things before. Same logic as
  Bridgit's mapping database.

---

## Where Tofu stops

**Tofu's job is extract → code → post to accounting software. That's where it ends.**

It does not:
- Build a trial balance or check that it balances
- Run a bank reconciliation as a hard gate
- Produce MA's Excel working file template
- Understand HMRC VAT rules at your firm's level
- Prepare year-end accounts, VAT returns, or personal tax
- Connect to MA's WIP board or job management
- Know which staff member is working on which client
- Produce the kind of final output your team takes to sign-off

**Tofu feeds documents into a pipeline. Bridgit IS the full pipeline.**

---

## What this means for Bridgit

**Tofu is not a threat to Bridgit. It is a quality reference and a potential component.**

Specifically:

**Reference (now):**
Tofu sets the bar for what "good" looks like on document extraction and exception
review. The click-to-verify feature, the quality of its duplicate detection, the
WhatsApp integration — these are what Faraz now expects. Bridgit will match or beat
these on every feature it includes. If anything Faraz sees in the Tofu trial stands
out as impressive, send it over — that becomes the target for that feature.

**Potential integration (later):**
Tofu already integrates with FreeAgent. If some MA clients already push documents
through Tofu into FreeAgent, Bridgit could pick up from there rather than re-extracting
the same documents. We'd be pulling Tofu's already-processed output, not competing
with it. Whether this makes sense depends on whether Tofu has a public API — we'll
check during the trial.

---

## What we are taking from Tofu into Bridgit

These were already planned but Tofu confirms they are non-optional:

**Phase 1 (Week 1):**
- Proper PDF bank statement parser — the Koliqi & Sons Starling statements are PDFs.
  Bridgit must handle them natively, not just CSV.
- Every transaction in the exception table links back to the exact page of the source
  document where the AI read it. Same as Tofu's click-to-verify.
- Duplicate detection runs before categorisation. Always.

**Phase 2:**
- Auto-split bulk PDFs — when clients dump mixed packs, we split before processing.
- Email ingestion — clients email invoices to MA; Bridgit reads the inbox automatically.
  (Originally Phase 3 — moved up because Tofu confirms the value.)

**Phase 3 (early):**
- WhatsApp integration — moved up to early Phase 3. Tofu already has it; it's a
  competitive baseline now, not a future nice-to-have.

---

## What we are NOT taking from Tofu

- Xero / QBO direct posting — Bridgit outputs to MA's Excel working file first.
  Xero is a read source for client data in Phase 3, not the destination.
- 200+ language translation — not relevant for a UK ACCA practice.
- AutoCount / Bukku / MYOB / Sage integrations — not MA's stack.

---

## One-line summary

Tofu does one part of the job better than anything else on the market.
Bridgit does the whole job — with Tofu as a possible input, not a competitor.

---

## Questions still open from the trial

1. Does Tofu have a public API? (Check in trial dashboard → could become Phase 2 document extraction layer.)
2. What features does Faraz rate most highly? Screenshots and specific moments — those set the UX bar for Bridgit's exception table.
3. Which MA clients are on FreeAgent vs Xero? (This determines Phase 2 and 3 integration priority.)
