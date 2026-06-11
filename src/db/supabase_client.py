"""Supabase client setup and utilities."""

from supabase import create_client, Client
from typing import Optional
import logging

from ..config import get_settings

logger = logging.getLogger(__name__)

# Global client instance (lazy initialization)
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Optional[Client]:
    """
    Get or create Supabase client instance.
    
    Returns None if credentials are not configured.
    """
    global _supabase_client
    
    if _supabase_client is not None:
        return _supabase_client
    
    settings = get_settings()
    
    # Check if credentials look valid
    if not settings.supabase_url or not settings.supabase_anon_key:
        logger.warning("Supabase credentials not configured")
        return None
    
    if not settings.supabase_url.startswith("https://"):
        logger.warning("Invalid Supabase URL format")
        return None
    
    try:
        _supabase_client = create_client(
            settings.supabase_url,
            settings.supabase_anon_key
        )
        logger.info("Supabase client initialized")
        return _supabase_client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        return None


async def is_supabase_available() -> bool:
    """
    Check if Supabase is available and connected.
    
    Returns True if client can be created and credentials are valid.
    """
    client = get_supabase_client()
    return client is not None


def reset_supabase_client():
    """Reset the global client instance (useful for testing)."""
    global _supabase_client
    _supabase_client = None
