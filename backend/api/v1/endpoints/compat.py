"""
Compatibility shim routes for the Next.js frontend.
Maps /api/members/{user_id} and /api/organizer to the v1 pipeline responses.
"""
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from services import run_member_pipeline, run_community_pipeline, get_mock_user
from services.mock_data import (
    get_mock_identity, get_mock_discovery, get_mock_learning,
    get_mock_mentor, get_mock_health, get_mock_organizer,
)
from services.cache_service import cache_service
from utils.logger import get_logger

# Maps resource_id → (url, type) for enriching LLM-returned resources
_RESOURCE_URL_MAP: Dict[str, Dict[str, str]] = {
    "res-001": {"url": "https://www.youtube.com/watch?v=ic55579V0g4", "type": "Video"},
    "res-002": {"url": "https://developer.nvidia.com/blog/using-shared-memory-cuda-cc/", "type": "Article"},
    "res-003": {"url": "https://tldp.org/LDP/lkmpg/2.6/html/lkmpg.html", "type": "Guide"},
    "res-004": {"url": "https://numpy.org/doc/stable/user/quickstart.html", "type": "Interactive Notebook"},
    "res-005": {"url": "https://pytorch.org/tutorials/intermediate/ddp_tutorial.html", "type": "Tutorial"},
    "res-006": {"url": "https://doc.rust-lang.org/book/", "type": "Guide"},
    "res-007": {"url": "https://www.youtube.com/watch?v=0sOvCWFmrtA", "type": "Video"},
    "res-008": {"url": "https://www.youtube.com/watch?v=PtM44dh7RjI", "type": "Video"},
    "res-009": {"url": "https://huggingface.co/learn/nlp-course/chapter1/1", "type": "Tutorial"},
    "res-010": {"url": "https://uxdesign.cc/ui-cheat-sheet-d6facd7e2f4c", "type": "Article"},
    "res-011": {"url": "https://www.youtube.com/watch?v=EUreLXAlPKs", "type": "Video"},
    "res-012": {"url": "https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#r-resource-management", "type": "Article"},
    "res-013": {"url": "https://www.atlassian.com/git/tutorials/comparing-workflows", "type": "Guide"},
    "res-014": {"url": "https://mlflow.org/docs/latest/deployment/index.html", "type": "Tutorial"},
    "res-015": {"url": "https://seaborn.pydata.org/tutorial.html", "type": "Interactive Notebook"},
    "res-016": {"url": "https://www.youtube.com/watch?v=Y9oNgLfF7ws", "type": "Video"},
    "res-017": {"url": "https://fastapi.tiangolo.com/tutorial/security/", "type": "Guide"},
    "res-018": {"url": "https://www.amazon.com/Heard-Street-Quantitative-Questions-Interviews/dp/0994708319", "type": "Article"},
    "res-019": {"url": "https://www.youtube.com/watch?v=sjVGFNPchV0", "type": "Video"},
    "res-020": {"url": "https://colab.research.google.com/github/cantaro86/Financial-Models-Numerical-Methods/blob/master/1.1%20Black-Scholes%20numerical%20methods.ipynb", "type": "Interactive Notebook"},
    "res-021": {"url": "https://www.math.tamu.edu/~stecher/425/Sp12/brownianMotion.pdf", "type": "Guide"},
    "res-022": {"url": "https://www.manning.com/books/c-plus-plus-concurrency-in-action", "type": "Tutorial"},
    "res-023": {"url": "https://www.youtube.com/watch?v=xfzGZB4HhEE", "type": "Video"},
    "res-024": {"url": "https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html", "type": "Guide"},
    "res-025": {"url": "https://www.youtube.com/watch?v=tomUWcQ0P3k", "type": "Video"},
    "res-026": {"url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/", "type": "Tutorial"},
    "res-027": {"url": "https://cloud.google.com/learn/certification/data-engineer", "type": "Guide"},
    "res-028": {"url": "https://pandas.pydata.org/docs/getting_started/intro_tutorials/", "type": "Interactive Notebook"},
    "res-029": {"url": "https://www.youtube.com/watch?v=qBigTkBLU6g", "type": "Video"},
    "res-030": {"url": "https://mode.com/sql-tutorial/", "type": "Tutorial"},
    "res-031": {"url": "https://owasp.org/www-project-top-ten/", "type": "Guide"},
    "res-032": {"url": "https://www.youtube.com/watch?v=0-S5a0eXPoc", "type": "Video"},
    "res-033": {"url": "https://www.youtube.com/watch?v=VPvVD8t02U8", "type": "Video"},
    "res-034": {"url": "https://github.com/donnemartin/system-design-primer", "type": "Article"},
    "res-035": {"url": "https://python.langchain.com/docs/tutorials/", "type": "Tutorial"},
    "res-036": {"url": "https://www.youtube.com/watch?v=R8_veQiYBjI", "type": "Video"},
    "res-037": {"url": "https://www.youtube.com/watch?v=3Kq1MIfTWCE", "type": "Video"},
}

