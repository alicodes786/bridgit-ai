from __future__ import annotations

from pathlib import Path

from app.models.transaction import ParseResult
from app.parsers.csv_excel import parse_csv_or_excel
from app.parsers.starling_pdf import parse_starling_pdf


def parse_bank_file(content: bytes, file_name: str) -> ParseResult:
    name = file_name.lower()
    if name.endswith(".pdf"):
        return parse_starling_pdf(content)
    if name.endswith((".csv", ".xlsx", ".xls")):
        return parse_csv_or_excel(content, file_name)
    raise ValueError(f"unsupported bank file type: {file_name}")
