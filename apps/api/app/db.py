from functools import lru_cache

from supabase import Client, create_client

from app.config import settings


class SupabaseNotConfigured(RuntimeError):
    pass


@lru_cache(maxsize=1)
def get_supabase() -> Client:
    url = settings.supabase_url.strip()
    key = settings.supabase_service_role_key.strip()
    if not url or not key:
        raise SupabaseNotConfigured(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env"
        )
    return create_client(url, key)


def db_ready() -> bool:
    try:
        get_supabase().table("ai_jobs").select("id").limit(1).execute()
        return True
    except Exception:
        return False
