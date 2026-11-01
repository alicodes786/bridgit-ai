from datetime import date
from decimal import Decimal
from io import BytesIO
from pathlib import Path
import unittest

from openpyxl import Workbook

from app.engine.categorise import categorise_transactions
from app.engine.payee import lookup_payee_mapping, payee_key
from app.engine.yearend_excel import write_yearend_bank_tabs
from app.engine.yearend_map import extract_payee_map
from app.ingest.tabular import parse_csv
from app.job_intake import check_missing_documents, classify_upload, period_coverage_question
from app.jobs_store import match_client_row, normalize_client_name
from app.models import CanonicalTxn

_DEMO = Path(__file__).resolve().parents[1] / "app" / "static" / "demo"


class IntakeTests(unittest.TestCase):
    def test_vat_yearend_pack_is_company_accounts(self):
        from app.job_intake import effective_job_type, job_type_label

        self.assertEqual(
            effective_job_type("vat_return", yearend_pack=True),
            "company_accounts",
        )
        self.assertEqual(effective_job_type("vat_return", yearend_pack=False), "vat_return")
        self.assertEqual(job_type_label("company_accounts"), "Company Accounts (statutory year-end)")
        self.assertEqual(job_type_label("vat_return"), "VAT Return")

    def test_year_end_asks_for_bank_and_comparative_but_does_not_hard_block(self):
        result = check_missing_documents(
            job_type="company_accounts",
            documents=[],
            period_start=date(2025, 3, 1),
            period_end=date(2026, 2, 28),
        )
        self.assertFalse(result.as_dict()["hard_block"])
        kinds = {m.kind for m in result.required_missing}
        self.assertIn("bank", kinds)
        self.assertIn("comparative", kinds)

    def test_vat_with_bank_still_mentions_optional_invoices(self):
        result = check_missing_documents(
            job_type="vat_return",
            documents=[{"kind": "bank"}],
        )
        required = {m.kind for m in result.required_missing}
        self.assertNotIn("bank", required)
        optional = {m.kind for m in result.missing if not m.required}
        self.assertIn("purchase_invoice", optional)

    def test_period_gap_question(self):
        txns = [
            CanonicalTxn(date(2026, 8, 1), "A", Decimal("1.00"), "debit"),
            CanonicalTxn(date(2026, 8, 18), "B", Decimal("1.00"), "debit"),
        ]
        q = period_coverage_question(
            txns, period_start=date(2026, 8, 1), period_end=date(2026, 8, 31)
        )
        self.assertIn("18 Aug", q)
        self.assertIn("31 Aug", q)


class ClientNameTests(unittest.TestCase):
    def test_reuses_hit_hunters_despite_case(self):
        rows = [{"id": "hh", "name": "Hit Hunters Ltd"}]
        self.assertEqual(normalize_client_name("  hit  hunters  ltd "), "hit hunters ltd")
        self.assertEqual(match_client_row("HIT HUNTERS LTD", rows)["id"], "hh")


class CountingupParseTests(unittest.TestCase):
    def test_sorts_and_opening_from_running_balance(self):
        csv = (
            "Date,Cleared date,Description,Category,Reference,Paid in (£),Paid out (£),Balance (£)\n"
            "2026-02-28,2026-02-28,Last,Sales,x,5.00,,95.00\n"
            "2026-02-01,2026-02-01,First,Web hosting,y,,10.00,90.00\n"
        )
        parsed = parse_csv(csv.encode(), file_name="t.csv")
        self.assertEqual(parsed.transactions[0].description, "First")
        self.assertEqual(parsed.opening_balance, Decimal("100.00"))
        self.assertEqual(parsed.closing_balance, Decimal("95.00"))
        rec = parsed.opening_balance + Decimal("5.00") - Decimal("10.00")
        self.assertEqual(rec, parsed.closing_balance)


