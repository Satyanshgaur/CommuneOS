// app.js - Ventriloc / AgentField.ai Hardcoded Frontend Logic

// 1. Initial Hardcoded Users Data
const hardcodedUsers = {
  "rahul": {
    id: "rahul",
    name: "Rahul",
    avatar: "R",
    role: "member",
    skill_level: "Intermediate",
    headline: "Welcome back, Rahul 👋",
    subtext: "Your intermediate CUDA tracks are heating up. Today you have 2 key workshops aligning with your memory architecture objectives.",
    verified_skills: [
      { name: "CUDA", level: 3 },
      { name: "C++", level: 4 },
      { name: "Linux Systems", level: 3 }
    ],
    goals: ["GPU Optimization", "Kernel Development", "ML Infrastructure"],
    learning_paths: [
      { name: "CUDA Optimization Roadmap", progress: 70, completed: 7, total: 10, next_milestone: "Milestone 8: CUDA Shared Memory Coalescing" }
    ],
    interests: ["Systems Programming", "GPU Architecture", "AI Infrastructure"],
    recommended_people: [
      { name: "Sarah Jenkins", role: "Principal GPU Engineer at Nvidia", match: 94, avatar: "SJ", reason: "Expert in CUDA Memory optimization & Shared Memory architectures. Has 5+ years experience and mentored 12+ developers." },
      { name: "Amit Sharma", role: "AI Infra Lead", match: 86, avatar: "AS", reason: "Works on distributed PyTorch engines. Good match for ML infrastructure goals." }
    ],
    communities: {
      show: ["Systems Programming", "GPU & Accelerators", "AI Infrastructure"],
      hide: ["Web3 & Blockchain", "Mobile Design", "React Frameworks"]
    },
    resources: [
      { id: "res-cuda-mem", title: "CUDA Shared Memory & Coalescing Techniques", type: "Article", duration: "25 min", difficulty: "Advanced", score: 96, reasoning: "Matches CUDA learning path (skill gap: memory coalescing) and GPU Systems Workshop is tonight." },
      { id: "res-kernel-dev", title: "Linux Kernel Module Programming Guide", type: "Guide", duration: "60 min", difficulty: "Intermediate", score: 82, reasoning: "Aligns with your kernel development interest & recent activity on systems threads." }
    ],
    events: [
      { id: "evt-gpu-ws", title: "GPU Memory Architectures Workshop", time: "Today, 7:00 PM (1h 30m)", type: "Workshop", difficulty: "Advanced", score: 95, reasoning: "Aligns with CUDA roadmap. Led by Sarah Jenkins. 28/30 registered." },
      { id: "evt-ama-rust", title: "Rust FFI & C++ Interoperability AMA", time: "Tomorrow, 5:30 PM (1h)", type: "AMA", difficulty: "Intermediate", score: 79, reasoning: "High overlap with your C++ background and growing systems interest." }
    ],
    insights: [
      { message: "You're in the top 12% active learners in Systems Programming this week.", type: "momentum" },
      { message: "Sarah Jenkins has available mentorship spots matching your timezone.", type: "match" }
    ]
  },
  "priya": {
    id: "priya",
    name: "Priya",
    avatar: "P",
    role: "member",
    skill_level: "Beginner",
    headline: "Step by step, Priya 🚀",
    subtext: "Welcome! Your journey into Machine Learning has started. Below is your AI-curated introduction path, matching your mathematics background.",
    verified_skills: [
      { name: "Python", level: 2 },
      { name: "Linear Algebra", level: 3 }
    ],
    goals: ["Machine Learning Fundamentals", "PyTorch Mastery", "Data Visualisation"],
    learning_paths: [
      { name: "PyTorch Introduction Path", progress: 20, completed: 2, total: 10, next_milestone: "Milestone 3: AutoGrad & Computation Graphs" }
    ],
    interests: ["Machine Learning", "Data Science", "Python Programming"],
    recommended_people: [
      { name: "Amit Sharma", role: "AI Infra Lead", match: 92, avatar: "AS", reason: "Excellent mentor for PyTorch beginners. High rating in explanation clarity." },
      { name: "Rahul", role: "Intermediate Systems Dev", match: 74, avatar: "R", reason: "Peer learner. Can assist with setting up CUDA runtimes on local Linux systems." }
    ],
    communities: {
      show: ["Machine Learning", "Data Science & Python"],
      hide: ["Systems Programming", "GPU & Accelerators", "Web3 & Blockchain", "Mobile Design"]
    },
    resources: [
      { id: "res-torch-tensors", title: "PyTorch Tensors: A Visual Guide for Beginners", type: "Video", duration: "18 min", difficulty: "Beginner", score: 94, reasoning: "Directly maps to PyTorch milestone 3 (Autograd basics) and matches beginner skill level." },
      { id: "res-numpy-linalg", title: "NumPy Matrix Operations in Practice", type: "Interactive Notebook", duration: "30 min", difficulty: "Beginner", score: 85, reasoning: "Bridges your linear algebra skills with Python libraries. 94% peer satisfaction." }
    ],
    events: [
      { id: "evt-ml-kickoff", title: "ML Study Group Weekly Sync", time: "Tonight, 6:00 PM (1h)", type: "Study Group", difficulty: "Beginner", score: 91, reasoning: "Highly recommended for peer support. 4 members from your cohort are attending." },
      { id: "evt-pytorch-live", title: "PyTorch Live Coding Session", time: "Friday, 4:00 PM (1h 30m)", type: "Webinar", difficulty: "Beginner", score: 88, reasoning: "Aligns with your PyTorch Introduction Roadmap. Code walkthroughs step-by-step." }
    ],
    insights: [
      { message: "You completed 2 Python resources this week. Keep up the streak!", type: "momentum" },
      { message: "ML community has 3 new introductory resources matching your roadmap.", type: "new" }
    ]
  },
  "sarah": {
    id: "sarah",
    name: "Sarah",
    avatar: "S",
    role: "member",
    skill_level: "Expert",
    headline: "Expert Space, Sarah ⚡",
    subtext: "You are currently guiding 12 community learners. Your systems optimization posts received high engagement this week.",
    verified_skills: [
      { name: "CUDA", level: 5 },
      { name: "Distributed Clusters", level: 5 },
      { name: "Linux Kernels", level: 4 }
    ],
    goals: ["Mentoring Community Devs", "Designing Distributed GPU Runtimes", "Writing Advanced Papers"],
    learning_paths: [
      { name: "Distributed GPU Systems Research", progress: 90, completed: 9, total: 10, next_milestone: "Milestone 10: Multi-Node NCCL Tuning" }
    ],
    interests: ["Distributed Systems", "GPU Infrastructure", "Open Source Contribution"],
    recommended_people: [
      { name: "Rahul", role: "Intermediate Systems Dev", match: 95, avatar: "R", reason: "Ideal mentee. Looking for CUDA shared memory guidance. Strong background in C++." },
      { name: "Emily Rogers", role: "Community Organizer", match: 88, avatar: "ER", reason: "Requested your guidance for setting up the GPU AMA cluster next month." }
    ],
    communities: {
      show: ["Systems Programming", "GPU & Accelerators", "AI Infrastructure", "Distributed Systems"],
      hide: ["Web3 & Blockchain", "Mobile Design"]
    },
    resources: [
      { id: "res-nccl-tuning", title: "Multi-GPU Communication: Optimizing NCCL Backends", type: "Research Paper", duration: "45 min", difficulty: "Expert", score: 98, reasoning: "Matches your research roadmap milestone 10 (NCCL tuning) and distributed systems focus." },
      { id: "res-cuda-advanced", title: "CUDA 12.4 Pipeline Registers & Asynchronous Copies", type: "API Doc", duration: "20 min", difficulty: "Expert", score: 90, reasoning: "New documentation released. Aligns with your GPU hardware architecture insights." }
    ],
    events: [
      { id: "evt-gpu-ws", title: "GPU Memory Architectures Workshop", time: "Tonight, 7:00 PM (1h 30m)", type: "Workshop (Speaker)", difficulty: "Expert", score: 99, reasoning: "You are the hosting speaker for this event. 28 members are attending." },
      { id: "evt-ama-rust", title: "Rust FFI & C++ Interoperability AMA", time: "Tomorrow, 5:30 PM (1h)", type: "AMA", difficulty: "Advanced", score: 85, reasoning: "Relevant for designing native bindings for your distributed cluster framework." }
    ],
    insights: [
      { message: "Your GPU Workshop is fully booked. Outstanding work!", type: "success" },
      { message: "Rahul is waiting for your response on a CUDA shared memory query.", type: "action" }
    ]
  },
  "alex": {
    id: "alex",
    name: "Alex",
    avatar: "A",
    role: "member",
    skill_level: "Intermediate",
    headline: "Welcome back, Alex 🎨",
    subtext: "Blending layout code with design principles. Your React design systems track is halfway complete.",
    verified_skills: [
      { name: "Figma", level: 5 },
      { name: "CSS Design Systems", level: 4 },
      { name: "HTML/JS", level: 3 }
    ],
    goals: ["Mastering React Componentry", "AI Layout Orchestration", "Design Tokens Automation"],
    learning_paths: [
      { name: "React Starter for Designers", progress: 50, completed: 5, total: 10, next_milestone: "Milestone 6: Styled Components & Prop Mapping" }
    ],
    interests: ["Frontend Dev", "Design Systems", "UI/UX Architecture"],
    recommended_people: [
      { name: "Emily Rogers", role: "Community Organizer", match: 90, avatar: "ER", reason: "Needs assistance with community branding templates. Aligns with your Design Tokens goals." },
      { name: "Amit Sharma", role: "AI Infra Lead", match: 72, avatar: "AS", reason: "Potential collaboration on building dashboard visual templates." }
    ],
    communities: {
      show: ["Frontend Development", "Design Systems & UI UX"],
      hide: ["Systems Programming", "GPU & Accelerators", "Distributed Systems"]
    },
    resources: [
      { id: "res-react-design", title: "React Component Archetypes for Designers", type: "Video Course", duration: "40 min", difficulty: "Intermediate", score: 92, reasoning: "Directly targets milestone 6 of your React path. Highly rated for Figma-to-React converters." },
      { id: "res-tokens", title: "Figma Variables & CSS Custom Properties Mapping", type: "Guide", duration: "15 min", difficulty: "Intermediate", score: 89, reasoning: "Fits your design tokens automation goal. Reviews design engineering best practices." }
    ],
    events: [
      { id: "evt-design-token", title: "Design Systems & Token Architecture Panel", time: "Saturday, 2:00 PM (1h 30m)", type: "Panel", difficulty: "Intermediate", score: 94, reasoning: "Matches your design system focus. Guest speakers from Figma and Vercel. 42 registered." },
      { id: "evt-ml-kickoff", title: "ML Study Group Weekly Sync", time: "Tonight, 6:00 PM (1h)", type: "Study Group", difficulty: "Beginner", score: 62, reasoning: "Lower relevance, but useful if you want to understand the design needs of ML engineers." }
    ],
    insights: [
      { message: "You solved 3 CSS grid bugs for community members. +15 community points!", type: "success" },
      { message: "New Figma variables guide added to the Design Systems resource hub.", type: "new" }
    ]
  },
  "emily": {
    id: "emily",
    name: "Emily",
    avatar: "E",
    role: "organizer",
    skill_level: "Organizer",
    headline: "Organizer Console: AgentField Community",
    subtext: "Tracking 14,230 active members across 18 specialized channels. The operational intelligence layer recommends 3 actions today.",
    verified_skills: [
      { name: "Community Management", level: 5 },
      { name: "Public Relations", level: 4 }
    ],
    goals: ["Growth", "Mentorship Activation", "Event Scaling"],
    learning_paths: [],
    interests: ["Operations", "Growth", "Events"],
    recommended_people: [],
    communities: { show: [], hide: [] },
    resources: [],
    events: [],
    insights: []
  }
};

