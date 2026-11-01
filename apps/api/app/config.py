from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

def _env_files() -> tuple[str, ...]:
    """Local repo-root .env, apps/api/.env, or cwd. Railway injects env vars."""
    here = Path(__file__).resolve()
    candidates: list[Path] = []
    for idx in (3, 1):
        try:
            candidates.append(here.parents[idx] / ".env")
        except IndexError:
            pass
    candidates.append(Path.cwd() / ".env")
    found: list[str] = []
    for path in candidates:
        try:
            if path.exists():
                text = str(path)
                if text not in found:
                    found.append(text)
        except OSError:
            continue
    return tuple(found)


def _clean(value: str) -> str:
    text = value.strip().strip('"').strip("'")
    if " #" in text:
        text = text.split(" #", 1)[0].strip()
    return text


def normalize_supabase_url(url: str) -> str:
    """Project URL only. Pasting /rest/v1 doubles the path (PGRST125)."""
    url = _clean(url).rstrip("/")
    lowered = url.lower()
    for suffix in ("/rest/v1", "/auth/v1", "/storage/v1", "/functions/v1"):
        if lowered.endswith(suffix):
            url = url[: -len(suffix)].rstrip("/")
            lowered = url.lower()
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_env_files() or None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bridgit_env: str = "local"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    bridgit_password: str = ""
    bridgit_cors_origins: str = ""

    @field_validator("supabase_url", mode="before")
    @classmethod
    def clean_url(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        return normalize_supabase_url(value)

    @property
    def supabase_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_service_role_key)


settings = Settings()
