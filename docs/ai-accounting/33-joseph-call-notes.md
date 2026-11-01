# 33. Call with Joseph (Zenas Security) — SharePoint + Azure

> **When:** ~10 Oct 2026 (three-way call after Faraz arranged it)
> **Who:** Joseph McLaughlin (`joseph@zenasecurity.nl`, Holland), Faraz (MA Associates;
> Joseph often says “Saeed”), Ali / Mirza (Bridgit)
> **Source:** auto-notes + full transcript. Names in the auto-notes are messy;
> speakers below are reconstructed from the transcript.
> **Prep that went in:** [32-joseph-call-prep.md](./32-joseph-call-prep.md).
> **Next:** Joseph emails a list of what he needs. Ali replies with Bridgit’s
> architecture. Then Joseph builds a **read-only** Graph API bridge to a **Man Tax**
> SharePoint copy.

---

## One-paragraph summary

Joseph is MA’s Microsoft / security consultant (SharePoint, admin, users, email).
He is **not** going to build Bridgit. He will **recommend and open the Microsoft
side**: a secure **SharePoint API bridge** (app registration + client certificate,
pull-only, IP-restricted) and later an **Azure Linux VM** if MA wants Bridgit
inside the tenant. Vocabulary correction: MA’s files live in **SharePoint**, not
personal OneDrive. SharePoint is a **document library**, not a Postgres database.
Agreed path: **proof of concept first** — Railway + current Supabase stays;
Joseph gives secrets so Bridgit can **read** a copy of the **Man Tax** folder
(lowest risk). Write-back and a live mirror of the **MA** client folder come
after that works. Full Azure (managed identity instead of certificates, optional
other MA products like CV on the same VM) is **step two**, after the workflow is
proven. Do **not** copy client files outside the Microsoft tenant as a “mirror”.

---

## Who said what (from the transcript)

### Faraz — why the call exists
- Introduced Joseph (cloud / SharePoint / Microsoft admin / security) and Ali
  (building Bridgit).
- Two goals: (1) connect Bridgit to MA’s file store **securely**; (2) keep Bridgit
  **in-house / ring-fenced** on Microsoft if a server is needed.
- Real workflow he wants: accountant says “work on this client’s year-end”;
  Bridgit finds files in the **client folder**, processes, asks check-this /
  check-that, then **drops the completed file back**. Download-from-chat is also
  fine as a second option.
- Asked whether Bridgit should work off a **mirrored copy** of the MA folder so
  it cannot wreck the live staff workspace.
- Confirmed **Man Tax** as the test site: less data, less damage if something
  goes wrong. MA folder is where staff actually work — later, not first.
- Cost: ~£20–30/month for Azure is acceptable; once it exists, **piggyback other
  products** Ali has built (he named **CV** and future ideas). Admin stays with
  Faraz as today.
- Asked about **ISO / certification** if an LLM sees confidential client data.
- Client WhatsApp chat is a **future vision**, not this phase. Staff-only for now.
  Clients send files in; MA save them into MA / Man Tax folders.

### Ali / Mirza — what Bridgit needs
- Bridgit is **Python / FastAPI**, intended host **Railway**, database
  **Supabase (Postgres on AWS)**. Both can be moved; the database must stay
  Postgres.
- Need **real-time access to documents** so they stop chasing Faraz for files.
- Asked: API vs what? Credentials / JWT? Where is “OneDrive” hosted?
- Proposed **two steps**: test the bridge while Bridgit stays on Railway; **then**
  move the whole app to Azure for production.
- For now **read** is enough; **read + write** later.
- Asked Joseph to describe the bridge clearly (compare to another project’s
  private network).
- Likes Azure VM for later; comfortable with Linux or Windows; asked if Azure
  OpenAI could replace Anthropic **inside** the tenant for stronger isolation.
- Flagged that **CV has outgrown free-tier hosting** — a shared VM would help
  that product too. Do Bridgit first, then CV.
- Will email Joseph the platform details Joseph asked for.

### Joseph — security / Microsoft side
- Role: **recommendations and Microsoft foundation**, not implementing Bridgit.
  “If it goes here, here are your concerns.”
- **Call it SharePoint**, not OneDrive. That is where MA’s existing files live.
- If Bridgit stays **outside** the tenant (Railway): he builds an **API** so
  Bridgit can pull files. Data does **not** have to move to Azure for that.
- If Bridgit **moves into Azure in the same tenant**: fewer walls; Postgres and
  the app can sit inside the fence.
- Asked whether Ali’s machine is Linux or Windows (Ali said Windows for local
  build; hosting is Railway).
- **Email him the stack** so he can set permissions based on where Bridgit sits
  today.
- Bridge: **Azure AD / Entra app registration + client certificate**. Ali gets
  secrets. Bridgit **pulls on demand** — not a permanent tunnel. Joseph
  registers Bridgit as an **enterprise app**: “if I get requests from this,
  with this information, you can have it.”
