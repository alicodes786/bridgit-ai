"""Categorisation chain (17-build-plan Day 3–5, 13-scope-phase1).

Order:
  0. Duplicate (same date + amount + description on this job) — flag, do not auto-post
  1. Exact prior mapping (approved only) — no AI
  2. Firm rules - skipped until MA Associates send VAT and chart of accounts
  3. LLM propose + confidence — on (ZDR confirmed 17 Sep)
  4. Exception with a specific question
"""

from __future__ import annotations

from decimal import Decimal

from app.ingest._util import normalize_description
from app.models import CanonicalTxn, ClassificationResult

VAT_STANDARD = Decimal("0.20")
STANDARD_VAT_CODES = {"SR"}


def vat_split(gross: Decimal, vat_code: str) -> tuple[Decimal, Decimal]:
    code = (vat_code or "").upper()
    if code in STANDARD_VAT_CODES:
        vat = (gross * VAT_STANDARD / (1 + VAT_STANDARD)).quantize(Decimal("0.01"))
        net = (gross - vat).quantize(Decimal("0.01"))
        return vat, net
    return Decimal("0.00"), gross.quantize(Decimal("0.01"))


def categorise_transactions(
    transactions: list[CanonicalTxn],
    mappings: list[dict],
    *,
    client_name: str = "",
    code_by_payee: bool = False,
    ask_unmatched: bool = False,
    remembered: dict | None = None,
) -> list[ClassificationResult]:
    approved = {}
    proposed = {}
    for row in mappings:
        key = normalize_description(row.get("description_pattern") or "")
        if not key:
            continue
        status = (row.get("status") or "approved").lower()
        target = approved if status == "approved" else proposed
        target.setdefault(key, row)

    seen: dict[tuple, int] = {}
    results: list[ClassificationResult] = []
    unknown_indices: list[int] = []

    for index, txn in enumerate(transactions):
        dup_key = (txn.txn_date.isoformat(), str(txn.amount), normalize_description(txn.description))
        if dup_key in seen:
            from app.engine.remember import duplicate_decision

            decision = duplicate_decision(remembered, txn)
            if decision == "exclude_repeat":
                vat, net = vat_split(txn.amount, "")
                results.append(
                    ClassificationResult(
                        account_code="",
                        account_name="",
                        vat_code="",
                        source="human",
                        reason="excluded as repeat posting",
                        confidence=Decimal("1.00"),
                        needs_review=False,
                        vat_amount=vat,
                        net_amount=net,
                    )
                )
                continue
            if decision != "keep_both":
                results.append(
                    _exception(
                        txn,
                        question=(
                            f"{txn.description} £{txn.amount} on {txn.txn_date:%d %b %Y} "
                            f"matches line {seen[dup_key] + 1} (same date, amount, description). "
                            "Keep both, or is one a repeat?"
                        ),
                        duplicate_of_row=seen[dup_key] + 1,
                    )
                )
                continue
            # keep_both: code this line like the first (mapping / new payee).
        else:
            seen[dup_key] = index

        if code_by_payee:
            from app.engine.payee import lookup_payee_mapping

            hit = lookup_payee_mapping(txn.description, mappings)
            if hit:
                name = (hit.get("account_name") or hit.get("account_code") or "").lower()
                if "private" in name or "suspense" in name:
                    vat_code = hit.get("vat_code") or ""
                    vat, net = vat_split(txn.amount, vat_code)
                    results.append(
                        ClassificationResult(
                            account_code=hit.get("account_code") or hit.get("account_name") or "",
                            account_name=hit.get("account_name") or "",
                            vat_code=vat_code,
                            source="mapping",
                            reason="Prior year put this payee in Private/Suspense — query, do not absorb quietly.",
                            confidence=Decimal("0.80"),
                            needs_review=True,
                            vat_amount=vat,
                            net_amount=net,
                            question=(
                                f"{txn.description} — £{txn.amount} on {txn.txn_date:%d %b %Y}. "
                                f"Last year this sat in '{hit.get('account_name')}'. "
                                "Query the client before it goes to the Director's Loan Account "
                                "(or confirm it stays as a query)."
                            ),
                        )
                    )
                    continue
                results.append(
                    _from_mapping(
                        txn,
                        hit,
                        needs_review=False,
                        reason="Prior-year payee coding for this client.",
                    )
                )
                continue
            unknown_indices.append(index)
            results.append(
                _exception(
                    txn,
                    question=(
                        f"{txn.description} — {_flow_phrase(txn)} £{txn.amount} on {txn.txn_date:%d %b %Y}. "
                        "New payee (not in last year's file). Which column should this go to? "
                        "Do not put it in Suspense unless you are querying the client."
                    ),
                )
            )
            continue

        key = normalize_description(txn.description)
        if key in approved:
            results.append(_from_mapping(txn, approved[key], needs_review=False))
            continue

        if key in proposed:
            row = proposed[key]
            vat_code = row.get("vat_code") or ""
            vat, net = vat_split(txn.amount, vat_code)
            category = row.get("account_name") or row.get("account_code") or ""
            results.append(
                ClassificationResult(
                    account_code=row.get("account_code") or category,
                    account_name=category,
                    vat_code=vat_code,
                    source="mapping",
                    reason="Prior coding existed but was marked REVIEW / personal — not auto-applied.",
                    confidence=Decimal("0.50"),
                    needs_review=True,
                    vat_amount=vat,
                    net_amount=net,
                    question=_personal_or_business_question(txn, category),
                )
            )
            continue

        unknown_indices.append(index)
        results.append(_exception(txn, question=_unknown_question(txn)))

    if code_by_payee:
        _collapse_payee_questions(transactions, results)

    if unknown_indices and not (ask_unmatched or code_by_payee):
        from app.engine.llm import propose_unknown_lines

        subset = [transactions[i] for i in unknown_indices]
        proposals = propose_unknown_lines(subset, mappings, client_name=client_name)
        for local_i, klass in proposals.items():
            if 0 <= local_i < len(unknown_indices):
                results[unknown_indices[local_i]] = klass

    return results


