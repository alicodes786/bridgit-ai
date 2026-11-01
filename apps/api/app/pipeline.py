"""Pipeline stages shown on the Bridgit board.

Copy is written for a walkthrough with MA Associates, not for developers.
"""

STAGES = [
    {
        "id": "intake",
        "title": "Know the job, then ask for missing papers (Intake)",
        "meaning": "Client, job type, period, then what is here vs missing.",
        "status": "live",
        "does": (
            "Before coding, Bridgit records what kind of job this is and the dates. "
            "It lists bank statements, last year's file, and invoices that are missing. "
            "It asks — it does not refuse to start. Same for VAT and year-end."
        ),
        "not": "Partial packs are allowed. Gaps stay on the questions list.",
    },
    {
        "id": "ingest",
        "title": "Read the bank file (Ingest)",
        "meaning": "Statement in, clean lines out.",
        "status": "live",
        "does": (
            "Bridgit reads a bank PDF, CSV, or Excel and turns it into the same simple rows: "
            "date, description, amount, money in or out, and which page it came from."
        ),
        "not": "Works for more than one bank. Starling PDFs were the first real files; CSV and Excel cover typical UK exports.",
    },
    {
        "id": "duplicates",
        "title": "Spot duplicates (Duplicates)",
        "meaning": "Same day, amount, and description is flagged.",
        "status": "live",
        "does": (
            "If two lines on this job look identical (same date, amount, and description), "
            "Bridgit stops and asks: keep both, or is one a repeat? It never posts a duplicate quietly."
        ),
        "not": None,
    },
    {
        "id": "mapping",
        "title": "Use last year's coding (Prior mapping)",
        "meaning": "Known suppliers are coded with no AI.",
        "status": "live",
        "does": (
            "If this client has already coded that description (for example Amazon or Dell), "
            "Bridgit applies the same account and VAT. No guessing. Koliqi already has 77 saved pairs."
        ),
        "not": "Lines marked REVIEW or personal still come back as a question. They are not auto-applied. Year-end jobs (Hit Hunters) code by payee from last year, not the CSV Category column.",
    },
    {
        "id": "firm_rules",
        "title": "Firm VAT and account rules (Firm rules)",
        "meaning": "MA Associates' own rules, in software.",
        "status": "live",
        "does": (
            "Once we have the chart of accounts and VAT rules, Bridgit will apply them in code: "
            "which VAT code, profit and loss vs balance sheet, when to open a new account. "
            "This is not the AI deciding."
        ),
        "not": "MA does not maintain a coded chart of accounts. Client rules (Hit Hunters: code by payee, director rem this year) live per client. VAT 'when to use which code' still open.",
    },
    {
        "id": "llm",
        "title": "Ask AI when it is new (LLM judgement)",
        "meaning": "A proposal with a confidence score.",
        "status": "live",
        "does": (
            "If there is no saved coding and no firm rule yet, Bridgit asks the AI to propose "
            "an account and VAT code. High confidence can auto-code. Low confidence becomes a question."
        ),
        "not": "The AI never files anything. A human still reviews the working file.",
    },
    {
        "id": "exceptions",
        "title": "Questions for the accountant (Exceptions)",
        "meaning": "Unsure lines become specific questions.",
        "status": "live",
        "does": (
            "Each flagged line has a real question, a proposed account, and Accept or Override. "
            "The answer is saved for this client, so Bridgit does not ask the same thing next time."
        ),
        "not": "These buttons are for an accountant. Do not guess if you are not coding the job.",
    },
    {
        "id": "excel",
        "title": "Write the working Excel (Excel writer)",
        "meaning": "MA Associates' VAT workbook shape, filled in.",
        "status": "live",
        "does": (
            "Bridgit writes Banking Analysis, Bank Payment Analysis, and Bank Reconciliation "
            "(opening and closing) in the format the team already uses. The file updates after each answer."
        ),
        "not": "Official blank template from MA Associates still optional.",
    },
    {
        "id": "gates",
        "title": "Bank rec must agree (Hard gates)",
        "meaning": "A software check, not an AI opinion.",
        "status": "live",
        "does": (
            "Opening plus receipts minus payments must match the statement closing. "
            "If it does not, the job stays as Needs your input. The accountant never gets an unbalanced file as 'done'."
        ),
        "not": "A full trial balance against ledger codes waits on the chart of accounts.",
    },
    {
        "id": "pdf_summary",
        "title": "One-page PDF summary (PDF summary)",
        "meaning": "A cover sheet, not the books.",
        "status": "live",
        "does": (
            "A short PDF: how many lines, how many coded, how many questions still open. "
            "Useful for a glance. The Excel is the real working file."
        ),
        "not": "Nothing is submitted to HMRC from this page.",
    },
    {
        "id": "product_ui",
        "title": "Bridgit UI",
        "meaning": "The polished accountant product comes next.",
        "status": "next",
        "does": (
            "Later: a dedicated Bridgit site with client picker, job status, a question table, "
            "and downloads. This page is the working engine so you can see progress now."
        ),
        "not": "This screen is a preview of the engine, not the final look and feel.",
    },
]
