"use client";

import React, { useState, useEffect } from "react";
import { 
  User, Sparkles, Cpu, BookOpen, Calendar, Users, Award, Activity, 
  TrendingUp, AlertTriangle, CheckCircle2, ArrowRight, ChevronRight, 
  Info, Lock, RefreshCw, Play, Check, CheckSquare, ShieldCheck, 
  Search, MessageSquare, Terminal, Eye, AlertCircle, ChevronDown
} from "lucide-react";

// Local high-fidelity fallback data in case the backend is loading or unavailable
const FALLBACK_DATA = {
  rahul: {
    member_id: "rahul",
    name: "Rahul",
    bio: "Systems programming and GPU enthusiast. Building custom CUDA kernels and optimizing LLM inference engines. Love low-level stuff.",
    skills: ["CUDA", "C++", "Rust", "Systems Programming", "GPU Architecture"],
    welcome_message: "Welcome back Rahul! Based on your recent activity, here are today's priorities.",
    priorities: [
      "Attend GPU Workshop with Sarah", 
      "Reply to Aman's Rust ownership thread", 
      "Finish CUDA Roadmap (Shared Memory Bank Conflicts)"
    ],
    recommended_mentor: {
      name: "Sarah",
      role: "Senior CUDA Engineer @ Nvidia",
      overlap_reason: "Strong interest overlap in systems programming, CUDA optimizations, and low-level performance metrics."
    },
    communities: {
      recommended: [
        { id: "systems-programming", name: "Systems Programming", description: "Low-level coding, OS design, assembly, compilers, and systems architecture." },
        { id: "gpu-computing", name: "GPU Computing", description: "CUDA, OpenCL, parallel computing, shaders, and hardware acceleration." },
        { id: "ai-infrastructure", name: "AI Infrastructure", description: "Serving, hardware optimization, distributed training pipelines, and MLOps." }
      ],
      lower_priority: [
        { id: "anime", name: "Anime", description: "Discussing your favorite anime shows, manga, and conventions." },
        { id: "football", name: "Football", description: "Match threads, Premier League discussions, and tactical analysis." },
        { id: "web3", name: "Web3", description: "Blockchains, smart contracts, and decentralized protocols." }
      ]
    },
    resources: [
      { id: "cuda-optimization", name: "CUDA Optimization Guide", url: "#", description: "Official handbook for optimizing CUDA grid layouts, memory coalescing, and instruction throughput." },
      { id: "gpu-performance", name: "GPU Performance Handbook", url: "#", description: "An exhaustive resource on memory hierarchies, instruction latencies, and profiling micro-architectures." },
      { id: "rust-ownership", name: "Rust Ownership Cheatsheet", url: "#", description: "A quick visual reference for understanding owners, references, borrowing, and lifetime mechanics." }
    ],
    events: [
      { id: "gpu-ama", name: "GPU AMA with Sarah", time: "Friday at 5:00 PM UTC", description: "Open Q&A session with Sarah (Senior CUDA Engineer) on hardware profiling, tensor cores, and kernel debugging." },
      { id: "ai-systems-meetup", name: "AI Systems & Inference Meetup", time: "Wednesday at 6:30 PM UTC", description: "Technical presentations detailing high-performance inference setups, vLLM optimization, and low-latency deployments." },
      { id: "rust-workshop", name: "Rust Lifetimes & Ownership Workshop", time: "Saturday at 2:00 PM UTC", description: "Interactive live coding lab addressing common lifetime errors, smart pointers, and borrow checker fights." }
    ],
    insights: [
      "Top 15% contributor",
      "Helped 6 beginners this week",
      "Eligible to become a mentor"
    ],
    explainability: {
      identity_agent: "Identity Agent: Analyzed Rahul's bio and active channels. His message in #gpu-computing regarding CUDA bank conflicts confirms intermediate-to-advanced low-level skills. His reply in #rust helping Aman proves he is highly capable and active in systems topics.",
      discovery_agent: "Discovery Agent: Matched Rahul's profile containing systems and GPU interests with the GPU Computing, Systems Programming, and AI Infrastructure channels. Filtered out anime and football as lower priority since they do not align with his systems engineering goals. Recommended CUDA and GPU performance resources and the upcoming GPU AMA.",
      learning_agent: "Learning Agent: Identified Rahul's intermediate skill level and hands-on style. Recommended immediate action to resolve his active question on bank conflicts, attend the GPU AMA, and help Aman to reinforce his own Rust mastery.",
      mentor_agent: "Mentor Agent: Matched Rahul with Sarah. Both have a primary focus on CUDA and hardware execution. Sarah's expert background at Nvidia is perfect to guide Rahul from intermediate CUDA kernel optimizations to advanced GPU memory layouts."
    }
  },
  priya: {
    member_id: "priya",
    name: "Priya",
    bio: "Beginner AI learner. Coming from a non-CS background. Want to understand machine learning concepts and how to train simple neural networks using PyTorch.",
    skills: ["Python", "Basic Math"],
    welcome_message: "Welcome back Priya! Based on your recent activity, here are today's priorities.",
    priorities: [
      "Post your introduction in #introductions", 
      "Complete PyTorch 101: Build Your First Neural Network", 
      "Review Neural Networks from Scratch guide"
    ],
    recommended_mentor: {
      name: "Elena",
      role: "Machine Learning Researcher",
      overlap_reason: "Shares high alignment in PyTorch, deep learning basics, and model architectures. Elena's bio details a passion for helping beginners."
    },
    communities: {
      recommended: [
        { id: "pytorch-study-group", name: "PyTorch Study Group", description: "Weekly study groups for building and training neural networks using PyTorch." },
        { id: "machine-learning-basics", name: "Machine Learning Basics", description: "Foundational math, linear algebra, and entry-level ML algorithms." },
        { id: "ai-infrastructure", name: "AI Infrastructure", description: "Serving, hardware optimization, distributed training pipelines, and MLOps." }
      ],
      lower_priority: [
        { id: "systems-programming", name: "Systems Programming", description: "Low-level coding, OS design, assembly, compilers, and systems architecture." },
        { id: "gpu-computing", name: "GPU Computing", description: "CUDA, OpenCL, parallel computing, shaders, and hardware acceleration." },
        { id: "web3", name: "Web3", description: "Blockchains, smart contracts, and decentralized protocols." }
      ]
    },
    resources: [
      { id: "intro-pytorch", name: "Intro to PyTorch Notebooks", url: "#", description: "Hands-on Jupyter notebooks detailing Tensors, Datasets, autograd, and training loops step-by-step." },
      { id: "nn-from-scratch", name: "Neural Networks from Scratch (Python)", url: "#", description: "Build, feedforward, backpropagate, and train fully connected neural nets in raw Python without external libraries." },
      { id: "deep-learning-ch5", name: "Deep Learning Book Chapter 5", url: "#", description: "A mathematical deep dive into machine learning foundations: loss functions, capacity, bias-variance trade-offs." }
    ],
    events: [
      { id: "pytorch-basics-101", name: "PyTorch 101: Build Your First Neural Network", time: "Thursday at 4:00 PM UTC", description: "Hands-on session for beginners. We'll build an MNIST digit classifier from scratch using PyTorch nn.Module." },
      { id: "ml-basics-study", name: "ML Basics Study Session", time: "Monday at 3:00 PM UTC", description: "Peer study group reviewing loss functions, gradient descent, and basic optimization math." }
    ],
    insights: [
      "Top 95% contributor (Newcomer)",
      "Helped 0 beginners this week",
      "Looking to connect with a mentor"
    ],
    explainability: {
      identity_agent: "Identity Agent: Detected that Priya is a brand new member from a non-CS background. Her introductory post in #introductions highlights high enthusiasm for PyTorch but requires structured, non-intimidating beginner-level starting points.",
      discovery_agent: "Discovery Agent: Priya's profile focuses on machine learning and PyTorch. Matched her with PyTorch Study Group and ML Basics. Recommended beginner-friendly resources like 'Intro to PyTorch Notebooks' and 'Neural Networks from Scratch' rather than low-level CUDA optimization guides. Scheduled her for the PyTorch 101 workshop.",
      learning_agent: "Learning Agent: Designed a beginner-friendly path for Priya starting with interactive notebooks and basic concepts. Advised attending the hands-on PyTorch 101 event and connecting with a mentor to build structural confidence.",
      mentor_agent: "Mentor Agent: Matched Priya with Elena. Priya is a beginner looking to build neural networks in PyTorch, which is Elena's research specialty. Elena's patient, math-to-code learning approach matches Priya's needs."
    }
  },
  organizer: {
    metrics: {
      active_members_ratio: "83%",
      weekly_messages: 42,
      unanswered_threads: 1,
      at_risk_members: 1
    },
    health_summary: {
      ignored_newcomers: ["Priya"],
      unanswered_questions: ["Priya's post: 'Where should I start with PyTorch? I have some basic python knowledge...'"],
      inactive_members: ["Vikram (Inactive for 21 days)"],
      trending_topics: [
        "CUDA optimizations (Matrix multiplication, memory bank conflicts)", 
        "Rust lifetimes & compiler errors", 
        "PyTorch deep learning for beginners"
      ],
      explainability: "Community Health Agent: Scanned activity logs and timestamps. Flagged Priya as an ignored newcomer since she joined and posted in #introductions over 12 hours ago with zero replies. Detected Vikram as inactive based on lack of events in over 21 days. Trending topics extracted from recent message content in #gpu-computing and #rust."
    },
    insights: {
      suggested_events: [
        { title: "GPU Shared Memory & CUDA Optimizations AMA", reason: "High interest in CUDA bank conflicts from Rahul, plus upcoming AMA with Sarah. Expanding it to cover common kernel issues would engage intermediate coders." },
        { title: "Beginner PyTorch Study Session", reason: "Priya recently joined and requested PyTorch starting tips. Elena's colab notebooks could be used as material." }
      ],
      potential_mentors: [
        { name: "Rahul", reason: "Helped 6 beginners this week, is in the top 15% of contributors, and has demonstrated intermediate-to-advanced proficiency in CUDA and Rust. Highly eligible to become a systems programming mentor." }
      ],
      members_at_risk: [
        { name: "Vikram", reason: "Has been inactive for 21 days. Had moderate intermediate activity in PyTorch before going cold. Risk of churn is high." }
      ],
      suggested_actions: [
        { id: "action-1", action: "Reply to Priya's introduction in #introductions and introduce her to Elena.", agent: "Community Health Agent", reason: "Priya has been waiting for 12 hours with no response since joining. Churn rate rises by 40% if new members are ignored on day 1." },
        { id: "action-2", action: "Invite Rahul to join the mentorship program for Systems Programming.", agent: "Mentor Agent", reason: "Rahul meets all contribution and activity thresholds for mentorship and helped 6 beginners this week." },
        { id: "action-3", action: "Send an automated check-in message to Vikram with PyTorch optimization resources.", agent: "Community Health Agent", reason: "Vikram is a PyTorch enthusiast who has been inactive for 21 days. Sharing recent research scripts might re-engage him." }
      ],
      explainability: "Organizer Agent: Synthesized the findings of the Identity, Mentor, and Health agents. Crafted high-value, actionable tasks for community moderators to reduce churn, match mentors, and schedule targeted content to address the CUDA and PyTorch trending demands."
    }
  }
};