// 2. State Variables
let currentUser = hardcodedUsers["rahul"];
let currentRole = "member"; // "member" or "organizer"
let customUserProfile = null; // Stored user onboarded profile

// 3. Organizer Community Data (For Organizer Dashboard)
const communityHealthMetrics = {
  score: 82,
  new_members: 142,
  active_members: 3482,
  at_risk_members: 8,
  trending_topics: ["CUDA Memory", "PyTorch Tensors", "Design Tokens", "Rust FFI"],
  unanswered_questions: 14,
  mentor_pool_size: 42,
  active_mentorships: 18
};

const suggestedActions = [
  {
    id: "act-ama",
    action: "Schedule GPU Memory AMA Session",
    reason: "14 unanswered GPU/CUDA questions flagged by Identity Agent in systems threads this week.",
    impact: "Would answer query bottlenecks for 18+ Intermediate and Beginner learners.",
    assign_to: "Sarah Jenkins",
    status: "suggested"
  },
  {
    id: "act-mentor",
    action: "Recruit Sarah Jenkins to mentor Rahul",
    reason: "Identity Agent detected 94% skills alignment compatibility. Rahul has CUDA Shared Memory gap; Sarah is expert.",
    impact: "Establishes structured learning path to complete Rahul's roadmap (now at 70%).",
    assign_to: "System Match",
    status: "suggested"
  },
  {
    id: "act-faq",
    action: "Generate PyTorch Tensor FAQ Doc",
    reason: "Learning Agent detected 8 beginner users repeating Tensor AutoGrad setup queries.",
    impact: "Reduces duplicate community support requests by estimated 25%.",
    assign_to: "Amit Sharma",
    status: "suggested"
  }
];

