"""Load Hit Hunters Ltd payee → column mappings from the 2025 comparative file.

Usage (from apps/api, venv on):
    python -m scripts.load_hithunters_mappings

Stores mappings on client "Hit Hunters Ltd" only. Does not touch Koliqi.
Also seeds client_rules: code_by_payee = true for company_accounts.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
import openpyxl

from app.engine.yearend_map import extract_payee_map
from app.jobs_store import get_or_create_client

WORKBOOK = (
    Path(__file__).resolve().parents[3]
    / "data/client/HitHunters"
    / "Hit Hunters Ltd Accounts 28.02.2025_Comparative_File_2025 (AA)-(OK)(VK).xlsx"
)
CLIENT_NAME = "Hit Hunters Ltd"


def main() -> None:
    load_dotenv(Path(__file__).resolve().parents[3] / ".env")
    from app.db import get_supabase

    if not WORKBOOK.exists():
        raise SystemExit(f"missing {WORKBOOK}")
    wb = openpyxl.load_workbook(WORKBOOK, data_only=False)
    rows = extract_payee_map(wb)
    client = get_or_create_client(CLIENT_NAME)
    sb = get_supabase()
    existing = (
        sb.table("ai_mappings")
        .select("description_pattern")
        .eq("client_id", client["id"])
        .execute()
    )
    have = {r["description_pattern"] for r in (existing.data or [])}
    inserted = 0
    for row in rows:
        if row["description_pattern"] in have:
            continue
        sb.table("ai_mappings").insert({**row, "client_id": client["id"]}).execute()
        inserted += 1
    try:
        sb.table("client_rules").insert(
            {
                "client_id": client["id"],
                "job_type": "company_accounts",
                "rule_key": "code_by_payee",
                "rule_value": "true",
                "status": "approved",
            }
        ).execute()
    except Exception as exc:
        print("client_rules insert skipped:", exc)
    print(f"{CLIENT_NAME}: {len(rows)} payee maps, {inserted} new rows")


if __name__ == "__main__":
    main()
