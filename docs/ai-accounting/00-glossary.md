# 0. Glossary — plain-English definitions

Terms used across these documents, explained simply. Useful for you when explaining
this to the client or anyone else non-technical.

- **Spike** — a short, time-boxed technical experiment done purely to answer one
  specific question before committing to an approach. It is throwaway code, not
  production code, has a fixed deadline (e.g. "2-3 days"), and ends with a decision,
  not a shippable feature. Example: "spend 2 days building a tiny prototype of both
  option A and option B, then decide which one to actually build for real." We
  originally planned a spike to decide between a custom state machine and LangGraph —
  you've now made that call directly (custom), so that spike is no longer needed. See
  [04-roadmap-and-deliverables.md](./04-roadmap-and-deliverables.md).

- **POC (Proof of Concept)** — the smallest version of the system that proves the core
  idea actually works, using real data, before investing in the full product. Its job
  is to answer "does this work at all," not to be feature-complete or beautiful.

- **MVP (Minimum Viable Product)** — the smallest version that's actually usable by
  real staff on real client work day-to-day, not just a proof it works.

- **Agent** — in this project, a specific piece of AI logic that gathers information
  through tools, reasons about a narrow task (e.g. "which account does this
  transaction belong to"), and returns a structured answer. Not a general-purpose
  chatbot — each agent has a specific, narrow job.

- **Orchestration / Orchestrator** — the layer of code that decides what happens next
  in the overall process (which stage, which agent, when to pause for a human). In
  this project it's a deterministic state machine, not an AI making that decision.

- **State machine** — a system with a fixed set of named stages (e.g.
  "Bookkeeping," "Trial Balance," "Review") and fixed rules about which stage can move
  to which next stage. Guarantees the process always follows the same controlled
  sequence.

- **RAG (Retrieval-Augmented Generation)** — instead of an AI model answering purely
  from what it was trained on, the system first retrieves relevant real
  documents/notes/rules and gives them to the model as context, so its answer is
  grounded in real material rather than guessed.

- **Vector database / embeddings** — a way of storing text so that "similar meaning"
  text can be found quickly (used for RAG). An embedding is a numeric representation of
  a piece of text's meaning; the vector database finds the closest matches.
  `pgvector` is the specific tool we're using — it's an extension that adds this
  capability directly into the existing Postgres database, so no separate database
  product is needed.

- **Fine-tuning** — actually retraining part of an AI model on your own examples so its
  behaviour permanently changes. This is different from just giving the model
  instructions/context at request time. We are **not** doing this in the POC or MVP —
  see [02-architecture.md](./02-architecture.md).

- **Token / token cost** — LLMs charge by "tokens" (roughly, chunks of text — a bit
  less than one word each on average). Cost = (tokens in your prompt + tokens in the
  response) x the provider's price per token. This is why processing 2,000
  transactions in one job matters for cost — more transactions/text = more tokens.

- **Confidence score** — a number an AI model reports alongside its answer, meant to
  indicate how sure it is. Important caveat (see
  [02-architecture.md](./02-architecture.md) §2.9): this number is not automatically
  trustworthy just because the model says it — it needs to be checked against real
  outcomes ("calibrated") before you can rely on a threshold like "auto-accept anything
  above 90% confidence."

- **Human-in-the-loop** — a design where the system pauses at defined points and
  requires a real person to review/approve before continuing. Central to this whole
  project — the client explicitly does not want a fully autonomous system.

- **Tool / tool calling** — a specific, named function an AI agent is allowed to call
  (e.g. `get_transactions()`) instead of having free/unrestricted access to a database.
  Keeps the AI's capabilities narrow and auditable.

- **Audit trail / traceability** — a complete record of every action the system took
  (which agent ran, what data it looked at, what it decided, who approved it) so any
  decision can be explained after the fact.

- **Golden dataset / golden evaluation set** — a set of real, already-completed jobs
  used as a test suite: give the AI the inputs, withhold the real human answer, run it,
  and compare. Used to measure whether the system is actually accurate, and to catch
  regressions when anything changes.

- **Trial Balance (TB)** — an accounting report listing every account and its balance,
  used to check that total debits equal total credits before accounts are finalized.

- **Reconciliation (bank rec)** — the process of checking that the transactions
  recorded in the books match the bank's own statement/balance.

- **LLM provider / model provider** — a company offering access to an AI model over an
  API, e.g. OpenAI (GPT), Anthropic (Claude), Google (Gemini). You call their API and
  pay per use; you do not run the model yourself.
