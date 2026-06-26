"""
CommuneOS Mock Data Service
Pre-generated realistic fallback data for all 6 agents.
Returns deterministic responses based on user_id seeding.
"""
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from utils.logger import get_logger

logger = get_logger("mock_data")


def _seed(user_id: str) -> int:
    """Create a deterministic seed from user_id for variety without true randomness."""
    return int(hashlib.md5(user_id.encode()).hexdigest()[:8], 16)


def get_mock_identity(user_id: str, profile: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Return mock Identity Agent output.
    Varies by user_id to provide different responses to different users.
    """
    seed = _seed(user_id)
    
    # Skill pool — pick deterministically
    skill_pool = [
        {"name": "Python", "proficiency": "Intermediate", "confidence": 0.82, "source": "stated"},
        {"name": "Machine Learning", "proficiency": "Beginner", "confidence": 0.65, "source": "inferred"},
        {"name": "CUDA", "proficiency": "Advanced", "confidence": 0.78, "source": "activity"},
        {"name": "React", "proficiency": "Intermediate", "confidence": 0.71, "source": "stated"},
        {"name": "Data Science", "proficiency": "Intermediate", "confidence": 0.68, "source": "inferred"},
        {"name": "C++", "proficiency": "Advanced", "confidence": 0.85, "source": "activity"},
        {"name": "PyTorch", "proficiency": "Beginner", "confidence": 0.60, "source": "inferred"},
        {"name": "Linux Systems", "proficiency": "Intermediate", "confidence": 0.73, "source": "stated"},
    ]
    
    # Extract from profile if available
    detected_skills = []
    if profile and profile.get("skills"):
        for skill_name, level in profile["skills"].items():
            level_map = {1: "Beginner", 2: "Beginner", 3: "Intermediate", 4: "Advanced", 5: "Expert"}
            detected_skills.append({
                "name": skill_name,
                "proficiency": level_map.get(level, "Intermediate"),
                "confidence": 0.75,
                "source": "stated"
            })
    else:
        # Select 3 skills deterministically
        indices = [(seed % len(skill_pool)), ((seed + 1) % len(skill_pool)), ((seed + 2) % len(skill_pool))]
        detected_skills = [skill_pool[i] for i in indices]
    
    expertise_pools = [
        ["Systems Programming", "GPU Optimization"],
        ["Machine Learning", "Data Analysis"],
        ["Web Development", "Frontend Engineering"],
        ["AI Research", "Deep Learning"],
        ["Cloud Infrastructure", "DevOps"],
    ]
    growth_pools = [
        ["Distributed Systems", "Kernel Development"],
        ["MLOps", "Model Deployment"],
        ["TypeScript", "System Design"],
        ["Reinforcement Learning", "NLP"],
        ["Kubernetes", "Observability"],
    ]
    
    idx = seed % len(expertise_pools)
    learning_styles = ["visual", "reading", "kinesthetic", "auditory"]
    
    return {
        "user_id": user_id,
        "detected_skills": detected_skills,
        "expertise_areas": expertise_pools[idx],
        "growth_areas": growth_pools[idx],
        "learning_preference": learning_styles[seed % len(learning_styles)],
        "overall_confidence": 0.62 + (seed % 20) * 0.01,
        "summary": f"Profile built from stated skills and community activity. Confidence: {round(0.62 + (seed % 20) * 0.01, 2)}",
        "_is_fallback": True,
    }


def get_mock_discovery(user_id: str, identity: Optional[Dict] = None, community_id: str = "comm-gpu") -> Dict[str, Any]:
    """Return mock Discovery Agent output scoped by community_id."""
    from services.db import get_channels_by_community, get_resources_by_community
    channels = get_channels_by_community(community_id)
    resources = get_resources_by_community(community_id)

    selected_channels = []
    for i, ch in enumerate(channels):
        selected_channels.append({
            "channel_id": ch["channel_id"],
            "name": ch["name"],
            "relevance_score": round(0.85 + (i * 0.03), 2),
            "reason": f"Matches your interest in {ch['name']}",
            "difficulty": "Intermediate" if i % 2 == 0 else "Advanced"
        })

    selected_resources = []
    for r in resources:
        selected_resources.append({
            "resource_id": r["resource_id"],
            "title": r["title"],
            "type": r["type"],
            "duration": r["duration"],
            "difficulty": r["difficulty"],
            "relevance_score": r.get("relevance_score", 0.8),
            "reason": r.get("reason", "Relevant to your learning path")
        })

    return {
        "user_id": user_id,
        "recommended_channels": selected_channels,
        "recommended_resources": selected_resources,
        "discovery_priority": [c["name"] for c in selected_channels[:3]] if selected_channels else ["Explore Channels"],
        "_is_fallback": True,
    }


def get_mock_learning(user_id: str, identity: Optional[Dict] = None, community_id: str = "comm-gpu") -> Dict[str, Any]:
    """Return mock Learning Agent output scoped by community_id."""
    from services.db import learning_tracks_table
    track = learning_tracks_table.get(community_id)
    if not track:
        track = learning_tracks_table.get("comm-gpu")

    milestones = track["milestones"]

    if community_id == "comm-gpu":
        checklist = [
            {"task_id": f"task-{user_id}-1", "task": "Read CUDA Shared Memory & Coalescing Techniques", "type": "reading", "duration_minutes": 25, "resource_link": "res-cuda-mem", "completed": False},
            {"task_id": f"task-{user_id}-2", "task": "Optimize GEMM kernel parameters on sample harness", "type": "coding", "duration_minutes": 60, "resource_link": "proj-cuda", "completed": False},
            {"task_id": f"task-{user_id}-3", "task": "Ask one question in GPU & Accelerators channel", "type": "discussion", "duration_minutes": 15, "resource_link": None, "completed": False},
        ]
    else:
        checklist = [
            {"task_id": f"task-{user_id}-1", "task": "Watch PyTorch Tensors Visual Guide video", "type": "watching", "duration_minutes": 18, "resource_link": "res-torch-tensors", "completed": False},
            {"task_id": f"task-{user_id}-2", "task": "Write basic linear regression forward pass in NumPy", "type": "coding", "duration_minutes": 45, "resource_link": "proj-mnist", "completed": False},
            {"task_id": f"task-{user_id}-3", "task": "Discuss gradient descent logic in ML channel", "type": "discussion", "duration_minutes": 15, "resource_link": None, "completed": False},
        ]

    return {
        "user_id": user_id,
        "roadmap_title": track["roadmap_title"],
        "total_weeks": track["total_weeks"],
        "daily_commitment_minutes": track["daily_commitment_minutes"],
        "milestones": milestones,
        "daily_checklist": checklist,
        "estimated_completion_date": track["estimated_completion_date"],
        "_is_fallback": True,
    }


def get_mock_mentor(user_id: str, identity: Optional[Dict] = None, community_id: str = "comm-gpu") -> Dict[str, Any]:
    """Return mock Mentor Agent output scoped by community_id."""
    from services.db import get_mentors_by_community
    mentors = get_mentors_by_community(community_id)
    if not mentors:
        mentors = get_mentors_by_community("comm-gpu")

    seed = _seed(user_id)
    primary_idx = seed % len(mentors)
    backup_idx = (seed + 1) % len(mentors)

    primary = mentors[primary_idx]
    backup = mentors[backup_idx] if len(mentors) > 1 else mentors[primary_idx]

    def enrich_mentor(m):
        initials = "".join([part[0] for part in m["name"].split() if part])
        return {
            "mentor_id": m["mentor_id"],
            "name": m["name"],
            "role": m["role"],
            "avatar": initials,
            "expertise_areas": m["expertise_areas"],
            "compatibility_score": m.get("compatibility_score", 0.9),
            "match_reason": m.get("match_reason", f"Highly compatible with your {community_id} learning path."),
            "availability": m.get("availability", "Flexible timings"),
            "teaching_style": m.get("teaching_style", "Hands-on coding reviews"),
            "years_experience": m.get("years_experience", 5),
        }

    return {
        "user_id": user_id,
        "primary_mentor": enrich_mentor(primary),
        "backup_mentors": [enrich_mentor(backup)] if backup != primary else [],
        "suggested_meeting_schedule": "Weekly 45-minute sessions, flexible scheduling",
        "introduction_template": f"Hi! I'm a community member interested in connecting with you as a mentor. I've been working on my roadmap and would love guidance.",
        "_is_fallback": True,
    }


def get_mock_health(community_id: str = "comm-gpu") -> Dict[str, Any]:
    """Return mock Health Agent output for community-level data."""
    if community_id == "comm-gpu":
        return {
            "community_health_score": 0.82,
            "total_members": 142,
            "active_members_7d": 89,
            "at_risk_members": [
                {"user_id": "user-456", "username": "inactive_gpu_dev", "risk_level": "high", "days_inactive": 18, "last_seen": "2025-01-02", "reason": "No activity in GPU channels for 18 days"},
            ],
            "topic_gaps": [
                {"topic": "Advanced CUDA Optimization", "unanswered_questions": 12, "demand_score": 0.87, "suggestion": "Schedule weekly CUDA office hours"},
            ],
            "trending_topics": ["CUDA memory", "Shared registers", "GPU kernels"],
            "engagement_trend": "stable",
            "summary": "GPU Systems Guild health is strong. Core bottleneck: bank conflicts in CUDA shared memory.",
            "_is_fallback": True,
        }
    else: # comm-ml
        return {
            "community_health_score": 0.74,
            "total_members": 218,
            "active_members_7d": 112,
            "at_risk_members": [
                {"user_id": "user-789", "username": "inactive_ml_learner", "risk_level": "medium", "days_inactive": 12, "last_seen": "2025-01-08", "reason": "No PyTorch runs submitted in 12 days"},
            ],
            "topic_gaps": [
                {"topic": "PyTorch AutoGrad", "unanswered_questions": 8, "demand_score": 0.74, "suggestion": "Create dedicated NumPy to PyTorch FAQ guides"},
            ],
            "trending_topics": ["PyTorch tensors", "NumPy matrices", "AutoGrad graphs"],
            "engagement_trend": "rising",
            "summary": "ML Practitioners Cohort is growing rapidly. Core bottleneck: understanding computation graphs.",
            "_is_fallback": True,
        }


def get_mock_organizer(community_id: str = "comm-gpu") -> Dict[str, Any]:
    """Return mock Organizer Agent output scoped by community_id."""
    from services.db import get_actions_by_community
    actions = get_actions_by_community(community_id)
    action_items = []
    for a in actions:
        action_items.append({
            "action_id": a["action_id"],
            "title": a["title"],
            "description": a["description"],
            "priority": "high",
            "category": "content",
            "assignee": a["assignee"],
            "deadline": "2026-07-01",
            "expected_impact": a["expected_impact"],
            "completed": a["completed"]
        })
    return {
        "action_items": action_items,
        "event_suggestions": [
            {
                "event_id": "evt-sug-1",
                "title": "Interactive Q&A Session" if community_id == "comm-gpu" else "Tensors Visual Roundtable",
                "type": "Workshop",
                "topic": "CUDA Optimization" if community_id == "comm-gpu" else "PyTorch AutoGrad",
                "rationale": "High unanswered questions count.",
                "suggested_timing": "Next Tuesday 7:00 PM IST",
                "target_audience": "All active learners",
                "expected_attendance": 20
            }
        ],
        "automation_recommendations": [
            "Auto-notify mentors when topic area has unanswered questions"
        ],
        "summary": "Retention and answering topic gaps are top priorities.",
        "_is_fallback": True
    }


def get_mock_user(user_id: str) -> Optional[Dict]:
    """Get a mock user from the in-memory store."""
    from services.db import users_table
    return users_table.get(user_id.lower())


def save_mock_user(user_id: str, user_data: Dict) -> None:
    """Save a user to the in-memory store."""
    from services.db import users_table
    users_table[user_id.lower()] = user_data
    logger.info(f"Saved user to mock store: {user_id}")


def list_mock_users() -> List[Dict]:
    """List all users in the mock store."""
    from services.db import users_table
    return list(users_table.values())
