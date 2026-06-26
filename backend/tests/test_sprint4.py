import pytest
import sys
import os
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from services.db import (
    users_table, community_members_table, mentors_table,
    projects_table, events_table, mentor_requests_table
)

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_sprint4_test_data():
    """Seed test users, memberships, mentors, projects, and events in the database."""
    users_table.clear()
    community_members_table.clear()
    mentor_requests_table.clear()
    
    # 1. Create a GPU community user (active)
    users_table["gpu_active_user"] = {
        "user_id": "gpu_active_user",
        "username": "GPU Active User",
        "email": "gpu_active@test.com",
        "bio": "Expert graphics developer",
        "skills": {"CUDA": 5},
        "created_at": (datetime.utcnow() - timedelta(days=2)).isoformat(),
        "last_active": (datetime.utcnow() - timedelta(days=1)).isoformat()
    }
    community_members_table["gpu_active_user"] = {
        "user_id": "gpu_active_user",
        "community_id": "comm-gpu",
        "role_id": "role-member"
    }

    # 2. Create an inactive GPU community user (inactive for 15 days)
    users_table["gpu_inactive_user"] = {
        "user_id": "gpu_inactive_user",
        "username": "GPU Inactive User",
        "email": "gpu_inactive@test.com",
        "bio": "Legacy shader writer",
        "skills": {"C++": 4},
        "created_at": (datetime.utcnow() - timedelta(days=20)).isoformat(),
        "last_active": (datetime.utcnow() - timedelta(days=15)).isoformat()
    }
    community_members_table["gpu_inactive_user"] = {
        "user_id": "gpu_inactive_user",
        "community_id": "comm-gpu",
        "role_id": "role-member"
    }

    # 3. Create a GPU user with incomplete profile (no skills)
    users_table["gpu_incomplete_user"] = {
        "user_id": "gpu_incomplete_user",
        "username": "GPU Incomplete User",
        "email": "gpu_inc@test.com",
        "bio": "Learning CUDA",
        "skills": {},
        "created_at": (datetime.utcnow() - timedelta(days=1)).isoformat(),
        "last_active": (datetime.utcnow() - timedelta(minutes=5)).isoformat()
    }
    community_members_table["gpu_incomplete_user"] = {
        "user_id": "gpu_incomplete_user",
        "community_id": "comm-gpu",
        "role_id": "role-member"
    }

    # 4. Create an ML active user
    users_table["ml_active_user"] = {
        "user_id": "ml_active_user",
        "username": "ML Active User",
        "email": "ml_active@test.com",
        "bio": "PyTorch researcher",
        "skills": {"Python": 4, "PyTorch": 4},
        "created_at": (datetime.utcnow() - timedelta(days=3)).isoformat(),
        "last_active": (datetime.utcnow() - timedelta(days=2)).isoformat()
    }
    community_members_table["ml_active_user"] = {
        "user_id": "ml_active_user",
        "community_id": "comm-ml",
        "role_id": "role-member"
    }

    # 5. Mentor Requests (gpu_active_user has an approved mentor request)
    mentor_requests_table.append({
        "request_id": "req-1",
        "user_id": "gpu_active_user",
        "mentor_id": "mentor-sarah",
        "status": "approved",
        "requested_at": (datetime.utcnow() - timedelta(days=3)).isoformat()
    })


def test_get_community_metrics():
    """GET /api/v1/community/metrics calculates and returns correct database metrics."""
    # Test for GPU community
    response = client.get("/api/v1/community/metrics", headers={"X-User-Id": "gpu_active_user"})
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    
    metrics = res_data["data"]
    # Total members = gpu_active_user + gpu_inactive_user + gpu_incomplete_user = 3
    assert metrics["total_members"] == 3
    # Active members (within 7 days) = gpu_active_user + gpu_incomplete_user = 2
    assert metrics["active_members"] == 2
    # New members (joined within 7 days) = gpu_active_user + gpu_incomplete_user = 2
    assert metrics["new_members"] == 2
    
    # Total mentors, projects, events scoped to comm-gpu
    assert metrics["total_mentors"] == 1  # mentor-sarah
    assert metrics["total_projects"] == 1  # proj-cuda
    assert metrics["total_events"] == 1  # evt-gpu-ws


def test_get_community_health():
    """GET /api/v1/community/health calculates deterministic health status correctly."""
    response = client.get("/api/v1/community/health", headers={"X-User-Id": "gpu_active_user"})
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    
    health = res_data["data"]
    # 1. Inactive 14d+ = gpu_inactive_user
    assert len(health["inactive_14d_members"]) == 1
    assert health["inactive_14d_members"][0]["user_id"] == "gpu_inactive_user"
    
    # 2. Incomplete profiles = gpu_incomplete_user (no skills)
    assert len(health["incomplete_profiles"]) == 1
    assert health["incomplete_profiles"][0]["user_id"] == "gpu_incomplete_user"
    
    # 3. Members without mentor = gpu_inactive_user + gpu_incomplete_user = 2 (gpu_active_user has approved mentor)
    assert len(health["members_without_mentor"]) == 2
    assert any(m["user_id"] == "gpu_inactive_user" for m in health["members_without_mentor"])
    assert any(m["user_id"] == "gpu_incomplete_user" for m in health["members_without_mentor"])
    
    # Health score check: should be less than 1.0 because of issues
    assert health["community_health_score"] < 1.0
    assert health["community_health_score"] > 0.0


def test_health_metrics_multi_tenant_isolation():
    """Multi-tenant isolation ensures metrics and health are scoped to correct community."""
    # Fetch ML metrics
    ml_response = client.get("/api/v1/community/metrics", headers={"X-User-Id": "ml_active_user"})
    assert ml_response.status_code == 200
    ml_metrics = ml_response.json()["data"]
    # Total members = ml_active_user = 1
    assert ml_metrics["total_members"] == 1
    assert ml_metrics["active_members"] == 1
    
    # Fetch GPU metrics again to verify no cross-leakage
    gpu_response = client.get("/api/v1/community/metrics", headers={"X-User-Id": "gpu_active_user"})
    gpu_metrics = gpu_response.json()["data"]
    assert gpu_metrics["total_members"] == 3
