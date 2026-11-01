# 19. Day 1 accounts guide — Anthropic key, ZDR, Railway

> Practical steps for 14 Sep 2026. Tracker: [17-build-plan.md](./17-build-plan.md).
> Decisions 18–20 in [08-decisions-log.md](./08-decisions-log.md).

---

## What is done

- Bridgit Supabase project exists
- MFA on that project
- Anthropic **business / API** purchased (not claude.ai)
- OpenAI **not** required for Phase 1
- Local `.env` filled: Supabase URL + anon + service_role, Anthropic key (14 Sep evening)

## What is left on Day 1

1. Request zero data retention from Anthropic sales (there is no toggle)
2. Optional now: create the Railway project. Deploy can wait until the engine runs locally

Day 2 can start locally without Railway.

---

## OpenAI — necessary?

No. Dual providers were only so we could A/B GPT vs Claude on the golden job. Faraz’s 5 accounts were Claude. Phase 1 is Anthropic-only. The code will still have a switchable provider interface so OpenAI (or anyone else) can be added later without rewriting the engine.

---

## Cheap APIs (DigitalOcean, etc.) — should we?

Not for the first real jobs.

Those 5 accounts worked because a **frontier** model sat in the problem with context. A rate like `$0.000233 per million tokens` is a tiny/cheap model class, not Claude. Using that in Week 1 would save almost nothing (one client file is small money) and would throw away the quality Faraz already felt.

**Do this instead:**

- Week 1: Claude (Sonnet-class for judgement). Same family he already trusts.
- After an internal Excel exists: consider Haiku / a cheaper model for *easy* lines, keep Sonnet for exceptions and personal-vs-business.
- DigitalOcean / Groq / Together: fine as a later adapter behind the same interface. Not the Week 1 brain.

Python still owns TB, bank rec, Excel, mappings. We are not “saving money by skipping the LLM.” We are not replacing Claude with a bargain model until we have a score.

---

## Where to create the Anthropic API key

Use the **Claude Console** (API), not claude.ai chat.

1. Open [https://platform.claude.com](https://platform.claude.com) and sign in with the **business/API** org you just bought — not the consumer Claude login if those are different.
2. Go to **Settings → API keys**  
   Direct: [https://platform.claude.com/settings/keys](https://platform.claude.com/settings/keys)
3. Click **Create key**.
4. Name it `bridgit-local` (or `bridgit-railway` later for a second key).
5. Prefer a **service account** key for anything that will live on Railway. A **personal** key is fine for local only; it dies if you leave the org.
6. Copy the key once. It starts with `sk-ant-`. You will not see the full value again.

Local `.env` (never commit this file — it is already in `.gitignore`):

```
ANTHROPIC_API_KEY=sk-ant-...
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_ANON_KEY=
BRIDGIT_ENV=local
```

Supabase keys: project → **Project Settings → API**. Use the **service role** key only on the FastAPI server, never in the Next.js browser bundle.

Billing: in Console, set a **monthly spend cap** so a bug cannot run away.

---

## Zero data retention — there is no on-switch

You cannot flip ZDR in the dashboard. Anthropic enables it **per organisation after you ask sales**.

**Request it:** [Anthropic sales](https://www.anthropic.com/contact-sales) / your account team. Say: commercial Claude API org for an ACCA firm’s bookkeeping product; need **zero data retention** on Messages API; no Files API / Batch / playground for client jobs.

**After they enable it, confirm:** Claude Console → **Settings → Privacy Controls → Data retention period**. You want this org on ZDR, not 30-day retention, for the workspace whose keys Bridgit uses.

**Status (17 Sep 2026):** Anthropic confirmed ZDR is on for this org. Bridgit may send client transaction text through the API. Still do not paste client files into claude.ai consumer chat or the Console Playground.

---

## Railway — FastAPI (can wait until first deploy)

Day 1 only needs the **project** to exist if you want. A green deploy of the empty stub is optional.

### Create the project

1. Sign up / log in at [https://railway.app](https://railway.app) with GitHub.
2. **New Project** → **Deploy from GitHub repo** → `bridgit-ai` (private is fine once GitHub is linked).
3. If it auto-detects Next.js from the repo root, that is wrong. We only want the API here.
   The **root Dockerfile** copies `apps/api` — leave Root Directory empty.
4. Open the service → **Settings** only if you are not using that Dockerfile:
   - **Root Directory:** `apps/api`
   - **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. **Variables** (same names as `.env`, no quotes):

   - `ANTHROPIC_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `BRIDGIT_ENV=production`
   - `BRIDGIT_PASSWORD` (team password for `/app` and `/jobs`)

6. **Settings → Networking → Generate domain.** Health check: `https://<your-app>.up.railway.app/health`. Accountants use `/app`. Dev board is `/board`.
7. Do not add the live MA Vercel project. This Railway service is Bridgit-only.

If the first GitHub deploy fights you because the stub is still in-memory jobs: skip deploy, create an **empty project** named `bridgit-api` and connect the repo later. The plan allowed Railway to wait.

Local run until then:

```
cd apps/api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy ..\..\.env.example .env
# fill ANTHROPIC_API_KEY
uvicorn app.main:app --reload --port 8000
```

---

## Do not do yet

- Real client bank files through Anthropic or Railway
- OpenAI account
- Cheap DigitalOcean models as the Week 1 brain
- Pasting keys into Slack, WhatsApp, or the MA dashboard repo
