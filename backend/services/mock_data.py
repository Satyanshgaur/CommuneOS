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


def get_mock_discovery(user_id: str, identity: Optional[Dict] = None) -> Dict[str, Any]:
    """Return mock Discovery Agent output."""
    seed = _seed(user_id)

    channel_pool = [
        {"channel_id": "ch-ml", "name": "Machine Learning", "relevance_score": 0.92, "reason": "Matches your ML interests and beginner skill level", "difficulty": "Intermediate"},
        {"channel_id": "ch-cuda", "name": "GPU & Accelerators", "relevance_score": 0.88, "reason": "High overlap with your CUDA background", "difficulty": "Advanced"},
        {"channel_id": "ch-systems", "name": "Systems Programming", "relevance_score": 0.85, "reason": "Aligns with C++ and Linux systems expertise", "difficulty": "Advanced"},
        {"channel_id": "ch-data", "name": "Data Science & Python", "relevance_score": 0.80, "reason": "Python is your primary language", "difficulty": "Beginner"},
        {"channel_id": "ch-ai-infra", "name": "AI Infrastructure", "relevance_score": 0.76, "reason": "Growth area matching your distribution interests", "difficulty": "Advanced"},
        {"channel_id": "ch-react", "name": "React Frameworks", "relevance_score": 0.65, "reason": "Web tech complement to your backend skills", "difficulty": "Intermediate"},
        {"channel_id": "ch-open-source", "name": "Open Source Contribution", "relevance_score": 0.72, "reason": "Community engagement opportunity", "difficulty": "Intermediate"},
    ]
    
    resource_pool = [
        {"resource_id": "res-001", "title": "PyTorch Tensors: A Visual Guide", "type": "Video", "duration": "18 min", "difficulty": "Beginner", "relevance_score": 0.94, "reason": "Directly matches your ML onboarding path"},
        {"resource_id": "res-002", "title": "CUDA Shared Memory & Coalescing", "type": "Article", "duration": "25 min", "difficulty": "Advanced", "relevance_score": 0.91, "reason": "Critical for GPU optimization goals"},
        {"resource_id": "res-003", "title": "Linux Kernel Module Programming Guide", "type": "Guide", "duration": "60 min", "difficulty": "Intermediate", "relevance_score": 0.83, "reason": "Aligns with systems programming interest"},
        {"resource_id": "res-004", "title": "NumPy Matrix Operations in Practice", "type": "Interactive Notebook", "duration": "30 min", "difficulty": "Beginner", "relevance_score": 0.78, "reason": "Bridges your math background to Python"},
        {"resource_id": "res-005", "title": "Distributed PyTorch Training Guide", "type": "Tutorial", "duration": "45 min", "difficulty": "Advanced", "relevance_score": 0.75, "reason": "Next step in your AI infrastructure journey"},
        {"resource_id": "res-006", "title": "Rust Programming for Systems Engineers", "type": "Guide", "duration": "90 min", "difficulty": "Advanced", "relevance_score": 0.88, "reason": "Great addition for learning low-level safety"},
        {"resource_id": "res-007", "title": "FastAPI Complete Tutorial: From Zero to Production", "type": "Video", "duration": "120 min", "difficulty": "Intermediate", "relevance_score": 0.85, "reason": "Build production-ready backend APIs using Python"},
        {"resource_id": "res-008", "title": "Docker & Kubernetes: MLOps Containerization", "type": "Article", "duration": "35 min", "difficulty": "Intermediate", "relevance_score": 0.80, "reason": "Necessary for scaling and deploying ML models"},
        {"resource_id": "res-009", "title": "Introduction to Transformers & NLP", "type": "Tutorial", "duration": "50 min", "difficulty": "Intermediate", "relevance_score": 0.82, "reason": "Deep dive into language models and modern neural architectures"},
        {"resource_id": "res-010", "title": "UI/UX Design Patterns for AI Applications", "type": "Guide", "duration": "40 min", "difficulty": "Beginner", "relevance_score": 0.70, "reason": "Design interfaces that feel alive and responsive"},
        {"resource_id": "res-011", "title": "Deep Reinforcement Learning in PyTorch", "type": "Tutorial", "duration": "75 min", "difficulty": "Advanced", "relevance_score": 0.77, "reason": "Learn DQN, PPO and how to build game agents"},
        {"resource_id": "res-012", "title": "Advanced C++ Memory Management", "type": "Article", "duration": "30 min", "difficulty": "Advanced", "relevance_score": 0.84, "reason": "Important for high performance C++ and GPU interaction"},
        {"resource_id": "res-013", "title": "Git Workflows for Large Engineering Teams", "type": "Guide", "duration": "25 min", "difficulty": "Beginner", "relevance_score": 0.72, "reason": "Collaborate effectively with main branches and checkpoints"},
        {"resource_id": "res-014", "title": "Model Deployment with MLflow & Triton", "type": "Tutorial", "duration": "55 min", "difficulty": "Advanced", "relevance_score": 0.79, "reason": "Learn to serve models with ultra-low latency"},
        {"resource_id": "res-015", "title": "Data Visualization Best Practices with Seaborn", "type": "Interactive Notebook", "duration": "45 min", "difficulty": "Beginner", "relevance_score": 0.76, "reason": "Improve user-facing data reporting and dashboards"},
        {"resource_id": "res-016", "title": "Introduction to GPU Programming with WebGPU", "type": "Video", "duration": "35 min", "difficulty": "Intermediate", "relevance_score": 0.81, "reason": "GPU acceleration directly in the web browser"},
        {"resource_id": "res-017", "title": "FastAPI Authentication and Security Best Practices", "type": "Guide", "duration": "50 min", "difficulty": "Intermediate", "relevance_score": 0.83, "reason": "Secure endpoints and build robust auth pipelines"},
    ]
    
    # Select channels deterministically
    n_channels = 3 + (seed % 3)  # 3-5 channels
    selected_channels = []
    for i in range(min(n_channels, len(channel_pool))):
        selected_channels.append(channel_pool[(seed + i) % len(channel_pool)])
    
    n_resources = 3 + (seed % 4)  # 3-6 resources
    selected_resources = []
    for i in range(min(n_resources, len(resource_pool))):
        selected_resources.append(resource_pool[(seed + i) % len(resource_pool)])
    
    return {
        "user_id": user_id,
        "recommended_channels": selected_channels,
        "recommended_resources": selected_resources,
        "discovery_priority": [c["name"] for c in selected_channels[:3]],
        "_is_fallback": True,
    }


