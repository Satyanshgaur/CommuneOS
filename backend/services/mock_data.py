"""
CommuneOS Mock Data Service
Pre-generated realistic fallback data for all 6 agents.
Returns deterministic responses based on user_id seeding.
"""
import hashlib
import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from utils.logger import get_logger

logger = get_logger("mock_data")

_USERS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "users.json")
_USERS_FILE = os.path.normpath(_USERS_FILE)


def _load_persisted_users() -> Dict[str, Dict]:
    try:
        if os.path.exists(_USERS_FILE):
            with open(_USERS_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load persisted users: {e}")
    return {}


def _persist_users(store: Dict[str, Dict]) -> None:
    try:
        os.makedirs(os.path.dirname(_USERS_FILE), exist_ok=True)
        with open(_USERS_FILE, "w") as f:
            json.dump(store, f, indent=2, default=str)
    except Exception as e:
        logger.warning(f"Could not persist users: {e}")


def _seed(user_id: str) -> int:
    """Create a deterministic seed from user_id for variety without true randomness."""
    return int(hashlib.md5(user_id.encode()).hexdigest()[:8], 16)


def _keywords(profile: Optional[Dict]) -> set:
    """Extract lowercase keywords from a user/identity profile for relevance scoring."""
    if not profile:
        return set()
    kws: set = set()
    for field in ("tags", "interests", "goals"):
        for item in profile.get(field, []):
            kws.update(str(item).lower().split())
    for skill in profile.get("detected_skills", []):
        kws.update(str(skill.get("name", "")).lower().split())
    for area in profile.get("expertise_areas", []) + profile.get("growth_areas", []):
        kws.update(str(area).lower().split())
    bio = profile.get("bio", "")
    if bio:
        stop = {"and", "or", "the", "a", "an", "in", "to", "of", "for", "with", "i", "my", "is", "am"}
        kws.update(w for w in bio.lower().split() if w not in stop and len(w) > 2)
    return kws


def _score(item_text: str, keywords: set) -> int:
    """Count keyword hits in a text string using substring matching."""
    text_lower = item_text.lower()
    return sum(1 for kw in keywords if kw in text_lower)


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
    
    # Extract from profile if available — prefer explicit tags/interests over generic skills dict
    detected_skills = []
    if profile and profile.get("tags"):
        for tag in profile.get("tags", []):
            detected_skills.append({"name": tag, "proficiency": "Intermediate", "confidence": 0.78, "source": "stated"})
        for interest in profile.get("interests", []):
            detected_skills.append({"name": interest, "proficiency": "Beginner", "confidence": 0.65, "source": "interest"})
    elif profile and profile.get("skills"):
        for skill_name, level in profile["skills"].items():
            level_map = {1: "Beginner", 2: "Beginner", 3: "Intermediate", 4: "Advanced", 5: "Expert"}
            detected_skills.append({
                "name": skill_name,
                "proficiency": level_map.get(level, "Intermediate"),
                "confidence": 0.75,
                "source": "stated"
            })
    else:
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
        "inferred_skills": {s["name"]: s["confidence"] for s in detected_skills},
        "expertise_areas": expertise_pools[idx],
        "growth_areas": growth_pools[idx],
        "learning_preference": learning_styles[seed % len(learning_styles)],
        "overall_confidence": 0.62 + (seed % 20) * 0.01,
        "summary": f"Profile built from stated skills and community activity. Confidence: {round(0.62 + (seed % 20) * 0.01, 2)}",
        # Carry through user profile fields so downstream mock functions can rank by them
        "tags": profile.get("tags", []) if profile else [],
        "interests": profile.get("interests", []) if profile else [],
        "goals": profile.get("goals", []) if profile else [],
        "bio": profile.get("bio", "") if profile else "",
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
        {"channel_id": "ch-quant", "name": "Quant Finance & Trading", "relevance_score": 0.95, "reason": "Covers quant research, algorithmic trading, and finance fundamentals", "difficulty": "Advanced"},
        {"channel_id": "ch-lowlatency", "name": "Low Latency & HFT Systems", "relevance_score": 0.93, "reason": "Matches HFT and low-latency C++ systems interest", "difficulty": "Advanced"},
        {"channel_id": "ch-cpp", "name": "Modern C++ & Systems", "relevance_score": 0.90, "reason": "C++ core language, STL, memory, concurrency for systems programmers", "difficulty": "Advanced"},
        {"channel_id": "ch-competitive", "name": "Competitive Programming", "relevance_score": 0.82, "reason": "Algorithms, data structures, and contest prep", "difficulty": "Intermediate"},
    ]

    resource_pool = [
        {"resource_id": "res-001", "title": "PyTorch Tensors: A Visual Guide", "type": "Video", "duration": "18 min", "difficulty": "Beginner", "relevance_score": 0.94, "reason": "Directly matches your ML onboarding path", "url": "https://www.youtube.com/watch?v=ic55579V0g4"},
        {"resource_id": "res-002", "title": "CUDA Shared Memory & Coalescing", "type": "Article", "duration": "25 min", "difficulty": "Advanced", "relevance_score": 0.91, "reason": "Critical for GPU optimization goals", "url": "https://developer.nvidia.com/blog/using-shared-memory-cuda-cc/"},
        {"resource_id": "res-003", "title": "Linux Kernel Module Programming Guide", "type": "Guide", "duration": "60 min", "difficulty": "Intermediate", "relevance_score": 0.83, "reason": "Aligns with systems programming interest", "url": "https://tldp.org/LDP/lkmpg/2.6/html/lkmpg.html"},
        {"resource_id": "res-004", "title": "NumPy Matrix Operations in Practice", "type": "Interactive Notebook", "duration": "30 min", "difficulty": "Beginner", "relevance_score": 0.78, "reason": "Bridges your math background to Python", "url": "https://numpy.org/doc/stable/user/quickstart.html"},
        {"resource_id": "res-005", "title": "Distributed PyTorch Training Guide", "type": "Tutorial", "duration": "45 min", "difficulty": "Advanced", "relevance_score": 0.75, "reason": "Next step in your AI infrastructure journey", "url": "https://pytorch.org/tutorials/intermediate/ddp_tutorial.html"},
        {"resource_id": "res-006", "title": "Rust Programming for Systems Engineers", "type": "Guide", "duration": "90 min", "difficulty": "Advanced", "relevance_score": 0.88, "reason": "Great addition for learning low-level safety", "url": "https://doc.rust-lang.org/book/"},
        {"resource_id": "res-007", "title": "FastAPI Complete Tutorial: From Zero to Production", "type": "Video", "duration": "120 min", "difficulty": "Intermediate", "relevance_score": 0.85, "reason": "Build production-ready backend APIs using Python", "url": "https://www.youtube.com/watch?v=0sOvCWFmrtA"},
        {"resource_id": "res-008", "title": "Docker & Kubernetes: MLOps Containerization", "type": "Video", "duration": "35 min", "difficulty": "Intermediate", "relevance_score": 0.80, "reason": "Necessary for scaling and deploying ML models", "url": "https://www.youtube.com/watch?v=PtM44dh7RjI"},
        {"resource_id": "res-009", "title": "Introduction to Transformers & NLP", "type": "Tutorial", "duration": "50 min", "difficulty": "Intermediate", "relevance_score": 0.82, "reason": "Deep dive into language models and modern neural architectures", "url": "https://huggingface.co/learn/nlp-course/chapter1/1"},
        {"resource_id": "res-010", "title": "UI/UX Design Patterns for AI Applications", "type": "Article", "duration": "40 min", "difficulty": "Beginner", "relevance_score": 0.70, "reason": "Design interfaces that feel alive and responsive", "url": "https://uxdesign.cc/ui-cheat-sheet-d6facd7e2f4c"},
        {"resource_id": "res-011", "title": "Deep Reinforcement Learning in PyTorch", "type": "Video", "duration": "75 min", "difficulty": "Advanced", "relevance_score": 0.77, "reason": "Learn DQN, PPO and how to build game agents", "url": "https://www.youtube.com/watch?v=EUreLXAlPKs"},
        {"resource_id": "res-012", "title": "Advanced C++ Memory Management", "type": "Article", "duration": "30 min", "difficulty": "Advanced", "relevance_score": 0.84, "reason": "Important for high performance C++ and GPU interaction", "url": "https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#r-resource-management"},
        {"resource_id": "res-013", "title": "Git Workflows for Large Engineering Teams", "type": "Guide", "duration": "25 min", "difficulty": "Beginner", "relevance_score": 0.72, "reason": "Collaborate effectively with main branches and checkpoints", "url": "https://www.atlassian.com/git/tutorials/comparing-workflows"},
        {"resource_id": "res-014", "title": "Model Deployment with MLflow & Triton", "type": "Tutorial", "duration": "55 min", "difficulty": "Advanced", "relevance_score": 0.79, "reason": "Learn to serve models with ultra-low latency", "url": "https://mlflow.org/docs/latest/deployment/index.html"},
        {"resource_id": "res-015", "title": "Data Visualization Best Practices with Seaborn", "type": "Interactive Notebook", "duration": "45 min", "difficulty": "Beginner", "relevance_score": 0.76, "reason": "Improve user-facing data reporting and dashboards", "url": "https://seaborn.pydata.org/tutorial.html"},
        {"resource_id": "res-016", "title": "Introduction to GPU Programming with WebGPU", "type": "Video", "duration": "35 min", "difficulty": "Intermediate", "relevance_score": 0.81, "reason": "GPU acceleration directly in the web browser", "url": "https://www.youtube.com/watch?v=Y9oNgLfF7ws"},
        {"resource_id": "res-017", "title": "FastAPI Authentication and Security Best Practices", "type": "Guide", "duration": "50 min", "difficulty": "Intermediate", "relevance_score": 0.83, "reason": "Secure endpoints and build robust auth pipelines", "url": "https://fastapi.tiangolo.com/tutorial/security/"},
        {"resource_id": "res-018", "title": "Quantitative Finance Interview Guide (Green Book)", "type": "Article", "duration": "120 min", "difficulty": "Advanced", "relevance_score": 0.97, "reason": "Essential for quant research and trading roles", "url": "https://www.amazon.com/Heard-Street-Quantitative-Questions-Interviews/dp/0994708319"},
        {"resource_id": "res-019", "title": "C++ for High-Frequency Trading: Lock-Free Queues", "type": "Video", "duration": "45 min", "difficulty": "Advanced", "relevance_score": 0.95, "reason": "Core low-latency C++ patterns used in HFT systems", "url": "https://www.youtube.com/watch?v=sjVGFNPchV0"},
        {"resource_id": "res-020", "title": "Options Pricing & Black-Scholes in Python", "type": "Interactive Notebook", "duration": "60 min", "difficulty": "Intermediate", "relevance_score": 0.93, "reason": "Quant finance fundamentals: derivatives pricing and hedging", "url": "https://colab.research.google.com/github/cantaro86/Financial-Models-Numerical-Methods/blob/master/1.1%20Black-Scholes%20numerical%20methods.ipynb"},
        {"resource_id": "res-021", "title": "Stochastic Calculus Primer for Quants", "type": "Guide", "duration": "90 min", "difficulty": "Advanced", "relevance_score": 0.91, "reason": "Mathematical foundation for quant research roles", "url": "https://www.math.tamu.edu/~stecher/425/Sp12/brownianMotion.pdf"},
        {"resource_id": "res-022", "title": "C++ Concurrency in Action (Chapters 1-5)", "type": "Tutorial", "duration": "80 min", "difficulty": "Advanced", "relevance_score": 0.90, "reason": "Lock-free data structures and atomic operations in C++17", "url": "https://www.manning.com/books/c-plus-plus-concurrency-in-action"},
        {"resource_id": "res-023", "title": "Algorithmic Trading with Python: Backtesting Basics", "type": "Video", "duration": "55 min", "difficulty": "Intermediate", "relevance_score": 0.88, "reason": "Build and backtest quant trading strategies", "url": "https://www.youtube.com/watch?v=xfzGZB4HhEE"},
        {"resource_id": "res-024", "title": "AWS Solutions Architect: Well-Architected Framework", "type": "Guide", "duration": "60 min", "difficulty": "Intermediate", "relevance_score": 0.90, "reason": "Core AWS design principles for cloud engineers", "url": "https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html"},
        {"resource_id": "res-025", "title": "Terraform: Infrastructure as Code Full Course", "type": "Video", "duration": "130 min", "difficulty": "Intermediate", "relevance_score": 0.88, "reason": "Provision and manage cloud infrastructure with Terraform", "url": "https://www.youtube.com/watch?v=tomUWcQ0P3k"},
        {"resource_id": "res-026", "title": "Kubernetes: From Zero to Production", "type": "Tutorial", "duration": "75 min", "difficulty": "Intermediate", "relevance_score": 0.87, "reason": "Container orchestration for scalable deployments", "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/"},
        {"resource_id": "res-027", "title": "Google Cloud Professional Data Engineer Guide", "type": "Guide", "duration": "90 min", "difficulty": "Advanced", "relevance_score": 0.84, "reason": "GCP data pipeline design and certification prep", "url": "https://cloud.google.com/learn/certification/data-engineer"},
        {"resource_id": "res-028", "title": "Pandas for Data Analysis: Complete Guide", "type": "Interactive Notebook", "duration": "45 min", "difficulty": "Beginner", "relevance_score": 0.91, "reason": "Core data wrangling and analysis library for Python", "url": "https://pandas.pydata.org/docs/getting_started/intro_tutorials/"},
        {"resource_id": "res-029", "title": "Statistics for Machine Learning (StatQuest)", "type": "Video", "duration": "40 min", "difficulty": "Beginner", "relevance_score": 0.89, "reason": "Intuitive statistics foundations for ML practitioners", "url": "https://www.youtube.com/watch?v=qBigTkBLU6g"},
        {"resource_id": "res-030", "title": "SQL for Data Analysis: Mode Analytics Tutorial", "type": "Tutorial", "duration": "50 min", "difficulty": "Beginner", "relevance_score": 0.86, "reason": "SQL querying and aggregation for data scientists", "url": "https://mode.com/sql-tutorial/"},
        {"resource_id": "res-031", "title": "OWASP Top 10 Web Application Security Risks", "type": "Guide", "duration": "40 min", "difficulty": "Intermediate", "relevance_score": 0.88, "reason": "Essential security vulnerabilities every developer must know", "url": "https://owasp.org/www-project-top-ten/"},
        {"resource_id": "res-032", "title": "React Native: Cross-Platform Mobile Development", "type": "Video", "duration": "85 min", "difficulty": "Intermediate", "relevance_score": 0.86, "reason": "Build iOS and Android apps with React Native", "url": "https://www.youtube.com/watch?v=0-S5a0eXPoc"},
        {"resource_id": "res-033", "title": "Flutter for Beginners: Complete Course", "type": "Video", "duration": "100 min", "difficulty": "Beginner", "relevance_score": 0.84, "reason": "Google's cross-platform UI framework from scratch", "url": "https://www.youtube.com/watch?v=VPvVD8t02U8"},
        {"resource_id": "res-034", "title": "System Design Interview: The Complete Guide", "type": "Article", "duration": "60 min", "difficulty": "Advanced", "relevance_score": 0.93, "reason": "Scalable system design patterns used in FAANG interviews", "url": "https://github.com/donnemartin/system-design-primer"},
        {"resource_id": "res-035", "title": "LangChain: Build Production LLM Applications", "type": "Tutorial", "duration": "55 min", "difficulty": "Intermediate", "relevance_score": 0.87, "reason": "Chains, agents, and RAG pipelines with LangChain", "url": "https://python.langchain.com/docs/tutorials/"},
        {"resource_id": "res-036", "title": "CI/CD with GitHub Actions: Complete Course", "type": "Video", "duration": "70 min", "difficulty": "Intermediate", "relevance_score": 0.85, "reason": "Automate build, test, and deploy pipelines with Actions", "url": "https://www.youtube.com/watch?v=R8_veQiYBjI"},
        {"resource_id": "res-037", "title": "Web Security: Ethical Hacking for Beginners", "type": "Video", "duration": "65 min", "difficulty": "Beginner", "relevance_score": 0.83, "reason": "Hands-on pentesting fundamentals and CTF basics", "url": "https://www.youtube.com/watch?v=3Kq1MIfTWCE"},
    ]
    
    # Rank channels and resources by keyword overlap with user profile
    kws = _keywords(identity)
    if kws:
        scored_channels = sorted(
            channel_pool,
            key=lambda c: _score(f"{c['name']} {c.get('reason', '')}", kws),
            reverse=True,
        )
        scored_resources = sorted(
            resource_pool,
            key=lambda r: _score(f"{r['title']} {r.get('reason', '')}", kws),
            reverse=True,
        )
    else:
        scored_channels = channel_pool[(seed % len(channel_pool)):] + channel_pool[:(seed % len(channel_pool))]
        scored_resources = resource_pool[(seed % len(resource_pool)):] + resource_pool[:(seed % len(resource_pool))]

    selected_channels = scored_channels[:4]
    selected_resources = scored_resources[:4]

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
        {
            "mentor_id": "mentor-ravi", "name": "Ravi Krishnamurthy",
            "role": "Quantitative Researcher @ Jane Street", "avatar": "RK",
            "expertise_areas": ["Quant Finance", "C++", "Algorithmic Trading", "Statistics"],
            "compatibility_score": 0.93,
            "match_reason": "Deep expertise in quant research, HFT systems, and C++ for low-latency trading. Ideal for students targeting quant roles.",
            "availability": "Weekends 10 AM - 12 PM IST", "teaching_style": "Green Book problems + system design deep dives",
            "years_experience": 9
        },
        {
            "mentor_id": "mentor-alex", "name": "Alex Kowalski",
            "role": "HFT Systems Engineer", "avatar": "AK",
            "expertise_areas": ["C++", "Low Latency", "Systems Programming", "Finance"],
            "compatibility_score": 0.91,
            "match_reason": "Builds matching engines and order management systems in C++. Strong fit for systems programming and quant engineering paths.",
            "availability": "Mon/Thu evenings", "teaching_style": "Code review + architecture walkthroughs",
            "years_experience": 7
        },
    ]

    # Generic action words that cause false-positive mentor matches
    _STOP_KWS = {"learn", "get", "study", "want", "need", "become", "build", "develop", "job", "internship"}

    kws = _keywords(identity) - _STOP_KWS
    if kws:
        # Weight expertise areas 3x more than match reason to avoid false positives
        def _mentor_score(m: dict) -> int:
            expertise_score = _score(" ".join(m.get("expertise_areas", [])), kws) * 3
            reason_score = _score(m.get("match_reason", ""), kws)
            return expertise_score + reason_score

        scored = sorted(
            mentor_pool,
            key=_mentor_score,
            reverse=True,
        )
        primary_idx = 0
        backup_idx = 1
        mentor_pool = scored  # type: ignore[assignment]
    else:
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


