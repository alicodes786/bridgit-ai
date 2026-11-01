# 31. Status + UI Plan — 26 Sep 2026

> **Context:** End-of-session status check + UI decision after first Hit Hunters
> company-accounts live run. Related: [17-build-plan.md](./17-build-plan.md),
> [29-sep26-hithunters-and-job-catalog.md](./29-sep26-hithunters-and-job-catalog.md).

---

## Where We Stand Right Now

### Build plan week position
| Week | Scope | Status |
|---|---|---|
| 1 — Engine | Ingest, categorise, Excel output, bank rec, LLM, exceptions | ✅ Done |
| 1b — Intake | Job types, period, missing-doc check, client rules | ✅ Done |
| 1c — Hit Hunters | Year-end bank analysis, payee map from comparative | ✅ 10 questions, correct shape |
| 2 — RAG | pgvector semantic search before LLM | ❌ Not started |
| 3 — Harden | Multiple formats, edge-case coverage | ❌ Not started |
| 4 — UI | Client-facing exception review table + job board | 🚧 Started this session |
| 5 — Demo | End-to-end sign-off | ❌ Not started |

Engine is done. UI is the blocker between "works on localhost" and "Faraz can use it."

### Live jobs in Supabase (26 Sep)
| Job | Client | Type | Status | Questions |
|---|---|---|---|---|
| Hit Hunters Feb 2026 | Hit Hunters Ltd | company_accounts | needs_input | 9 (+ 1 period gap) |
| Koliqi Aug 2026 | Koliqi & Sons | vat_return | needs_input | 16 (no comparative) |

The Hit Hunters questions (pulled from DB, 26 Sep):
1. Snap 247 — 10 lines, £349.90 — Private (last year) — client query
2–9. 8 new payees: Play Dir Ltd, Lewisham PCN, NCP, Ebony Systems, LB of Merton, HMRC SA, MFG Streatham, paddle.net/Bandlab
10. Period gap — CSV ends 27 Feb, period says 28 Feb

These are **for Faraz/Qasim to answer**, not for the developer. They know which
column each payee should go to. Every answer saves permanently to `ai_mappings`.

---

## Why the Engine Does Not Call the LLM for Year-End

This is intentional, confirmed by a senior-dev review (Sonnet 4.6 thinking high, 26 Sep):

- **Year-end "coding" is a column position in an MA-specific Excel**, not a semantic
  category. The LLM does not know MA's Banking / Bank Pay column layout.
- Faraz's own process log: "Code by payee from prior year. New payees → ask."
- Private / Suspense items must never be auto-posted — always a client query.
- Hallucination in statutory accounts is worse than a question.

**When LLM WILL be used (Phase 2 plan, not now):**
- Pass the client's actual column headers (extracted from comparative) as context.
- LLM proposes top-2 candidate columns, never auto-applies, shown as quick-pick
  suggestions inside the question card.
- `source` stays `human` regardless. The model assists; the accountant confirms.

---

## Key Bugs Fixed This Session (26 Sep)

| Bug | Fix |
|---|---|
| Script needed to load prior-year payees (separate step) | Comparative uploaded on the job auto-extracts + seeds mappings on process |
| VAT Return was the default job type — no company_accounts coding ran | Dropdown now requires a choice; VAT is not pre-selected |
| Type showed as `vat_return` even for year-end jobs | `effective_job_type()` promotes to `company_accounts` if comparative has Banking + Bank Pay tabs |
| Old VAT job for Hit Hunters still in DB | Deleted via `delete_job()` |
| Same payee = one question per line (flood) | `_collapse_payee_questions()` collapses to one card per payee group |
| Prefix match boundary bug (`"TES"` → `"TESSA CONSULTING"`) | Word-boundary check enforced on both directions |
| Sibling lines inconsistently `needs_review=False` | All sibling lines stay `needs_review=True` until lead question answered |

---

## Next Steps

### Immediate (unblocks Faraz today)

1. **Deploy to Railway** — 2-hour job. API gets a real URL. Faraz can reach it.
   ```bash
   cd apps/api
   railway init   # new project
   railway up
   # Set env vars: SUPABASE_URL, SUPABASE_SERVICE_KEY, ANTHROPIC_API_KEY
   ```

2. **Send Faraz the URL** — ask him to answer the 9 Hit Hunters questions himself.
   He knows the columns. Bridgit can't answer them for him.
   Message template: *"Engine is done. Need you to answer 9 questions on Hit Hunters
   Feb 2026 — you know the columns, I don't. Once answered Bridgit writes the Banking
   and Bank Pay tabs into a copy of last year's Excel and you can download it."*

### This session — new client-facing UI

**Decision:** Keep `localhost:8000/` as the dev board (existing). Build a proper
client-facing SPA at `/app`, served from the same FastAPI process, deployable to
Railway with no separate build step.

See §UI Design below.

### Week 2 (after Faraz answers questions + downloads Excel)

