"""
CommuneOS Agent-Level Unit Tests
Tests each of the 6 agents individually under successful LLM generation and fallback modes.
"""
import pytest
import sys
import os
from unittest.mock import AsyncMock, patch
from services.llm_service import LLMService

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.identity_agent import IdentityAgent
from agents.discovery_agent import DiscoveryAgent
from agents.learning_agent import LearningAgent
from agents.mentor_agent import MentorAgent
from agents.health_agent import HealthAgent
from agents.organizer_agent import OrganizerAgent
from services.cache_service import cache_service


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before each test to ensure isolated agent runs."""
    cache_service.clear_prefix("")
    yield
    cache_service.clear_prefix("")


# Mock user data for testing
MOCK_USER_DATA = {
    "username": "TestUser",
    "bio": "Low-level system engineer interested in GPU coding and parallel programming.",
    "skills": {"C++": 4, "Linux": 3},
    "skill_level": "Intermediate",
    "interests": ["Systems Programming", "GPU Architecture"],
    "goals": ["Learn CUDA", "Optimize kernels"],
    "tags": ["cpp", "linux", "gpu"],
    "timezone": "Asia/Kolkata",
}


# ─── Identity Agent Tests ─────────────────────────────────────────────────────

@pytest.mark.asyncio
@patch.object(LLMService, "complete_json")
async def test_identity_agent_success(mock_llm):
    """IdentityAgent parses user profile and returns structured output on LLM success."""
    llm_output = {
        "detected_skills": [
            {"name": "C++", "proficiency": "Advanced", "confidence": 0.9, "source": "stated"},
            {"name": "CUDA", "proficiency": "Beginner", "confidence": 0.6, "source": "inferred"}
        ],
        "expertise_areas": ["Systems Programming"],
        "growth_areas": ["GPU Architecture", "CUDA"],
        "learning_preference": "kinesthetic",
        "overall_confidence": 0.85,
        "summary": "Systems programmer expanding into GPU optimization."
    }
    mock_llm.return_value = (llm_output, False)

    agent = IdentityAgent()
    result = await agent.run("testuser", MOCK_USER_DATA)

    assert result["success"] is True
    assert result["is_fallback"] is False
    assert result["data"]["user_id"] == "testuser"
    assert len(result["data"]["detected_skills"]) == 2
    assert result["data"]["learning_preference"] == "kinesthetic"
    mock_llm.assert_called_once()


@pytest.mark.asyncio
@patch.object(LLMService, "complete_json")
async def test_identity_agent_fallback(mock_llm):
    """IdentityAgent gracefully falls back to mock data if LLM fails."""
    mock_llm.return_value = (None, True)

    agent = IdentityAgent()
    result = await agent.run("testuser", MOCK_USER_DATA)

    assert result["success"] is True
    assert result["is_fallback"] is True
    assert "detected_skills" in result["data"]
    assert len(result["data"]["detected_skills"]) > 0


# ─── Discovery Agent Tests ────────────────────────────────────────────────────

@pytest.mark.asyncio
@patch.object(LLMService, "complete_json")
async def test_discovery_agent_success(mock_llm):
    """DiscoveryAgent recommends channels and resources on LLM success."""
    identity_data = {
        "detected_skills": [{"name": "C++", "proficiency": "Advanced"}],
        "expertise_areas": ["Systems Programming"],
        "growth_areas": ["CUDA"],
        "learning_preference": "kinesthetic"
    }
    llm_output = {
        "recommended_channels": [
            {"channel_id": "ch-cuda", "name": "GPU & Accelerators", "relevance_score": 0.95, "reason": "CUDA growth area", "difficulty": "Advanced"}
        ],
        "recommended_resources": [
            {"resource_id": "res-002", "title": "CUDA Shared Memory & Coalescing", "type": "Article", "duration": "25 min", "difficulty": "Advanced", "relevance_score": 0.92, "reason": "GPU optimization"}
        ],
        "discovery_priority": ["GPU & Accelerators"]
    }
    mock_llm.return_value = (llm_output, False)

    agent = DiscoveryAgent()
    result = await agent.run("testuser", MOCK_USER_DATA, identity_data=identity_data)

    assert result["success"] is True
    assert result["is_fallback"] is False
    assert len(result["data"]["recommended_channels"]) == 1
    assert result["data"]["recommended_channels"][0]["channel_id"] == "ch-cuda"


@pytest.mark.asyncio
@patch.object(LLMService, "complete_json")
async def test_discovery_agent_fallback(mock_llm):
    """DiscoveryAgent falls back to mock channels/resources on LLM failure."""
    mock_llm.return_value = (None, True)

    agent = DiscoveryAgent()
    result = await agent.run("testuser", MOCK_USER_DATA, identity_data={})

    assert result["success"] is True
    assert result["is_fallback"] is True
    assert len(result["data"]["recommended_channels"]) > 0


# ─── Learning Agent Tests ─────────────────────────────────────────────────────

@pytest.mark.asyncio
@patch.object(LLMService, "complete_json")
async def test_learning_agent_success(mock_llm):
    """LearningAgent generates roadmaps on LLM success."""
    llm_output = {
        "roadmap_title": "CUDA Beginner Pathway",
        "total_weeks": 4,
        "daily_commitment_minutes": 45,
        "milestones": [
            {"week": 1, "title": "CUDA Basics", "objectives": ["CUDA execution model"], "resources": ["res-001"], "estimated_hours": 4.0}
        ],
        "daily_checklist": [
            {"task_id": "task-testuser-0", "task": "Read CUDA intro", "type": "reading", "duration_minutes": 20, "resource_link": None, "completed": False}
        ],
        "estimated_completion_date": "July 30, 2026"
    }
    mock_llm.return_value = (llm_output, False)

    agent = LearningAgent()
    result = await agent.run("testuser", MOCK_USER_DATA, identity_data={})

    assert result["success"] is True
    assert result["is_fallback"] is False
    assert result["data"]["roadmap_title"] == "CUDA Beginner Pathway"
    assert result["data"]["total_weeks"] == 4


@pytest.mark.asyncio
@patch.object(LLMService, "complete_json")
async def test_learning_agent_fallback(mock_llm):
    """LearningAgent falls back to mock roadmap on LLM failure."""
    mock_llm.return_value = (None, True)

    agent = LearningAgent()
    result = await agent.run("testuser", MOCK_USER_DATA, identity_data={})

    assert result["success"] is True
    assert result["is_fallback"] is True
    assert "roadmap_title" in result["data"]
    assert len(result["data"]["milestones"]) > 0


# ─── Mentor Agent Tests ───────────────────────────────────────────────────────

@pytest.mark.asyncio
@patch.object(LLMService, "complete_json")
async def test_mentor_agent_success(mock_llm):
    """MentorAgent matches a primary and backup mentor on LLM success."""
    llm_output = {
        "primary_mentor": {
            "mentor_id": "mentor-sarah",
            "name": "Sarah Jenkins",
            "role": "Principal GPU Engineer at NVIDIA",
            "avatar": "SJ",
            "expertise_areas": ["CUDA"],
            "compatibility_score": 0.95,
            "match_reason": "CUDA alignment",
            "availability": "Flexible",
            "teaching_style": "Hands-on",
            "years_experience": 8
        },
        "backup_mentors": [],
        "suggested_meeting_schedule": "Weekly",
        "introduction_template": "Hello Sarah..."
    }
    mock_llm.return_value = (llm_output, False)

    agent = MentorAgent()
    result = await agent.run("testuser", MOCK_USER_DATA, identity_data={}, learning_data={})

    assert result["success"] is True
    assert result["is_fallback"] is False
    assert result["data"]["primary_mentor"]["mentor_id"] == "mentor-sarah"


@pytest.mark.asyncio
@patch.object(LLMService, "complete_json")
async def test_mentor_agent_fallback(mock_llm):
    """MentorAgent falls back to mock mentor list on LLM failure."""
    mock_llm.return_value = (None, True)

    agent = MentorAgent()
    result = await agent.run("testuser", MOCK_USER_DATA, identity_data={}, learning_data={})

    assert result["success"] is True
    assert result["is_fallback"] is True
    assert "primary_mentor" in result["data"]


# ─── Health Agent Tests ───────────────────────────────────────────────────────

@pytest.mark.asyncio
@patch.object(LLMService, "complete_json")
async def test_health_agent_success(mock_llm):
    """HealthAgent analyzes community statistics and returns health report on LLM success."""
    llm_output = {
        "community_health_score": 0.82,
        "total_members": 150,
        "active_members_7d": 75,
        "at_risk_members": [],
        "topic_gaps": [],
        "trending_topics": ["CUDA", "C++"],
        "engagement_trend": "rising",
        "summary": "Community health is stable."
    }
    mock_llm.return_value = (llm_output, False)

    agent = HealthAgent()
    result = await agent.run_community()

    assert result["success"] is True
    assert result["is_fallback"] is False
    assert result["data"]["community_health_score"] == 0.82
    assert result["data"]["total_members"] == 150


@pytest.mark.asyncio
@patch.object(LLMService, "complete_json")
async def test_health_agent_fallback(mock_llm):
    """HealthAgent falls back to mock health metrics on LLM failure."""
    mock_llm.return_value = (None, True)

    agent = HealthAgent()
    result = await agent.run_community()

    assert result["success"] is True
    assert result["is_fallback"] is True
    assert "community_health_score" in result["data"]


# ─── Organizer Agent Tests ────────────────────────────────────────────────────

@pytest.mark.asyncio
@patch.object(LLMService, "complete_json")
async def test_organizer_agent_success(mock_llm):
    """OrganizerAgent generates operational items on LLM success."""
    llm_output = {
        "action_items": [
            {
                "action_id": "action-1",
                "title": "Welcome new cohort",
                "description": "Send message",
                "priority": "critical",
                "category": "welcome",
                "assignee": "manager",
                "deadline": "2026-07-01",
                "expected_impact": "high",
                "completed": False
            }
        ],
        "event_suggestions": [],
        "automation_recommendations": [],
        "resource_allocation": "Split evenly",
        "summary": "Focus on welcome actions."
    }
    mock_llm.return_value = (llm_output, False)

    agent = OrganizerAgent()
    result = await agent.run_community(health_data={})

    assert result["success"] is True
    assert result["is_fallback"] is False
    assert len(result["data"]["action_items"]) == 1
    assert result["data"]["action_items"][0]["action_id"] == "action-1"


@pytest.mark.asyncio
@patch.object(LLMService, "complete_json")
async def test_organizer_agent_fallback(mock_llm):
    """OrganizerAgent falls back to mock action plan on LLM failure."""
    mock_llm.return_value = (None, True)

    agent = OrganizerAgent()
    result = await agent.run_community(health_data={})

    assert result["success"] is True
    assert result["is_fallback"] is True
    assert len(result["data"]["action_items"]) > 0