# In-memory user store pre-seeded with demo personas, merged with persisted real users
_user_store: Dict[str, Dict] = {
    "rahul": {
        "user_id": "rahul",
        "username": "rahul",
        "bio": "Systems programming and GPU enthusiast. Building custom CUDA kernels and optimizing LLM inference engines.",
        "skills": {"CUDA": 4, "C++": 4, "Rust": 3, "Systems Programming": 4, "GPU Architecture": 3},
        "tags": ["cuda", "gpu", "systems", "c++", "rust"],
        "interests": ["gpu-computing", "systems-programming", "rust"],
        "goals": ["Master CUDA optimization", "Understand hardware-level execution", "Contribute to open-source"],
        "learning_style": "Hands-on projects, deep-dive guides, reading source code",
        "skill_level": "Intermediate",
        "activity_log": [
            {"type": "message", "channel": "gpu-computing", "content": "Anyone dealt with shared memory bank conflicts during matrix multiplication?"},
            {"type": "message", "channel": "rust", "content": "Hey Aman, the ownership model can be tricky — think of it as compile-time resource management."},
        ],
        "metrics": {"contributions_percentile": 15, "beginners_helped_this_week": 6, "is_mentor_eligible": True},
        "created_at": "2026-06-20T10:00:00",
    },
    "priya": {
        "user_id": "priya",
        "username": "priya",
        "bio": "Beginner AI learner from a non-CS background. Want to understand ML and train neural networks with PyTorch.",
        "skills": {"Python": 2, "Basic Math": 1},
        "tags": ["pytorch", "machine-learning", "beginner", "ai"],
        "interests": ["pytorch-study-group", "machine-learning-basics"],
        "goals": ["Build first neural network", "Learn PyTorch", "Transition into AI engineering"],
        "learning_style": "Step-by-step tutorials, interactive notebooks, mentor guidance",
        "skill_level": "Beginner",
        "activity_log": [
            {"type": "join", "timestamp": "2026-06-25T09:00:00Z"},
            {"type": "message", "channel": "introductions", "content": "Hi everyone! I'm Priya, excited to learn AI! Where should I start with PyTorch?"},
        ],
        "metrics": {"contributions_percentile": 95, "beginners_helped_this_week": 0, "is_mentor_eligible": False},
        "created_at": "2026-06-25T09:00:00",
    },
    "organizer": {
        "user_id": "organizer",
        "username": "organizer",
        "bio": "Community operations lead for AgentField Community.",
        "skills": {"Community Management": 5, "Analytics": 4},
        "tags": ["organizer", "admin"],
        "interests": ["community-ops"],
        "goals": ["Grow community engagement", "Reduce churn", "Onboard quality mentors"],
        "learning_style": "Data-driven",
        "skill_level": "Expert",
        "activity_log": [],
        "metrics": {"contributions_percentile": 1, "beginners_helped_this_week": 0, "is_mentor_eligible": False},
        "created_at": "2026-06-01T00:00:00",
    },
}