router = APIRouter(tags=["Compat"])
logger = get_logger("endpoint.compat")


def _identity_reasoning(username: str, skills: list, identity: Dict) -> str:
    skill_str = ", ".join(skills[:3]) if skills else "general topics"
    confidence = round(identity.get("overall_confidence", 0.72) * 100)
    expertise = ", ".join(identity.get("expertise_areas", [])[:2]) or "multiple domains"
    return (
        f"Identity Agent: Scanned {username}'s profile and activity signals. "
        f"Detected {len(skills)} skill(s): {skill_str}. "
        f"Primary expertise mapped to {expertise}. "
        f"Overall profile confidence: {confidence}%."
    )


def _discovery_reasoning(username: str, discovery: Dict) -> str:
    channels = discovery.get("recommended_channels", [])
    resources = discovery.get("recommended_resources", [])
    top_channel = channels[0].get("name", "a community") if channels else "relevant communities"
    return (
        f"Discovery Agent: Matched {username}'s skill profile against all available channels and resources. "
        f"Recommended {len(channels)} channel(s) — top pick: {top_channel}. "
        f"Surfaced {len(resources)} learning resource(s) ranked by relevance to stated goals."
    )


def _learning_reasoning(username: str, learning: Dict, user_data: Dict) -> str:
    weeks = learning.get("total_weeks", 8)
    minutes = learning.get("daily_commitment_minutes", 60)
    goals = user_data.get("goals", [])
    goal_str = ", ".join(goals[:2]) if goals else "skill development"
    return (
        f"Learning Agent: Built a {weeks}-week personalised roadmap for {username} "
        f"targeting: {goal_str}. "
        f"Daily commitment: {minutes} min. "
        f"Roadmap title: {learning.get('roadmap_title', 'Custom Path')}."
    )


def _mentor_reasoning(username: str, mentor: Dict) -> str:
    m = mentor.get("primary_mentor", mentor)
    name = m.get("name", "a community mentor")
    role = m.get("role", "industry expert")
    score = round(m.get("compatibility_score", 0.85) * 100)
    match = m.get("match_reason", "skill and goal overlap")
    return (
        f"Mentor Agent: Matched {username} with {name} ({role}). "
        f"Compatibility score: {score}%. "
        f"Reason: {match}"
    )


