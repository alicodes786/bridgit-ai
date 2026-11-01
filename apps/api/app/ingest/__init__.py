from __future__ import annotations

from pathlib import Path

from app.ingest.pdf import parse_pdf
from app.ingest.tabular import parse_csv, parse_xlsx
from app.models import ParseResult


def parse_bank_file(file_name: str, content: bytes) -> ParseResult:
    """Detect format from filename + bytes. All banks share this entry point."""
    suffix = Path(file_name or "bank.bin").suffix.lower()
    if suffix == ".pdf" or content[:4] == b"%PDF":
        return parse_pdf(content, file_name=file_name)
    if suffix in {".xlsx", ".xlsm"}:
        return parse_xlsx(content, file_name=file_name)
    if suffix in {".csv", ".txt"}:
        return parse_csv(content, file_name=file_name)
    # Excel OLE files
    if content[:2] == b"PK":
        return parse_xlsx(content, file_name=file_name)
    return parse_csv(content, file_name=file_name)
