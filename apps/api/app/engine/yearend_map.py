"""Extract payee → Banking / Bank Pay column from a prior-year statutory pack."""

from __future__ import annotations

from collections import Counter
from io import BytesIO

from openpyxl.worksheet.worksheet import Worksheet

from app.engine.payee import payee_key

BANKING_HEADER_ROW = 6
BANKING_FIRST_DATA = 8
BANK_PAY_HEADER_ROWS = (4, 5)
BANK_PAY_FIRST_DATA = 7


def banking_headers(ws: Worksheet) -> dict[int, str]:
    out: dict[int, str] = {}
    for col in range(4, 12):  # D..K
        name = str(ws.cell(BANKING_HEADER_ROW, col).value or "").strip()
        if name:
            out[col] = name
    return out


def bank_pay_headers(ws: Worksheet) -> dict[int, str]:
    out: dict[int, str] = {}
    for col in range(4, 30):  # D..AC
        top = str(ws.cell(BANK_PAY_HEADER_ROWS[0], col).value or "").strip()
        bot = str(ws.cell(BANK_PAY_HEADER_ROWS[1], col).value or "").strip()
        name = " ".join(p for p in (top, bot) if p).strip()
        if name:
            out[col] = name
    return out


def _echo_column(ws: Worksheet, row: int, amount_col: int, last_cat: int) -> int | None:
    needle = f"=C{row}"
    for col in range(amount_col + 1, last_cat + 1):
        val = ws.cell(row, col).value
        if isinstance(val, str) and val.replace(" ", "").upper() == needle.upper():
            return col
    return None


def extract_payee_map(wb) -> list[dict]:
    """Dominant column per payee. CSV Category is not used."""
    votes: dict[str, Counter] = {}
    labels: dict[str, str] = {}

    def _add(desc: object, col_name: str) -> None:
        text = str(desc or "").strip()
        if not text or text.upper() == "TOTAL":
            return
        key = payee_key(text)
        if not key:
            return
        votes.setdefault(key, Counter())[col_name] += 1
        labels.setdefault(key, text.split(";")[0].strip())

    banking = wb["Banking"]
    b_headers = banking_headers(banking)
    for row in range(BANKING_FIRST_DATA, (banking.max_row or BANKING_FIRST_DATA) + 1):
        details = banking.cell(row, 2).value
        amount = banking.cell(row, 3).value
        if not details or amount is None:
            continue
        col = _echo_column(banking, row, 3, 11)
        if col and col in b_headers:
            _add(details, b_headers[col])

    pay = wb["Bank Pay"]
    p_headers = bank_pay_headers(pay)
    last_amount = BANK_PAY_FIRST_DATA
    for row in range(BANK_PAY_FIRST_DATA, min(pay.max_row or 0, 400) + 1):
        if pay.cell(row, 3).value is not None:
            last_amount = row
    for row in range(BANK_PAY_FIRST_DATA, last_amount + 1):
        details = pay.cell(row, 2).value
        amount = pay.cell(row, 3).value
        if not details or amount is None:
            continue
        col = _echo_column(pay, row, 3, 29)
        if col and col in p_headers:
            _add(details, p_headers[col])

    rows = []
    for key, counter in votes.items():
        col_name, _ = counter.most_common(1)[0]
        rows.append(
            {
                "description_pattern": labels[key],
                "account_code": col_name,
                "account_name": col_name,
                "vat_code": "NV",
                "status": "approved",
            }
        )
    rows.sort(key=lambda r: r["description_pattern"].lower())
    return rows


def is_yearend_pack(content: bytes | None) -> bool:
    """True when the workbook is MA's statutory pack (Banking + Bank Pay tabs)."""
    if not content:
        return False
    from openpyxl import load_workbook

    try:
        wb = load_workbook(BytesIO(content), read_only=True, data_only=False)
    except Exception:
        return False
    try:
        names = set(wb.sheetnames)
        return "Banking" in names and "Bank Pay" in names
    except Exception:
        return False
    finally:
        try:
            wb.close()
        except Exception:
            pass


def mappings_from_workbook_bytes(content: bytes | None) -> list[dict]:
    """Read payee → column from an uploaded comparative workbook.

    Returns [] if the file is missing, not Excel, or has no Banking / Bank Pay tabs.
    """
    if not content:
        return []
    from openpyxl import load_workbook

    try:
        wb = load_workbook(BytesIO(content), data_only=False)
    except Exception:
        return []
    try:
        if "Banking" not in wb.sheetnames or "Bank Pay" not in wb.sheetnames:
            return []
        return extract_payee_map(wb)
    except Exception:
        return []
    finally:
        try:
            wb.close()
        except Exception:
            pass
