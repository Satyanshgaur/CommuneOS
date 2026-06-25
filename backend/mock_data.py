# backend/mock_data.py

MEMBERS = {
    "rahul": {
        "id": "rahul",
        "name": "Rahul",
        "bio": "Systems programming and GPU enthusiast. Building custom CUDA kernels and optimizing LLM inference engines. Love low-level stuff.",
        "skills": ["CUDA", "C++", "Rust", "Systems Programming", "GPU Architecture"],
        "skill_level": "Intermediate",
        "goals": "Master CUDA optimization, understand hardware-level execution, contribute to open-source systems libraries.",
        "learning_style": "Hands-on projects, deep-dive guides, reading source code.",
        "activity_log": [
            {"type": "message", "channel": "gpu-computing", "content": "Has anyone dealt with shared memory bank conflicts when doing matrix multiplication? I am seeing a 2x slowdown and suspect my layout.", "timestamp": "2026-06-25T10:00:00Z"},
            {"type": "message", "channel": "rust", "content": "Hey Aman, the ownership model can be tricky. Think of it as compile-time resource management. I wrote a small guide on lifetimes here, check it out.", "timestamp": "2026-06-24T15:30:00Z"},
            {"type": "reaction", "channel": "systems-programming", "target": "Sarah's post about memory ordering", "timestamp": "2026-06-25T11:15:00Z"}
        ],
        "metrics": {
            "contributions_percentile": 15,
            "beginners_helped_this_week": 6,
            "is_mentor_eligible": True
        }
    },
    "priya": {
        "id": "priya",
        "name": "Priya",
        "bio": "Beginner AI learner. Coming from a non-CS background. Want to understand machine learning concepts and how to train simple neural networks using PyTorch.",
        "skills": ["Python", "Basic Math"],
        "skill_level": "Beginner",
        "goals": "Build my first neural network, learn PyTorch, transition into an AI engineering role.",
        "learning_style": "Step-by-step tutorials, interactive notebooks, mentor guidance.",
        "activity_log": [
            {"type": "join", "timestamp": "2026-06-25T09:00:00Z"},
            {"type": "message", "channel": "introductions", "content": "Hi everyone! I'm Priya, excited to learn AI! Where should I start with PyTorch? I have some basic python knowledge but no CS background.", "timestamp": "2026-06-25T09:05:00Z"}
        ],
        "metrics": {
            "contributions_percentile": 95, # low percentile meaning newcomer
            "beginners_helped_this_week": 0,
            "is_mentor_eligible": False
        }
    },
    "sarah": {
        "id": "sarah",
        "name": "Sarah",
        "bio": "Senior CUDA Engineer @ Nvidia. Love teaching systems programming, GPU performance engineering, and parallel algorithms.",
        "skills": ["CUDA", "GPU Performance", "C++", "Parallel Computing", "Systems Programming"],
        "skill_level": "Expert",
        "goals": "Mentor the next generation of systems engineers, organize GPU AMA sessions.",
        "learning_style": "Writing code, technical specifications.",
        "activity_log": [
            {"type": "message", "channel": "gpu-computing", "content": "Will be hosting a GPU AMA this Friday! Bring all your architecture questions, memory alignment issues, and CUDA kernel optimization queries.", "timestamp": "2026-06-25T08:00:00Z"}
        ],
        "metrics": {
            "contributions_percentile": 2,
            "beginners_helped_this_week": 14,
            "is_mentor_eligible": True,
            "is_mentor": True
        }
    },
    "elena": {
        "id": "elena",
        "name": "Elena",
        "bio": "Machine Learning Researcher. Specializes in LLM fine-tuning and model evaluation.",
        "skills": ["PyTorch", "LLM", "Python", "Deep Learning", "Transformers"],
        "skill_level": "Expert",
        "goals": "Help beginners understand neural networks, publish papers on model compression.",
        "learning_style": "Mathematical derivations, code implementations.",
        "activity_log": [
            {"type": "message", "channel": "pytorch-study-group", "content": "I shared a colab notebook covering backpropagation visualisations. Check out the resources section.", "timestamp": "2026-06-23T12:00:00Z"}
        ],
        "metrics": {
            "contributions_percentile": 5,
            "beginners_helped_this_week": 8,
            "is_mentor_eligible": True,
            "is_mentor": True
        }
    },
    "aman": {
        "id": "aman",
        "name": "Aman",
        "bio": "CS undergraduate student. Interested in systems programming and Rust, but struggling with lifetimes and pointers.",
        "skills": ["Rust", "C"],
        "skill_level": "Beginner",
        "goals": "Learn Rust and build a CLI tool.",
        "learning_style": "Books, small exercises.",
        "activity_log": [
            {"type": "message", "channel": "rust", "content": "Can someone explain why the compiler is complaining about this reference escaping here? I am lost with lifetimes.", "timestamp": "2026-06-24T14:00:00Z"}
        ],
        "metrics": {
            "contributions_percentile": 80,
            "beginners_helped_this_week": 0,
            "is_mentor_eligible": False
        }
    },
    "vikram": {
        "id": "vikram",
        "name": "Vikram",
        "bio": "Machine Learning engineer. Interested in PyTorch optimization and deploying models.",
        "skills": ["PyTorch", "Docker", "Python"],
        "skill_level": "Intermediate",
        "goals": "Optimize model serving on edge devices.",
        "learning_style": "Benchmarks, blog posts.",
        "activity_log": [],
        "metrics": {
            "contributions_percentile": 50,
            "beginners_helped_this_week": 0,
            "is_mentor_eligible": False,
            "last_active": "2026-06-04T10:00:00Z" # 21 days inactive
        }
    }
}

