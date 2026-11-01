# 24. Meeting agenda — 19 Sep 2026 (Qasim walkthrough)

Internal script for Mirza. Do not send this file to MA. Do not Accept/Override any
job on the board during this call. You are not coding the client.

**Goal of the call:** leave with (1) how they actually do a job, (2) the chart of
accounts, (3) VAT codes and how they choose them, (4) what they do when a VAT
invoice is missing (this showed up on Koliqi). Show Bridgit for 2 minutes if they
ask. Do not turn this into a product demo.

Live tracker: [17-build-plan.md](./17-build-plan.md). Original data ask:
[09-data-request-for-ma.md](./09-data-request-for-ma.md).

---

## 0. Open (1 minute)

**Say this:**

- "Thanks for making time. We've run a real Koliqi Starling statement through Bridgit. Known suppliers code from last year. Anything new or personal comes back as a question. We write Excel in your VAT file shape. Nothing is filed and I'm not here to demo the product."
- "What I need today is how you'd train a junior on a real job, plus your chart of accounts and VAT rules, so Bridgit follows your rules instead of guessing."
- "Can we start with you walking through one job the way you normally would?"

**Reminder for you:** known suppliers auto-code. New/personal = questions. Excel written. Nothing filed.

---

## 1. The walkthrough (most important, 15–20 min)

**What “walkthrough” means:** Qasim (Cass) opens one real job and talks through it
like training a new hire. Not the flowchart. A real file, decision by decision.

Faraz already framed this: you are a trainee. Real jobs deviate (missing invoices,
estimates). The flowchart is not enough.

**Ask them to go in this order** (their SOP from the August call). Each step has
a one-line reminder for you, then **exact words you can say**.

### 1. Comparatives

**Reminder:** last year vs this year. Like a diff to spot weird jumps.

**Say this:**

- "When you open a job, what's the first thing you look at before you touch the bank?"
- "How do you compare this year to last year? Which sheet or report?"
- "What would make you stop and ask the client a question at this stage?"

### 2. Opening balances

**Reminder:** starting numbers must match last period's closing. Wrong here = whole file wrong.

**Say this:**

- "Where do the opening balances come from? Last year's file, or somewhere else?"
- "What has to match what? Can you show me on the spreadsheet?"
- "If the opening balance doesn't tie, what do you do before you carry on?"

### 3. Bank analysis

**Reminder:** each bank line → category + VAT. This is what Bridgit is building.

**Say this:**

- "Can you walk me through three real lines on a bank statement and tell me how you'd code each one?"
- "How do you decide if a payment is business or personal?"
- "Do you need an invoice for every line, or can you code from the bank description alone?"
- "When you see something like Costa, parking, or a hotel, what's your default until you know more?"

### 4. Sales invoice listing (only if this job has sales)

**Reminder:** if the client sells things, sales invoices should match money coming into the bank.

**Say this:**

- "For a client like Koliqi, do you even use the Sales Invoices tab, or is it mostly bank-only?"
- "If you do use it, how do you check sales invoices agree with the bank?"
- "What do you do when the bank shows money in but there's no matching invoice?"

### 5. Bank rec

**Reminder:** opening + money in − money out = closing on the statement. Bridgit already checks this.

**Say this:**

- "How do you do bank rec in practice? Can you show me where you see if it's agreed?"
- "When the rec doesn't balance, what's the first thing you check: missing line, duplicate, or wrong opening balance?"
- "Have you got an example of a rec that was out by a few pounds and how you fixed it?"

### 6. Review

**Reminder:** second check before the file is "done".

**Say this:**

- "Before you sign this off as finished, what do you always skim?"
- "What mistakes does a reviewer usually catch: wrong VAT, personal spend, duplicates?"
- "If you were reviewing the Koliqi August file, what would make you send it back?"

---

**Any time they pick an account or VAT code, interrupt politely with:**

- "Why that one and not [the other option they didn't pick]?"
- "Why that VAT code on this line?"
- "Would you ever create a brand new account for this, or always use an existing one?"
- "Is this profit and loss or balance sheet, and how do you tell?"
- "If you don't have the invoice, can you still code it, or do you wait?"

**Write down their answers.** Do not click Accept on the August job even if they say "yes that's personal".

**If they won't walk a live file, say:**

- "Can we pick 8–10 lines from the August Koliqi statement together? Things like Trip.com, Booking.com, parking, a bakery, Experian, HMCTS. For each one, what account and VAT would you use, and why?"