const potentialMentorsList = [
  { name: "Sarah Jenkins", expertise: ["CUDA", "Distributed Systems"], rating: "4.9★", count: 12, status: "Active" },
  { name: "Amit Sharma", expertise: ["PyTorch", "AI Infrastructure"], rating: "4.8★", count: 8, status: "Active" },
  { name: "Marcus Aurelius", expertise: ["Rust", "Systems Design"], rating: "5.0★", count: 15, status: "Away" },
  { name: "Yuki Tanaka", expertise: ["Figma", "Design Engineering"], rating: "4.7★", count: 5, status: "Active" }
];

// 4. Onboarding Parsing and Custom Profile Generation
function generateCustomProfile(name, githubUrl, linkedinUrl) {
  // Simple check checks
  let cleanGithub = githubUrl.toLowerCase();
  let skill = "Intermediate";
  let inferredInterests = [];
  let skills = [];
  let goals = [];
  let roadmap = "";
  
  // Rule-based inference engine (Identity Agent mockup)
  if (cleanGithub.includes("cuda") || cleanGithub.includes("gpu") || cleanGithub.includes("kernel") || cleanGithub.includes("cpp")) {
    inferredInterests = ["Systems Programming", "GPU Architecture", "AI Infrastructure"];
    skills = [
      { name: "C++", level: 3 },
      { name: "GPU Runtimes", level: 2 }
    ];
    goals = ["Master CUDA Memory Optimization", "Understand System Level Kernels"];
    roadmap = "CUDA & Systems Programming Path";
  } else if (cleanGithub.includes("pytorch") || cleanGithub.includes("ml") || cleanGithub.includes("ai") || cleanGithub.includes("python") || cleanGithub.includes("tensor") || cleanGithub.includes("deeplearning")) {
    inferredInterests = ["Machine Learning", "AI Infrastructure", "Python Programming"];
    skills = [
      { name: "Python", level: 3 },
      { name: "Data Science", level: 2 }
    ];
    goals = ["Deep Learning Deployment", "PyTorch Custom Layers Architecture"];
    roadmap = "Machine Learning Infrastructure Roadmap";
  } else if (cleanGithub.includes("react") || cleanGithub.includes("js") || cleanGithub.includes("web") || cleanGithub.includes("html") || cleanGithub.includes("design") || cleanGithub.includes("figma")) {
    inferredInterests = ["Frontend Dev", "Design Systems", "UI/UX Architecture"];
    skills = [
      { name: "HTML/CSS/JS", level: 4 },
      { name: "React Framework", level: 3 }
    ];
    goals = ["Automate Design Tokens", "Build Custom Web Layouts"];
    roadmap = "React & Frontend Design Systems";
  } else {
    // Default fallback
    inferredInterests = ["Software Engineering", "Open Source Contribution", "Systems Engineering"];
    skills = [
      { name: "Web Technologies", level: 3 },
      { name: "Programming Basics", level: 4 }
    ];
    goals = ["Build Full-Stack Apps", "Learn Advanced Algorithms"];
    roadmap = "Full Stack Development & Orchestration";
  }

  // Create personalized custom profile
  const customProfile = {
    id: "custom_user",
    name: name,
    avatar: name.substring(0, 2).toUpperCase(),
    role: "member",
    skill_level: skill,
    headline: `Welcome, ${name} 🌟`,
    subtext: `Your personalized environment is active. Custom signals generated from GitHub [${githubUrl.split('/').pop()}] & LinkedIn.`,
    verified_skills: skills,
    goals: goals,
    learning_paths: [
      { name: roadmap, progress: 10, completed: 1, total: 10, next_milestone: "Milestone 2: Initial Setup & Environment Verification" }
    ],
    interests: inferredInterests,
    recommended_people: [
      { name: "Sarah Jenkins", role: "Principal GPU Engineer at Nvidia", match: 89, avatar: "SJ", reason: "Top system systems programmer match for your GitHub repo projects." },
      { name: "Amit Sharma", role: "AI Infra Lead", match: 85, avatar: "AS", reason: "Matches pythonic AI and data processing components found in your repositories." }
    ],
    communities: {
      show: inferredInterests,
      hide: ["Web3 & Blockchain", "Mobile Design"].filter(x => !inferredInterests.includes(x))
    },
    resources: [
      { id: "res-custom-1", title: `Introduction to ${inferredInterests[0]} Best Practices`, type: "Selected Guide", duration: "20 min", difficulty: "Intermediate", score: 92, reasoning: "Directly matches Github repos data structure signals." },
      { id: "res-custom-2", title: "Open Source Collaboration Guidelines", type: "Article", duration: "15 min", difficulty: "Beginner", score: 85, reasoning: "Highly recommended for active GitHub developers entering CommunityOS." }
    ],
    events: [
      { id: "evt-custom-1", title: `${inferredInterests[0]} Weekly Roundtable`, time: "Today, 8:00 PM (1h)", type: "Roundtable", difficulty: "Intermediate", score: 90, reasoning: "Matches your top stated interest and skill level." },
      { id: "evt-custom-2", title: "GitHub Portfolio & Career Building Clinic", time: "Monday, 6:00 PM (1h 30m)", type: "AMA", difficulty: "Beginner", score: 80, reasoning: "Aligns with your new community signup activity." }
    ],
    insights: [
      { message: "Identity Agent successfully parsed your environment profile.", type: "success" },
      { message: `Roadmap generated: ${roadmap}. Starting with 10% progress.`, type: "roadmap" }
    ]
  };

  return customProfile;
}

