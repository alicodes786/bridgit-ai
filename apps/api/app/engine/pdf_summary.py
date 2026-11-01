"""One-page PDF job summary (Phase 1 output)."""

from __future__ import annotations

from fpdf import FPDF


def _latin(text: object) -> str:
    s = (
        str(text or "")
        .replace("\u00a3", "GBP ")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u00a0", " ")
    )
    return "".join(ch if 32 <= ord(ch) <= 126 or ch in "\n" else "?" for ch in s)


def build_summary_pdf(job: dict) -> bytes:
    txns = job.get("transactions") or []
    exceptions = job.get("exceptions") or []
    coded = 0
    for row in txns:
        classes = row.get("ai_transaction_classifications") or []
        klass = classes[0] if classes else {}
        if klass and not klass.get("needs_review"):
            coded += 1

    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    width = pdf.epw
    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(width, 10, "Bridgit - job summary")
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(width, 7, _latin(f"Job: {job.get('title') or ''}"))
    pdf.multi_cell(width, 7, _latin(f"Client: {job.get('client_name') or ''}"))
    pdf.multi_cell(width, 7, _latin(f"Status: {job.get('status') or ''}"))
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.multi_cell(width, 8, "Counts")
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(width, 7, f"Transactions: {len(txns)}")
    pdf.multi_cell(width, 7, f"Auto / confirmed coded: {coded}")
    pdf.multi_cell(width, 7, f"Open questions: {len(exceptions)}")
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.multi_cell(width, 8, "Open questions")
    pdf.set_font("Helvetica", size=10)
    if not exceptions:
        pdf.multi_cell(width, 6, "None. Ready for accountant review.")
    else:
        for i, item in enumerate(exceptions[:18], start=1):
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(width, 5, _latin(f"{i}. {item.get('question') or ''}"))
        if len(exceptions) > 18:
            pdf.multi_cell(width, 6, f"... and {len(exceptions) - 18} more")
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 9)
    pdf.multi_cell(
        width,
        5,
        "Nothing is submitted to HMRC. This is a working summary for human review. "
        "Trial balance and bank rec live in the Excel working file. "
        "Every Accept/Override is saved as a client mapping except duplicate keep-both / repeat flags.",
    )
    return bytes(pdf.output())