export default function Home() {
  const [screen, setScreen] = useState<"landing" | "demo">("landing");
  const [persona, setPersona] = useState<"rahul" | "priya" | "organizer">("rahul");
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [backendStatus, setBackendStatus] = useState<"connected" | "disconnected" | "checking">("checking");
  
  // Explainability drawer state
  const [showAllExplainability, setShowAllExplainability] = useState<boolean>(false);
  
  // Simulation states
  const [executedActions, setExecutedActions] = useState<Record<string, boolean>>({});
  const [executingActionId, setExecutingActionId] = useState<string | null>(null);
  const [welcomedMembers, setWelcomedMembers] = useState<Record<string, boolean>>({});
  const [invitedMentors, setInvitedMentors] = useState<Record<string, boolean>>({});
  const [reengagedMembers, setReengagedMembers] = useState<Record<string, boolean>>({});

  // Check backend health and load data
  useEffect(() => {
    const checkBackend = async () => {
      try {
        const res = await fetch("http://localhost:8000/");
        if (res.ok) {
          setBackendStatus("connected");
        } else {
          setBackendStatus("disconnected");
        }
      } catch (e) {
        setBackendStatus("disconnected");
      }
    };
    checkBackend();
  }, []);

  // Fetch data on persona/screen change
  useEffect(() => {
    if (screen !== "demo") return;
    
    const fetchData = async () => {
      setLoading(true);
      try {
        let endpoint = `http://localhost:8000/api/members/${persona}`;
        if (persona === "organizer") {
          endpoint = "http://localhost:8000/api/organizer";
        }
        
        const res = await fetch(endpoint);
        if (res.ok) {
          const json = await res.json();
          setData(json);
        } else {
          setData(FALLBACK_DATA[persona]);
        }
      } catch (e) {
        setData(FALLBACK_DATA[persona]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [persona, screen]);

  // Execute community operation action
  const handleExecuteAction = (actionId: string) => {
    setExecutingActionId(actionId);
    setTimeout(() => {
      setExecutedActions(prev => ({ ...prev, [actionId]: true }));
      setExecutingActionId(null);
    }, 1500);
  };

  return (
    <div className="flex-1 flex flex-col bg-mist text-carbon font-inter selection:bg-signal-orange selection:text-white min-h-screen">
      
      {/* HEADER / FLOATING NAV BAR */}
      <header className="w-full py-6 px-6 md:px-12 flex justify-between items-center max-w-[1200px] mx-auto z-40">
        
        {/* LOGO MARK: ventriloc with trailing orange swoosh */}
        <div className="flex items-center gap-2 cursor-pointer" onClick={() => setScreen("landing")}>
          <span className="font-polysans font-normal text-2xl tracking-[-0.02em] text-carbon relative flex items-center">
            ventriloc
            <svg className="w-6 h-6 text-signal-orange ml-0.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
              <path d="M3 17C9 17 15 13 21 5" />
            </svg>
          </span>
          <span className="text-[10px] bg-carbon text-white px-2 py-0.5 rounded-full font-mono tracking-wider font-semibold">
            COMMUNEOS
          </span>
        </div>

        {/* FLOATING NAV CAPSULE */}
        <div className="hidden md:flex items-center bg-white border border-slate/30 rounded-full px-4 py-1.5 shadow-[0_1px_3px_rgba(32,32,32,0.04)]">
          <button 
            onClick={() => setScreen("landing")} 
            className={`px-3 py-1 text-sm font-medium transition-all rounded-full ${screen === "landing" ? "text-signal-orange" : "text-carbon hover:text-graphite"}`}
          >
            Home
          </button>
          <button 
            onClick={() => setScreen("demo")} 
            className={`px-3 py-1 text-sm font-medium transition-all rounded-full ${screen === "demo" ? "text-signal-orange" : "text-carbon hover:text-graphite"}`}
          >
            Interactive Demo
          </button>
          <span className="w-px h-4 bg-slate/20 mx-2" />
          <div className="flex items-center gap-1.5 text-xs text-graphite">
            <span className={`w-2 h-2 rounded-full ${backendStatus === "connected" ? "bg-emerald-500" : "bg-amber-500"}`} />
            <span>API {backendStatus === "connected" ? "Connected" : "Offline"}</span>
          </div>
        </div>

        {/* LANGUAGE TOGGLE & PRIMARY CTA */}
        <div className="flex items-center gap-6">
          <span className="text-sm font-medium text-carbon hover:underline cursor-pointer">EN</span>
          {screen === "landing" ? (
            <button 
              onClick={() => setScreen("demo")}
              className="px-5 py-2.5 rounded-full bg-carbon text-white font-medium text-[15px] hover:bg-graphite active:scale-95 transition-all shadow-[0_1px_3px_rgba(32,32,32,0.04)] flex items-center gap-2"
            >
              Demo console
            </button>
          ) : (
            <button 
              onClick={() => setScreen("landing")}
              className="px-5 py-2.5 rounded-full border border-carbon text-carbon font-medium text-[15px] hover:bg-fog active:scale-95 transition-all"
            >
              Overview
            </button>
          )}
        </div>
      </header>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 flex flex-col">
        
        {/* ================= LANDING SCREEN ================= */}
        {screen === "landing" && (
          <div className="flex-1 flex flex-col">
            
            {/* HERO SECTION */}
            <section className="px-6 py-16 md:py-24 max-w-[1200px] mx-auto w-full grid grid-cols-1 md:grid-cols-12 gap-12 items-center">
              
              {/* Left Column: Headline & Action Buttons */}
              <div className="md:col-span-6 flex flex-col items-start text-left">
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-sienna-bronze/10 border border-sienna-bronze/20 text-sienna-bronze text-[11px] font-semibold uppercase tracking-wider mb-6">
                  <Sparkles className="w-3.5 h-3.5" /> Hackathon Track 2 Project
                </div>
                
                {/* HERO HEADLINE: Compressed Monument style (PolySans, tight line-height) */}
                <h1 className="font-polysans font-normal text-[52px] md:text-[66px] leading-[0.91] tracking-[-1.32px] text-carbon">
                  Traditional <br />
                  Communities <br />
                  Are Static.
                </h1>
                
                <p className="text-base md:text-lg text-graphite mt-6 leading-relaxed max-w-[480px]">
                  Everyone receives the same onboarding, channels, resources, events, and notifications. 
                  <strong className="text-carbon font-semibold mt-2 block">CommunityOS introduces an AI operating layer.</strong>
                  A team of specialized agents continuously personalizes the experience for every member while helping organizers automate community operations.
                </p>
                
                {/* CTA CLUSTER: Carbon-filled & outlined pill buttons */}
                <div className="flex flex-row gap-4 mt-8 w-full sm:w-auto">
                  <button 
                    onClick={() => setScreen("demo")}
                    className="px-6 py-3 rounded-full bg-carbon text-white font-medium text-[15px] hover:bg-graphite active:scale-95 transition-all shadow-[0_1px_3px_rgba(32,32,32,0.04)] flex items-center justify-center gap-2"
                  >
                    Interactive Demo <Play className="w-4 h-4 fill-white" />
                  </button>
                  <a 
                    href="#agents-info"
                    className="px-6 py-3 rounded-full border border-carbon text-carbon font-medium text-[15px] hover:bg-fog active:scale-95 transition-all flex items-center justify-center gap-2"
                  >
                    Meet the Agents
                  </a>
                </div>
              </div>
              
              {/* Right Column: Overlapping Dashboard Preview Cards */}
              <div className="md:col-span-6 relative w-full h-[320px] md:h-[400px] flex items-center">
                
                {/* Card 1: Back/Left */}
                <div className="absolute top-0 left-0 w-[72%] bg-white p-6 rounded-[8px] border border-chalk shadow-[0_1px_3px_rgba(32,32,32,0.04),0_4px_12px_rgba(32,32,32,0.03)] z-0">
                  <span className="text-[10px] text-slate uppercase font-bold tracking-widest block mb-1">Active Members Ratio</span>
                  <div className="font-polysans text-3xl font-normal text-carbon mb-4">83%</div>
                  
                  {/* Signal Orange Area Chart */}
                  <svg className="w-full h-24 overflow-visible" viewBox="0 0 300 100" preserveAspectRatio="none">
                    <defs>
                      <linearGradient id="orangeGrad1" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#ff682c" stopOpacity="0.2" />
                        <stop offset="100%" stopColor="#ff682c" stopOpacity="0.0" />
                      </linearGradient>
                    </defs>
                    <line x1="0" y1="25" x2="300" y2="25" stroke="#f5f5f5" strokeWidth="1" />
                    <line x1="0" y1="50" x2="300" y2="50" stroke="#f5f5f5" strokeWidth="1" />
                    <line x1="0" y1="75" x2="300" y2="75" stroke="#f5f5f5" strokeWidth="1" />
                    <path d="M 0 100 L 0 75 Q 60 40 120 70 T 240 30 T 300 15 L 300 100 Z" fill="url(#orangeGrad1)" />
                    <path d="M 0 75 Q 60 40 120 70 T 240 30 T 300 15" fill="none" stroke="#202020" strokeWidth="2.5" strokeLinecap="round" />
                  </svg>
                </div>

                {/* Card 2: Front/Right (Overlapping) */}
                <div className="absolute bottom-4 right-0 w-[68%] bg-white p-6 rounded-[8px] border border-chalk shadow-[0_2px_6px_rgba(32,32,32,0.06),0_8px_24px_rgba(32,32,32,0.04)] z-10 transition-transform hover:translate-y-[-4px]">
                  <div className="flex justify-between items-start mb-1">
                    <span className="text-[10px] text-slate uppercase font-bold tracking-widest block">GPU Kernel Optimization</span>
                    <span className="text-[10px] bg-sienna-bronze/10 text-sienna-bronze px-2 py-0.5 rounded-full font-medium">Active</span>
                  </div>
                  <div className="font-polysans text-2xl font-normal text-carbon mb-3">4.8x Velocity</div>
                  
                  {/* Signal Orange Area Chart */}
                  <svg className="w-full h-20 overflow-visible" viewBox="0 0 300 100" preserveAspectRatio="none">
                    <defs>
                      <linearGradient id="orangeGrad2" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#ff682c" stopOpacity="0.2" />
                        <stop offset="100%" stopColor="#ff682c" stopOpacity="0.0" />
                      </linearGradient>
                    </defs>
                    <path d="M 0 100 L 0 90 Q 50 85 100 50 T 200 35 T 300 5 L 300 100 Z" fill="url(#orangeGrad2)" />
                    <path d="M 0 90 Q 50 85 100 50 T 200 35 T 300 5" fill="none" stroke="#202020" strokeWidth="2" strokeLinecap="round" />
                  </svg>
                </div>
              </div>
            </section>

            {/* PARTNER LOGO STRIP (no background, sits on Mist canvas) */}
            <section className="w-full border-y border-chalk/80 py-10">
              <div className="max-w-[1200px] mx-auto px-6">
                <p className="text-[11px] font-bold text-graphite uppercase tracking-widest mb-6">
                  Trusted by 80+ partners
                </p>
                <div className="flex flex-wrap items-center gap-x-16 gap-y-6 opacity-75">
                  <span className="font-polysans font-bold text-lg text-slate tracking-wider">ABB</span>
                  <span className="font-sans font-extrabold text-xl text-slate tracking-tighter">OLYMEL</span>
                  <span className="font-serif italic font-bold text-xl text-slate">Cascades</span>
                  <span className="font-mono font-semibold text-lg text-slate">ANGELCARE</span>
                  <span className="font-polysans font-normal text-lg text-slate tracking-tight">LOGITECH</span>
                  <span className="font-sans font-light text-xl text-slate tracking-widest">NVIDIA</span>
                </div>
              </div>
            </section>

            {/* PLATFORM ARCHITECTURE GRAPHIC */}
            <section className="px-6 py-20 max-w-[1200px] mx-auto w-full text-center">
              <div className="mb-12">
                <span className="text-[11px] uppercase tracking-widest text-slate font-bold">Platform Integration Architecture</span>
                <h2 className="font-polysans text-3xl md:text-4px font-normal text-carbon mt-2">How CommunityOS Plugs In</h2>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                
                {/* Left: Core Platform */}
                <div className="p-8 rounded-[8px] bg-white border border-chalk flex flex-col items-center shadow-sm">
                  <div className="w-12 h-12 rounded-full bg-fog border border-chalk flex items-center justify-center mb-6">
                    <Users className="w-5 h-5 text-graphite" />
                  </div>
                  <h3 className="font-polysans font-normal text-lg text-carbon mb-2">Community Platform</h3>
                  <p className="text-xs text-graphite leading-relaxed">
                    Discord, Slack, Discourse, or custom portals feeding raw workspace logs and profiles.
                  </p>
                </div>
                
                {/* Middle: Agent Layer */}
                <div className="p-8 rounded-[8px] bg-white border border-t-4 border-t-signal-orange border-chalk flex flex-col items-center shadow-sm relative">
                  <div className="w-12 h-12 rounded-full bg-fog border border-chalk flex items-center justify-center mb-6">
                    <Cpu className="w-5 h-5 text-signal-orange" />
                  </div>
                  <h3 className="font-polysans font-normal text-lg text-carbon mb-2">AI Agent Layer</h3>
                  <p className="text-xs text-graphite leading-relaxed">
                    Agentfield control plane runs orchestrated LLMs that trace signals, activity thresholds, and query topics.
                  </p>
                </div>

                {/* Right: Output */}
                <div className="p-8 rounded-[8px] bg-white border border-chalk flex flex-col items-center shadow-sm">
                  <div className="w-12 h-12 rounded-full bg-fog border border-chalk flex items-center justify-center mb-6">
                    <Sparkles className="w-5 h-5 text-sienna-bronze" />
                  </div>
                  <h3 className="font-polysans font-normal text-lg text-carbon mb-2">Hyper-Personalization</h3>
                  <p className="text-xs text-graphite leading-relaxed">
                    Dynamic onboarding timelines, recommended checklists, calendar events, and direct mentor matchups.
                  </p>
                </div>
              </div>
            </section>

            {/* THE AGENT TEAM LIST */}
            <section id="agents-info" className="px-6 py-20 border-t border-chalk/80 max-w-[1200px] mx-auto w-full">
              <div className="text-center mb-16">
                <span className="text-[11px] uppercase tracking-widest text-slate font-bold">The Multi-Agent Core Network</span>
                <h2 className="font-polysans text-3xl md:text-4px font-normal text-carbon mt-2">
                  Meet the Orchestration Engine
                </h2>
                <p className="mt-3 text-sm text-graphite max-w-2xl mx-auto">
                  Instead of a single chat interface, CommunityOS employs six specialized agents that parse behaviors and automate operations.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                
                {/* 1. Identity Agent */}
                <div className="p-8 rounded-[8px] bg-white border border-chalk hover:border-slate/30 transition-all flex flex-col shadow-sm">
                  <div className="w-10 h-10 rounded-[8px] bg-fog border border-chalk text-carbon flex items-center justify-center mb-5">
                    <User className="w-4 h-4" />
                  </div>
                  <h3 className="font-polysans text-lg font-normal text-carbon mb-2">Identity Agent</h3>
                  <p className="text-xs text-graphite leading-relaxed">
                    Continuously observes chat logs, code queries, and intro posts. Formulates interests, skills, confidence level, and learning style.
                  </p>
                </div>

                {/* 2. Discovery Agent */}
                <div className="p-8 rounded-[8px] bg-white border border-chalk hover:border-slate/30 transition-all flex flex-col shadow-sm">
                  <div className="w-10 h-10 rounded-[8px] bg-fog border border-chalk text-carbon flex items-center justify-center mb-5">
                    <Search className="w-4 h-4" />
                  </div>
                  <h3 className="font-polysans text-lg font-normal text-carbon mb-2">Discovery Agent</h3>
                  <p className="text-xs text-graphite leading-relaxed">
                    Matches the dynamically built identity model with relevant channels, resources, templates, and events to deliver a custom community portal.
                  </p>
                </div>

                {/* 3. Learning Agent */}
                <div className="p-8 rounded-[8px] bg-white border border-chalk hover:border-slate/30 transition-all flex flex-col shadow-sm">
                  <div className="w-10 h-10 rounded-[8px] bg-fog border border-chalk text-carbon flex items-center justify-center mb-5">
                    <BookOpen className="w-4 h-4" />
                  </div>
                  <h3 className="font-polysans text-lg font-normal text-carbon mb-2">Learning Agent</h3>
                  <p className="text-xs text-graphite leading-relaxed">
                    Creates daily checklists and custom step-by-step roadmap paths. Adjusts technical difficulty depending on user progress and queries.
                  </p>
                </div>

                {/* 4. Mentor Agent */}
                <div className="p-8 rounded-[8px] bg-white border border-chalk hover:border-slate/30 transition-all flex flex-col shadow-sm">
                  <div className="w-10 h-10 rounded-[8px] bg-fog border border-chalk text-carbon flex items-center justify-center mb-5">
                    <Users className="w-4 h-4" />
                  </div>
                  <h3 className="font-polysans text-lg font-normal text-carbon mb-2">Mentor Agent</h3>
                  <p className="text-xs text-graphite leading-relaxed">
                    Examines profiles of expert members and rookies. Computes technical overlaps to recommend optimal mentor assignments.
                  </p>
                </div>

                {/* 5. Community Health Agent */}
                <div className="p-8 rounded-[8px] bg-white border border-chalk hover:border-slate/30 transition-all flex flex-col shadow-sm">
                  <div className="w-10 h-10 rounded-[8px] bg-fog border border-chalk text-carbon flex items-center justify-center mb-5">
                    <Activity className="w-4 h-4" />
                  </div>
                  <h3 className="font-polysans text-lg font-normal text-carbon mb-2">Community Health Agent</h3>
                  <p className="text-xs text-graphite leading-relaxed">
                    Surveys inactive periods, ignored newcomers, and unanswered technical posts to highlight potential operational risks and churn signs.
                  </p>
                </div>

                {/* 6. Organizer Agent */}
                <div className="p-8 rounded-[8px] bg-white border border-chalk hover:border-slate/30 transition-all flex flex-col shadow-sm">
                  <div className="w-10 h-10 rounded-[8px] bg-fog border border-chalk text-carbon flex items-center justify-center mb-5">
                    <ShieldCheck className="w-4 h-4" />
                  </div>
                  <h3 className="font-polysans text-lg font-normal text-carbon mb-2">Organizer Agent</h3>
                  <p className="text-xs text-graphite leading-relaxed">
                    Translates data diagnostics from Health Agent into concrete suggested events, mentor invites, churn rescues, and automated moderation actions.
                  </p>
                </div>

              </div>
            </section>
          </div>
        )}

        {/* ================= DEMO DASHBOARD SCREEN ================= */}
        {screen === "demo" && (
          <div className="flex-1 flex flex-col w-full max-w-[1200px] mx-auto px-6 py-8">
            
            {/* PERSONA CHANGER HEADER */}
            <div className="bg-white border border-chalk rounded-[8px] px-6 py-4 flex flex-col md:flex-row items-center justify-between gap-4 mb-6 shadow-sm">
              <div className="flex items-center gap-3">
                <span className="text-xs text-slate uppercase tracking-wider font-bold">Select Persona:</span>
                <div className="flex bg-fog p-1 rounded-full border border-chalk">
                  <button 
                    onClick={() => { setPersona("rahul"); setData(null); }}
                    className={`px-4 py-2 rounded-full text-xs font-semibold transition-all flex items-center gap-1.5 ${persona === "rahul" ? "bg-carbon text-white shadow-sm" : "text-graphite hover:text-carbon"}`}
                  >
                    <User className="w-3.5 h-3.5" /> Rahul (GPU)
                  </button>
                  <button 
                    onClick={() => { setPersona("priya"); setData(null); }}
                    className={`px-4 py-2 rounded-full text-xs font-semibold transition-all flex items-center gap-1.5 ${persona === "priya" ? "bg-carbon text-white shadow-sm" : "text-graphite hover:text-carbon"}`}
                  >
                    <User className="w-3.5 h-3.5" /> Priya (AI Rookie)
                  </button>
                  <button 
                    onClick={() => { setPersona("organizer"); setData(null); }}
                    className={`px-4 py-2 rounded-full text-xs font-semibold transition-all flex items-center gap-1.5 ${persona === "organizer" ? "bg-carbon text-white shadow-sm" : "text-graphite hover:text-carbon"}`}
                  >
                    <ShieldCheck className="w-3.5 h-3.5" /> Organizer Console
                  </button>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={() => setShowAllExplainability(!showAllExplainability)}
                  className="px-4 py-2 rounded-full border border-slate text-xs font-semibold text-carbon hover:bg-fog active:scale-95 transition-all flex items-center gap-1.5 bg-white shadow-sm"
                >
                  <Sparkles className="w-3.5 h-3.5 text-signal-orange" /> {showAllExplainability ? "Hide AI Reasoning" : "Why am I seeing this?"}
                </button>
                
                <button
                  onClick={() => { setData(null); }}
                  className="p-2 rounded-full border border-chalk hover:bg-fog text-slate hover:text-carbon transition-all"
                  title="Reload Agent Reasoning"
                >
                  <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin text-signal-orange" : ""}`} />
                </button>
              </div>
            </div>

            {/* EXPLAINABILITY DRAWER / SESSION DIAGNOSTICS */}
            {showAllExplainability && data && (
              <div className="bg-[#f5f5f5] border border-slate/30 rounded-[8px] p-6 mb-8 shadow-sm">
                <div className="flex items-center gap-2 mb-4">
                  <Terminal className="w-4 h-4 text-carbon" />
                  <h3 className="text-xs uppercase font-bold text-carbon tracking-widest font-mono">Agentfield Control Plane --- Diagnostics Trace</h3>
                </div>

                {persona !== "organizer" ? (
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    
                    {/* Identity agent explanation */}
                    <div className="p-4 rounded-[8px] bg-white border border-chalk">
                      <div className="flex items-center gap-2 mb-2 pb-2 border-b border-chalk">
                        <User className="w-4 h-4 text-sienna-bronze" />
                        <span className="text-xs font-bold text-carbon font-mono">Identity Agent</span>
                      </div>
                      <p className="text-xs text-graphite leading-relaxed">{data.explainability?.identity_agent}</p>
                    </div>

                    {/* Discovery Agent explanation */}
                    <div className="p-4 rounded-[8px] bg-white border border-chalk">
                      <div className="flex items-center gap-2 mb-2 pb-2 border-b border-chalk">
                        <Search className="w-4 h-4 text-sienna-bronze" />
                        <span className="text-xs font-bold text-carbon font-mono">Discovery Agent</span>
                      </div>
                      <p className="text-xs text-graphite leading-relaxed">{data.explainability?.discovery_agent}</p>
                    </div>

                    {/* Learning Agent explanation */}
                    <div className="p-4 rounded-[8px] bg-white border border-chalk">
                      <div className="flex items-center gap-2 mb-2 pb-2 border-b border-chalk">
                        <BookOpen className="w-4 h-4 text-sienna-bronze" />
                        <span className="text-xs font-bold text-carbon font-mono">Learning Agent</span>
                      </div>
                      <p className="text-xs text-graphite leading-relaxed">{data.explainability?.learning_agent}</p>
                    </div>

                    {/* Mentor Agent explanation */}
                    <div className="p-4 rounded-[8px] bg-white border border-chalk">
                      <div className="flex items-center gap-2 mb-2 pb-2 border-b border-chalk">
                        <Users className="w-4 h-4 text-sienna-bronze" />
                        <span className="text-xs font-bold text-carbon font-mono">Mentor Agent</span>
                      </div>
                      <p className="text-xs text-graphite leading-relaxed">{data.explainability?.mentor_agent}</p>
                    </div>

                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    
                    {/* Health agent explanation */}
                    <div className="p-4 rounded-[8px] bg-white border border-chalk">
                      <div className="flex items-center gap-2 mb-2 pb-2 border-b border-chalk">
                        <Activity className="w-4 h-4 text-signal-orange" />
                        <span className="text-xs font-bold text-carbon font-mono">Community Health Agent</span>
                      </div>
                      <p className="text-xs text-graphite leading-relaxed">{data.health_summary?.explainability}</p>
                    </div>

                    {/* Organizer Agent explanation */}
                    <div className="p-4 rounded-[8px] bg-white border border-chalk">
                      <div className="flex items-center gap-2 mb-2 pb-2 border-b border-chalk">
                        <ShieldCheck className="w-4 h-4 text-signal-orange" />
                        <span className="text-xs font-bold text-carbon font-mono">Organizer Agent</span>
                      </div>
                      <p className="text-xs text-graphite leading-relaxed">{data.insights?.explainability}</p>
                    </div>

                  </div>
                )}
              </div>
            )}

            {/* DASHBOARD CARD CONTAINER WITH SIDEBAR & CONTENT */}
            {loading ? (
              <div className="bg-white rounded-[8px] border border-chalk p-24 flex flex-col items-center justify-center gap-4 shadow-sm min-h-[500px]">
                <RefreshCw className="w-8 h-8 text-signal-orange animate-spin" />
                <div className="text-xs font-mono text-slate">AgentField invoking LLM reasoners...</div>
              </div>
            ) : data ? (
              <div className="bg-white rounded-[8px] border border-chalk shadow-[0_1px_3px_rgba(32,32,32,0.04),0_4px_12px_rgba(32,32,32,0.03)] flex flex-col md:flex-row min-h-[600px] overflow-hidden">
                
                {/* 200px WIDTH LEFT SIDEBAR */}
                <aside className="w-full md:w-[220px] shrink-0 bg-fog border-r border-chalk p-6 flex flex-col gap-8">
                  
                  {/* Navigation links */}
                  <div>
                    <span className="text-[10px] font-bold text-slate uppercase tracking-widest block mb-4">Dashboard Nav</span>
                    <nav className="flex flex-col gap-2">
                      <button className="flex items-center justify-between text-left text-xs font-semibold text-carbon bg-white border border-chalk px-3 py-2 rounded-[6px] shadow-sm">
                        <span>Overview</span>
                        <span className="w-1.5 h-1.5 rounded-full bg-signal-orange" />
                      </button>
                      <button className="flex items-center text-left text-xs font-medium text-graphite hover:text-carbon px-3 py-2 rounded-[6px] transition-all">
                        <span>Roadmaps</span>
                      </button>
                      <button className="flex items-center text-left text-xs font-medium text-graphite hover:text-carbon px-3 py-2 rounded-[6px] transition-all">
                        <span>Mentors</span>
                      </button>
                      <button className="flex items-center text-left text-xs font-medium text-graphite hover:text-carbon px-3 py-2 rounded-[6px] transition-all">
                        <span>Analytics</span>
                      </button>
                    </nav>
                  </div>

                  {/* Filters section */}
                  <div>
                    <span className="text-[10px] font-bold text-slate uppercase tracking-widest block mb-4">Filter Context</span>
                    
                    {persona !== "organizer" ? (
                      <div className="space-y-4">
                        <div>
                          <label className="text-[11px] font-semibold text-graphite block mb-1.5 flex items-center justify-between">
                            Focus Topic <ChevronDown className="w-3 h-3 text-slate" />
                          </label>
                          <select className="w-full text-xs bg-white border border-chalk rounded-[6px] px-2 py-1.5 text-carbon outline-none" defaultValue="all">
                            <option value="all">All Topics</option>
                            <option value="gpu">GPU Computing</option>
                            <option value="systems">Systems Programming</option>
                          </select>
                        </div>
                        <div>
                          <label className="text-[11px] font-semibold text-graphite block mb-1.5 flex items-center justify-between">
                            Resources <ChevronDown className="w-3 h-3 text-slate" />
                          </label>
                          <select className="w-full text-xs bg-white border border-chalk rounded-[6px] px-2 py-1.5 text-carbon outline-none" defaultValue="guides">
                            <option value="guides">Guides & Books</option>
                            <option value="code">Code Snippets</option>
                          </select>
                        </div>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        <div>
                          <label className="text-[11px] font-semibold text-graphite block mb-1.5 flex items-center justify-between">
                            Risk Segment <ChevronDown className="w-3 h-3 text-slate" />
                          </label>
                          <select className="w-full text-xs bg-white border border-chalk rounded-[6px] px-2 py-1.5 text-carbon outline-none" defaultValue="high">
                            <option value="high">High Risk</option>
                            <option value="medium">Medium Risk</option>
                            <option value="low">Low Risk</option>
                          </select>
                        </div>
                        <div>
                          <label className="text-[11px] font-semibold text-graphite block mb-1.5 flex items-center justify-between">
                            Action Queue <ChevronDown className="w-3 h-3 text-slate" />
                          </label>
                          <select className="w-full text-xs bg-white border border-chalk rounded-[6px] px-2 py-1.5 text-carbon outline-none" defaultValue="moderation">
                            <option value="moderation">Moderator Tasks</option>
                            <option value="events">Event Triggers</option>
                          </select>
                        </div>
                      </div>
                    )}
                  </div>
                </aside>

                {/* MAIN CONTENT AREA */}
                <div className="flex-1 p-8 bg-white overflow-y-auto">
                  
                  {/* ================= PERSONA: MEMBER VIEW ================= */}
                  {persona !== "organizer" && (
                    <div className="space-y-8">
                      
                      {/* Welcome Banner (Parchment background with signal orange left border) */}
                      <div className="p-6 rounded-[8px] bg-fog border-l-4 border-l-signal-orange border-y border-r border-chalk relative overflow-hidden">
                        <h2 className="font-polysans text-2xl font-normal text-carbon mb-2">Welcome back, {data.name}!</h2>
                        <p className="text-xs text-graphite leading-relaxed max-w-2xl">{data.welcome_message}</p>
                        
                        {/* Skills Model */}
                        <div className="mt-4 flex flex-wrap items-center gap-2">
                          <span className="text-[10px] font-bold text-slate uppercase tracking-wider">Detected Skills:</span>
                          <div className="flex flex-wrap gap-1">
                            {data.skills?.map((skill: string) => (
                              <span key={skill} className="px-2.5 py-0.5 rounded-full bg-white border border-chalk text-[10px] font-medium text-carbon shadow-sm">
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* STATS TILES (Metric KPI Cards) */}
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                        
                        {/* Stat 1 */}
                        <div className="p-6 rounded-[8px] bg-white border border-chalk shadow-sm flex flex-col justify-between">
                          <div>
                            <span className="text-[11px] font-medium text-slate block mb-1">Rank Status</span>
                            <div className="font-polysans text-3xl font-normal text-carbon">{persona === "rahul" ? "Top 15%" : "Top 95%"}</div>
                          </div>
                          <div className="mt-4 flex items-center gap-1 text-[11px] text-[#2e7d32] font-semibold bg-emerald-500/10 px-2 py-0.5 rounded-full w-fit">
                            <TrendingUp className="w-3 h-3" /> {persona === "rahul" ? "Systems Leader" : "Newcomer"}
                          </div>
                        </div>

                        {/* Stat 2 */}
                        <div className="p-6 rounded-[8px] bg-white border border-chalk shadow-sm flex flex-col justify-between">
                          <div>
                            <span className="text-[11px] font-medium text-slate block mb-1">Helpers Thread</span>
                            <div className="font-polysans text-3xl font-normal text-carbon">{persona === "rahul" ? "6 members" : "0 members"}</div>
                          </div>
                          <div className="mt-4 flex items-center gap-1 text-[11px] text-graphite bg-fog px-2 py-0.5 rounded-full w-fit">
                            {persona === "rahul" ? "Helped this week" : "Needs mentorship"}
                          </div>
                        </div>

                        {/* Stat 3 */}
                        <div className="p-6 rounded-[8px] bg-white border border-chalk shadow-sm flex flex-col justify-between">
                          <div>
                            <span className="text-[11px] font-medium text-slate block mb-1">Mentor Matching</span>
                            <div className="font-polysans text-3xl font-normal text-carbon">{persona === "rahul" ? "Matched" : "Assigned"}</div>
                          </div>
                          <div className="mt-4 flex items-center gap-1 text-[11px] text-sienna-bronze bg-sienna-bronze/10 px-2 py-0.5 rounded-full w-fit">
                            {persona === "rahul" ? "Sarah (Nvidia)" : "Elena (Researcher)"}
                          </div>
                        </div>

                      </div>

                      {/* PRIORITIES & TIMELINE ROADMAP */}
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        
                        {/* Priorities card */}
                        <div className="p-6 rounded-[8px] bg-white border border-chalk shadow-sm">
                          <h3 className="font-polysans text-base font-normal text-carbon mb-4 flex items-center gap-2">
                            <CheckSquare className="w-4 h-4 text-signal-orange" /> Priorities Checklist
                          </h3>
                          <ul className="space-y-4">
                            {data.priorities?.map((priority: string, i: number) => (
                              <li key={i} className="flex gap-3 text-xs text-graphite items-start">
                                <span className="w-5 h-5 rounded-full bg-fog border border-chalk flex items-center justify-center text-[10px] text-slate font-mono shrink-0 mt-0.5">{i+1}</span>
                                <span className="flex-1 leading-normal">{priority}</span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Timeline Roadmap */}
                        <div className="p-6 rounded-[8px] bg-white border border-chalk shadow-sm">
                          <h3 className="font-polysans text-base font-normal text-carbon mb-4 flex items-center gap-2">
                            <BookOpen className="w-4 h-4 text-signal-orange" /> Pathways Milestones
                          </h3>
                          <div className="relative border-l border-chalk ml-3 pl-6 space-y-4">
                            {persona === "rahul" ? (
                              <>
                                <div className="relative">
                                  <div className="absolute -left-[30px] top-1 w-2.5 h-2.5 rounded-full bg-signal-orange" />
                                  <h4 className="text-xs font-semibold text-carbon">Analyze shared memory bank conflicts</h4>
                                  <p className="text-[11px] text-slate mt-0.5">Explore Matrix Multiplication stride configurations.</p>
                                </div>
                                <div className="relative">
                                  <div className="absolute -left-[30px] top-1 w-2.5 h-2.5 rounded-full bg-chalk border border-slate" />
                                  <h4 className="text-xs font-semibold text-graphite">Implement memory padding layouts</h4>
                                  <p className="text-[11px] text-slate mt-0.5">Profile CUDA throughput speedups.</p>
                                </div>
                                <div className="relative">
                                  <div className="absolute -left-[30px] top-1 w-2.5 h-2.5 rounded-full bg-chalk border border-slate" />
                                  <h4 className="text-xs font-semibold text-graphite">Schedule profile review with Sarah</h4>
                                  <p className="text-[11px] text-slate mt-0.5">Share code repository in GPU Computing AMA.</p>
                                </div>
                              </>
                            ) : (
                              <>
                                <div className="relative">
                                  <div className="absolute -left-[30px] top-1 w-2.5 h-2.5 rounded-full bg-signal-orange" />
                                  <h4 className="text-xs font-semibold text-carbon">Run PyTorch interactive notebooks</h4>
                                  <p className="text-[11px] text-slate mt-0.5">Load autograd tensors and basic training loops.</p>
                                </div>
                                <div className="relative">
                                  <div className="absolute -left-[30px] top-1 w-2.5 h-2.5 rounded-full bg-chalk border border-slate" />
                                  <h4 className="text-xs font-semibold text-graphite">Build MNIST Digit Classifier</h4>
                                  <p className="text-[11px] text-slate mt-0.5">Attend PyTorch 101 workshop to deploy the model.</p>
                                </div>
                                <div className="relative">
                                  <div className="absolute -left-[30px] top-1 w-2.5 h-2.5 rounded-full bg-chalk border border-slate" />
                                  <h4 className="text-xs font-semibold text-graphite">Connect with mentor Elena</h4>
                                  <p className="text-[11px] text-slate mt-0.5">Ask questions about neural networks mathematical fundamentals.</p>
                                </div>
                              </>
                            )}
                          </div>
                        </div>

                      </div>

                      {/* AREA CHART CARD: Code & Activity Velocity */}
                      <div className="p-6 rounded-[8px] bg-white border border-chalk shadow-sm">
                        <h4 className="text-xs font-bold text-slate uppercase tracking-wider mb-4">Member Activity Profile</h4>
                        <div className="font-polysans text-2xl font-normal text-carbon mb-4">Weekly Signal Velocity</div>
                        
                        {/* Signal Orange Area Chart */}
                        <svg className="w-full h-32 overflow-visible" viewBox="0 0 600 100" preserveAspectRatio="none">
                          <defs>
                            <linearGradient id="orangeGradMain" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="0%" stopColor="#ff682c" stopOpacity="0.18" />
                              <stop offset="100%" stopColor="#ff682c" stopOpacity="0.0" />
                            </linearGradient>
                          </defs>
                          <line x1="0" y1="20" x2="600" y2="20" stroke="#f5f5f5" strokeWidth="1" />
                          <line x1="0" y1="50" x2="600" y2="50" stroke="#f5f5f5" strokeWidth="1" />
                          <line x1="0" y1="80" x2="600" y2="80" stroke="#f5f5f5" strokeWidth="1" />
                          
                          <path d="M 0 100 L 0 75 Q 100 85 200 45 T 400 30 T 600 8 L 600 100 Z" fill="url(#orangeGradMain)" />
                          <path d="M 0 75 Q 100 85 200 45 T 400 30 T 600 8" fill="none" stroke="#202020" strokeWidth="2.2" strokeLinecap="round" />
                        </svg>
                        
                        <div className="flex justify-between text-[10px] text-slate mt-2">
                          <span>Monday</span>
                          <span>Wednesday</span>
                          <span>Friday</span>
                          <span>Sunday</span>
                        </div>
                      </div>

                      {/* RECOMMENDATIONS (RESOURCES, EVENTS, MENTORS) */}
                      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        
                        {/* Resources */}
                        <div className="lg:col-span-2 space-y-4">
                          <h4 className="text-[11px] font-bold text-slate uppercase tracking-widest flex items-center gap-1">
                            <BookOpen className="w-3.5 h-3.5 text-signal-orange" /> Suggested Guides
                          </h4>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            {data.resources?.map((res: any) => (
                              <div key={res.id} className="p-5 rounded-[8px] bg-white border border-chalk hover:border-slate/40 flex flex-col justify-between shadow-sm">
                                <div>
                                  <h5 className="text-xs font-semibold text-carbon">{res.name}</h5>
                                  <p className="text-[11px] text-graphite mt-1 leading-relaxed">{res.description}</p>
                                </div>
                                <div className="mt-3 flex justify-end">
                                  <a href={res.url} className="text-[11px] text-signal-orange hover:underline inline-flex items-center gap-0.5 font-semibold">
                                    Read Guide <ChevronRight className="w-3 h-3" />
                                  </a>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Events list */}
                        <div className="space-y-4">
                          <h4 className="text-[11px] font-bold text-slate uppercase tracking-widest flex items-center gap-1">
                            <Calendar className="w-3.5 h-3.5 text-signal-orange" /> Recommended Events
                          </h4>
                          <div className="space-y-3">
                            {data.events?.map((evt: any) => (
                              <div key={evt.id} className="p-4 rounded-[8px] bg-white border border-chalk shadow-sm">
                                <div className="flex items-start justify-between gap-2">
                                  <h5 className="text-xs font-semibold text-carbon leading-snug">{evt.name}</h5>
                                  <span className="text-[9px] px-2 py-0.5 rounded-full bg-sienna-bronze/10 text-sienna-bronze border border-sienna-bronze/20 shrink-0 font-medium font-mono">
                                    {evt.time.split(" at ")[0]}
                                  </span>
                                </div>
                                <p className="text-[10px] text-graphite mt-1.5 leading-relaxed">{evt.description}</p>
                              </div>
                            ))}
                          </div>
                        </div>

                      </div>

                      {/* MENTOR MATCH & CHANNELS */}
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        
                        {/* Mentor card */}
                        <div className="p-6 rounded-[8px] bg-fog border border-chalk shadow-sm flex flex-col justify-between">
                          <div>
                            <span className="text-[10px] font-bold text-slate uppercase tracking-widest block mb-4">Recommended Mentor</span>
                            <div className="flex items-center gap-3">
                              <div className="w-12 h-12 rounded-full bg-white border border-chalk flex items-center justify-center font-bold text-carbon text-lg">
                                {data.recommended_mentor?.name[0]}
                              </div>
                              <div>
                                <h4 className="font-bold text-carbon text-sm">{data.recommended_mentor?.name}</h4>
                                <p className="text-xs text-graphite">{data.recommended_mentor?.role}</p>
                              </div>
                            </div>
                            
                            <div className="mt-4 p-3.5 rounded-[8px] bg-white border border-chalk text-[11px] text-graphite leading-relaxed">
                              <strong className="text-carbon block mb-1">Agent Matching Reasoning:</strong>
                              {data.recommended_mentor?.overlap_reason}
                            </div>
                          </div>

                          <button className="w-full mt-4 py-2 px-4 rounded-full bg-carbon hover:bg-graphite text-white text-xs font-semibold transition-all active:scale-95 flex items-center justify-center gap-1.5 shadow-sm">
                            <MessageSquare className="w-3.5 h-3.5" /> Direct Message {data.recommended_mentor?.name}
                          </button>
                        </div>

                        {/* Matched channels list */}
                        <div className="p-6 rounded-[8px] bg-white border border-chalk shadow-sm">
                          <span className="text-[10px] font-bold text-slate uppercase tracking-widest block mb-4">Matched Workspace Channels</span>
                          
                          <div className="space-y-4">
                            <div>
                              <span className="text-[9px] text-slate font-bold uppercase tracking-wider block mb-2">High Affinity (Unlocked)</span>
                              <div className="space-y-1.5">
                                {data.communities?.recommended?.map((com: any) => (
                                  <div key={com.id} className="p-3 rounded-[6px] bg-fog border border-chalk flex items-center justify-between hover:border-slate/40 transition-all cursor-pointer">
                                    <span className="text-xs font-medium text-carbon"># {com.name}</span>
                                    <ChevronRight className="w-3.5 h-3.5 text-slate" />
                                  </div>
                                ))}
                              </div>
                            </div>

                            <div>
                              <span className="text-[9px] text-slate font-bold uppercase tracking-wider block mb-2">Low Priority (Archived)</span>
                              <div className="space-y-1.5">
                                {data.communities?.lower_priority?.map((com: any) => (
                                  <div key={com.id} className="p-3 rounded-[6px] bg-white border border-chalk flex items-center justify-between opacity-50 hover:opacity-100 transition-all cursor-not-allowed">
                                    <span className="text-xs font-medium text-graphite"># {com.name}</span>
                                    <Lock className="w-3.5 h-3.5 text-slate" />
                                  </div>
                                ))}
                              </div>
                            </div>
                          </div>
                        </div>

                      </div>

                    </div>
                  )}

                  {/* ================= PERSONA: ORGANIZER VIEW ================= */}
                  {persona === "organizer" && (
                    <div className="space-y-8">
                      
                      {/* STATS OVERVIEW GRID */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                        
                        {/* Card 1 */}
                        <div className="p-6 rounded-[8px] bg-white border border-chalk shadow-sm flex items-center gap-4">
                          <div className="w-10 h-10 rounded-full bg-fog border border-chalk flex items-center justify-center shrink-0">
                            <Activity className="w-5 h-5 text-signal-orange" />
                          </div>
                          <div>
                            <span className="text-[9px] text-slate block uppercase font-bold tracking-wider">Health Score</span>
                            <span className="font-polysans text-2xl font-normal text-carbon">
                              {data.metrics?.active_members_ratio === "83%" ? "92%" : "88%"}
                            </span>
                          </div>
                        </div>

                        {/* Card 2 */}
                        <div className="p-6 rounded-[8px] bg-white border border-chalk shadow-sm flex items-center gap-4">
                          <div className="w-10 h-10 rounded-full bg-fog border border-chalk flex items-center justify-center shrink-0">
                            <Users className="w-5 h-5 text-carbon" />
                          </div>
                          <div>
                            <span className="text-[9px] text-slate block uppercase font-bold tracking-wider">Active Members</span>
                            <span className="font-polysans text-2xl font-normal text-carbon">{data.metrics?.active_members_ratio}</span>
                          </div>
                        </div>

                        {/* Card 3 */}
                        <div className="p-6 rounded-[8px] bg-white border border-chalk shadow-sm flex items-center gap-4">
                          <div className="w-10 h-10 rounded-full bg-fog border border-chalk flex items-center justify-center shrink-0">
                            <MessageSquare className="w-5 h-5 text-carbon" />
                          </div>
                          <div>
                            <span className="text-[9px] text-slate block uppercase font-bold tracking-wider">Weekly Messages</span>
                            <span className="font-polysans text-2xl font-normal text-carbon">{data.metrics?.weekly_messages}</span>
                          </div>
                        </div>

                        {/* Card 4 */}
                        <div className="p-6 rounded-[8px] bg-white border border-chalk shadow-sm flex items-center gap-4">
                          <div className="w-10 h-10 rounded-full bg-fog border border-chalk flex items-center justify-center shrink-0">
                            <AlertTriangle className="w-5 h-5 text-signal-orange" />
                          </div>
                          <div>
                            <span className="text-[9px] text-slate block uppercase font-bold tracking-wider">Unanswered</span>
                            <span className="font-polysans text-2xl font-normal text-carbon">{data.metrics?.unanswered_threads}</span>
                          </div>
                        </div>

                      </div>

                      {/* AI SUGGESTED ACTIONS (Main Ops Console widget) */}
                      <div className="p-6 rounded-[8px] bg-fog border border-chalk shadow-sm">
                        <div className="flex items-center gap-2 mb-6">
                          <Cpu className="w-5 h-5 text-signal-orange animate-pulse" />
                          <h3 className="font-polysans text-base font-normal text-carbon">AI Suggested Automations</h3>
                        </div>

                        <div className="space-y-4">
                          {data.insights?.suggested_actions?.map((act: any) => (
                            <div 
                              key={act.id}
                              className={`p-5 rounded-[8px] border transition-all flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white ${
                                executedActions[act.id] ? "border-emerald-500/30 opacity-75" : "border-chalk"
                              }`}
                            >
                              <div className="space-y-1">
                                <div className="flex flex-wrap items-center gap-2">
                                  <span className={`text-[9px] font-mono px-2 py-0.5 rounded font-semibold tracking-wider ${
                                    act.agent.includes("Health") 
                                      ? "bg-amber-500/10 text-amber-600 border border-amber-500/20" 
                                      : "bg-sienna-bronze/10 text-sienna-bronze border border-sienna-bronze/20"
                                  }`}>
                                    {act.agent}
                                  </span>
                                  <span className="text-[9px] font-mono px-2 py-0.5 rounded bg-carbon text-white font-semibold tracking-wider">
                                    HIGH PRIORITY
                                  </span>
                                </div>
                                <h4 className={`text-xs font-bold text-carbon ${executedActions[act.id] ? "line-through text-slate" : ""}`}>
                                  {act.action}
                                </h4>
                                <p className="text-[11px] text-graphite leading-relaxed">{act.reason}</p>
                              </div>

                              <div className="shrink-0 flex items-center">
                                {executedActions[act.id] ? (
                                  <span className="text-xs text-emerald-600 font-semibold flex items-center gap-1 px-3.5 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
                                    <Check className="w-3.5 h-3.5" /> Flow Triggered
                                  </span>
                                ) : (
                                  <button
                                    onClick={() => handleExecuteAction(act.id)}
                                    disabled={executingActionId === act.id}
                                    className="px-4 py-2 rounded-full bg-carbon hover:bg-graphite disabled:bg-chalk disabled:text-slate text-white text-xs font-bold transition-all flex items-center gap-1.5 shadow-sm"
                                  >
                                    {executingActionId === act.id ? (
                                      <>
                                        <RefreshCw className="w-3 h-3 animate-spin" /> Invoking...
                                      </>
                                    ) : (
                                      <>
                                        <Play className="w-3 h-3 fill-white" /> Run Agent Flow
                                      </>
                                    )}
                                  </button>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* MAIN GRID BLOCK: Rescue, Trends, Funnel, Progress */}
                      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        
                        {/* Left & Middle Column */}
                        <div className="lg:col-span-2 space-y-8">
                          
                          {/* Member Rescue pipeline */}
                          <div className="p-6 rounded-[8px] bg-white border border-chalk shadow-sm">
                            <h3 className="font-polysans text-base font-normal text-carbon mb-4 flex items-center gap-2">
                              <AlertCircle className="w-4 h-4 text-signal-orange" /> Member Rescue Pipeline
                            </h3>
                            <div className="space-y-4">
                              {data.health_summary?.ignored_newcomers?.map((newcomer: string, idx: number) => (
                                <div key={idx} className="p-4 rounded-[8px] bg-fog border border-chalk flex items-center justify-between gap-4">
                                  <div className="space-y-1">
                                    <div className="flex items-center gap-2">
                                      <span className="w-2 h-2 rounded-full bg-signal-orange animate-pulse" />
                                      <h4 className="text-xs font-bold text-carbon">{newcomer}</h4>
                                    </div>
                                    <p className="text-[11px] text-graphite">Bio: Non-CS learner looking to build her first neural network in PyTorch.</p>
                                    <span className="text-[10px] text-signal-orange block font-mono">12 hours since introduction in #introductions. 0 replies.</span>
                                  </div>

                                  <button 
                                    onClick={() => setWelcomedMembers(prev => ({ ...prev, [newcomer]: true }))}
                                    disabled={welcomedMembers[newcomer]}
                                    className="px-3.5 py-1.5 rounded-full bg-white border border-slate text-xs font-bold text-carbon disabled:text-emerald-600 disabled:bg-emerald-500/10 disabled:border-emerald-500/20 shrink-0 transition-all shadow-sm"
                                  >
                                    {welcomedMembers[newcomer] ? (
                                      <span className="flex items-center gap-1"><Check className="w-3 h-3" /> Welcomed</span>
                                    ) : (
                                      "Welcome Her"
                                    )}
                                  </button>
                                </div>
                              ))}
                            </div>
                          </div>

                          {/* Funnel & Donut charts */}
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            
                            {/* Funnel Visualization */}
                            <div className="space-y-4 bg-white p-6 rounded-[8px] border border-chalk shadow-sm">
                              <h4 className="text-xs font-bold text-slate uppercase tracking-wider">Conversion Funnel</h4>
                              <div className="flex items-center gap-1.5 h-20">
                                {/* Stage 1 */}
                                <div className="flex-1 h-full bg-[#ff682c] rounded-l-[4px] relative flex flex-col justify-center items-center text-white px-2">
                                  <span className="font-polysans text-sm font-semibold">100%</span>
                                  <span className="text-[8px] opacity-90 font-medium uppercase font-mono">Visitor</span>
                                </div>
                                {/* Stage 2 */}
                                <div className="flex-1 h-full bg-[#ff682c]/75 relative flex flex-col justify-center items-center text-white px-2">
                                  <span className="font-polysans text-sm font-semibold">68%</span>
                                  <span className="text-[8px] opacity-90 font-medium uppercase font-mono">Sign-up</span>
                                </div>
                                {/* Stage 3 */}
                                <div className="flex-1 h-full bg-[#ff682c]/45 relative flex flex-col justify-center items-center text-carbon px-2">
                                  <span className="font-polysans text-sm font-semibold">42%</span>
                                  <span className="text-[8px] opacity-90 font-medium uppercase font-mono">Active</span>
                                </div>
                                {/* Stage 4 */}
                                <div className="flex-1 h-full border border-[#ff682c]/40 rounded-r-[4px] relative flex flex-col justify-center items-center text-carbon px-2">
                                  <span className="font-polysans text-sm font-semibold">12%</span>
                                  <span className="text-[8px] opacity-90 font-medium uppercase font-mono">Sub</span>
                                </div>
                              </div>
                            </div>

                            {/* Donut/Progress Chart */}
                            <div className="p-6 rounded-[8px] bg-white border border-chalk shadow-sm flex flex-col items-center">
                              <h4 className="text-xs font-bold text-slate uppercase tracking-wider mb-4 self-start">Member Retention</h4>
                              <div className="relative w-24 h-24 flex items-center justify-center">
                                <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                                  <path
                                    className="text-fog"
                                    strokeWidth="3.5"
                                    stroke="currentColor"
                                    fill="none"
                                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                                  />
                                  <path
                                    className="text-signal-orange"
                                    strokeWidth="3.5"
                                    strokeDasharray="83, 100"
                                    strokeLinecap="round"
                                    stroke="currentColor"
                                    fill="none"
                                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                                  />
                                </svg>
                                <div className="absolute font-polysans text-lg font-normal text-carbon">83%</div>
                              </div>
                              <div className="mt-4 flex gap-4 text-[10px]">
                                <div className="flex items-center gap-1">
                                  <span className="w-2 h-2 rounded-full bg-signal-orange" />
                                  <span className="text-graphite">Active</span>
                                </div>
                                <div className="flex items-center gap-1">
                                  <span className="w-2 h-2 rounded-full bg-fog border border-chalk" />
                                  <span className="text-graphite">Inactive</span>
                                </div>
                              </div>
                            </div>

                          </div>

                          {/* Proposed Events list */}
                          <div className="p-6 rounded-[8px] bg-white border border-chalk shadow-sm">
                            <h3 className="font-polysans text-base font-normal text-carbon mb-4 flex items-center gap-2">
                              <Calendar className="w-4 h-4 text-sienna-bronze" /> AI Suggested Events (Based on Trends)
                            </h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                              {data.insights?.suggested_events?.map((evt: any, i: number) => (
                                <div key={i} className="p-5 rounded-[8px] bg-fog border border-chalk flex flex-col justify-between">
                                  <div>
                                    <span className="text-[9px] font-mono bg-sienna-bronze/10 text-sienna-bronze border border-sienna-bronze/20 px-2 py-0.5 rounded font-semibold tracking-wider">
                                      EVENT PROPOSAL
                                    </span>
                                    <h4 className="text-xs font-bold text-carbon mt-2.5">{evt.title}</h4>
                                    <p className="text-[11px] text-graphite mt-1 leading-relaxed">{evt.reason}</p>
                                  </div>
                                  <div className="mt-4 flex justify-end">
                                    <button className="px-4 py-2 rounded-full bg-carbon hover:bg-graphite text-white text-xs font-bold transition-all shadow-sm">
                                      Schedule Event
                                    </button>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>

                        </div>

                        {/* Right Sidebar Columns */}
                        <div className="space-y-8">
                          
                          {/* Trending Topics */}
                          <div className="p-6 rounded-[8px] bg-white border border-chalk shadow-sm">
                            <h3 className="font-polysans text-sm font-normal text-carbon mb-4 flex items-center gap-1.5">
                              <TrendingUp className="w-4 h-4 text-signal-orange" /> Trending Topics
                            </h3>
                            <div className="space-y-2.5">
                              {data.health_summary?.trending_topics?.map((topic: string, i: number) => (
                                <div key={i} className="p-3 rounded-[6px] bg-fog border border-chalk text-xs text-carbon leading-relaxed">
                                  <div className="w-1.5 h-1.5 rounded-full bg-signal-orange inline-block mr-2" />
                                  <span>{topic}</span>
                                </div>
                              ))}
                            </div>
                          </div>

                          {/* Potential Mentors */}
                          <div className="p-6 rounded-[8px] bg-white border border-chalk shadow-sm">
                            <h3 className="font-polysans text-sm font-normal text-carbon mb-4 flex items-center gap-1.5">
                              <Award className="w-4 h-4 text-sienna-bronze" /> Potential Mentors
                            </h3>
                            <div className="space-y-3.5">
                              {data.insights?.potential_mentors?.map((mentor: any, i: number) => (
                                <div key={i} className="p-4 rounded-[8px] bg-fog border border-chalk text-xs space-y-3">
                                  <div className="flex items-center justify-between">
                                    <span className="font-bold text-carbon">{mentor.name}</span>
                                    <span className="text-[9px] bg-emerald-500/10 text-emerald-600 border border-emerald-500/20 px-2 py-0.5 rounded-full font-mono font-bold">ELIGIBLE</span>
                                  </div>
                                  <p className="text-[11px] text-graphite leading-relaxed">{mentor.reason}</p>
                                  
                                  <button 
                                    onClick={() => setInvitedMentors(prev => ({ ...prev, [mentor.name]: true }))}
                                    disabled={invitedMentors[mentor.name]}
                                    className="w-full py-2 bg-white hover:bg-fog disabled:bg-emerald-500/10 border border-slate disabled:border-emerald-500/20 disabled:text-emerald-600 text-carbon rounded-full text-[11px] font-bold transition-all shadow-sm"
                                  >
                                    {invitedMentors[mentor.name] ? "Invitation Sent" : "Promote to Mentor"}
                                  </button>
                                </div>
                              ))}
                            </div>
                          </div>

                          {/* Churn Risk Members */}
                          <div className="p-6 rounded-[8px] bg-white border border-chalk shadow-sm">
                            <h3 className="font-polysans text-sm font-normal text-carbon mb-4 flex items-center gap-1.5">
                              <AlertTriangle className="w-4 h-4 text-signal-orange" /> Churn Risk Members
                            </h3>
                            <div className="space-y-3.5">
                              {data.insights?.members_at_risk?.map((member: any, i: number) => (
                                <div key={i} className="p-4 rounded-[8px] bg-fog border border-chalk text-xs space-y-3">
                                  <div className="flex items-center justify-between">
                                    <span className="font-bold text-carbon">{member.name}</span>
                                    <span className="text-[9px] bg-signal-orange/10 text-signal-orange border border-signal-orange/20 px-2 py-0.5 rounded-full font-mono font-bold">HIGH RISK</span>
                                  </div>
                                  <p className="text-[11px] text-graphite leading-relaxed">{member.reason}</p>
                                  
                                  <button 
                                    onClick={() => setReengagedMembers(prev => ({ ...prev, [member.name]: true }))}
                                    disabled={reengagedMembers[member.name]}
                                    className="w-full py-2 bg-white hover:bg-fog disabled:bg-chalk border border-slate disabled:border-chalk disabled:text-slate text-carbon rounded-full text-[11px] font-bold transition-all shadow-sm"
                                  >
                                    {reengagedMembers[member.name] ? "Nudge Message Sent" : "Send Re-engagement Nudge"}
                                  </button>
                                </div>
                              ))}
                            </div>
                          </div>

                        </div>

                      </div>

                    </div>
                  )}

                </div>
              </div>
            ) : (
              <div className="bg-white rounded-[8px] border border-chalk p-24 flex flex-col items-center justify-center gap-2 shadow-sm min-h-[500px]">
                <AlertCircle className="w-8 h-8 text-signal-orange animate-pulse" />
                <div className="text-xs text-graphite font-mono">Failed to render dashboard data.</div>
              </div>
            )}
          </div>
        )}

      </main>

      {/* FOOTER */}
      <footer className="py-10 px-6 border-t border-chalk text-center text-xs text-slate max-w-[1200px] mx-auto w-full mt-auto">
        &copy; {new Date().getFullYear()} Ventriloc --- CommunityOS AI-Powered personalizations. Built for Track 2.
      </footer>
    </div>
  );
}