// 5. Decision logs for Explainability ("Why am I seeing this?")
const agentDecisionLogs = {
  // Rahul Decisions
  "res-cuda-mem": {
    title: "CUDA Shared Memory & Coalescing Techniques",
    score: "96%",
    involved: ["Identity", "Learning", "Discovery"],
    timings: { "Identity": "1.2ms", "Learning": "2.4ms", "Discovery": "4.1ms" },
    reasoning: [
      "Identity Agent: Detected Intermediate skill level with verified CUDA proficiency of level 3.",
      "Learning Agent: Identified active CUDA Optimization Roadmap with 70% completion. Next milestone requires Memory Coalescing skills (currently marked as a skill gap).",
      "Discovery Agent: Extracted 'Systems Programming' tag. Located this high-priority article, applying a 20% roadmap alignment boost.",
      "Temporal Engine: Applied 10% boost because GPU Memory Architectures Workshop starts tonight (led by author Sarah Jenkins)."
    ]
  },
  "res-kernel-dev": {
    title: "Linux Kernel Module Programming Guide",
    score: "82%",
    involved: ["Identity", "Discovery"],
    timings: { "Identity": "1.2ms", "Discovery": "3.5ms" },
    reasoning: [
      "Identity Agent: Read 'Linux Systems' (level 3) from verified skills.",
      "Discovery Agent: Matched user's active goals (Kernel Development). Ranked this resource with 82% confidence because of high community bookmarks count (128)."
    ]
  },
  "evt-gpu-ws": {
    title: "GPU Memory Architectures Workshop",
    score: "95%",
    involved: ["Identity", "Learning", "Mentor", "Discovery"],
    timings: { "Identity": "1.2ms", "Learning": "2.1ms", "Mentor": "3.0ms", "Discovery": "3.8ms" },
    reasoning: [
      "Identity Agent: Confirmed CUDA focus and intermediate systems profile.",
      "Learning Agent: Matched CUDA Memory milestone. Aligns with CUDA roadmap objectives.",
      "Mentor Agent: Identified event host (Sarah Jenkins) is user's top recommended mentor (94% compatibility).",
      "Discovery Agent: Applied maximum temporal boost since workshop is tonight. Reserved capacity: 2 spots left."
    ]
  },
  "evt-ama-rust": {
    title: "Rust FFI & C++ Interoperability AMA",
    score: "79%",
    involved: ["Identity", "Discovery"],
    timings: { "Identity": "1.0ms", "Discovery": "2.8ms" },
    reasoning: [
      "Identity Agent: Scanned profile and found interest in 'Systems Programming' and 'C++' skills.",
      "Discovery Agent: Rust FFI is highly trending in the Systems community this week. Aligns with intermediate development capability."
    ]
  },

  // Priya Decisions
  "res-torch-tensors": {
    title: "PyTorch Tensors: A Visual Guide for Beginners",
    score: "94%",
    involved: ["Identity", "Learning", "Discovery"],
    timings: { "Identity": "0.8ms", "Learning": "1.5ms", "Discovery": "3.0ms" },
    reasoning: [
      "Identity Agent: Detected Beginner ML profile with verified Python skills (level 2).",
      "Learning Agent: Tracked PyTorch Introduction Path progress (20% complete). Next milestone: computation graphs.",
      "Discovery Agent: Found direct keyword overlap with milestone 3. Filtered out advanced papers, highlighting this high-quality visualization."
    ]
  },
  "res-numpy-linalg": {
    title: "NumPy Matrix Operations in Practice",
    score: "85%",
    involved: ["Identity", "Discovery"],
    timings: { "Identity": "0.8ms", "Discovery": "2.2ms" },
    reasoning: [
      "Identity Agent: Highlighted user's Linear Algebra background (level 3) combined with Python programming.",
      "Discovery Agent: Recommends bridging math theories with practical library operations. 94% peer rating among beginner cohorts."
    ]
  },
  "evt-ml-kickoff": {
    title: "ML Study Group Weekly Sync",
    score: "91%",
    involved: ["Identity", "Discovery"],
    timings: { "Identity": "0.8ms", "Discovery": "2.5ms" },
    reasoning: [
      "Identity Agent: New signup profile, benefit from peer-led environments.",
      "Discovery Agent: High social proof signal. 4 members from your immediate signup cohort registered. Facilitates early onboarding."
    ]
  },
  "evt-pytorch-live": {
    title: "PyTorch Live Coding Session",
    score: "88%",
    involved: ["Learning", "Discovery"],
    timings: { "Learning": "1.8ms", "Discovery": "2.9ms" },
    reasoning: [
      "Learning Agent: PyTorch Introduction Roadmap alignment. Step-by-step beginner codes.",
      "Discovery Agent: Highly interactive event. Live Q&A fits learner profile preferences."
    ]
  },

  // Sarah Decisions
  "res-nccl-tuning": {
    title: "Multi-GPU Communication: Optimizing NCCL Backends",
    score: "98%",
    involved: ["Identity", "Learning", "Discovery"],
    timings: { "Identity": "1.5ms", "Learning": "2.0ms", "Discovery": "4.0ms" },
    reasoning: [
      "Identity Agent: Detected Expert profile in Distributed Clusters and CUDA (level 5).",
      "Learning Agent: Matched final milestone (Multi-Node NCCL Tuning) of systems research roadmap.",
      "Discovery Agent: Served this expert paper on communication collectives. Bypassed simple guides entirely."
    ]
  },
  "res-cuda-advanced": {
    title: "CUDA 12.4 Pipeline Registers & Asynchronous Copies",
    score: "90%",
    involved: ["Identity", "Discovery"],
    timings: { "Identity": "1.5ms", "Discovery": "3.1ms" },
    reasoning: [
      "Identity Agent: Expert in hardware systems.",
      "Discovery Agent: Newly released CUDA documentation. Flagged as highly critical for expert engineers maintaining systems codebases."
    ]
  },

  // Alex Decisions
  "res-react-design": {
    title: "React Component Archetypes for Designers",
    score: "92%",
    involved: ["Identity", "Learning", "Discovery"],
    timings: { "Identity": "1.1ms", "Learning": "2.3ms", "Discovery": "3.8ms" },
    reasoning: [
      "Identity Agent: Intermediate designer transitioning to React coding skills.",
      "Learning Agent: Active roadmap 'React Starter for Designers' (50% progress). Aligns with Milestone 6 (prop mapping).",
      "Discovery Agent: High relevance score because layout codes are shown in visual representations."
    ]
  },
  "res-tokens": {
    title: "Figma Variables & CSS Custom Properties Mapping",
    score: "89%",
    involved: ["Identity", "Discovery"],
    timings: { "Identity": "1.1ms", "Discovery": "3.0ms" },
    reasoning: [
      "Identity Agent: Figma skill level 5, CSS layout level 4.",
      "Discovery Agent: Strong goals correlation (automate design tokens). Recommended design tokens automation workflow."
    ]
  },
  "evt-design-token": {
    title: "Design Systems & Token Architecture Panel",
    score: "94%",
    involved: ["Identity", "Discovery"],
    timings: { "Identity": "1.1ms", "Discovery": "3.5ms" },
    reasoning: [
      "Identity Agent: Design systems interest verified.",
      "Discovery Agent: Panel features industry-leading web designers. High social engagement index."
    ]
  },
  "evt-ml-kickoff": {
    title: "ML Study Group Weekly Sync",
    score: "62%",
    involved: ["Identity", "Discovery"],
    timings: { "Identity": "1.0ms", "Discovery": "2.0ms" },
    reasoning: [
      "Identity Agent: User profile has no ML objectives.",
      "Discovery Agent: Low confidence score (62%). Showed in secondary list to offer broader cross-disciplinary learning options."
    ]
  },

  // Custom User Fallbacks
  "res-custom-1": {
    title: "Introductory Environment Resource Guide",
    score: "92%",
    involved: ["Identity", "Discovery"],
    timings: { "Identity": "1.5ms", "Discovery": "2.5ms" },
    reasoning: [
      "Identity Agent: Automatically parsed interest from GitHub profile repositories configuration.",
      "Discovery Agent: Recommended this core guide to familiarize yourself with parsed systems engineering patterns."
    ]
  },
  "res-custom-2": {
    title: "Open Source Collaboration Guidelines",
    score: "85%",
    involved: ["Identity", "Discovery"],
    timings: { "Identity": "1.0ms", "Discovery": "2.0ms" },
    reasoning: [
      "Identity Agent: Detected active developer status from GitHub URL inputs.",
      "Discovery Agent: Standard onboarding guide for developers joining CommunityOS workspaces."
    ]
  },
  "evt-custom-1": {
    title: "Specialized Weekly Roundtable",
    score: "90%",
    involved: ["Identity", "Discovery"],
    timings: { "Identity": "1.5ms", "Discovery": "3.0ms" },
    reasoning: [
      "Identity Agent: Inferred primary software engineering sector based on GitHub structures.",
      "Discovery Agent: High priority workshop matching your custom learning roadmap."
    ]
  },
  "evt-custom-2": {
    title: "GitHub Portfolio & Career Building Clinic",
    score: "80%",
    involved: ["Identity", "Discovery"],
    timings: { "Identity": "1.0ms", "Discovery": "2.5ms" },
    reasoning: [
      "Identity Agent: Scanned Github profile links.",
      "Discovery Agent: Direct guidance for maximizing Github community contribution footprints."
    ]
  }
};