1. Internal compare: Bridgit's output vs completed 2026 Excel Faraz sent
2. If Banking / Bank Pay tabs match → process-log Phase 1 complete for Hit Hunters
3. Only then: process-log Phase 2 (ETB, journals, comparatives) — separate chunk
4. VAT decision rules from Qasim (codes confirmed; decision logic still open)
5. Week 2 RAG: pgvector semantic search before LLM for VAT-type jobs

---

## Two-Screen UI Design (Client-facing, built 26 Sep)

**Goal:** Faraz / Qasim open a URL, see their clients and jobs, answer questions,
download the Excel. It should feel like talking to a junior accountant, not filling
in a form.

### Access
- Hard-coded password gate (no auth system yet). Default: see `.env.example`
- Password set via env var `BRIDGIT_PASSWORD`. If unset, gate shows a warning.
- Stored in `localStorage` as a session flag. Cleared on sign-out.

### Screen 1 — Job board
```
┌─────────────────────────┬────────────────────────────────────────────────┐
│  BRIDGIT                │                                                │
│  MA Associates          │        ← select a job to open it              │
│  ─────────────────────  │                                                │
│  + New job              │                                                │
│                         │                                                │
│  Hit Hunters Ltd        │                                                │
│    ● Feb 2026 year-end  │                                                │
│      Needs your input   │                                                │
│                         │                                                │
│  Koliqi & Sons          │                                                │
│    ● Aug 2026 VAT       │                                                │
│      Needs your input   │                                                │
└─────────────────────────┴────────────────────────────────────────────────┘
```

### Screen 2 — Job conversation
```
Hit Hunters Ltd  ·  Company Accounts  ·  Mar 2025 – Feb 2026

┌─ Bridgit ────────────────────────────────────────────────────────────────┐
│  I've analysed 168 bank lines for Hit Hunters Ltd.                       │
│                                                                          │
│  159 lines matched last year's coding and were applied automatically.    │
│  9 lines are new or need your confirmation.                              │
│                                                                          │
│  Bank rec: £0.00 ✓   |   Hard gates: passed                             │
└──────────────────────────────────────────────────────────────────────────┘

┌─ Question 1 of 9 ────────────────────────────────────────────────────────┐
│  NEEDS DECISION                                                          │
│  Snap 247 — 10 lines, £349.90                                           │
│  Last year this sat in 'Private'. Query the client before it goes to    │
│  the Director's Loan Account (or confirm it stays as a query).          │
│                                                                          │
│  27 Jan 2026 · Out · £349.90  ·  Saved coding                          │
│  This answer also codes 9 other lines for the same payee.              │
│                                                                          │
│  [ Private ]  [ Director Loan Account ]  [ Motor ]  [ Other… ]         │
└──────────────────────────────────────────────────────────────────────────┘

┌─ Question 2 of 9 ────────────────────────────────────────────────────────┐
│  NEW PAYEE                                                               │
│  Play Dir Ltd Sw — 1 line, £1,000.00                                   │
│  New payee (not in last year's file). Which column?                     │
│                                                                          │
│  [ Directors Remuneration ]  [ Salaries ]  [ Other… ]                  │
└──────────────────────────────────────────────────────────────────────────┘
```

Quick-pick buttons are derived from the client's coded lines on this job (the
account names already applied automatically). Client-specific, no hardcoding.

When the last question is answered:
```
┌─ Bridgit ────────────────────────────────────────────────────────────────┐
│  ✓ All done. 168 lines coded. Bank rec: £0.00.                          │
│                                                                          │
│  [ Download Excel ]   [ Download PDF summary ]                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### New job modal
- Client name (autocomplete from existing clients or free-text new)
- Job type (dropdown — Company Accounts at top, VAT Return second)
- Period start / end
- Bank file upload
- Comparative file (shown for all types — auto-promotes to company_accounts if
  the file has Banking + Bank Pay tabs)
- [Process] — creates job + processes immediately

---

## Robustness Notes for More Uploads

Faraz will upload more jobs. Expected cases:

| Scenario | What happens |
|---|---|
| VAT Return (no comparative) | Normal path: prior mapping → LLM → exception |
| VAT Return with VAT comparative | Comparative used as Excel template only; payees not extracted (no Banking/Bank Pay tabs) |
| Company Accounts + comparative | Auto-promotes job type; extracts payees; code-by-payee path |
| Company Accounts, no comparative | Runs without payee map; all lines → questions |
| New client, first job | No prior mappings; everything → questions (this is correct) |
| Wrong job type selected | If comparative has Banking+Bank Pay, auto-corrects to company_accounts |
| Same client name with different capitalisation | `get_or_create_client` is case-sensitive — could create duplicate clients. **Known risk.** Fix: normalise to title case on create. |

The one known risk is client-name case sensitivity. Faraz should use consistent naming.
The UI will show existing client names as autocomplete suggestions to reduce this.