- IP restriction: only that location talks to SharePoint.
- **Moving to Azure later → managed identity** instead of certificate secrets
  (more secure, less secret handling).
- **Do not copy data outside the tenant.** “Anything you say data outside the
  tenant, I start throwing red flags.” A **bridge** to Railway is fine; a dump
  of the MA folder onto Ali’s AWS is not.
- Proof of concept **first**. Refine, make mistakes, then buy Azure.
- Mirror / sync: he will **think after the call**. Worried about two copies
  drifting (one updated, one not). May use **Power Automate** (“if something
  lands here, copy there”) once write-back exists. For now: **read a copy of
  Man Tax**.
- SharePoint is **not** a database — it is a document folder. He will look at
  the Man Tax site and play with options.
- Azure starter: **Linux VM, 2 CPUs, 4 GB RAM, ~$30/month**. Can shut the CPU
  down when idle; storage + static IP still cost a little. No long contract;
  can put **budgets / limits**. Earlier “£150–250” worry was a full-blown box.
- Other MA apps on the same VM: **yes**, can scale later.
- **AI vendor ISO:** he does not trust vendor claims (“they told us that’s what
  they did and then they lied”). Association risk even if MA does everything
  right, because **Claude is the one thing you don’t control**. Preference:
  **local LLM** long term. Practical advice now: **you don’t need to be
  certified, you need to be insured.** Regulation is still chaotic.
- Client-facing chat / WhatsApp: **a good problem later**. Maybe WhatsApp can
  ask questions but **cannot send files**. Need bailout paths.
- **Azure OpenAI:** research later. Landscape changes daily; **Microsoft
  integrations break more easily**. Get the **workflow working first**, then
  wipe the board and choose platform.
- Next: he sends a **detailed email** (questions + what he will give). Then
  Teams or Google Chat for “try it now” testing — not a call every time.

---

## Decisions from this call

1. **Files live in SharePoint**, not personal OneDrive. Talk and design in
   SharePoint / Graph API terms.
2. **Two-step hosting:** Railway + current Supabase for PoC; Azure (same tenant,
   Linux VM, managed identity) after the workflow is proven. Do not buy Azure
   before that.
3. **First SharePoint access is read-only**, pull-based, to a **copy of Man Tax**,
   not the live MA staff folder.
4. **Auth for the bridge:** app registration + **client certificate** while
   Bridgit is outside the tenant. **Managed identity** after a move to Azure.
5. **No client data dump outside the Microsoft tenant.** The bridge pulls; it
   does not replicate the library onto AWS.
6. **Write-back and folder mirroring** are post-PoC. Joseph owns the Power
   Automate / sync design.
7. **Azure OpenAI vs Anthropic:** research only. Do not switch LLM host until
   PoC works.
8. **Client WhatsApp / per-client chat:** future. Staff-only now.
9. **Other products (CV) on the same Azure VM:** Faraz is open; **after Bridgit
   PoC**, not instead of it.

---

## Technical picture (agreed)

```
Now (PoC)
  Bridgit FastAPI + Postgres (Railway / Supabase)
       --pull, cert + app registration, IP allowlist-->
  SharePoint: copy of Man Tax document library  [READ ONLY]

Later (production, if PoC works)
  Bridgit on Azure Linux VM (same MA tenant)
       --managed identity-->
  SharePoint (MA + Man Tax as designed)
  Optional: Azure OpenAI / local LLM  [not decided]
```

Joseph’s cost sketch for a small Linux VM: **~$30/month**, 2 vCPU / 4 GB RAM,
shut down when idle.

---

## Action items

### Joseph
- Email Ali a **roadmap**: questions he needs answered, secrets he will issue,
  protocols to confirm.
- Build/test the **read-only** Graph bridge to a **Man Tax** copy.
- Think through **mirrored library + Power Automate** for later write-back
  (do not block PoC on this).
- After Ali’s stack email: send **certificate / secrets / how to call** the API.

### Ali / Mirza
- Reply to Joseph’s email with: FastAPI, Railway, Supabase Postgres, what Bridgit
  will **GET** (files in a folder), **read-only first**, public egress IP if
  Railway has a stable one (or say “no static IP — please advise”).
- Test the bridge when Joseph says “try it now”.
- Keep Anthropic ZDR as the current LLM path; **research Azure OpenAI** in the
  background, do not promise a switch.
- Do **not** start copying MA/Man Tax libraries into personal drives or git.

### Faraz
- Man Tax folder designated for the test (done on the call).
- Keep coordinating Joseph ↔ Ali.
- Azure spend (~£20–30/month plus later CV) — he already said he is open.
- Insurance vs ISO: he asked; Joseph’s answer is **insurance**, not a Bridgit
  ISO badge.

