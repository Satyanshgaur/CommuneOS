"""
Supabase profiles table — read/write via REST API.
Uses httpx (already a project dependency), no extra packages needed.
"""
import asyncio
from typing import Any, Dict, List, Optional

import httpx

from config import settings
from utils.logger import get_logger

logger = get_logger("supabase_service")

_BASE = f"{settings.SUPABASE_URL}/rest/v1"
_HEADERS = {
    "apikey": settings.SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {settings.SUPABASE_ANON_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


async def upsert_profile(user_data: Dict[str, Any]) -> bool:
    """Write (or overwrite) a user profile to the Supabase profiles table."""
    payload = {
        "user_id": user_data.get("user_id"),
        "username": user_data.get("username"),
        "bio": user_data.get("bio", ""),
        "tags": user_data.get("tags", []),
        "interests": user_data.get("interests", []),
        "goals": user_data.get("goals", []),
        "updated_at": "now()",
    }
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.post(
                f"{_BASE}/profiles",
                headers={**_HEADERS, "Prefer": "resolution=merge-duplicates,return=representation"},
                json=payload,
            )
        if r.status_code in (200, 201):
            logger.info(f"Supabase upsert OK: {payload['user_id']}")
            return True
        logger.warning(f"Supabase upsert {r.status_code}: {r.text[:200]}")
        return False
    except Exception as e:
        logger.error(f"Supabase upsert error: {e}")
        return False


async def fetch_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a profile from Supabase. Returns None if not found or on error."""
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.get(
                f"{_BASE}/profiles",
                headers=_HEADERS,
                params={"user_id": f"eq.{user_id}", "limit": "1"},
            )
        if r.status_code == 200:
            rows = r.json()
            if rows:
                return rows[0]
        return None
    except Exception as e:
        logger.error(f"Supabase fetch error: {e}")
        return None


async def fetch_all_profiles() -> List[Dict[str, Any]]:
    """Fetch all profiles (for admin/debug)."""
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.get(
                f"{_BASE}/profiles",
                headers=_HEADERS,
                params={"order": "created_at.desc"},
            )
        if r.status_code == 200:
            return r.json()
        return []
    except Exception as e:
        logger.error(f"Supabase fetch_all error: {e}")
        return []
