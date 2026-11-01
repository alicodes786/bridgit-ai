Yes bro — **I read the flowchart properly**, and with the transcript + meeting notes + MA codebase, we now have enough context to narrow this down considerably.

The flowchart should be the **backbone of the accounting workflow**. The architecture exists to execute that workflow safely; we shouldn't invent an abstract “multi-agent system” and then try to force the accounting process into it.

The chart gives us this real process:

**source documents → working file → prior-year/template setup → transaction-by-transaction analysis → account/category → VAT → supporting documents → trial balance → reconciliation checks → internal review → queries/amendments → client approval.**

That matches the meeting's goal of specialist AI workers operating in stages. 

Here is how I would turn everything into an **actual build plan**.

---

# 1. First, freeze the architecture

Don't start coding individual prompts randomly.

This is the architecture I want us to build toward:

```text
MA ASSOCIATES DASHBOARD
        │
        │ New AI Job / Chat / Upload
        ▼
┌─────────────────────────────┐
│      JOB ORCHESTRATOR       │
│                             │
│ Client                      │
│ Job                         │
│ Accounting period           │
│ Current stage               │
│ Required approvals          │
└──────────────┬──────────────┘
               │
      ┌────────┴────────┐
      │ KNOWLEDGE/TOOLS │
      │                 │
      │ MA database     │
      │ Uploaded files  │
      │ Previous jobs   │
      │ Firm rules      │
      │ RAG             │
      │ Excel processor │
      │ FreeAgent       │
      │ Xero            │
      │ Nylon/HMRC      │
      └────────┬────────┘
               │
               ▼
        BOOKKEEPING AGENT
               │
               ▼
       ACCOUNTS PREP AGENT
               │
        HUMAN APPROVAL
               │
               ▼
          REVIEW AGENT
               │
        HUMAN APPROVAL
               │
               ▼
        REPORTING AGENT
               │
               ▼
             DONE
```

But **we are not building all of that now**.

The meeting explicitly agreed to master one agent first, then add the others. 

---

# 2. The flowchart becomes our state machine

This part is important.

I would literally encode the workflow you sent into states.

```text
RECEIVED_SOURCE_DOCUMENTS
        ↓
NORMALISING_DOCUMENTS
        ↓
WORKING_FILE_READY
        ↓
PRIOR_FILE_SELECTED
        ↓
PROCESSING_TRANSACTIONS
        ↓
CATEGORISING_TRANSACTIONS
        ↓
APPLYING_VAT
        ↓
MATCHING_SUPPORTING_DOCS
        ↓
TRIAL_BALANCE_READY
        ↓
VALIDATING_DEBITS_CREDITS
        ↓
VALIDATING_BANK_RECONCILIATION
        ↓
VALIDATING_TB_LINKS
        ↓
INTERNAL_REVIEW
        ↓
QUERIES_RAISED
        ↓
AMENDMENTS
        ↓
CLIENT_APPROVAL
        ↓
COMPLETE
```

This is where **LangGraph fits better than a loose router**.

LangGraph supports persistent graph state and can stop execution for human input and later resume from the stored state, which is exactly what we need around the review/approval steps. ([Docs by LangChain][1])

So:

**Router = determines what workflow/job this is.**

**State graph = runs the actual accounting process.**

---

# 3. Do NOT make every box an agent

This is one of the biggest architectural decisions.

For example:

> “Debits = credits?”

doesn't need an LLM.

That's code.

```python
if total_debits == total_credits:
    continue_workflow()
else:
    raise_exception()
```

Same with:

* does client have prior file?
* is VAT registered?
* account exists?
* bank opening/closing balance arithmetic
* debit/credit totals
* file exists
* job status
* period dates

Use **deterministic code** whenever there is a definite answer.

Use the **LLM only where judgement is required**.

For example:

> Barclays: £3,428.00 — STRIPE PAYMENTS UK

What account/category should that map to?

That is something the Bookkeeping Agent can reason about using:

* transaction description
* client history
* previous-year mappings
* accounting rules
* invoices/supporting documents
* firm knowledge

That's where the LLM earns its place.

---

# 4. Agent 1 — Bookkeeping Agent

This is what we build first.

Looking directly at your flowchart, its responsibilities should initially be:

```text
SOURCE DATA
    ↓
Working file
    ↓
Previous accounts/template
    ↓
Transaction
    ↓
Find appropriate account
    ↓
Categorise P&L / Balance Sheet
    ↓
Determine VAT treatment
    ↓
Match supporting evidence
    ↓
Post proposed bookkeeping entry
    ↓
Next transaction
```

The Bookkeeping Agent should return structured data, not paragraphs.

For every transaction:

```json
{
  "transaction_id": "TX-1028",
  "account_code": "7200",
  "account_name": "Software",
  "account_type": "PL",
  "vat_code": "T1",
  "net": 100,
  "vat": 20,
  "gross": 120,
  "confidence": 0.94,
  "source_evidence": ["invoice-283.pdf"],
  "requires_review": false
}
```

That becomes **much more reliable** than:

> “Claude, please look at this Excel and do the bookkeeping.”

---

# 5. Start POC from the working file, NOT PDF conversion

This is where I would intentionally deviate from doing the entire diagram immediately.

Your client already said PDF conversion would be useful, but they currently use Adobe and it isn't essential for the first version. 

So POC v0.1 starts here:

```text
            ↓
     ADD TO WORKING FILE
            ↓
     Prior file exists?
            ↓
           ...
```

Not here:

```text
Receive random JPEG
↓
OCR
↓
PDF extraction
↓
conversion...
```

Otherwise half of our first two weeks gets eaten by document extraction instead of proving the accounting AI.

Initially:

**Accepted inputs**

```text
.xlsx
.csv
previous-year .xlsx
```

Then PDF/JPEG ingestion becomes Phase 2.

---

# 6. First thing YOU need from MA

Before coding the Bookkeeping Agent, get **2–3 completed historical jobs**.

Each job should include:

```text
BEFORE
Current-year bank transactions
Source Excel/CSV
Relevant invoices/documents if available
Previous-year working file

AFTER
The actual completed bookkeeping/accounts Excel
Correct transaction classifications
Correct VAT treatment
Correct TB
Final reviewed file
Reviewer corrections if available
```

This is probably the most valuable data we can possibly get.

Because then:

```text
Historical raw data
        ↓
Our AI
        ↓
AI result

vs

Actual accountant result
```

Now we can measure whether the thing works.

The meeting already identified previous client Excel files/templates as necessary training/test material. 

---

# 7. Second thing we need: define every diamond

This is **your immediate discovery task with Qasim/Faroz**.

The flowchart tells us *what decisions happen*, but not yet the exact decision rules.

We need answers for these:

| Flowchart decision   | We need to know                                 |
| -------------------- | ----------------------------------------------- |
| Already Excel/CSV?   | Accepted formats/column structures              |
| Readable PDF?        | What makes something readable/unreadable?       |
| Prior file exists?   | How do we locate it?                            |
| Similar client file? | What determines “similar”?                      |
| Account exists?      | Which chart of accounts? Where is it stored?    |
| Assign P&L/BS        | Exact MA categorisation rules/examples          |
| VAT registered?      | MA DB already knows some of this                |
| VAT treatment        | All VAT codes + MA rules                        |
| Supporting documents | How are invoice↔transaction matches determined? |
| Debits = credits?    | Easy deterministic check                        |
| Bank rec agrees?     | Exact reconciliation formula/process            |
| Pages agree to TB?   | Which workbook pages and which links?           |
| Internal review      | Full reviewer checklist                         |
| Queries raised?      | What counts as a query and what happens next?   |

**This is now the highest-priority requirement.**

The screenshot is enough to design the system.

It is **not yet enough to teach the accounting rules**.

---

# 8. Build a “MA Accounting Rulebook”

This becomes extremely important.

Instead of putting everything into one huge system prompt, create structured rules.

Something like:

```text
knowledge/
    firm/
        bookkeeping_rules
        chart_of_accounts
        vat_rules
        account_creation_rules
        review_checklist

    templates/
        year_end
        vat
        self_employed
        property

    examples/
        completed_job_001
        completed_job_002
        completed_job_003
```

And eventually:

```text
client/
    ABC_LIMITED/
        preferences
        previous_mappings
        recurring_suppliers
        previous_year
        reviewer_corrections
```

That's the knowledge the agents work from.

---

# 9. RAG goes here — not everywhere

Use RAG for:

```text
Previous accounting notes
MA SOPs
Tax notes
Client notes
Historical comments
Accounting policies
Long PDFs
Nylon/HMRC knowledge
Reviewer instructions
```

Supabase supports pgvector directly in Postgres for embeddings/vector similarity, so we can initially keep this inside the database stack MA already uses rather than introducing another vector database. ([Supabase][2])

And access can later be restricted through Postgres/RLS patterns, which matters because knowledge must remain separated by client/user permissions. ([Supabase][3])

But don't RAG this:

```text
SELECT SUM(amount)
FROM transactions
WHERE client_id = ...
```

Use SQL.

---

# 10. Add these tables to MA

I would create a dedicated AI schema / tables.

```text
ai_jobs
ai_job_documents
ai_transactions
ai_agent_runs
ai_messages
ai_tool_calls
ai_outputs
ai_approvals
ai_exceptions
ai_memories
ai_feedback
```

### `ai_jobs`

Most important one.

