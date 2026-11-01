import logging

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.constants import MAX_UPLOAD_BYTES
from app.db import SupabaseNotConfigured
from app.job_intake import JOB_TYPES, classify_upload, normalize_job_type, parse_iso_date
from app import jobs_store
from app.engine.pdf_summary import build_summary_pdf
from app.engine.chat import ChatError, handle_chat
from app.engine.process_job import process_job
from app.engine.resolve import ResolveError, resolve_exception

# Resolve + PDF summary are the Week 1 teach-as-we-go loop.

log = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["jobs"])


def _run_process(job_id: str) -> None:
    try:
        process_job(job_id)
    except Exception:
        log.exception("background process_job failed for %s", job_id)


class ResolveBody(BaseModel):
    action: str = Field(..., min_length=1)
    account_name: str | None = None
    vat_code: str | None = None


class ChatBody(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)


def _db_error(exc: Exception) -> HTTPException:
    if isinstance(exc, SupabaseNotConfigured):
        return HTTPException(status_code=503, detail=str(exc))
    return HTTPException(status_code=502, detail=f"database error: {exc}")


def _read_upload(content: bytes, *, label: str) -> bytes:
    if not content:
        raise HTTPException(status_code=400, detail=f"{label} is empty")
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail=f"{label} is too large (max 25MB)")
    return content


@router.get("/meta/types")
def list_job_types():
    return {"job_types": [{"id": k, "label": label} for k, label in JOB_TYPES]}


@router.get("/meta/clients")
def list_clients_meta():
    try:
        return {"clients": jobs_store.list_client_names()}
    except Exception as exc:
        raise _db_error(exc) from exc


@router.post("")
async def create_job(
    title: str = Form("Untitled job"),
    client_name: str = Form("Unknown client"),
    period: str | None = Form(None),
    job_type: str | None = Form(None),
    period_start: str | None = Form(None),
    period_end: str | None = Form(None),
    bank_file: UploadFile | None = File(None),
    comparative_file: UploadFile | None = File(None),
    supporting_files: list[UploadFile] | None = File(default=None),
):
    try:
        job = jobs_store.create_job(
            title=title,
            client_name=client_name,
            period=period,
            job_type=normalize_job_type(job_type) if (job_type or "").strip() else None,
            period_start=period_start if parse_iso_date(period_start) else None,
            period_end=period_end if parse_iso_date(period_end) else None,
        )
        if bank_file is not None and bank_file.filename:
            content = _read_upload(await bank_file.read(), label="Bank file")
            jobs_store.attach_job_file(
                job["id"],
                file_name=bank_file.filename,
                content=content,
                kind="bank",
            )
        if comparative_file is not None and comparative_file.filename:
            content = _read_upload(await comparative_file.read(), label="Comparative file")
            jobs_store.attach_job_file(
                job["id"],
                file_name=comparative_file.filename,
                content=content,
                kind="comparative",
            )
        extras = supporting_files or []
        if extras and not isinstance(extras, list):
            extras = [extras]
        for extra in extras:
            if extra is None or not extra.filename:
                continue
            content = _read_upload(await extra.read(), label=extra.filename)
            jobs_store.attach_job_file(
                job["id"],
                file_name=extra.filename,
                content=content,
                kind="supporting",
            )
        return jobs_store.get_job(job["id"])
    except HTTPException:
        raise
    except Exception as exc:
        raise _db_error(exc) from exc


@router.get("/{job_id}/suggested-accounts")
def job_suggested_accounts(job_id: str):
    try:
        if not jobs_store.get_job(job_id):
            raise HTTPException(status_code=404, detail="not_found")
        return {"accounts": jobs_store.suggested_accounts_for_job(job_id)}
    except HTTPException:
        raise
    except Exception as exc:
        raise _db_error(exc) from exc


@router.get("/{job_id}")
def get_job(job_id: str):
    try:
        job = jobs_store.get_job(job_id)
    except Exception as exc:
        raise _db_error(exc) from exc
    if not job:
        raise HTTPException(status_code=404, detail="not_found")
    return job


def _same_as_latest(job: dict, kind: str, content: bytes) -> bool:
    doc = jobs_store.latest_document(job, kind)
    if not doc or not doc.get("storage_path"):
        return False
    try:
        existing = jobs_store.download_storage_bytes(doc["storage_path"])
    except Exception:
        return False
    return existing == content


def _attach_uploads(job: dict, uploads: list[tuple[str, bytes]]) -> tuple[list[dict], list[dict]]:
    attached = []
    skipped = []
    job_id = job["id"]
    for file_name, content in uploads:
        kind = classify_upload(file_name, content)
        if kind in {"bank", "comparative"} and _same_as_latest(job, kind, content):
            skipped.append({"file_name": file_name, "kind": kind, "same": True})
            continue
        jobs_store.attach_job_file(
            job_id,
            file_name=file_name,
            content=content,
            kind=kind,
        )
        attached.append({"file_name": file_name, "kind": kind})
        job.setdefault("documents", []).append({"kind": kind, "file_name": file_name})
    return attached, skipped


def _files_reply(
    attached: list[dict],
    skipped: list[dict],
    *,
    process_started: bool,
) -> str:
    lines = []
    for item in skipped:
        name = item.get("file_name") or "file"
        kind = item.get("kind")
        if kind == "bank":
            lines.append(
                f"{name} is already the bank file on this job. I have not asked the questions again."
            )
        else:
            lines.append(f"{name} is already on this job. Nothing new to process.")
    for item in attached:
        kind = item.get("kind") or "supporting"
        name = item.get("file_name") or "file"
        if kind == "bank":
            lines.append(f"{name} is the bank file. I will code the lines from it.")
        elif kind == "comparative":
            lines.append(
                f"{name} is last year's Excel. I will reuse payee columns from it on this job."
            )
        else:
            lines.append(
                f"{name} is extra paper. It stays on the job; I do not read it line by line yet."
            )
    if process_started:
        lines.append("Processing the bank / last-year file now. That can take a minute.")
    if not lines:
        return "No files were attached."
    return " ".join(lines)