def get_mock_learning(user_id: str, identity: Optional[Dict] = None) -> Dict[str, Any]:
    """Return mock Learning Agent output."""
    seed = _seed(user_id)
    
    roadmap_titles = [
        "ML Foundations to Practice",
        "GPU Systems Mastery Path",
        "Full Stack AI Engineer Path",
        "Data Science Fundamentals",
        "Systems Programming Deep Dive",
    ]
    title = roadmap_titles[seed % len(roadmap_titles)]
    
    milestones = [
        {
            "week": 1,
            "title": "Foundations & Setup",
            "objectives": ["Set up development environment", "Understand core concepts", "Complete intro exercises"],
            "resources": ["res-001", "res-004"],
            "estimated_hours": 5.0
        },
        {
            "week": 2,
            "title": "Core Skills Development",
            "objectives": ["Master fundamental operations", "Build first project", "Join community discussions"],
            "resources": ["res-002", "res-003"],
            "estimated_hours": 7.0
        },
        {
            "week": 3,
            "title": "Intermediate Concepts",
            "objectives": ["Apply skills to real problems", "Peer review sessions", "Contribute to community"],
            "resources": ["res-005"],
            "estimated_hours": 8.0
        },
        {
            "week": 4,
            "title": "Advanced Application",
            "objectives": ["Build capstone project", "Mentor junior members", "Present learnings"],
            "resources": [],
            "estimated_hours": 10.0
        },
    ]
    
    checklist = [
        {"task_id": f"task-{user_id}-1", "task": "Read today's featured article in your primary channel", "type": "reading", "duration_minutes": 20, "resource_link": None, "completed": False},
        {"task_id": f"task-{user_id}-2", "task": "Complete one hands-on exercise from your roadmap", "type": "coding", "duration_minutes": 45, "resource_link": None, "completed": False},
        {"task_id": f"task-{user_id}-3", "task": "Answer or ask one question in the community", "type": "discussion", "duration_minutes": 15, "resource_link": None, "completed": False},
    ]
    
    completion_date = (datetime.utcnow() + timedelta(weeks=8)).strftime("%B %d, %Y")
    
    return {
        "user_id": user_id,
        "roadmap_title": title,
        "total_weeks": 8,
        "daily_commitment_minutes": 60 + (seed % 30),
        "milestones": milestones,
        "daily_checklist": checklist,
        "estimated_completion_date": completion_date,
        "_is_fallback": True,
    }


