import pytest
import sys
import os
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from services.db import (
    users_table, resumes_table, identities_table, community_members_table,
    recommendations_table, learning_roadmaps_table, mentor_matches_table,
    mentor_requests_table, pipeline_hashes
)

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_users():
    """Seed test users and memberships in the in-memory database."""
    users_table.clear()
    resumes_table.clear()
    identities_table.clear()
    community_members_table.clear()
    recommendations_table.clear()
    learning_roadmaps_table.clear()
    mentor_matches_table.clear()
    mentor_requests_table.clear()
    pipeline_hashes.clear()
    
    # Add a GPU user
    users_table["sprint3_user"] = {
        "user_id": "sprint3_user",
        "username": "Sprint3 User",
        "email": "sprint3@test.com",
        "bio": "GPU Systems engineer",
        "skills": {"Python": 3, "CUDA": 2},
        "tags": ["python", "cuda"],
        "interests": ["GPU Systems"],
        "goals": ["Learn CUDA kernel optimization"]
    }
    
    community_members_table["sprint3_user"] = {
        "user_id": "sprint3_user",
        "community_id": "comm-gpu",
        "role_id": "role-member"
    }


def test_get_recommendations_initial():
    """GET /api/v1/recommendations automatically triggers pipeline and saves recommendations."""
    response = client.get("/api/v1/recommendations", headers={"X-User-Id": "sprint3_user"})
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    data = res_data["data"]
    
    # Validate structure based on DiscoveryAgent output
    assert "channels" in data
    assert "projects" in data
    assert "events" in data
    assert "resources" in data
    assert "study_groups" in data
    
    # Check that it's persisted in db
    assert "sprint3_user" in recommendations_table


def test_get_learning_roadmap_initial():
    """GET /api/v1/learning-roadmap retrieves personalized roadmap and persists it."""
    response = client.get("/api/v1/learning-roadmap", headers={"X-User-Id": "sprint3_user"})
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    data = res_data["data"]
    
    assert "roadmap_title" in data
    assert "milestones" in data
    assert "daily_checklist" in data
    assert "progress_percent" in data
    
    assert "sprint3_user" in learning_roadmaps_table


def test_update_learning_progress():
    """POST /api/v1/learning/progress toggles milestone completion and updates progress percent."""
    # Run once to initialize roadmap
    client.get("/api/v1/learning-roadmap", headers={"X-User-Id": "sprint3_user"})
    assert "sprint3_user" in learning_roadmaps_table
    
    # Initially progress is 0.0
    roadmap = learning_roadmaps_table["sprint3_user"]
    assert roadmap["progress_percent"] == 0.0
    
    # Mark first milestone completed (week 1)
    response = client.post(
        "/api/v1/learning/progress",
        json={"week": 1, "completed": True},
        headers={"X-User-Id": "sprint3_user"}
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["success"] is True
    assert data["progress_percent"] > 0.0
    
    # Verify in DB
    updated_roadmap = learning_roadmaps_table["sprint3_user"]
    assert updated_roadmap["progress_percent"] > 0.0
    assert updated_roadmap["milestones"][0]["completed"] is True


def test_get_mentors_and_request():
    """GET /api/v1/mentors fetches recommendations, POST /api/v1/mentor/request creates request."""
    # Get mentors
    response = client.get("/api/v1/mentors", headers={"X-User-Id": "sprint3_user"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert "primary_mentor" in data
    primary = data["primary_mentor"]
    assert primary is not None
    mentor_id = primary["mentor_id"]
    
    # Request that mentor
    response = client.post(
        "/api/v1/mentor/request",
        json={"mentor_id": mentor_id},
        headers={"X-User-Id": "sprint3_user"}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    
    # Verify request is recorded
    assert len(mentor_requests_table) == 1
    req = mentor_requests_table[0]
    assert req["user_id"] == "sprint3_user"
    assert req["mentor_id"] == mentor_id
    assert req["status"] == "pending"


def test_recommendations_refresh():
    """POST /api/v1/recommendations/refresh enqueues a new background task run."""
    response = client.post("/api/v1/recommendations/refresh", headers={"X-User-Id": "sprint3_user"})
    assert response.status_code == 200
    assert response.json()["success"] is True