---

## How this changes Bridgit (engineering)

- OneDrive “drop zone” in older docs is really **SharePoint Graph API**,
  **read-only**, **Man Tax first**.
- Do not treat SharePoint as a second Postgres. Ingest is still: download file
  → existing parsers → `ai_documents` / Storage.
- Railway stays valid for PoC. Azure VM is the **production house**, not a
  rewrite of the engine.
- Write-back of completed Excel into SharePoint is **after** read PoC — same
  as process-log “don’t skip bank analysis”.
- Local / self-hosted LLM is Joseph’s **preference**, not a Phase 1 commitment
  (Decision 5 still stands until volume or a hard compliance mandate).

---

## Email thread (after the call)

### Joseph asked (verbatim)

> Please remind me where everything is currently sitting, did you say Railway? Then the list of details of your platform, Windows? Postgres, etc.
>
> My first question would be, can you authenticate app-only through Microsoft Graph?
>
> Can you generate a certificate and send me only the public .cer? If not, we can do client secret
>
> Is your outbound ip static?
>
> Are you going to read the data when requests or made or for example, populate your database with Mantex at the beginning?

### Answers we are sending (do not drift)

| Question | Answer |
|---|---|
| Where is it sitting? | **Build is local (Windows + FastAPI) today.** PoC host is **Railway** (Linux container). We keep building the product as planned; the bridge is parallel, not a blocker. |
| Platform | Python / FastAPI / uvicorn. **Postgres via a dedicated Bridgit Supabase project** (not MA’s live database). Job files in **Supabase Storage**. LLM: Anthropic Claude **API** with ZDR — not claude.ai. |
| App-only Graph? | **Yes.** Confidential client (client credentials). No user login for this PoC. |
| Certificate? | **Yes.** We generate it, send Joseph **only the public `.cer`**, keep the private key on our side (never email, never git). Prefer cert over client secret. |
| Static outbound IP? | **No on Railway.** IPs change. Do not IP-allowlist Railway for PoC. Cert + app registration is the control. Static IP comes with the Azure VM later. |
| Read vs populate Man Tax? | **Pull on demand for a job.** Do **not** copy the Man Tax library into Postgres / Supabase. That would put a replica outside the tenant. Graph list + download the files for that job → existing ingest. Working copy for that job only. **Read-only.** |

### Certificate (Ali, after sending the email)

Do this on the laptop, **not in the git repo**. Email Joseph only `bridgit-graph.cer`.

```
openssl req -x509 -newkey rsa:2048 -keyout bridgit-graph.key -out bridgit-graph.cer -days 365 -nodes -subj "/CN=Bridgit Graph PoC"
```

Keep `bridgit-graph.key` private. Joseph uploads the `.cer` to the Entra app registration.

### Draft reply

Hi Joseph,

Thanks for this — answers below so you can start the bridge while we keep building Bridgit on our side. We are not waiting on SharePoint to continue the product work.

**Where it is sitting**

- Right now: still local. Windows laptop, Python FastAPI, same codebase we will deploy.
- Proof of concept host: **Railway** (Linux container). Yes, that is what I mentioned. Not Azure yet — that is the later step we agreed.
- Database: **Postgres** via a **dedicated Bridgit Supabase project** (hosted Postgres). This is not MA’s live database and not a copy of SharePoint.
- Job files (uploads / working papers we produce): Supabase Storage.
- LLM: Anthropic Claude **API** with zero data retention on. Not the public claude.ai chat.

So: Windows for development, Railway + Postgres for the PoC service, SharePoint stays in your tenant.

**App-only Microsoft Graph**

Yes. We can authenticate as a confidential client (app-only / client credentials) against Graph. No user sign-in for this PoC. Python side will use the app registration you create.

**Certificate**

Yes. I will generate a cert and send you **only the public `.cer`**. The private key stays on our side — it will not be emailed or committed. Happy to send that `.cer` as a follow-up to this email. If anything blocks that, we can fall back to a client secret as you said, but certificate is our preference.

**Outbound IP**

No — Railway does not give us a static outbound IP. It will change. Please do not IP-restrict the app to a Railway address for this test. The certificate + app registration should be the control. When we move to an Azure VM we can use a static IP / managed identity as you described.

**Read on request vs populate Man Tax into our database**

**Read when a request / job is made.** We will not bulk-copy the Man Tax library into our Postgres or Storage at the start. That would duplicate client files outside the tenant, which we want to avoid.

Intended flow for the PoC:

1. Bridgit (or the accountant) needs files for a specific job.
2. We call Graph, list/download only those files from the Man Tax copy you expose.
3. We run our existing pipeline on that working copy.
4. **Read-only.** No write-back in this phase.

If you need anything else from our side before you register the app (name, reply URL — we do not need a user login redirect for app-only), say the word.

Thanks,
Ali
