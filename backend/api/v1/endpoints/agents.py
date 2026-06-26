"""
CommuneOS Agent Orchestration Endpoints
Triggers agent pipelines and returns personalization data.

Pipeline has a hard 45s timeout - falls back to rich mock data if LLM is slow.
"""
import asyncio
import time
import uuid
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status

from api.v1.dependencies import get_request_id, validate_user_id_param
from config import settings
from services.cache_service import cache_service
from services.mock_data import (
    get_mock_user, get_mock_identity, get_mock_discovery,
    get_mock_learning, get_mock_mentor, get_mock_health, get_mock_organizer,
)
from utils.formatters import success_response
from utils.logger import get_logger

router = APIRouter(prefix="/agents", tags=["Agents"])
logger = get_logger("endpoint.agents")

# In-memory status store for polling
_pipeline_status: Dict[str, Dict] = {}

# Hard wall-clock cap for the full pipeline
PIPELINE_HARD_TIMEOUT = 45  # seconds


# ─── Fallback pipeline (instant, no LLM) ─────────────────────────────────────

def _build_fallback_profile(user_id: str, user_data: Dict, pipeline_ms: float = 0) -> Dict:
    """Build a complete profile instantly from mock data (no LLM calls)."""
    identity = get_mock_identity(user_id, user_data)
    identity.pop("_is_fallback", None)

    discovery = get_mock_discovery(user_id, identity)
    discovery.pop("_is_fallback", None)

    learning = get_mock_learning(user_id, identity)
    learning.pop("_is_fallback", None)

    mentor = get_mock_mentor(user_id, identity)
    mentor.pop("_is_fallback", None)

    return {
        "user_id": user_id,
        "identity": identity,
        "discovery": discovery,
        "learning": learning,
        "mentor": mentor,
        "pipeline_time_ms": pipeline_ms,
        "is_partial": False,
        "fallback_used": True,
    }


# ─── LLM pipeline (async, with hard timeout) ─────────────────────────────────

async def _run_llm_pipeline(user_id: str, user_data: Dict) -> Dict:
    """
    Run the full LLM personalization pipeline:
      Step 1: Identity Agent
      Step 2: Discovery + Learning (parallel)
      Step 3: Mentor Agent

    Each agent has its own internal timeout and falls back to mock data if LLM fails.
    The whole pipeline is also capped by PIPELINE_HARD_TIMEOUT.
    """
    from agents.identity_agent import IdentityAgent
    from agents.discovery_agent import DiscoveryAgent
    from agents.learning_agent import LearningAgent
    from agents.mentor_agent import MentorAgent

    pipeline_start = time.time()

    _pipeline_status[user_id] = {
        "status": "running", "progress_percent": 10,
        "current_agent": "identity_agent", "user_id": user_id,
    }

    # Step 1: Identity Agent (sequential — others depend on it)
    identity_result = await IdentityAgent().run(user_id, user_data)

    _pipeline_status[user_id].update({
        "progress_percent": 35,
        "current_agent": "discovery_agent + learning_agent",
    })

    # Step 2: Discovery + Learning in parallel
    disc_coro = DiscoveryAgent().run(user_id, user_data, identity_result.get("data"))
    learn_coro = LearningAgent().run(user_id, user_data, identity_result.get("data"))
    discovery_result, learning_result = await asyncio.gather(
        disc_coro, learn_coro, return_exceptions=True
    )

    if isinstance(discovery_result, Exception):
        logger.warning(f"Discovery failed, using mock: {discovery_result}")
        fallback = get_mock_discovery(user_id, user_data)
        fallback.pop("_is_fallback", None)
        discovery_result = {"success": True, "data": fallback, "is_fallback": True}

    if isinstance(learning_result, Exception):
        logger.warning(f"Learning failed, using mock: {learning_result}")
        fallback = get_mock_learning(user_id, user_data)
        fallback.pop("_is_fallback", None)
        learning_result = {"success": True, "data": fallback, "is_fallback": True}

    _pipeline_status[user_id].update({
        "progress_percent": 70,
        "current_agent": "mentor_agent",
    })

    # Step 3: Mentor Agent
    mentor_result = await MentorAgent().run(
        user_id, user_data,
        identity_result.get("data"),
        learning_result.get("data"),
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
        "is_partial": False,
        "fallback_used": any_fallback,
    }

    # Cache it
    cache_service.set(
        cache_service.agent_key("personalization", user_id),
        profile,
        ttl=settings.CACHE_TTL_AGENT,
    )

    _pipeline_status[user_id].update({
        "status": "completed", "progress_percent": 100, "current_agent": None,
    })

    logger.info(
        f"Pipeline done for {user_id} in {pipeline_ms}ms | "
        f"fallback={any_fallback}"
    )
    return profile


