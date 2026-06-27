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
    },
    "comm-web": {
        "community_id": "comm-web",
        "name": "Web & Frontend Engineering",
        "logo": "🎨",
        "description": "Modern frontend development, React, Next.js, CSS architecture, performance, and responsive interfaces."
    },
    "comm-sys": {
        "community_id": "comm-sys",
        "name": "Rust Systems Programming",
        "logo": "🦀",
        "description": "Safe systems software, Rust concurrency models, low-level memory control, and network protocols."
    },
    "comm-data": {
        "community_id": "comm-data",
        "name": "Data Engineering & Analytics",
        "logo": "📊",
        "description": "Data lakehouses, large-scale pipelines, Apache Spark, DBT, SQL modeling, and ETL optimization."
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
    {"channel_id": "ch-nlp", "community_id": "comm-ml", "name": "NLP & Transformers"},
    # Web
    {"channel_id": "ch-react", "community_id": "comm-web", "name": "React & Frameworks"},
    {"channel_id": "ch-css", "community_id": "comm-web", "name": "CSS & Design Systems"},
    {"channel_id": "ch-web-perf", "community_id": "comm-web", "name": "Web Performance"},
    # Rust
    {"channel_id": "ch-rust-basics", "community_id": "comm-sys", "name": "Rust Foundations"},
    {"channel_id": "ch-rust-concurrency", "community_id": "comm-sys", "name": "Concurrency & Safety"},
    {"channel_id": "ch-rust-tokio", "community_id": "comm-sys", "name": "Asynchronous & I/O"},
    # Data
    {"channel_id": "ch-spark", "community_id": "comm-data", "name": "Spark & Big Data"},
    {"channel_id": "ch-dbt", "community_id": "comm-data", "name": "Data Modeling & DBT"},
    {"channel_id": "ch-pipelines", "community_id": "comm-data", "name": "ETL Pipelines"}
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
    },
    # Web
    {
        "resource_id": "res-nextjs-app", "community_id": "comm-web",
        "title": "Next.js 14 App Router Deep Dive", "type": "Video",
        "duration": "45 min", "difficulty": "Intermediate", "relevance_score": 0.95,
        "reason": "Explains server components and layout routing structures."
    },
    {
        "resource_id": "res-css-grid", "community_id": "comm-web",
        "title": "Mastering CSS Grid & Subgrid Layouts", "type": "Interactive Guide",
        "duration": "30 min", "difficulty": "Beginner", "relevance_score": 0.88,
        "reason": "Hands-on tutorials for modern grid alignments."
    },
    # Rust
    {
        "resource_id": "res-rust-borrow", "community_id": "comm-sys",
        "title": "The Borrow Checker Guide", "type": "Article",
        "duration": "20 min", "difficulty": "Intermediate", "relevance_score": 0.97,
        "reason": "Deep explanation of lifetime syntax and stack allocation rules."
    },
    # Data
    {
        "resource_id": "res-spark-tuning", "community_id": "comm-data",
        "title": "Spark Memory Tuning & Partitioning Guide", "type": "Article",
        "duration": "35 min", "difficulty": "Advanced", "relevance_score": 0.92,
        "reason": "Key tips on executor allocation and garbage collection patterns."
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
    },
    # Web
    {
        "event_id": "evt-nextjs-qa", "community_id": "comm-web",
        "title": "Next.js App Router Q&A", "time": "Tomorrow, 5:00 PM (1h)",
        "type": "Q&A Session", "difficulty": "Intermediate", "score": 93,
        "reason": "Interactive developer discussion on server actions caching."
    },
    # Rust
    {
        "event_id": "evt-rust-unsafe", "community_id": "comm-sys",
        "title": "Demystifying Unsafe Rust", "time": "Tonight, 8:00 PM (1h 30m)",
        "type": "Workshop", "difficulty": "Advanced", "score": 96,
        "reason": "Understanding boundaries, raw pointers, and undefined behavior."
    },
    # Data
    {
        "event_id": "evt-data-dbt", "community_id": "comm-data",
        "title": "DBT Data Modeling Round Table", "time": "Friday, 4:00 PM (1h)",
        "type": "Discussion", "difficulty": "Intermediate", "score": 89,
        "reason": "Best practices for star schema modularization and lineage."
    }
]

