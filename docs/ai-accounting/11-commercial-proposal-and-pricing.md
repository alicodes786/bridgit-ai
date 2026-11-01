> **INTERNAL ONLY — DO NOT SHARE WITH THE CLIENT.**
> This file contains pricing strategy and negotiation notes. Every other file in this
> folder is safe to show MA Associates if useful; this one is not. If this folder is
> ever handed to the client or a third party, remove this file first.

# 11. Commercial Proposal and Pricing Strategy

Context this is based on: client is UK-based, price-sensitive but genuinely interested
in the project and willing to pay for proven value; you are Dubai-based. Client
temperament: negotiates hard on price, but is reasonable when he can see the value in
front of him — so the strategy is to price each phase so the win lands right before
payment is due, not to have one big negotiation up front.

## 11.1 Why milestone-based, not hourly or one lump sum

- **Hourly/day-rate** invites disputes over hours with a price-sensitive client and
  doesn't map cleanly to a phased AI project. Avoid.
- **One large upfront project fee** is a hard sell before he's seen anything real work
  — too much perceived risk for a cautious buyer.
- **Milestone-based fixed fees**, tied directly to the phases already defined in
  [04-roadmap-and-deliverables.md](./04-roadmap-and-deliverables.md), let him see
  exactly what he's paying for, and let each payment follow a visible win from
  [07-quick-wins-for-client.md](./07-quick-wins-for-client.md) rather than a promise.
  This is the recommended structure.

## 11.1a Realistic path for this client (use this, not 11.2)

The numbers in 11.2 are a UK-specialist price. He will not agree. Do not take £8k POC
to him as the opening ask. Use this structure instead.

**The trick:** do not sell a 5–7 week project first. Sell a **small paid proof** on
one of his real jobs. That is what he actually wants. Then sell the in-app POC only
after he has seen it work.

### What to take to him

**Step A — Paid proof (2–3 weeks). Ask £2,000. Floor £1,500.**

What he gets:
- One real past MA job (his files, his chart of accounts)
- System categorises the transactions, applies VAT, flags unsure items
- Scorecard vs the real finished file: % correct, exceptions, TB balanced yes/no
- A working demo he can watch — not a polished product inside the MA app yet

Payment: **£1,000 now, £1,000 when you show the scorecard.**

This is not free. API + hosting + your time for 2–3 weeks. Below £1,500 you are
working for almost nothing.

**Step B — In-app POC (3–4 weeks after A). Ask £3,500. Floor £2,500.**

What he gets: the AI Accountant tab inside the real MA dashboard, professional UI,
upload + chat + exception list, same engine as A now usable by staff.

Payment: 50% start, 50% on demo.

Only sell this after A works. If A is weak, you both stop. That is the deal that
makes a cautious client say yes.

**Step C — MVP.** Do not price this now. After A+B, quote **£6,000–£8,000**. He will
pay more once he has seen proof. If you quote MVP today, he will negotiate it down
before he believes it.

**Step D — Monthly.** After MVP, **£2,000–£3,000/month**. Not £3–5k.

### Totals he will actually hear

| If he only buys | He pays | You deliver |
| --- | --- | --- |
| Proof only | £1,500–£2,000 | One real job, scorecard, stop if it fails |
| Proof + in-app POC | £4,000–£5,500 | Usable tab in MA app |
| Through MVP | ~£10,000–£13,500 | Staff using it on live jobs |

That is roughly half of 11.2. It is still paid. It matches how he buys: small yes,
then next yes.

### How low can you go

| Number | Meaning |
| --- | --- |
| £2,000 proof | Fair. Take this. |
| £1,500 proof | Lowest you should accept. Tight 2 weeks, one job, no fancy UI. |
| £1,000 proof | Only if 100% up front and scope is tiny. You barely cover time. |
| Below £1,000 | Do not. He is testing if you work free. |
| Full in-app POC below £2,500 | Do not, unless proof already paid extra. |

**Hard rule:** never do the proof unpaid "and then we talk money." That is how this
client type gets a prototype and delays paying.

### What to say (plain)

"I won't ask you to fund the full system first. Send me one completed past job. In
about two weeks I'll run the AI on it and show you a score: how many lines matched
what your team already did, and what it flagged as unsure. That's £2,000 — half now,
half when you see the numbers. If it's not useful, we stop and you've only paid for
that test. If it is, the next step is putting it inside the MA app so the team can
use it — that's a separate piece, around £3,500. We only talk about that after you've
seen it work on your own file."