async def _run_personalization_pipeline(user_id: str, user_data: Dict) -> Dict:
    """
    Run pipeline with a hard wall-clock timeout.
    If LLM calls are too slow, falls back to instant mock data.
    """
    pipeline_start = time.time()
    try:
        profile = await asyncio.wait_for(
            _run_llm_pipeline(user_id, user_data),
            timeout=PIPELINE_HARD_TIMEOUT,
        )
        return profile
    except asyncio.TimeoutError:
        elapsed_ms = round((time.time() - pipeline_start) * 1000, 1)
        logger.warning(
            f"Pipeline hard-timeout ({PIPELINE_HARD_TIMEOUT}s) for {user_id} "
            f"after {elapsed_ms}ms — returning rich mock data"
        )
        _pipeline_status[user_id] = {
            "status": "completed", "progress_percent": 100,
            "current_agent": None, "user_id": user_id,
        }
        profile = _build_fallback_profile(user_id, user_data, pipeline_ms=elapsed_ms)
        cache_service.set(
            cache_service.agent_key("personalization", user_id),
            profile,
            ttl=settings.CACHE_TTL_AGENT,
        )
        return profile


# ─── API Endpoints ─────────────────────────────────────────────────────────────

@router.post("/personalize/{user_id}")
async def personalize_member(
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
        "status": "running", "progress_percent": 0,
        "current_agent": "starting", "user_id": user_id,
        "started_at": time.time(),
    }

    try:
        profile = await _run_personalization_pipeline(user_id, user_data)
        return success_response(
            data=profile, request_id=request_id, message="Personalization complete"
        )
    except Exception as e:
        logger.error(f"Pipeline failed for {user_id}: {e}", exc_info=True)
        _pipeline_status[user_id]["status"] = "failed"
        # Last-resort fallback — always return something useful
        profile = _build_fallback_profile(user_id, user_data)
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
async def refresh_personalization(
    user_id: str = Depends(validate_user_id_param),
    request_id: str = Depends(get_request_id),
) -> Dict[str, Any]:
    """Force-refresh personalization by clearing cache and re-running the pipeline."""
    user_data = get_mock_user(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")

    cache_service.clear_prefix("agent:")
    logger.info(f"Force-refresh for {user_id}")

    try:
        profile = await _run_personalization_pipeline(user_id, user_data)
        return success_response(data=profile, request_id=request_id, message="Personalization refreshed")
    except Exception as e:
        logger.error(f"Refresh failed for {user_id}: {e}", exc_info=True)
        profile = _build_fallback_profile(user_id, user_data)
        return success_response(data=profile, request_id=request_id, message="Personalization refreshed (fallback)")


@router.post("/community/health")
async def run_community_health(request_id: str = Depends(get_request_id)) -> Dict[str, Any]:
    """
    Run community health + organizer pipeline.
    Executes: Health Agent → Organizer Agent
    Hard timeout: 30 seconds.
    """
    from agents.health_agent import HealthAgent
    from agents.organizer_agent import OrganizerAgent

    async def _run():
        health_result = await HealthAgent().run_community()
        organizer_result = await OrganizerAgent().run_community(health_result.get("data"))
        return {
            "health": health_result.get("data", {}),
            "actions": organizer_result.get("data", {}),
            "fallback_used": health_result.get("is_fallback") or organizer_result.get("is_fallback"),
        }

    try:
        combined = await asyncio.wait_for(_run(), timeout=30)
    except asyncio.TimeoutError:
        logger.warning("Community health pipeline timed out — returning mock data")
        combined = {
            "health": get_mock_health(),
            "actions": get_mock_organizer(),
            "fallback_used": True,
        }

    cache_service.set(cache_service.community_key("health_and_actions"), combined, ttl=1800)
    return success_response(data=combined, request_id=request_id)
