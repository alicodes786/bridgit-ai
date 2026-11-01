# 8. Decisions Log

A running record of every real decision made on this project, so nobody has to
re-litigate something already settled, and so anyone joining later can see exactly what
was decided and why.

---

### Decision 1 — Orchestration engine
**Decided:** Custom Postgres-backed state machine. No LangGraph.
**Date:** confirmed in this conversation, 17 Aug 2026.
**Why:** the accounting workflow (per the client's flowchart) is a linear pipeline with
binary branches, not a case requiring free agent negotiation. A `current_stage` column
plus an explicit transitions table on infrastructure the team already owns (Postgres)
delivers the persistence and pause/resume behaviour needed without adopting a second
framework. See [02-architecture.md](./02-architecture.md) §2.4 and
[03-review-of-gpt-plan.md](./03-review-of-gpt-plan.md) §3.2.
**Status:** final for POC and MVP. Revisit only if a concrete limitation is hit that
the custom implementation can't reasonably solve.

### Decision 2 — POC/MVP UI location and quality bar
**Decided:** the AI Accountant entry point lives inside the real MA dashboard from day
one of the POC, and must be built to a genuinely professional/production-quality
standard — not a bare internal tool, not a placeholder UI.
**Date:** confirmed in this conversation, 17 Aug 2026.
**Why:** perception matters for continued buy-in on a project like this, and the
existing MA app already has a solid component library (Tailwind + Radix/shadcn + an
established MA theme) to build on, so "professional" doesn't require a from-scratch
design effort.
**Trade-off accepted:** Phase 1 (POC) timeline moved from an original 4–6 week estimate
to 5–7 weeks to account for the real frontend work this requires. See
[04-roadmap-and-deliverables.md](./04-roadmap-and-deliverables.md) Phase 1.
**Status:** final.

### Decision 3 — Historical data availability
**Decided:** multiple real historical job data sources are available, via Qasim and
Faraz (MA Associates' owners), reachable through an existing WhatsApp group.
**Date:** confirmed in this conversation, 17 Aug 2026.
**Why it matters:** this was flagged as the single biggest schedule risk in
[04-roadmap-and-deliverables.md](./04-roadmap-and-deliverables.md) Phase 0. Confirmed
access materially de-risks the timeline, provided the actual data (not just access to
the people) starts flowing promptly.
**Next action:** send the request in
[09-data-request-for-ma.md](./09-data-request-for-ma.md) as soon as possible — access
to the people isn't the same as having the data in hand yet.
**Status:** channel confirmed; data itself still pending as of this log entry.

### Decision 4 — Agent backend hosting
**Decided:** Railway, for the POC agent backend service (FastAPI).
**Date:** confirmed in this conversation, 17 Aug 2026 (recommended, not pushed back on).
**Why:** fastest path to a live, demo-ready service; doesn't cold-start awkwardly
mid-demo; cheap at this stage (~$5–20/month); no meaningful lock-in if a move is needed
later. See [05-hosting-and-tech-stack.md](./05-hosting-and-tech-stack.md) §5.0.1.
**Status:** final for POC. Revisit for MVP/Production once real usage/security
requirements are known (see [05-hosting-and-tech-stack.md](./05-hosting-and-tech-stack.md) §5.3).

### Decision 5 — Self-hosted LLM vs. API providers
**Decided:** use API providers (OpenAI, Anthropic) — do not self-host an open-weight
model.
**Date:** confirmed in this conversation, 17 Aug 2026.
**Why:** open-weight self-hosted models currently lag frontier proprietary models on
the complex judgement/reasoning tasks this project depends on; self-hosting costs real
money 24/7 (GPU reservation) versus tens of dollars total for API use at current
volume; running inference infrastructure reliably is a specialized ongoing job that
competes with time better spent on the accounting agent itself; and the main reason
firms consider self-hosting — data privacy — is already addressed by enterprise API
tiers with zero data retention and no training on customer data. See
[05-hosting-and-tech-stack.md](./05-hosting-and-tech-stack.md) §5.4.1.
**Status:** final for POC/MVP/Production. Revisit only if sustained high volume flips
the cost math, or a specific compliance mandate arises that enterprise API tiers (or
Azure OpenAI/AWS Bedrock/Google Vertex as a middle ground) can't satisfy. Self-hosting
remains a later vision (client meeting Aug 2026), not Phase 1.

### Decision 6 — Phase 1 delivery: weekly scorecards, proof before polish
**Decided:** Phase 1 is bank statements → trial balance only. Weekly sprint
scorecards against a real historical job. The engine and scorecard come first;
the polished AI Accountant UI inside MA follows once numbers exist. OneDrive
drop-zone pipeline must work before Phase 1 is declared started.
**Date:** client meeting, ~24 Aug 2026.
**Why:** client will not sit through weeks of silence; they also will not accept
"stuck in Phase 1 forever" without a written pass/fail bar. Emails, handwritten
notes, and unnamed receipts are out of Phase 1 (Qasim).
**Trade-off accepted:** sequences Decision 2 (UI still in the real MA app, not
before the first real scorecard).
**Status:** final for Phase 1 scope. Categorisation logic itself stays open until
solid — see Decision 7.

### Decision 7 — Categorisation chain (working, not frozen)
**Decided:** Phase 1 chain is prior mapping → firm rule → LLM (with a specific
question when unsure) → exception queue. Nylon is **not** in Phase 1; it is an
optional Phase 2 fallback between LLM and the queue if a developer API exists.
**Date:** post-meeting design, 24 Aug 2026.
**Why:** the Emirates / personal-vs-business example is real, but Phase 1 solves
it by asking, not by blocking on Nylon. Keep tightening this chain until
scorecards are acceptable.
**Status:** working design. Not closed.

### Decision 8 — FreeAgent and MTD timing
**Decided:** FreeAgent is not Phase 1. Plan it for Phase 2 as an optional invoice
data source. MTD (VAT and personal tax talking to MTD-enabled software) is a
named Phase 3 requirement, not an afterthought.
**Date:** client meeting, ~24 Aug 2026.
**Status:** final for phasing. API access still to confirm.

### Decision 9 — Agent name and drop-zone folder convention
**Decided:** not yet. S FA (Faraz) to propose agent name and OneDrive folder naming.
**Date:** raised 24 Aug 2026.
**Status:** open.

### Decision 10 — Phase 1 reframed: learning phase, not a kill-gate
**Decided:** Phase 1 is a sandbox-testing / learning phase. The project has
started at Phase 1, not paused pending its verdict. Weak early results tune the
system; they do not end the engagement. Hard software gates (TB balances, bank
rec agrees) are unaffected — those remain binary checks regardless of framing.
**Date:** follow-up client meeting, 23 Aug 2026 (Mirza, Qasim/Cass, Faraz "S FA").
**Why:** Mirza's own words: "it's not like, oh, it's not working, phase one is
gone, finished, we're not going ahead with the project." This is also more
honest — a real-world categorisation engine improves with tuning across weeks,
it does not resolve in a single pass/fail run. The prior "if Phase 1 doesn't
work, we stop" framing (Decision 6 note) was too binary and should not be used
verbatim in client-facing material going forward.
**Trade-off accepted:** softens the urgency framing used earlier with the
client; must be replaced with a concrete number (90%+, see Decision 11) so it
doesn't drift into "no accountability."
**Status:** final. Supersedes the stop/fail framing in Decision 6 — Decision 6's
scope and pipeline pre-condition still stand, only the "stop if it fails" tone
changes.

### Decision 11 — Accuracy target: 90%+
**Decided:** target 90%+ transaction categorisation accuracy before the AI's
output is relied on without full human re-checking. A per-transaction rating/
scoring process runs from the early weeks specifically to measure this.
**Date:** 23 Aug 2026 meeting.
**Why:** concrete, communicable number; matches what Mirza proposed and the
client did not push back on. Also grounded by Qasim's own assessment that most
transactions fall into a well-defined HMRC allowable-expense list, so the AI is
not starting from a genuinely hard problem for the common case.
**Status:** final as a target; actual measured accuracy still pending real data.

### Decision 12 — MTD/FreeAgent: read-only API confirmed, submission method open
**Decided:** the FreeAgent API is read-only. It cannot be used for MTD
submission. The submission approach (most likely a computer-use style
automation operating the FreeAgent software directly) is an open technical R&D
item, to be tested before Phase 3 MTD scope is locked in. Do not assume an API
integration will cover submission.
**Date:** 23 Aug 2026 meeting.
**Why:** all MTD work happens inside FreeAgent's own interface with no Excel
step; a read-only pull into a spreadsheet adds work rather than removing it.
**Status:** final on the read-only fact. Submission method: open, needs a
spike.

### Decision 13 — Assistant scope: accounting-only vs general-purpose
**Decided:** not yet. Options: (a) restrict the assistant to accounting-related
queries only via prompt + knowledge-base guardrails, or (b) allow it to answer
general questions like a normal chatbot. Cost/speed impact is negligible either
way — this is a product decision, not an engineering constraint.
**Date:** raised 23 Aug 2026 by Faraz (S FA).
**Owner:** Faraz to decide and confirm.
**Status:** open.

### Decision 14 — Continuity plan: three concrete scenarios
**Decided:** (1) if Mirza is unavailable long-term, MA gets full access to code,
Railway, and infrastructure to migrate/hire another developer; (2) if
responsibility moves from Faraz to Qasim/Cass, Mirza's team runs a formal
knowledge-transfer session; (3) if the project continues but needs occasional
support, a named developer from Mirza's team (not only Mirza personally) is the
point of contact.
**Date:** 23 Aug 2026 meeting.
**Why:** client explicitly raised this as a real risk given the scale of
investment and that usage will span multiple people/offices (Pakistan, Dubai,
London) around the clock.
**Status:** final in principle; needs to be written into the contract in this
exact form.

### Decision 15 — NDA and SOP walkthrough call before deep data sharing
**Decided:** send an NDA before MA shares sensitive job data. In addition to
document handover, do a dedicated call with Qasim (Cass) walking through one
real job step by step (comparatives, opening balances, bank analysis, sales
invoice listing) — the actual SOP, not just the general flowchart, since real
jobs deviate client-by-client (missing invoices, need for estimates).
**Date:** 23 Aug 2026 meeting.
**Status:** final. Action pending on both sides.

### Decision 16 — Data protection: Data Centre in MA, ZDR on APIs, no extra vector DB
**Decided:** (1) All AI-held data lives in the existing MA Supabase project
(`pgvector` in the same Postgres, Storage for files). No separate vector database.
(2) MA staff control what stays via a **Data Centre** page inside the MA
dashboard, not by handing out the Supabase admin console. (3) LLM calls go through
Anthropic and OpenAI **business APIs** with zero-data-retention enabled; consumer
chat apps are not used for client jobs. (4) Proposed retention: raw files deletable
30 days after sign-off (Faraz to confirm period); approved mappings and audit
trail kept. (5) MFA on Supabase; developer production access is not standing.
(6) NDA + DPA in the contract; local/email copies of client files deleted when
that piece of work is done.
**Date:** client meetings 23–24 Aug 2026; design locked as Point 2, 25 Aug 2026.
**Why:** ACCA / GDPR / ICO. Faraz asked for this in writing in the proposal and
the contract, plus a way for MA to delete data themselves.
**Trade-off accepted:** Data Centre is in Phase 1 UI, not deferred. Auto-purge of
raw files after N days can wait until Phase 2 if manual delete is live.
**Status:** proposed ideas for MA to pick, not committed Phase 1 scope. Client-facing
wording in [proposal.html](./proposal.html) is framed as ideas to agree, not a locked
spec. Working file-flow (OneDrive drop zone → existing MA Supabase) is the baseline.
Data Centre UI, ZDR-in-contract, 30-day auto-delete, and DPA wording land only if
Faraz/Qasim say yes.

### Decision 17 — Workflow/UI design (Point 3)
**Decided:** (1) Chat and exception review are separate UI surfaces — chat starts
jobs and answers ad-hoc questions, exceptions live in a structured review table.
(2) Job status is a fixed five-state lifecycle: Queued → Processing → Needs your
input → Ready for review → Approved. (3) Notifications go both by email (existing
Resend infra) and in-app badge when a job needs input or is ready. (4) Default
output is MA's Excel template plus a one-page PDF summary, both downloadable and
stored in `ai_documents`. (5) The per-client AI job history ("portal") stays Phase
3, built as the same job-list UI scoped and kept historically, not a new system.
(6) Real screenshots are owed before the layout is treated as final — Faraz
explicitly wants to see it in use before judging it.
**Date:** discussed 23 Aug 2026 meeting; confirmed with Mirza 25 Aug 2026.
**Why:** matches Faraz's own walkthrough of the scenario he wants (start a job,
know it's running, know where the result lands), and avoids mixing two different
UI needs (starting work vs. reviewing a large exception list) into one chat feed.
**Status:** final for design. Screenshots and the real exception-table UI are
still an execution task, not a design gap.

### Decision 18 — Anthropic only for Phase 1; OpenAI not required
**Decided:** Skip OpenAI for Phase 1. Bridgit calls Anthropic (Claude) as the primary model. Keep a provider abstraction so OpenAI or another API can be added later without rewriting the engine.
**Date:** 14 Sep 2026
**Why:** Faraz's 5 in-house accounts were done on Claude. Matching that success means using the same class of model first. A second vendor was only for benchmarking, not a start-gate. Paying for two frontier APIs before the first bank file is processed is unnecessary.
**Trade-off accepted:** No A/B between GPT and Claude on the golden job until we add a second provider. Fine for Week 1.
**Status:** final for Phase 1. Revisit if cost, availability, or a failed Claude run justifies a second model.

### Decision 19 — Do not start Week 1 on a cheap small model
**Decided:** Do not swap Claude for DigitalOcean / ultra-cheap-per-token models for the first real client jobs. Cost-optimise later (Haiku for easy lines, cheaper models for non-judgement tasks) after an internal Excel exists and accuracy is known.
**Date:** 14 Sep 2026
**Why:** Those 5 accounts worked because of a frontier LLM with fat context. A $0.0002/million-token class model will not mimic that. The plan already uses the LLM generously for judgement; starving quality to save pennies on Week 1 volume is the wrong trade.
**Trade-off accepted:** Higher token cost on early jobs. Volume is small (one client file).
**Status:** final until Week 1 internal score exists.

### Decision 20 — Anthropic ZDR is a sales request, not a toggle
**Decided:** Zero data retention on Anthropic is requested from Anthropic sales / account team, per organisation. There is no self-serve "turn on ZDR" switch. Check Console → Settings → Privacy Controls → Data retention period after they enable it. Until then, commercial API terms still say customer data is not used for training without permission; that is not the same as ZDR. Do not put real MA client files through the API until ZDR is confirmed, or MA explicitly accepts the default commercial retention in writing.
**Date:** 14 Sep 2026
**Why:** Matches what we told Faraz. Docs: https://platform.claude.com/docs/en/manage-claude/api-and-data-retention
**Status:** **confirmed live 17 Sep 2026.** Anthropic told Mirza ZDR is on for the org. Real client files may go through the Bridgit API / Claude. LLM step in the categorisation chain is unblocked.

### Decision 21 — Tofu is a reference and future integration, not a replacement
**Decided:** Faraz is studying Tofu to extract ideas and feed them into Bridgit (reference),
and is also exploring Tofu as a potential integration layer for invoice/document extraction
in later phases. He is NOT proposing to switch away from building Bridgit, and he is NOT
proposing to use Tofu instead of Bridgit. Bridgit remains the full accounting pipeline.
**Date:** 15 Sep 2026
**Why:** Confirmed by Faraz directly (session notes 15 Sep). Tofu does extract → code → post to
Xero/QBO. It does not do: trial balance, bank rec, MA's Excel template, HMRC pipeline, or MA's
WIP board integration. The two systems serve different scopes.
**What changes:** Faraz will continue trialling Tofu and feeding specific UX/feature notes
back (e.g. what the click-to-verify feels like in practice). Those become input to Bridgit's
exception table UX and document extraction quality bar.
**Status:** final. Document any future integration ideas in Phase 2 planning when MA confirms
Tofu API availability.

### Decision 22 — WhatsApp moved to early Phase 3
**Decided:** WhatsApp client integration is prioritised as early Phase 3 Block A, not late Phase 3.
**Date:** 15 Sep 2026
**Why:** Tofu already has WhatsApp receipt ingestion and it is a competitive feature expectation
for UK accounting firms. Faraz has seen it in a live product. It is no longer a future idea.
**Trade-off accepted:** Other Phase 3 features may shift out slightly.
**Status:** final.

### Decision 23 — Xero confirmed used by MA Associates; read source moves to Phase 3 Block A
**Decided:** MA Associates uses Xero for some clients (confirmed 15 Sep 2026). Xero as a
read-only data source is moved from "optional" to "planned, Phase 3 Block A" — same pipeline
as FreeAgent in Phase 2. Implementation behind the existing `get_supporting_documents()` interface.
**Date:** 15 Sep 2026
**Why:** Previously unknown whether MA had Xero clients. Now confirmed. Tofu's integration list
also confirms Xero is the dominant platform for the client base in question.
**Trade-off accepted:** None — this is an additive change, no scope removed.
**Status:** final.

### Decision 24 — Bank ingest is format-detecting, not Starling-only
**Decided:** Bridgit is not a Starling-only parser. All bank files go through one ingest entry that emits the same canonical row (`date, description, amount, debit/credit, source_page`). PDF: try UK current-account layout (DATE / TYPE / IN / OUT — first proven on Koliqi Starling PDFs), then tables, then dated text. CSV/Excel: detect columns by aliases (Lloyds/Barclays/HSBC/NatWest exports). Add a new PDF layout when MA sends a bank that fails the generic path — do not rewrite categorisation or Excel.
**Date:** 17 Sep 2026
**Why:** First client files happen to be Starling PDFs. The plan always also required CSV/Excel for multiple banks (`13-scope-phase1.md` Week 1, `17-build-plan.md` Day 3–5). "Starling first" meant first test files, not the product scope.
**Trade-off accepted:** Unknown bank PDFs may need a layout tweak; CSV/Excel covers most UK exports immediately.
**Status:** final.

### Decision 25 — Client rules vs job-type rules are separate records
**Decided:** Bridgit stores **three** layers, never collapsed into one mapping table:
(1) **job-type rules** (how any VAT job / any year-end / any CIS job is done),
(2) **client rules** (this company's formatting, expense application, this-year
instructions such as director rem NIL), (3) **client mappings** (this payee → this
column/account for this client). Faraz (26 Sep): the only way to handle
“certain clients have certain performers, formatting, rules, application of
expenses” is a record **on that client**.
**Date:** 26 Sep 2026
**Why:** Hit Hunters codes by payee and ignores the CSV Category column; Koliqi VAT
uses different tabs and VAT codes. A firm-wide “Gocardless = web hosting” rule would
be wrong. A forever “director rem = £9,600” mapping would also be wrong — that is a
this-year client instruction (same class as capitalise vs expense). Architecture
already described `client_memory` vs `firm_rules` in
[02-architecture.md](./02-architecture.md) §2.7; `ai_mappings` only covers layer (3)
today. Layers (1) and (2) must become first-class, proposed→approved, like mappings.
**Trade-off accepted:** slightly more schema and intake (job type + client) before
processing. Cost of not doing it: one client's year-end columns leak into another
client's VAT file.
**Status:** final. Implementation starts with Hit Hunters as the first client-rules
seed. Detail: [29-sep26-hithunters-and-job-catalog.md](./29-sep26-hithunters-and-job-catalog.md).

### Decision 26 — Official job-type catalog and top 5
**Decided:** Faraz's list is the catalog Bridgit will eventually cover, **not from
day one**. Build towards the **top 5 in this order:** (1) Company Accounts
(statutory year-end), (2) VAT Returns, (3) Property Lettings, (4) Sole Trader /
Self Employed, (5) CIS. Full list and out-of-engine items (formation, dormant,
dissolving, registered address, HMRC investigations) live in
[27-job-types-catalog.md](./27-job-types-catalog.md).
**Date:** 26 Sep 2026
**Why:** 19 Sep call ranking was informal (company accounts, self-assessment, VAT,
CIS). Faraz later sent a cleaner list with property lettings at #3 and employed
self-assessment *off* the top 5. Use the written catalog so training jobs are not
chosen ad hoc.
**Trade-off accepted:** we already started on VAT (Koliqi) because that pack arrived
first. Keep Koliqi as the live VAT track. **Do not throw it away.** Next *new*
training pack is company accounts (Hit Hunters), which is now #1 in the catalog
and actually in hand.
**Status:** final.

### Decision 27 — Hit Hunters is the first company-accounts training job
**Decided:** Train Bridgit on Hit Hunters Ltd year ended 28 Feb 2026 using the
comparative file + 2026 CSV + completed 2026 file + Faraz's process log. **Bank
analysis first** (process-log Phase 1). ETB / P&L / balance sheet (process-log
Phase 2) only after bank tabs tie internally. Faraz does not need to re-run the
job in Claude to extract prompts — the process log is that extract. Bridgit is
not yet the live tool for his next year-end; this pack is the teach-in.
**Date:** 26 Sep 2026
**Why:** Complete year-end with comparative *and* answer key *and* SOP. Faraz:
“this is what I'd like to have done on Bridgit directly. Then it learns and
remembers.” Matches Week 3 “second historical job” in
[17-build-plan.md](./17-build-plan.md), which is no longer optional/waiting.
**Trade-off accepted:** VAT box-total work and the May VAT blind job drop behind
this in the queue (not cancelled). Full statutory finalisation is still a larger
chunk than VAT boxes — do not collapse them.
**Status:** final. File pack: [28-client-files-hithunters.md](./28-client-files-hithunters.md).

### Decision 28 — SharePoint Graph bridge (read-only, Man Tax) then Azure
**Decided:** MA files live in **SharePoint** (not personal OneDrive). Joseph
(Zenas) will expose a **pull-based Microsoft Graph bridge**: Entra app
registration + **client certificate**, IP-restricted, **read-only**, first
against a **copy of the Man Tax** library (lowest risk). Bridgit stays on
**Railway + Supabase** for that proof of concept. **Do not copy libraries
outside the Microsoft tenant.** After the workflow works: optional move of
Bridgit onto an **Azure Linux VM** (~2 vCPU / 4 GB / ~$30/month) in MA’s
tenant, then **managed identity** instead of cert secrets. Write-back and
Power Automate mirroring are **after** read PoC. Azure OpenAI vs Anthropic
is research only. Client WhatsApp is still later. Other MA products (e.g. CV)
may share the VM **after** Bridgit PoC — Faraz is open, not a Bridgit blocker.
**Date:** ~10 Oct 2026 call (Joseph, Faraz, Ali). Notes:
[33-joseph-call-notes.md](./33-joseph-call-notes.md).
**Why:** Joseph will not implement Bridgit; he will open Microsoft securely.
PoC-before-Azure matches how Bridgit was already being built. Man Tax first
limits blast radius versus the live MA staff folder.
**Trade-off accepted:** OneDrive-as-start-gate stays **not** blocking the
engine (Decision 6 / 14 Sep). The bridge is how we stop asking Faraz for
files — it is not a rewrite of categorisation.
**Status:** final for sequence. Secrets and site URLs still incoming from Joseph.

### Decision 29 — Late uploads on the chat bar, same kinds as New job
**Decided:** After a job exists, Faraz can attach files from Chat (paperclip /
drop) or Cards (Add files). Bridgit classifies **bank** / **comparative** /
**supporting** the same way as the first upload. Bank or last-year Excel
**re-runs process**. Extra papers are stored on the job and are **not OCR'd**
in this phase (re-process would wipe open answers).
**Date:** 25 Oct 2026.
**Why:** Claude/GPT let you drop a file mid-thread. New job was the only
upload door; missing last-year Excel or a replacement bank CSV should not
force a second job.
**Trade-off accepted:** Supporting PDFs still do not post into Sales/Purchase
tabs. Latest bank / comparative wins; unique storage paths so Excel download
is not a stale upsert.
**Status:** final for Phase 1 working file. Notes:
[36-oct25-session.md](./36-oct25-session.md).

### Decision 31 — Normal conversation about the work, not only inside a job
**Decided:** Bridgit talks like Claude about the bookkeeping work. The team is
**not** limited to a script, and **not** limited to having a job open. Home is a
desk conversation across clients and jobs. Inside a job, the same natural talk
stays grounded on that job and can still code a line when that is the intent.
Export is a transcript download. No invented figures.
**Date:** 1 Nov 2026.
**Why:** `/app` should feel like a proper SaaS agent, not only a form with a
chat box for “Motor vs Phone”. Accountants will ask “where are we?” and want
something they can paste into a file note or email.
**Trade-off accepted:** Grounding rules stay strict (no fake rec numbers, no
Accept on live client jobs for Ali). Export is a product surface, not a substitute
for the working Excel. RAG / SharePoint context comes later; Phase 1 export is
job + mappings + chat already in Supabase.
**Status:** provisional — document and design next; partial grounding exists in
`engine/chat.py` today. Live demo pack: [37-live-demo-northbridge.md](./37-live-demo-northbridge.md).

### Decision 32 — Supporting papers (.txt, notes) on New job and clearer intake
**Decided:** **Next build.** New job and Chat must accept **plain text and other
supporting papers** (e.g. Meridian insurance `.txt`) alongside PDF/images, with
copy that explains they are **stored on the job** but **not OCR'd** in Phase 1.
Today the New job drop zone was CSV/Excel-heavy; Chat already allowed `.txt` in
the file picker but UX did not make that obvious.
**Date:** 1 Nov 2026.
**Why:** Live trial: insurance note could not be uploaded on New job; accountants
will attach memos, emails saved as .txt, and scans later.
**Trade-off accepted:** No automatic posting from supporting docs until a later
phase; classify + store + list in chat is enough for now.
**Status:** provisional — `.txt` added to New job accept list; full product
surface (list on job, “what papers do we have?”) still to polish.

### Decision 33 — Visible “working file updated” feedback
**Decided:** **Next polish (partial now).** Whenever Bridgit **rebuilds the working
Excel/PDF** (after each answer, after process, after bank re-upload), the UI must
tell the user: toast and/or inline **“Working file updated”** with last-updated
time — not silent background refresh.
**Date:** 1 Nov 2026.
**Why:** Faraz needs confidence the download reflects the latest answers; feels
like a proper agent updating deliverables.
**Status:** provisional — toasts + timestamp on job header in `/app`; extend if
we move Excel refresh async later.

### Decision 34 — “Test” label on dummy jobs/clients
**Decided:** Jobs whose **title or client name** contains `test` or `demo`
(case-insensitive) show a **Test** badge in the sidebar and on the job header.
Real client names stay unlabelled.
**Date:** 1 Nov 2026.
**Status:** final for `/app` trial UI.

---

## Template for future decisions

When a new decision gets made, add an entry here in this format:

```
### Decision N — <short title>
**Decided:** <the actual decision>
**Date:** <date>
**Why:** <reasoning>
**Trade-off accepted (if any):** <what this costs>
**Status:** <final / provisional / revisit when X>
```