def get_mock_mentor(user_id: str, identity: Optional[Dict] = None) -> Dict[str, Any]:
    """Return mock Mentor Agent output."""
    seed = _seed(user_id)
    
    mentor_pool = [
        {
            "mentor_id": "mentor-sarah", "name": "Sarah Jenkins",
            "role": "Principal GPU Engineer at NVIDIA", "avatar": "SJ",
            "expertise_areas": ["CUDA", "GPU Architecture", "Distributed Systems"],
            "compatibility_score": 0.94,
            "match_reason": "Expert in CUDA Memory optimization. Has 5+ years experience and mentored 12+ developers.",
            "availability": "Weekdays 6-8 PM IST", "teaching_style": "Hands-on projects with code reviews",
            "years_experience": 8
        },
        {
            "mentor_id": "mentor-amit", "name": "Amit Sharma",
            "role": "AI Infrastructure Lead", "avatar": "AS",
            "expertise_areas": ["PyTorch", "MLOps", "Distributed Training"],
            "compatibility_score": 0.86,
            "match_reason": "Works on distributed PyTorch engines. Good match for ML infrastructure goals.",
            "availability": "Weekends 10 AM - 12 PM IST", "teaching_style": "Theory-first with practical examples",
            "years_experience": 6
        },
        {
            "mentor_id": "mentor-priya", "name": "Priya Nair",
            "role": "Senior Data Scientist", "avatar": "PN",
            "expertise_areas": ["Python", "Data Science", "Machine Learning"],
            "compatibility_score": 0.81,
            "match_reason": "Strong foundation in data science fundamentals. Great for beginners.",
            "availability": "Flexible evenings", "teaching_style": "Structured curriculum with checkpoints",
            "years_experience": 5
        },
        {
            "mentor_id": "mentor-marcus", "name": "Marcus Chen",
            "role": "Senior Systems Developer", "avatar": "MC",
            "expertise_areas": ["C++", "Linux Systems", "Rust"],
            "compatibility_score": 0.89,
            "match_reason": "Deep background in low-level systems programming and memory safety using Rust.",
            "availability": "Mon/Wed/Fri 7-9 PM", "teaching_style": "Deep dive into system internals and debugging",
            "years_experience": 10
        },
        {
            "mentor_id": "mentor-elena", "name": "Elena Rostova",
            "role": "Deep Learning Researcher", "avatar": "ER",
            "expertise_areas": ["NLP", "Transformers", "PyTorch"],
            "compatibility_score": 0.87,
            "match_reason": "Passionate about large language models, custom attention heads and transformers.",
            "availability": "Tuesday evenings", "teaching_style": "Paper discussions combined with implementation",
            "years_experience": 7
        },
        {
            "mentor_id": "mentor-david", "name": "David Miller",
            "role": "DevOps Architect", "avatar": "DM",
            "expertise_areas": ["Kubernetes", "Docker", "Cloud Infra"],
            "compatibility_score": 0.83,
            "match_reason": "Enjoys containerizing large systems and managing distributed clusters.",
            "availability": "Saturdays 9-11 AM", "teaching_style": "Config-heavy step-by-step infrastructure building",
            "years_experience": 9
        },
        {
            "mentor_id": "mentor-aisha", "name": "Aisha Rahman",
            "role": "MLOps Engineer", "avatar": "AR",
            "expertise_areas": ["Model Deployment", "MLflow", "FastAPI"],
            "compatibility_score": 0.85,
            "match_reason": "Bridges research code and production deployment with high efficiency.",
            "availability": "Weekdays 8-9 PM", "teaching_style": "Practical MLOps pipelines and APIs",
            "years_experience": 4
        },
        {
            "mentor_id": "mentor-yuki", "name": "Yuki Tanaka",
            "role": "Frontend Tech Lead", "avatar": "YT",
            "expertise_areas": ["React", "TypeScript", "UI/UX"],
            "compatibility_score": 0.80,
            "match_reason": "Expert in state management, responsive designs, and interactive AI dashboards.",
            "availability": "Fridays 4-6 PM", "teaching_style": "Interactive frontend pairing and layout refactoring",
            "years_experience": 6
        },
        {
            "mentor_id": "mentor-clara", "name": "Clara Dupont",
            "role": "Product Manager AI", "avatar": "CD",
            "expertise_areas": ["Product Strategy", "UX Research", "Agile"],
            "compatibility_score": 0.82,
            "match_reason": "Specializes in product lifecycle, user interviewing, and metrics-driven development.",
            "availability": "Thursday afternoons", "teaching_style": "Case studies, mockup reviews, and user flow feedback",
            "years_experience": 7
        },
        {
            "mentor_id": "mentor-james", "name": "James Wilson",
            "role": "Reinforcement Learning Expert", "avatar": "JW",
            "expertise_areas": ["RL", "Robotics", "Python"],
            "compatibility_score": 0.84,
            "match_reason": "Experienced in building complex simulation environments and Q-learning architectures.",
            "availability": "Weekends variable", "teaching_style": "Simulation builds and agent tuning sessions",
            "years_experience": 8
        },
    ]
    
    primary_idx = seed % len(mentor_pool)
    backup_idx = (seed + 1) % len(mentor_pool)
    
    return {
        "user_id": user_id,
        "primary_mentor": mentor_pool[primary_idx],
        "backup_mentors": [mentor_pool[backup_idx]],
        "suggested_meeting_schedule": "Weekly 45-minute sessions, flexible scheduling",
        "introduction_template": f"Hi! I'm a community member interested in connecting with you as a mentor. I've been working on [topic] and would love guidance on [specific area].",
        "_is_fallback": True,
    }


