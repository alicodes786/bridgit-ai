"""Local parser check — does not upload client files or call the LLM."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.engine.categorise import categorise_transactions
from app.engine.excel_writer import bank_rec_check, write_working_file
from app.ingest import parse_bank_file

FILES = [
    Path(__file__).resolve().parents[3]
    / "data/client/koliqi-sons/StarlingStatement_2026-04_2026-07.pdf",
    Path(__file__).resolve().parents[3]
    / "data/client/koliqi-sons/StarlingStatement_2026-08_2026-08.pdf",
]


def main() -> None:
    for path in FILES:
        if not path.exists():
            print("MISSING", path)
            continue
        parsed = parse_bank_file(path.name, path.read_bytes())
        rec = bank_rec_check(parsed, parsed.transactions)
        print("=" * 60)
        print(path.name)
        print("parser", parsed.parser)
        print("rows", len(parsed.transactions))
        print("in", sum(1 for t in parsed.transactions if t.debit_credit == "credit"))
        print("out", sum(1 for t in parsed.transactions if t.debit_credit == "debit"))
        print("opening", parsed.opening_balance, "closing", parsed.closing_balance)
        print("bank_rec", rec)
        print("first", parsed.transactions[0] if parsed.transactions else None)
        print("last", parsed.transactions[-1] if parsed.transactions else None)
        print("warnings", parsed.warnings)

        dummy = [{"description_pattern": "Costa Coffee", "account_code": "Subsistence", "account_name": "Subsistence / coffee (personal?)", "vat_code": "NV", "status": "proposed"}]
        try:
            from scripts.load_koliqi_mappings import extract_mappings
            import openpyxl

            wb_path = path.parent / "Koliqi_Sons_VAT_File_May-Jun_2026 (FN CL).xlsx"
            if wb_path.exists():
                dummy = extract_mappings(openpyxl.load_workbook(wb_path, data_only=True))
        except Exception as exc:
            print("mapping_load_error", type(exc).__name__, exc)
        results = categorise_transactions(parsed.transactions, dummy)
        approved_hits = sum(1 for r in results if r.source == "mapping" and not r.needs_review)
        proposed_hits = sum(1 for r in results if r.source == "mapping" and r.needs_review)
        dups = sum(1 for r in results if r.duplicate_of_row)
        unknown = sum(1 for r in results if r.source == "human" and not r.duplicate_of_row)
        print("mappings_loaded", len(dummy))
        print("auto_coded", approved_hits, "proposed_review", proposed_hits, "duplicates", dups, "unknown", unknown)
        xlsx = write_working_file(parsed, parsed.transactions, results)
        print("excel_bytes", len(xlsx))


if __name__ == "__main__":
    main()
