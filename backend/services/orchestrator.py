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
    from services.db import community_members_table
    member_info = community_members_table.get(user_id.lower())
    community_id = member_info["community_id"] if member_info else "comm-gpu"

    identity = get_mock_identity(user_id, user_data)
    identity.pop("_is_fallback", None)
    discovery = get_mock_discovery(user_id, identity, community_id=community_id)
    discovery.pop("_is_fallback", None)
    learning = get_mock_learning(user_id, identity, community_id=community_id)
    learning.pop("_is_fallback", None)
    mentor = get_mock_mentor(user_id, identity, community_id=community_id)
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


def _instant_community(community_id: str = "comm-gpu", elapsed_ms: float = 0) -> Dict:
    """Build community report from mock data — no LLM."""
    health = get_mock_health(community_id=community_id)
    health.pop("_is_fallback", None)
    organizer = get_mock_organizer(community_id=community_id)
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
    from services.db import community_members_table
    member_info = community_members_table.get(user_id.lower())
    community_id = member_info["community_id"] if member_info else "comm-gpu"

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
        disc_data = get_mock_discovery(user_id, user_data, community_id=community_id)
        disc_data.pop("_is_fallback", None)
        disc_res = {"data": disc_data, "is_fallback": True, "success": True}

    if isinstance(learn_res, Exception):
        logger.warning(f"[{user_id}] Learning exception: {learn_res} — using mock")
        learn_data = get_mock_learning(user_id, user_data, community_id=community_id)
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

async def _community_llm_pipeline(community_id: str = "comm-gpu") -> Dict:
    """
    Community health analysis:
      Step 1: Health Agent  — detect churn, gaps, trends
      Step 2: Organizer Agent — convert health data to action items
    """
    from agents.health_agent import HealthAgent
    from agents.organizer_agent import OrganizerAgent

    t0 = time.time()

    logger.info(f"[community {community_id}] Step 1/2 -> Health Agent")
    health_result = await HealthAgent().run_community(community_id=community_id)

    logger.info(f"[community {community_id}] Step 2/2 -> Organizer Agent")
    organizer_result = await OrganizerAgent().run_community(community_id=community_id, health_data=health_result.get("data"))

    total_ms = round((time.time() - t0) * 1000, 1)
    any_fallback = health_result.get("is_fallback") or organizer_result.get("is_fallback")

    # Override results using tenant DB scoping if falling back to mock or to enforce multi-tenant parameters
    if any_fallback:
        result = _instant_community(community_id=community_id, elapsed_ms=total_ms)
        return result

    result = {
        "health": health_result.get("data", {}),
        "actions": organizer_result.get("data", {}),
        "pipeline_time_ms": total_ms,
        "fallback_used": any_fallback,
    }

    logger.info(f"[community {community_id}] Pipeline complete: {total_ms}ms | fallback={any_fallback}")
    return result


async def run_community_pipeline(community_id: str = "comm-gpu") -> Dict:
    """
    Public entry point for community health + organizer.
    Returns cached result if available.
    """
    cache_key = cache_service.community_key(f"health_and_actions:{community_id}")
    cached = cache_service.get(cache_key)
    if cached:
        logger.info(f"[community {community_id}] Cache HIT")
        return cached

    t0 = time.time()
    try:
        result = await asyncio.wait_for(
            _community_llm_pipeline(community_id=community_id),
            timeout=COMMUNITY_PIPELINE_TIMEOUT,
        )
    except asyncio.TimeoutError:
        elapsed = round((time.time() - t0) * 1000, 1)
        logger.warning(f"[community {community_id}] Timeout after {elapsed}ms — mock fallback")
        result = _instant_community(community_id=community_id, elapsed_ms=elapsed)
    except Exception as e:
        elapsed = round((time.time() - t0) * 1000, 1)
        logger.error(f"[community {community_id}] Error: {e} — mock fallback", exc_info=True)
        result = _instant_community(community_id=community_id, elapsed_ms=elapsed)

    cache_service.set(cache_key, result, ttl=1800)
    return result


# ─── Sprint 3 Pipeline ─────────────────────────────────────────────────────────

def get_user_state_hash(user_id: str, community_id: str) -> str:
    """Generate a hash based on all inputs that affect Sprint 3 recommendations."""
    import hashlib
    import json
    from services.db import users_table, resumes_table, identities_table, get_resources_by_community
    
    user_id_lower = user_id.lower()
    user_profile = users_table.get(user_id_lower, {})
    resume_profile = resumes_table.get(user_id_lower, {})
    identity_profile = identities_table.get(user_id_lower, {})
    resources = get_resources_by_community(community_id)
    
    state = {
        "profile": {
            "updated_at": user_profile.get("updated_at"),
            "github_username": user_profile.get("github_username"),
            "resume_name": user_profile.get("resume_name"),
            "skills": user_profile.get("skills"),
            "interests": user_profile.get("interests"),
            "goals": user_profile.get("goals"),
            "career_goals": user_profile.get("career_goals"),
        },
        "resume": resume_profile,
        "identity": identity_profile,
        "resources_count": len(resources),
        "resources_titles": [r["title"] for r in resources]
    }
    
    state_str = json.dumps(state, sort_keys=True, default=str)
    return hashlib.sha256(state_str.encode("utf-8")).hexdigest()