// 6. DOM Elements Cache
const elements = {
  userSelect: null,
  roleToggleMember: null,
  roleToggleOrganizer: null,
  
  onboardingContainer: null,
  onboardingForm: null,
  
  mainDashboard: null,
  organizerDashboard: null,
  
  // Member Dashboard details
  heroHeadline: null,
  heroBody: null,
  heroPills: null,
  
  prioritiesSection: null,
  priorityGrid: null,
  
  kpiPathsName: null,
  kpiPathsProgress: null,
  kpiPathsNext: null,
  kpiSkillsList: null,
  kpiInterestsList: null,
  
  mentorSection: null,
  mentorList: null,
  
  communitiesSection: null,
  communitiesList: null,
  
  resourcesSection: null,
  resourcesList: null,
  
  eventsSection: null,
  eventsList: null,
  
  insightsSection: null,
  insightsList: null,
  
  // Organizer Dashboard Details
  orgHealthScore: null,
  orgNewMembers: null,
  orgActiveMembers: null,
  orgAtRiskMembers: null,
  orgTrendingTopics: null,
  orgUnanswered: null,
  orgActionsList: null,
  orgMentorsList: null,
  
  // Agent Pipeline Details
  agentTimeline: null,
  
  // Modal Details
  modalOverlay: null,
  modalTitle: null,
  modalBody: null,
  modalClose: null
};

// 7. Initialization & Event Bindings
document.addEventListener("DOMContentLoaded", () => {
  // Initialize elements cache
  elements.userSelect = document.getElementById("user-select");
  elements.roleToggleMember = document.getElementById("role-member");
  elements.roleToggleOrganizer = document.getElementById("role-organizer");
  
  elements.onboardingContainer = document.getElementById("onboarding-container");
  elements.onboardingForm = document.getElementById("onboarding-form");
  
  elements.mainDashboard = document.getElementById("main-dashboard");
  elements.organizerDashboard = document.getElementById("organizer-dashboard");
  
  elements.heroHeadline = document.getElementById("hero-headline");
  elements.heroBody = document.getElementById("hero-body");
  elements.heroPills = document.getElementById("hero-pills");
  
  elements.prioritiesSection = document.getElementById("priorities-section");
  elements.priorityGrid = document.getElementById("priority-grid");
  
  elements.kpiPathsName = document.getElementById("kpi-paths-name");
  elements.kpiPathsProgress = document.getElementById("kpi-paths-progress");
  elements.kpiPathsNext = document.getElementById("kpi-paths-next");
  elements.kpiSkillsList = document.getElementById("kpi-skills-list");
  elements.kpiInterestsList = document.getElementById("kpi-interests-list");
  
  elements.mentorSection = document.getElementById("mentor-section");
  elements.mentorList = document.getElementById("mentor-list");
  
  elements.communitiesSection = document.getElementById("communities-section");
  elements.communitiesList = document.getElementById("communities-list");
  
  elements.resourcesSection = document.getElementById("resources-section");
  elements.resourcesList = document.getElementById("resources-list");
  
  elements.eventsSection = document.getElementById("events-section");
  elements.eventsList = document.getElementById("events-list");
  
  elements.insightsSection = document.getElementById("insights-section");
  elements.insightsList = document.getElementById("insights-list");
  
  elements.orgHealthScore = document.getElementById("org-health-score");
  elements.orgNewMembers = document.getElementById("org-new-members");
  elements.orgActiveMembers = document.getElementById("org-active-members");
  elements.orgAtRiskMembers = document.getElementById("org-at-risk-members");
  elements.orgTrendingTopics = document.getElementById("org-trending-topics");
  elements.orgUnanswered = document.getElementById("org-unanswered");
  elements.orgActionsList = document.getElementById("org-actions-list");
  elements.orgMentorsList = document.getElementById("org-mentors-list");
  
  elements.agentTimeline = document.getElementById("agent-timeline");
  
  elements.modalOverlay = document.getElementById("modal-overlay");
  elements.modalTitle = document.getElementById("modal-title");
  elements.modalBody = document.getElementById("modal-body");
  elements.modalClose = document.getElementById("modal-close");

  // Event bindings
  elements.userSelect.addEventListener("change", handleUserChange);
  elements.roleToggleMember.addEventListener("click", () => switchRole("member"));
  elements.roleToggleOrganizer.addEventListener("click", () => switchRole("organizer"));
  
  elements.onboardingForm.addEventListener("submit", handleOnboardingSubmit);
  elements.modalClose.addEventListener("click", closeModal);
  elements.modalOverlay.addEventListener("click", (e) => {
    if (e.target === elements.modalOverlay) closeModal();
  });

  // Load Initial Dashboard
  renderApp();
});

