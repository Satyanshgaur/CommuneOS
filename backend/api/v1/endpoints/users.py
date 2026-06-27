"""
CommuneOS User Management Endpoints
CRUD operations for user profiles and onboarding.

NOTE: Static routes (/config, /) MUST be declared before /{user_id} wildcard.
"""
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form

from api.v1.dependencies import get_request_id, validate_user_id_param
from models.user import UserCreateRequest, UserProfile
from services.cache_service import cache_service
from services.mock_data import get_mock_user, list_mock_users, save_mock_user
from services.supabase_service import upsert_profile, fetch_profile
from services.resume_service import process_and_index_resume
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
    Create a new user profile (JSON endpoint).
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


@router.post("/{user_id}/onboard", status_code=status.HTTP_200_OK)
async def onboard_user(
    user_id: str,
    username: str = Form(...),
    bio: str = Form(...),
    current_role: str = Form(...),
    skill_level: str = Form(...),
    interests: str = Form(...),
    goals: str = Form(...),
    resume: Optional[UploadFile] = File(None),
    request_id: str = Depends(get_request_id),
) -> Dict[str, Any]:
    """
    Onboard a user by saving their profile details and optional resume.
    Processes the resume (text extraction, extraction agent, chunking, indexing)
    and saves the user profile.
    """
    interests_list = [i.strip() for i in interests.split(",") if i.strip()]
    goals_list = [g.strip() for g in goals.split(",") if g.strip()]

    user_dict = {
        "user_id": user_id,
        "username": username,
        "bio": bio,
        "current_role": current_role,
        "skill_level": skill_level,
        "interests": interests_list,
        "goals": goals_list,
        "tags": interests_list,
        "skills": {},
        "updated_at": datetime.utcnow().isoformat(),
        "created_at": datetime.utcnow().isoformat(),
        "role": "member",
    }

    # Process resume if provided
    resume_extracted = None
    if resume:
        try:
            logger.info(f"Received resume upload: {resume.filename} for {user_id}")
            resumes_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "resumes")
            os.makedirs(resumes_dir, exist_ok=True)
            
            pdf_path = os.path.join(resumes_dir, f"{user_id}.pdf")
            with open(pdf_path, "wb") as f:
                f.write(await resume.read())
            
            # Run resume extraction and chunking pipeline
            resume_data = await process_and_index_resume(pdf_path, user_id)
            parsed_json = resume_data["parsed_json"]
            
            # Merge extracted skills into profile
            extracted_skills = parsed_json.get("skills", []) or parsed_json.get("programming languages", [])
            if isinstance(extracted_skills, list) and extracted_skills:
                user_dict["skills"] = {s: 4 for s in extracted_skills}
                user_dict["tags"] = list(set(user_dict["tags"] + extracted_skills))
                
            user_dict["resume_extracted_json"] = parsed_json
            user_dict["resume_filename"] = resume.filename
            resume_extracted = parsed_json
            logger.info(f"Resume processed successfully for {user_id}")
        except Exception as e:
            logger.error(f"Error processing resume: {e}", exc_info=True)
            # Don't fail the whole onboarding if resume parsing fails, but log it

    save_mock_user(user_id, user_dict)
    cache_service.clear_prefix(f"user:{user_id}")
    cache_service.clear_prefix("agent:")

    # Persist to Supabase
    import asyncio
    asyncio.create_task(upsert_profile(user_dict))

    return success_response(
        data={
            "user_id": user_id,
            "username": username,
            "resume_extracted": resume_extracted,
            "onboarded": True
        },
        request_id=request_id,
        message="Onboarding profile completed successfully"
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
