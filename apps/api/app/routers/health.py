from fastapi import APIRouter

from app.config import settings
from app.constants import JOB_STATUSES
from app.db import db_ready

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    ready = db_ready()
    llm = "off"
    if settings.anthropic_api_key:
        llm = "anthropic-on"
    return {
        "ok": ready,
        "service": "bridgit-api",
        "database": "up" if ready else "down",
        "job_statuses": list(JOB_STATUSES),
        "llm": llm,
        "engine": "ingest+categorise+excel+resolve",
    }