class PayeeMapTests(unittest.TestCase):
    def test_payee_key_strips_after_semicolon(self):
        self.assertEqual(payee_key("O2; mobile"), payee_key("O2"))

    def test_lookup_prefix(self):
        mappings = [
            {
                "description_pattern": "Paypal Payment",
                "account_name": "Equipment Expensed",
                "status": "approved",
            }
        ]
        hit = lookup_payee_mapping("Paypal Payment extra", mappings)
        self.assertEqual(hit["account_name"], "Equipment Expensed")
        self.assertEqual(
            lookup_payee_mapping("O2 extra", [{"description_pattern": "O2", "account_name": "Phone", "status": "approved"}])[
                "account_name"
            ],
            "Phone",
        )

    def test_unmatched_payee_does_not_call_llm(self):
        txn = CanonicalTxn(date(2026, 2, 1), "Brand New Cafe", Decimal("4.00"), "debit")
        results = categorise_transactions(
            [txn],
            [],
            code_by_payee=True,
            ask_unmatched=True,
        )
        self.assertTrue(results[0].needs_review)
        self.assertIn("New payee", results[0].question or "")
        self.assertIn("money out", results[0].question or "")
        self.assertNotIn("Business or personal", results[0].question or "")

    def test_same_new_payee_asks_once(self):
        txns = [
            CanonicalTxn(date(2026, 2, 1), "Brand New Cafe; a", Decimal("4.00"), "debit"),
            CanonicalTxn(date(2026, 2, 8), "Brand New Cafe; b", Decimal("6.00"), "debit"),
            CanonicalTxn(date(2026, 2, 15), "Brand New Cafe", Decimal("2.00"), "debit"),
        ]
        results = categorise_transactions(txns, [], code_by_payee=True, ask_unmatched=True)
        questions = [r.question for r in results if r.question]
        self.assertEqual(len(questions), 1)
        self.assertIn("3 lines", questions[0])
        self.assertIn("£12.00", questions[0])
        self.assertIn("money out", questions[0])
        self.assertTrue(all(r.needs_review for r in results))

    def test_private_payee_asks_once_keeps_coding(self):
        mappings = [
            {
                "description_pattern": "Director Draw",
                "account_name": "Private",
                "account_code": "Private",
                "status": "approved",
            }
        ]
        txns = [
            CanonicalTxn(date(2026, 2, 1), "Director Draw", Decimal("10.00"), "debit"),
            CanonicalTxn(date(2026, 2, 8), "Director Draw; atm", Decimal("20.00"), "debit"),
        ]
        results = categorise_transactions(txns, mappings, code_by_payee=True, ask_unmatched=True)
        questions = [r.question for r in results if r.question]
        self.assertEqual(len(questions), 1)
        self.assertIn("2 lines", questions[0])
        self.assertEqual(results[0].account_name, "Private")
        self.assertTrue(results[0].needs_review)
        self.assertEqual(results[1].account_name, "Private")
        # sibling stays needs_review=True (consistent — coding not yet confirmed)
        self.assertTrue(results[1].needs_review)

    def test_payment_token_does_not_steal_unrelated_payee(self):
        mappings = [
            {
                "description_pattern": "Paypal Payment",
                "account_name": "Equipment Expensed",
                "status": "approved",
            }
        ]
        self.assertIsNone(lookup_payee_mapping("Card Payment Tesco", mappings))

    def test_saved_mapping_beats_comparative_extract(self):
        from app.engine.payee import merge_payee_mappings

        db = [{"description_pattern": "O2", "account_name": "Phone", "status": "approved"}]
        extract = [{"description_pattern": "O2", "account_name": "Light Heat Power", "status": "approved"}]
        merged = merge_payee_mappings(db, extract)
        self.assertEqual(merged[0]["account_name"], "Phone")


