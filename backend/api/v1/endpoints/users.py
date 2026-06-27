"""
CommuneOS User Management Endpoints
CRUD operations for user profiles.

NOTE: Static routes (/config, /) MUST be declared before /{user_id} wildcard.
"""
import uuid
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from api.v1.dependencies import get_request_id, validate_user_id_param
from models.user import UserCreateRequest, UserProfile
from services.cache_service import cache_service
from services.mock_data import get_mock_user, list_mock_users, save_mock_user
from services.supabase_service import upsert_profile, fetch_profile
from utils.formatters import error_response, success_response
from utils.logger import get_logger

router = APIRouter(prefix="/users", tags=["Users"])
logger = get_logger("endpoint.users")


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreateRequest,
    request_id: str = Depends(get_request_id),
) -> Dict[str, Any]:
    """
    Create a new user profile.
    Accepts basic profile data (username, bio, tags, interests, goals).
    """
    user_id = request.user_id or str(uuid.uuid4())[:8]
    profile = request.to_user_profile(user_id)

    user_dict = profile.model_dump(mode="json")
    save_mock_user(user_id, user_dict)
    cache_service.clear_prefix(f"user:{user_id}")

    # Persist to Supabase (fire-and-forget — don't block on failure)
    import asyncio
    asyncio.create_task(upsert_profile(user_dict))

    logger.info(f"Created user: {user_id} ({profile.username})")
    return success_response(
        data={"user_id": user_id, "username": profile.username, "created": True},
        request_id=request_id,
        message=f"User '{profile.username}' created successfully",
    )


# ── Static routes BEFORE /{user_id} wildcard ──────────────────────────────────

@router.get("/")
async def list_users(request_id: str = Depends(get_request_id)) -> Dict[str, Any]:
    """List all users (development/admin endpoint)."""
    users = list_mock_users()
    return success_response(
        data={"users": users, "count": len(users)},
        request_id=request_id,
    )


@router.get("/config")
async def get_config(request_id: str = Depends(get_request_id)) -> Dict[str, Any]:
    """Return Supabase config for frontend initialisation (can be empty strings)."""
    from config import settings
    return success_response(
        data={
            "supabase_url": settings.SUPABASE_URL,
            "supabase_anon_key": settings.SUPABASE_ANON_KEY,
        },
        request_id=request_id,
    )


# ── Parameterised routes ───────────────────────────────────────────────────────

@router.get("/{user_id}/profile")
async def get_user_personalization_profile(
    user_id: str = Depends(validate_user_id_param),
    request_id: str = Depends(get_request_id),
) -> Dict[str, Any]:
    """
    Get the cached personalization profile for a user.
    Call POST /agents/personalize/{user_id} first if not yet generated.
    """
    cache_key = cache_service.agent_key("personalization", user_id)
    cached = cache_service.get(cache_key)
    if cached:
        logger.info(f"Personalization profile for {user_id} from cache")
        return success_response(data=cached, request_id=request_id)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No personalization profile for '{user_id}'. Call POST /agents/personalize/{user_id} first.",
    )


@router.get("/{user_id}")
async def get_user(
    user_id: str = Depends(validate_user_id_param),
    request_id: str = Depends(get_request_id),
) -> Dict[str, Any]:
    """Retrieve a user profile by ID."""
    cache_key = cache_service.user_key(user_id)
    cached = cache_service.get(cache_key)
    if cached:
        logger.debug(f"User {user_id} from cache")
        return success_response(data=cached, request_id=request_id)

    user = get_mock_user(user_id)
    if not user:
        # Try Supabase as fallback
        user = await fetch_profile(user_id)
        if user:
            save_mock_user(user_id, user)  # warm local cache
        else:
            logger.warning(f"User not found: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{user_id}' not found",
            )

    cache_service.set(cache_key, user, ttl=1800)
    return success_response(data=user, request_id=request_id)


@router.put("/{user_id}")
async def update_user(
    update_data: Dict[str, Any],
    user_id: str = Depends(validate_user_id_param),
    request_id: str = Depends(get_request_id),
) -> Dict[str, Any]:
    """Merge update_data into existing user profile."""
    existing = get_mock_user(user_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' not found",
        )

    existing.update(update_data)
    existing["updated_at"] = datetime.utcnow().isoformat()
    save_mock_user(user_id, existing)
    cache_service.clear_prefix(f"user:{user_id}")
    cache_service.clear_prefix("agent:")

    logger.info(f"Updated user: {user_id}")
    return success_response(
        data={"user_id": user_id, "updated": True},
        request_id=request_id,
        message="Profile updated",
    )