# Merge persisted real users on startup (seed personas take lower priority)
_user_store.update(_load_persisted_users())


def get_mock_user(user_id: str) -> Optional[Dict]:
    """Get a user from the store (checks exact key first, then lowercased)."""
    return _user_store.get(user_id) or _user_store.get(user_id.lower())


def save_mock_user(user_id: str, user_data: Dict) -> None:
    """Save a user to the store and persist to disk."""
    _user_store[user_id] = user_data
    _SEED_IDS = {"rahul", "priya", "organizer"}
    _persist_users({k: v for k, v in _user_store.items() if k not in _SEED_IDS})
    logger.info(f"Saved and persisted user: {user_id}")


def list_mock_users() -> List[Dict]:
    """List all users in the store."""
    return list(_user_store.values())


# ─── Module-level pool exports for LLM prompt injection ───────────────────────

_channel_pool_raw = [
    {"channel_id": "ch-ml", "name": "Machine Learning", "reason": "ML interests and Python skills"},
    {"channel_id": "ch-cuda", "name": "GPU & Accelerators", "reason": "CUDA and GPU programming"},
    {"channel_id": "ch-systems", "name": "Systems Programming", "reason": "C++ and Linux systems expertise"},
    {"channel_id": "ch-data", "name": "Data Science & Python", "reason": "Python as primary language"},
    {"channel_id": "ch-ai-infra", "name": "AI Infrastructure", "reason": "Distributed systems and MLOps"},
    {"channel_id": "ch-react", "name": "React Frameworks", "reason": "Frontend web development"},
    {"channel_id": "ch-open-source", "name": "Open Source Contribution", "reason": "Community engagement"},
    {"channel_id": "ch-quant", "name": "Quant Finance & Trading", "reason": "Quant research and algorithmic trading"},
    {"channel_id": "ch-lowlatency", "name": "Low Latency & HFT Systems", "reason": "HFT and low-latency C++ systems"},
    {"channel_id": "ch-cpp", "name": "Modern C++ & Systems", "reason": "C++ language, STL, memory, concurrency"},
    {"channel_id": "ch-competitive", "name": "Competitive Programming", "reason": "Algorithms and contest prep"},
    {"channel_id": "ch-content", "name": "Content Creation & Video", "reason": "Video editing, storytelling, YouTube growth, and creator tools"},
    {"channel_id": "ch-creative", "name": "Creative Skills & Design", "reason": "Graphic design, photography, visual storytelling for creators"},
    {"channel_id": "ch-cooking", "name": "Food & Cooking Community", "reason": "Cooking techniques, food photography, recipe development and culinary skills"},
    {"channel_id": "ch-marketing", "name": "Digital Marketing & Growth", "reason": "Social media strategy, audience building, brand partnerships"},
    {"channel_id": "ch-freelance", "name": "Freelancing & Creative Careers", "reason": "Monetizing creative skills, client acquisition, portfolio building"},
]