def _collapse_payee_questions(
    transactions: list[CanonicalTxn],
    results: list[ClassificationResult],
) -> None:
    """One question per payee, not per bank line."""
    from collections import defaultdict

    from app.engine.payee import payee_key

    groups: dict[tuple[str, str], list[int]] = defaultdict(list)
    for index, (txn, klass) in enumerate(zip(transactions, results)):
        if not klass.needs_review or not klass.question or klass.duplicate_of_row:
            continue
        pk = payee_key(txn.description)
        if not pk:
            continue
        q = klass.question
        if "New payee" in q:
            groups[("new", pk)].append(index)
        elif "Private/Suspense" in q or "sat in '" in q:
            groups[("query", pk)].append(index)

    for (kind, _pk), indices in groups.items():
        lead = indices[0]
        txn = transactions[lead]
        total = sum(transactions[i].amount for i in indices)
        n = len(indices)
        label = (txn.description or "").split(";")[0].strip() or txn.description
        if kind == "new":
            results[lead] = _exception(
                txn,
                question=(
                    f"{label} — {n} line{'s' if n != 1 else ''}, {_flow_phrase(txn)} £{total}. "
                    "New payee (not in last year's file). Which column should this go to? "
                    "Do not put it in Suspense unless you are querying the client."
                ),
            )
            for i in indices[1:]:
                results[i].question = None
                results[i].needs_review = True  # still unresolved, just no separate card
                results[i].reason = "Same new payee as another line — one question covers the group."
            continue

        hit_name = results[lead].account_name or results[lead].account_code or "Private/Suspense"
        results[lead].question = (
            f"{label} — {n} line{'s' if n != 1 else ''}, {_flow_phrase(txn)} £{total}. "
            f"Last year this sat in '{hit_name}'. "
            "Query the client before it goes to the Director's Loan Account "
            "(or confirm it stays as a query)."
        )
        for i in indices[1:]:
            results[i].question = None
            results[i].needs_review = True  # coding not yet confirmed for these siblings
            results[i].reason = "Same Private/Suspense payee as another line — one question covers the group."


def _flow_phrase(txn: CanonicalTxn) -> str:
    if txn.debit_credit == "credit":
        return "money in (received into the bank)"
    if txn.debit_credit == "debit":
        return "money out (left the bank)"
    return "bank movement"


def _from_mapping(
    txn: CanonicalTxn,
    row: dict,
    *,
    needs_review: bool,
    reason: str = "Exact prior mapping for this client.",
) -> ClassificationResult:
    vat_code = row.get("vat_code") or ""
    vat, net = vat_split(txn.amount, vat_code)
    category = row.get("account_name") or row.get("account_code") or ""
    return ClassificationResult(
        account_code=row.get("account_code") or category,
        account_name=category,
        vat_code=vat_code,
        source="mapping",
        reason=reason,
        confidence=Decimal("1.00"),
        needs_review=needs_review,
        vat_amount=vat,
        net_amount=net,
    )


def _exception(txn: CanonicalTxn, *, question: str, duplicate_of_row: int | None = None) -> ClassificationResult:
    vat, net = vat_split(txn.amount, "")
    return ClassificationResult(
        account_code="",
        account_name="",
        vat_code="",
        source="human",
        reason="Needs a human — no approved mapping / firm rule, or LLM was unsure.",
        confidence=None,
        needs_review=True,
        vat_amount=vat,
        net_amount=net,
        question=question,
        duplicate_of_row=duplicate_of_row,
    )


def _personal_or_business_question(txn: CanonicalTxn, category: str) -> str:
    return (
        f"{txn.description} - £{txn.amount} on {txn.txn_date:%d %b %Y}. "
        f"Business or personal? Last coding was '{category}' (unconfirmed)."
    )


def _unknown_question(txn: CanonicalTxn) -> str:
    return (
        f"{txn.description} - £{txn.amount} on {txn.txn_date:%d %b %Y}. "
        "Business or personal? If business, which category?"
    )
