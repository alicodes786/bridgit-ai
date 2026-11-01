# 18. Session Notes — 14 Sep 2026

Capture of decisions, client messages, and open reminders from this session.
Come back to each **TODO** before starting the next day's build.

---

## Client conversation — Faraz using Claude directly

**What he said (verbatim):**
> "Yeh Ali ive done like 5 accounts on claude. For in house companies.
> And its getting better and smarter. Can you get this to a stage where we are
> engaging with the agent. And then we teach it as we go along. So instead of
> using claude we can start with this straight away."

### Implications

**Does this change the build plan? No.** It validates it. He's hitting the exact
ceiling Bridgit was designed to break through:

| Claude (consumer) | Bridgit |
|---|---|
| Starts from scratch every session | Permanent per-client mappings |
| He re-teaches chart of accounts each time | Loaded once, used forever |
| No hard TB / bank rec gates | Code enforces both before review |
| Conversation → he copies to Excel manually | Writes MA's actual Excel template |
| No audit trail | Every decision logged with reason |
| No exception table | Structured table, separate from chat |
| No job status | Five-state lifecycle |

**Same models underneath.** Bridgit calls Claude / GPT APIs exactly like
claude.ai does. Intelligence is identical. Everything else is what's different.

### GDPR flag — raise this with Faraz carefully

He's been processing real client bank statements through **claude.ai** (consumer
product). That is **not** zero-data-retention. MA is an ACCA firm — client
financial data through a consumer chat app is an ICO / GDPR risk right now, today.

**How to frame it (not a scare, a sell):**
> "The reason we're building this properly is so you don't have to do what you're
> doing now, which carries real data risk. Bridgit uses the same models but
> through business APIs with zero data retention — your client data never trains
> anyone else's model."

**TODO — come back to client files** after `/health` is green.
See [20-client-files-koliqi.md](./20-client-files-koliqi.md). Put files in `data/client/koliqi-sons/` only — not in this chat.

---

## TODO — Week 1 interactive adjustment

Faraz's message ("engage with the agent, teach it as we go") tells us the
interactive experience matters earlier than Week 4 in the current plan.