If he says too expensive: drop to £1,500, keep half up front, cut to one job / no
in-app UI. Do not drop the up-front half.

If he says "just build a small demo first, then we'll pay": "I can do a small demo.
It still costs API and time. £1,500, £750 now. Same scorecard. That's the smallest
version that is still real."

### Trade-off if you take the low path

The 5–7 week polished in-app POC in the roadmap splits in two: first the engine +
scorecard (ugly is fine), then the professional UI. Do not promise both for £2,000.

---

## 11.2 Higher price (only if he surprises you)

- **Discovery/Architecture** — already effectively delivered (this entire
  documentation set). Don't invoice this separately. Use it as a credibility/trust
  move: "we've already put real work into making sure this is designed correctly
  before asking for anything" — this also justifies why the POC price isn't
  rock-bottom despite being the "prove it" phase.

- **POC — 5-7 weeks.**
  - **Target: £6,000-£9,000 fixed.** Anchor around £8,000, floor at £5,000-£6,000 if
    he pushes hard.
  - Price this accessibly, not cheaply — it needs to be low-risk enough that he says
    yes quickly, but not so low that it signals low quality or anchors future phases
    too low. This is the phase where you're proving the concept, so protecting margin
    matters less than getting a fast yes and a clean start.
  - Tie the final payment explicitly to Win 4 in
    [07-quick-wins-for-client.md](./07-quick-wins-for-client.md) — the quantified
    scorecard against a real historical job. Don't release final payment before that
    demo happens; it's your leverage and his reassurance at the same time.

- **MVP — 6-10 weeks.**
  - **Target: £10,000-£15,000 fixed.** Anchor around £13,000.
  - By this point he's seen real proof (POC scorecard) — price sensitivity drops
    significantly once ROI stops being theoretical. This is where you recover margin
    against the deliberately modest POC price.

- **Production — 3-6 months, ongoing.**
  - Switch from fixed milestones to a **monthly retainer: £3,000-£5,000/month** for
    continued development and support. Fixed-fee stops making sense here since scope
    is genuinely iterative (see [04-roadmap-and-deliverables.md](./04-roadmap-and-deliverables.md)
    Phase 3).
  - **Optional success kicker:** an additional fee tied to measured value once live —
    e.g. a small fee per AI-processed job, or a percentage tied to accountant hours
    saved per month (use the exact metric from Win 5 in
    [07-quick-wins-for-client.md](./07-quick-wins-for-client.md)). This is the
    strongest lever for a cost-conscious client — he only pays more when he's
    demonstrably winning, which makes it an easy yes, and it converts the engagement
    into recurring revenue for you.

## 11.3 Payment terms

- **30% upfront, 70% on milestone delivery/demo**, per milestone (not one deposit for
  the whole engagement). Upfront portion covers your immediate costs (hosting, API
  credits, your time); the larger back-loaded portion reassures him he's only paying in
  full once he's seen the result.
- **Bill in GBP.** His currency, no FX complaints from him, and easier for him to
  benchmark against what a UK-based specialist would charge (which would typically be
  noticeably higher for this kind of work — that comparison is your leverage, don't
  undercut it by pricing like generic offshore web development).
- **If he pushes on price, negotiate payment schedule/timing before discounting total
  value.** A cost-conscious client often cares more about smoothing cashflow (e.g.
  splitting a milestone into 3 smaller installments) than about the absolute number.
  Offering that flexibility can close the deal without eroding the price itself.
- **Get scope in writing per milestone** — reuse
  [04-roadmap-and-deliverables.md](./04-roadmap-and-deliverables.md) almost directly
  as the scope-of-work text for each phase. This is your main protection against
  after-the-fact "can you also just add..." requests from a client inclined to
  negotiate.

## 11.4 Framing notes for the actual conversation with him

- Lead with the **phased structure and the fact that each payment follows a
  demonstrated win**, not with the total project cost — this reframes the
  conversation from "how much is this" to "here's what you get and when."
- If he compares your price to a cheap generic developer: the differentiator is that
  this is specialized AI/LLM systems work integrated into his firm's actual accounting
  process, not template software — worth stating plainly, not just implying.
- Don't offer the success-kicker/retainer model until Production — introducing it too
  early makes the earlier fixed fees feel negotiable by association.
- If he asks for a discount on the whole project up front, the answer is: "the
  price for the POC is already priced to get started quickly — let's prove the value
  first, and the rest becomes an easy conversation." This keeps the anchor prices
  intact while still sounding reasonable to him.
