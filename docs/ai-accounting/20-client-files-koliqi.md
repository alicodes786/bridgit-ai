# 20. Client files — Koliqi & Sons (come back)

> **Day 2 closed (14 Sep).** Dummy job confirmed in Bridgit Supabase by Mirza.
> **Day 2–3 closed (15 Sep).** 77 mappings loaded. Excel spike done.
> **Day 3–5 engine closed enough to run live (18 Sep).** First real job: August Starling PDF on the dashboard, 40 lines, 16 questions.
> **Exception loop live (18 Sep).** Accept / Override on `http://localhost:8000/` writes `ai_mappings`. PDF summary downloadable.
> **26 Sep:** CoA is not coming (Decision 25/26 era — MA has no coded chart). Second
> client is **Hit Hunters** year-end — do not mix mappings. Koliqi remains the VAT
> track. Next on Koliqi still: those 16 August questions when an accountant answers
> them. Do not paste client files into chat.

## Where they go

`d:\bridgit-ai\data\client\koliqi-sons\`

That folder is gitignored. Never commit. Never Slack / WhatsApp / claude.ai / this chat.

This Cursor session is **not** the Bridgit Anthropic API. Parser + process exist. ZDR is on (17 Sep). Dummy job already proven. Real Starling PDFs can be processed on the dashboard.

## What MA sent (14 Sep 2026)

On disk at `data/client/koliqi-sons/` (gitignored):

| File | Likely role | When we use it |
|---|---|---|
| `StarlingStatement_2026-04_2026-07.pdf` | Bank input (Apr–Jul 2026) | Day 3–5 parser. PDF, not CSV. |
| `StarlingStatement_2026-08_2026-08.pdf` | Bank input (Aug 2026) | **First live job 18 Sep** (Dashboard test). |
| `Completion Statement.pdf` | Conveyancing / completion | Supporting. No OCR gate. |
| `Purchase Statement of AC - Draft V2 - 27.05.26.pdf` | Draft purchase statement | Supporting. |
| `Burrows invoice - Remortgage.pdf` | Invoice evidence | Attach to job. No matching in Week 1. |
| `Koliqi_Sons_VAT_File_May-Jun_2026 (FN CL).xlsx` | **Highest value.** Completed VAT working file | Day 2–3 → `ai_mappings` + Excel shape. |

## Rules when we come back

1. Workbook first (mappings + template).
2. Then bank (parse format). Ask for CSV if PDFs are scans.
3. Invoices last. Attach only. No OCR gate.
4. Internal run only. No % scorecard to Faraz.
5. Delete local copies when that piece of work is done (Decision 16).
