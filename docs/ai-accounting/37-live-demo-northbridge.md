# 37. Live demo packs (Railway)

**Use Meridian Studio Ltd for new tests** — step-by-step:
**[38-live-test-playbook.md](./38-live-test-playbook.md)**.

Northbridge Demo Ltd below is the **older** demo name (same idea, different payees).

## Download the pack (works on Railway)

Replace `<host>` with your Railway domain (no trailing slash):

| File | URL |
|------|-----|
| Bank CSV | `https://<host>/static/demo/northbridge-bank.csv` |
| Last year Excel | `https://<host>/static/demo/northbridge-comparative.xlsx` |
| Brief (this script in plain text) | `https://<host>/static/demo/northbridge-demo-brief.txt` |
| Optional supporting note | `https://<host>/static/demo/northbridge-supporting-vat-note.txt` |

Production hides the demo links in **New job** (`show_demo` off). The static URLs
above still work — bookmark them or download on your laptop and upload from disk.

Regenerate files after edits: `cd apps/api && python scripts/make_demo_pack.py`

## Create the job on live

1. Open `https://<host>/app` and sign in.
2. **+ New job**
3. **Client:** `Northbridge Demo Ltd` (new client is fine).
4. **Job type:** Company accounts (statutory year-end) — or VAT if you want to
   test VAT path with the same bank file (year-end + comparative is the richer demo).
5. **Period:** start `2025-03-01`, end `2026-02-28`.
6. Upload **bank CSV** + **comparative xlsx** together.
7. Wait for process → answer **Cards** or **Chat** questions.

## What the story exercises

| Area | What to look for |
|------|------------------|
| Auto-code | O2, Tesco, Sage, Castles, HMRC, Client ABC, MA Associates, Canva, AWS, Stationery, Bright Forge (from last-year columns) |
| Duplicate | Two Tesco lines same day/amount — **Keep both** once; re-upload same CSV should not re-ask if remembered |
| New payees | Lime, NCP, Github, Uber Eats, Client XYZ — mapping or Private |
| Bank rec | Header **Bank check → Ties · £0.00** after process |
| Output | **Working Excel** download — Banking / Bank Pay / Bank Rec rewritten |
| Late upload | Chat → **Add files** → supporting VAT note; message + file in one send |
| Chat (today) | “How many lines are coded?”, “What files are on this job?”, “Is the working file ready?” |

## Client one-liner for Faraz

> Northbridge Demo Ltd is a dummy design consultancy — Countingup CSV plus last
> year’s MA Excel. It shows auto-coding, a duplicate line, new payees, and the
> bank working file. Nothing here is a live client.

## Product note (logged)

Bridgit should also support **normal conversation** about the job (progress,
what it knows, plain-English summary) and **exportable** chat/data like Claude.
See **Decision 31** in [08-decisions-log.md](./08-decisions-log.md).