**Proposed tweak (don't change the engine-first rule, just surface it earlier):**

Week 1 target adds:
- Upload a bank file → see categorised rows in a simple table
- See exceptions with specific questions → answer them on-screen
- Download the Excel

That IS the "teach it as you go" loop. Every exception answered becomes a
permanent mapping. No pretty dashboard needed — even a raw table in Week 1
will feel better than Claude because it remembered last year and wrote the Excel.

**TODO — come back and update `17-build-plan.md` Week 1 section to reflect
this before building the Week 1 engine.** **Done 18 Sep** — exception cards are on the FastAPI board (`localhost:8000`). Next.js remains the Faraz product UI later.

---

## Client conversation — OneDrive and Copilot

**What he said (verbatim):**
> "Integrating with our one drive. Someone was telling me copilot premium does
> this? So like can we use that with our agent? How will it work. And also talking
> to our dashboard - wip flow etc"

### What OneDrive integration means for Bridgit

Already in the plan. The design is a **drop zone**, not a live desktop mount:

1. MA creates an "Agent" folder in their existing OneDrive / SharePoint.
2. Staff drop a client's bank file into the right subfolder (by client/job).
3. Bridgit picks it up automatically via the **Microsoft Graph API**, copies it
   into Supabase Storage, and starts a job.
4. No one needs to log into Bridgit to upload — just drop the file as they
   always would.

This is **not** blocked on Phase 1. The pipe needs to work before Phase 1 is
declared started (per Decision 6 / build plan).

**TODO — follow up with Faraz: confirm Agent folder name + client subfolder
convention. He or Qasim needs to create it on the MA SharePoint side.**

### Copilot Premium vs Bridgit

Microsoft 365 Copilot is a general AI assistant baked into Office / Teams.
It can summarise a Word doc, draft an email, answer questions about a SharePoint
file. It does not know MA's accounting workflow, it does not produce your Excel
template, it does not run a bank rec, and it does not have memory of your clients.

Bridgit uses the same underlying models (Claude, GPT) but is purpose-built for
exactly MA's process. Copilot and Bridgit are not competing — you could have both.
Copilot is a general productivity tool. Bridgit is an accounting operations system.

### WIP / dashboard — what Faraz actually meant

Faraz's "talking to our dashboard - wip flow etc" was in the context of OneDrive,
not a separate request. He was asking: can the OneDrive connection also feed / update
the WIP board, not just drop files?

**Answer: yes, eventually — Phase 3.** Phase 1 OneDrive is file-drop only:
bank file lands in the Agent folder → Bridgit picks it up → job starts.

Later (Phase 3), the same OneDrive connection can trigger WIP updates automatically
when a job completes — no manual WIP entry needed. Build the file side first.

**What to tell Faraz for now — see the WhatsApp reply template below.**

---

## WhatsApp reply template for Faraz (OneDrive / Copilot / WIP question)

> OneDrive: yes, that's already in the plan. You drop files into an Agent folder
> on your existing OneDrive — Bridgit picks them up automatically. Later it can
> also update your WIP board when a job's done, but we build the file side first.
>
> Copilot Premium is Microsoft's general AI for Office — it can read your files
> but it doesn't know your accounting process. Bridgit uses the same models but
> built specifically for your workflow. Different things, you can have both.

Keep it short. Don't over-explain now.

---

---

## Client conversation — KB storage and data protection

**What he asked:**
> "Also where will the KB be saved. What data protection is in place? For
> confidential files."

### Answer sent

> KB: saved in your own dedicated Bridgit database — nothing shared with other
> firms, nothing we can access without your permission. One place, you control it.
>
> Data protection: files only go to Anthropic/OpenAI through business APIs with
> zero data retention turned on — client data doesn't train their models. Not the
> consumer chat apps. You'll have a Data Centre page in the dashboard where you
> can delete any client's files yourself without asking us. Raw bank files
> auto-delete 30 days after you sign off a job. NDA and DPA go into the contract
> before any real files move.

### What this maps to in the architecture

- **KB location:** dedicated Bridgit Supabase project — `ai_mappings`,
  `firm_rules`, `knowledge_chunks` (pgvector). One project to lock down,
  one project to delete from. Not shared with other firms.
- **ZDR:** Anthropic + OpenAI business APIs, zero data retention explicitly
  enabled. Not claude.ai / ChatGPT consumer apps.
- **Data Centre:** `/ma/ai/data` page in Phase 1 UI — Faraz / Qasim can delete
  per-client files, parsed data, or approved mappings themselves.
- **Retention:** raw bank files deletable after sign-off. Proposed 30-day
  auto-delete. Approved mappings + audit trail kept.
- **NDA + DPA:** in the contract before any real files move. See Decision 16.

---

## Plan changes applied (14 Sep 2026)

- **`17-build-plan.md` — End of Week 1 UI** updated: exception table is now
  explicitly interactive (answer on-screen, each answer saves to `ai_mappings`).
  Added framing: this IS the "teach it as we go" loop Faraz wants. Goal: Faraz
  uploads a real file in Week 1 and it feels better than Claude.
- **`17-build-plan.md` — Week 2** updated: added "feedback loop visible" item —
  show the accountant how many lines are now auto-resolving that weren't before.
  The "it's getting smarter" moment, permanently.

---

## Day 1 status (as of 14 Sep 2026, evening)

- [x] Supabase project created (new Bridgit project)
- [x] MFA on that Supabase project
- [x] Anthropic business API purchased
- [x] OpenAI skipped for Phase 1 (Decision 18)
- [x] Anthropic API key + Bridgit Supabase keys stored in local `.env` only (14 Sep evening)
- [x] ZDR requested from Anthropic sales (14 Sep)
- [x] ZDR confirmed on by Anthropic (17 Sep)
- [ ] Railway project for FastAPI (can wait until first deploy)

Real client files may go through the Bridgit API. ZDR is on.

## Day 2 status (14 Sep 2026, evening)

- [x] `supabase/schema.sql` applied on Bridgit Supabase (includes pgvector)
- [x] FastAPI jobs persist in Supabase (code wired — verify locally)
- [x] Bank file upload stored (code wired — run `supabase/storage.sql` if bucket missing)
- [x] Job status from DB
- [x] Local API run confirmed (`GET /health` shows `"database": "up"`)
- [x] Dummy job create + file upload verified (not a real client file)
- [x] Mirza confirmed in Bridgit Supabase Table Editor + Storage (14 Sep ~23:00):
  `ai_jobs` row "Day 2 pipe test" / `queued`; `ai_documents` dummy-bank.csv;
  Storage bucket `ai-documents` holds the file. **Day 2 closed.**

Key + Railway walkthrough: [19-day1-accounts-guide.md](./19-day1-accounts-guide.md)

## Day 2–3 status (15–17 Sep 2026)

- [x] 77 Koliqi mappings loaded (`scripts/load_koliqi_mappings.py`)
- [x] Excel template spike (`23-excel-template-spike.md`)

## Day 3–5 status (17 Sep 2026)

Following [17-build-plan.md](./17-build-plan.md) in order. **Not Starling-only** — Decision 24.

- [x] Bank ingest: `app/ingest` (PDF + CSV + Excel → canonical rows)
- [x] Categorisation: duplicates → approved mapping → proposed mapping asks → LLM on unknowns → exception
- [x] Excel writer into MA VAT workbook shape
- [x] Bank rec hard gate — both Koliqi Starling PDFs reconcile to £0.00 locally
- [x] `POST /jobs/{id}/process` wired
- [x] LLM step on (ZDR confirmed 17 Sep)
- [x] One-page PDF summary
- [x] Exception Accept / Override on the internal board (writes `ai_mappings`; duplicates keep-both / repeat)

Dashboard: `http://localhost:8000/` — sample CSV is a demo file; real Starling PDFs are allowed now.

## First live client run (18 Sep 2026)

Mirza uploaded Koliqi **August** Starling PDF on the board.

- Job title: Dashboard test. Status: `needs_input` until the 16 questions are answered.
- 40 lines, 16 open questions, working Excel + PDF summary downloadable.
- Engine path proven end-to-end on a real file (ingest → mapping/LLM → Excel).
- **Teach-as-we-go is now clickable:** Accept / Override on each card. Accept saves an approved mapping. Override saves your account + VAT. Same description on this job is coded together. Last answer → `ready_for_review`.

## Internal live board (17 Sep 2026)

Mirza asked for a visual on localhost:8000 so progress is not invisible while “engine before UI” is still the rule.

- **This is not the Faraz product UI.** Next.js (`apps/web`) remains the accountant app (upload, exception Accept/Override, download).
- **This is the engine board:** open `http://localhost:8000/` while uvicorn is running. Architecture stages, live `/health`, jobs from Supabase, sample CSV or real bank file upload + process. ZDR is on.
