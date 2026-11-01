# 34. 12 Oct night — where we paused

> **Superseded for next steps:** see [36-oct25-session.md](./36-oct25-session.md)
> (evening) and [35-oct25-faraz-trial.md](./35-oct25-faraz-trial.md).

> Stopped ~02:40. Pick up here in the morning. Do **not** Accept/Override live
> Hit Hunters or Koliqi questions. Use the dummy pack for trials.

---

## What Faraz can do (once Railway is up)

Open `/app`, password, pick a job. **Cards** (buttons) or **Chat** (type like Claude).
Answers teach `ai_mappings`. Download Excel + PDF. Approve when questions are gone.

This is a **bank working file**, not ETB / full statutory. SharePoint is Joseph’s
track in the background.

---

## What landed this session

**Trial hardening (so a real URL is safe)**
- Engine summary saved on the job (coded counts, bank rec)
- Client names match case-insensitively
- Team password: POST + HttpOnly HMAC cookie; `/jobs` locked when `BRIDGIT_PASSWORD` is set
- Approve + retry process
- 25MB upload cap

**Client UI (`/app`)**
- MA logo (`apps/api/app/static/MA_logo.jpg` from job-dashboard `public/MA_logo.jpg`)
- Cards | Chat toggle (remembered)
- Chat: composer pinned, Enter sends, Shift+Enter new line
- Hide/show questions while chatting
- Optimistic send + “Bridgit is working” dots (no “Sending…” stuck in the box)
- Em dashes stripped in the UI
- Dark theme on `/app`: near-black canvas, MA gold accent, gold Send / active toggle
- Sign out is a real sidebar button (clears the session cookie)

**Dummy pack (fictional — not a live MA client)**
- Files only, **not** a job in the database until you upload them
- `apps/api/app/static/demo/northbridge-bank.csv`
- `apps/api/app/static/demo/northbridge-comparative.xlsx`
- Rec ties £0.00. Known payees auto-code; new payees, Uber Eats (Private), Tesco duplicate = questions
- Regenerate: `python scripts/make_demo_pack.py` from `apps/api` with `PYTHONPATH` set

**Chat backend**
- `POST /jobs/{id}/chat` → coding answer or job-knowledge or Claude (grounded)
- Transcript on `ai_jobs.chat` (migration `004_job_chat.sql`); falls back onto `engine.chat`

---

## Why you do not see a “Northbridge” job

It was never created in Supabase. The sidebar only shows jobs you (or Faraz) uploaded.

**To create it locally**

1. http://127.0.0.1:8001/app (uvicorn: `apps/api`, port **8001**)
2. **+ New job**
3. Client: `Northbridge Demo Ltd`
4. Type: Company Accounts
5. Period: 2025-03-01 to 2026-02-28
6. Download from the modal links (or `/static/demo/...`) and attach bank CSV + last year Excel
7. Upload and process

Then it appears on the left. Answer it freely. Leave Hit Hunters / Koliqi alone.

---

## Still on you before Faraz

1. Supabase SQL (Bridgit project):

```sql
alter table ai_jobs add column if not exists engine jsonb;
alter table ai_jobs add column if not exists chat jsonb;
```

2. Railway: CLI not installed here. Deploy `apps/api` with `SUPABASE_*`, `ANTHROPIC_API_KEY`, `BRIDGIT_ENV=production`, `BRIDGIT_PASSWORD`. Send him `https://<host>/app`.

3. Set `BRIDGIT_PASSWORD` in `.env` (local already in use).

---

## Next in the app (in order)

Still testing — do **not** Accept live Hit Hunters / Koliqi.

1. **You, locally:** Ctrl+F5 `/app`, upload Northbridge Demo Ltd (CSV + last-year Excel from `/static/demo/`). Exercise Cards, Chat, hide questions, Sign out, then Approve when questions are gone.
2. **Supabase:** run the `engine` + `chat` jsonb SQL (block above) if not already.
3. **Railway:** deploy `apps/api` with `SUPABASE_*`, `ANTHROPIC_API_KEY`, `BRIDGIT_ENV=production`, `BRIDGIT_PASSWORD`. Send Faraz `https://<host>/app` only.
4. **Faraz trial message:** Cards or Chat, he answers **Hit Hunters**, downloads Excel. Not a finished statutory pack. No accuracy %.
5. After his feedback: tighten question copy, then VAT box totals / more job types. Not ETB yet.

Parked: ETB, RAG, SharePoint/Graph (Joseph), Azure VM, local LLM.
