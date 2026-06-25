"use client";

import React, { useState, useEffect } from "react";
import { 
  User, Sparkles, Cpu, BookOpen, Calendar, Users, Award, Activity, 
  TrendingUp, AlertTriangle, CheckCircle2, ArrowRight, ChevronRight, 
  Info, Lock, RefreshCw, Play, Check, CheckSquare, ShieldCheck, 
  Search, MessageSquare, Terminal, Eye, AlertCircle
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
  const [activeExplainAgent, setActiveExplainAgent] = useState<string | null>(null);
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
          // Fallback to client-side data
          setData(FALLBACK_DATA[persona]);
        }
      } catch (e) {
        // Fallback to client-side data
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
    <div className="flex-1 flex flex-col bg-slate-950 text-slate-100 font-sans selection:bg-indigo-500 selection:text-white overflow-x-hidden min-h-screen">
      
      {/* BACKGROUND DECORATIONS */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-indigo-900/10 rounded-full blur-3xl -z-10 pointer-events-none" />
      <div className="absolute top-1/3 right-1/4 w-[500px] h-[500px] bg-purple-900/10 rounded-full blur-3xl -z-10 pointer-events-none" />
      <div className="absolute bottom-10 left-10 w-80 h-80 bg-blue-900/10 rounded-full blur-3xl -z-10 pointer-events-none" />

      {/* HEADER */}
      <header className="sticky top-0 z-40 bg-slate-950/80 backdrop-blur-md border-b border-slate-900 py-4 px-6 md:px-12 flex items-center justify-between">
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => setScreen("landing")}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Cpu className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
              CommunityOS
            </span>
            <span className="text-[10px] block text-slate-500 font-mono tracking-wider">ADAPTIVE AGENT LAYER</span>
          </div>
        </div>

        <nav className="flex items-center gap-4">
          <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/60 border border-slate-800 text-xs">
            <span className={`w-2 h-2 rounded-full ${backendStatus === "connected" ? "bg-emerald-500 animate-pulse" : backendStatus === "checking" ? "bg-amber-500 animate-pulse" : "bg-red-500"}`} />
            <span className="text-slate-400">
              Backend API: {backendStatus === "connected" ? "Connected" : backendStatus === "checking" ? "Checking Status..." : "Offline (Using Local Fallback)"}
            </span>
          </div>
          
          {screen === "landing" ? (
            <button 
              onClick={() => setScreen("demo")}
              className="px-5 py-2.5 rounded-xl bg-indigo-600 text-white font-medium text-sm hover:bg-indigo-500 active:scale-95 transition-all shadow-lg shadow-indigo-600/25 flex items-center gap-2 hover:gap-3"
            >
              View Interactive Demo <ArrowRight className="w-4 h-4" />
            </button>
          ) : (
            <button 
              onClick={() => setScreen("landing")}
              className="px-4 py-2 rounded-xl bg-slate-900 text-slate-300 font-medium text-sm hover:bg-slate-850 hover:text-white transition-all border border-slate-800 flex items-center gap-2"
            >
              Landing Page
            </button>
          )}
        </nav>
      </header>

      {/* MAIN CONTAINER */}
      <main className="flex-1 flex flex-col">
        
        {/* ================= LANDING SCREEN ================= */}
        {screen === "landing" && (
          <div className="flex-1 flex flex-col">
            
            {/* HERO SECTION */}
            <section className="px-6 py-20 md:py-32 max-w-5xl mx-auto text-center flex flex-col items-center justify-center">
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold tracking-wide uppercase mb-8 shadow-sm">
                <Sparkles className="w-3.5 h-3.5" /> Hackathon Track 2 Project
              </div>
              
              <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-8">
                <span className="bg-gradient-to-r from-white via-slate-100 to-slate-300 bg-clip-text text-transparent">
                  Traditional Communities
                </span>{" "}
                <br className="hidden md:inline" />
                <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                  Are Completely Static.
                </span>
              </h1>
              
              <p className="text-lg md:text-xl text-slate-400 max-w-3xl mb-12 leading-relaxed">
                Everyone receives the same onboarding, channels, resources, events, and notifications. 
                <strong className="text-white block mt-2">CommunityOS introduces an AI operating layer.</strong>
                A team of specialized agents continuously personalize the experience for every member while helping organizers automate community operations.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center w-full">
                <button 
                  onClick={() => setScreen("demo")}
                  className="w-full sm:w-auto px-8 py-4 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold hover:from-indigo-500 hover:to-purple-500 active:scale-95 transition-all shadow-xl shadow-indigo-600/30 flex items-center justify-center gap-3 text-base"
                >
                  Launch Interactive Demo <Play className="w-5 h-5 fill-white" />
                </button>
                <a 
                  href="#agents-info"
                  className="w-full sm:w-auto px-8 py-4 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-850 hover:border-slate-700 transition-all flex items-center justify-center gap-2 text-base"
                >
                  Meet the Agents
                </a>
              </div>
            </section>

            {/* PLATFORM + AGENTS ARCHITECTURE GRAPHIC */}
            <section className="px-6 py-12 bg-slate-950 border-t border-slate-900/60 flex flex-col items-center">
              <div className="max-w-4xl w-full text-center mb-8">
                <h3 className="text-xs uppercase tracking-widest text-slate-500 font-mono">Platform Integration Architecture</h3>
                <h2 className="text-2xl font-bold mt-2">How CommunityOS Plugs In</h2>
              </div>
              
              <div className="w-full max-w-3xl p-8 rounded-2xl bg-slate-900/40 border border-slate-900 backdrop-blur-xl relative overflow-hidden">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center justify-center relative">
                  
                  {/* Left Box: Core Platform */}
                  <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 flex flex-col items-center">
                    <div className="w-12 h-12 rounded-lg bg-slate-800 flex items-center justify-center mb-4">
                      <Users className="w-6 h-6 text-slate-400" />
                    </div>
                    <h4 className="font-semibold text-white">Community Platform</h4>
                    <p className="text-[11px] text-slate-500 text-center mt-2">Discord, Slack, Discourse, custom portal database</p>
                  </div>
                  
                  {/* Middle Box: Agent Layer */}
                  <div className="p-6 rounded-xl bg-gradient-to-tr from-indigo-950 via-slate-900 to-purple-950 border border-indigo-900/50 flex flex-col items-center relative shadow-2xl">
                    <div className="absolute top-0 right-0 w-3 h-3 bg-indigo-500 rounded-full animate-ping m-2" />
                    <div className="w-12 h-12 rounded-lg bg-indigo-900/40 border border-indigo-500/30 flex items-center justify-center mb-4">
                      <Cpu className="w-6 h-6 text-indigo-400" />
                    </div>
                    <h4 className="font-semibold text-indigo-200">AI Agent Layer</h4>
                    <p className="text-[11px] text-indigo-400/80 text-center mt-2">AgentField control plane running LLM microservices</p>
                  </div>

                  {/* Right Box: Output */}
                  <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 flex flex-col items-center">
                    <div className="w-12 h-12 rounded-lg bg-slate-800 flex items-center justify-center mb-4">
                      <Sparkles className="w-6 h-6 text-pink-400" />
                    </div>
                    <h4 className="font-semibold text-white">Hyper-Personalization</h4>
                    <p className="text-[11px] text-slate-500 text-center mt-2">Dynamic onboardings, learning roadmaps, mentor matching</p>
                  </div>
                </div>
              </div>
            </section>

            {/* THE AGENT TEAM LIST */}
            <section id="agents-info" className="px-6 py-20 bg-slate-950 border-t border-slate-900 max-w-5xl mx-auto">
              <div className="text-center mb-16">
                <h2 className="text-3xl font-extrabold text-white sm:text-4xl">
                  The Multi-Agent Core Network
                </h2>
                <p className="mt-4 text-lg text-slate-400 max-w-2xl mx-auto">
                  Instead of a single general chatbot, CommunityOS uses six specialized agents orchestrating raw member behaviors into insights.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                
                {/* 1. Identity Agent */}
                <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-850 hover:border-slate-800 hover:bg-slate-900/60 transition-all group">
                  <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center mb-4 group-hover:scale-110 transition-all">
                    <User className="w-5 h-5" />
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2">Identity Agent</h3>
                  <p className="text-sm text-slate-400 leading-relaxed">
                    Continuously observes chat logs, code queries, and intro posts. Formulates interests, skills, confidence level, and learning style.
                  </p>
                </div>

                {/* 2. Discovery Agent */}
                <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-850 hover:border-slate-800 hover:bg-slate-900/60 transition-all group">
                  <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400 flex items-center justify-center mb-4 group-hover:scale-110 transition-all">
                    <Search className="w-5 h-5" />
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2">Discovery Agent</h3>
                  <p className="text-sm text-slate-400 leading-relaxed">
                    Matches the dynamically built identity model with relevant channels, resources, templates, and events to deliver a custom community portal.
                  </p>
                </div>

                {/* 3. Learning Agent */}
                <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-850 hover:border-slate-800 hover:bg-slate-900/60 transition-all group">
                  <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mb-4 group-hover:scale-110 transition-all">
                    <BookOpen className="w-5 h-5" />
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2">Learning Agent</h3>
                  <p className="text-sm text-slate-400 leading-relaxed">
                    Creates daily priorities and custom step-by-step roadmap paths. Adjusts technical difficulty depending on user progress and questions.
                  </p>
                </div>

                {/* 4. Mentor Agent */}
                <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-850 hover:border-slate-800 hover:bg-slate-900/60 transition-all group">
                  <div className="w-10 h-10 rounded-xl bg-pink-500/10 border border-pink-500/20 text-pink-400 flex items-center justify-center mb-4 group-hover:scale-110 transition-all">
                    <Users className="w-5 h-5" />
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2">Mentor Agent</h3>
                  <p className="text-sm text-slate-400 leading-relaxed">
                    Examines profiles of expert members and rookies. Computes technical overlaps to recommend optimal mentor assignments.
                  </p>
                </div>

                {/* 5. Community Health Agent */}
                <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-850 hover:border-slate-800 hover:bg-slate-900/60 transition-all group">
                  <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center mb-4 group-hover:scale-110 transition-all">
                    <Activity className="w-5 h-5" />
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2">Community Health Agent</h3>
                  <p className="text-sm text-slate-400 leading-relaxed">
                    Surveys inactive periods, ignored newcomers, and unanswered technical posts to highlight potential operational risks and churn signs.
                  </p>
                </div>

                {/* 6. Organizer Agent */}
                <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-850 hover:border-slate-800 hover:bg-slate-900/60 transition-all group">
                  <div className="w-10 h-10 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-center justify-center mb-4 group-hover:scale-110 transition-all">
                    <ShieldCheck className="w-5 h-5" />
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2">Organizer Agent</h3>
                  <p className="text-sm text-slate-400 leading-relaxed">
                    Translates data diagnostics from Health Agent into concrete suggested events, mentor invites, churn rescues, and automated moderation actions.
                  </p>
                </div>

              </div>
            </section>
          </div>
        )}

        {/* ================= DEMO DASHBOARD ================= */}
        {screen === "demo" && (
          <div className="flex-1 flex flex-col">
            
            {/* PERSONA CHANGER HEADER */}
            <div className="bg-slate-900/40 border-b border-slate-900 px-6 py-4 flex flex-col md:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-400 uppercase tracking-wider font-mono">Select Persona:</span>
                <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-800">
                  <button 
                    onClick={() => { setPersona("rahul"); setData(null); }}
                    className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center gap-2 ${persona === "rahul" ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/10" : "text-slate-400 hover:text-slate-200"}`}
                  >
                    <User className="w-3.5 h-3.5" /> Rahul (Systems/GPU)
                  </button>
                  <button 
                    onClick={() => { setPersona("priya"); setData(null); }}
                    className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center gap-2 ${persona === "priya" ? "bg-purple-600 text-white shadow-md shadow-purple-600/10" : "text-slate-400 hover:text-slate-200"}`}
                  >
                    <User className="w-3.5 h-3.5" /> Priya (Beginner AI)
                  </button>
                  <button 
                    onClick={() => { setPersona("organizer"); setData(null); }}
                    className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center gap-2 ${persona === "organizer" ? "bg-rose-600 text-white shadow-md shadow-rose-600/10" : "text-slate-400 hover:text-slate-200"}`}
                  >
                    <ShieldCheck className="w-3.5 h-3.5" /> Organizer Dashboard
                  </button>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={() => setShowAllExplainability(!showAllExplainability)}
                  className="px-3.5 py-1.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-xs font-medium text-indigo-400 hover:bg-indigo-500/20 active:scale-95 transition-all flex items-center gap-1.5"
                >
                  <Sparkles className="w-3.5 h-3.5" /> {showAllExplainability ? "Hide AI Reasoning" : "Why am I seeing this?"}
                </button>
                
                <button
                  onClick={() => { setData(null); }}
                  className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-all"
                  title="Reload Agent Reasoning"
                >
                  <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin text-indigo-400" : ""}`} />
                </button>
              </div>
            </div>

            {/* EXPLAINABILITY DRAWER (WHOLE TEAM AT A GLANCE) */}
            {showAllExplainability && data && (
              <div className="bg-gradient-to-r from-indigo-950/40 via-slate-900/60 to-purple-950/40 border-b border-indigo-950 px-6 py-6 transition-all duration-300">
                <div className="max-w-6xl mx-auto">
                  <div className="flex items-center gap-2 mb-4">
                    <Terminal className="w-4 h-4 text-indigo-400" />
                    <h3 className="text-xs uppercase font-bold text-indigo-300 tracking-widest font-mono">Agentfield Control Plane --- Multi-Agent Session Diagnostics</h3>
                  </div>

                  {persona !== "organizer" ? (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      
                      {/* Identity agent explanation */}
                      <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-850 hover:border-blue-900/40 transition-all">
                        <div className="flex items-center gap-2 mb-2 pb-2 border-b border-slate-900">
                          <User className="w-4 h-4 text-blue-400" />
                          <span className="text-xs font-bold text-blue-300 font-mono">Identity Agent</span>
                        </div>
                        <p className="text-xs text-slate-300 leading-relaxed font-sans">{data.explainability?.identity_agent}</p>
                      </div>

                      {/* Discovery Agent explanation */}
                      <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-850 hover:border-purple-900/40 transition-all">
                        <div className="flex items-center gap-2 mb-2 pb-2 border-b border-slate-900">
                          <Search className="w-4 h-4 text-purple-400" />
                          <span className="text-xs font-bold text-purple-300 font-mono">Discovery Agent</span>
                        </div>
                        <p className="text-xs text-slate-300 leading-relaxed font-sans">{data.explainability?.discovery_agent}</p>
                      </div>

                      {/* Learning Agent explanation */}
                      <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-850 hover:border-emerald-900/40 transition-all">
                        <div className="flex items-center gap-2 mb-2 pb-2 border-b border-slate-900">
                          <BookOpen className="w-4 h-4 text-emerald-400" />
                          <span className="text-xs font-bold text-emerald-300 font-mono">Learning Agent</span>
                        </div>
                        <p className="text-xs text-slate-300 leading-relaxed font-sans">{data.explainability?.learning_agent}</p>
                      </div>

                      {/* Mentor Agent explanation */}
                      <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-850 hover:border-pink-900/40 transition-all">
                        <div className="flex items-center gap-2 mb-2 pb-2 border-b border-slate-900">
                          <Users className="w-4 h-4 text-pink-400" />
                          <span className="text-xs font-bold text-pink-300 font-mono">Mentor Agent</span>
                        </div>
                        <p className="text-xs text-slate-300 leading-relaxed font-sans">{data.explainability?.mentor_agent}</p>
                      </div>

                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      
                      {/* Health agent explanation */}
                      <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-850 hover:border-amber-900/40 transition-all">
                        <div className="flex items-center gap-2 mb-2 pb-2 border-b border-slate-900">
                          <Activity className="w-4 h-4 text-amber-400" />
                          <span className="text-xs font-bold text-amber-300 font-mono">Community Health Agent</span>
                        </div>
                        <p className="text-xs text-slate-300 leading-relaxed font-sans">{data.health_summary?.explainability}</p>
                      </div>

                      {/* Organizer Agent explanation */}
                      <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-850 hover:border-rose-900/40 transition-all">
                        <div className="flex items-center gap-2 mb-2 pb-2 border-b border-slate-900">
                          <ShieldCheck className="w-4 h-4 text-rose-400" />
                          <span className="text-xs font-bold text-rose-300 font-mono">Organizer Agent</span>
                        </div>
                        <p className="text-xs text-slate-300 leading-relaxed font-sans">{data.insights?.explainability}</p>
                      </div>

                    </div>
                  )}
                </div>
              </div>
            )}

            {/* DASHBOARD BODY */}
            {loading ? (
              <div className="flex-1 flex flex-col items-center justify-center py-24 gap-4">
                <RefreshCw className="w-8 h-8 text-indigo-500 animate-spin" />
                <div className="text-sm text-slate-400 font-mono">AgentField invoking LLM reasoners...</div>
              </div>
            ) : data ? (
              <div className="flex-1 overflow-y-auto px-6 py-8 md:px-12">
                <div className="max-w-6xl mx-auto">
                  
                  {/* ================= MEMBER PERSONA PANEL ================= */}
                  {persona !== "organizer" && (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                      
                      {/* LEFT 2 COLUMNS */}
                      <div className="lg:col-span-2 space-y-8">
                        
                        {/* WELCOME BANNER */}
                        <div className="p-8 rounded-2xl bg-gradient-to-r from-slate-900 to-indigo-950/50 border border-indigo-900/30 relative overflow-hidden shadow-xl">
                          <div className="absolute top-0 right-0 w-24 h-24 bg-indigo-500/5 rounded-full blur-xl" />
                          <h2 className="text-3xl font-extrabold text-white mb-3">Welcome back, {data.name}!</h2>
                          <p className="text-slate-300 leading-relaxed">{data.welcome_message}</p>
                          
                          {/* User Bio and Tags */}
                          <div className="mt-6 pt-6 border-t border-slate-800/80 flex flex-col sm:flex-row sm:items-center gap-4">
                            <span className="text-xs font-bold text-slate-400 uppercase tracking-wide">Skills Model:</span>
                            <div className="flex flex-wrap gap-1.5">
                              {data.skills?.map((skill: string) => (
                                <span key={skill} className="px-2.5 py-0.5 rounded-full bg-slate-950 text-indigo-300 border border-slate-800 text-[11px] font-medium">
                                  {skill}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>

                        {/* PRIORITIES & ROADMAP */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                          
                          {/* TODAY'S PRIORITIES */}
                          <div className="p-6 rounded-2xl bg-slate-900/30 border border-slate-850/80 flex flex-col h-full">
                            <div className="flex items-center gap-2.5 mb-5">
                              <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400 border border-indigo-500/20">
                                <CheckSquare className="w-4 h-4" />
                              </div>
                              <h3 className="font-bold text-white text-base">Today's Priorities</h3>
                            </div>
                            
                            <ul className="space-y-4 flex-1">
                              {data.priorities?.map((priority: string, i: number) => (
                                <li key={i} className="flex gap-3 text-sm text-slate-300 items-start">
                                  <span className="w-5 h-5 rounded-full bg-slate-950 border border-slate-800 flex items-center justify-center text-[10px] text-slate-500 font-mono mt-0.5">{i+1}</span>
                                  <span className="flex-1">{priority}</span>
                                </li>
                              ))}
                            </ul>
                          </div>

                          {/* PERSONALIZED PATHWAY */}
                          <div className="p-6 rounded-2xl bg-slate-900/30 border border-slate-850/80 flex flex-col h-full">
                            <div className="flex items-center gap-2.5 mb-5">
                              <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400 border border-emerald-500/20">
                                <BookOpen className="w-4 h-4" />
                              </div>
                              <h3 className="font-bold text-white text-base">Learning Roadmap</h3>
                            </div>

                            {/* Timeline steps */}
                            <div className="relative border-l border-slate-800 ml-3 pl-6 space-y-5 flex-1">
                              {persona === "rahul" ? (
                                <>
                                  <div className="relative">
                                    <div className="absolute -left-[30px] top-1 w-2 h-2 rounded-full bg-indigo-500 ring-4 ring-indigo-950" />
                                    <h4 className="text-xs font-semibold text-indigo-400">Step 1: Code Kernel</h4>
                                    <p className="text-xs text-slate-400 mt-1">Analyze shared memory bank conflicts in matrix multiplication.</p>
                                  </div>
                                  <div className="relative">
                                    <div className="absolute -left-[30px] top-1 w-2 h-2 rounded-full bg-slate-700" />
                                    <h4 className="text-xs font-semibold text-slate-300">Step 2: Benchmark Padding</h4>
                                    <p className="text-xs text-slate-400 mt-1">Implement memory padding configurations and test grid speed.</p>
                                  </div>
                                  <div className="relative">
                                    <div className="absolute -left-[30px] top-1 w-2 h-2 rounded-full bg-slate-700" />
                                    <h4 className="text-xs font-semibold text-slate-300">Step 3: Meet Expert Sarah</h4>
                                    <p className="text-xs text-slate-400 mt-1">Attend the GPU AMA to run profile reviews of CUDA code.</p>
                                  </div>
                                </>
                              ) : (
                                <>
                                  <div className="relative">
                                    <div className="absolute -left-[30px] top-1 w-2 h-2 rounded-full bg-purple-500 ring-4 ring-purple-950" />
                                    <h4 className="text-xs font-semibold text-purple-400">Step 1: Tensor Basics</h4>
                                    <p className="text-xs text-slate-400 mt-1">Run basic operations in PyTorch interactive notebooks.</p>
                                  </div>
                                  <div className="relative">
                                    <div className="absolute -left-[30px] top-1 w-2 h-2 rounded-full bg-slate-700" />
                                    <h4 className="text-xs font-semibold text-slate-300">Step 2: Build MNIST</h4>
                                    <p className="text-xs text-slate-400 mt-1">Attend PyTorch 101 workshop to program your first classifier.</p>
                                  </div>
                                  <div className="relative">
                                    <div className="absolute -left-[30px] top-1 w-2 h-2 rounded-full bg-slate-700" />
                                    <h4 className="text-xs font-semibold text-slate-300">Step 3: Mentor Check-In</h4>
                                    <p className="text-xs text-slate-400 mt-1">Connect with Elena for custom feedback on deep learning books.</p>
                                  </div>
                                </>
                              )}
                            </div>
                          </div>

                        </div>

                        {/* RECOMMENDATIONS: CHANNELS, FILES, MEETUPS */}
                        <div className="space-y-6">
                          <h3 className="font-bold text-white text-lg border-b border-slate-900 pb-3 flex items-center gap-2">
                            <Sparkles className="w-5 h-5 text-indigo-400" /> Discovery recommendations
                          </h3>
                          
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            
                            {/* Resources list */}
                            <div className="space-y-4">
                              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-1.5">
                                <BookOpen className="w-3.5 h-3.5 text-indigo-400" /> Recommended Resources
                              </h4>
                              <div className="space-y-3">
                                {data.resources?.map((res: any) => (
                                  <div key={res.id} className="p-4 rounded-xl bg-slate-900/20 border border-slate-900 hover:border-slate-850 hover:bg-slate-900/40 transition-all flex flex-col justify-between">
                                    <div>
                                      <h5 className="text-sm font-semibold text-slate-200">{res.name}</h5>
                                      <p className="text-xs text-slate-400 mt-1 leading-relaxed">{res.description}</p>
                                    </div>
                                    <div className="mt-3 flex justify-end">
                                      <a href={res.url} className="text-xs text-indigo-400 hover:text-indigo-300 inline-flex items-center gap-1">
                                        Read Guide <ChevronRight className="w-3.5 h-3.5" />
                                      </a>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>

                            {/* Events list */}
                            <div className="space-y-4">
                              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-1.5">
                                <Calendar className="w-3.5 h-3.5 text-indigo-400" /> Suggested Events
                              </h4>
                              <div className="space-y-3">
                                {data.events?.map((evt: any) => (
                                  <div key={evt.id} className="p-4 rounded-xl bg-slate-900/20 border border-slate-900 hover:border-slate-850 hover:bg-slate-900/40 transition-all">
                                    <div className="flex items-center justify-between gap-2">
                                      <h5 className="text-sm font-semibold text-slate-200">{evt.name}</h5>
                                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 shrink-0 font-medium">
                                        {evt.time}
                                      </span>
                                    </div>
                                    <p className="text-xs text-slate-400 mt-2 leading-relaxed">{evt.description}</p>
                                    <div className="mt-3 flex justify-end">
                                      <button className="text-xs px-2.5 py-1 rounded bg-slate-950 border border-slate-800 hover:bg-slate-900 text-slate-300 transition-all">
                                        Add to Calendar
                                      </button>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>

                          </div>
                        </div>

                      </div>

                      {/* RIGHT COLUMN (SIDEBAR) */}
                      <div className="space-y-8">
                        
                        {/* RECOMMENDED MENTOR */}
                        <div className="p-6 rounded-2xl bg-gradient-to-b from-indigo-950/20 to-slate-900/40 border border-indigo-900/20 shadow-xl">
                          <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-widest mb-4">Recommended Mentor</h4>
                          
                          <div className="flex items-start gap-4">
                            <div className="w-12 h-12 rounded-xl bg-indigo-900/30 flex items-center justify-center shrink-0 border border-indigo-500/20 font-bold text-indigo-300">
                              {data.recommended_mentor?.name[0]}
                            </div>
                            <div>
                              <h3 className="font-bold text-white text-base">{data.recommended_mentor?.name}</h3>
                              <p className="text-xs text-slate-400">{data.recommended_mentor?.role}</p>
                            </div>
                          </div>

                          <div className="mt-4 p-3 rounded-lg bg-slate-950/80 border border-slate-850 text-xs text-slate-300 leading-relaxed">
                            <span className="font-semibold text-indigo-300 block mb-1">Agent Match Reason:</span>
                            {data.recommended_mentor?.overlap_reason}
                          </div>

                          <button className="w-full mt-4 py-2.5 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold hover:shadow-lg transition-all active:scale-95 flex items-center justify-center gap-1.5">
                            <MessageSquare className="w-3.5 h-3.5" /> Direct Message {data.recommended_mentor?.name}
                          </button>
                        </div>

                        {/* COMMUNITIES GRID */}
                        <div className="p-6 rounded-2xl bg-slate-900/30 border border-slate-850/80">
                          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Matched Channels</h4>
                          
                          <div className="space-y-4">
                            <div>
                              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block mb-2">High Priority</span>
                              <div className="space-y-2">
                                {data.communities?.recommended?.map((com: any) => (
                                  <div key={com.id} className="p-3 rounded-xl bg-indigo-950/10 border border-indigo-950/50 hover:border-indigo-900 flex items-center justify-between transition-all">
                                    <span className="text-xs font-medium text-slate-200"># {com.name}</span>
                                    <ChevronRight className="w-3.5 h-3.5 text-slate-500" />
                                  </div>
                                ))}
                              </div>
                            </div>

                            <div>
                              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block mb-2">Lower Priority</span>
                              <div className="space-y-2">
                                {data.communities?.lower_priority?.map((com: any) => (
                                  <div key={com.id} className="p-3 rounded-xl bg-slate-950/60 border border-slate-900 flex items-center justify-between opacity-50 hover:opacity-100 transition-all">
                                    <span className="text-xs font-medium text-slate-400"># {com.name}</span>
                                    <Lock className="w-3 h-3 text-slate-600" />
                                  </div>
                                ))}
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* COMMUNITY INSIGHTS CARD */}
                        <div className="p-6 rounded-2xl bg-slate-900/30 border border-slate-850/80">
                          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Community Insights</h4>
                          
                          <div className="space-y-3">
                            {data.insights?.map((insight: string, idx: number) => (
                              <div key={idx} className="flex items-center gap-2.5 p-2 rounded-lg bg-slate-950/40 border border-slate-900 text-xs text-slate-300">
                                <Award className="w-4 h-4 text-amber-500" />
                                <span>{insight}</span>
                              </div>
                            ))}
                          </div>
                        </div>

                      </div>

                    </div>
                  )}

                  {/* ================= ORGANIZER DASHBOARD PANEL ================= */}
                  {persona === "organizer" && (
                    <div className="space-y-8">
                      
                      {/* STATS OVERVIEW HEADER */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        
                        {/* Health score */}
                        <div className="p-6 rounded-2xl bg-slate-900/30 border border-slate-850/80 flex items-center gap-4">
                          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center justify-center shrink-0">
                            <Activity className="w-5 h-5" />
                          </div>
                          <div>
                            <span className="text-[10px] text-slate-500 block uppercase font-mono tracking-wider">Health Score</span>
                            <span className="text-xl font-bold text-white">{data.metrics?.active_members_ratio === "83%" ? "92%" : "88%"}</span>
                          </div>
                        </div>

                        {/* Active members */}
                        <div className="p-6 rounded-2xl bg-slate-900/30 border border-slate-850/80 flex items-center gap-4">
                          <div className="w-10 h-10 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20 flex items-center justify-center shrink-0">
                            <Users className="w-5 h-5" />
                          </div>
                          <div>
                            <span className="text-[10px] text-slate-500 block uppercase font-mono tracking-wider">Active Members</span>
                            <span className="text-xl font-bold text-white">{data.metrics?.active_members_ratio}</span>
                          </div>
                        </div>

                        {/* Weekly posts */}
                        <div className="p-6 rounded-2xl bg-slate-900/30 border border-slate-850/80 flex items-center gap-4">
                          <div className="w-10 h-10 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20 flex items-center justify-center shrink-0">
                            <MessageSquare className="w-5 h-5" />
                          </div>
                          <div>
                            <span className="text-[10px] text-slate-500 block uppercase font-mono tracking-wider">Weekly Messages</span>
                            <span className="text-xl font-bold text-white">{data.metrics?.weekly_messages}</span>
                          </div>
                        </div>

                        {/* Unanswered posts */}
                        <div className="p-6 rounded-2xl bg-slate-900/30 border border-slate-850/80 flex items-center gap-4">
                          <div className="w-10 h-10 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center justify-center shrink-0">
                            <AlertTriangle className="w-5 h-5" />
                          </div>
                          <div>
                            <span className="text-[10px] text-slate-500 block uppercase font-mono tracking-wider">Unanswered Posts</span>
                            <span className="text-xl font-bold text-white">{data.metrics?.unanswered_threads}</span>
                          </div>
                        </div>

                      </div>

                      {/* AI SUGGESTED ACTIONS - MAIN OPERATIONS COMPONENT */}
                      <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 to-indigo-950/20 border border-indigo-900/20 shadow-xl">
                        <div className="flex items-center gap-2 mb-6">
                          <Cpu className="w-5 h-5 text-indigo-400 animate-pulse" />
                          <h3 className="font-bold text-white text-lg">AI Suggested Actions</h3>
                        </div>

                        <div className="space-y-4">
                          {data.insights?.suggested_actions?.map((act: any) => (
                            <div 
                              key={act.id} 
                              className={`p-5 rounded-xl border transition-all flex flex-col md:flex-row md:items-center justify-between gap-4 ${
                                executedActions[act.id] 
                                  ? "bg-emerald-950/15 border-emerald-900/40 opacity-80" 
                                  : "bg-slate-950/80 border-slate-850 hover:border-slate-800"
                              }`}
                            >
                              <div className="space-y-2">
                                <div className="flex flex-wrap items-center gap-2">
                                  <span className={`text-[9px] font-mono px-2 py-0.5 rounded font-semibold tracking-wider ${
                                    act.agent.includes("Health") 
                                      ? "bg-amber-500/10 text-amber-400 border border-amber-500/20" 
                                      : "bg-pink-500/10 text-pink-400 border border-pink-500/20"
                                  }`}>
                                    {act.agent}
                                  </span>
                                  <span className="text-[9px] font-mono px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-semibold tracking-wider">
                                    HIGH PRIORITY
                                  </span>
                                </div>
                                <h4 className={`text-sm font-semibold text-slate-200 ${executedActions[act.id] ? "line-through text-slate-500" : ""}`}>
                                  {act.action}
                                </h4>
                                <p className="text-xs text-slate-400">{act.reason}</p>
                              </div>

                              <div className="shrink-0 flex items-center gap-3">
                                {executedActions[act.id] ? (
                                  <span className="text-xs text-emerald-400 font-bold flex items-center gap-1 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                                    <Check className="w-3.5 h-3.5" /> Action Executed
                                  </span>
                                ) : (
                                  <button
                                    onClick={() => handleExecuteAction(act.id)}
                                    disabled={executingActionId === act.id}
                                    className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-900 disabled:text-slate-600 text-white text-xs font-bold transition-all flex items-center gap-1.5 shadow-md shadow-indigo-600/15"
                                  >
                                    {executingActionId === act.id ? (
                                      <>
                                        <RefreshCw className="w-3 h-3 animate-spin" /> Executing Flow...
                                      </>
                                    ) : (
                                      <>
                                        <Play className="w-3 h-3 fill-white" /> Execute Action
                                      </>
                                    )}
                                  </button>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* MAIN GRID BLOCK */}
                      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        
                        {/* LEFT AND MID PANEL */}
                        <div className="lg:col-span-2 space-y-8">
                          
                          {/* NEW / IGNORED MEMBERS */}
                          <div className="p-6 rounded-2xl bg-slate-900/30 border border-slate-850/80">
                            <h3 className="font-bold text-white text-base mb-4 flex items-center gap-2">
                              <AlertCircle className="w-4 h-4 text-amber-400" /> Member Rescue Pipeline
                            </h3>
                            <div className="space-y-4">
                              {data.health_summary?.ignored_newcomers?.map((newcomer: string, idx: number) => (
                                <div key={idx} className="p-4 rounded-xl bg-slate-950 border border-amber-900/30 hover:border-amber-900/50 transition-all flex items-center justify-between gap-4">
                                  <div className="space-y-1">
                                    <div className="flex items-center gap-2">
                                      <span className="w-2.5 h-2.5 rounded-full bg-amber-500 animate-pulse" />
                                      <h4 className="text-sm font-semibold text-slate-200">{newcomer}</h4>
                                    </div>
                                    <p className="text-xs text-slate-400">Bio: Non-CS learner looking to build her first neural network in PyTorch.</p>
                                    <span className="text-[10px] text-amber-400 block font-mono">12 hours since introduction in #introductions. 0 responses.</span>
                                  </div>

                                  <button 
                                    onClick={() => setWelcomedMembers(prev => ({ ...prev, [newcomer]: true }))}
                                    disabled={welcomedMembers[newcomer]}
                                    className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-850 text-xs font-semibold text-slate-300 disabled:text-emerald-400 disabled:border-emerald-950 disabled:bg-emerald-950/10 flex items-center gap-1.5 shrink-0 transition-all"
                                  >
                                    {welcomedMembers[newcomer] ? (
                                      <>
                                        <Check className="w-3 h-3" /> Welcomed
                                      </>
                                    ) : (
                                      "Welcome Her"
                                    )}
                                  </button>
                                </div>
                              ))}
                            </div>
                          </div>

                          {/* SUGGESTED EVENTS GENERATION */}
                          <div className="p-6 rounded-2xl bg-slate-900/30 border border-slate-850/80">
                            <h3 className="font-bold text-white text-base mb-4 flex items-center gap-2">
                              <Calendar className="w-4 h-4 text-purple-400" /> AI Suggested Events (Based on Trends)
                            </h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              {data.insights?.suggested_events?.map((evt: any, i: number) => (
                                <div key={i} className="p-4 rounded-xl bg-slate-950 border border-slate-900 hover:border-slate-850 transition-all flex flex-col justify-between">
                                  <div>
                                    <span className="text-[9px] font-mono bg-purple-500/10 text-purple-400 border border-purple-500/20 px-2 py-0.5 rounded font-semibold tracking-wider">
                                      EVENT PROPOSAL
                                    </span>
                                    <h4 className="text-sm font-semibold text-slate-200 mt-2">{evt.title}</h4>
                                    <p className="text-xs text-slate-400 mt-1 leading-relaxed">{evt.reason}</p>
                                  </div>
                                  <div className="mt-4 flex justify-end">
                                    <button className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all">
                                      Schedule Event
                                    </button>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>

                        </div>

                        {/* RIGHT COLUMNS */}
                        <div className="space-y-8">
                          
                          {/* TRENDING TOPICS */}
                          <div className="p-6 rounded-2xl bg-slate-900/30 border border-slate-850/80">
                            <h3 className="font-bold text-white text-sm uppercase tracking-wider mb-4 flex items-center gap-1.5">
                              <TrendingUp className="w-4 h-4 text-indigo-400" /> Trending Topics
                            </h3>
                            <div className="space-y-3">
                              {data.health_summary?.trending_topics?.map((topic: string, i: number) => (
                                <div key={i} className="p-3 rounded-lg bg-slate-950 border border-slate-900 text-xs text-slate-300">
                                  <div className="w-1.5 h-1.5 rounded-full bg-indigo-400 inline-block mr-2" />
                                  <span>{topic}</span>
                                </div>
                              ))}
                            </div>
                          </div>

                          {/* POTENTIAL MENTORS */}
                          <div className="p-6 rounded-2xl bg-slate-900/30 border border-slate-850/80">
                            <h3 className="font-bold text-white text-sm uppercase tracking-wider mb-4 flex items-center gap-1.5">
                              <Award className="w-4 h-4 text-emerald-400" /> Potential Mentors
                            </h3>
                            <div className="space-y-3">
                              {data.insights?.potential_mentors?.map((mentor: any, i: number) => (
                                <div key={i} className="p-4 rounded-xl bg-slate-950 border border-slate-900 text-xs space-y-2">
                                  <div className="flex items-center justify-between">
                                    <span className="font-bold text-slate-200">{mentor.name}</span>
                                    <span className="text-[10px] text-emerald-400 font-mono">Eligible</span>
                                  </div>
                                  <p className="text-slate-400 leading-relaxed">{mentor.reason}</p>
                                  <button 
                                    onClick={() => setInvitedMentors(prev => ({ ...prev, [mentor.name]: true }))}
                                    disabled={invitedMentors[mentor.name]}
                                    className="w-full mt-2 py-1.5 bg-slate-900 hover:bg-slate-850 disabled:bg-emerald-950/20 disabled:text-emerald-400 border border-slate-800 disabled:border-emerald-900/40 text-slate-300 rounded text-[11px] font-semibold transition-all"
                                  >
                                    {invitedMentors[mentor.name] ? "Invitation Sent" : "Promote to Mentor"}
                                  </button>
                                </div>
                              ))}
                            </div>
                          </div>

                          {/* MEMBERS AT RISK */}
                          <div className="p-6 rounded-2xl bg-slate-900/30 border border-slate-850/80">
                            <h3 className="font-bold text-white text-sm uppercase tracking-wider mb-4 flex items-center gap-1.5">
                              <AlertTriangle className="w-4 h-4 text-rose-400" /> Churn Risk Members
                            </h3>
                            <div className="space-y-3">
                              {data.insights?.members_at_risk?.map((member: any, i: number) => (
                                <div key={i} className="p-4 rounded-xl bg-slate-950 border border-rose-950/25 text-xs space-y-2">
                                  <div className="flex items-center justify-between">
                                    <span className="font-bold text-slate-200">{member.name}</span>
                                    <span className="text-[10px] text-rose-400 font-mono">HIGH RISK</span>
                                  </div>
                                  <p className="text-slate-400 leading-relaxed">{member.reason}</p>
                                  <button 
                                    onClick={() => setReengagedMembers(prev => ({ ...prev, [member.name]: true }))}
                                    disabled={reengagedMembers[member.name]}
                                    className="w-full mt-2 py-1.5 bg-slate-900 hover:bg-slate-850 disabled:bg-slate-950 border border-slate-800 disabled:text-slate-600 disabled:border-slate-900 text-slate-300 rounded text-[11px] font-semibold transition-all"
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
              <div className="flex-1 flex flex-col items-center justify-center py-24 gap-2">
                <AlertCircle className="w-8 h-8 text-rose-500" />
                <div className="text-sm text-slate-400">Failed to render dashboard data.</div>
              </div>
            )}
          </div>
        )}

      </main>

          {/* FOOTER */}
          <footer className="py-8 px-6 border-t border-slate-900 text-center text-xs text-slate-500 mt-auto">
            &copy; {new Date().getFullYear()} CommunityOS --- AI-Powered Community Operations Agent. Built for Track 2.
          </footer>
        </div>
      );
    }
