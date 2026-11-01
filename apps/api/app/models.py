from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal


@dataclass
class CanonicalTxn:
    """One bank line in Bridgit's standard shape. Parsers all emit this."""

    txn_date: date
    description: str
    amount: Decimal  # always positive
    debit_credit: str  # debit = money out (payment), credit = money in (receipt)
    payment_type: str = ""
    source_page: int | None = None
    source_row: int | None = None
    reference: str = ""
    running_balance: Decimal | None = None


@dataclass
class ParseResult:
    transactions: list[CanonicalTxn]
    parser: str
    opening_balance: Decimal | None = None
    closing_balance: Decimal | None = None
    warnings: list[str] = field(default_factory=list)


@dataclass
class ClassificationResult:
    account_code: str
    account_name: str
    vat_code: str
    source: str  # mapping | firm_rule | llm | human
    reason: str
    confidence: Decimal | None
    needs_review: bool
    vat_amount: Decimal
    net_amount: Decimal
    question: str | None = None
    duplicate_of_row: int | None = None
