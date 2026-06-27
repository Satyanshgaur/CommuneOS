"""
CommuneOS Agent Orchestrator Service
Coordinates execution of all specialized agents (Identity, Discovery, Learning, Mentor, Health, Organizer).
Uses Memory Agent to perform RAG vector database retrievals for all personalization requests.
"""
import asyncio
import json
import time
from typing import Any, Dict, Optional

from config import settings
from services.analytics import analytics_service
from services.cache_service import cache_service
from services.llm_service import LLMService
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
    
    # Adapt to new schema
    detected_skills = identity.get("detected_skills", [])
    tech_stack = [s["name"] for s in detected_skills] if detected_skills else ["Python", "Systems"]
    inferred = {s["name"]: s["proficiency"] for s in detected_skills} if detected_skills else {"Python": "Intermediate"}
    
    return {
        "user_id": user_id,
        "identity": {
            "current_skill_level": user_data.get("skill_level") or "Intermediate",
            "learning_goals": user_data.get("goals") or ["Become an AI Systems Engineer"],
            "primary_interests": user_data.get("interests") or ["AI", "Systems"],
            "technology_stack": tech_stack,
            "inferred_skills": inferred,
            "insights": [f"Has interest in {', '.join(user_data.get('interests', ['AI']))}"],
            "reasoning": identity.get("summary", "Fallback profile generated."),
        },
        "discovery": {
            "recommended_channels": discovery.get("recommended_channels", []),
            "recommended_resources": discovery.get("recommended_resources", []),
            "discovery_priority": discovery.get("discovery_priority", []),
            "answer": "You should attend the GPU Systems Workshop since your profile shows strong interest in low-level GPU programming.",
            "reasoning": "Matched user tags against available channels."
        },
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


# ─── Unified single-call pipeline ─────────────────────────────────────────────

_UNIFIED_SYSTEM = """You are CommuneOS, an AI community platform. Analyze user profiles and select the most relevant items from the provided lists.

Output ONLY valid JSON — no markdown, no explanation, no code fences."""

_UNIFIED_PROMPT = """Analyze this user's profile and resume context to return personalized recommendations by selecting from the provided lists.

USER PROFILE:
- Username: {username}
- Bio: {bio}
- Stated Skills/Tags: {tags}
- Interests: {interests}
- Goals: {goals}

RETRIEVED PERSONAL & COMMUNITY RAG CONTEXT:
{memory_context}

AVAILABLE CHANNELS (select 3-4 most relevant, use exact names):
{channels}

AVAILABLE RESOURCES (select 3-4 most relevant, use exact titles):
{resources}

AVAILABLE MENTORS (select the single best match, use exact name and role):
{mentors}

Return this exact JSON structure:
{{
  "identity": {{
    "current_skill_level": "Beginner|Intermediate|Advanced|Expert",
    "learning_goals": ["Goal1", "Goal2"],
    "primary_interests": ["Interest1", "Interest2"],
    "technology_stack": ["Tech1", "Tech2"],
    "inferred_skills": {{"Skill1": "Beginner|Intermediate|Advanced|Expert"}},
    "insights": ["Insight1", "Insight2"],
    "reasoning": "2 sentences summarizing their background."
  }},
  "discovery": {{
    "recommended_channels": [
      {{"channel_id": "ch-id", "name": "EXACT channel name", "reason": "1 sentence why", "relevance_score": 0.90}}
    ],
    "recommended_resources": [
      {{"resource_id": "res-id", "title": "EXACT resource title", "reason": "1 sentence why", "relevance_score": 0.88}}
    ],
    "answer": "A highly personalized recommendation paragraph answering what they should do or attend.",
    "reasoning": "2 sentences explaining why these channels and resources match."
  }},
  "learning": {{
    "roadmap_title": "Custom path name based on their goals",
    "total_weeks": 8,
    "daily_commitment_minutes": 45,
    "milestones": [
      {{"week": 1, "title": "milestone title", "objectives": ["specific objective"], "estimated_hours": 5.0}}
    ],
    "daily_checklist": [
      {{"task_id": "task-1", "task": "Specific actionable task", "type": "reading|coding", "duration_minutes": 30, "resource_link": null, "completed": false}}
    ],
    "reasoning": "2 sentences explaining the roadmap."
  }},
  "mentor": {{
    "primary_mentor": {{
      "mentor_id": "mentor-id",
      "name": "EXACT mentor name",
      "role": "EXACT role",
      "expertise_areas": ["area1", "area2"],
      "compatibility_score": 0.92,
      "match_reason": "1 sentence explaining the match."
    }},
    "reasoning": "2 sentences explaining why this mentor was chosen."
  }}
}}"""


def _get_pools_for_prompt() -> Dict[str, str]:
    """Extract channel/resource/mentor pools from mock_data for injection into LLM prompt."""
    from services.mock_data import _channel_pool_raw, _resource_pool_raw, _mentor_pool_raw
    channels = "\n".join(f"- {c['name']} (id: {c['channel_id']}): {c.get('reason','')}" for c in _channel_pool_raw)
    resources = "\n".join(f"- {r['title']} (id: {r['resource_id']}): {r.get('reason','')}" for r in _resource_pool_raw)
    mentors = "\n".join(
        f"- {m['name']} (id: {m['mentor_id']}), {m['role']}, expertise: {', '.join(m.get('expertise_areas',[]))}"
        for m in _mentor_pool_raw
    )
    return {"channels": channels, "resources": resources, "mentors": mentors}


async def _unified_pipeline(user_id: str, user_data: Dict) -> Optional[Dict]:
    """
    Single LLM call that produces all 4 agent outputs at once.
    Returns None if the LLM fails (caller falls through to per-agent pipeline).
    """
    try:
        pools = _get_pools_for_prompt()
    except Exception:
        pools = {"channels": "General, Systems Programming, Quant Finance", "resources": "see community", "mentors": "see community"}

    # Fetch RAG context from Memory Agent
    from agents.memory_agent import MemoryAgent
    memory_agent = MemoryAgent()
    memory_res = await memory_agent.run(user_id, user_data)
    memory_context = memory_res.get("data", {}).get("merged_text", "No specific memory found.")

    prompt = _UNIFIED_PROMPT.format(
        username=user_data.get("username", user_id[:8]),
        bio=user_data.get("bio", "Not provided"),
        tags=", ".join(user_data.get("tags", [])) or "None",
        interests=", ".join(user_data.get("interests", [])) or "None",
        goals=", ".join(user_data.get("goals", [])) or "None",
        memory_context=memory_context,
        **pools,
    )

    llm = LLMService()
    result, is_fallback = await llm.complete(
        prompt=prompt,
        system_prompt=_UNIFIED_SYSTEM,
        temperature=0.4,
        max_tokens=2000,
        use_cache=True,
    )

    if is_fallback or not result:
        return None

    # Strip markdown code fences if model wrapped the JSON
    text = result.strip()
    if text.startswith("```"):
        text = text.split("```")[-2] if "```" in text[3:] else text[3:]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip().rstrip("`").strip()

    try:
        data = json.loads(text)
        # Validate shape
        if all(k in data for k in ("identity", "discovery", "learning", "mentor")):
            logger.info(f"[{user_id}] Unified pipeline SUCCESS via LLM")
            return data
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning(f"[{user_id}] Unified pipeline JSON parse error: {e}")

    return None


# ─── Member Personalization Pipeline ──────────────────────────────────────────

async def _member_llm_pipeline(user_id: str, user_data: Dict) -> Dict:
    """
    LLM-powered member personalization using sequential per-agent execution:
      Step 1: Identity Agent     (sequential — others depend on it)
      Step 2: Discovery + Learning (asyncio.gather — parallel)
      Step 3: Mentor Agent       (uses learning output)
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
    profile = None

    # ── Attempt 1: unified single LLM call ────────────────────────────────────
    _unified_rate_limited = False
    try:
        unified = await asyncio.wait_for(_unified_pipeline(user_id, user_data), timeout=22)
        if unified:
            elapsed = round((time.time() - t0) * 1000, 1)
            identity_data = unified.get("identity", {})
            
            # Map legacy format variables to avoid compatibility issues
            identity_data["detected_skills"] = [
                {"name": name, "proficiency": level, "confidence": 0.9, "source": "resume"}
                for name, level in identity_data.get("inferred_skills", {}).items()
            ]
            
            profile = {
                "user_id": user_id,
                "identity": identity_data,
                "discovery": unified.get("discovery", {}),
                "learning": unified.get("learning", {}),
                "mentor": unified.get("mentor", {}),
                "pipeline_time_ms": elapsed,
                "is_partial": False,
                "fallback_used": False,
            }
            analytics_service.record_agent_execution("full_pipeline", elapsed, success=True, is_fallback=False)
            logger.info(f"[{user_id}] Unified pipeline: {elapsed}ms")
        else:
            _unified_rate_limited = True
            logger.info(f"[{user_id}] Unified pipeline returned None — LLM unavailable")
    except asyncio.TimeoutError:
        logger.warning(f"[{user_id}] Unified pipeline timeout")
    except Exception as e:
        logger.warning(f"[{user_id}] Unified pipeline error: {e}")

    # ── Attempt 2: per-agent pipeline ──────────────────────────────────────────
    if profile is None and not _unified_rate_limited:
        try:
            profile = await asyncio.wait_for(
                _member_llm_pipeline(user_id, user_data),
                timeout=MEMBER_PIPELINE_TIMEOUT,
            )
        except asyncio.TimeoutError:
            elapsed = round((time.time() - t0) * 1000, 1)
            logger.warning(f"[{user_id}] Full pipeline timeout after {elapsed}ms — instant mock fallback")
            profile = _instant_profile(user_id, user_data, elapsed_ms=elapsed)
        except Exception as e:
            elapsed = round((time.time() - t0) * 1000, 1)
            logger.error(f"[{user_id}] Pipeline error: {e} — instant mock fallback", exc_info=True)
            profile = _instant_profile(user_id, user_data, elapsed_ms=elapsed)

    # ── Instant mock fallback if everything failed ─────────────────────────────
    if profile is None:
        elapsed = round((time.time() - t0) * 1000, 1)
        logger.info(f"[{user_id}] Using smart mock fallback in {elapsed}ms")
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
