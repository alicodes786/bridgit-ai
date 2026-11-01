"""Generate all fictional demo client packs under app/static/demo/."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from demo_packs import ALL_PACKS, brief_meridian, brief_northbridge, write_pack  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "app" / "static" / "demo"


def _verify(slug: str) -> None:
    from app.engine.yearend_map import mappings_from_workbook_bytes
    from app.ingest.tabular import parse_csv

    csv_path = OUT / f"{slug}-bank.csv"
    xlsx_path = OUT / f"{slug}-comparative.xlsx"
    parsed = parse_csv(csv_path.read_bytes(), file_name=csv_path.name)
    maps = mappings_from_workbook_bytes(xlsx_path.read_bytes())
    print(f"\n=== {slug} ===")
    print("lines", len(parsed.transactions), "open", parsed.opening_balance, "close", parsed.closing_balance)
    print("maps", len(maps))
    if parsed.opening_balance is None:
        raise SystemExit(f"{slug}: no opening balance")
    in_amt = sum((t.amount for t in parsed.transactions if t.debit_credit == "credit"), Decimal("0"))
    out_amt = sum((t.amount for t in parsed.transactions if t.debit_credit == "debit"), Decimal("0"))
    calc = (parsed.opening_balance + in_amt - out_amt).quantize(Decimal("0.01"))
    diff = (calc - parsed.closing_balance).quantize(Decimal("0.01"))
    print("rec diff", diff)
    if diff != 0:
        raise SystemExit(f"{slug}: bank rec does not tie")


def main() -> None:
    for pack in ALL_PACKS:
        write_pack(OUT, pack)
        print("wrote", OUT / f"{pack.slug}-bank.csv")
        print("wrote", OUT / f"{pack.slug}-comparative.xlsx")
        _verify(pack.slug)
    (OUT / "meridian-studio-demo-brief.txt").write_text(brief_meridian(), encoding="utf-8")
    (OUT / "northbridge-demo-brief.txt").write_text(brief_northbridge(), encoding="utf-8")
    (OUT / "meridian-studio-insurance-note.txt").write_text(
        "MERIDIAN STUDIO LTD — professional indemnity renewal quote (fictional).\n"
        "Upload via Chat to test supporting files. Bridgit stores it; Phase 1 does not OCR.\n",
        encoding="utf-8",
    )
    print("wrote briefs + meridian-studio-insurance-note.txt")


if __name__ == "__main__":
    main()
