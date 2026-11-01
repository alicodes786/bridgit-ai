"""
Load Koliqi & Sons transaction mappings from the VAT workbook into ai_mappings.

Usage (from apps/api):
    python -m scripts.load_koliqi_mappings

What this does:
  1. Creates (or reuses) the Koliqi & Sons client in ai_clients
  2. Reads every coded row from Banking Analysis + Bank Payment Analysis sheets
  3. Deduplicates by description (first-seen wins)
  4. Inserts into ai_mappings:
       - status='approved'  for clean business lines
       - status='proposed'  for lines flagged REVIEW or (personal?)
       NOTE: account_code is set to the VAT category description until MA sends
             the chart of accounts. Run update_account_codes.py after that.

Run this ONCE before the first bank file is processed.
Re-running is safe — it skips descriptions already in the table.
"""

import sys
from pathlib import Path

# Allow running from apps/api root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import openpyxl

WORKBOOK_PATH = (
    Path(__file__).resolve().parents[3]
    / "data/client/koliqi-sons/Koliqi_Sons_VAT_File_May-Jun_2026 (FN CL).xlsx"
)

CLIENT_NAME = "Koliqi & Sons Developments Ltd"

# Categories that need human review before being used as auto-mappings
REVIEW_MARKERS = ["review", "(personal?)"]


def is_review(category: str) -> bool:
    cat_lower = category.lower()
    return any(m in cat_lower for m in REVIEW_MARKERS)


def extract_mappings(wb: openpyxl.Workbook) -> list[dict]:
    """Return unique description → category/VAT rows from both analysis sheets."""
    seen: dict[str, dict] = {}

    for sheet_name in ["Banking Analysis", "Bank Payment Analysis"]:
        ws = wb[sheet_name]
        for row in ws.iter_rows(min_row=6, values_only=True):
            date, typ, detail, amount, category, code, vat, net = row
            if not detail or not category or not code:
                continue
            detail_str = str(detail).strip()
            category_str = str(category).strip()
            code_str = str(code).strip()

            # Skip totals / anchor rows
            lower_detail = detail_str.lower()
            if any(x in lower_detail for x in ["totals", "total anchors", "do not delete"]):
                continue

            if detail_str not in seen:
                seen[detail_str] = {
                    "description_pattern": detail_str,
                    # account_code: use category until CoA arrives
                    "account_code": category_str,
                    "account_name": category_str,
                    "vat_code": code_str,
                    "status": "proposed" if is_review(category_str) else "approved",
                }

    return list(seen.values())


def main() -> None:
    from dotenv import load_dotenv

    from app.db import get_supabase

    load_dotenv(Path(__file__).resolve().parents[3] / ".env")

    print(f"Loading mappings from:\n  {WORKBOOK_PATH}\n")

    if not WORKBOOK_PATH.exists():
        print("ERROR: workbook not found. Check the path.")
        sys.exit(1)

    wb = openpyxl.load_workbook(str(WORKBOOK_PATH), data_only=True)
    mappings = extract_mappings(wb)

    approved = [m for m in mappings if m["status"] == "approved"]
    proposed = [m for m in mappings if m["status"] == "proposed"]
    print(f"Extracted {len(mappings)} unique descriptions")
    print(f"  {len(approved)} approved  (clean business lines — used immediately)")
    print(f"  {len(proposed)} proposed  (flagged REVIEW/personal — need human confirm)")

    supabase = get_supabase()

    # 1. Upsert client
    existing = (
        supabase.table("ai_clients")
        .select("id")
        .eq("name", CLIENT_NAME)
        .execute()
    )
    if existing.data:
        client_id = existing.data[0]["id"]
        print(f"\nClient already exists: {client_id}")
    else:
        result = supabase.table("ai_clients").insert({"name": CLIENT_NAME}).execute()
        client_id = result.data[0]["id"]
        print(f"\nClient created: {client_id}")

    # 2. Get already-loaded descriptions for this client (skip re-inserts)
    existing_rows = (
        supabase.table("ai_mappings")
        .select("description_pattern")
        .eq("client_id", client_id)
        .execute()
    )
    already_loaded = {r["description_pattern"] for r in (existing_rows.data or [])}
    print(f"Already in DB: {len(already_loaded)} descriptions (will skip)")

    # 3. Insert new rows
    to_insert = [
        {**m, "client_id": client_id}
        for m in mappings
        if m["description_pattern"] not in already_loaded
    ]

    if not to_insert:
        print("\nNothing new to insert. All mappings already loaded.")
        return

    print(f"\nInserting {len(to_insert)} new rows...")
    supabase.table("ai_mappings").insert(to_insert).execute()

    new_approved = sum(1 for m in to_insert if m["status"] == "approved")
    new_proposed = sum(1 for m in to_insert if m["status"] == "proposed")
    print(f"Done. {new_approved} approved + {new_proposed} proposed inserted.")
    print()
    print("NOTE: account_code is currently set to the category description.")
    print("      Once MA sends the chart of accounts, run update_account_codes.py")
    print("      to replace these with the proper ledger codes (e.g. 4000, 5010).")


if __name__ == "__main__":
    main()