def get_mock_health(community_data: Optional[Dict] = None) -> Dict[str, Any]:
    """Return mock Health Agent output for community-level data."""
    return {
        "community_health_score": 0.74,
        "total_members": 247,
        "active_members_7d": 89,
        "at_risk_members": [
            {"user_id": "user-456", "username": "inactive_dev", "risk_level": "high", "days_inactive": 18, "last_seen": "2025-01-02", "reason": "No activity in 18 days, previously active daily"},
            {"user_id": "user-789", "username": "new_joiner", "risk_level": "medium", "days_inactive": 9, "last_seen": "2025-01-11", "reason": "New member with no engagement after joining"},
        ],
        "topic_gaps": [
            {"topic": "Advanced CUDA Optimization", "unanswered_questions": 12, "demand_score": 0.87, "suggestion": "Schedule weekly CUDA office hours with Sarah Jenkins"},
            {"topic": "MLOps & Deployment", "unanswered_questions": 8, "demand_score": 0.74, "suggestion": "Create a dedicated MLOps resource library"},
            {"topic": "Rust for Systems", "unanswered_questions": 5, "demand_score": 0.62, "suggestion": "Invite Rust experts for an AMA session"},
        ],
        "trending_topics": ["CUDA optimization", "PyTorch 2.0", "Distributed training", "Linux internals"],
        "engagement_trend": "stable",
        "summary": "Community health is moderate. Key focus areas: re-engagement of dormant members and filling topic gaps in advanced CUDA content.",
        "_is_fallback": True,
    }