---

## 1b. Doubts from the Koliqi pack (ask these, do not guess)

**Context for you:** we had bank PDFs + the finished VAT workbook, but almost no
purchase invoices. Only Burrows remortgage + conveyancing PDFs. Bridgit codes from
the bank only today. Invoice reading is Phase 2.

**Say this:**

- "For Koliqi, do you wait until you have all the purchase invoices before you finish the VAT file, or do you code the bank first and chase invoices later?"
- "If an invoice never turns up, what do you actually do? Leave it blank, mark it personal, estimate, or put a note on Notes and Queries?"
- "When you do have an invoice, like the Burrows remortgage one, do you enter it on the Purchase Invoices tab and on the bank analysis, or only one of those?"
- "How do you know you can claim VAT back if you only have the bank payment and not the invoice?"
- "On August we had hotels, parking, food, court fees. Would you code those from the statement alone, or refuse to code until you see a receipt?"
- "When something's missing, is that you chasing the client, or just an internal note for the team?"

Do not promise invoice matching today unless they say VAT cannot be right without it.

---

## 2. Chart of accounts (must leave with a file)

**Context for you:** Bridgit uses category names from the Koliqi workbook (Amazon, Dell,
Personal / drawings). We need the real list with **codes** (e.g. 6201 Motor).

**Say this:**

- "Can you send us your chart of accounts? The actual list you use, Excel or PDF, not a generic template."
- "For each account, is it profit and loss or balance sheet?"
- "Is it one chart for every client, or does Koliqi have its own setup?"
- "In the VAT workbook, the category column, is that the same name as the ledger account, or a shorthand?"
- "When would you create a brand new account instead of using an existing one?"
- "Are there accounts you never auto-pick, always ask first?"
- "For things we see a lot, software, motor, drawings, what are the standard codes you always use?"

**Ask them to send on the call if possible:** chart of accounts file (codes + names).

---

## 3. VAT codes (must leave with the rules, not only the letters)

**Context for you:** Bridgit uses SR, ZR, EX, NV, OS. We need when they pick each one.

| Code | What it means (quick) |
|---|---|
| SR | Standard 20% VAT |
| ZR | Zero rated |
| EX | Exempt |
| NV | No VAT / personal / out of scope |
| OS | Outside scope |

**Say this:**

- "Can you walk me through when you use SR versus NV versus OS? What's the difference in your head?"
- "For Koliqi specifically, property and development, what's usually business VAT and what's usually personal?"
- "Parking, food, hotels, flights, Companies House fees, bank charges: for each type, which VAT code do you normally use?"
- "If the supplier charged 20% on the receipt, do you always use SR, or sometimes something else?"
- "Can we open three lines in the completed Koliqi VAT file and you tell me why that VAT code was chosen?"
- "Who decides VAT, you as the accountant, or does it depend on the client's VAT registration?"
- "Can you send a one-pager or even rough notes on your VAT rules? Examples help us more than a long explanation."

**Ask them to send:** VAT rules or examples, even handwritten notes.

---

## 4. If they ask about Bridgit (keep it short)

**If they ask about chat / Claude:**

- "We use the same kind of AI underneath, but Bridgit remembers each client, writes your Excel, and saves every answer so you don't re-teach it. Questions stay in a table, not a long chat."

**If they ask when they can use it:**

- "The engine is running on Koliqi already. We need today's rules loaded, then your team answers the open questions on a real job. I'm not coding those myself."

**If they ask for a demo:**

- Show localhost:8000 for 2 minutes max. Architecture boxes + one job with questions. Do not Accept anything live.

---

## 5. Do not

- Accept / Override / Keep both on the live job.
- Quote an accuracy %.
- Promise WhatsApp, invoices, or the MA dashboard embed today.
- Put client files in WhatsApp / Claude / this chat. They send into the usual
  private folder.

---

## 6. Leave-with checklist

- [ ] Walkthrough happened (or 8–10 lines narrated)
- [ ] Chart of accounts file promised / received (codes + names)
- [ ] VAT codes + decision rules promised / received
- [ ] What they do when a VAT / purchase invoice is missing (Koliqi pack was thin)
- [ ] P&L vs BS / new-account rule if they said it
- [ ] Who sends the files, and by when

After the call: put files in `data/client/` (gitignored), tell engineering. Firm
rules stay empty until those files exist.