def _member_response(user_id: str, profile: Dict) -> Dict:
    """Reshape pipeline output to the format page.tsx expects."""
    identity = profile.get("identity", {})
    discovery = profile.get("discovery", {})
    learning = profile.get("learning", {})
    mentor = profile.get("mentor", {})

    user_data = get_mock_user(user_id) or {}
    username = user_data.get("username") or user_id.split("-")[0]

    # Merge all skill signals: LLM-inferred + stored tags + interests
    inferred = list(identity.get("inferred_skills", {}).keys())
    stored_tags = user_data.get("tags", [])
    interests = user_data.get("interests", [])
    skills = inferred or list(dict.fromkeys(stored_tags + interests))

    return {
        "member_id": user_id,
        "name": username,
        "bio": user_data.get("bio", ""),
        "skills": skills,
        "welcome_message": f"Welcome back, {username}! Here are your personalised recommendations.",
        "milestones": learning.get("milestones", [])[:3],
        "roadmap_title": learning.get("roadmap_title", ""),
        "priorities": (
            learning.get("checklist", [])[:3]
            if isinstance(learning.get("checklist"), list) and learning.get("checklist")
            else [
                (m.get("objectives", [""])[0] if isinstance(m.get("objectives"), list) else m.get("objectives", ""))
                for m in learning.get("milestones", [])[:3]
                if m.get("objectives")
            ]
        ),
        "recommended_mentor": {
            "name": mentor.get("primary_mentor", {}).get("name", mentor.get("mentor_name", "")),
            "role": mentor.get("primary_mentor", {}).get("role", mentor.get("mentor_role", "")),
            "overlap_reason": mentor.get("primary_mentor", {}).get("match_reason", mentor.get("match_reason", "")),
        },
        "communities": {
            "recommended": [
                {"id": c.get("id", ""), "name": c.get("name", ""), "description": c.get("description", "")}
                for c in discovery.get("recommended_channels", [])
            ],
            "lower_priority": [
                {"id": c.get("id", ""), "name": c.get("name", ""), "description": c.get("description", "")}
                for c in discovery.get("lower_priority_channels", [])
            ],
        },
        "resources": [
            {
                "id": r.get("resource_id", r.get("id", "")),
                "name": r.get("title", r.get("name", "")),
                "url": _RESOURCE_URL_MAP.get(r.get("resource_id", ""), {}).get("url") or r.get("url") or "#",
                "type": _RESOURCE_URL_MAP.get(r.get("resource_id", ""), {}).get("type") or r.get("type", "Guide"),
                "description": r.get("reason", r.get("description", "")),
            }
            for r in discovery.get("recommended_resources", [])
        ],
        "events": [
            {"id": e.get("id", ""), "name": e.get("title", e.get("name", "")), "time": e.get("time", ""), "description": e.get("description", "")}
            for e in discovery.get("upcoming_events", [])
        ],
        "insights": identity.get("insights", []),
        "explainability": {
            "identity_agent": identity.get("reasoning") or _identity_reasoning(username, skills, identity),
            "discovery_agent": discovery.get("reasoning") or _discovery_reasoning(username, discovery),
            "learning_agent": learning.get("reasoning") or _learning_reasoning(username, learning, user_data),
            "mentor_agent": mentor.get("reasoning") or _mentor_reasoning(username, mentor),
        },
    }


@router.get("/api/members/{user_id}")
async def get_member(user_id: str) -> Dict[str, Any]:
    """Return member profile in the format the Next.js frontend expects."""
    user_data = get_mock_user(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")

    cache_key = cache_service.agent_key("personalization", user_id)
    cached = cache_service.get(cache_key)
    if cached:
        return _member_response(user_id, cached)

    try:
        profile = await run_member_pipeline(user_id, user_data)
        return _member_response(user_id, profile)
    except Exception as e:
        logger.error(f"Compat member fetch failed for {user_id}: {e}")
        identity = get_mock_identity(user_id, user_data)
        discovery = get_mock_discovery(user_id, identity)
        learning = get_mock_learning(user_id, identity)
        mentor = get_mock_mentor(user_id, identity)
        return _member_response(user_id, {
            "identity": identity, "discovery": discovery,
            "learning": learning, "mentor": mentor,
        })


@router.get("/api/organizer")
async def get_organizer() -> Dict[str, Any]:
    """Return community health in the format the Next.js frontend expects."""
    try:
        combined = await run_community_pipeline()
        health = combined.get("health", {})
        organizer = combined.get("actions", {})
    except Exception:
        health = get_mock_health()
        organizer = get_mock_organizer()

    return {
        "metrics": {
            "active_members_ratio": health.get("active_members_ratio", "83%"),
            "weekly_messages": health.get("weekly_messages", 42),
            "unanswered_threads": health.get("unanswered_threads", 1),
            "at_risk_members": len(health.get("at_risk_members", [])),
        },
        "health_summary": {
            "ignored_newcomers": health.get("ignored_newcomers", []),
            "unanswered_questions": health.get("unanswered_questions", []),
            "inactive_members": health.get("inactive_members", []),
            "trending_topics": health.get("trending_topics", []),
            "explainability": health.get("reasoning", ""),
        },
        "insights": {
            "suggested_events": organizer.get("suggested_events", []),
            "potential_mentors": organizer.get("potential_mentors", []),
            "members_at_risk": organizer.get("members_at_risk", []),
            "suggested_actions": organizer.get("suggested_actions", []),
            "explainability": organizer.get("reasoning", ""),
        },
    }