COMMUNITIES = [
    {"id": "systems-programming", "name": "Systems Programming", "category": "Tech", "description": "Low-level coding, OS design, assembly, compilers, and systems architecture."},
    {"id": "gpu-computing", "name": "GPU Computing", "category": "Tech", "description": "CUDA, OpenCL, parallel computing, shaders, and hardware acceleration."},
    {"id": "ai-infrastructure", "name": "AI Infrastructure", "category": "Tech", "description": "Serving, hardware optimization, distributed training pipelines, and MLOps."},
    {"id": "pytorch-study-group", "name": "PyTorch Study Group", "category": "Tech", "description": "Weekly study groups for building and training neural networks using PyTorch."},
    {"id": "machine-learning-basics", "name": "Machine Learning Basics", "category": "Tech", "description": "Foundational math, linear algebra, and entry-level ML algorithms."},
    {"id": "anime", "name": "Anime", "category": "Social", "description": "Discussing your favorite anime shows, manga, and conventions."},
    {"id": "football", "name": "Football", "category": "Social", "description": "Match threads, Premier League discussions, and tactical analysis."},
    {"id": "web3", "name": "Web3", "category": "Social/Tech", "description": "Blockchains, smart contracts, and decentralized protocols."}
]

RESOURCES = [
    {"id": "cuda-optimization", "name": "CUDA Optimization Guide", "category": "GPU/Systems", "url": "https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html", "description": "Official handbook for optimizing CUDA grid layouts, memory coalescing, and instruction throughput."},
    {"id": "rust-ownership", "name": "Rust Ownership Cheatsheet", "category": "Systems", "url": "https://rust-lang.github.io/book/ch04-00-understanding-ownership.html", "description": "A quick visual reference for understanding owners, references, borrowing, and lifetime mechanics."},
    {"id": "gpu-performance", "name": "GPU Performance Handbook", "category": "GPU/Systems", "url": "https://github.com/hgpu/handbook", "description": "An exhaustive resource on memory hierarchies, instruction latencies, and profiling micro-architectures."},
    {"id": "intro-pytorch", "name": "Intro to PyTorch Notebooks", "category": "AI/ML", "url": "https://pytorch.org/tutorials/beginner/basics/intro.html", "description": "Hands-on Jupyter notebooks detailing Tensors, Datasets, autograd, and training loops step-by-step."},
    {"id": "nn-from-scratch", "name": "Neural Networks from Scratch (Python)", "category": "AI/ML", "url": "https://nnfs.io", "description": "Build, feedforward, backpropagate, and train fully connected neural nets in raw Python without external libraries."},
    {"id": "deep-learning-ch5", "name": "Deep Learning Book Chapter 5", "category": "AI/ML", "url": "https://www.deeplearningbook.org/contents/ml.html", "description": "A mathematical deep dive into machine learning foundations: loss functions, capacity, bias-variance trade-offs."}
]

EVENTS = [
    {"id": "gpu-ama", "name": "GPU AMA with Sarah", "time": "Friday at 5:00 PM UTC", "description": "Open Q&A session with Sarah (Senior CUDA Engineer) on hardware profiling, tensor cores, and kernel debugging."},
    {"id": "rust-workshop", "name": "Rust Lifetimes & Ownership Workshop", "time": "Saturday at 2:00 PM UTC", "description": "Interactive live coding lab addressing common lifetime errors, smart pointers, and borrow checker fights."},
    {"id": "ai-systems-meetup", "name": "AI Systems & Inference Meetup", "time": "Wednesday at 6:30 PM UTC", "description": "Technical presentations detailing high-performance inference setups, vLLM optimization, and low-latency deployments."},
    {"id": "pytorch-basics-101", "name": "PyTorch 101: Build Your First Neural Network", "time": "Thursday at 4:00 PM UTC", "description": "Hands-on session for beginners. We'll build an MNIST digit classifier from scratch using PyTorch nn.Module."},
    {"id": "ml-basics-study", "name": "ML Basics Study Session", "time": "Monday at 3:00 PM UTC", "description": "Peer study group reviewing loss functions, gradient descent, and basic optimization math."}
]