```text
id
client_id
wip_job_id
job_type
period
current_stage
current_agent
status
created_by
created_at
```

For example:

```text
Client: ABC Limited
Job: Year End Accounts
Period: 2025-2026

Current stage:
PROCESSING_TRANSACTIONS

Agent:
BOOKKEEPER

Processed:
847 / 1,124

Exceptions:
34
```

This is what allows the AI to stop today and continue tomorrow.

---

# 11. Integrate it into MA immediately

Don't build some disconnected Python demo as the actual product.

The existing MA app already has:

* companies
* WIP jobs
* VAT
* personal tax
* deadlines
* staff assignments
* audit history

in Supabase. 

So add:

```text
MA Dashboard

Companies
WIP
VAT
Personal Tax
Clients
────────────
AI Accountant   ←
```

Inside:

```text
+ New AI Job

Client:
[ ABC Limited        ]

Job:
[ Year End Accounts  ]

Period:
[ 2025/26            ]

Current year file:
[ Upload ]

Prior year file:
[ Upload ]

[ Start Job ]
```

And then chat underneath:

```text
AI:

I've loaded ABC Limited.

1,247 transactions identified.
Previous-year accounts found.
ABC Limited is VAT registered.

I've started bookkeeping.

1,181 transactions have high-confidence classifications.
66 require review.

[View Exceptions]
```

That is much closer to what the client imagined.

The meeting explicitly settled on chat + document upload inside the MA dashboard as the initial interaction pattern. 

---

# 12. The chat and the workflow are NOT the same thing

Very important.

When someone says:

> “What jobs are overdue?”

That's the **MA Assistant**.

When someone says:

> “Start ABC Ltd's year-end accounts.”

The assistant invokes:

```text
start_accounting_job()
```

Then the orchestrator runs the workflow.

So:

```text
                  MA AI CHAT
                      │
       ┌──────────────┼──────────────┐
       │              │              │
      Q&A        Start job       Inspect job
       │              │              │
       ▼              ▼              ▼
    MA tools     Orchestrator      Job state
```

That separation will make the system far easier to maintain.

Vercel's AI SDK can fit the existing Next.js frontend and supports typed/tool-driven conversational workflows, including explicit approval of tool execution. ([AI SDK][4])

---

# 13. Tech stack — freeze this for POC

I would stop debating dozens of technologies and start with this.

| Component          | Use                           |
| ------------------ | ----------------------------- |
| Existing frontend  | Next.js / React               |
| AI chat frontend   | Vercel AI SDK                 |
| Existing data      | Supabase                      |
| AI job state       | Supabase/Postgres             |
| Vector/RAG         | Supabase pgvector             |
| AI service         | Python FastAPI                |
| Orchestration      | LangGraph                     |
| Excel              | pandas + openpyxl             |
| File storage       | private object storage        |
| LLM                | provider abstraction          |
| External data      | tool connectors               |
| Evaluation         | custom golden-job tests       |
| Production tracing | LangSmith/OpenTelemetry later |

LangGraph gives us the persistent execution + pause/resume behaviour needed for the approval stages rather than requiring us to invent that from scratch. ([Docs by LangChain][1])

---

# 14. Don't choose the final LLM yet

This one is important.

Don't say:

> “We're building it on Claude.”

or:

> “We're using GPT.”

yet.

Build an interface like:

```python
model.generate(...)
```

Then test candidate models against our historical jobs.

For example:

```text
20 difficult transactions

Model A: 17/20 correct
Model B: 19/20 correct
Model C: 15/20 correct
```

Then compare:

```text
accuracy
speed
cost
structured-output reliability
tool calling
reasoning
```

Choose based on **MA's accounting benchmark**, not marketing.

---

# 15. Your actual first 14 days

Here's how I would execute it.

### Days 1–2 — Domain definition

Get Qasim/Faroz.

Take the flowchart.

Go through **every diamond**.

Write exact rules.

Collect:

```text
2–3 completed jobs
Chart of accounts
VAT codes
Bookkeeping template
Review checklist
Prior-year files
Correct final outputs
```

**Deliverable:**

> Bookkeeping Agent Specification v1

---

### Days 3–4 — AI foundation

Set up:

```text
/ai-service
    /agents
    /workflows
    /tools
    /knowledge
    /models
    /evals
```

Implement:

```text
FastAPI
LangGraph
Supabase connection
model abstraction
ai_jobs
ai_agent_runs
ai_transactions
ai_exceptions
```

No fancy UI yet.

---

### Days 5–6 — Excel ingestion

Build:

```text
upload xlsx/csv
      ↓
identify columns
      ↓
normalise
      ↓
canonical transaction schema
```

For example:

```text
date
description
reference
debit
credit
amount
balance
```

