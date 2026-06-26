"""
CommuneOS Phase 1 — Basic Test Suite
Tests for models, mock data service, and API health endpoints.
"""
import pytest
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.user import UserProfile, UserCreateRequest
from models.agent_response import AgentResponse, IdentityAgentOutput
from services.mock_data import get_mock_identity, get_mock_discovery, get_mock_learning, get_mock_mentor, get_mock_health, get_mock_organizer, get_mock_user
from services.cache_service import cache_service
from utils.formatters import success_response, error_response


# ─── Model Tests ──────────────────────────────────────────────────────────────

def test_user_create_request_valid():
    """UserCreateRequest accepts valid data."""
    req = UserCreateRequest(
        username="testuser",
        bio="A test user for CommuneOS",
        tags=["python", "ml"],
        interests=["Machine Learning"],
        goals=["Learn PyTorch"],
    )
    assert req.username == "testuser"
    assert "python" in req.tags


def test_user_profile_creation():
    """UserProfile can be created and converts to dict."""
    profile = UserProfile(
        user_id="test-01",
        username="TestUser",
        bio="Test bio",
        skills={"Python": 3, "CUDA": 4},
        interests=["ML"],
    )
    assert profile.user_id == "test-01"
    assert profile.skills["Python"] == 3


def test_user_create_to_profile():
    """UserCreateRequest.to_user_profile() creates a valid UserProfile."""
    req = UserCreateRequest(username="newuser", bio="hello", tags=["python"])
    profile = req.to_user_profile()
    assert profile.username == "newuser"
    assert profile.user_id is not None


def test_user_id_lowercase():
    """user_id is normalized to lowercase."""
    profile = UserProfile(user_id="TestUser123", username="test")
    assert profile.user_id == "testuser123"


def test_user_skills_summary():
    """UserProfile.get_skills_summary() returns readable text."""
    profile = UserProfile(
        user_id="u1",
        username="u1",
        skills={"Python": 3, "CUDA": 5}
    )
    summary = profile.get_skills_summary()
    assert "Python" in summary
    assert "CUDA" in summary


# ─── Mock Data Tests ───────────────────────────────────────────────────────────

def test_mock_identity_returns_data():
    """get_mock_identity() returns valid identity data."""
    data = get_mock_identity("rahul")
    assert "detected_skills" in data
    assert len(data["detected_skills"]) > 0
    assert "learning_preference" in data
    assert 0.0 <= data["overall_confidence"] <= 1.0


def test_mock_identity_varies_by_user():
    """Different user_ids return different but valid data."""
    data1 = get_mock_identity("rahul")
    data2 = get_mock_identity("priya")
    # Both valid but may differ
    assert data1["user_id"] == "rahul"
    assert data2["user_id"] == "priya"


def test_mock_discovery_returns_channels():
    """get_mock_discovery() returns channel and resource recommendations."""
    data = get_mock_discovery("rahul")
    assert "recommended_channels" in data
    assert "recommended_resources" in data
    assert len(data["recommended_channels"]) > 0


def test_mock_learning_returns_roadmap():
    """get_mock_learning() returns a roadmap with milestones."""
    data = get_mock_learning("priya")
    assert "milestones" in data
    assert "daily_checklist" in data
    assert len(data["milestones"]) > 0
    assert data["total_weeks"] > 0


def test_mock_mentor_returns_mentor():
    """get_mock_mentor() returns a primary mentor."""
    data = get_mock_mentor("rahul")
    assert "primary_mentor" in data
    assert data["primary_mentor"] is not None
    assert "compatibility_score" in data["primary_mentor"]


def test_mock_health_returns_metrics():
    """get_mock_health() returns community health data."""
    data = get_mock_health()
    assert "community_health_score" in data
    assert 0.0 <= data["community_health_score"] <= 1.0
    assert "at_risk_members" in data
    assert "topic_gaps" in data


def test_mock_organizer_returns_actions():
    """get_mock_organizer() returns action items."""
    data = get_mock_organizer()
    assert "action_items" in data
    assert len(data["action_items"]) > 0
    assert "event_suggestions" in data


def test_mock_user_exists():
    """Mock user can be saved and retrieved in the store."""
    from services.mock_data import save_mock_user
    user_data = {
        "user_id": "test_user", "username": "Test User", "email": "test@example.com"
    }
    save_mock_user("test_user", user_data)
    retrieved = get_mock_user("test_user")
    assert retrieved is not None
    assert retrieved["username"] == "Test User"



def test_mock_user_not_found():
    """Unknown user returns None."""
    result = get_mock_user("nonexistent_user_xyz")
    assert result is None


# ─── Cache Tests ───────────────────────────────────────────────────────────────

def test_cache_set_get():
    """Cache set and get work correctly."""
    cache_service.set("test:key", {"value": 42}, ttl=60)
    result = cache_service.get("test:key")
    assert result == {"value": 42}


def test_cache_miss():
    """Cache miss returns None."""
    result = cache_service.get("nonexistent:key:xyz")
    assert result is None


def test_cache_delete():
    """Cache delete removes a key."""
    cache_service.set("test:delete", "hello", ttl=60)
    cache_service.delete("test:delete")
    assert cache_service.get("test:delete") is None


def test_cache_stats():
    """Cache stats return valid structure."""
    stats = cache_service.stats()
    assert "total_keys" in stats
    assert "active_keys" in stats


# ─── Response Formatter Tests ──────────────────────────────────────────────────

def test_success_response_structure():
    """success_response() returns correct envelope."""
    resp = success_response(data={"foo": "bar"}, request_id="req-123")
    assert resp["success"] is True
    assert resp["data"] == {"foo": "bar"}
    assert resp["error"] is None
    assert resp["request_id"] == "req-123"
    assert "timestamp" in resp


def test_error_response_structure():
    """error_response() returns correct envelope."""
    resp = error_response(error="Something went wrong")
    assert resp["success"] is False
    assert resp["error"] == "Something went wrong"
    assert resp["data"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
