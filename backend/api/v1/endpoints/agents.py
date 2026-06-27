"""
CommuneOS Agent Orchestration Endpoints
Triggers agent pipelines and returns personalization data.

Pipeline has a hard timeout - falls back to rich mock data if LLM is slow.
"""
import asyncio
import time
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from api.v1.dependencies import get_request_id, validate_user_id_param
from services import (
    run_member_pipeline, run_community_pipeline, get_mock_user
)
from utils.formatters import success_response
from utils.logger import get_logger

router = APIRouter(prefix="/agents", tags=["Agents"])
logger = get_logger("endpoint.agents")
limiter = Limiter(key_func=get_remote_address)

# In-memory status store for polling
_pipeline_status: Dict[str, Dict] = {}


@router.post("/personalize/{user_id}")
@limiter.limit("10/minute")
async def personalize_member(
    request: Request,
    user_id: str = Depends(validate_user_id_param),
    request_id: str = Depends(get_request_id),
) -> Dict[str, Any]:
    """
    Run the complete member personalization pipeline.

    Executes: Identity → (Discovery + Learning in parallel) → Mentor
    Hard timeout: 45 seconds — falls back to rich mock data if LLM is slow.

    Returns full personalization profile:
    - Detected skills and learning preferences
    - Recommended channels and resources
    - Personalized learning roadmap
    - Best mentor match
    """
    # Check cache first — return immediately if available
    from services.cache_service import cache_service
    cache_key = cache_service.agent_key("personalization", user_id)
    cached = cache_service.get(cache_key)
    if cached:
        logger.info(f"Personalization cache hit for {user_id}")
        return success_response(data=cached, request_id=request_id, message="Personalization (cached)")

    user_data = get_mock_user(user_id)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' not found. Create via POST /api/v1/users/create",
        )

    _pipeline_status[user_id] = {
        "status": "running", "progress_percent": 10,
        "current_agent": "orchestrator", "user_id": user_id,
        "started_at": time.time(),
    }

    try:
        profile = await run_member_pipeline(user_id, user_data)
        _pipeline_status[user_id].update({
            "status": "completed", "progress_percent": 100, "current_agent": None,
        })
        return success_response(
            data=profile, request_id=request_id, message="Personalization complete"
        )
    except Exception as e:
        logger.error(f"Pipeline failed for {user_id}: {e}", exc_info=True)
        _pipeline_status[user_id]["status"] = "failed"
        # run_member_pipeline has its own fallback so it shouldn't raise normally,
        # but if it does, return mock data
        from services.mock_data import get_mock_identity, get_mock_discovery, get_mock_learning, get_mock_mentor
        identity = get_mock_identity(user_id, user_data)
        discovery = get_mock_discovery(user_id, identity)
        learning = get_mock_learning(user_id, identity)
        mentor = get_mock_mentor(user_id, identity)
        profile = {
            "user_id": user_id,
            "identity": identity,
            "discovery": discovery,
            "learning": learning,
            "mentor": mentor,
            "pipeline_time_ms": 0,
            "is_partial": False,
            "fallback_used": True,
        }
        return success_response(
            data=profile, request_id=request_id,
            message="Personalization complete (fallback)"
        )


@router.get("/status/{user_id}")
async def get_agent_status(
    user_id: str = Depends(validate_user_id_param),
    request_id: str = Depends(get_request_id),
) -> Dict[str, Any]:
    """
    Poll the status of a running agent pipeline.
    Status: pending | running | completed | failed
    """
    status_data = _pipeline_status.get(user_id, {
        "status": "pending", "progress_percent": 0,
        "current_agent": None, "user_id": user_id,
    })
    return success_response(data=status_data, request_id=request_id)


@router.post("/refresh/{user_id}")
@limiter.limit("10/minute")
async def refresh_personalization(
    request: Request,
    user_id: str = Depends(validate_user_id_param),
    request_id: str = Depends(get_request_id),
) -> Dict[str, Any]:
    """Force-refresh personalization by clearing cache and re-running the pipeline."""
    user_data = get_mock_user(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")

    from services.cache_service import cache_service
    cache_service.clear_prefix("agent:")
    logger.info(f"Force-refresh for {user_id}")

    _pipeline_status[user_id] = {
        "status": "running", "progress_percent": 10,
        "current_agent": "orchestrator", "user_id": user_id,
        "started_at": time.time(),
    }

    try:
        profile = await run_member_pipeline(user_id, user_data)
        _pipeline_status[user_id].update({
            "status": "completed", "progress_percent": 100, "current_agent": None,
        })
        return success_response(data=profile, request_id=request_id, message="Personalization refreshed")
    except Exception as e:
        logger.error(f"Refresh failed for {user_id}: {e}", exc_info=True)
        _pipeline_status[user_id]["status"] = "failed"
        from services.mock_data import get_mock_identity, get_mock_discovery, get_mock_learning, get_mock_mentor
        identity = get_mock_identity(user_id, user_data)
        discovery = get_mock_discovery(user_id, identity)
        learning = get_mock_learning(user_id, identity)
        mentor = get_mock_mentor(user_id, identity)
        profile = {
            "user_id": user_id,
            "identity": identity,
            "discovery": discovery,
            "learning": learning,
            "mentor": mentor,
            "pipeline_time_ms": 0,
            "is_partial": False,
            "fallback_used": True,
        }
        return success_response(data=profile, request_id=request_id, message="Personalization refreshed (fallback)")


@router.post("/community/health")
async def run_community_health(request_id: str = Depends(get_request_id)) -> Dict[str, Any]:
    """
    Run community health + organizer pipeline.
    Executes: Health Agent → Organizer Agent
    Hard timeout: 30 seconds.
    """
    try:
        combined = await run_community_pipeline()
        return success_response(data=combined, request_id=request_id)
    except Exception as e:
        logger.error(f"Community health pipeline failed: {e}", exc_info=True)
        # As fallback, return mock health/organizer directly
        from services.mock_data import get_mock_health, get_mock_organizer
        combined = {
            "health": get_mock_health(),
            "actions": get_mock_organizer(),
            "fallback_used": True,
        }
        return success_response(data=combined, request_id=request_id, message="Community health complete (fallback)")