projects_table = [
    # GPU
    {"project_id": "proj-cuda", "community_id": "comm-gpu", "title": "Custom GEMM Kernel Optimization", "description": "Write and optimize a general matrix multiply CUDA kernel matching cuBLAS speeds."},
    # ML
    {"project_id": "proj-mnist", "community_id": "comm-ml", "title": "MNIST Classifier from Scratch", "description": "Implement forward and backward propagation in raw NumPy before transitioning to PyTorch."},
    # Web
    {"project_id": "proj-react-dash", "community_id": "comm-web", "title": "Interactive Analytics Dashboard", "description": "Build a responsive analytics dashboard with chart visualization using Next.js."},
    # Rust
    {"project_id": "proj-rust-tcp", "community_id": "comm-sys", "title": "Multi-threaded TCP Server", "description": "Write a multi-threaded web server in raw Rust using standard library threads."},
    # Data
    {"project_id": "proj-data-pipeline", "community_id": "comm-data", "title": "E-Commerce Batch Pipeline", "description": "Build a pipeline processing transaction logs with Spark and loading into a DBT warehouse."}
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
    },
    "comm-web": {
        "track_id": "track-web",
        "community_id": "comm-web",
        "roadmap_title": "Frontend Engineering Mastery Path",
        "total_weeks": 8,
        "daily_commitment_minutes": 60,
        "estimated_completion_date": "September 30, 2026",
        "milestones": [
            {
                "week": 1,
                "title": "Modern DOM & React Essentials",
                "objectives": ["Understand React virtual DOM", "Build components with hooks"],
                "resources": ["res-css-grid"],
                "estimated_hours": 5.0
            },
            {
                "week": 2,
                "title": "Next.js App Router Architecture",
                "objectives": ["Implement nested layouts", "Use server components"],
                "resources": ["res-nextjs-app"],
                "estimated_hours": 7.0
            }
        ]
    },
    "comm-sys": {
        "track_id": "track-sys",
        "community_id": "comm-sys",
        "roadmap_title": "Rust Systems Programming Path",
        "total_weeks": 10,
        "daily_commitment_minutes": 90,
        "estimated_completion_date": "October 15, 2026",
        "milestones": [
            {
                "week": 1,
                "title": "Ownership, Lifetimes, Borrowing",
                "objectives": ["Understand borrow rules", "Write safe lifetime annotations"],
                "resources": ["res-rust-borrow"],
                "estimated_hours": 8.0
            }
        ]
    },
    "comm-data": {
        "track_id": "track-data",
        "community_id": "comm-data",
        "roadmap_title": "Scalable Data Platform Path",
        "total_weeks": 8,
        "daily_commitment_minutes": 75,
        "estimated_completion_date": "October 01, 2026",
        "milestones": [
            {
                "week": 1,
                "title": "Distributed Big Data Processing",
                "objectives": ["Understand map-reduce concept", "Optimize Spark partitions"],
                "resources": ["res-spark-tuning"],
                "estimated_hours": 6.0
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
    },
    # Web
    {
        "mentor_id": "mentor-elena", "community_id": "comm-web",
        "name": "Elena Rostova", "role": "Principal UX Architect at Vercel",
        "expertise_areas": ["React", "CSS", "Design Systems", "Web Performance"],
        "compatibility_score": 0.95,
        "match_reason": "Vercel core developer with deep insight into component rendering and layouts."
    },
    # Rust
    {
        "mentor_id": "mentor-karl", "community_id": "comm-sys",
        "name": "Karl Schmidt", "role": "Principal Systems Engineer",
        "expertise_areas": ["Rust", "Systems Programming", "Concurrency", "Linux Kernels"],
        "compatibility_score": 0.96,
        "match_reason": "Contributor to tokio runtime. Perfect match for asynchronous Rust."
    },
    # Data
    {
        "mentor_id": "mentor-sanjay", "community_id": "comm-data",
        "name": "Sanjay Patel", "role": "Lead Data Architect",
        "expertise_areas": ["Apache Spark", "DBT", "SQL Modeling", "ETL"],
        "compatibility_score": 0.91,
        "match_reason": "Expert in warehouse scaling and star schemas."
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
    },
    # Web
    {
        "action_id": "act-web-qa", "community_id": "comm-web",
        "title": "Set up React Server Components FAQ",
        "description": "A group of Web members reported struggles with App Router layout render loops.",
        "expected_impact": "Reduces layout nesting configuration errors.",
        "assignee": "Elena Rostova", "completed": False
    },
    # Rust
    {
        "action_id": "act-rust-safety", "community_id": "comm-sys",
        "title": "Schedule Borrow Checker Live Review",
        "description": "Systems learners requested a walkthrough of double-mutable reference errors.",
        "expected_impact": "Helps clarify borrow lifetime restrictions.",
        "assignee": "Karl Schmidt", "completed": False
    },
    # Data
    {
        "action_id": "act-data-tuning", "community_id": "comm-data",
        "title": "Organize Spark Memory Profiling Session",
        "description": "5 members flagged out-of-memory errors on transaction dataset joins.",
        "expected_impact": "Resolves executor partition allocation bottlenecks.",
        "assignee": "Sanjay Patel", "completed": False
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


# ─── Sprint 3 Tables ───────────────────────────────────────────────────────────
recommendations_table = {}     # user_id -> Recommendations Dict
learning_roadmaps_table = {}   # user_id -> Learning Roadmap Dict
mentor_matches_table = {}      # user_id -> Mentor Matches Dict
mentor_requests_table = []     # List of Mentor Requests: {request_id, user_id, mentor_id, status, requested_at}
pipeline_hashes = {}           # user_id -> hash of user profile & resources state

# ─── Sprint 5 Documents ───────────────────────────────────────────────────────
documents_table = {}           # doc_id -> Document Metadata Dict
documents_storage = {}         # doc_id -> bytes (file content)


