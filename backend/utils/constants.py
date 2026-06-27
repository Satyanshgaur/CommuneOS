"""
CommuneOS Application Constants
Central repository for all fixed values used across the system.
"""

# ─── Skill Proficiency Levels ─────────────────────────────────────────────────
SKILL_LEVELS = ["Beginner", "Intermediate", "Advanced", "Expert"]
SKILL_LEVEL_MAP = {
    1: "Beginner",
    2: "Beginner",
    3: "Intermediate",
    4: "Advanced",
    5: "Expert"
}

# ─── Learning Styles ──────────────────────────────────────────────────────────
LEARNING_STYLES = ["visual", "auditory", "kinesthetic", "reading"]

# ─── Agent Names ──────────────────────────────────────────────────────────────
AGENT_IDENTITY = "identity_agent"
AGENT_DISCOVERY = "discovery_agent"
AGENT_LEARNING = "learning_agent"
AGENT_MENTOR = "mentor_agent"
AGENT_HEALTH = "health_agent"
AGENT_ORGANIZER = "organizer_agent"

ALL_AGENTS = [
    AGENT_IDENTITY,
    AGENT_DISCOVERY,
    AGENT_LEARNING,
    AGENT_MENTOR,
    AGENT_HEALTH,
    AGENT_ORGANIZER,
]

# ─── Community Channels ───────────────────────────────────────────────────────
COMMUNITY_CHANNELS = [
    {"id": "ch-cuda", "name": "GPU & Accelerators", "topics": ["cuda", "gpu", "accelerators", "nvidia", "opencl"], "difficulty": "Advanced"},
    {"id": "ch-ml", "name": "Machine Learning", "topics": ["ml", "machine learning", "deep learning", "pytorch", "tensorflow"], "difficulty": "Intermediate"},
    {"id": "ch-systems", "name": "Systems Programming", "topics": ["systems", "c++", "rust", "linux", "kernels", "os"], "difficulty": "Advanced"},
    {"id": "ch-ai-infra", "name": "AI Infrastructure", "topics": ["ai infrastructure", "distributed", "mlops", "deployment"], "difficulty": "Advanced"},
    {"id": "ch-data", "name": "Data Science & Python", "topics": ["data science", "python", "pandas", "numpy", "visualization"], "difficulty": "Beginner"},
    {"id": "ch-web3", "name": "Web3 & Blockchain", "topics": ["web3", "blockchain", "solidity", "ethereum", "defi"], "difficulty": "Intermediate"},
    {"id": "ch-mobile", "name": "Mobile Design", "topics": ["mobile", "ios", "android", "flutter", "react native"], "difficulty": "Beginner"},
    {"id": "ch-react", "name": "React Frameworks", "topics": ["react", "nextjs", "frontend", "javascript", "typescript"], "difficulty": "Intermediate"},
    {"id": "ch-open-source", "name": "Open Source Contribution", "topics": ["open source", "github", "contributions", "oss"], "difficulty": "Intermediate"},
    {"id": "ch-research", "name": "Research & Papers", "topics": ["research", "papers", "arxiv", "academics"], "difficulty": "Expert"},
]

# ─── Churn Risk Thresholds (days inactive) ───────────────────────────────────
CHURN_HIGH_RISK_DAYS = 14
CHURN_MEDIUM_RISK_DAYS = 7
CHURN_LOW_RISK_DAYS = 3

# ─── Action Priority Levels ───────────────────────────────────────────────────
PRIORITY_CRITICAL = "critical"       # 0-24 hours
PRIORITY_HIGH = "high"               # 1-3 days
PRIORITY_MEDIUM = "medium"           # 1-2 weeks
PRIORITY_LOW = "low"                 # Monthly

# ─── Pipeline Timeouts ────────────────────────────────────────────────────────
PIPELINE_TOTAL_TIMEOUT = 10          # seconds — max for entire pipeline
PIPELINE_MEMBER_TIMEOUT = 8          # seconds — member personalization
PIPELINE_HEALTH_TIMEOUT = 6          # seconds — community health

# ─── Cache Key Templates ──────────────────────────────────────────────────────
CACHE_KEY_AGENT = "{agent}:{user_id}"
CACHE_KEY_LLM = "llm:{prompt_hash}"
CACHE_KEY_COMMUNITY = "community:{metric_type}"
CACHE_KEY_USER = "user:{user_id}"
