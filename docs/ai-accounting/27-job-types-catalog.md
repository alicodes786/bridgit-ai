# 27. Job types Bridgit will carry out (official catalog)

> **Source:** Faraz, 19–26 Sep 2026. Full list first; top 5 confirmed separately.
> **How to use this file:** this is the catalog of *what MA actually sells*. Not
> everything here is in the current engine. Build **step by step**, top 5 first.
> Cross-ref: [29-sep26-hithunters-and-job-catalog.md](./29-sep26-hithunters-and-job-catalog.md),
> [25-sep19-meeting-analysis.md](./25-sep19-meeting-analysis.md) §5.

Faraz: these are **not from the get-go**. Eventually, in this order of importance
for training and product coverage.

---

## Top 5 (build towards these, in this order)

| # | Job type | What it is | First real pack we have |
|---|---|---|---|
| 1 | **Company Accounts** | Statutory year-end accounts (full workbook: bank analysis → ETB → P&L → balance sheet → notes → corp tax) | **Hit Hunters Ltd**, year ended 28 Feb 2026 — [28-client-files-hithunters.md](./28-client-files-hithunters.md) |
| 2 | **VAT Returns** | Quarterly VAT working file (bank analysis → VAT calc) | **Koliqi & Sons**, first quarter — [20-client-files-koliqi.md](./20-client-files-koliqi.md) |
| 3 | **Property Lettings Account** | Landlord income & expenditure → feeds personal tax | Not received yet |
| 4 | **Sole Trader / Self Employed accounts** | Income & expenditure, then tax computation | Not received yet |
| 5 | **CIS Accounts** | Often CIS vouchers (sometimes **no** bank statements) → I&E → refund-heavy tax comp | Not received yet |

This ranking **supersedes** the informal ranking from the 19 Sep call (that one put
self-assessment employed above property lettings). Use **this** list when choosing
the next training job.

---

## Full catalog (eventually)

| Job type | Engine work? | Notes from MA (19 Sep + Faraz list) |
|---|---|---|
| Company Accounts | **Yes — top 1.** Bank analysis now; ETB/P&L/BS after bank analysis is proven on Hit Hunters | 21-tab statutory pack. Comparative file is the template. |
| VAT Returns | **Yes — top 2.** Bank analysis live on Koliqi | VAT box totals still a scope question ([26](./26-faraz-scope-tension-message.md)). |
| Property lettings accounts | Yes, later (top 3) | Simpler I&E. Prefer estate-agent statement + receipts; not always provided. |
| Self Employment Accounts (Sole Trader) | Yes, later (top 4) | Close to property I&E; no full BS complexity. |
| CIS Accounts | Yes, later (top 5) | ~30/year. Half have **no bank statements** — vouchers only. |
| Self Assessment (For Employed) | Later | Multiple P60s, tax-band lookups. On the full list, **not** in the top 5. |
| Partnership Accounts | Later | “Same as sole trader, not that different.” |
| Management Accounts | Later | **Forward-looking estimates**, not historical fact. Needs accountant-supplied growth % assumptions. |
| Capital Gains Tax Calculations | Later | Questionnaire + template, not bank analysis. |
| Company CIS and PAYE Filings | Later | Filing service, not the bookkeeping engine. |
| Backdated Accounts | Later | Variant of company accounts with extra reconstruction. |
| Specialist Tax Advisory | Later | Scenario modelling (e.g. sole trader → limited). Nylon more useful here. |
| HMRC investigations | Out of engine | Advisory / correspondence. Letter templates are Phase 3. |
| Use of Registered Address | Out of engine | Admin service, not accounts prep. |
| Company Formation | Out of engine | Qasim (19 Sep): *“I don't think Bridget would engage here.”* |
| Company Dissolving | Out of engine | Filing / legal process. |
| Dormant Account Filings | Out of engine | Qasim (19 Sep): *“Don't think it can do that.”* |

**Shared foundation for every engine job:** source docs are always some mix of bank
statements, purchase invoices/receipts, sales invoices (plus P60s / mortgage
statements for individuals). Bookkeeping analysis (banking + bank payments + rec)
is the common first half. The **job type** decides what happens after that
(VAT boxes vs ETB vs I&E vs CIS vouchers).

---

## Two rule layers (Faraz, 26 Sep — required, not optional)

> “It will need to differentiate between **company by company** rules [and]
> **job type by job type** rules and the only way you can do that is by storing
> a record specifically related to that client because certain clients have
> certain performers, certain formatting, certain rules, certain application of
> expenses.”

| Layer | Lives on | Examples |
|---|---|---|
| **Job-type rules** | job type (VAT / year-end / CIS / …) | VAT workbook shape; year-end ETB is the only engine; CIS starts from vouchers |
| **Client rules** | that client, forever | Hit Hunters: code by **payee** not CSV Category; director rem NIL this year; Copyright vs PRS column quirk; Private items query before DLA |
| **Client mappings** | that client + description/payee | Vodafone → Phone; Gocardless → Acc Fees / Web hosting as *this client* treated it last year |

Bridgit today only stores **client mappings** (`ai_mappings`). Job-type rules and
client rules are not first-class records yet. See Decision 25 in
[08-decisions-log.md](./08-decisions-log.md).

Never mix Hit Hunters year-end column names into Koliqi VAT mappings. Never apply
Koliqi “personal / drawings” defaults to a company with a Director's Loan Account.
