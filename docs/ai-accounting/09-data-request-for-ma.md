# 9. Data Request for MA Associates (Qasim and Faraz)

This is the exact ask — what to request and, below it, a ready-to-send message you can
paste into your WhatsApp group. Historical jobs are **no longer the blocker** (Koliqi
VAT + Hit Hunters year-end are in hand). Remaining asks: VAT *decision* rules, and
later samples for property / sole trader / CIS.

> **Update 19 Sep 2026, after the Qasim/Carson walkthrough call** (full analysis:
> [25-sep19-meeting-analysis.md](./25-sep19-meeting-analysis.md)): item 2 below (chart
> of accounts) and item 4 (P&L vs BS / new-account rule) are **resolved, not incoming**
> — MA confirmed they don't maintain a formal coded chart of accounts, and the P&L/BS
> split is a structural trial-balance-stage decision, not a firm-specific lookup.
> Bridgit relies on its own standard accounting knowledge for both. **Item 3 (VAT
> decision rules) is the one Tier 1 ask still genuinely open** — the codes themselves
> (SR/ZR/EX/NV/OS) are confirmed, but not the rules for when to use which.
>
> **26 Sep:** a complete **company accounts** job is now in hand (Hit Hunters —
> comparative + current CSV + completed file + process log). That closes a large
> part of original Tier 1 item 1 for year-end. Still useful: property / sole trader /
> CIS examples (top 5 in [27-job-types-catalog.md](./27-job-types-catalog.md)), and
> the 31 Mar year-end Faraz mentioned. VAT “when to use which code” still open.

## What you actually need, in priority order

**Tier 1 — can't meaningfully start building the agent without these:**
1. **2–3 fully completed historical accounting jobs**, each with:
   - The raw current-year bank transactions (CSV/Excel export) they started with.
   - Any supporting documents available for that job (invoices/receipts), even
     partial.
   - The previous-year working file/accounts they rolled forward from.
   - The **final, reviewed, completed** working file/accounts for that job (the
     "answer key" we'll test against).
2. **Chart of accounts** — the actual list of account codes/names they use.
3. **VAT codes and the rules for applying them** — which code applies to which type
   of transaction, and how they decide.

**Tier 2 — needed to get accuracy right, but can start without them and fill in as
they arrive:**
4. Exact rule for **P&L vs. Balance Sheet** classification (what makes something one
   or the other, especially edge cases).
5. Rule for **when a new account should be created** vs. using an existing one.
6. The **bookkeeping template(s)** currently used (the actual Excel file structure —
   which tabs, which formulas link to what).
7. The exact **bank reconciliation** procedure they follow.
8. What "**pages agree to trial balance**" means concretely in their real files —
   which tabs/cells need to tie out.
9. Their **internal review checklist**.
10. A few real examples of **reviewer queries/corrections** from past jobs (what a
    reviewer typically catches or flags).

**Tier 3 — most valuable single thing, if they're willing:**
11. **A recorded 30-60 minute walkthrough** of one real job from source documents all
    the way to client approval, with an MA accountant narrating every decision as they
    make it ("I picked this account because...", "I know this is VAT-able because...").
    This one recording will likely teach us more than everything else combined.

## Ready-to-send WhatsApp message

You can send this as-is, or trim it down:

> Hey Qasim, Faraz — starting to build the AI accounting system now. Before we can
> get the first working version tested properly, I need a few things from you both:
>
> 1. **2-3 complete past jobs** — for each one: the raw bank transactions you started
> with, any invoices/receipts you had, last year's working file, and the FINAL
> completed/reviewed file. This is the most important thing — it's what lets us check
> if the AI is actually getting things right.
>
> 2. **Your chart of accounts** (the list of account codes/names you use).
>
> 3. **Your VAT codes** and how you decide which one applies to a transaction.
>
> 4. If you have 5 minutes: how do you decide P&L vs Balance Sheet for a transaction,
> and when do you create a brand new account vs use an existing one?
>
> 5. Your bookkeeping Excel template (the actual file structure/tabs you normally use).
>
> 6. Your bank reconciliation process and internal review checklist, if you have these
> written down anywhere (even rough notes are fine).
>
> Biggest ask if you have time: could one of you record yourself doing a walkthrough of
> one real job, start to finish, explaining out loud why you're making each decision as
> you go? Doesn't need to be polished — even a phone recording is genuinely more useful
> than another meeting.
>
> Send whatever you can, even if it's not everything at once — I can start working with
> partial info and fill in gaps as more comes through.

## What to do as data arrives

- Log what's received and what's still missing against the Tier 1/2/3 list above.
- The first historical job that's complete enough (raw data + final answer) becomes
  the first real test case — don't wait for all 2-3 before starting to build against
  the first one.
- Anything sensitive (real client financial data) should go into the isolated
  dev/test environment described in
  [02-architecture.md](./02-architecture.md) §2.13, not general-purpose storage.