def get_mock_organizer(health_data: Optional[Dict] = None) -> Dict[str, Any]:
    """Return mock Organizer Agent output."""
    return {
        "action_items": [
            {
                "action_id": f"action-{uuid.uuid4().hex[:8]}",
                "title": "Send personalized welcome to 3 new members",
                "description": "New members joined this week without receiving personalized welcome messages. Reach out within 24 hours.",
                "priority": "critical",
                "category": "welcome",
                "assignee": "community_manager",
                "deadline": (datetime.utcnow() + timedelta(hours=24)).strftime("%Y-%m-%d"),
                "expected_impact": "30% improvement in new member retention",
                "completed": False,
            },
            {
                "action_id": f"action-{uuid.uuid4().hex[:8]}",
                "title": "Follow up with 2 high-risk churning members",
                "description": "Members inactive for 14+ days. Send personalized check-in messages referencing their previous activity.",
                "priority": "high",
                "category": "engagement",
                "assignee": "community_manager",
                "deadline": (datetime.utcnow() + timedelta(days=2)).strftime("%Y-%m-%d"),
                "expected_impact": "Recover 40% of at-risk members",
                "completed": False,
            },
            {
                "action_id": f"action-{uuid.uuid4().hex[:8]}",
                "title": "Create CUDA optimization resource guide",
                "description": "12 unanswered questions about CUDA optimization. Create a comprehensive FAQ or beginner guide.",
                "priority": "medium",
                "category": "content",
                "assignee": "sarah_jenkins",
                "deadline": (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d"),
                "expected_impact": "Reduce support load by 60% for CUDA questions",
                "completed": False,
            },
        ],
        "event_suggestions": [
            {
                "event_id": f"evt-{uuid.uuid4().hex[:8]}",
                "title": "CUDA Memory Architecture Deep Dive",
                "type": "Workshop",
                "topic": "Advanced CUDA Optimization",
                "rationale": "12 unanswered community questions. High demand signal. Sarah Jenkins available.",
                "suggested_timing": "Next Tuesday 7:00 PM IST",
                "target_audience": "Intermediate to Advanced GPU developers",
                "expected_attendance": 25,
            },
            {
                "event_id": f"evt-{uuid.uuid4().hex[:8]}",
                "title": "MLOps & Model Deployment AMA",
                "type": "AMA",
                "topic": "MLOps & Deployment",
                "rationale": "Growing interest in production deployment. 8 unanswered questions this week.",
                "suggested_timing": "Next Thursday 6:00 PM IST",
                "target_audience": "All members interested in production ML",
                "expected_attendance": 40,
            },
        ],
        "automation_recommendations": [
            "Set up auto-welcome for new members within 1 hour of joining",
            "Auto-notify mentors when their topic area has 3+ unanswered questions",
            "Weekly digest email for inactive members (7-14 days) with top community posts",
        ],
        "resource_allocation": "Focus 60% effort on member retention this week. 40% on content creation for CUDA and MLOps gaps.",
        "summary": "Priority this week: onboarding 3 new members and re-engaging 2 churning members. Two events suggested to fill community knowledge gaps.",
        "_is_fallback": True,
    }


# In-memory user store for development (replaces database in Phase 1)
_user_store: Dict[str, Dict] = {}


def get_mock_user(user_id: str) -> Optional[Dict]:
    """Get a mock user from the in-memory store."""
    return _user_store.get(user_id.lower())


def save_mock_user(user_id: str, user_data: Dict) -> None:
    """Save a user to the in-memory store."""
    _user_store[user_id.lower()] = user_data
    logger.info(f"Saved user to mock store: {user_id}")


def list_mock_users() -> List[Dict]:
    """List all users in the mock store."""
    return list(_user_store.values())
