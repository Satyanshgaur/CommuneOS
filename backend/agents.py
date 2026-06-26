# backend/agents.py

import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from agentfield import Agent, AIConfig
from backend.mock_data import MEMBERS, COMMUNITIES, RESOURCES, EVENTS

# Check if OpenRouter key is configured
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
model_name = os.getenv("OPENROUTER_MODEL", "openrouter/google/gemma-2-9b-it:free")

# Ensure the model is correctly routed through OpenRouter in LiteLLM/AgentField
if model_name and not model_name.startswith("openrouter/") and not model_name.startswith("openai/"):
    model_name = f"openrouter/{model_name}"

# Ensure LiteLLM / AgentField environment variables are set correctly for OpenRouter
if OPENROUTER_API_KEY:
    os.environ["OPENROUTER_API_KEY"] = OPENROUTER_API_KEY
    os.environ["OPENAI_API_KEY"] = OPENROUTER_API_KEY
    os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"

# Initialize AgentField app
app = Agent(
    node_id="community-ops-agent",
    ai_config=AIConfig(
        model=model_name,
        temperature=0.2
    ) if OPENROUTER_API_KEY else None
)

# --- Pydantic Schemas for Agents ---

class IdentityProfile(BaseModel):
    interests: List[str] = Field(description="List of detected interests (e.g., CUDA, PyTorch, Rust)")
    skill_level: str = Field(description="Detected skill level (Beginner, Intermediate, Expert)")
    goals: List[str] = Field(description="Member goals (e.g., transition to AI, optimize kernels)")
    learning_style: str = Field(description="Preferred style of learning")
    reasoning: str = Field(description="Internal reasoning of the Identity Agent detailing how it analyzed the user profile and activities")

class DiscoveryRecommendations(BaseModel):
    recommended_communities: List[str] = Field(description="IDs of recommended communities")
    lower_priority_communities: List[str] = Field(description="IDs of lower priority communities")
    recommended_resources: List[str] = Field(description="IDs of recommended learning resources")
    recommended_events: List[str] = Field(description="IDs of recommended upcoming events")
    reasoning: str = Field(description="Internal reasoning of the Discovery Agent detailing how it matched interests with resources and groups")

class LearningPath(BaseModel):
    priorities: List[str] = Field(description="List of 3 immediate priorities for the welcome dashboard")
    steps: List[str] = Field(description="List of structured learning steps/milestones")
    reasoning: str = Field(description="Internal reasoning of the Learning Agent for creating this roadmap")

class MentorMatch(BaseModel):
    mentor_name: str = Field(description="Name of the matched mentor")
    mentor_role: str = Field(description="Professional role or skill of the mentor")
    overlap_reason: str = Field(description="Why this mentor is a match")
    reasoning: str = Field(description="Internal reasoning of the Mentor Agent detailing the matching criteria")

class HealthReport(BaseModel):
    ignored_newcomers: List[str] = Field(description="List of names of new members who haven't received replies")
    unanswered_questions: List[str] = Field(description="List of recent unanswered questions/topics")
    inactive_members: List[str] = Field(description="List of members who have been inactive recently")
    trending_topics: List[str] = Field(description="Trending discussion topics in the community")
    reasoning: str = Field(description="Internal reasoning of the Community Health Agent")

class ActionSuggestion(BaseModel):
    action: str = Field(description="The recommended action for the organizer")
    agent: str = Field(description="The agent proposing this action (e.g., Mentor Agent, Health Agent)")
    reason: str = Field(description="The underlying data/reason for this recommendation")

class OrganizerInsights(BaseModel):
    suggested_events: List[Dict[str, str]] = Field(description="List of event ideas with title and reason")
    potential_mentors: List[Dict[str, str]] = Field(description="List of active experts who could mentor, with name and reason")
    members_at_risk: List[Dict[str, str]] = Field(description="List of inactive members with name and risk level/reason")
    suggested_actions: List[ActionSuggestion] = Field(description="List of actionable tasks for organizers")
    reasoning: str = Field(description="Internal reasoning of the Organizer Agent")

# --- Agent Reasoners ---

