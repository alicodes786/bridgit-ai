from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.engine.categorise import categorise_transactions
from app.engine.excel_writer import bank_rec_check, trial_balance_check, write_working_file
from app.engine.pdf_summary import build_summary_pdf
from app.ingest import parse_bank_file
from app.job_intake import (
    check_missing_documents,
    effective_job_type,
    parse_iso_date,
    period_coverage_question,
)
from app.engine.payee import merge_payee_mappings
from app.engine.remember import load as load_remembered
from app.engine.yearend_map import is_yearend_pack, mappings_from_workbook_bytes
from app.jobs_store import (
    attach_output_file,
    download_storage_bytes,
    get_job,
    insert_job_questions,
    latest_document,
    list_client_mappings,
    list_client_rules,
    replace_job_results,
    rule_flag,
    save_job_engine,
    save_job_intake,
    seed_client_mappings,
    set_job_status,
    set_job_type,
)

log = logging.getLogger(__name__)

_PROCESS_FAIL = "Processing failed. Check the bank file and retry."


def process_job(job_id: str) -> dict:
    try:
        return _process_job(job_id)
    except ValueError:
        raise
    except Exception:
        log.exception("process_job failed")
        try:
            prior = dict((get_job(job_id) or {}).get("engine") or {})
            prior["last_error"] = _PROCESS_FAIL
            save_job_engine(job_id, prior)
        except Exception:
            save_job_engine(job_id, {"last_error": _PROCESS_FAIL})
        try:
            set_job_status(job_id, "queued", reason="process failed — retry")
        except Exception:
            pass
        raise RuntimeError(_PROCESS_FAIL) from None


def _process_job(job_id: str) -> dict:
    job = get_job(job_id)
    if not job:
        raise ValueError("job not found")

    period_start = parse_iso_date(str(job.get("period_start") or "") or None)
    period_end = parse_iso_date(str(job.get("period_end") or "") or None)

    comparative = latest_document(job, "comparative")
    template_bytes = None
    extracted: list[dict] = []
    yearend_pack = False
    if comparative:
        template_bytes = download_storage_bytes(comparative["storage_path"])
        yearend_pack = is_yearend_pack(template_bytes)
        if yearend_pack:
            extracted = mappings_from_workbook_bytes(template_bytes)

    job_type = effective_job_type(job.get("job_type"), yearend_pack=yearend_pack)
    if yearend_pack and job.get("job_type") != job_type:
        set_job_type(job_id, job_type)

    remembered = load_remembered(job)
    waived = set(remembered.get("waived_kinds") or [])
    intake = check_missing_documents(
        job_type=job_type,
        documents=job.get("documents"),
        period_start=period_start,
        period_end=period_end,
    )
    save_job_intake(job_id, intake.as_dict())
    insert_job_questions(
        job_id,
        [m.question for m in intake.required_missing if m.kind not in waived],
    )

    bank_doc = latest_document(job, "bank")
    if not bank_doc:
        set_job_status(
            job_id,
            "needs_input",
            reason="intake: bank file missing — asked, not blocked forever",
        )
        job = get_job(job_id)
        job["intake"] = intake.as_dict()
        engine = {"last_error": None, "coded": 0, "exceptions": 0}
        save_job_engine(job_id, engine)
        job["engine"] = engine
        return job

    set_job_status(job_id, "processing", reason="engine started")
    content = download_storage_bytes(bank_doc["storage_path"])
    parsed = parse_bank_file(bank_doc.get("file_name") or "bank.bin", content)

    coverage = period_coverage_question(
        parsed.transactions,
        period_start=period_start,
        period_end=period_end,
    )
    if coverage and remembered.get("coverage_ok"):
        coverage = None
    if coverage:
        intake.coverage_question = coverage
        save_job_intake(job_id, intake.as_dict())
        insert_job_questions(job_id, [coverage])

    rules = list_client_rules(job.get("client_id"), job_type=job_type)
    code_by_payee = rule_flag(rules, "code_by_payee") or job_type == "company_accounts"
    if extracted:
        try:
            seed_client_mappings(job.get("client_id"), extracted)
        except Exception:
            pass

    mappings = merge_payee_mappings(list_client_mappings(job.get("client_id")), extracted)
    classifications = categorise_transactions(
        parsed.transactions,
        mappings,
        client_name=job.get("client_name") or "",
        code_by_payee=code_by_payee,
        ask_unmatched=code_by_payee,
        remembered=remembered,
    )

    rec = bank_rec_check(parsed, parsed.transactions)
    tb = trial_balance_check(parsed.transactions)
    open_exceptions = sum(1 for c in classifications if c.needs_review and c.question)
    coded = sum(1 for c in classifications if not c.needs_review)
    notes = [
        f"{coded} of {len(parsed.transactions)} bank lines auto-coded from prior mappings.",
        (
            f"{open_exceptions} line(s) still need an accountant (yellow on the analysis tabs)."
            if open_exceptions
            else "All bank lines have a category."
        ),
        (
            f"Bank rec difference £{rec.get('difference')}."
            if rec.get("difference") is not None
            else "Bank rec: opening/closing not on the statement parse."
        ),
        "This is the bank working file. It is not a finished statutory pack.",
    ]

    excel_bytes = write_working_file(
        parsed,
        parsed.transactions,
        classifications,
        template_bytes=template_bytes,
        job_type=job_type,
        period_start=period_start,
        period_end=period_end,
        client_name=job.get("client_name"),
        notes=notes,
    )
    attach_output_file(
        job_id,
        file_name=f"bridgit-working-file-{job_id[:8]}.xlsx",
        content=excel_bytes,
        kind="working_file",
    )

    replace_job_results(
        job_id,
        transactions=parsed.transactions,
        classifications=classifications,
    )
    still_missing = [m for m in intake.required_missing if m.kind not in waived]
    insert_job_questions(
        job_id,
        [m.question for m in still_missing] + ([coverage] if coverage else []),
    )

    missing_n = len(still_missing) + (1 if coverage else 0)

    if not rec["ok"] or not tb["ok"]:
        status = "needs_input"
        reason = "hard gate failed (bank rec or trial balance)"
    elif open_exceptions or missing_n:
        status = "needs_input"
        reason = f"{open_exceptions} line questions, {missing_n} document/period questions"
    else:
        status = "ready_for_review"
        reason = "all lines coded; hard gates passed"

    set_job_status(job_id, status, reason=reason)
    job = get_job(job_id)
    pdf = build_summary_pdf(job)
    attach_output_file(
        job_id,
        file_name=f"bridgit-summary-{job_id[:8]}.pdf",
        content=pdf,
        kind="summary_pdf",
        content_type="application/pdf",
    )
    job = get_job(job_id)
    job["intake"] = intake.as_dict()
    engine = {
        "parser": parsed.parser,
        "transaction_count": len(parsed.transactions),
        "coded": coded,
        "exceptions": open_exceptions,
        "warnings": parsed.warnings,
        "bank_rec": rec,
        "trial_balance": tb,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "code_by_payee": code_by_payee,
        "comparative_payees": len(extracted),
        "mappings_used": len(mappings),
        "job_type": job_type,
        "yearend_pack": yearend_pack,
        "last_error": None,
        "remembered": remembered,
    }
    save_job_engine(job_id, engine)
    job["engine"] = engine
    return job
