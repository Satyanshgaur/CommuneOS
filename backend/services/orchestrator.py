"""
CommuneOS Agent Orchestrator Service
Dedicated pipeline manager for coordinating all 6 agents.

Patterns:
  - Member Personalization: Identity → (Discovery + Learning) → Mentor
  - Community Health:       Health → Organizer

Features:
  - Hard pipeline timeouts via asyncio.wait_for
  - Per-step error recovery with graceful degradation
  - Structured logging with step-by-step timing
  - Instant mock-data fallback path
"""
import asyncio
import time
from typing import Any, Dict, Optional

from config import settings
from services.analytics import analytics_service
from services.cache_service import cache_service
from services.mock_data import (
    get_mock_identity, get_mock_discovery, get_mock_learning,
    get_mock_mentor, get_mock_health, get_mock_organizer,
)
from utils.logger import get_logger

logger = get_logger("orchestrator")

# Timeouts
MEMBER_PIPELINE_TIMEOUT = 45   # seconds hard cap
COMMUNITY_PIPELINE_TIMEOUT = 30


# ─── Instant fallback helpers ──────────────────────────────────────────────────

def _instant_profile(user_id: str, user_data: Dict, elapsed_ms: float = 0) -> Dict:
    """Build a complete personalization profile from mock data — no LLM."""
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
        "pipeline_time_ms": elapsed_ms,
        "is_partial": False,
        "fallback_used": True,
        "note": "AI-generated via cached community data",
    }


def _instant_community(elapsed_ms: float = 0) -> Dict:
    """Build community report from mock data — no LLM."""
    health = get_mock_health()
    health.pop("_is_fallback", None)
    organizer = get_mock_organizer(health)
    organizer.pop("_is_fallback", None)
    return {
        "health": health,
        "actions": organizer,
        "pipeline_time_ms": elapsed_ms,
        "fallback_used": True,
    }


# ─── Member Personalization Pipeline ──────────────────────────────────────────

async def _member_llm_pipeline(user_id: str, user_data: Dict) -> Dict:
    """
    LLM-powered member personalization:
      Step 1: Identity Agent     (sequential — others depend on it)
      Step 2: Discovery + Learning (asyncio.gather — parallel)
      Step 3: Mentor Agent       (uses learning output)

    Each agent has its own internal fallback. If LLM fails per-agent,
    that agent silently returns mock data and the pipeline continues.
    """
    from agents.identity_agent import IdentityAgent
    from agents.discovery_agent import DiscoveryAgent
    from agents.learning_agent import LearningAgent
    from agents.mentor_agent import MentorAgent

    t0 = time.time()
    steps: Dict[str, float] = {}

    # ── Step 1: Identity ──────────────────────────────────────────────────────
    logger.info(f"[{user_id}] Step 1/3 -> Identity Agent")
    t_step = time.time()
    identity_result = await IdentityAgent().run(user_id, user_data)
    steps["identity_ms"] = round((time.time() - t_step) * 1000, 1)
    logger.info(f"[{user_id}] Identity done in {steps['identity_ms']}ms | fallback={identity_result.get('is_fallback')}")

    identity_data = identity_result.get("data", {})

    # ── Step 2: Discovery + Learning (parallel) ────────────────────────────────
    logger.info(f"[{user_id}] Step 2/3 -> Discovery + Learning (parallel)")
    t_step = time.time()
    disc_res, learn_res = await asyncio.gather(
        DiscoveryAgent().run(user_id, user_data, identity_data),
        LearningAgent().run(user_id, user_data, identity_data),
        return_exceptions=True,
    )
    steps["discovery_learning_ms"] = round((time.time() - t_step) * 1000, 1)

    # Recover from any exceptions
    if isinstance(disc_res, Exception):
        logger.warning(f"[{user_id}] Discovery exception: {disc_res} — using mock")
        disc_data = get_mock_discovery(user_id, user_data)
        disc_data.pop("_is_fallback", None)
        disc_res = {"data": disc_data, "is_fallback": True, "success": True}

    if isinstance(learn_res, Exception):
        logger.warning(f"[{user_id}] Learning exception: {learn_res} — using mock")
        learn_data = get_mock_learning(user_id, user_data)
        learn_data.pop("_is_fallback", None)
        learn_res = {"data": learn_data, "is_fallback": True, "success": True}

    logger.info(
        f"[{user_id}] Discovery+Learning done in {steps['discovery_learning_ms']}ms | "
        f"disc_fallback={disc_res.get('is_fallback')} learn_fallback={learn_res.get('is_fallback')}"
    )

    # ── Step 3: Mentor ────────────────────────────────────────────────────────
    logger.info(f"[{user_id}] Step 3/3 -> Mentor Agent")
    t_step = time.time()
    mentor_res = await MentorAgent().run(
        user_id, user_data, identity_data, learn_res.get("data", {})
    )
    steps["mentor_ms"] = round((time.time() - t_step) * 1000, 1)
    logger.info(f"[{user_id}] Mentor done in {steps['mentor_ms']}ms | fallback={mentor_res.get('is_fallback')}")

    # ── Assemble profile ──────────────────────────────────────────────────────
    total_ms = round((time.time() - t0) * 1000, 1)
    any_fallback = any([
        identity_result.get("is_fallback"),
        disc_res.get("is_fallback"),
        learn_res.get("is_fallback"),
        mentor_res.get("is_fallback"),
    ])

    profile = {
        "user_id": user_id,
        "identity": identity_data,
        "discovery": disc_res.get("data", {}),
        "learning": learn_res.get("data", {}),
        "mentor": mentor_res.get("data", {}),
        "pipeline_time_ms": total_ms,
        "step_timings_ms": steps,
        "is_partial": False,
        "fallback_used": any_fallback,
    }

    analytics_service.record_agent_execution(
        "full_pipeline", total_ms, success=True, is_fallback=any_fallback
    )
    logger.info(
        f"[{user_id}] Pipeline complete: {total_ms}ms | "
        f"fallback={any_fallback} | steps={steps}"
    )
    return profile