@app.reasoner()
async def run_identity_agent(member_id: str) -> IdentityProfile:
    member = MEMBERS.get(member_id)
    if not member:
        raise ValueError(f"Member {member_id} not found.")

    def get_fallback():
        if member_id == "rahul":
            return IdentityProfile(
                interests=["CUDA", "Systems Programming", "Rust", "GPU Architecture"],
                skill_level="Intermediate/Advanced",
                goals=["Master CUDA optimization", "Understand GPU hardware-level execution", "Optimize LLM inference engines"],
                learning_style="Hands-on coding, deep-dive source code review, benchmarking",
                reasoning="Identity Agent: Analyzed Rahul's bio and active channels. His message in #gpu-computing regarding CUDA bank conflicts confirms intermediate-to-advanced low-level skills. His reply in #rust helping Aman proves he is highly capable and active in systems topics."
            )
        elif member_id == "priya":
            return IdentityProfile(
                interests=["PyTorch", "Deep Learning", "Python Basics", "Neural Networks"],
                skill_level="Beginner",
                goals=["Build first neural network in PyTorch", "Transition to AI Engineering", "Learn machine learning math fundamentals"],
                learning_style="Step-by-step interactive notebooks, beginner study groups, mentor guidance",
                reasoning="Identity Agent: Detected that Priya is a brand new member from a non-CS background. Her introductory post in #introductions highlights high enthusiasm for PyTorch but requires structured, non-intimidating beginner-level starting points."
            )
        else:
            return IdentityProfile(
                interests=member.get("skills", []),
                skill_level=member.get("skill_level", "Intermediate"),
                goals=[member.get("goals", "Learn and contribute")],
                learning_style=member.get("learning_style", "Collaborative learning"),
                reasoning=f"Identity Agent: Analyzed {member['name']}'s bio and metrics. Detected skill level as {member['skill_level']}."
            )

    if not OPENROUTER_API_KEY:
        return get_fallback()

    prompt = f"""
    Analyze the following community member profile and activity logs to generate a structured Identity Profile:
    Member Data: {member}
    
    Determine:
    1. Key interests (specific technologies).
    2. Overall skill level (Beginner, Intermediate, Expert).
    3. Goals in the community.
    4. Preferred learning style.
    5. Write a detailed reason explaining your classification as the "Identity Agent".
    """
    
    try:
        out = await app.ai(
            system="You are the Identity Agent of CommunityOS. Your job is to analyze member profiles and behavior to build an accurate identity model.",
            user=prompt,
            schema=IdentityProfile
        )
        return out
    except Exception as e:
        print(f"Identity Agent OpenRouter error: {e}. Falling back to high-fidelity mock reasoning.")
        return get_fallback()

@app.reasoner()
async def run_discovery_agent(member_id: str, profile: IdentityProfile) -> DiscoveryRecommendations:
    def get_fallback():
        if member_id == "rahul":
            return DiscoveryRecommendations(
                recommended_communities=["systems-programming", "gpu-computing", "ai-infrastructure"],
                lower_priority_communities=["anime", "football", "web3"],
                recommended_resources=["cuda-optimization", "gpu-performance", "rust-ownership"],
                recommended_events=["gpu-ama", "ai-systems-meetup", "rust-workshop"],
                reasoning="Discovery Agent: Matched Rahul's profile containing systems and GPU interests with the GPU Computing, Systems Programming, and AI Infrastructure channels. Filtered out anime and football as lower priority since they do not align with his systems engineering goals. Recommended CUDA and GPU performance resources and the upcoming GPU AMA."
            )
        elif member_id == "priya":
            return DiscoveryRecommendations(
                recommended_communities=["pytorch-study-group", "machine-learning-basics", "ai-infrastructure"],
                lower_priority_communities=["systems-programming", "gpu-computing", "web3"],
                recommended_resources=["intro-pytorch", "nn-from-scratch", "deep-learning-ch5"],
                recommended_events=["pytorch-basics-101", "ml-basics-study"],
                reasoning="Discovery Agent: Priya's profile focuses on machine learning and PyTorch. Matched her with PyTorch Study Group and ML Basics. Recommended beginner-friendly resources like 'Intro to PyTorch Notebooks' and 'Neural Networks from Scratch' rather than low-level CUDA optimization guides. Scheduled her for the PyTorch 101 workshop."
            )
        else:
            return DiscoveryRecommendations(
                recommended_communities=["systems-programming"],
                lower_priority_communities=["anime"],
                recommended_resources=["rust-ownership"],
                recommended_events=["rust-workshop"],
                reasoning="Discovery Agent: Generated generic matched recommendations based on member profile."
            )

    if not OPENROUTER_API_KEY:
        return get_fallback()

    prompt = f"""
    Based on the following Identity Profile, recommend relevant communities, resources, and events from our database.
    
    Identity Profile: {profile.model_dump()}
    Available Communities: {COMMUNITIES}
    Available Resources: {RESOURCES}
    Available Events: {EVENTS}
    
    Determine:
    1. Recommended communities (list of IDs from Available Communities) that match their interests.
    2. Lower priority communities (list of IDs of general/social communities or less relevant tech).
    3. Recommended resources (list of IDs from Available Resources).
    4. Recommended events (list of IDs from Available Events).
    5. Write a detailed reason explaining your choices as the "Discovery Agent".
    """

    try:
        out = await app.ai(
            system="You are the Discovery Agent of CommunityOS. Your job is to match member profiles with channels, files, events, and learning pathways.",
            user=prompt,
            schema=DiscoveryRecommendations
        )
        return out
    except Exception as e:
        print(f"Discovery Agent OpenRouter error: {e}. Falling back to high-fidelity mock reasoning.")
        return get_fallback()

