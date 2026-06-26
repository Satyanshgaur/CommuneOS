import pytest
import sys
import os
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from services.db import users_table, resumes_table, identities_table, community_members_table

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_users():
    """Seed test users and memberships in the in-memory database."""
    # Reset
    users_table.clear()
    resumes_table.clear()
    identities_table.clear()
    community_members_table.clear()
    
    # Add a GPU user
    users_table["sprint2_user"] = {
        "user_id": "sprint2_user",
        "username": "Sprint2 User",
        "email": "sprint2@test.com",
        "bio": "Developer",
        "skills": {"Python": 4},
        "tags": ["python"],
        "interests": ["Machine Learning"],
        "goals": ["Learn CUDA"]
    }
    
    community_members_table["sprint2_user"] = {
        "user_id": "sprint2_user",
        "community_id": "comm-gpu",
        "role_id": "role-member"
    }


def test_get_profile():
    """GET /api/v1/profile retrieves the authenticated user's profile."""
    response = client.get("/api/v1/profile", headers={"X-User-Id": "sprint2_user"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["user_id"] == "sprint2_user"
    assert data["community_id"] == "comm-gpu"


@patch("services.github_service.get_github_profile_data")
@patch("agents.identity_agent.llm_service.complete_json")
def test_update_profile_and_github_enrichment(mock_llm, mock_gh):
    """PUT /api/v1/profile updates fields and triggers GitHub enrichment if username changes."""
    # Mock github service
    mock_gh.return_value = {
        "languages": ["C++", "CUDA"],
        "topics": ["gpgpu", "compiler"],
        "repo_summaries": []
    }
    # Mock LLM for IdentityAgent
    mock_llm.return_value = ({
        "skill_level": "Advanced",
        "skills": ["C++", "CUDA"],
        "technologies": ["Git"],
        "interests": ["Compilers"],
        "domains": ["GPU Infrastructure"],
        "goals": ["Build CUDA kernel"],
        "confidence_score": 0.9
    }, False)

    update_payload = {
        "experience_level": "Senior",
        "github_username": "gpu_ninja",
        "portfolio_url": "https://ninja.gpu",
        "career_goals": ["Build CUDA compiler"],
        "preferred_domains": ["AI Systems"],
        "availability": "15 hours/week"
    }

    response = client.put(
        "/api/v1/profile",
        json=update_payload,
        headers={"X-User-Id": "sprint2_user"}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

    # Retrieve updated profile
    profile = users_table["sprint2_user"]
    assert profile["experience_level"] == "Senior"
    assert profile["github_username"] == "gpu_ninja"
    assert profile["portfolio_url"] == "https://ninja.gpu"
    assert "C++" in profile["preferred_technologies"]
    assert "gpgpu" in profile["tags"]
    assert profile["availability"] == "15 hours/week"


@patch("services.resume_parser.llm_service.complete_json")
@patch("agents.identity_agent.llm_service.complete_json")
def test_resume_upload_and_identity_agent(mock_resume_llm, mock_identity_llm):
    """POST /api/v1/resume processes upload, extracts text, and triggers stateless Identity Agent."""
    # Mock resume LLM parsing
    mock_resume_llm.return_value = ({
        "skills": ["C++", "CUDA"],
        "technologies": ["Git", "CMake"],
        "frameworks": ["PyTorch"],
        "languages": ["English"],
        "education": [],
        "projects": [],
        "experience": [],
        "certifications": []
    }, False)
    
    # Mock Identity LLM parsing
    mock_identity_llm.return_value = ({
        "skill_level": "Advanced",
        "skills": ["C++", "CUDA"],
        "technologies": ["Git"],
        "interests": ["GPU Systems"],
        "domains": ["Systems"],
        "goals": ["Learn GPU kernels"],
        "confidence_score": 0.88
    }, False)

    # Use a dummy text file
    resume_content = b"Resume text: C++ CUDA developer at NVIDIA."
    
    response = client.post(
        "/api/v1/resume",
        files={"file": ("resume.txt", resume_content, "text/plain")},
        headers={"X-User-Id": "sprint2_user"}
    )
    
    assert response.status_code == 200
    res_data = response.json()["data"]
    assert res_data["resume_name"] == "resume.txt"
    assert "C++" in res_data["parsed_resume"]["skills"]
    assert res_data["identity_profile"]["skill_level"] == "Advanced"

    # Verify db stores
    assert "sprint2_user" in resumes_table
    assert "sprint2_user" in identities_table
    assert resumes_table["sprint2_user"]["skills"] == ["C++", "CUDA"]
    assert identities_table["sprint2_user"]["skill_level"] == "Advanced"


def test_get_identity():
    """GET /api/v1/identity retrieves identity profile from database."""
    # Directly seed identity
    identities_table["sprint2_user"] = {
        "skill_level": "Intermediate",
        "skills": ["Python"],
        "technologies": ["Git"],
        "interests": ["ML"],
        "domains": ["Systems"],
        "goals": ["Learn PyTorch"],
        "confidence_score": 0.8
    }

    response = client.get("/api/v1/identity", headers={"X-User-Id": "sprint2_user"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["skill_level"] == "Intermediate"
    assert data["confidence_score"] == 0.8


def test_community_knowledge_endpoints():
    """GET /resources, GET /projects, GET /events, and GET /learning-tracks return scoped data."""
    # Test resources
    response = client.get("/api/v1/resources", headers={"X-User-Id": "sprint2_user"})
    assert response.status_code == 200
    res_data = response.json()["data"]
    assert res_data["count"] > 0
    assert all(r["community_id"] == "comm-gpu" for r in res_data["resources"])

    # Test projects
    response = client.get("/api/v1/projects", headers={"X-User-Id": "sprint2_user"})
    assert response.status_code == 200
    proj_data = response.json()["data"]
    assert proj_data["count"] > 0
    assert all(p["community_id"] == "comm-gpu" for p in proj_data["projects"])

    # Test events
    response = client.get("/api/v1/events", headers={"X-User-Id": "sprint2_user"})
    assert response.status_code == 200
    evt_data = response.json()["data"]
    assert evt_data["count"] > 0
    assert all(e["community_id"] == "comm-gpu" for e in evt_data["events"])

    # Test learning tracks
    response = client.get("/api/v1/learning-tracks", headers={"X-User-Id": "sprint2_user"})
    assert response.status_code == 200
    track_data = response.json()["data"]
    assert track_data["count"] > 0
    assert all(t["community_id"] == "comm-gpu" for t in track_data["learning_tracks"])
