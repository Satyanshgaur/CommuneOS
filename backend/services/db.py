# db.py - In-memory Relational Multi-Tenant Database Store

# Tables representing DB Entities
users_table = {}          # user_id -> User Profile Dict
resumes_table = {}        # user_id -> Parsed Resume Dict
identities_table = {}     # user_id -> Identity Profile Dict
communities_table = {
    "comm-gpu": {
        "community_id": "comm-gpu",
        "name": "GPU Systems Guild",
        "logo": "⚡",
        "description": "High performance GPU cluster engineering, CUDA kernel optimization, and systems programming."
    },
    "comm-ml": {
        "community_id": "comm-ml",
        "name": "ML Practitioners Cohort",
        "logo": "🧠",
        "description": "Deep learning research, PyTorch model deployment, MLOps, and neural architectures."
    }
}
community_members_table = {}  # user_id -> {user_id, community_id, role_id}
roles_table = {
    "role-member": {
        "role_id": "role-member",
        "name": "Member",
        "permissions": ["read:dashboard", "read:channels", "read:resources"]
    },
    "role-organizer": {
        "role_id": "role-organizer",
        "name": "Organizer",
        "permissions": ["read:dashboard", "read:channels", "read:resources", "read:organizer", "write:actions"]
    }
}

# Scoped Entities (Belong to exactly one community)
channels_table = [
    # GPU
    {"channel_id": "ch-cuda", "community_id": "comm-gpu", "name": "GPU & Accelerators"},
    {"channel_id": "ch-sysprog", "community_id": "comm-gpu", "name": "Systems Programming"},
    {"channel_id": "ch-ai-infra", "community_id": "comm-gpu", "name": "AI Infrastructure"},
    # ML
    {"channel_id": "ch-ml", "community_id": "comm-ml", "name": "Machine Learning"},
    {"channel_id": "ch-python", "community_id": "comm-ml", "name": "Data Science & Python"},
    {"channel_id": "ch-nlp", "community_id": "comm-ml", "name": "NLP & Transformers"}
]

resources_table = [
    # GPU
    {
        "resource_id": "res-cuda-mem", "community_id": "comm-gpu",
        "title": "CUDA Shared Memory & Coalescing Techniques", "type": "Article",
        "duration": "25 min", "difficulty": "Advanced", "relevance_score": 0.96,
        "reason": "Critical for low-level kernel performance optimization."
    },
    {
        "resource_id": "res-kernel-dev", "community_id": "comm-gpu",
        "title": "Linux Kernel Module Programming Guide", "type": "Guide",
        "duration": "60 min", "difficulty": "Intermediate", "relevance_score": 0.82,
        "reason": "Covers kernel memory space allocation and thread scheduling."
    },
    # ML
    {
        "resource_id": "res-torch-tensors", "community_id": "comm-ml",
        "title": "PyTorch Tensors: A Visual Guide for Beginners", "type": "Video",
        "duration": "18 min", "difficulty": "Beginner", "relevance_score": 0.94,
        "reason": "Visual explanation of matrix transformations in computation graphs."
    },
    {
        "resource_id": "res-numpy-linalg", "community_id": "comm-ml",
        "title": "NumPy Matrix Operations in Practice", "type": "Interactive Notebook",
        "duration": "30 min", "difficulty": "Beginner", "relevance_score": 0.85,
        "reason": "Numerical algebra implementations in standard Python runtimes."
    }
]

events_table = [
    # GPU
    {
        "event_id": "evt-gpu-ws", "community_id": "comm-gpu",
        "title": "GPU Memory Architectures Workshop", "time": "Today, 7:00 PM (1h 30m)",
        "type": "Workshop", "difficulty": "Advanced", "score": 95,
        "reason": "Deep dive on hardware memory hierarchy & bank conflicts."
    },
    # ML
    {
        "event_id": "evt-ml-kickoff", "community_id": "comm-ml",
        "title": "ML Study Group Weekly Sync", "time": "Tonight, 6:00 PM (1h)",
        "type": "Study Group", "difficulty": "Beginner", "score": 91,
        "reason": "Collaborative paper review of attention mechanisms."
    }
]