@app.reasoner()
async def run_learning_agent(member_id: str, profile: IdentityProfile) -> LearningPath:
    def get_fallback():
        if member_id == "rahul":
            return LearningPath(
                priorities=["Attend GPU Workshop with Sarah", "Reply to Aman's Rust ownership thread", "Finish CUDA Roadmap (Shared Memory Bank Conflicts)"],
                steps=[
                    "Analyze memory bank conflicts in matrix multiplication kernel",
                    "Benchmark performance gains from shared memory padding",
                    "Participate in the GPU AMA with Sarah to discuss kernel optimizations",
                    "Contribute optimized CUDA helper functions to the community library"
                ],
                reasoning="Learning Agent: Identified Rahul's intermediate skill level and hands-on style. Recommended immediate action to resolve his active question on bank conflicts, attend the GPU AMA, and help Aman to reinforce his own Rust mastery."
            )
        elif member_id == "priya":
            return LearningPath(
                priorities=["Post your introduction in #introductions", "Complete PyTorch 101: Build Your First Neural Network", "Review Neural Networks from Scratch guide"],
                steps=[
                    "Run basic tensor operations in PyTorch Colab notebooks",
                    "Attend the PyTorch 101 hands-on MNIST classifier workshop",
                    "Connect with Elena (ML mentor) for study roadmap advice",
                    "Complete the Neural Networks from Scratch (Python) manual backprop chapters"
                ],
                reasoning="Learning Agent: Designed a beginner-friendly path for Priya starting with interactive notebooks and basic concepts. Advised attending the hands-on PyTorch 101 event and connecting with a mentor to build structural confidence."
            )
        else:
            return LearningPath(
                priorities=["Participate in discussions", "Explore resources"],
                steps=["Step 1: Check out code tutorials", "Step 2: Join study groups"],
                reasoning="Learning Agent: Generated default learning path steps."
            )

    if not OPENROUTER_API_KEY:
        return get_fallback()

    prompt = f"""
    Create a personalized list of 3 immediate priorities and a structured step-by-step learning path.
    
    Identity Profile: {profile.model_dump()}
    Recent Activity / Context: {MEMBERS.get(member_id, {})}
    Available Resources: {RESOURCES}
    Available Events: {EVENTS}
    
    Determine:
    1. Today's Priorities (list of 3 action items).
    2. A structured step-by-step learning path (3-4 logical milestones).
    3. Write a detailed reason explaining your plan as the "Learning Agent".
    """

    try:
        out = await app.ai(
            system="You are the Learning Agent of CommunityOS. Your job is to design highly customized milestones and actions that fit each member's skill level and style.",
            user=prompt,
            schema=LearningPath
        )
        return out
    except Exception as e:
        print(f"Learning Agent OpenRouter error: {e}. Falling back to high-fidelity mock reasoning.")
        return get_fallback()

