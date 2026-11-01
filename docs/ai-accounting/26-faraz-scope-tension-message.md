# 26. Message for Faraz — "finalise the calculation" scope tension

> **Context:** raised in [25-sep19-meeting-analysis.md](./25-sep19-meeting-analysis.md)
> §7, from the 19 Sep Qasim/Carson walkthrough call. See
> [17-build-plan.md](./17-build-plan.md) Week 1b — the first item there is blocked on
> this getting resolved with Faraz.
>
> **Update 1 (before the first draft was sent):** Faraz replied to a related comment
> with:
>
> > "Phase 1 should be very quick then. Because the analysis part is the easy part
> > honestly."
> >
> > "That's what I was saying. I don't fully get all these phases."
>
> This is bigger than a VAT-only tension — he's expecting fast finalisation for **any**
> job type, and phase language isn't landing with him.
>
> **Update 2 (actually sent, 19 Sep 4:52–4:56pm, three WhatsApp messages):** kept a
> short reference to the Scope of Works link (live at
> `https://bridgit-scope-works.netlify.app/`) rather than dropping phase language
> entirely, offered the job-by-job breakdown as a fallback only if the phase framing
> still doesn't land (didn't send the detailed VAT/company-accounts breakdown text
> up front — held it in reserve), and closed with the **other job types** point
> (self-assessment, CIS, property letting, management accounts — full list in
> [25-sep19-meeting-analysis.md](./25-sep19-meeting-analysis.md) §5). Real sent text
> and the held-in-reserve follow-up are both below.

---

## 0. What this actually means — the two things to keep straight

**a) This is bigger than VAT, and bigger than company accounts.** MA described at
least seven other job types on the call (self-assessment, CIS, property letting,
management accounts, partnership accounts, capital gains, specialist advisory — see
[25-sep19-meeting-analysis.md](./25-sep19-meeting-analysis.md) §5). "Finalise the
calculation should be fast" logically extends to all of them once Faraz hears it
applied to company accounts, not just VAT. **The message needs to address that
directly, not let him assume "and everything else too" by default.** The honest
answer for each of these is the same shape as company accounts: each one needs its
own "finish it" step built once (CIS has vouchers + a refund calculation,
self-assessment has tax-band lookups, property is a simple income & expenditure,
capital gains could be a questionnaire) — but **none of them start from zero**, because
the bookkeeping/categorisation layer underneath (the part that's actually built, and
that compounds per client with every job Bridgit processes) is shared across all of
them. That's a real answer, not "don't worry about it" — say it precisely so the same
confusion doesn't repeat itself for CIS in three weeks.

**b) Heads-up for you (Mirza), not for the message to Faraz:** the Scope of Works /
`11-commercial-proposal-and-pricing.md` milestone structure prices Phase 1 and Phase 2
separately. If "finish company accounts" (and now, implicitly, every other job type)
gets treated as included in what he already paid for, that's the exact scope-creep
scenario `11-commercial-proposal-and-pricing.md` warns against. Don't raise price in
this message — not the right moment, and he's already said phases confuse him, so a
pricing argument now would land badly. Flag it to yourself as a live risk and revisit
once he's seen a real finished VAT number and has something concrete to react to.

---

## Message actually sent (WhatsApp, 19 Sep, 4:52–4:56pm — three messages)

> **4:52pm:** Yes, Phase 1 should be quick, and it'll have the bookkeeping analysis
> ready for you.
>
> But if we're talking full pipeline, like VAT actually finished, company accounts
> actually fully finished, everything, that's Phase 2 and Phase 3 both coming into the
> picture, as per the Scope of Works link I sent you.
>
> Have a look at that again when you get a chance (that's why I say it's best to read
> it, to avoid any mismatches or conflict of interest later — I do the same with all
> clients before proceeding)
> https://bridgit-scope-works.netlify.app/
>
> **4:53pm:** But let me know please if the phase talk still isn't landing, we will
> have to go another way, like job by job.
>
> **4:56pm:** I know we have other types of jobs too, like self-assessment, CIS,
> property letting, management accounts and a couple more which Qasim walked me
> through. Same logic applies to all of them, one still needs its own "finish it"
> step built once, but none of them start from zero.
>
> By the time company accounts is solid then Bridgit's already learned a lot from VAT
> jobs — like it's doing really well now for Koliqi — and then from your prompts and
> messages when you actually use it, each new job type will be understood faster by
> Bridgit, and cheaper to add.

