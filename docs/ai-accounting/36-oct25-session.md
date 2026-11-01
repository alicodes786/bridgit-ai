# 36. 25 Oct (evening) — Queued, Bank Rec, chat uploads

> Pick up here. Do **not** Accept/Override live Hit Hunters or Koliqi.
> Dummy pack: **Northbridge Demo Ltd** only. Dummy Test Client is gone.
> Knowledgebase this phase is still `ai_mappings`, not RAG.
> Faraz still gets `/app` only. Railway deploy is still **your** step.
> Full prior trial notes: [35-oct25-faraz-trial.md](./35-oct25-faraz-trial.md).

---

## What this session was

Mirza used `/app` on the dummy Northbridge job, then asked for three product
fixes and a full write-up of the evening:

1. **Queued** looked like “still in line” while Cards said processing failed.
2. **Bank Rec** on the working Excel looked thin; make it MA-clear.
3. **Uploads after the job exists**, on the chat bar, like Claude/GPT.
4. Document the lot and tick the tracker.

---

## Queued vs failed (Northbridge second test)

Queued never meant “still coding.” Normal flow:

**Waiting → Processing → Needs your input → Ready for review.**

What happened on **Northbridge second test**: files were up, process started,
then died (0 lines). The engine put the job back to `queued` with
`engine.last_error` so Retry would work. **Cards** showed “Processing did not
finish.” **Chat** hid that banner, so it looked like nothing had started.

Fixes:

- Status label: `queued` → **Waiting**; `queued` + `last_error` → **Didn’t finish**.
- Same fail + **Retry process** on Chat as on Cards.
- Chat opener no longer says “all questions are answered” when there are 0 lines.
- Chat answers “is the working file ready?” from job facts, not a guess.
- Failed process **merges** `last_error` into existing `engine` json (does not
  wipe counts).
- Working files now save to a **unique storage path**. Same filename + upsert
  was leaving Excel downloads on a stale blob.

The dummy job was then processed: **16 lines, 14 auto-coded, 2 questions**.
Re-download Excel after a refresh; an old Downloads copy is stale.

---

## Bank Rec (working file)

Year-end Bank Rec is no longer five loose labels. Bridgit **rebuilds** the
`Bank Rec` sheet on every year-end write (VAT `Bank Reconciliation` uses the
same layout).

Stable formula cells (do not move):

| Cell | Meaning |
|---|---|
| E8 | Opening (yellow) from the statement / CSV |
| E9 | Receipts formula → Banking total |
| E10 | Payments formula (negative) → Bank Pay total |
| E11 | Calculated close `=E8+E9+E10` |
| E12 | Statement closing (yellow) |
| E13 | Difference `=E11-E12` (must be nil) |
| E14 | `TIES` / `DOES NOT TIE` |

Navy/gold, notes, linked totals. Live Hit Hunters / Koliqi packs were **not**
rewritten in this session.

**Opening / closing on Northbridge** (`11,168.72` / `10,948.40`): dummy-client
pounds, but **correct for that CSV**. Bridgit reads the Countingup running
balance (earliest line ± that movement = open; latest balance = close). It
does not invent the yellow cells. Blue formula rows stay blank until Excel
calculates (`F9` / Calculate Now). On a real job the same two cells come from
that client’s statement.

Demo comparative regenerated: `apps/api/app/static/demo/northbridge-comparative.xlsx`.

---

## Dummy Test Client removed

**Day 2 pipe test** (`Dummy Test Client`) deleted from Bridgit Supabase,
including storage objects, mappings, and the client row. Sidebar should only
show:

- Hit Hunters Ltd
- Koliqi & Sons Developments Ltd
- Northbridge Demo Ltd

Do not delete those. A leftover client named **Hithunters** (no space) may
still appear in the New job picker; leave it unless you choose to merge it
later.

---

## Chat-bar uploads after the job exists

You can attach files **after** New job, from Chat (paperclip / drop on the
composer) or Cards (**Add files**). Same kinds as the first upload:

| Bridgit decides | What it does |
|---|---|
| **bank** (CSV / statement-like Excel or PDF) | Stored as bank. **Process runs** (codes lines, rebuilds Excel). Latest bank wins. |
| **comparative** (year-end pack with Banking + Bank Pay, or a last-year filename) | Stored as last year. **Process runs** (payee map + year-end tabs). |
| **supporting** (photos, random PDFs, extra papers) | Stored on the job. **Not OCR’d.** Chat can list them. Process is **not** re-run (that would wipe open answers). |

API: `POST /jobs/{id}/files` (multipart `files`, optional `note`). Classifier:
`app.job_intake.classify_upload`. Chat facts include uploaded names; “what
files are on this job?” is grounded.

Extra invoices still do **not** post into Sales/Purchase tabs. That stays
Phase 2.

---

## Code / files touched (this evening)

- `apps/api/app/static/app.html` — status labels, Chat fail/retry, paperclip
- `apps/api/app/engine/process_job.py` — merge `last_error`
- `apps/api/app/engine/chat.py` — working-file + files questions; `last_error` in facts
- `apps/api/app/engine/ma_template.py` + `yearend_excel.py` — Bank Rec layout
- `apps/api/app/engine/excel_writer.py` — money format
- `apps/api/app/jobs_store.py` — unique working-file storage path
- `apps/api/app/job_intake.py` + `routers/jobs.py` — classify + `/files`
- `apps/api/scripts/make_demo_pack.py` — demo Bank Rec
- Tests in `test_week1bc_intake.py`, `test_trial_hardening.py`

---

## Still you / still parked

- **Railway:** Dockerfile is in the repo. Set `BRIDGIT_PASSWORD`, keys,
  `BRIDGIT_ENV=production`. Health then send Faraz `/app` only.
- SQL if missing: `alter table ai_jobs add column if not exists chat jsonb;`
  (`engine` is already on live Supabase).
- Do **not** Accept live Hit Hunters or Koliqi.
- ETB / final pack, RAG, VAT box productization, SharePoint (Joseph), Azure VM:
  parked. See [35-oct25-faraz-trial.md](./35-oct25-faraz-trial.md).

Try on dummy: open Northbridge Chat → paperclip a spare PDF → should stay
supporting. Paperclip a second bank CSV → should go to Processing.

### Same-file re-upload (later the same evening)

Re-dropping the **same** bank CSV used to wipe Tesco duplicate + period-coverage
questions. Bridgit now: (1) skips process if the bytes already are the bank file
on the job; (2) stores Keep both / Carry on on the job (`engine.remembered`) so
Retry process does not re-ask. Chat send is **message + files in one go**.

### `/app` look (same evening)

Home is a bookkeeping greeting (orb, “What should we code?”, New job / open questions / working Excel). Sidebar is a quiet job list. Chat composer is **Add files** plus a round send. Dark with a warm glow, MA gold. Not a generic chatbot skin.
