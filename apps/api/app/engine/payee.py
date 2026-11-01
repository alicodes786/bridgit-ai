"""Payee keys for year-end coding (Hit Hunters process log: code by payee, not CSV Category)."""

from __future__ import annotations

from app.ingest._util import normalize_description

# Too generic to use as a keyword match — "Card Payment Tesco" must not become Paypal.
# payee_key is uppercase.
_STOP_TOKENS = frozenset(
    {
        "PAYMENT",
        "PAYMENTS",
        "TRANSFER",
        "CARD",
        "DEBIT",
        "CREDIT",
        "DIRECT",
        "BANK",
        "FEE",
        "FEES",
        "LTD",
        "LIMITED",
        "THE",
        "AND",
        "FROM",
        "WITH",
    }
)


def payee_key(description: str | None) -> str:
    """Text before ';' , stripped, normalised. CSV Category is ignored by the caller."""
    raw = (description or "").split(";")[0].strip()
    return normalize_description(raw)


def merge_payee_mappings(*groups: list[dict]) -> list[dict]:
    """Earlier groups win for the same payee key (saved mappings beat a fresh extract)."""
    by_key: dict[str, dict] = {}
    order: list[str] = []
    for group in groups:
        for row in group:
            mk = payee_key(row.get("description_pattern") or "")
            if not mk or mk in by_key:
                continue
            by_key[mk] = row
            order.append(mk)
    return [by_key[k] for k in order]


def lookup_payee_mapping(description: str, mappings: list[dict]) -> dict | None:
    """Exact payee key, then prefix, then distinctive keyword — same order as the process log."""
    key = payee_key(description)
    if not key:
        return None
    by_key: dict[str, dict] = {}
    for row in mappings:
        status = (row.get("status") or "approved").lower()
        if status != "approved":
            continue
        mk = payee_key(row.get("description_pattern") or "")
        if mk and mk not in by_key:
            by_key[mk] = row
    if key in by_key:
        return by_key[key]
    for mk, row in by_key.items():
        # Word-boundary prefix: "O2" → "O2 Extra" ✓  "TES" → "TESSA CONSULTING" ✗
        if key.startswith(mk) and (len(key) == len(mk) or key[len(mk) : len(mk) + 1] == " "):
            if len(mk) >= 2:
                return row
        if mk.startswith(key) and (len(key) == len(mk) or mk[len(key) : len(key) + 1] == " "):
            if len(key) >= 2:
                return row
    tokens = [t for t in key.split() if len(t) >= 4 and t not in _STOP_TOKENS]
    if not tokens:
        return None
    for mk, row in by_key.items():
        mk_tokens = [t for t in mk.split() if len(t) >= 4 and t not in _STOP_TOKENS]
        if any(t in mk.split() for t in tokens) or any(t in key.split() for t in mk_tokens):
            return row
    return None
