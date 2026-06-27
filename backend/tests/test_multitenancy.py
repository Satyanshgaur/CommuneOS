"""
CommuneOS Multi-Tenant Architecture Tests
Verifies community isolation, headers, middleware, and join workflows.
"""
import pytest
import sys
import os
from fastapi.testclient import TestClient

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from services.db import community_members_table, users_table

client = TestClient(app)


def test_list_communities():
    """GET /api/v1/community/list returns available communities."""
    response = client.get("/api/v1/community/list")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["communities"]) == 5
    assert any(c["community_id"] == "comm-gpu" for c in data["data"]["communities"])
    assert any(c["community_id"] == "comm-ml" for c in data["data"]["communities"])
    assert any(c["community_id"] == "comm-web" for c in data["data"]["communities"])
    assert any(c["community_id"] == "comm-sys" for c in data["data"]["communities"])
    assert any(c["community_id"] == "comm-data" for c in data["data"]["communities"])


def test_join_community_invalid():
    """POST /api/v1/community/join fails with invalid community_id."""
    response = client.post(
        "/api/v1/community/join",
        json={"user_id": "test_user_id_123", "community_id": "invalid-community"}
    )
    assert response.status_code == 400
    assert "does not exist" in response.json()["detail"]


def test_access_denied_without_auth():
    """Tenant middleware returns 401 if user id header is missing."""
    response = client.get("/api/v1/community/metrics")
    assert response.status_code == 401
    assert "Missing user identification" in response.json()["message"]


def test_access_denied_not_joined():
    """Tenant middleware returns 403 if user has not joined any community."""
    # Ensure user profile exists
    users_table["unjoined_user"] = {
        "user_id": "unjoined_user", "username": "unjoined", "email": "unjoined@test.com"
    }
    
    response = client.get("/api/v1/community/metrics", headers={"X-User-Id": "unjoined_user"})
    assert response.status_code == 403
    assert "User has not joined" in response.json()["message"]


def test_tenant_metrics_gpu():
    """User who joined comm-gpu gets gpu metrics, channels, and roadmaps."""
    # Setup user profile and community members entry
    users_table["gpu_user"] = {
        "user_id": "gpu_user", "username": "gpu_dev", "email": "gpu@test.com"
    }
    
    # Join community
    join_resp = client.post(
        "/api/v1/community/join",
        json={"user_id": "gpu_user", "community_id": "comm-gpu"}
    )
    assert join_resp.status_code == 200
    
    # Get metrics
    metrics_resp = client.get("/api/v1/community/metrics", headers={"X-User-Id": "gpu_user"})
    assert metrics_resp.status_code == 200
    metrics = metrics_resp.json()["data"]
    assert metrics["total_members"] == 1
    assert metrics["total_mentors"] == 1
    assert metrics["total_projects"] == 1
    assert metrics["total_events"] == 1
    
    # Get channels (scoped to comm-gpu)
    channels_resp = client.get("/api/v1/discovery/gpu_user/channels", headers={"X-User-Id": "gpu_user"})
    assert channels_resp.status_code == 200
    channels = channels_resp.json()["data"]["channels"]
    assert any(ch["channel_id"] == "ch-cuda" for ch in channels)
    assert not any(ch["channel_id"] == "ch-ml" for ch in channels)


def test_tenant_metrics_ml():
    """User who joined comm-ml gets ml metrics, channels, and roadmaps."""
    # Setup user profile and community members entry
    users_table["ml_user"] = {
        "user_id": "ml_user", "username": "ml_dev", "email": "ml@test.com"
    }
    
    # Join community
    join_resp = client.post(
        "/api/v1/community/join",
        json={"user_id": "ml_user", "community_id": "comm-ml"}
    )
    assert join_resp.status_code == 200
    
    # Get metrics
    metrics_resp = client.get("/api/v1/community/metrics", headers={"X-User-Id": "ml_user"})
    assert metrics_resp.status_code == 200
    metrics = metrics_resp.json()["data"]
    assert metrics["total_members"] == 1
    assert metrics["total_mentors"] == 1
    assert metrics["total_projects"] == 1
    assert metrics["total_events"] == 1
    
    # Get channels (scoped to comm-ml)
    channels_resp = client.get("/api/v1/discovery/ml_user/channels", headers={"X-User-Id": "ml_user"})
    assert channels_resp.status_code == 200
    channels = channels_resp.json()["data"]["channels"]
    assert any(ch["channel_id"] == "ch-ml" for ch in channels)
    assert not any(ch["channel_id"] == "ch-cuda" for ch in channels)


def test_tenant_isolation_cross_access():
    """User cannot query another community's user's data."""
    # Setup two users in different communities
    users_table["gpu_user_cross"] = {
        "user_id": "gpu_user_cross", "username": "gpu_dev_cross", "email": "gpu_cross@test.com"
    }
    users_table["ml_user_cross"] = {
        "user_id": "ml_user_cross", "username": "ml_dev_cross", "email": "ml_cross@test.com"
    }
    
    client.post("/api/v1/community/join", json={"user_id": "gpu_user_cross", "community_id": "comm-gpu"})
    client.post("/api/v1/community/join", json={"user_id": "ml_user_cross", "community_id": "comm-ml"})
    
    # ML user tries to query GPU user discovery channels
    response = client.get("/api/v1/discovery/gpu_user_cross/channels", headers={"X-User-Id": "ml_user_cross"})
    assert response.status_code == 403
    assert "Cannot access another community's data" in response.json()["detail"]