Then parse previous-year workbook.

---

### Days 7–9 — Bookkeeping Agent v0.1

For each transaction:

```text
Get transaction
      ↓
Look at prior mappings
      ↓
Look at client memory
      ↓
Look at MA accounting rules
      ↓
Check existing accounts
      ↓
Select P&L / BS account
      ↓
Apply VAT treatment
      ↓
Return structured classification
      ↓
confidence score
```

Important:

```text
confidence > threshold
        ↓
accept draft

confidence < threshold
        ↓
EXCEPTION QUEUE
```

Don't force AI to guess.

---

### Day 10 — Trial balance

Generate:

```text
transaction classifications
        ↓
journal-style entries
        ↓
draft trial balance
```

Then deterministic validation:

```text
Debits == Credits
```

If not:

```text
STOP
↓
raise exception
```

Exactly as your flowchart says.

---

### Day 11 — Review tools

Implement the three flowchart checks:

```text
Debits = Credits?
Bank reconciliation agrees?
Accounts pages agree to TB?
```

Where a deterministic check is possible, use code.

Where judgement is required, use the Review Agent later.

---

### Day 12 — Historical evaluation

Give AI an old raw job.

Do not give it the human answer.

Run:

```text
AI result
vs
actual MA result
```

Calculate:

```text
categorisation accuracy
VAT accuracy
unmatched transactions
false classifications
exceptions
TB differences
token cost
runtime
```

---

### Day 13 — Fix

Analyse every failure.

Don't just change the system prompt.

Determine whether failure was:

```text
missing data
bad retrieval
bad rule
bad prompt
bad model
incorrect tool
ambiguous transaction
```

Then fix the correct layer.

---

### Day 14 — Demo

Client sees:

```text
ABC Limited
Year End 2025

1,247 transactions

1,164 correct automatically
56 exceptions
27 require human judgement

TB: Balanced ✓
Bank rec: Agreed ✓

Accuracy: 93.3%
Processing time: 8m 42s
Human review time: 22 mins
```

**That is a real POC.**

Not:

> “Look guys, I can chat with an accounting bot.”

---

# 16. After the Bookkeeping POC works

Then the build order becomes:

```text
BOOKKEEPING AGENT
       ↓
make reliable
       ↓
ACCOUNTS PREP AGENT
       ↓
human approval
       ↓
REVIEW AGENT
       ↓
human approval
       ↓
REPORTING AGENT
```

The reporting agent isn't actually shown in the screenshot you just sent — **the screenshot ends at client approval**.

The reporting agent comes from the meeting requirements, where the client described generating an email/PDF/WhatsApp-style client summary from the final accounts. 

So we should not mix those two requirements.

---

# 17. FreeAgent/Xero/Nylon come AFTER the core agent

Initially:

```text
CSV/XLSX
+
Prior accounts
+
MA database
+
MA rules
```

Once that works:

```text
FreeAgent ────────┐
Xero ─────────────┤
Nylon/HMRC ───────┤
Companies House ──┤
                  ▼
             TOOL LAYER
                  ▼
              AGENTS
```

The agents shouldn't care where data originates.

They call:

```text
get_bank_transactions()
```

Maybe today that reads Excel.

Tomorrow it reads FreeAgent.

The agent doesn't change.

**That abstraction is extremely important.**

---

# 18. What we need from the client NOW

This is basically the only immediate blocker now.

Get these things before we start implementation:

1. **Two or three fully completed historical jobs.**
2. **Blank/current working-file template.**
3. **Previous-year file for each test job.**
4. **Chart of accounts/account codes.**
5. **VAT codes and exact VAT decision rules.**
6. **How they choose P&L vs Balance Sheet categories.**
7. **When a new account should be created.**
8. **How transaction ↔ invoice/supporting-document matching works.**
9. **Exact bank reconciliation procedure.**
10. **What “pages agree to TB” specifically means in their Excel process.**
11. **Internal review checklist.**
12. **Examples of reviewer queries/corrections.**

And then one thing that would help enormously:

> **Ask Qasim to walk you through ONE real completed job from the very first source document all the way to “sent to client for approval,” using this flowchart.**

Record that call.

That one walkthrough will probably give us more implementation information than another general two-hour AI discussion.

---

# 19. So your next three moves are very simple

**Move 1 — Tomorrow / next client discussion**

Don't discuss LLM providers.

Don't discuss DigitalOcean.

Don't discuss RAG pricing.

Go through the **12 accounting-rule questions above**.

---

**Move 2 — Get one perfect historical job**

One complete:

```text
INPUT → HUMAN PROCESS → FINAL ANSWER
```

That becomes our first golden test.

---

**Move 3 — Then we start POC engineering**

First coding target:

```text
Upload current transactions
+
Upload prior-year workbook
        ↓
Create AI job
        ↓
Normalise transactions
        ↓
Bookkeeping Agent
        ↓
Classification + VAT
        ↓
Exceptions
        ↓
Draft TB
        ↓
Validation
        ↓
Excel output
```

**That is the first milestone.**

Everything else can wait.

And yes bro — **with the flowchart you just sent, the MA codebase context, transcript and meeting notes, I now think we have enough context to move out of “what are we building?” and into actual technical design.**

The one significant missing piece is no longer architecture.

It's **accounting domain rules and real historical examples**.

Once you give me those — even gradually — we can start defining **Agent 1 at implementation level: exact inputs, exact outputs, tool definitions, DB schema, LangGraph nodes, prompts, confidence logic and evaluation tests.**

[1]: https://docs.langchain.com/oss/python/langgraph/interrupts?utm_source=chatgpt.com "Interrupts - Docs by LangChain"
[2]: https://supabase.com/docs/guides/database/extensions/pgvector?utm_source=chatgpt.com "pgvector: Embeddings and vector similarity"
[3]: https://supabase.com/docs/guides/ai/rag-with-permissions?utm_source=chatgpt.com "RAG with Permissions | Supabase Docs"
[4]: https://ai-sdk.dev/docs/ai-sdk-core/tools-and-tool-calling?utm_source=chatgpt.com "AI SDK Core: Tool Calling"


earlier plan:
Bro, yes — **now we actually have enough context to design version 0.1 of the real system.** And after reading the meeting summary, transcript, and MA codebase context, I would change a few assumptions from the meeting before we start coding.

# 1. What we are actually building

I would describe this project as:

> **An AI accounting operations platform embedded inside MA Associates, using a stateful orchestrator to coordinate specialised accounting agents, firm/client knowledge, external data sources, deterministic accounting logic and human approvals.**

Not:

> “We are training our own LLM.”

At least **not initially**.

The client wants four distinct specialist stages: bookkeeping, accounts preparation, review, and client reporting, with two human approval points. 

So conceptually:

```text
                     MA ASSOCIATES
                          │
                 ┌────────▼────────┐
                 │   AI Assistant   │
                 │ Chat / Job UI    │
                 └────────┬────────┘
                          │
                 ┌────────▼────────┐
                 │   ORCHESTRATOR   │
                 │ Job State/Router │
                 └────────┬────────┘
                          │
          ┌───────────────┼────────────────┐
          │               │                │
     MA Database      Job documents    External tools
     / WIP            PDF/XLSX/CSV     FreeAgent
     / Clients        Prior accounts   Xero
     / Deadlines      Invoices         Nylon/HMRC
          │               │                │
          └───────────────┬────────────────┘
                          │
                  KNOWLEDGE / TOOLS
                          │
              ┌───────────▼───────────┐
              │  1. BOOKKEEPING AGENT │
              └───────────┬───────────┘
                          ↓
              ┌───────────────────────┐
              │ 2. ACCOUNTS PREP      │
              │        AGENT          │
              └───────────┬───────────┘
                          ↓
                 👤 Human approval #1
                          ↓
              ┌───────────────────────┐
              │ 3. REVIEW AGENT       │
              │ Reconcile / validate  │
              └───────────┬───────────┘
                          ↓
                 👤 Human approval #2
                          ↓
              ┌───────────────────────┐
              │ 4. REPORTING AGENT    │
              │ Email/PDF/WhatsApp    │
              └───────────┬───────────┘
                          ↓
                       COMPLETE
```

That closely matches what the client described in the meeting. 

---

# 2. Is this a router pattern?

**Partially. But I wouldn't build it as only a router.**

There are three related concepts.

| Pattern              | What it does                                             | MA use          |
| -------------------- | -------------------------------------------------------- | --------------- |
| Router               | Classifies a request and sends it somewhere              | Useful          |
| Supervisor           | LLM dynamically decides which agents to invoke           | Useful for chat |
| Workflow/state graph | Explicitly controls which steps happen and in what order | **Critical**    |

LangChain's current documentation makes exactly this distinction: a router is generally a classification/dispatch step, while a supervisor maintains context and dynamically coordinates subagents. LangGraph also supports custom workflows mixing deterministic code with LLM-driven steps. ([Docs by LangChain][1])

For MA, I'd use a **hybrid**.

```text
User request
     ↓
Supervisor / Chat Agent
     ↓
Job Router
     ↓
Accounting Workflow Graph
     ↓
Specialist agents
```

The **workflow graph**, rather than an LLM deciding everything, controls the accounting process.

That's important because we don't want:

> “Bookkeeping agent thinks maybe I'll skip reconciliation and ask the reporting agent.”

No. 😭

The state machine says:

```text
BOOKKEEPING
   ↓
ACCOUNTS_PREPARATION
   ↓
HUMAN_REVIEW_1
   ↓
AI_REVIEW
   ↓
HUMAN_REVIEW_2
   ↓
REPORTING
   ↓
COMPLETE
```

The AI has freedom **inside a controlled box**.

That's much safer for accounting.

LangGraph is currently designed specifically around state, nodes, edges, persistent execution and human-in-the-loop pauses, which fits this project extremely well. ([Docs by LangChain][2])

---

# 3. Very important: what is the source of truth?

You said:

> MA Associates project/repo must be the source of truth.

I'd slightly change that.

### Engineering source of truth

**MA Associates repository**

It tells us:

* application structure
* business logic
* database models
* workflows
* permissions
* available APIs

### Operational source of truth

**MA Supabase database**

It currently contains companies, WIP jobs, VAT, personal tax, clients, staff assignments, deadlines and workflow information. 

### Accounting evidence source of truth

Original:

```text
Bank statements
Invoices
CSV/XLSX
Prior-year accounts
FreeAgent
Xero
Client documents
```

### Firm-knowledge source of truth

Approved:

```text
MA accounting SOPs
Templates
Accounting rules
Review checklists
Human corrections
Client-specific rules
Tax guidance
Nylon/HMRC knowledge
```

### LLM

**NOT source of truth.**

The LLM is:

> reasoning + interpretation + tool selection + language generation.

This one architectural distinction will massively reduce hallucination.

---

# 4. We do NOT “train the LLM” initially

This is another thing I would correct from our meeting discussion.

When Qasim teaches the system:

> “For this type of transaction, MA normally does X.”

we shouldn't immediately change model weights.

Initially, “training MA AI” actually consists of:

```text
Base foundation model
        +
System instructions
        +
Agent-specific instructions
        +
Accounting workflow
        +
MA knowledge/RAG
        +
Client memory
        +
Prior examples
        +
Approved corrections
        +
Tools
        +
Evaluation dataset
```

Only much later do we consider **fine-tuning**.

And training a foundation model from scratch makes basically zero sense here.

The intelligence MA owns is not the underlying language model.

The valuable proprietary asset becomes:

> **MA's accounting workflows + examples + historical decisions + templates + prompts + tools + evaluation data + client-specific knowledge.**

That's what makes their AI accountant uniquely theirs.

---

# 5. RAG — but we're going to use it differently than I explained in the meeting

This is important.

We **should not RAG everything**.

For example, if we have 5,000 bank transactions:

```text
transaction_id
date
description
amount
category
supplier
account
```

we should NOT embed 5,000 rows and ask semantic search:

> “What were our expenses?”

That's structured data.

Use:

**SQL / Python / deterministic calculations.**

RAG is best for:

```text
Accounting manuals
MA process documentation
Previous accounting notes
Client correspondence
Prior-year commentary
Tax guidance
Policies
Unstructured PDFs
Review instructions
Client-specific knowledge
```

Supabase already supports pgvector inside Postgres for embeddings/vector similarity, including access-control patterns for RAG. ([Supabase][3])

So our retrieval architecture becomes:

```text
                 QUESTION
                     │
              Orchestrator
             ┌───────┴─────────┐
             │                 │
       Structured?        Unstructured?
             │                 │
            SQL               RAG
        MA Supabase         pgvector
        FreeAgent API      Documents
        Xero API           SOPs
        Excel data         Notes
             │                 │
             └────────┬────────┘
                      ↓
                     LLM
```

Much better.

---

# 6. Memory needs three levels

Don't just create one enormous “memory”.

### Job memory

Everything relevant to:

> ABC Limited — Year End Accounts — 2025/26

Temporary/stateful.

### Client memory

Persistent knowledge:

> ABC Limited usually pays AWS monthly.
> XYZ Consulting is a director-related transaction.
> Last year this expense mapped to 4020.

### Firm memory

MA-wide:

> MA Associates bookkeeping methodology
> Accounts templates
> Review checklist
> Treatment rules
> Reporting style

LangGraph distinguishes thread-level/short-term state from longer-term application memory, which maps nicely to this design. ([Docs by LangChain][4])

And every piece of memory needs metadata:

```text
firm_id
client_id
job_id
document_id
source
created_at
approved_by
confidence
```

That prevents one client's information leaking into another client's job.

The meeting explicitly called out the need to keep multiple clients/jobs separate. 

---

# 7. Tech stack I would use

Given what MA already uses, I **would not rewrite the application**.

The current MA app is Next.js 15 + React 19 + TypeScript + Supabase and Vercel. 

I'd build around it:

| Layer                 | Recommendation                          |
| --------------------- | --------------------------------------- |
| MA frontend           | Existing Next.js                        |
| AI chat UI            | Vercel AI SDK                           |
| Main MA DB            | Existing Supabase Postgres              |
| Vector store          | Supabase + pgvector                     |
| Document storage      | Private Supabase Storage                |
| Agent service         | **Python + FastAPI**                    |
| Orchestration         | **LangGraph**                           |
| Structured processing | Python / Pandas / OpenPyXL              |
| Model                 | Provider abstraction initially          |
| Model hosting/API     | Evaluate DigitalOcean + major providers |
| Agent state           | Postgres                                |
| Tracing               | LangSmith initially or OpenTelemetry    |
| Background jobs       | Worker/queue later                      |
| Existing app hosting  | Vercel                                  |
| AI runtime            | DigitalOcean initially                  |

Vercel's AI SDK supports streaming chat and tool-call approval patterns in Next.js, so it fits the existing MA frontend nicely. ([AI SDK][5])

DigitalOcean currently provides serverless and dedicated inference options, so we can benchmark there without locking the architecture to a particular model. ([DigitalOcean][6])

And **don't promise the $25/month figure yet**. DigitalOcean pricing depends on model usage plus things such as knowledge bases/guardrails, so we should measure real cost per accounting job during the POC. ([DigitalOcean][7])

---

# 8. The MA dashboard becomes the control centre

The meeting already landed on this: chat/document upload should live inside the existing MA dashboard. 

I'd add something like:

```text
MA Associates

Companies
WIP
VAT
Personal Tax
Clients
Executive
AI ACCOUNTANT  ← NEW
```

Opening it gives you:

```text
┌──────────────────────────────────────────┐
│ MA AI                                    │
│                                          │
│ Client: ABC Limited                      │
│ Job: Year End Accounts 2025/26           │
│ Status: Bookkeeping Agent Processing     │
│                                          │
│ [ Chat ] [ Documents ] [ Activity ]      │
│ [ Approvals ] [ Outputs ]                │
│                                          │
│ "I've analysed 1,248 transactions."      │
│ "47 require review."                     │
│ "Would you like to inspect them?"        │
│                                          │
│          [ Review exceptions ]           │
└──────────────────────────────────────────┘
```

And importantly, the user doesn't necessarily need to say:

> “Use bookkeeping agent.”

They say:

> “Start the year-end accounts for ABC Ltd.”

The system knows:

```text
job_type = year_end
current_state = NEW

→ Intake
→ Bookkeeping
→ Accounts Prep
→ Review...
```

---

# 9. We need an actual AI job entity

This should be fundamental.

Something like:

```text
ai_jobs

id
client_id
wip_job_id
job_type
accounting_period
status
current_agent
current_stage
created_by
created_at
updated_at
```

Then supporting tables such as:

```text
ai_documents
ai_messages
ai_runs
ai_agent_runs
ai_tool_calls
ai_artifacts
ai_approvals
ai_memories
ai_feedback
ai_evaluations
```

Every operation becomes auditable.

So six months later we can answer:

> Why did AI classify transaction #482 as travel?

And see:

```text
Source: HSBC statement
Description: UBER BV
Agent: Bookkeeping v0.8
Rule retrieved: MA-BOOK-027
Prior client mapping: Travel
Confidence: 92%
Human correction: None
```

**That level of traceability is what will make this production-worthy.**

---

# 10. The first POC should be MUCH smaller

The meeting target was a testable bookkeeping agent within **10–14 days**, using 2–3 sources. 

I think that remains reasonable **for a POC**, provided we deliberately limit it.

### POC v0.1

```text
ONE job type
↓
Year-end bookkeeping

INPUT
↓
Current-year CSV/XLSX bank transactions
Previous-year Excel workbook
MA client context

PROCESS
↓
Normalise transaction data
Retrieve previous mappings
Analyse transactions
Categorise transactions
Flag uncertain transactions
Produce bookkeeping output

OUTPUT
↓
Structured Excel workbook
Exceptions list
Confidence score
Processing summary

HUMAN
↓
Review corrections

MEMORY
↓
Store approved corrections for future jobs
```

No Xero initially.

No FreeAgent initially.

No Nylon initially.

No automatic emails.

No four-agent orchestration.

No autonomous actions.

**Just prove that one AI bookkeeper can take a historical real job and reproduce a human-quality result.**

That is our foundation.

---

# 11. How we test whether the AI is actually good

We need old completed jobs.

Not random prompts.

For example:

```text
INPUT:
2024 bank transactions
2023 accounts
client documentation

EXPECTED RESULT:
Actual bookkeeping file produced by MA
```

Hide the final answer from the agent.

Run the agent.

Then compare:

| Metric                     | Measure                 |
| -------------------------- | ----------------------- |
| Transaction categorisation | % matching human result |
| Reconciliation             | Pass/fail               |
| Missing transactions       | Count                   |
| Incorrect classifications  | Count                   |
| Unsupported assumptions    | Count                   |
| Human corrections          | %                       |
| Token/model cost           | £ per job               |
| Runtime                    | minutes/job             |
| Review time saved          | minutes/hours           |

This becomes our **golden evaluation set**.

And every time we change the prompt/model/RAG:

```text
v0.1 → 82%
v0.2 → 89%
v0.3 → 94%
```

Now we're genuinely “training the system” instead of judging it by whether a conversation looks impressive.

---

# 12. One serious issue in the current MA app

Before **production**, we need a security phase.

Your codebase notes say the current authentication uses plaintext passwords, localStorage/cookie sessions and client-side guards. 

That cannot be the security boundary for an AI system accessing things like UTRs, Companies House authentication codes, accounting documents and financial records. The codebase itself already identifies those fields as sensitive. 

For POC:

**isolated dev/test environment.**

Before production:

**proper server authentication + server-side permissions + secrets + audit logging.**

Also, we should **never give the LLM unrestricted Supabase service-role access**. Supabase documents that elevated secret/service-role credentials bypass RLS, so those must remain server-side. ([Supabase][8])

Instead, the LLM gets tools like:

```text
get_client()
get_wip_job()
get_transactions()
get_previous_accounts()
save_draft_output()
request_approval()
```

NOT:

```text
execute_any_sql()
```

Huge difference.

---

# 13. Our development roadmap

I'd currently structure it like this:

| Phase                          | Deliverable                                       |    Approx. |
| ------------------------------ | ------------------------------------------------- | ---------: |
| **0 — Discovery/architecture** | workflow, schemas, sample jobs, eval set          |   3–5 days |
| **1 — POC**                    | one bookkeeping agent                             | 10–14 days |
| **2 — Bookkeeper v1**          | MA integration, memory, RAG, proper UI            |  2–4 weeks |
| **3 — Accounts Prep**          | second specialist + approval #1                   |  2–4 weeks |
| **4 — Review Agent**           | reconciliation/checklist + approval #2            |  2–3 weeks |
| **5 — Reporting**              | client summaries/reports                          |  1–2 weeks |
| **6 — Integrations**           | FreeAgent/Xero/Nylon                              |  iterative |
| **7 — Production hardening**   | auth, audit, monitoring, permissions, evaluations |  2–4 weeks |
| **Later**                      | proactive deadlines/chasing/autonomous workflows  |    ongoing |

Those aren't commitments yet. Once we have the client's actual workflow diagram and 2–3 historical jobs, we can estimate properly.

---

# 14. The immediate next step

**Do not start with LangGraph code yet.**

First we need to convert their real accounting process into a machine-readable workflow.

And fortunately, the meeting itself identified exactly that as the immediate requirement: detailed inputs, outputs and process steps for the first agent. 

The next context you give me should therefore be exactly what you mentioned:

**the client's workflow screenshot/flowchart**, plus any further notes you have.

Then, as you keep feeding me context, we're going to progressively build one living design:

> **MA AI Architecture v0.1 → Agent contracts → Bookkeeping workflow → Data model → RAG/memory design → prompt architecture → evaluation strategy → API/tool contracts → POC backlog → actual implementation.**

And crucially, we **won't design the other agents prematurely**. We'll establish the shared foundation and make the Bookkeeping Agent genuinely work first, which is also exactly the phased approach the client asked for. 

This is absolutely buildable. The key is that we're **not really building “an LLM” anymore — we're building an accounting operating system where LLMs are one of the reasoning engines inside it.**

[1]: https://docs.langchain.com/oss/python/langchain/multi-agent/router?utm_source=chatgpt.com "Router - Docs by LangChain"
[2]: https://docs.langchain.com/oss/python/langgraph/graph-api?utm_source=chatgpt.com "Graph API overview - Docs by LangChain"
[3]: https://supabase.com/docs/guides/database/extensions/pgvector?utm_source=chatgpt.com "pgvector: Embeddings and vector similarity"
[4]: https://docs.langchain.com/oss/python/concepts/memory?utm_source=chatgpt.com "Memory overview - Docs by LangChain"
[5]: https://ai-sdk.dev/docs/introduction?utm_source=chatgpt.com "AI SDK by Vercel"
[6]: https://docs.digitalocean.com/products/inference/?utm_source=chatgpt.com "Inference | DigitalOcean Documentation"
[7]: https://docs.digitalocean.com/products/inference/details/pricing/?utm_source=chatgpt.com "Inference Pricing | DigitalOcean Documentation"
[8]: https://supabase.com/docs/guides/database/postgres/roles?utm_source=chatgpt.com "Postgres Roles | Supabase Docs"