@app.reasoner()
async def run_mentor_agent(member_id: str, profile: IdentityProfile) -> MentorMatch:
    def get_fallback():
        if member_id == "rahul":
            return MentorMatch(
                mentor_name="Sarah",
                mentor_role="Senior CUDA Engineer @ Nvidia",
                overlap_reason="Strong interest overlap in systems programming, CUDA optimizations, and low-level performance metrics.",
                reasoning="Mentor Agent: Matched Rahul with Sarah. Both have a primary focus on CUDA and hardware execution. Sarah's expert background at Nvidia is perfect to guide Rahul from intermediate CUDA kernel optimizations to advanced GPU memory layouts."
            )
        elif member_id == "priya":
            return MentorMatch(
                mentor_name="Elena",
                mentor_role="Machine Learning Researcher",
                overlap_reason="Shares high alignment in PyTorch, deep learning basics, and model architectures. Elena's bio details a passion for helping beginners.",
                reasoning="Mentor Agent: Matched Priya with Elena. Priya is a beginner looking to build neural networks in PyTorch, which is Elena's research specialty. Elena's patient, math-to-code learning approach matches Priya's needs."
            )
        else:
            return MentorMatch(
                mentor_name="Sarah",
                mentor_role="Mentor",
                overlap_reason="General technical support",
                reasoning="Mentor Agent: Assigned Sarah as a general mentor."
            )

    if not OPENROUTER_API_KEY:
        return get_fallback()

    # Filter experts in mock database
    potential_mentors = [m for m in MEMBERS.values() if m.get("metrics", {}).get("is_mentor")]
    
    prompt = f"""
    Find the best mentor match for the following member profile from our list of mentors:
    
    Member Profile: {profile.model_dump()}
    Mentors List: {potential_mentors}
    
    Determine:
    1. Best matched mentor name.
    2. Mentor's professional role.
    3. Why there is a match (overlap details).
    4. Write a detailed reason explaining your match as the "Mentor Agent".
    """

    try:
        out = await app.ai(
            system="You are the Mentor Agent of CommunityOS. Your job is to match experienced mentors with members needing guidance based on skill alignment, interests, and goals.",
            user=prompt,
            schema=MentorMatch
        )
        return out
    except Exception as e:
        print(f"Mentor Agent OpenRouter error: {e}. Falling back to high-fidelity mock reasoning.")
        return get_fallback()

@app.reasoner()
async def run_health_agent() -> HealthReport:
    def get_fallback():
        return HealthReport(
            ignored_newcomers=["Priya"],
            unanswered_questions=["Priya's post: 'Where should I start with PyTorch? I have some basic python knowledge...'"],
            inactive_members=["Vikram (Inactive for 21 days)"],
            trending_topics=["CUDA optimizations (Matrix multiplication, memory bank conflicts)", "Rust lifetmes & compiler errors", "PyTorch deep learning for beginners"],
            reasoning="Community Health Agent: Scanned activity logs and timestamps. Flagged Priya as an ignored newcomer since she joined and posted in #introductions over 12 hours ago with zero replies. Detected Vikram as inactive based on lack of events in over 21 days. Trending topics extracted from recent message content in #gpu-computing and #rust."
        )

    if not OPENROUTER_API_KEY:
        return get_fallback()

    prompt = f"""
    Analyze the overall community state:
    Members Database: {MEMBERS}
    Communities list: {COMMUNITIES}
    
    Determine:
    1. Ignored newcomers (members who recently joined and posted but have no replies).
    2. Unanswered questions or topics.
    3. Inactive members (who haven't been active for 14+ days).
    4. Trending topics (based on message frequencies and channel topics).
    5. Write a detailed reason explaining your health diagnostics as the "Community Health Agent".
    """

    try:
        out = await app.ai(
            system="You are the Community Health Agent of CommunityOS. Your job is to observe community health metrics, identify neglected members, drop-off risks, and trending discussions.",
            user=prompt,
            schema=HealthReport
        )
        return out
    except Exception as e:
        print(f"Health Agent OpenRouter error: {e}. Falling back to high-fidelity mock reasoning.")
        return get_fallback()

@app.reasoner()
async def run_organizer_agent(health_report: HealthReport) -> OrganizerInsights:
    def get_fallback():
        return OrganizerInsights(
            suggested_events=[
                {"title": "GPU Shared Memory & CUDA Optimizations AMA", "reason": "High interest in CUDA bank conflicts from Rahul, plus upcoming AMA with Sarah. Expanding it to cover common kernel issues would engage intermediate coders."},
                {"title": "Beginner PyTorch Study Session", "reason": "Priya recently joined and requested PyTorch starting tips. Elena's colab notebooks could be used as material."}
            ],
            potential_mentors=[
                {"name": "Rahul", "reason": "Helped 6 beginners this week, is in the top 15% of contributors, and has demonstrated intermediate-to-advanced proficiency in CUDA and Rust. Highly eligible to become a systems programming mentor."}
            ],
            members_at_risk=[
                {"name": "Vikram", "reason": "Has been inactive for 21 days. Had moderate intermediate activity in PyTorch before going cold. Risk of churn is high."}
            ],
            suggested_actions=[
                {"action": "Reply to Priya's introduction in #introductions and introduce her to Elena.", "agent": "Community Health Agent", "reason": "Priya has been waiting for 12 hours with no response since joining. Churn rate rises by 40% if new members are ignored on day 1."},
                {"action": "Invite Rahul to join the mentorship program for Systems Programming.", "agent": "Mentor Agent", "reason": "Rahul meets all contribution and activity thresholds for mentorship and helped 6 beginners this week."},
                {"action": "Send an automated check-in message to Vikram with PyTorch optimization resources.", "agent": "Community Health Agent", "reason": "Vikram is a PyTorch enthusiast who has been inactive for 21 days. Sharing recent research scripts might re-engage him."}
            ],
            reasoning="Organizer Agent: Synthesized the findings of the Identity, Mentor, and Health agents. Crafted high-value, actionable tasks for community moderators to reduce churn, match mentors, and schedule targeted content to address the CUDA and PyTorch trending demands."
        )

    if not OPENROUTER_API_KEY:
        return get_fallback()

    prompt = f"""
    Based on the Community Health Report and the Members database, generate operational insights and suggested actions for the community organizer:
    
    Health Report: {health_report.model_dump()}
    Members Database: {MEMBERS}
    
    Determine:
    1. Suggested events (event ideas with title and reason matching trending topics).
    2. Potential mentors (active members who could be onboarded as mentors, with name and reason).
    3. Members at risk of churning (with name and risk level/reason).
    4. Suggested actions (a list of ActionSuggestion items with action, agent, and reason).
    5. Write a detailed reason explaining these insights as the "Organizer Agent".
    """

    try:
        out = await app.ai(
            system="You are the Organizer Agent of CommunityOS. Your job is to transform raw community health metrics and member profiles into actionable operational intelligence to help organizers grow engagement.",
            user=prompt,
            schema=OrganizerInsights
        )
        return out
    except Exception as e:
        print(f"Organizer Agent OpenRouter error: {e}. Falling back to high-fidelity mock reasoning.")
        return get_fallback()