_resource_pool_raw = [
    {"resource_id": "res-001", "title": "PyTorch Tensors: A Visual Guide", "reason": "ML onboarding with Python"},
    {"resource_id": "res-002", "title": "CUDA Shared Memory & Coalescing", "reason": "GPU optimization for CUDA programmers"},
    {"resource_id": "res-003", "title": "Linux Kernel Module Programming Guide", "reason": "Systems programming and OS internals"},
    {"resource_id": "res-004", "title": "NumPy Matrix Operations in Practice", "reason": "Python math and data manipulation"},
    {"resource_id": "res-005", "title": "Distributed PyTorch Training Guide", "reason": "Scaling ML models across GPUs"},
    {"resource_id": "res-006", "title": "Rust Programming for Systems Engineers", "reason": "Low-level systems safety in Rust"},
    {"resource_id": "res-007", "title": "FastAPI Complete Tutorial", "reason": "Production Python backend APIs"},
    {"resource_id": "res-008", "title": "Docker & Kubernetes: MLOps Containerization", "reason": "Container orchestration for ML"},
    {"resource_id": "res-009", "title": "Introduction to Transformers & NLP", "reason": "Language models and NLP"},
    {"resource_id": "res-010", "title": "UI/UX Design Patterns for AI Applications", "reason": "Frontend design for AI products"},
    {"resource_id": "res-011", "title": "Deep Reinforcement Learning in PyTorch", "reason": "RL agents and environments"},
    {"resource_id": "res-012", "title": "Advanced C++ Memory Management", "reason": "High-performance C++ and GPU interaction"},
    {"resource_id": "res-013", "title": "Git Workflows for Large Engineering Teams", "reason": "Collaboration and version control best practices"},
    {"resource_id": "res-014", "title": "Model Deployment with MLflow & Triton", "reason": "Serving ML models with ultra-low latency"},
    {"resource_id": "res-015", "title": "Data Visualization Best Practices with Seaborn", "reason": "Data reporting and dashboard design"},
    {"resource_id": "res-016", "title": "Introduction to GPU Programming with WebGPU", "reason": "GPU acceleration in the browser"},
    {"resource_id": "res-017", "title": "FastAPI Authentication and Security Best Practices", "reason": "Secure endpoints and auth pipelines"},
    {"resource_id": "res-018", "title": "Quantitative Finance Interview Guide (Green Book)", "reason": "Essential for quant research and trading roles"},
    {"resource_id": "res-019", "title": "C++ for High-Frequency Trading: Lock-Free Queues", "reason": "Core low-latency C++ patterns for HFT"},
    {"resource_id": "res-020", "title": "Options Pricing & Black-Scholes in Python", "reason": "Quant finance derivatives pricing"},
    {"resource_id": "res-021", "title": "Stochastic Calculus Primer for Quants", "reason": "Mathematical foundation for quant research"},
    {"resource_id": "res-022", "title": "C++ Concurrency in Action (Chapters 1-5)", "reason": "Lock-free data structures and atomics in C++17"},
    {"resource_id": "res-023", "title": "Algorithmic Trading with Python: Backtesting Basics", "reason": "Build and backtest quant trading strategies"},
    {"resource_id": "res-024", "title": "AWS Solutions Architect: Well-Architected Framework", "reason": "Core AWS design principles for cloud engineers"},
    {"resource_id": "res-025", "title": "Terraform: Infrastructure as Code Full Course", "reason": "Provision and manage cloud infrastructure with Terraform"},
    {"resource_id": "res-026", "title": "Kubernetes: From Zero to Production", "reason": "Container orchestration for scalable deployments"},
    {"resource_id": "res-027", "title": "Google Cloud Professional Data Engineer Guide", "reason": "GCP data pipeline design and certification prep"},
    {"resource_id": "res-028", "title": "Pandas for Data Analysis: Complete Guide", "reason": "Core data wrangling and analysis library for Python"},
    {"resource_id": "res-029", "title": "Statistics for Machine Learning (StatQuest)", "reason": "Intuitive statistics foundations for ML practitioners"},
    {"resource_id": "res-030", "title": "SQL for Data Analysis: Mode Analytics Tutorial", "reason": "SQL querying and aggregation for data scientists"},
    {"resource_id": "res-031", "title": "OWASP Top 10 Web Application Security Risks", "reason": "Essential security vulnerabilities every developer must know"},
    {"resource_id": "res-032", "title": "React Native: Cross-Platform Mobile Development", "reason": "Build iOS and Android apps with React Native"},
    {"resource_id": "res-033", "title": "Flutter for Beginners: Complete Course", "reason": "Google's cross-platform UI framework from scratch"},
    {"resource_id": "res-034", "title": "System Design Interview: The Complete Guide", "reason": "Scalable system design patterns for FAANG interviews"},
    {"resource_id": "res-035", "title": "LangChain: Build Production LLM Applications", "reason": "Chains, agents, and RAG pipelines with LangChain"},
    {"resource_id": "res-036", "title": "CI/CD with GitHub Actions: Complete Course", "reason": "Automate build, test, and deploy pipelines"},
    {"resource_id": "res-037", "title": "Web Security: Ethical Hacking for Beginners", "reason": "Hands-on pentesting fundamentals and CTF basics"},
]