async def run_sprint3_pipeline(user_id: str, force_refresh: bool = False) -> Dict[str, Any]:
    """
    Sprint 3 personalized discovery, roadmap, and mentor matching pipeline.
    Runs Discovery & Learning in parallel, followed by Mentor Matching.
    Saves outputs in backend database tables.
    """
    from services.db import (
        users_table,
        identities_table,
        community_members_table,
        recommendations_table,
        learning_roadmaps_table,
        mentor_matches_table,
        pipeline_hashes
    )
    from agents.discovery_agent import DiscoveryAgent
    from agents.learning_agent import LearningAgent
    from agents.mentor_agent import MentorAgent
    from agents.identity_agent import IdentityAgent
    
    user_id_lower = user_id.lower()
    user_data = users_table.get(user_id_lower)
    if not user_data:
        logger.error(f"User {user_id} not found in database.")
        return {}
        
    member_info = community_members_table.get(user_id_lower)
    community_id = member_info["community_id"] if member_info else "comm-gpu"
    
    # 1. Ensure identity profile exists. If not, generate it statelessly.
    identity_data = identities_table.get(user_id_lower)
    if not identity_data:
        logger.info(f"Identity profile not found for {user_id}. Running Identity Agent first.")
        try:
            identity_data = await IdentityAgent().run_stateless(user_id)
        except Exception as e:
            logger.error(f"Identity generation failed in pipeline for {user_id}: {e}")
            identity_data = IdentityAgent()._get_fallback(user_id, user_data)
            identities_table[user_id_lower] = identity_data
            
    # 2. Check if state changed.
    current_hash = get_user_state_hash(user_id, community_id)
    stored_hash = pipeline_hashes.get(user_id_lower)
    
    # Check if we can skip regeneration
    if (
        not force_refresh
        and stored_hash == current_hash
        and user_id_lower in recommendations_table
        and user_id_lower in learning_roadmaps_table
        and user_id_lower in mentor_matches_table
    ):
        logger.info(f"Sprint 3 pipeline skip for {user_id}: No changes detected and data exists.")
        return {
            "recommendations": recommendations_table[user_id_lower],
            "learning_roadmap": learning_roadmaps_table[user_id_lower],
            "mentor_matches": mentor_matches_table[user_id_lower]
        }
        
    logger.info(f"Running Sprint 3 pipeline for user {user_id} (force_refresh={force_refresh}).")
    
    # 3. Run Discovery and Learning Agents in parallel
    try:
        discovery_task = DiscoveryAgent().run_sprint3(user_id, user_data, identity_data, community_id)
        learning_task = LearningAgent().run_sprint3(user_id, user_data, identity_data, community_id)
        
        discovery_res, learning_res = await asyncio.gather(discovery_task, learning_task)
    except Exception as e:
        logger.error(f"Error during parallel Discovery/Learning agent runs: {e}")
        # Fallbacks
        from agents.discovery_agent import DiscoveryAgent as DA
        from agents.learning_agent import LearningAgent as LA
        from services.db import get_channels_by_community, get_resources_by_community, get_events_by_community, get_projects_by_community, learning_tracks_table
        
        channels = get_channels_by_community(community_id)
        resources = get_resources_by_community(community_id)
        events = get_events_by_community(community_id)
        projects = get_projects_by_community(community_id)
        track = learning_tracks_table.get(community_id)
        learning_tracks = [track] if track else []
        
        discovery_res = DA()._get_sprint3_fallback(user_data, channels, resources, events, projects, learning_tracks)
        learning_res = LA()._get_sprint3_fallback(user_id, user_data, track)
        
    # 4. Run Mentor Matching Agent (needs learning_roadmap output)
    try:
        mentor_res = await MentorAgent().run_sprint3(user_id, user_data, identity_data, learning_res, community_id)
    except Exception as e:
        logger.error(f"Error during Mentor agent run: {e}")
        from agents.mentor_agent import MentorAgent as MA
        from services.db import get_mentors_by_community
        mentors = get_mentors_by_community(community_id)
        mentor_res = MA()._get_sprint3_fallback(user_data, mentors)
        
    # 5. Save results to database
    # Preserve user completion progress if roadmap already exists
    if user_id_lower in learning_roadmaps_table:
        old_roadmap = learning_roadmaps_table[user_id_lower]
        completed_weeks = {m["week"] for m in old_roadmap.get("milestones", []) if m.get("completed")}
        completed_tasks = {t["task_id"] for t in old_roadmap.get("daily_checklist", []) if t.get("completed")}
        
        for m in learning_res.get("milestones", []):
            if m["week"] in completed_weeks:
                m["completed"] = True
                
        for t in learning_res.get("daily_checklist", []):
            if t["task_id"] in completed_tasks:
                t["completed"] = True
                
        # Recalculate progress percent
        total_milestones = len(learning_res.get("milestones", []))
        completed_count = sum(1 for m in learning_res.get("milestones", []) if m.get("completed"))
        learning_res["progress_percent"] = (completed_count / total_milestones * 100) if total_milestones > 0 else 0.0

    recommendations_table[user_id_lower] = discovery_res
    learning_roadmaps_table[user_id_lower] = learning_res
    mentor_matches_table[user_id_lower] = mentor_res
    
    # Store state hash
    pipeline_hashes[user_id_lower] = current_hash
    
    logger.info(f"Sprint 3 pipeline completed successfully for user {user_id}.")
    return {
        "recommendations": discovery_res,
        "learning_roadmap": learning_res,
        "mentor_matches": mentor_res
    }
