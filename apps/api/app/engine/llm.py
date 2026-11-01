"""Claude judgement for lines with no mapping and no firm rule.

ZDR confirmed 17 Sep 2026 (Decision 20). Only descriptions/amounts/dates are sent,
not the source PDF bytes.
"""

from __future__ import annotations

import json
from decimal import Decimal

from app.config import settings
from app.engine.categorise import vat_split
from app.models import CanonicalTxn, ClassificationResult

CONFIDENCE_AUTO = Decimal("0.75")
_MODEL = "claude-sonnet-4-5"


def propose_unknown_lines(
    transactions: list[CanonicalTxn],
    mappings: list[dict],
    *,
    client_name: str = "",
) -> dict[int, ClassificationResult]:
    """index-in-transactions → classification. Empty if no API key or no unknowns."""
    if not settings.anthropic_api_key.strip() or not transactions:
        return {}

    examples = []
    for row in mappings[:40]:
        examples.append(
            {
                "description": row.get("description_pattern"),
                "account": row.get("account_name") or row.get("account_code"),
                "vat_code": row.get("vat_code"),
                "status": row.get("status"),
            }
        )

    payload = [
        {
            "i": i,
            "date": txn.txn_date.isoformat(),
            "description": txn.description,
            "amount": str(txn.amount),
            "direction": "out" if txn.debit_credit == "debit" else "in",
            "type": txn.payment_type,
        }
        for i, txn in enumerate(transactions)
    ]

    prompt = f"""You are Bridgit, MA Associates' bookkeeping assistant (UK ACCA practice).
Client: {client_name or "unknown"}
Property/development context is common. VAT codes we use: SR (20% standard), ZR, EX (exempt), NV (no VAT / out of scope personal), OS (outside scope).

Prior client mappings (examples, not exhaustive):
{json.dumps(examples, ensure_ascii=False)}

For EACH transaction below, propose account_name, vat_code, confidence 0-1, and a short question if unsure.
Question rules: one sentence. Ask only business vs personal (or keep-both if it looks like a repeat). Do not ask for trip purpose, meeting notes, or extra story. Do not invent ledger numbers.
If it looks personal (coffee, groceries, pharmacy) say "Business or personal?"

Transactions:
{json.dumps(payload, ensure_ascii=False)}

Return JSON only: {{"results": [{{"i": 0, "account_name": "", "vat_code": "NV", "confidence": 0.4, "question": "Costa Coffee — £4.05 on 8 Aug 2026. Business or personal?"}}]}}
"""

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key.strip())
        message = client.messages.create(
            model=_MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in message.content if getattr(block, "type", "") == "text")
        text = text.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()
        data = json.loads(text)
    except Exception:
        return {}

    by_index: dict[int, ClassificationResult] = {}
    lookup = {i: txn for i, txn in enumerate(transactions)}
    for item in data.get("results") or []:
        try:
            i = int(item["i"])
        except (KeyError, TypeError, ValueError):
            continue
        txn = lookup.get(i)
        if txn is None:
            continue
        vat_code = str(item.get("vat_code") or "").upper()
        account = str(item.get("account_name") or "").strip()
        try:
            confidence = Decimal(str(item.get("confidence") or "0")).quantize(Decimal("0.01"))
        except Exception:
            confidence = Decimal("0.00")
        vat, net = vat_split(txn.amount, vat_code)
        question = str(item.get("question") or "").strip() or None
        auto = confidence >= CONFIDENCE_AUTO and bool(account)
        by_index[i] = ClassificationResult(
            account_code=account,
            account_name=account,
            vat_code=vat_code,
            source="llm",
            reason=f"Claude proposal at confidence {confidence}.",
            confidence=confidence,
            needs_review=not auto,
            vat_amount=vat,
            net_amount=net,
            question=None if auto else (question or _fallback_question(txn)),
        )
    return by_index


def _fallback_question(txn: CanonicalTxn) -> str:
    return (
        f"{txn.description} - £{txn.amount} on {txn.txn_date:%d %b %Y}. "
        "Business or personal?"
    )