class YearEndExtractTests(unittest.TestCase):
    def test_extract_dominant_column(self):
        wb = Workbook()
        banking = wb.active
        banking.title = "Banking"
        for col, name in enumerate(
            ["Date", "Details", "Amount", "Income", "Refund", "Contra", "Grant", "Suspense", "Copyright", "PRS", "Director"],
            start=1,
        ):
            banking.cell(6, col).value = name
        banking.cell(9, 1).value = date(2025, 4, 15)
        banking.cell(9, 2).value = "Mechanical Copyrig"
        banking.cell(9, 3).value = 72.35
        banking.cell(9, 9).value = "=C9"
        pay = wb.create_sheet("Bank Pay")
        pay.cell(5, 1).value = "Date"
        pay.cell(5, 2).value = "Details"
        pay.cell(5, 3).value = "Amount"
        pay.cell(5, 17).value = "Phone"
        pay.cell(8, 1).value = 11
        pay.cell(8, 2).value = "O2"
        pay.cell(8, 3).value = 51.91
        pay.cell(8, 17).value = "=C8"
        rows = extract_payee_map(wb)
        names = {r["description_pattern"]: r["account_name"] for r in rows}
        self.assertEqual(names["Mechanical Copyrig"], "Copyright")
        self.assertEqual(names["O2"], "Phone")

    def test_extract_from_uploaded_bytes(self):
        wb = Workbook()
        banking = wb.active
        banking.title = "Banking"
        for col, name in enumerate(
            ["Date", "Details", "Amount", "Income", "Refund", "Contra", "Grant", "Suspense", "Copyright", "PRS", "Director"],
            start=1,
        ):
            banking.cell(6, col).value = name
        banking.cell(9, 1).value = date(2025, 4, 15)
        banking.cell(9, 2).value = "Mechanical Copyrig"
        banking.cell(9, 3).value = 72.35
        banking.cell(9, 9).value = "=C9"
        pay = wb.create_sheet("Bank Pay")
        pay.cell(5, 2).value = "Details"
        pay.cell(5, 3).value = "Amount"
        pay.cell(5, 17).value = "Phone"
        pay.cell(8, 2).value = "O2"
        pay.cell(8, 3).value = 51.91
        pay.cell(8, 17).value = "=C8"
        buf = BytesIO()
        wb.save(buf)
        from app.engine.yearend_map import is_yearend_pack, mappings_from_workbook_bytes

        rows = mappings_from_workbook_bytes(buf.getvalue())
        names = {r["description_pattern"]: r["account_name"] for r in rows}
        self.assertEqual(names["O2"], "Phone")
        self.assertEqual(mappings_from_workbook_bytes(b"not-excel"), [])
        self.assertTrue(is_yearend_pack(buf.getvalue()))
        self.assertFalse(is_yearend_pack(b"not-excel"))

    def test_write_bank_tabs_into_copy(self):
        wb = Workbook()
        banking = wb.active
        banking.title = "Banking"
        banking["A3"] = "FOR THE YEAR ENDED 28TH FEBRUARY 2025"
        for col, name in enumerate(
            ["Date", "Details", "Amount", "Income", "Refund", "Contra", "Grant", "Suspense", "Copyright", "PRS", "Director"],
            start=1,
        ):
            banking.cell(6, col).value = name
        pay = wb.create_sheet("Bank Pay")
        pay["A3"] = "FOR THE YEAR ENDED 28TH FEBRUARY 2025"
        pay.cell(5, 2).value = "Details"
        pay.cell(5, 3).value = "Amount"
        pay.cell(5, 17).value = "Phone"
        pay.cell(287, 2).value = "TOTAL"
        buf = BytesIO()
        wb.save(buf)
        from app.models import ClassificationResult

        txn = CanonicalTxn(date(2026, 3, 11), "O2", Decimal("51.91"), "debit")
        klass = ClassificationResult(
            account_code="Phone",
            account_name="Phone",
            vat_code="NV",
            source="mapping",
            reason="t",
            confidence=Decimal("1"),
            needs_review=False,
            vat_amount=Decimal("0"),
            net_amount=Decimal("51.91"),
        )
        out = write_yearend_bank_tabs(buf.getvalue(), [txn], [klass], period_end=date(2026, 2, 28))
        from openpyxl import load_workbook

        written = load_workbook(BytesIO(out))
        self.assertIn("2026", str(written["Bank Pay"]["A3"].value))
        self.assertIn("Bridgit", written.sheetnames)
        self.assertEqual(written["Bank Pay"]["C8"].number_format, "0.00")
        rec = written["Bank Rec"]
        self.assertEqual(rec["E9"].value, "=Banking!C8")
        self.assertEqual(rec["E13"].value, "=E11-E12")
        self.assertIn("TIES", str(rec["E14"].value))