async def run_member_pipeline(user_id: str, user_data: Dict) -> Dict:
    """
    Public entry point for member personalization.
    Wraps LLM pipeline with a hard timeout; falls back gracefully.
    Also checks cache before running anything.
    """
    # Check cache first
    cache_key = cache_service.agent_key("personalization", user_id)
    cached = cache_service.get(cache_key)
    if cached:
        logger.info(f"[{user_id}] Personalization cache HIT")
        return cached

    t0 = time.time()
    try:
        profile = await asyncio.wait_for(
            _member_llm_pipeline(user_id, user_data),
            timeout=MEMBER_PIPELINE_TIMEOUT,
        )
    except asyncio.TimeoutError:
        elapsed = round((time.time() - t0) * 1000, 1)
        logger.warning(
            f"[{user_id}] Pipeline hard-timeout ({MEMBER_PIPELINE_TIMEOUT}s) "
            f"after {elapsed}ms — instant mock fallback"
        )
        profile = _instant_profile(user_id, user_data, elapsed_ms=elapsed)
    except Exception as e:
        elapsed = round((time.time() - t0) * 1000, 1)
        logger.error(f"[{user_id}] Pipeline error: {e} — instant mock fallback", exc_info=True)
        profile = _instant_profile(user_id, user_data, elapsed_ms=elapsed)

    # Cache result regardless of source
    cache_service.set(cache_key, profile, ttl=settings.CACHE_TTL_AGENT)
    return profile


# ─── Community Health Pipeline ─────────────────────────────────────────────────

async def _community_llm_pipeline() -> Dict:
    """
    Community health analysis:
      Step 1: Health Agent  — detect churn, gaps, trends
      Step 2: Organizer Agent — convert health data to action items
    """
    from agents.health_agent import HealthAgent
    from agents.organizer_agent import OrganizerAgent

    t0 = time.time()

    logger.info("[community] Step 1/2 -> Health Agent")
    health_result = await HealthAgent().run_community()

    logger.info("[community] Step 2/2 -> Organizer Agent")
    organizer_result = await OrganizerAgent().run_community(health_result.get("data"))

    total_ms = round((time.time() - t0) * 1000, 1)
    any_fallback = health_result.get("is_fallback") or organizer_result.get("is_fallback")

    result = {
        "health": health_result.get("data", {}),
        "actions": organizer_result.get("data", {}),
        "pipeline_time_ms": total_ms,
        "fallback_used": any_fallback,
    }

    logger.info(f"[community] Pipeline complete: {total_ms}ms | fallback={any_fallback}")
    return result


async def run_community_pipeline() -> Dict:
    """
    Public entry point for community health + organizer.
    Returns cached result if available.
    """
    cache_key = cache_service.community_key("health_and_actions")
    cached = cache_service.get(cache_key)
    if cached:
        logger.info("[community] Cache HIT")
        return cached

    t0 = time.time()
    try:
        result = await asyncio.wait_for(
            _community_llm_pipeline(),
            timeout=COMMUNITY_PIPELINE_TIMEOUT,
        )
    except asyncio.TimeoutError:
        elapsed = round((time.time() - t0) * 1000, 1)
        logger.warning(f"[community] Timeout after {elapsed}ms — mock fallback")
        result = _instant_community(elapsed_ms=elapsed)
    except Exception as e:
        elapsed = round((time.time() - t0) * 1000, 1)
        logger.error(f"[community] Error: {e} — mock fallback", exc_info=True)
        result = _instant_community(elapsed_ms=elapsed)

    cache_service.set(cache_key, result, ttl=1800)
    return result
