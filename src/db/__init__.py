"""Database module."""

from .supabase_client import get_supabase_client, is_supabase_available

__all__ = ["get_supabase_client", "is_supabase_available"]
