"""
CommuneOS Community Metrics Endpoints
Health metrics, discovery, learning, and admin/organizer routes.
"""
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request

from api.v1.dependencies import get_request_id, validate_user_id_param
from models.community import ProgressUpdate, CommunityJoinRequest
from services.cache_service import cache_service
from services.mock_data import (
    get_mock_user, get_mock_discovery, get_mock_learning,
    get_mock_mentor, get_mock_health, get_mock_organizer
)
from utils.formatters import success_response
from utils.logger import get_logger

router = APIRouter(tags=["Community & Discovery"])
logger = get_logger("endpoint.community")


# ─── Community Join & List (Multi-Tenant) ──────────────────────────────────────

@router.post("/community/join")
async def join_community(
    payload: CommunityJoinRequest,
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """Assign a member to a community."""
    from services.db import community_members_table, communities_table
    user_id = payload.user_id.lower()
    community_id = payload.community_id.lower()
    
    if community_id not in communities_table:
        raise HTTPException(
            status_code=400,
            detail=f"Community '{payload.community_id}' does not exist. Available: {list(communities_table.keys())}"
        )
        
    community_members_table[user_id] = {
        "user_id": payload.user_id,
        "community_id": payload.community_id,
        "role_id": payload.role_id or "role-member"
    }
    
    # Invalidate cache for the user
    cache_service.clear_prefix(f"user:{payload.user_id}")
    cache_service.clear_prefix(f"agent:")
    
    logger.info(f"User {payload.user_id} joined community {payload.community_id}")
    return success_response(
        data={"user_id": payload.user_id, "community_id": payload.community_id, "joined": True},
        request_id=request_id,
        message=f"Joined community '{payload.community_id}' successfully"
    )


@router.get("/community/list")
async def list_communities(request_id: str = Depends(get_request_id)) -> Dict[str, Any]:
    """List all available communities."""
    from services.db import communities_table
    communities = list(communities_table.values())
    return success_response(
        data={"communities": communities, "count": len(communities)},
        request_id=request_id
    )


# ─── Community Metrics ────────────────────────────────────────────────────────

@router.get("/community/metrics")
async def get_community_metrics(request: Request, request_id: str = Depends(get_request_id)) -> Dict[str, Any]:
    """Get overall community health metrics filtered by community_id."""
    community_id = request.state.community_id
    cache_key = cache_service.community_key(f"metrics:{community_id}")
    cached = cache_service.get(cache_key)
    if cached:
        return success_response(data=cached, request_id=request_id)
    
    health_data = get_mock_health(community_id)
    metrics = {
        "community_health_score": health_data["community_health_score"],
        "total_members": health_data["total_members"],
        "active_members_7d": health_data["active_members_7d"],
        "trending_topics": health_data["trending_topics"],
        "engagement_trend": health_data["engagement_trend"],
    }
    cache_service.set(cache_key, metrics, ttl=1800)
    return success_response(data=metrics, request_id=request_id)


@router.get("/community/members/at-risk")
async def get_at_risk_members(request: Request, request_id: str = Depends(get_request_id)) -> Dict[str, Any]:
    """Get list of community members at risk of churning filtered by community_id."""
    community_id = request.state.community_id
    health_data = get_mock_health(community_id)
    at_risk = health_data.get("at_risk_members", [])
    return success_response(
        data={"at_risk_members": at_risk, "count": len(at_risk)},
        request_id=request_id
    )


@router.get("/community/gaps")
async def get_community_gaps(request: Request, request_id: str = Depends(get_request_id)) -> Dict[str, Any]:
    """Get underserved topic areas in the community filtered by community_id."""
    community_id = request.state.community_id
    health_data = get_mock_health(community_id)
    gaps = health_data.get("topic_gaps", [])
    return success_response(
        data={"topic_gaps": gaps, "count": len(gaps)},
        request_id=request_id
    )


@router.get("/community/trends")
async def get_community_trends(request: Request, request_id: str = Depends(get_request_id)) -> Dict[str, Any]:
    """Get trending topics in the community filtered by community_id."""
    community_id = request.state.community_id
    health_data = get_mock_health(community_id)
    return success_response(
        data={
            "trending_topics": health_data.get("trending_topics", []),
            "engagement_trend": health_data.get("engagement_trend", "stable"),
        },
        request_id=request_id
    )


# ─── Discovery Endpoints ───────────────────────────────────────────────────────

@router.get("/discovery/{user_id}/channels")
async def get_recommended_channels(
    request: Request,
    user_id: str = Depends(validate_user_id_param),
    request_id: str = Depends(get_request_id),
) -> Dict[str, Any]:
    """Get channel recommendations for a user filtered by community_id."""
    if request.state.user_id.lower() != user_id.lower():
        from services.db import community_members_table
        requester_comm = request.state.community_id
        target_member_info = community_members_table.get(user_id.lower())
        if not target_member_info or target_member_info["community_id"] != requester_comm:
            raise HTTPException(status_code=403, detail="Access denied. Cannot access another community's data.")
            
    community_id = request.state.community_id
    cache_key = cache_service.agent_key(f"discovery_channels:{community_id}", user_id)
    cached = cache_service.get(cache_key)
    if cached:
        return success_response(data=cached, request_id=request_id)
    
    user_data = get_mock_user(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
    
    discovery = get_mock_discovery(user_id, user_data, community_id=community_id)
    result = {
        "channels": discovery["recommended_channels"],
        "count": len(discovery["recommended_channels"]),
        "is_fallback": discovery.get("_is_fallback", False),
    }
    cache_service.set(cache_key, result, ttl=3600)
    return success_response(data=result, request_id=request_id)


@router.get("/discovery/{user_id}/resources")
async def get_recommended_resources(
    request: Request,
    user_id: str = Depends(validate_user_id_param),
    request_id: str = Depends(get_request_id),
) -> Dict[str, Any]:
    """Get resource recommendations for a user filtered by community_id."""
    if request.state.user_id.lower() != user_id.lower():
        from services.db import community_members_table
        requester_comm = request.state.community_id
        target_member_info = community_members_table.get(user_id.lower())
        if not target_member_info or target_member_info["community_id"] != requester_comm:
            raise HTTPException(status_code=403, detail="Access denied. Cannot access another community's data.")
            
    community_id = request.state.community_id
    user_data = get_mock_user(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
    
    discovery = get_mock_discovery(user_id, user_data, community_id=community_id)
    return success_response(
        data={
            "resources": discovery["recommended_resources"],
            "count": len(discovery["recommended_resources"]),
        },
        request_id=request_id
    )


@router.get("/discovery/{user_id}/mentors")
async def get_mentor_matches(
    request: Request,
    user_id: str = Depends(validate_user_id_param),
    request_id: str = Depends(get_request_id),
) -> Dict[str, Any]:
    """Get mentor matches for a user filtered by community_id."""
    if request.state.user_id.lower() != user_id.lower():
        from services.db import community_members_table
        requester_comm = request.state.community_id
        target_member_info = community_members_table.get(user_id.lower())
        if not target_member_info or target_member_info["community_id"] != requester_comm:
            raise HTTPException(status_code=403, detail="Access denied. Cannot access another community's data.")
            
    community_id = request.state.community_id
    user_data = get_mock_user(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
    
    mentor_data = get_mock_mentor(user_id, user_data, community_id=community_id)
    return success_response(
        data={
            "primary_mentor": mentor_data["primary_mentor"],
            "backup_mentors": mentor_data["backup_mentors"],
            "suggested_schedule": mentor_data["suggested_meeting_schedule"],
        },
        request_id=request_id
    )


@router.post("/discovery/{user_id}/feedback")
async def log_recommendation_feedback(
    request: Request,
    user_id: str = Depends(validate_user_id_param),
    feedback: Dict[str, Any] = {},
    request_id: str = Depends(get_request_id),
) -> Dict[str, Any]:
    """Log user feedback on recommendations."""
    if request.state.user_id.lower() != user_id.lower():
        from services.db import community_members_table
        requester_comm = request.state.community_id
        target_member_info = community_members_table.get(user_id.lower())
        if not target_member_info or target_member_info["community_id"] != requester_comm:
            raise HTTPException(status_code=403, detail="Access denied. Cannot access another community's data.")
            
    logger.info(f"Feedback from {user_id}: {feedback}")
    return success_response(data={"logged": True}, request_id=request_id, message="Feedback recorded")


# ─── Learning Endpoints ────────────────────────────────────────────────────────

@router.get("/learning/{user_id}/roadmap")
async def get_learning_roadmap(
    request: Request,
    user_id: str = Depends(validate_user_id_param),
    request_id: str = Depends(get_request_id),
) -> Dict[str, Any]:
    """Get the personalized learning roadmap for a user filtered by community_id."""
    if request.state.user_id.lower() != user_id.lower():
        from services.db import community_members_table
        requester_comm = request.state.community_id
        target_member_info = community_members_table.get(user_id.lower())
        if not target_member_info or target_member_info["community_id"] != requester_comm:
            raise HTTPException(status_code=403, detail="Access denied. Cannot access another community's data.")
            
    community_id = request.state.community_id
    user_data = get_mock_user(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
    
    learning = get_mock_learning(user_id, user_data, community_id=community_id)
    return success_response(
        data={
            "roadmap_title": learning["roadmap_title"],
            "total_weeks": learning["total_weeks"],
            "daily_commitment_minutes": learning["daily_commitment_minutes"],
            "milestones": learning["milestones"],
            "estimated_completion_date": learning["estimated_completion_date"],
        },
        request_id=request_id
    )


@router.get("/learning/{user_id}/checklist")
async def get_daily_checklist(
    request: Request,
    user_id: str = Depends(validate_user_id_param),
    request_id: str = Depends(get_request_id),
) -> Dict[str, Any]:
    """Get today's action checklist for a user filtered by community_id."""
    if request.state.user_id.lower() != user_id.lower():
        from services.db import community_members_table
        requester_comm = request.state.community_id
        target_member_info = community_members_table.get(user_id.lower())
        if not target_member_info or target_member_info["community_id"] != requester_comm:
            raise HTTPException(status_code=403, detail="Access denied. Cannot access another community's data.")
            
    community_id = request.state.community_id
    user_data = get_mock_user(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
    
    learning = get_mock_learning(user_id, user_data, community_id=community_id)
    return success_response(
        data={"checklist": learning["daily_checklist"]},
        request_id=request_id
    )


@router.post("/learning/{user_id}/progress")
async def log_learning_progress(
    progress: ProgressUpdate,
    request: Request,
    user_id: str = Depends(validate_user_id_param),
    request_id: str = Depends(get_request_id),
) -> Dict[str, Any]:
    """Log a learning task completion for a user."""
    if request.state.user_id.lower() != user_id.lower():
        from services.db import community_members_table
        requester_comm = request.state.community_id
        target_member_info = community_members_table.get(user_id.lower())
        if not target_member_info or target_member_info["community_id"] != requester_comm:
            raise HTTPException(status_code=403, detail="Access denied. Cannot access another community's data.")
            
    logger.info(f"Progress update for {user_id}: task={progress.task_id} completed={progress.completed}")
    return success_response(
        data={"user_id": user_id, "task_id": progress.task_id, "recorded": True},
        request_id=request_id,
        message="Progress logged"
    )


@router.get("/learning/{user_id}/milestones")
async def get_milestones(
    request: Request,
    user_id: str = Depends(validate_user_id_param),
    request_id: str = Depends(get_request_id),
) -> Dict[str, Any]:
    """Get milestone progress for a user filtered by community_id."""
    if request.state.user_id.lower() != user_id.lower():
        from services.db import community_members_table
        requester_comm = request.state.community_id
        target_member_info = community_members_table.get(user_id.lower())
        if not target_member_info or target_member_info["community_id"] != requester_comm:
            raise HTTPException(status_code=403, detail="Access denied. Cannot access another community's data.")
            
    community_id = request.state.community_id
    user_data = get_mock_user(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
    
    learning = get_mock_learning(user_id, user_data, community_id=community_id)
    return success_response(
        data={"milestones": learning["milestones"]},
        request_id=request_id
    )


# ─── Organizer/Admin Endpoints ────────────────────────────────────────────────

@router.get("/organizer/actions")
async def get_organizer_actions(request: Request, request_id: str = Depends(get_request_id)) -> Dict[str, Any]:
    """Get prioritized action items for community organizers filtered by community_id."""
    community_id = request.state.community_id
    cache_key = cache_service.community_key(f"organizer_actions:{community_id}")
    cached = cache_service.get(cache_key)
    if cached:
        return success_response(data=cached, request_id=request_id)
    
    organizer_data = get_mock_organizer(community_id)
    result = {"action_items": organizer_data["action_items"], "count": len(organizer_data["action_items"])}
    cache_service.set(cache_key, result, ttl=1800)
    return success_response(data=result, request_id=request_id)


@router.get("/organizer/events")
async def get_suggested_events(request: Request, request_id: str = Depends(get_request_id)) -> Dict[str, Any]:
    """Get event suggestions for the community filtered by community_id."""
    community_id = request.state.community_id
    organizer_data = get_mock_organizer(community_id)
    return success_response(
        data={
            "events": organizer_data["event_suggestions"],
            "count": len(organizer_data["event_suggestions"]),
        },
        request_id=request_id
    )


@router.post("/organizer/actions/{action_id}/complete")
async def complete_action(
    action_id: str,
    request: Request,
    request_id: str = Depends(get_request_id),
) -> Dict[str, Any]:
    """Mark an organizer action as completed."""
    community_id = request.state.community_id
    logger.info(f"Action marked complete: {action_id} in community {community_id}")
    
    # Update completion status in the mock DB actions table
    from services.db import actions_table
    found = False
    for a in actions_table:
        if a["action_id"] == action_id and a["community_id"] == community_id:
            a["completed"] = True
            found = True
            break
            
    cache_service.clear_prefix(cache_service.community_key(f"organizer_actions:{community_id}"))
    return success_response(
        data={"action_id": action_id, "completed": True},
        request_id=request_id,
        message="Action marked as completed"
    )


@router.post("/organizer/automation/trigger")
async def trigger_automation(
    payload: Optional[Dict[str, Any]] = None,
    request_id: str = Depends(get_request_id),
) -> Dict[str, Any]:
    """Manually trigger a community automation."""
    logger.info(f"Automation triggered: {payload}")
    return success_response(
        data={"triggered": True, "payload": payload},
        request_id=request_id,
        message="Automation triggered"
    )