// 8. Event Handlers
function handleUserChange(e) {
  const userId = e.target.value;
  if (userId === "new") {
    // Show Onboarding and hide dashboard
    elements.onboardingContainer.style.display = "block";
    elements.mainDashboard.style.display = "none";
    elements.organizerDashboard.style.display = "none";
    document.getElementById("agent-view").style.display = "none";
  } else {
    elements.onboardingContainer.style.display = "none";
    if (userId === "custom") {
      currentUser = customUserProfile;
    } else {
      currentUser = hardcodedUsers[userId];
    }
    
    // Automatically adjust role availability
    if (currentUser.id === "emily") {
      switchRole("organizer");
    } else {
      switchRole("member");
    }
  }
}

function handleOnboardingSubmit(e) {
  e.preventDefault();
  
  const name = document.getElementById("onboard-name").value.trim();
  const github = document.getElementById("onboard-github").value.trim();
  const linkedin = document.getElementById("onboard-linkedin").value.trim();
  
  if (!name || !github || !linkedin) {
    alert("Please fill out all fields for your personalized environment.");
    return;
  }
  
  // Generate Profile
  customUserProfile = generateCustomProfile(name, github, linkedin);
  
  // Add to select options dynamically if not already added
  let hasCustomOption = false;
  for (let option of elements.userSelect.options) {
    if (option.value === "custom") {
      hasCustomOption = true;
      break;
    }
  }
  
  if (!hasCustomOption) {
    const option = document.createElement("option");
    option.value = "custom";
    option.text = `${name} (Personalized)`;
    elements.userSelect.add(option, elements.userSelect.options[elements.userSelect.options.length - 1]);
  } else {
    // Update label
    for (let option of elements.userSelect.options) {
      if (option.value === "custom") {
        option.text = `${name} (Personalized)`;
        break;
      }
    }
  }
  
  // Select custom user and render
  elements.userSelect.value = "custom";
  currentUser = customUserProfile;
  
  elements.onboardingContainer.style.display = "none";
  switchRole("member");
}

function switchRole(role) {
  currentRole = role;
  
  if (role === "member") {
    elements.roleToggleMember.classList.add("active");
    elements.roleToggleOrganizer.classList.remove("active");
    
    elements.mainDashboard.style.display = "block";
    elements.organizerDashboard.style.display = "none";
    document.getElementById("agent-view").style.display = "block";
  } else {
    elements.roleToggleMember.classList.remove("active");
    elements.roleToggleOrganizer.classList.add("active");
    
    elements.mainDashboard.style.display = "none";
    elements.organizerDashboard.style.display = "block";
    document.getElementById("agent-view").style.display = "block";
  }
  
  renderApp();
}

// 9. Main Render Router
function renderApp() {
  if (currentRole === "member") {
    renderMemberDashboard();
  } else {
    renderOrganizerDashboard();
  }
  renderAgentFlow();
}

// 10. Member Dashboard Renderer
function renderMemberDashboard() {
  const u = currentUser;
  
  // Hero section
  elements.heroHeadline.textContent = u.headline;
  elements.heroBody.textContent = u.subtext;
  
  // Hero CTA Buttons
  elements.heroPills.innerHTML = `
    <button class="btn-filled" onclick="alert('Starting learning path: ${u.learning_paths[0]?.name || 'General Core'}')">Continue Path</button>
    <a href="${u.id === 'custom' ? 'https://github.com' : '#'}" target="_blank" class="btn-outlined">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px;"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg>
      GitHub Profile
    </a>
  `;

  // Render Priority list / Action items
  elements.priorityGrid.innerHTML = "";
  
  // Build top priorities
  if (u.learning_paths && u.learning_paths.length > 0) {
    const path = u.learning_paths[0];
    createPriorityCard("Active learning path progress", path.name, `${path.progress}% Complete`, `Next: ${path.next_milestone}`, "Identity/Learning Agents", "res-cuda-mem");
  }
  
  if (u.events && u.events.length > 0) {
    const event = u.events[0];
    createPriorityCard("High-confidence recommended event", event.title, event.time, `Confidence Score: ${event.score}%`, "Discovery Agent", event.id);
  }
  
  if (u.recommended_people && u.recommended_people.length > 0) {
    const mentor = u.recommended_people[0];
    createPriorityCard("Top mentor match for goals", mentor.name, mentor.role, `Compatibility Score: ${mentor.match}%`, "Mentor Agent", "mentor-match");
  }

  // Render KPI Card Metrics
  if (u.learning_paths && u.learning_paths.length > 0) {
    const path = u.learning_paths[0];
    elements.kpiPathsName.textContent = path.name;
    elements.kpiPathsProgress.textContent = `${path.progress}%`;
    elements.kpiPathsNext.textContent = path.next_milestone;
  } else {
    elements.kpiPathsName.textContent = "No active roadmaps";
    elements.kpiPathsProgress.textContent = "0%";
    elements.kpiPathsNext.textContent = "Complete profile to generate paths.";
  }

  // Verified Skills
  elements.kpiSkillsList.innerHTML = u.verified_skills.map(s => `
    <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px; border-bottom: 1px dashed var(--color-chalk); padding-bottom: 4px;">
      <span style="font-weight: 500;">${s.name}</span>
      <span style="color: var(--color-signal-orange); font-weight: 600;">Lvl ${s.level}</span>
    </div>
  `).join("");

  // Stated Interests
  elements.kpiInterestsList.innerHTML = u.interests.map(i => `
    <span class="card-badge orange" style="margin-right: 6px; margin-bottom: 6px; display: inline-block;">${i}</span>
  `).join("");

  // Recommended People / Mentors
  if (u.recommended_people && u.recommended_people.length > 0) {
    elements.mentorSection.style.display = "block";
    elements.mentorList.innerHTML = u.recommended_people.map(p => `
      <div class="mentor-item">
        <div class="mentor-info">
          <div class="mentor-avatar">${p.avatar}</div>
          <div class="mentor-details">
            <span class="mentor-name">${p.name}</span>
            <span class="mentor-role">${p.role}</span>
            <p style="font-size: 12px; color: var(--color-graphite); margin-top: 4px;">${p.reason}</p>
          </div>
        </div>
        <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 8px;">
          <span class="mentor-score-pill"><span class="mentor-score-label">${p.match}%</span> match</span>
          <button class="btn-filled btn-small" onclick="alert('Connection request sent to ${p.name}')">Connect</button>
        </div>
      </div>
    `).join("");
  } else {
    elements.mentorSection.style.display = "none";
  }

  // Recommended Communities (show visible, hide filtered out)
  elements.communitiesList.innerHTML = "";
  u.communities.show.forEach(c => {
    const pill = document.createElement("span");
    pill.className = "community-pill";
    pill.textContent = `# ${c}`;
    pill.onclick = () => alert(`Entering channel: #${c}`);
    elements.communitiesList.appendChild(pill);
  });
  u.communities.hide.forEach(c => {
    const pill = document.createElement("span");
    pill.className = "community-pill hidden";
    pill.title = "Filtered out by Discovery Agent to reduce clutter. Click to reveal.";
    pill.textContent = `# ${c}`;
    pill.onclick = () => {
      if (confirm(`This channel was hidden by the Discovery Agent. Enter anyway?`)) {
        alert(`Entering channel: #${c}`);
      }
    };
    elements.communitiesList.appendChild(pill);
  });

  // Recommended Resources
  elements.resourcesList.innerHTML = u.resources.map(r => `
    <div class="card">
      <div class="card-header-row">
        <div>
          <span class="card-badge">${r.type}</span>
          <span class="card-badge orange" style="margin-left: 6px;">Score: ${r.score}%</span>
        </div>
        <button class="why-btn" onclick="openExplainabilityModal('${r.id}')">Why?</button>
      </div>
      <h3 class="card-title" style="margin-top: 6px; font-size: 15px;">${r.title}</h3>
      <p style="font-size: 12px; color: var(--color-slate); margin-top: 4px;">Est: ${r.duration} • Difficulty: ${r.difficulty}</p>
      <div style="margin-top: auto; padding-top: 16px; display: flex; justify-content: space-between; align-items: center;">
        <p style="font-size: 11px; color: var(--color-graphite); max-width: 70%; line-height: 1.2;">${r.reasoning.substring(0, 60)}...</p>
        <button class="btn-filled btn-small" onclick="alert('Opening resource: ${r.title}')">Open</button>
      </div>
    </div>
  `).join("");

  // Upcoming Events
  elements.eventsList.innerHTML = u.events.map(e => `
    <div class="event-row">
      <div class="event-info">
        <span class="event-title">${e.title}</span>
        <span class="event-time">${e.time} • <strong style="color: var(--color-signal-orange);">${e.score}% compatibility</strong></span>
      </div>
      <div style="display: flex; gap: 8px;">
        <button class="why-btn" style="padding: 4px 10px;" onclick="openExplainabilityModal('${e.id}')">Why?</button>
        <button class="btn-filled btn-small" onclick="alert('Registered successfully for ${e.title}')">Register</button>
      </div>
    </div>
  `).join("");

  // Insights / Notifications
  elements.insightsList.innerHTML = u.insights.map(i => `
    <div style="display: flex; align-items: center; gap: 12px; padding: 12px; background-color: var(--color-fog); border-radius: var(--radius-cards); margin-bottom: 8px; border-left: 3px solid var(--color-signal-orange);">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--color-signal-orange);"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
      <span style="font-size: 13px; font-weight: 500; color: var(--color-carbon);">${i.message}</span>
    </div>
  `).join("");
}