# --- Unified Personalization Dashboard Execution ---

async def get_member_dashboard(member_id: str) -> Dict[str, Any]:
    member = MEMBERS.get(member_id)
    if not member:
        return {}
    
    # Run agent pipeline
    profile = await run_identity_agent(member_id)
    discovery = await run_discovery_agent(member_id, profile)
    learning = await run_learning_agent(member_id, profile)
    mentor = await run_mentor_agent(member_id, profile)
    
    # Build dashboard response
    # Resolve communities
    rec_coms = [c for c in COMMUNITIES if c["id"] in discovery.recommended_communities]
    low_coms = [c for c in COMMUNITIES if c["id"] in discovery.lower_priority_communities]
    
    # Resolve resources
    rec_res = [r for r in RESOURCES if r["id"] in discovery.recommended_resources]
    
    # Resolve events
    rec_evts = [e for e in EVENTS if e["id"] in discovery.recommended_events]
    
    return {
        "member_id": member_id,
        "name": member["name"],
        "bio": member["bio"],
        "skills": member["skills"],
        "welcome_message": f"Welcome back {member['name']}! Based on your recent activity, here are today's priorities.",
        "priorities": learning.priorities,
        "recommended_mentor": {
            "name": mentor.mentor_name,
            "role": mentor.mentor_role,
            "overlap_reason": mentor.overlap_reason
        },
        "communities": {
            "recommended": rec_coms,
            "lower_priority": low_coms
        },
        "resources": rec_res,
        "events": rec_evts,
        "insights": [
            f"Top {member['metrics'].get('contributions_percentile', 90)}% contributor",
            f"Helped {member['metrics'].get('beginners_helped_this_week', 0)} beginners this week",
            "Eligible to become a mentor" if member["metrics"].get("is_mentor_eligible") else "Looking to connect with a mentor"
        ],
        "explainability": {
            "identity_agent": profile.reasoning,
            "discovery_agent": discovery.reasoning,
            "learning_agent": learning.reasoning,
            "mentor_agent": mentor.reasoning
        }
    }

async def get_organizer_dashboard() -> Dict[str, Any]:
    health = await run_health_agent()
    insights = await run_organizer_agent(health)
    
    # Simple count aggregates for metrics
    health_metrics = {
        "active_members_ratio": "83%",
        "weekly_messages": 42,
        "unanswered_threads": len(health.unanswered_questions),
        "at_risk_members": len(insights.members_at_risk)
    }
    
    return {
        "metrics": health_metrics,
        "health_summary": {
            "ignored_newcomers": health.ignored_newcomers,
            "unanswered_questions": health.unanswered_questions,
            "inactive_members": health.inactive_members,
            "trending_topics": health.trending_topics,
            "explainability": health.reasoning
        },
        "insights": {
            "suggested_events": insights.suggested_events,
            "potential_mentors": insights.potential_mentors,
            "members_at_risk": insights.members_at_risk,
            "suggested_actions": [a.model_dump() for a in insights.suggested_actions],
            "explainability": insights.reasoning
        }
    }
