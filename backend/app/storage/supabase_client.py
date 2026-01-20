"""
Supabase client utility for database operations.
"""
from typing import Optional
from app.core.config import settings

# Lazy-load Supabase client to avoid import errors blocking server startup
_supabase_client: Optional[any] = None


def get_supabase():
    """Get or create Supabase client instance."""
    global _supabase_client
    if _supabase_client is None:
        from supabase import create_client
        _supabase_client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
    return _supabase_client