**What changed vs the earlier draft:** shorter, and deliberately held back the
detailed VAT-vs-company-accounts breakdown (invoice-reading not built yet, the £10k
van judgement-call example) — it's offered as a fallback ("if the phase talk still
isn't landing... job by job") rather than sent up front. That's a reasonable call:
lead with the Scope of Works reference first, see if that alone resolves it, keep the
more granular technical explanation in reserve rather than over-explaining
pre-emptively. **Keep that reserve message ready** — see below — in case he replies
that the phase talk still isn't landing.

---

## Reserve follow-up (send only if he says the phase framing isn't landing)

> **VAT (Koliqi, and any VAT job):** once the bank lines are categorised, turning that
> into the actual return number — Box 1, Box 4 — is quick. That's just adding up
> numbers we already have. I can get that finished soon, no caveats.
>
> **Company accounts (trial balance, profit and loss, balance sheet):** this one is
> honestly not quick, and it's not because of any phase label — it's because a bank
> statement alone genuinely isn't enough to finish a company's accounts.
>
> Qasim mentioned today that the trial balance pulls from the banking and the
> purchase and sales invoices. We haven't built the invoice-reading piece yet — that's
> real, separate engineering, not a delay for the sake of it.
>
> On top of that, some decisions genuinely change year to year for the same client —
> like the £10k van example you mentioned on the call, capitalise one year, expense
> the next, same client, different call each time. Those need a human to confirm each
> time, they can't be auto-finished either.
>
> So in short: VAT, yes, fast, I can show you a finished number soon. Company
> accounts, finishing it properly needs the invoice-reading piece built first — that's
> the honest size difference, nothing to do with what we call it.

## Why the "other job types" closing line is worded carefully

It says precisely what carries over (the categorisation/learning layer, which is
real and already visible on Koliqi) and what doesn't (each job type's own finishing
logic — CIS vouchers, tax-band lookups, etc. — still needs building once) —
**cheaper and faster, not free.** That avoids the exact overstatement that started
this thread ("the analysis part is the easy part") resurfacing for CIS or
self-assessment in a few weeks.

## If he says "just do both / do it all, why can't it all be fast"

Send the reserve follow-up above, and if he pushes further: *"VAT is fast because we
already have everything it needs — the bank data. Company accounts, and most of the
other job types, need invoices read and matched too, and we haven't built that part
yet. That's not a choice, it's what's actually built vs not built right now. I can
start building it — just tell me if that's the priority over other things in the
queue."*

## Next steps

- **Waiting on Faraz's reply.** If he says the Scope of Works link resolves it — no
  further message needed, log his acknowledgement and move on.
- **If he says phase talk still isn't landing:** send the reserve follow-up above.
- **If VAT ends up the agreed priority:** build VAT box-total calculation now
  (already queued in `17-build-plan.md` Week 1b).
- **If company accounts (or another job type) is the real priority:** flag clearly
  that invoice reading/matching has to be scoped and built first — this is a
  genuinely bigger chunk of work than anything currently in flight. Don't attempt to
  "finish" company accounts (or CIS, self-assessment, etc.) without that piece; it
  produces a wrong number, not a slow one.
- **Either way:** revisit the pricing/milestone question from §0(b) once there's a
  concrete deliverable to point to, not an abstract phase argument.
- **Keep "Phase 1/2/3" internal-only from here** — useful for our own planning docs,
  not for conversations with Faraz; use the job-by-job / capability-by-capability
  framing with him going forward since that's what actually landed.
- **Note:** the Scope of Works is now live at
  `https://bridgit-scope-works.netlify.app/` — worth adding this link to
  `17-build-plan.md` / `README.md` so it's easy to find internally too.