// Helper to construct priority cards
function createPriorityCard(label, title, val, footerText, agentText, decisionId) {
  const card = document.createElement("div");
  card.className = "card";
  card.innerHTML = `
    <div class="card-header-row">
      <span class="card-badge">${label}</span>
      <button class="why-btn" onclick="openExplainabilityModal('${decisionId}')">Why?</button>
    </div>
    <h3 class="card-title" style="margin-top: 8px; font-size: 18px; line-height: 1.2;">${title}</h3>
    <div class="kpi-value" style="font-size: 24px; margin: 8px 0;">${val}</div>
    <div style="margin-top: auto; display: flex; justify-content: space-between; font-size: 11px; color: var(--color-slate); border-top: 1px solid var(--color-chalk); padding-top: 8px;">
      <span>${footerText}</span>
      <span style="color: var(--color-sienna-bronze);">${agentText}</span>
    </div>
  `;
  elements.priorityGrid.appendChild(card);
}

// 11. Organizer Dashboard Renderer
function renderOrganizerDashboard() {
  const m = communityHealthMetrics;
  
  // Health Metrics scores
  elements.orgHealthScore.textContent = `${m.score}%`;
  elements.orgNewMembers.textContent = `+${m.new_members}`;
  elements.orgActiveMembers.textContent = m.active_members;
  elements.orgAtRiskMembers.textContent = `${m.at_risk_members} members`;
  elements.orgUnanswered.textContent = m.unanswered_questions;

  // Trending tags
  elements.orgTrendingTopics.innerHTML = m.trending_topics.map(t => `
    <span class="card-badge orange" style="margin-right: 6px; margin-bottom: 6px; display: inline-block;"># ${t}</span>
  `).join("");

  // Suggested Actions List
  elements.orgActionsList.innerHTML = suggestedActions.map(a => `
    <div style="padding: 16px; background-color: var(--color-fog); border-radius: var(--radius-cards); margin-bottom: 12px; border-left: 3px solid ${a.status === 'approved' ? '#10b981' : 'var(--color-signal-orange)'};">
      <div style="display: flex; justify-content: space-between; align-items: flex-start;">
        <span style="font-weight: 600; font-size: 14px; color: var(--color-carbon);">${a.action}</span>
        <span class="card-badge" style="text-transform: capitalize; background-color: ${a.status === 'approved' ? 'rgba(16, 185, 129, 0.1)' : 'var(--color-chalk)'}; color: ${a.status === 'approved' ? '#10b981' : 'var(--color-graphite)'};">${a.status}</span>
      </div>
      <p style="font-size: 12px; color: var(--color-graphite); margin: 8px 0 4px 0;"><strong>Reason:</strong> ${a.reason}</p>
      <p style="font-size: 12px; color: var(--color-sienna-bronze); margin-bottom: 8px;"><strong>Impact Projection:</strong> ${a.impact}</p>
      <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px dashed var(--color-chalk); padding-top: 8px; margin-top: 4px;">
        <span style="font-size: 11px; color: var(--color-slate);">Assignee suggestion: <strong>${a.assign_to}</strong></span>
        ${a.status === 'suggested' ? `
          <button class="btn-filled btn-small" onclick="approveAction('${a.id}')">Approve & Execute</button>
        ` : `
          <span style="font-size: 12px; color: #10b981; font-weight: 500;">✓ In Execution Pipeline</span>
        `}
      </div>
    </div>
  `).join("");

  // Mentors Pool list
  elements.orgMentorsList.innerHTML = potentialMentorsList.map(p => `
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid var(--color-chalk);">
      <div style="display: flex; flex-direction: column;">
        <span style="font-size: 14px; font-weight: 600; color: var(--color-carbon);">${p.name} (${p.rating})</span>
        <span style="font-size: 11px; color: var(--color-slate);">${p.expertise.join(", ")}</span>
      </div>
      <div style="text-align: right; display: flex; align-items: center; gap: 12px;">
        <span style="font-size: 12px; color: var(--color-graphite);">${p.count} active mentees</span>
        <span class="card-badge" style="background-color: ${p.status === 'Active' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)'}; color: ${p.status === 'Active' ? '#10b981' : '#ef4444'};">${p.status}</span>
      </div>
    </div>
  `).join("");
}