_mentor_pool_raw = [
    {"mentor_id": "mentor-sarah", "name": "Sarah Jenkins", "role": "Principal GPU Engineer at NVIDIA", "expertise_areas": ["CUDA", "GPU Architecture", "Distributed Systems"]},
    {"mentor_id": "mentor-amit", "name": "Amit Sharma", "role": "AI Infrastructure Lead", "expertise_areas": ["PyTorch", "MLOps", "Distributed Training"]},
    {"mentor_id": "mentor-priya", "name": "Priya Nair", "role": "Senior Data Scientist", "expertise_areas": ["Python", "Data Science", "Machine Learning"]},
    {"mentor_id": "mentor-marcus", "name": "Marcus Chen", "role": "Senior Systems Developer", "expertise_areas": ["C++", "Linux Systems", "Rust"]},
    {"mentor_id": "mentor-elena", "name": "Elena Rostova", "role": "Deep Learning Researcher", "expertise_areas": ["NLP", "Transformers", "PyTorch"]},
    {"mentor_id": "mentor-david", "name": "David Miller", "role": "DevOps Architect", "expertise_areas": ["Kubernetes", "Docker", "Cloud Infra"]},
    {"mentor_id": "mentor-aisha", "name": "Aisha Rahman", "role": "MLOps Engineer", "expertise_areas": ["Model Deployment", "MLflow", "FastAPI"]},
    {"mentor_id": "mentor-yuki", "name": "Yuki Tanaka", "role": "Frontend Tech Lead", "expertise_areas": ["React", "TypeScript", "UI/UX"]},
    {"mentor_id": "mentor-clara", "name": "Clara Dupont", "role": "Product Manager AI", "expertise_areas": ["Product Strategy", "UX Research", "Agile"]},
    {"mentor_id": "mentor-james", "name": "James Wilson", "role": "Reinforcement Learning Expert", "expertise_areas": ["RL", "Robotics", "Python"]},
    {"mentor_id": "mentor-ravi", "name": "Ravi Krishnamurthy", "role": "Quantitative Researcher @ Jane Street", "expertise_areas": ["Quant Finance", "C++", "Algorithmic Trading", "Statistics"]},
    {"mentor_id": "mentor-alex", "name": "Alex Kowalski", "role": "HFT Systems Engineer", "expertise_areas": ["C++", "Low Latency", "Systems Programming", "Finance"]},
    {"mentor_id": "mentor-zara", "name": "Zara Ahmed", "role": "Full-Time Content Creator & Food Blogger", "expertise_areas": ["Video Editing", "Cooking", "YouTube Growth", "Food Content", "Social Media"]},
    {"mentor_id": "mentor-kai", "name": "Kai Nakamura", "role": "Creative Director & Video Producer", "expertise_areas": ["Video Production", "Storytelling", "Content Creation", "Brand Building", "Editing"]},
]
