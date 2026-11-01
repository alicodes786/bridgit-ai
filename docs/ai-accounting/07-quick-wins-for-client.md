# 7. Quick Wins — What to Show the Client, and When

The client is trusting a fairly abstract idea ("AI accountants"). The way to keep
confidence high isn't one big reveal at the end — it's a sequence of concrete,
believable moments early and often. Here's the sequence, mapped to the roadmap in
[04-roadmap-and-deliverables.md](./04-roadmap-and-deliverables.md), with what makes
each one land well with a non-technical stakeholder.

## Win 1 — "It's inside our actual system" (end of POC Week 2)

**What it is:** the polished job-creation flow and chat panel live inside the real MA
dashboard — a genuine "AI Accountant" tab, not a prototype on some random URL.

**Why it lands:** this is the moment it stops feeling like "some AI experiment" and
starts feeling like "our software got a new feature." Non-technical stakeholders judge
credibility heavily on whether something *looks* finished. This is the single highest
perception-per-effort win in the whole project, which is exactly why the polished-UI
decision (confirmed in [08-decisions-log.md](./08-decisions-log.md)) is worth the extra
week.

**How to present it:** log into the real MA app, click the new "AI Accountant" tab,
show the client picker and file upload, send one chat message. Nothing needs to be
"smart" yet for this demo — it needs to look and feel real.

## Win 2 — "Watch it read a real bank statement and understand it" (POC Week 3-4)

**What it is:** upload one of MA's own real historical transaction files, and the
system correctly normalises it and shows a transaction count, date range, and basic
summary — before any AI classification even happens.

**Why it lands:** it's tangible proof the system can handle *their* real, messy data,
not a clean toy example. This quietly de-risks the biggest technical fear (real files
are messy) in a way the client can see for themselves.

## Win 3 — "It categorised most of a real job automatically" (POC Week 4-5)

**What it is:** run the Bookkeeping Agent against a real historical job and show the
live categorisation happening — transactions getting an account, a VAT code, and a
confidence score, with the ones it's unsure about clearly flagged rather than guessed.

**Why it lands:** this is the actual product working, and just as importantly, it
visibly does **not** pretend to know things it doesn't — the exception queue right next
to the "confident" results is what makes this trustworthy rather than magical. Frame it
exactly this way to the client: "it's not trying to fool anyone — here's what it's
confident about, and here's what it's flagging for a human."

## Win 4 — "Here's the proof it matches what your senior accountant actually did" (POC Week 5, end of POC)

**What it is:** the quantified scorecard against a real historical job — e.g. "1,247
transactions, 91% correctly classified automatically, 34 exceptions correctly
flagged as uncertain, trial balance balanced, bank reconciliation agreed, processed in
9 minutes."

**Why it lands:** this is the win that turns "looks impressive" into "we can actually
trust this." It's a comparison against MA's own real completed work, not a synthetic
demo — the client can judge it the same way they'd judge a junior accountant's trial
piece. This is the moment that should determine whether you get budget/buy-in to
proceed to MVP.

## Win 5 — "It's already saving real review time" (early MVP)

**What it is:** the same workflow, but now running alongside a live (not historical)
client job, with a real MA staff member reviewing and approving the output, and a
measured "time this would normally take vs. time it took with the AI doing the first
pass."

**Why it lands:** this converts the story from "a clever prototype" to "a productivity
tool our staff are actually using." This is the number (hours saved per job, per
month) that ultimately justifies the investment.

## Win 6 — "We can see exactly why it made every decision" (any time from POC onward, but especially worth highlighting once a client raises trust concerns)

**What it is:** click into any transaction the AI classified and see the full trace —
which prior mapping or firm rule it used, what evidence it looked at, what confidence
it assigned.

**Why it lands:** accountants are (rightly) skeptical of black boxes handling client
money. This is the answer to "how do we know it's not just making things up" — and it's
already built into the architecture (see
[02-architecture.md](./02-architecture.md) §2.6/§2.14), so it costs nothing extra to
show off once it exists.

## What NOT to lead with

- Don't lead with the chat interface alone — "look, I can talk to an AI" is the least
  impressive part of this project and undersells everything else that's actually hard
  and valuable (the accounting logic, the accuracy, the auditability).
- Don't show a demo on synthetic/made-up data if a real-historical-job demo is
  available — real data is dramatically more convincing to accountants than a clean toy
  example, and they'll ask.
- Don't present a confidence score as ground truth before it's been calibrated (see
  [02-architecture.md](./02-architecture.md) §2.9) — if you show "94% confident" and it
  turns out wrong in front of the client, that costs more trust than it's worth. Show
  exception flags and the scorecard's *measured* accuracy instead of raw model
  confidence claims.
