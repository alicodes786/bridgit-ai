from pathlib import Path

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.engine.chat import ChatError, handle_workspace_chat
from app.auth import (
    clear_session_cookie,
    is_protected_path,
    password_configured,
    password_ok,
    request_authorized,
    set_session_cookie,
)
from app.config import settings
from app.pipeline import STAGES
from app.routers import health, jobs

_STATIC = Path(__file__).resolve().parent / "static"

_DEFAULT_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8001",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8001",
]


def _cors_origins() -> list[str]:
    extra = [
        o.strip()
        for o in (settings.bridgit_cors_origins or "").split(",")
        if o.strip()
    ]
    return list(dict.fromkeys(_DEFAULT_ORIGINS + extra))


app = FastAPI(title="Bridgit AI", version="0.1.0")


@app.middleware("http")
async def require_bridgit_password(request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)
    if password_configured() and is_protected_path(request.url.path):
        if not request_authorized(request):
            return JSONResponse({"detail": "unauthorized"}, status_code=401)
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory=_STATIC), name="static")
app.include_router(health.router)
app.include_router(jobs.router)


@app.get("/")
def home():
    return RedirectResponse("/app", status_code=307)


@app.get("/app")
def client_app():
    return FileResponse(_STATIC / "app.html")


@app.get("/board")
def dashboard():
    return FileResponse(_STATIC / "dashboard.html")


@app.get("/meta/app")
def app_meta():
    production = settings.bridgit_env == "production"
    return {
        "password_required": password_configured(),
        "env": settings.bridgit_env,
        "show_demo": not production,
    }


class PasswordBody(BaseModel):
    pw: str = ""


class WorkspaceChatBody(BaseModel):
    message: str = ""
    history: list[dict] = []


@app.post("/meta/chat")
def workspace_chat(body: WorkspaceChatBody):
    try:
        reply = handle_workspace_chat(body.message, body.history)
    except ChatError as exc:
        return JSONResponse({"detail": str(exc)}, status_code=400)
    return {"reply": reply}


@app.post("/meta/password-check")
def password_check(body: PasswordBody, response: Response):
    if not password_configured():
        return {"ok": False, "warning": "no_password_configured"}
    if not password_ok(body.pw):
        return {"ok": False}
    set_session_cookie(response)
    return {
        "ok": True,
        "env": settings.bridgit_env,
        "show_demo": settings.bridgit_env != "production",
    }


@app.post("/meta/logout")
def logout(response: Response):
    clear_session_cookie(response)
    return {"ok": True}


@app.get("/pipeline")
def pipeline():
    """Stage copy for the board. Reload this module after copy edits."""
    return {"stages": STAGES}
