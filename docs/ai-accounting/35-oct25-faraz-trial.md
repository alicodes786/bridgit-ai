# 35. 25 Oct — Faraz trial (working file, not final pack)

> **Evening notes (Queued, Bank Rec, chat uploads):**
> [36-oct25-session.md](./36-oct25-session.md).
> Do **not** Accept/Override live Hit Hunters or Koliqi.
> Dummy pack: Northbridge Demo Ltd. Knowledgebase in this phase is `ai_mappings`,
> not RAG / pgvector.

---

## Where we are in the plan

Still **commercial Phase 1**, **Week 1c**.

| Layer | Status |
|---|---|
| Bank working file (code lines, questions, Excel + rec) | Built |
| Client UI `/app` (Cards + Chat, password, dark MA gold) | Built |
| Teach-as-we-go (`ai_mappings` per client) | Built |
| Railway URL for Faraz | **You deploy this** (Dockerfile is in the repo) |
| Process-log Phase 2 — ETB / final statutory pack | **Not started** |
| Week 2 RAG | Parked |

Faraz can upload client bank + last year (+ extra papers). Bridgit codes known
payees, asks the rest, and **every answer is saved for that client**. Next job
for the same client auto-codes more. That is how the knowledgebase gets stronger
this phase. Extra PDFs/invoices are stored on the job; they are **not OCR'd yet**.

---

## What landed 25 Oct (this session)

- `/` now opens `/app` (Faraz). Internal cream board is `/board`.
- Extra papers on New job (optional, multiple files).
- Job page shows how many payees Bridgit already knows for that client.
- Chat: “I will remember X as Y for this client”; can ask what it has learned.
- Process runs in the background and the UI polls (Railway will not sit on one HTTP call).
- Dockerfiles + `Procfile` so Railway has a start command on `$PORT`.
- Demo Northbridge links hidden when `BRIDGIT_ENV=production`.

---

## You, before sending Faraz the URL

1. Bridgit Supabase SQL (if not already):

```sql
alter table ai_jobs add column if not exists engine jsonb;
alter table ai_jobs add column if not exists chat jsonb;
```

2. Deploy Railway (GitHub repo `bridgit-ai`).
   - Prefer **root Dockerfile** (copies `apps/api`). Do **not** also set Root Directory
     unless you know you want `apps/api` as the context.
   - Variables: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `ANTHROPIC_API_KEY`,
     `BRIDGIT_PASSWORD`, `BRIDGIT_ENV=production`.
   - Health: `https://<host>/health`
   - Faraz: `https://<host>/app` only.

3. Open `/app` yourself on that URL: login, Hit Hunters visible, download still works.
   Smoke Northbridge locally if you have not: bank CSV + last-year Excel from `/static/demo/`
   (local only; hidden in production).

---

## Message to Faraz (working file, not finished accounts)

> Bridgit is up at `https://<host>/app` — team password in the other message.
>
> New job → client name (same spelling as last time so it remembers) → job type →
> period → bank CSV/PDF/Excel. For year-end also attach last year’s workbook.
> Extra invoices/papers are optional (kept on the job; not read line by line yet).
>
> Use **Cards** or **Chat** like Claude. Each coding answer is saved for that
> client, so the next pack asks less.
>
> Download Excel + PDF when questions are done. That is the **bank working file**
> (Banking / Bank Pay / rec). It is not the finished statutory pack / ETB yet.
>
> Please do Hit Hunters on there and tell me what feels wrong.

Do **not** send an accuracy %.

---

## Parked until after he uses it

ETB / final pack, RAG, VAT box totals, SharePoint/Graph (Joseph), Azure VM,
local LLM, Vercel Next.js.