class VatWorkingFileTests(unittest.TestCase):
    def test_blank_template_matches_koliqi_tabs(self):
        from app.engine.ma_template import build_vat_workbook

        wb = build_vat_workbook(
            client_name="Northbridge Demo Ltd",
            period_start=date(2025, 3, 1),
            period_end=date(2026, 2, 28),
        )
        self.assertEqual(
            wb.sheetnames,
            [
                "Notes & Queries",
                "Bank Reconciliation",
                "Banking Analysis",
                "Bank Payment Analysis",
                "Sales Invoices",
                "Purchase Invoices",
                "VAT Calculation",
            ],
        )
        rec = wb["Bank Reconciliation"]
        self.assertEqual(rec["E9"].value, "='Banking Analysis'!D1000")
        self.assertEqual(rec["E13"].value, "=E11-E12")
        self.assertIn("Box 1", str(wb["VAT Calculation"]["A9"].value))

    def test_vat_write_uses_formulas_not_hardcoded_vat(self):
        from app.engine.excel_writer import write_working_file
        from app.models import ClassificationResult, ParseResult
        from openpyxl import load_workbook

        txn = CanonicalTxn(date(2026, 2, 10), "O2", Decimal("51.91"), "debit")
        klass = ClassificationResult(
            account_code="Phone",
            account_name="Phone",
            vat_code="NV",
            source="mapping",
            reason="t",
            confidence=Decimal("1"),
            needs_review=False,
            vat_amount=Decimal("0"),
            net_amount=Decimal("51.91"),
        )
        parsed = ParseResult(
            transactions=[txn],
            parser="test",
            opening_balance=Decimal("100"),
            closing_balance=Decimal("48.09"),
        )
        out = write_working_file(
            parsed,
            [txn],
            [klass],
            job_type="vat_return",
            client_name="Northbridge Demo Ltd",
            period_end=date(2026, 2, 28),
        )
        written = load_workbook(BytesIO(out))
        pay = written["Bank Payment Analysis"]
        self.assertEqual(pay["A1"].value, "Northbridge Demo Ltd")
        self.assertEqual(pay["C6"].value, "O2")
        self.assertTrue(str(pay["G6"].value).startswith("=IF"))
        self.assertEqual(pay["H6"].value, "=D6-G6")
        self.assertEqual(written["Bank Reconciliation"]["E8"].value, 100.0)


class RememberedAnswersTests(unittest.TestCase):
    def test_keep_both_does_not_reask_duplicate(self):
        from app.engine.categorise import categorise_transactions
        from app.engine.remember import duplicate_key

        a = CanonicalTxn(date(2026, 2, 14), "Tesco Stores", Decimal("86.20"), "debit")
        b = CanonicalTxn(date(2026, 2, 14), "Tesco Stores", Decimal("86.20"), "debit")
        maps = [
            {
                "description_pattern": "Tesco Stores",
                "account_name": "Motor",
                "account_code": "Motor",
                "status": "approved",
            }
        ]
        rem = {"duplicates": {duplicate_key(b): "keep_both"}}
        out = categorise_transactions(
            [a, b], maps, code_by_payee=True, remembered=rem
        )
        self.assertFalse(out[1].needs_review)
        self.assertEqual(out[1].account_name, "Motor")

    def test_coverage_stays_open_without_memory(self):
        a = CanonicalTxn(date(2026, 2, 14), "Tesco Stores", Decimal("86.20"), "debit")
        b = CanonicalTxn(date(2026, 2, 14), "Tesco Stores", Decimal("86.20"), "debit")
        maps = [
            {
                "description_pattern": "Tesco Stores",
                "account_name": "Motor",
                "account_code": "Motor",
                "status": "approved",
            }
        ]
        out = categorise_transactions([a, b], maps, code_by_payee=True)
        self.assertTrue(out[1].needs_review)
        self.assertIn("Keep both", out[1].question or "")


class ClassifyUploadTests(unittest.TestCase):
    def test_demo_csv_is_bank(self):
        path = _DEMO / "northbridge-bank.csv"
        self.assertEqual(classify_upload(path.name, path.read_bytes()), "bank")

    def test_demo_yearend_xlsx_is_comparative(self):
        path = _DEMO / "northbridge-comparative.xlsx"
        self.assertEqual(classify_upload(path.name, path.read_bytes()), "comparative")

    def test_photo_is_supporting(self):
        self.assertEqual(classify_upload("receipt.jpg", b"\xff\xd8\xff\xd9"), "supporting")

    def test_named_comparative_without_bank_tabs(self):
        wb = Workbook()
        wb.active.title = "Sheet1"
        buf = BytesIO()
        wb.save(buf)
        self.assertEqual(
            classify_upload("northbridge-comparative.xlsx", buf.getvalue()),
            "comparative",
        )


if __name__ == "__main__":
    unittest.main()
