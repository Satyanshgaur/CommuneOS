"""
CommuneOS Agent Orchestration Endpoints
Triggers agent pipelines and returns personalization data.
"""
import asyncio
import time
import uuid
from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from api.v1.dependencies import get_request_id, validate_user_id_param
from models.user import UserProfile
from services.cache_service import cache_service
from services.mock_data import (
    get_mock_user, get_mock_identity, get_mock_discovery,
    get_mock_learning, get_mock_mentor, get_mock_health, get_mock_organizer
)
from utils.formatters import success_response
from utils.logger import get_logger

router = APIRouter(prefix="/agents", tags=["Agents"])
logger = get_logger("endpoint.agents")

# In-memory status store for async pipelines
_pipeline_status: Dict[str, Dict] = {}


async def _run_personalization_pipeline(user_id: str, user_data: Dict) -> Dict:
    """
    Run the member personalization pipeline:
    Step 1: Identity Agent
    Step 2: Discovery + Learning Agents (parallel)
    Step 3: Mentor Agent
    
    Returns merged personalization profile.
    """
    from agents.identity_agent import IdentityAgent
    from agents.discovery_agent import DiscoveryAgent
    from agents.learning_agent import LearningAgent
    from agents.mentor_agent import MentorAgent

    pipeline_start = time.time()
    
    # Update status
    _pipeline_status[user_id] = {
        "status": "running", "progress_percent": 10,
        "current_agent": "identity_agent", "user_id": user_id
    }

    # Step 1: Identity Agent
    identity_agent = IdentityAgent()
    identity_result = await identity_agent.run(user_id, user_data)
    
    _pipeline_status[user_id].update({"progress_percent": 35, "current_agent": "discovery_agent+learning_agent"})

    # Step 2: Parallel — Discovery + Learning
    discovery_agent = DiscoveryAgent()
    learning_agent = LearningAgent()
    
    discovery_result, learning_result = await asyncio.gather(
        discovery_agent.run(user_id, user_data, identity_result.get("data")),
        learning_agent.run(user_id, user_data, identity_result.get("data")),
        return_exceptions=True
    )
    
    # Handle if exceptions were returned
    if isinstance(discovery_result, Exception):
        logger.error(f"Discovery agent failed: {discovery_result}")
        discovery_result = {"success": False, "data": {}, "is_fallback": True}
    if isinstance(learning_result, Exception):
        logger.error(f"Learning agent failed: {learning_result}")
        learning_result = {"success": False, "data": {}, "is_fallback": True}

    _pipeline_status[user_id].update({"progress_percent": 70, "current_agent": "mentor_agent"})

    # Step 3: Mentor Agent (needs learning output)
    mentor_agent = MentorAgent()
    mentor_result = await mentor_agent.run(
        user_id, user_data, identity_result.get("data"), learning_result.get("data")
    )

    pipeline_ms = round((time.time() - pipeline_start) * 1000, 1)
    
    any_fallback = any([
        identity_result.get("is_fallback"),
        discovery_result.get("is_fallback"),
        learning_result.get("is_fallback"),
        mentor_result.get("is_fallback"),
    ])

    profile = {
        "user_id": user_id,
        "identity": identity_result.get("data", {}),
        "discovery": discovery_result.get("data", {}),
        "learning": learning_result.get("data", {}),
        "mentor": mentor_result.get("data", {}),
        "pipeline_time_ms": pipeline_ms,
        "is_partial": not all([
            identity_result.get("success"),
            discovery_result.get("success"),
            learning_result.get("success"),
            mentor_result.get("success"),
        ]),
        "fallback_used": any_fallback,
    }

    # Cache the result
    from config import settings
    cache_service.set(
        cache_service.agent_key("personalization", user_id),
        profile,
        ttl=settings.CACHE_TTL_AGENT
    )

    _pipeline_status[user_id].update({
        "status": "completed", "progress_percent": 100,
        "current_agent": None,
    })

    logger.info(f"Personalization pipeline for {user_id} completed in {pipeline_ms}ms | fallback={any_fallback}")
    return profile


@router.post("/personalize/{user_id}")
async def personalize_member(
    user_id: str = Depends(validate_user_id_param),
    request_id: str = Depends(get_request_id),
) -> Dict[str, Any]:
    """
    Run the complete member personalization pipeline.
    
    Executes: Identity → (Discovery + Learning in parallel) → Mentor
    
    Returns the full personalization profile with:
    - Detected skills and learning preferences
    - Recommended channels and resources
    - Personalized learning roadmap
    - Best mentor match
    """
    user_data = get_mock_user(user_id)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' not found. Create the user first via POST /users/create"
        )
    
    # Initialize status
    _pipeline_status[user_id] = {
        "status": "running", "progress_percent": 0,
        "current_agent": "starting", "user_id": user_id,
        "started_at": time.time()
    }
    
    try:
        profile = await _run_personalization_pipeline(user_id, user_data)
        return success_response(data=profile, request_id=request_id, message="Personalization complete")
    except Exception as e:
        logger.error(f"Pipeline failed for {user_id}: {e}", exc_info=True)
        _pipeline_status[user_id]["status"] = "failed"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline failed: {str(e)}"
        )


@router.get("/status/{user_id}")
async def get_agent_status(
    user_id: str = Depends(validate_user_id_param),
    request_id: str = Depends(get_request_id),
) -> Dict[str, Any]:
    """
    Get the current status of an agent pipeline for a user.
    
    Use this endpoint to poll pipeline progress.
    Status values: pending | running | completed | failed
    """
    status_data = _pipeline_status.get(user_id, {
        "status": "pending", "progress_percent": 0,
        "current_agent": None, "user_id": user_id
    })
    return success_response(data=status_data, request_id=request_id)


@router.post("/refresh/{user_id}")
async def refresh_personalization(
    user_id: str = Depends(validate_user_id_param),
    request_id: str = Depends(get_request_id),
) -> Dict[str, Any]:
    """
    Force refresh the personalization profile for a user.
    
    Clears existing cache and re-runs the full pipeline.
    """
    user_data = get_mock_user(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
    
    # Clear existing cache
    cache_service.clear_prefix(f"agent:")
    logger.info(f"Refreshing personalization for {user_id}")
    
    try:
        profile = await _run_personalization_pipeline(user_id, user_data)
        return success_response(
            data=profile, request_id=request_id,
            message="Personalization refreshed"
        )
    except Exception as e:
        logger.error(f"Refresh pipeline failed for {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/community/health")
async def run_community_health(request_id: str = Depends(get_request_id)) -> Dict[str, Any]:
    """
    Run community health analysis pipeline.
    
    Executes: Health Agent → Organizer Agent
    Returns: Community health metrics + action items
    """
    from agents.health_agent import HealthAgent
    from agents.organizer_agent import OrganizerAgent

    health_agent = HealthAgent()
    health_result = await health_agent.run_community()
    
    organizer_agent = OrganizerAgent()
    organizer_result = await organizer_agent.run_community(health_result.get("data"))
    
    combined = {
        "health": health_result.get("data", {}),
        "actions": organizer_result.get("data", {}),
        "fallback_used": health_result.get("is_fallback") or organizer_result.get("is_fallback"),
    }
    
    cache_service.set(
        cache_service.community_key("health_and_actions"),
        combined,
        ttl=1800  # 30 min
    )
    
    return success_response(data=combined, request_id=request_id)
