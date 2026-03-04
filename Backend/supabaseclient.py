import os
from functools import lru_cache

from supabase import Client, create_client


class SupabaseConfigError(RuntimeError):
    """Raised when required Supabase environment variables are missing."""


@lru_cache(maxsize=1) # Cache the client instance for reuse across the app
def get_supabase_client() -> Client:
    """
    Build and cache a Supabase client for backend use.

    Required env vars:
    - SUPABASE_URL
    - SUPABASE_SERVICE_ROLE_KEY (preferred) or SUPABASE_KEY (legacy fallback)
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

    if not url:
        raise SupabaseConfigError("SUPABASE_URL is not set.")

    if not key:
        raise SupabaseConfigError(
            "SUPABASE_SERVICE_ROLE_KEY is not set. "
            "Use the service role key for backend requests."
        )

    return create_client(url, key)
