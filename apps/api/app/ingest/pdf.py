"""PDF bank statements → canonical rows.

Not a Starling-only product. Strategy, in order:
1. If the PDF looks like a UK current-account layout (DATE / TYPE / TRANSACTION / IN / OUT)
   — Starling and similar — parse by column x-position. First proven file: Koliqi Starling PDFs.
2. Else try table extraction (many bank PDFs are real tables).
3. Else fall back to dated text lines.
"""

from __future__ import annotations

import re
from collections import defaultdict
from decimal import Decimal
from io import BytesIO

import pdfplumber

from app.ingest._util import parse_date, parse_money
from app.models import CanonicalTxn, ParseResult

_DATE_TOKEN = re.compile(r"^\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}$")
_NOISE = (
    "starlingbank",
    "customer service",
    "financial services compensation",
    "authorised by the prudential",
    "date range applicable",
    "interest rate paid",
    "end of day",
    "opening balance",
    "closing balance",
    "www.starlingbank.com",
)

# Right-edge (x1) of amount columns on A4 Starling-style statements.
_IN_X1_MAX = 470
_OUT_X1_MAX = 515


def parse_pdf(content: bytes, *, file_name: str = "") -> ParseResult:
    with pdfplumber.open(BytesIO(content)) as pdf:
        if _is_starling_style(pdf):
            return _parse_starling_style(pdf, file_name=file_name)
        table_result = _parse_tables(pdf, file_name=file_name)
        if table_result.transactions:
            return table_result
        return _parse_text_lines(pdf, file_name=file_name)


def _is_starling_style(pdf) -> bool:
    if not pdf.pages:
        return False
    sample = (pdf.pages[0].extract_text() or "").upper()
    has_cols = "DATE" in sample and "TRANSACTION" in sample and "IN" in sample and "OUT" in sample
    return has_cols or "STARLING" in sample


def _page_rows(page) -> list[list[dict]]:
    grouped: dict[int, list] = defaultdict(list)
    for word in page.extract_words():
        grouped[round(word["top"])].append(word)
    return [sorted(grouped[y], key=lambda w: w["x0"]) for y in sorted(grouped)]


def _parse_starling_style(pdf, *, file_name: str) -> ParseResult:
    txns: list[CanonicalTxn] = []
    opening = closing = None
    warnings: list[str] = []
    current: CanonicalTxn | None = None
    row_no = 0

    for page_index, page in enumerate(pdf.pages, start=1):
        text = page.extract_text() or ""
        opening = opening or _balance_after(text, "OPENING BALANCE")
        closing = _balance_after(text, "CLOSING BALANCE") or closing

        for words in _page_rows(page):
            if not words:
                continue
            first = words[0]["text"]
            line = " ".join(w["text"] for w in words)
            if _is_noise(line):
                current = None
                continue

            if _DATE_TOKEN.match(first) and words[0]["x0"] < 70:
                parsed = _starling_txn_row(words, page_index)
                if parsed is None:
                    current = None
                    continue
                parsed.description = _clean_desc(parsed.description)
                row_no += 1
                parsed.source_row = row_no
                txns.append(parsed)
                current = parsed
                continue

            if current and words[0]["x0"] > 70:
                extra = " ".join(
                    w["text"] for w in words if 80 <= w["x0"] < 400
                ).strip()
                extra = _clean_desc(extra)
                if extra and not _is_noise(extra):
                    current.description = (current.description + " " + extra).strip()

    if not txns:
        warnings.append(f"starling-style parser found no rows in {file_name or 'pdf'}")

    return ParseResult(
        transactions=txns,
        parser="pdf-starling-style",
        opening_balance=opening,
        closing_balance=closing,
        warnings=warnings,
    )


def _starling_txn_row(words: list[dict], page: int) -> CanonicalTxn | None:
    txn_date = parse_date(words[0]["text"])
    if txn_date is None:
        return None
    type_parts = [w["text"] for w in words if 80 <= w["x0"] < 175]
    desc_parts: list[str] = []
    in_amt = out_amt = None
    for word in words[1:]:
        amount = parse_money(word["text"])
        if amount is not None and word["x0"] > 350:
            x1 = word["x1"]
            if x1 < _IN_X1_MAX:
                in_amt = amount
            elif x1 < _OUT_X1_MAX:
                out_amt = amount
            continue
        if 175 <= word["x0"] < 400:
            desc_parts.append(word["text"])
    if not type_parts or (in_amt is None and out_amt is None):
        return None
    if in_amt is not None:
        amount, debit_credit = in_amt, "credit"
    else:
        amount, debit_credit = out_amt, "debit"
    return CanonicalTxn(
        txn_date=txn_date,
        description=" ".join(desc_parts).strip(),
        amount=amount,
        debit_credit=debit_credit,
        payment_type=" ".join(type_parts),
        source_page=page,
        reference=" ".join(type_parts),
    )


