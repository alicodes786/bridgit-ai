from datetime import date
from decimal import Decimal
from io import BytesIO
import unittest

from openpyxl import Workbook, load_workbook

from app.engine.categorise import vat_split
from app.engine.excel_writer import BANKING, DATA_START, PAYMENTS, write_working_file
from app.engine.exceptions import exception_kind, is_duplicate_question
from app.engine.pdf_summary import build_summary_pdf
from app.models import CanonicalTxn, ClassificationResult, ParseResult


def _blank_template() -> bytes:
    wb = Workbook()
    wb.active.title = BANKING
    wb.create_sheet(PAYMENTS)
    wb.create_sheet("Bank Reconciliation")
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _txn(desc: str, amount: str = "10.00", **kwargs) -> CanonicalTxn:
    return CanonicalTxn(
        txn_date=date(2026, 8, 8),
        description=desc,
        amount=Decimal(amount),
        debit_credit="debit",
        payment_type="CARD",
        **kwargs,
    )


def _klass(**kwargs) -> ClassificationResult:
    defaults = dict(
        account_code="Motor",
        account_name="Motor",
        vat_code="SR",
        source="mapping",
        reason="test",
        confidence=Decimal("1.00"),
        needs_review=False,
        vat_amount=Decimal("1.67"),
        net_amount=Decimal("8.33"),
    )
    defaults.update(kwargs)
    return ClassificationResult(**defaults)


class ExceptionKindTests(unittest.TestCase):
    def test_duplicate_from_question(self):
        q = "PAYBYPHONE £1.50 on 08 Aug 2026 matches line 3 (same date, amount, description). Keep both, or is one a repeat?"
        self.assertTrue(is_duplicate_question(q))
        self.assertEqual(exception_kind(q, "human"), "duplicate")

    def test_mapping_review(self):
        self.assertEqual(exception_kind("Business or personal?", "mapping"), "mapping_review")

    def test_llm(self):
        self.assertEqual(exception_kind("Business or personal?", "llm"), "llm")

    def test_strips_review_flag(self):
        from app.engine.exceptions import clean_account_name

        self.assertEqual(
            clean_account_name("Personal / drawings \u2013 REVIEW"),
            "Personal / drawings",
        )
        self.assertEqual(clean_account_name("Motor (personal?)"), "Motor")


class VatSplitTests(unittest.TestCase):
    def test_standard_rate(self):
        vat, net = vat_split(Decimal("12.00"), "SR")
        self.assertEqual(vat + net, Decimal("12.00"))
        self.assertGreater(vat, Decimal("0"))

    def test_no_vat(self):
        vat, net = vat_split(Decimal("12.00"), "NV")
        self.assertEqual(vat, Decimal("0.00"))
        self.assertEqual(net, Decimal("12.00"))


class WorkingFileTests(unittest.TestCase):
    def test_duplicate_lines_are_written(self):
        a = _txn("PAYBYPHONE")
        b = _txn("PAYBYPHONE")
        parsed = ParseResult(transactions=[a, b], parser="test")
        klasses = [
            _klass(),
            _klass(needs_review=True, duplicate_of_row=1, question="matches line 1. Keep both?"),
        ]
        raw = write_working_file(parsed, [a, b], klasses, template_bytes=_blank_template())
        wb = load_workbook(BytesIO(raw))
        ws = wb[PAYMENTS]
        written = [ws.cell(DATA_START, 3).value, ws.cell(DATA_START + 1, 3).value]
        self.assertEqual(written, ["PAYBYPHONE", "PAYBYPHONE"])


class PdfSummaryTests(unittest.TestCase):
    def test_builds_bytes(self):
        pdf = build_summary_pdf(
            {
                "title": "Dashboard test",
                "client_name": "Koliqi",
                "status": "needs_input",
                "transactions": [{"ai_transaction_classifications": [{"needs_review": False}]}],
                "exceptions": [{"question": "Business or personal?"}],
            }
        )
        self.assertTrue(pdf.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