projects_table = [
    # GPU
    {"project_id": "proj-cuda", "community_id": "comm-gpu", "title": "Custom GEMM Kernel Optimization", "description": "Write and optimize a general matrix multiply CUDA kernel matching cuBLAS speeds."},
    # ML
    {"project_id": "proj-mnist", "community_id": "comm-ml", "title": "MNIST Classifier from Scratch", "description": "Implement forward and backward propagation in raw NumPy before transitioning to PyTorch."}
]

learning_tracks_table = {
    "comm-gpu": {
        "track_id": "track-gpu",
        "community_id": "comm-gpu",
        "roadmap_title": "GPU Systems Mastery Path",
        "total_weeks": 8,
        "daily_commitment_minutes": 75,
        "estimated_completion_date": "September 15, 2026",
        "milestones": [
            {
                "week": 1,
                "title": "CUDA Core Concepts",
                "objectives": ["Understand Grids, Blocks, Threads", "Run kernel vector addition"],
                "resources": ["res-cuda-mem"],
                "estimated_hours": 6.0
            },
            {
                "week": 2,
                "title": "Shared Memory & Coalescing",
                "objectives": ["Write a matrix transpose using shared memory", "Eliminate bank conflicts"],
                "resources": ["res-kernel-dev"],
                "estimated_hours": 8.0
            }
        ]
    },
    "comm-ml": {
        "track_id": "track-ml",
        "community_id": "comm-ml",
        "roadmap_title": "ML Foundations to Practice",
        "total_weeks": 6,
        "daily_commitment_minutes": 60,
        "estimated_completion_date": "August 30, 2026",
        "milestones": [
            {
                "week": 1,
                "title": "Tensors & Algebra",
                "objectives": ["Master matrix multiplications", "Understand auto-differentiation"],
                "resources": ["res-torch-tensors", "res-numpy-linalg"],
                "estimated_hours": 5.0
            }
        ]
    }
}

mentors_table = [
    # GPU
    {
        "mentor_id": "mentor-sarah", "community_id": "comm-gpu",
        "name": "Sarah Jenkins", "role": "Principal GPU Engineer at NVIDIA",
        "expertise_areas": ["CUDA", "GPU Architecture", "Distributed Systems"],
        "compatibility_score": 0.94,
        "match_reason": "Expert in CUDA Memory optimization & Shared Memory architectures. Has 8+ years experience."
    },
    # ML
    {
        "mentor_id": "mentor-amit", "community_id": "comm-ml",
        "name": "Amit Sharma", "role": "AI Infrastructure Lead",
        "expertise_areas": ["PyTorch", "MLOps", "Distributed Training"],
        "compatibility_score": 0.86,
        "match_reason": "Works on distributed training optimization. Good match for ML infrastructure goals."
    }
]

# Organizer suggested actions (dynamic generation scoped by community)
actions_table = [
    # GPU
    {
        "action_id": "act-ama", "community_id": "comm-gpu",
        "title": "Schedule GPU Memory AMA Session",
        "description": "Unanswered GPU/CUDA questions flagged by Identity Agent in systems threads this week.",
        "expected_impact": "Would answer query bottlenecks for GPU learners.",
        "assignee": "Sarah Jenkins", "completed": False
    },
    # ML
    {
        "action_id": "act-faq", "community_id": "comm-ml",
        "title": "Generate PyTorch Tensor FAQ Doc",
        "description": "Learning Agent detected 8 beginner users repeating Tensor AutoGrad setup queries.",
        "expected_impact": "Reduces duplicate community support requests by estimated 25%.",
        "assignee": "Amit Sharma", "completed": False
    }
]

# Query Scoping Helpers
def get_channels_by_community(community_id: str):
    return [c for c in channels_table if c["community_id"] == community_id]

def get_resources_by_community(community_id: str):
    return [r for r in resources_table if r["community_id"] == community_id]

def get_events_by_community(community_id: str):
    return [e for e in events_table if e["community_id"] == community_id]

def get_projects_by_community(community_id: str):
    return [p for p in projects_table if p["community_id"] == community_id]

def get_mentors_by_community(community_id: str):
    return [m for m in mentors_table if m["community_id"] == community_id]

def get_actions_by_community(community_id: str):
    return [a for a in actions_table if a["community_id"] == community_id]