// Action executor mockup
window.approveAction = function(actionId) {
  const action = suggestedActions.find(a => a.id === actionId);
  if (action) {
    action.status = "approved";
    alert(`Action Approved! Identity and Discovery Agents have dispatched notification to ${action.assign_to}.`);
    renderOrganizerDashboard();
  }
};

// 12. Agent Execution Timeline Flow Renderer
function renderAgentFlow() {
  const steps = [
    { name: "Identity Agent", desc: "Profile understanding & verified skills detection", timing: "0.8ms - 1.5ms" },
    { name: "Learning Agent", desc: "Learning path milestone check & active skill gaps analysis", timing: "1.5ms - 2.4ms" },
    { name: "Discovery Agent", desc: "Relevance calculations, interest matching, decay applied", timing: "2.2ms - 4.1ms" },
    { name: "Mentor Agent", desc: "Co-collaborator & teacher search matrix comparison", timing: "2.8ms - 3.8ms" }
  ];

  if (currentRole === "organizer") {
    steps.push({ name: "Organizer Agent", desc: "Aggregate overall stats & churn vector evaluations", timing: "4.5ms" });
  }

  elements.agentTimeline.innerHTML = steps.map((s, index) => `
    <div class="agent-node ${index === steps.length - 1 ? 'active' : ''}">
      <div class="agent-node-header">
        <span>${s.name}</span>
        <span style="color: var(--color-signal-orange);">${s.timing}</span>
      </div>
      <div class="agent-node-desc">${s.desc}</div>
      <div class="agent-node-meta">Inputs parsed: user_id, active_session_logs, graph_nodes_cache</div>
    </div>
  `).join("") + `
    <div style="font-size: 13px; color: #10b981; font-weight: 600; margin-top: 12px; display: flex; align-items: center; gap: 8px;">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
      Dashboard refreshed and layout orchestrated successfully.
    </div>
  `;
}

// 13. Explainability Modal ("Why am I seeing this?")
window.openExplainabilityModal = function(decisionId) {
  let log = agentDecisionLogs[decisionId];
  
  if (!log) {
    // Generate custom fallbacks dynamically for custom users/mentors
    if (decisionId === "mentor-match") {
      log = {
        title: `Recommended Mentors`,
        score: `${currentUser.recommended_people[0]?.match || 90}%`,
        involved: ["Identity", "Mentor"],
        timings: { "Identity": "1.2ms", "Mentor": "3.5ms" },
        reasoning: [
          `Identity Agent: Evaluated goals: [${currentUser.goals.join(', ')}].`,
          `Mentor Agent: Filtered for verified community mentors with overlapping tags: [${currentUser.interests.join(', ')}]. Matching score computed based on communication skills and availability.`
        ]
      };
    } else {
      // Fallback
      log = {
        title: `Reasoning Context - Decision ID: ${decisionId}`,
        score: "85%",
        involved: ["Identity", "Discovery"],
        timings: { "Identity": "1.0ms", "Discovery": "2.0ms" },
        reasoning: [
          "Identity Agent: Read stated interests from onboarded user profile preferences.",
          "Discovery Agent: Highlighted high-engagement items in alignment with community topics."
        ]
      };
    }
  }

  // Populate Modal contents
  elements.modalTitle.textContent = "Why am I seeing this?";
  
  elements.modalBody.innerHTML = `
    <div style="margin-bottom: 20px;">
      <h4 style="font-size: 16px; font-weight: 600; color: var(--color-carbon); margin-bottom: 4px;">${log.title}</h4>
      <p style="font-size: 13px; color: var(--color-slate);">Multiple cooperative AI agents collaborated to rank this card for your viewport.</p>
    </div>
    
    <div style="margin-bottom: 24px;">
      <label class="form-label" style="font-weight: 600;">Cooperating Agents and Execution Timings</label>
      <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 6px;">
        ${log.involved.map(agent => `
          <div style="background-color: var(--color-fog); border: 1px solid var(--color-chalk); border-radius: var(--radius-tags); padding: 4px 12px; font-size: 12px; display: flex; justify-content: space-between; width: calc(50% - 4px);">
            <strong style="color: var(--color-carbon);">${agent} Agent</strong>
            <span style="color: var(--color-sienna-bronze);">${log.timings[agent] || '—'}</span>
          </div>
        `).join("")}
      </div>
    </div>
    
    <div style="margin-bottom: 24px;">
      <label class="form-label" style="font-weight: 600;">Agent Reasoning Chain Details</label>
      <div class="reasoning-list">
        ${log.reasoning.map(step => `
          <div class="reasoning-item">${step}</div>
        `).join("")}
      </div>
    </div>

    <div style="margin-bottom: 24px; border-top: 1px solid var(--color-chalk); padding-top: 16px;">
      <label class="form-label" style="font-weight: 600; margin-bottom: 8px;">Fine-tune Recommendations</label>
      <p style="font-size: 12px; color: var(--color-slate); margin-bottom: 12px;">Adjust the agent weighting coefficients below to customize recommendations for your focus.</p>
      
      <div style="display: flex; flex-direction: column; gap: 10px;">
        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12px;">
          <span style="font-weight: 500;">Learning Roadmap Bias</span>
          <input type="range" min="1" max="100" value="80" class="tuning-slider" style="width: 150px; accent-color: var(--color-signal-orange);" oninput="updateCoef(this.value)">
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12px;">
          <span style="font-weight: 500;">Temporal Recency Bias</span>
          <input type="range" min="1" max="100" value="50" class="tuning-slider" style="width: 150px; accent-color: var(--color-signal-orange);">
        </div>
      </div>
    </div>
    
    <div class="confidence-gauge">
      <span class="confidence-title">Overall Recommendation Confidence</span>
      <span class="confidence-value">${log.score}</span>
    </div>
  `;
  
  elements.modalOverlay.classList.add("active");
};

window.updateCoef = function(val) {
  // Mock weight adjusting
  console.log(`Updated roadmap bias coefficient to: ${val}`);
};

function closeModal() {
  elements.modalOverlay.classList.remove("active");
}