@router.post("/{job_id}/files")
async def attach_job_files(
    job_id: str,
    background_tasks: BackgroundTasks,
    files: list[UploadFile] | None = File(default=None),
    note: str | None = Form(None),
):
    """Upload after the job exists (chat paperclip). Same kinds as New job."""
    try:
        job = jobs_store.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="not_found")
        incoming = files or []
        if incoming and not isinstance(incoming, list):
            incoming = [incoming]
        uploads: list[tuple[str, bytes]] = []
        for item in incoming:
            if item is None or not item.filename:
                continue
            content = _read_upload(await item.read(), label=item.filename)
            uploads.append((item.filename, content))
        if not uploads:
            raise HTTPException(status_code=400, detail="Attach at least one file.")
        attached, skipped = _attach_uploads(job, uploads)
        names = ", ".join(a["file_name"] for a in attached + skipped)
        user_text = (note or "").strip()
        kick = any(a["kind"] in {"bank", "comparative"} for a in attached)
        already = job.get("status") == "processing"
        process_started = False
        if kick and not already:
            jobs_store.set_job_status(job_id, "processing", reason="file uploaded on chat")
            background_tasks.add_task(_run_process, job_id)
            process_started = True
        reply = _files_reply(attached, skipped, process_started=process_started)
        if user_text:
            chat_out = handle_chat(job_id, f"{user_text}\n(Attached: {names})")
            extra = (chat_out.get("reply") or "").strip()
            reply = (reply + " " + extra).strip() if extra else reply
            fresh = chat_out.get("job") or jobs_store.get_job(job_id) or job
        else:
            jobs_store.append_job_chat(job_id, role="user", text=f"Uploaded {names}")
            jobs_store.append_job_chat(
                job_id, role="assistant", text=reply, extra={"source": "upload"}
            )
            fresh = jobs_store.get_job(job_id) or job
        return {
            "job": fresh,
            "attached": attached,
            "process_started": process_started,
            "reply": reply,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise _db_error(exc) from exc


@router.post("/{job_id}/process")
def process_existing_job(job_id: str, background_tasks: BackgroundTasks):
    try:
        job = jobs_store.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="not_found")
        if job.get("status") == "processing":
            return job
        jobs_store.set_job_status(job_id, "processing", reason="engine started in background")
        background_tasks.add_task(_run_process, job_id)
        return jobs_store.get_job(job_id) or {"id": job_id, "status": "processing"}
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Could not start processing. Retry from the job page.",
        ) from None


@router.post("/{job_id}/approve")
def approve_existing_job(job_id: str):
    try:
        if not jobs_store.get_job(job_id):
            raise HTTPException(status_code=404, detail="not_found")
        return jobs_store.approve_job(job_id)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise _db_error(exc) from exc


@router.delete("/{job_id}")
def remove_job(job_id: str):
    try:
        if not jobs_store.delete_job(job_id):
            raise HTTPException(status_code=404, detail="not_found")
        return {"ok": True, "id": job_id}
    except HTTPException:
        raise
    except Exception as exc:
        raise _db_error(exc) from exc


@router.get("/{job_id}/working-file")
def download_working_file(job_id: str):
    try:
        job = jobs_store.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="not_found")
        docs = [d for d in job.get("documents") or [] if d.get("kind") == "working_file"]
        if not docs:
            raise HTTPException(status_code=404, detail="no_working_file")
        docs.sort(key=lambda d: d.get("created_at") or "")
        doc = docs[-1]
        content = jobs_store.download_storage_bytes(doc["storage_path"])
        filename = jobs_store.download_filename(doc.get("file_name"), "bridgit-working-file.xlsx")
        return Response(
            content=content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise _db_error(exc) from exc


@router.get("/{job_id}/summary.pdf")
def download_summary_pdf(job_id: str):
    try:
        job = jobs_store.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="not_found")
        content = build_summary_pdf(job)
        name = jobs_store.download_filename(
            f"bridgit-summary-{job_id[:8]}.pdf",
            "bridgit-summary.pdf",
        )
        return Response(
            content=content,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{name}"'},
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"summary error: {exc}") from exc


@router.post("/{job_id}/chat")
def chat_on_job(job_id: str, body: ChatBody):
    try:
        if not jobs_store.get_job(job_id):
            raise HTTPException(status_code=404, detail="not_found")
        return handle_chat(job_id, body.message)
    except HTTPException:
        raise
    except ChatError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ResolveError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Chat failed. Try again, or use the Cards view to answer.",
        ) from None


@router.post("/{job_id}/exceptions/{exception_id}/resolve")
def resolve_job_exception(job_id: str, exception_id: str, body: ResolveBody):
    try:
        if not jobs_store.get_job(job_id):
            raise HTTPException(status_code=404, detail="not_found")
        return resolve_exception(
            job_id,
            exception_id,
            action=body.action,
            account_name=body.account_name,
            vat_code=body.vat_code,
        )
    except HTTPException:
        raise
    except ResolveError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"resolve error: {exc}") from exc


@router.get("")
def list_jobs():
    try:
        return {
            "jobs": jobs_store.list_jobs(),
            "statuses": list(jobs_store.allowed_statuses()),
        }
    except Exception as exc:
        raise _db_error(exc) from exc