def _parse_tables(pdf, *, file_name: str) -> ParseResult:
    txns: list[CanonicalTxn] = []
    row_no = 0
    for page_index, page in enumerate(pdf.pages, start=1):
        for table in page.extract_tables() or []:
            if not table:
                continue
            header_idx, mapping = _header_map(table[0])
            body = table[1:] if header_idx else table
            for raw in body:
                parsed = _row_from_cells(raw, mapping, page_index)
                if parsed is None:
                    continue
                row_no += 1
                parsed.source_row = row_no
                txns.append(parsed)
    return ParseResult(
        transactions=txns,
        parser="pdf-table",
        warnings=[] if txns else [f"no tables parsed from {file_name or 'pdf'}"],
    )


def _parse_text_lines(pdf, *, file_name: str) -> ParseResult:
    txns: list[CanonicalTxn] = []
    row_no = 0
    for page_index, page in enumerate(pdf.pages, start=1):
        for line in (page.extract_text() or "").splitlines():
            if _is_noise(line):
                continue
            parts = line.split()
            if not parts or not _DATE_TOKEN.match(parts[0]):
                continue
            txn_date = parse_date(parts[0])
            money_tokens = [parse_money(p) for p in parts if parse_money(p) is not None]
            if txn_date is None or not money_tokens:
                continue
            amount = money_tokens[0]
            desc = " ".join(parts[1:])
            for token in parts:
                if parse_money(token) is not None:
                    desc = desc.replace(token, "").strip()
            row_no += 1
            debit_credit = "debit" if amount < 0 else "credit"
            txns.append(
                CanonicalTxn(
                    txn_date=txn_date,
                    description=desc,
                    amount=abs(amount),
                    debit_credit=debit_credit,
                    source_page=page_index,
                    source_row=row_no,
                )
            )
    return ParseResult(
        transactions=txns,
        parser="pdf-text",
        warnings=[] if txns else [f"no dated lines parsed from {file_name or 'pdf'}"],
    )


def _header_map(cells: list) -> tuple[bool, dict[str, int]]:
    labels = [str(c or "").strip().lower() for c in cells]
    mapping: dict[str, int] = {}
    for i, label in enumerate(labels):
        if "date" in label and "date" not in mapping:
            mapping["date"] = i
        elif any(k in label for k in ("desc", "narration", "detail", "transaction", "payee")):
            mapping["description"] = i
        elif any(k in label for k in ("money in", "paid in", "credit", "in")) and "in" not in mapping:
            mapping["in"] = i
        elif any(k in label for k in ("money out", "paid out", "debit", "out")) and "out" not in mapping:
            mapping["out"] = i
        elif "amount" in label and "amount" not in mapping:
            mapping["amount"] = i
        elif "type" in label:
            mapping["type"] = i
    return bool(mapping.get("date") is not None), mapping


def _row_from_cells(raw: list, mapping: dict[str, int], page: int) -> CanonicalTxn | None:
    cells = [str(c).strip() if c is not None else "" for c in raw]
    if not cells:
        return None

    def col(key: str) -> str:
        idx = mapping.get(key)
        return cells[idx] if idx is not None and idx < len(cells) else ""

    txn_date = parse_date(col("date") or (cells[0] if cells else ""))
    if txn_date is None:
        return None
    in_amt = parse_money(col("in"))
    out_amt = parse_money(col("out"))
    amount = parse_money(col("amount"))
    if in_amt is not None and in_amt != 0:
        value, debit_credit = abs(in_amt), "credit"
    elif out_amt is not None and out_amt != 0:
        value, debit_credit = abs(out_amt), "debit"
    elif amount is not None:
        value, debit_credit = abs(amount), ("debit" if amount < 0 else "credit")
    else:
        return None
    desc = col("description") or " ".join(c for c in cells[1:] if c and parse_money(c) is None)
    return CanonicalTxn(
        txn_date=txn_date,
        description=desc.strip(),
        amount=value,
        debit_credit=debit_credit,
        payment_type=col("type"),
        source_page=page,
        reference=col("type"),
    )


def _balance_after(text: str, label: str) -> Decimal | None:
    upper = text.upper()
    idx = upper.find(label)
    if idx < 0:
        return None
    return parse_money(text[idx : idx + 80])


def _is_noise(line: str) -> bool:
    lower = line.lower()
    return any(token in lower for token in _NOISE)


def _clean_desc(text: str) -> str:
    lower = text.lower()
    for marker in ("date range applicable", "interest rate paid", "%aer"):
        idx = lower.find(marker)
        if idx >= 0:
            text = text[:idx]
            lower = text.lower()
    return text.strip()
