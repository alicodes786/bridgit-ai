"""Check the signed-in home: page has the home chat, desk chat answers."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from http.cookiejar import CookieJar
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8001"


def password() -> str:
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("BRIDGIT_PASSWORD="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("BRIDGIT_PASSWORD missing")


def main() -> None:
    jar = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

    def call(path: str, data: dict | None = None, raw: bool = False):
        body = None if data is None else json.dumps(data).encode()
        req = urllib.request.Request(
            BASE + path,
            data=body,
            headers={"Content-Type": "application/json"} if body else {},
        )
        with opener.open(req, timeout=60) as res:
            blob = res.read()
            return blob if raw else json.loads(blob.decode())

    page = call("/app", raw=True).decode("utf-8", "replace")
    missing = [token for token in ("id=\"go-home\"", "id=\"home-chat-form\"", "id=\"job-home\"", "Talk about the work") if token not in page]
    if missing:
        raise SystemExit("homepage markup missing: " + ", ".join(missing))
    print("page: home control, home chat, job home link")

    login = call("/meta/password-check", {"pw": password()})
    if not login.get("ok"):
        raise SystemExit("login failed")
    print("login: ok")

    jobs = call("/jobs")
    print("jobs:", len(jobs.get("jobs") or []))

    chat = call("/meta/chat", {"message": "how are we doing?", "history": []})
    reply = (chat.get("reply") or "").strip()
    if len(reply) < 20:
        raise SystemExit("desk chat reply too short: " + reply)
    print("desk chat:", reply[:180].replace("\n", " "))
    print("home check: ok")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.URLError as exc:
        raise SystemExit(f"could not reach {BASE}: {exc}") from exc
