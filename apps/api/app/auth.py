"""Shared team password for the trial URL.

Not per-user auth. Cookie is an HMAC of the password, never the password itself.
Downloads (<a href>) send the cookie; JSON calls may also send X-Bridgit-Password.
"""

from __future__ import annotations

import hmac
import hashlib

from fastapi import Request, Response

from app.config import settings

COOKIE_NAME = "bridgit_session"
HEADER_NAME = "x-bridgit-password"
_SESSION_PAYLOAD = b"bridgit-session-v1"


def password_configured() -> bool:
    return bool(settings.bridgit_password)


def _digest(value: str) -> bytes:
    return hmac.new(b"bridgit-pw-check", value.encode("utf-8"), hashlib.sha256).digest()


def password_ok(pw: str | None) -> bool:
    expected = settings.bridgit_password or ""
    if not expected:
        return False
    given = pw if isinstance(pw, str) else ""
    return hmac.compare_digest(_digest(given), _digest(expected))


def session_token() -> str:
    return hmac.new(
        settings.bridgit_password.encode("utf-8"),
        _SESSION_PAYLOAD,
        hashlib.sha256,
    ).hexdigest()


def cookie_ok(value: str | None) -> bool:
    if not value or not password_configured():
        return False
    return hmac.compare_digest(value, session_token())


def request_authorized(request: Request) -> bool:
    if not password_configured():
        return True
    header = request.headers.get(HEADER_NAME) or ""
    if header and password_ok(header):
        return True
    return cookie_ok(request.cookies.get(COOKIE_NAME))


def set_session_cookie(response: Response) -> None:
    response.set_cookie(
        COOKIE_NAME,
        session_token(),
        httponly=True,
        samesite="lax",
        secure=settings.bridgit_env == "production",
        max_age=60 * 60 * 24 * 14,
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(COOKIE_NAME, path="/")


def is_protected_path(path: str) -> bool:
    if path == "/meta/chat":
        return True
    return path == "/jobs" or path.startswith("/jobs/")
