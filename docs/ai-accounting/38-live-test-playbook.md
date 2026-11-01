# 38. Live test playbook (Railway `/app`)

Use **Meridian Studio Ltd** for a clean run (new name, own files). Do **not**
Accept/Override on live **Hit Hunters** or **Koliqi** jobs.

Replace `<host>` everywhere with your Railway domain, e.g. `bridgit-api-production.up.railway.app`.

---

## A. Before you start (one-time)

1. Open `https://<host>/health` in the browser.  
   Expect: `"ok": true`, `"database": "up"`, `"llm": "anthropic-on"`.  
   If database is down → fix `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` on Railway and redeploy.

2. Confirm Railway **Variables** include:  
   `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `ANTHROPIC_API_KEY`, `BRIDGIT_PASSWORD`, `BRIDGIT_ENV=production`.

3. On **Bridgit Supabase** → SQL Editor, run if never done:
   ```sql
   alter table ai_jobs add column if not exists engine jsonb;
   alter table ai_jobs add column if not exists chat jsonb;
   ```

4. **Push latest demo files** to GitHub if you just regenerated packs locally; wait for Railway deploy to finish (or files on live may be old).

---

## B. Download the Meridian pack

On your laptop, save these four files (right-click → Save as):

| # | URL |
|---|-----|
| 1 | `https://<host>/static/demo/meridian-studio-bank.csv` |
| 2 | `https://<host>/static/demo/meridian-studio-comparative.xlsx` |
| 3 | `https://<host>/static/demo/meridian-studio-demo-brief.txt` (optional reference) |
| 4 | `https://<host>/static/demo/meridian-studio-insurance-note.txt` (for step H) |

If a URL 404s, redeploy from GitHub after `python scripts/make_demo_pack.py` was run and committed.

---

## C. Sign in

1. Go to `https://<host>/app` (not `/board`).
2. Enter the **Railway** `BRIDGIT_PASSWORD` (what you set in Variables, not necessarily local `test`).
3. You should land on the home screen (“Hello. What should we code?”) or the job list.

---

## D. Create the job

1. Click **+ New job** (sidebar or home card).
2. Fill in **exactly**:
   - **Client name:** `Meridian Studio Ltd`
   - **Job title:** e.g. `Meridian live test Nov 2026`
   - **Job type:** Company accounts (statutory year-end)
   - **Period start:** `2025-03-01`
   - **Period end:** `2026-02-28`
3. **Bank file:** choose `meridian-studio-bank.csv`
4. **Last year / comparative:** choose `meridian-studio-comparative.xlsx`
5. Click **Upload and process**.
6. Sidebar: open the new job. Status should move **Waiting → Processing → Needs your input** (or Ready if everything auto-coded).

---

## E. Read the header

On the job, check the four facts:

- **Period:** 1 Mar 2025 – 28 Feb 2026  
- **What this is:** Year-end accounts  
- **Lines coded:** increases as process runs  
- **Bank check:** should end as **Ties · £0.00** when done  

Toggle **Questions** vs **Chat** in the top-right pills.

---

## F. Answer questions (Cards or Chat)

Work through open cards until none remain. Typical Meridian demo:

| Question type | What to do |
|---------------|------------|
| Duplicate **Sainsbury's** (13 Feb, same amount) | **Keep both** (or exclude repeat — pick one and stick to it) |
| **ParkBee**, **Deliveroo** | Often Private or Motor — pick a column that matches your judgement |
| **Slate Creative Ltd** (money in) | **Sales** (new client receipt) |
| **Period / missing days** | Answer once if shown; note for re-upload test in step I |

Use **Save answer** / Accept on each card. Status should become **Ready for review** when the last question is closed.

---

## G. Downloads and outputs

1. Click **Working Excel** (top right). Open in Excel — **Banking**, **Bank Pay**, **Bank Rec** tabs updated.  
2. Press **F9** (Calculate) if formula cells look blank; Bank Rec should show **TIES**.  
3. Click **Summary** (PDF) — one-page job summary downloads.  
4. Do **not** treat this as the statutory ETB pack — it is the **bank working file** only.

---

## H. Chat checks

Switch to **Chat**. Try these messages (one at a time):

1. `How many lines are coded?`  
2. `What files are on this job?`  
3. `Is the working file ready?`  
4. `Which payees still need me?` (after all answered: should say none / all done)

**Late upload:** switch to **Chat** → **Add files** (picker allows `.txt`), choose
`meridian-studio-insurance-note.txt`, type `Please keep this on file for PI renewal`, **Send**.  
Or on **New job**, use **Other papers** (`.txt` allowed there too after latest UI).  
Bridgit stores it; Phase 1 does not OCR supporting files.

---

## I. Memory / same file re-upload

1. In Chat, **Add files** again and attach the **same** `meridian-studio-bank.csv`.  
2. Bridgit should **skip** identical bytes or not re-ask duplicate/coverage if you already answered and remembered.  
3. If it re-asks everything, note the job id for debugging — expected behaviour is remember on same client.

---

## J. UI smoke (optional)

- **Light / Dark:** sidebar bottom toggle; refresh — theme should stick.  
- **Narrow window:** **Jobs** button opens drawer; pick another job and back.  
- **Approve:** on Ready job, optional **Approve** (trial only — does not file with HMRC).

---

## K. What not to do on live

- Do not **Accept** all lines on **Hit Hunters** or **Koliqi** real jobs.  
- Do not send Faraz accuracy percentages.  
- Do not commit `.env` or real client CSVs to GitHub.

---

## L. One-line for Faraz (when you are happy)

> Meridian Studio Ltd is a dummy client on Bridgit — bank CSV plus last year’s Excel.  
> URL: `https://<host>/app` · password: *(team password you set)*.

Older pack name **Northbridge Demo Ltd** still works (`northbridge-*` files) but use **Meridian** for new tests.

Related: [37-live-demo-northbridge.md](./37-live-demo-northbridge.md) (legacy name), Decision 31 in [08-decisions-log.md](./08-decisions-log.md).
