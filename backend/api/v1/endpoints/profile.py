"""
CommuneOS Profile and Knowledge Endpoints
Includes profile CRUD, resume upload, identity agent, and community scoped data.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, BackgroundTasks

from api.v1.dependencies import get_request_id
from utils.formatters import success_response, error_response
from utils.logger import get_logger

router = APIRouter(tags=["Sprint 2 - Profile & Community"])
logger = get_logger("endpoint.profile")


# ─── GET /profile ─────────────────────────────────────────────────────────────
@router.get("/profile")
async def get_profile(request: Request, request_id: str = Depends(get_request_id)) -> Dict[str, Any]:
    """Retrieve the current authenticated user's profile."""
    user_id = request.state.user_id
    from services.db import users_table, community_members_table
    
    profile = users_table.get(user_id.lower())
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile for user '{user_id}' not found."
        )
        
    # Enrich with community membership info
    member_info = community_members_table.get(user_id.lower())
    profile_dict = dict(profile)
    if member_info:
        profile_dict["community_id"] = member_info["community_id"]
        profile_dict["role_id"] = member_info["role_id"]
        
    return success_response(data=profile_dict, request_id=request_id)


# ─── PUT /profile ─────────────────────────────────────────────────────────────
@router.put("/profile")
async def update_profile(
    request: Request,
    update_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """Update the current authenticated user's profile and trigger LLM identity enrichment if GitHub changes."""
    user_id = request.state.user_id
    from services.db import users_table
    
    profile = users_table.get(user_id.lower())
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile for user '{user_id}' not found."
        )
        
    old_github = profile.get("github_username")
    new_github = update_data.get("github_username")
    
    # Merge update fields
    for key, value in update_data.items():
        # Prevent overwriting user_id
        if key == "user_id":
            continue
        profile[key] = value
        
    profile["updated_at"] = datetime.utcnow().isoformat()
    
    # If GitHub username has changed, fetch and enrich profile with languages/topics
    if new_github and new_github != old_github:
        from services.github_service import get_github_profile_data
        try:
            gh_data = await get_github_profile_data(new_github)
            if gh_data:
                profile["github_username"] = new_github
                profile["github_url"] = f"https://github.com/{new_github}"
                
                # Enrich preferred technologies with languages used
                langs = gh_data.get("languages", [])
                curr_tech = profile.get("preferred_technologies", [])
                profile["preferred_technologies"] = list(set(curr_tech + langs))
                
                # Enrich tags with topics
                topics = gh_data.get("topics", [])
                curr_tags = profile.get("tags", [])
                profile["tags"] = list(set(curr_tags + topics))
                
                logger.info(f"Enriched profile for {user_id} with GitHub user {new_github}")
        except Exception as e:
            logger.error(f"GitHub enrichment failed for {new_github}: {e}")
            
    users_table[user_id.lower()] = profile
    
    # Invalidate cache
    from services.cache_service import cache_service
    cache_service.clear_prefix(f"user:{user_id}")
    cache_service.clear_prefix(f"agent:")
    
    # Trigger Sprint 3 pipeline in background
    from services.orchestrator import run_sprint3_pipeline
    background_tasks.add_task(run_sprint3_pipeline, user_id)
        
    return success_response(
        data={"user_id": user_id, "updated": True},
        request_id=request_id,
        message="Profile updated successfully"
    )


# ─── POST /resume ─────────────────────────────────────────────────────────────
@router.post("/resume")
async def upload_resume(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """Upload a resume file, parse it into structured JSON, and trigger the Identity Agent to update profile in DB."""
    user_id = request.state.user_id
    from services.db import resumes_table, users_table
    
    contents = await file.read()
    filename = file.filename
    
    # Extract text from file (PDF or TXT)
    from services.resume_parser import extract_text, parse_resume_text
    text = extract_text(contents, filename)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to extract text from the uploaded resume file. Make sure it is a valid PDF or text file."
        )
        
    # Parse text to structured JSON
    parsed_json = await parse_resume_text(text)
    resumes_table[user_id.lower()] = parsed_json
    
    # Update profile resume name in db
    profile = users_table.get(user_id.lower())
    if profile:
        profile["resume_name"] = filename
        profile["updated_at"] = datetime.utcnow().isoformat()
        users_table[user_id.lower()] = profile
        
    # Trigger IdentityAgent run (stateless!)
    from agents.identity_agent import IdentityAgent
    identity_data = {}
    try:
        identity_data = await IdentityAgent().run_stateless(user_id)
    except Exception as e:
        logger.error(f"Failed to run IdentityAgent after resume upload: {e}")
        
    # Clear cache
    from services.cache_service import cache_service
    cache_service.clear_prefix(f"user:{user_id}")
    cache_service.clear_prefix(f"agent:")
    
    # Trigger Sprint 3 pipeline in background
    from services.orchestrator import run_sprint3_pipeline
    background_tasks.add_task(run_sprint3_pipeline, user_id)
    
    return success_response(
        data={
            "resume_name": filename,
            "parsed_resume": parsed_json,
            "identity_profile": identity_data
        },
        request_id=request_id,
        message="Resume uploaded and processed successfully"
    )


# ─── GET /identity ────────────────────────────────────────────────────────────
@router.get("/identity")
async def get_identity(request: Request, request_id: str = Depends(get_request_id)) -> Dict[str, Any]:
    """Retrieve the structured identity profile for the current user from the database."""
    user_id = request.state.user_id
    from services.db import identities_table
    
    identity = identities_table.get(user_id.lower())
    if not identity:
        # If not present, run IdentityAgent statelessly to generate it
        from agents.identity_agent import IdentityAgent
        try:
            identity = await IdentityAgent().run_stateless(user_id)
        except Exception as e:
            logger.error(f"Failed to generate identity for {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate identity profile."
            )
            
    return success_response(data=identity, request_id=request_id)


# ─── GET /resources ───────────────────────────────────────────────────────────
@router.get("/resources")
async def get_resources(request: Request, request_id: str = Depends(get_request_id)) -> Dict[str, Any]:
    """Get community resources scoped by community_id."""
    community_id = request.state.community_id
    from services.db import get_resources_by_community
    
    resources = get_resources_by_community(community_id)
    return success_response(data={"resources": resources, "count": len(resources)}, request_id=request_id)


# ─── GET /projects ────────────────────────────────────────────────────────────
@router.get("/projects")
async def get_projects(request: Request, request_id: str = Depends(get_request_id)) -> Dict[str, Any]:
    """Get community projects scoped by community_id."""
    community_id = request.state.community_id
    from services.db import get_projects_by_community
    
    projects = get_projects_by_community(community_id)
    return success_response(data={"projects": projects, "count": len(projects)}, request_id=request_id)


# ─── GET /events ──────────────────────────────────────────────────────────────
@router.get("/events")
async def get_events(request: Request, request_id: str = Depends(get_request_id)) -> Dict[str, Any]:
    """Get community events scoped by community_id."""
    community_id = request.state.community_id
    from services.db import get_events_by_community
    
    events = get_events_by_community(community_id)
    return success_response(data={"events": events, "count": len(events)}, request_id=request_id)


# ─── GET /learning-tracks ─────────────────────────────────────────────────────
@router.get("/learning-tracks")
async def get_learning_tracks(request: Request, request_id: str = Depends(get_request_id)) -> Dict[str, Any]:
    """Get community learning tracks scoped by community_id."""
    community_id = request.state.community_id
    from services.db import learning_tracks_table
    
    track = learning_tracks_table.get(community_id)
    tracks = [track] if track else []
    return success_response(data={"learning_tracks": tracks, "count": len(tracks)}, request_id=request_id)


# ─── GET /recommendations ─────────────────────────────────────────────────────
@router.get("/recommendations")
async def get_recommendations(request: Request, request_id: str = Depends(get_request_id)) -> Dict[str, Any]:
    """Get personalized recommendations scoped by community_id and user."""
    user_id = request.state.user_id
    from services.db import recommendations_table
    from services.orchestrator import run_sprint3_pipeline
    
    recs = recommendations_table.get(user_id.lower())
    if not recs:
        # Run pipeline synchronously to initialize if not present
        res = await run_sprint3_pipeline(user_id)
        recs = res.get("recommendations", {})
        
    return success_response(data=recs, request_id=request_id)


# ─── POST /recommendations/refresh ────────────────────────────────────────────
@router.post("/recommendations/refresh")
async def refresh_recommendations(
    request: Request,
    background_tasks: BackgroundTasks,
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """Manually trigger background refresh of personalization pipeline."""
    user_id = request.state.user_id
    from services.orchestrator import run_sprint3_pipeline
    
    background_tasks.add_task(run_sprint3_pipeline, user_id, force_refresh=True)
    return success_response(
        data={"status": "processing", "message": "Personalization pipeline manual refresh triggered in background."},
        request_id=request_id
    )


# ─── GET /learning-roadmap ────────────────────────────────────────────────────
@router.get("/learning-roadmap")
async def get_learning_roadmap(request: Request, request_id: str = Depends(get_request_id)) -> Dict[str, Any]:
    """Get personalized learning roadmap."""
    user_id = request.state.user_id
    from services.db import learning_roadmaps_table
    from services.orchestrator import run_sprint3_pipeline
    
    roadmap = learning_roadmaps_table.get(user_id.lower())
    if not roadmap:
        # Run pipeline synchronously to initialize if not present
        res = await run_sprint3_pipeline(user_id)
        roadmap = res.get("learning_roadmap", {})
        
    return success_response(data=roadmap, request_id=request_id)


# ─── POST /learning/progress ──────────────────────────────────────────────────
@router.post("/learning/progress")
async def update_learning_progress(
    request: Request,
    payload: Dict[str, Any],
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """Mark roadmap milestones or checklist tasks complete/incomplete."""
    user_id = request.state.user_id
    from services.db import learning_roadmaps_table
    
    roadmap = learning_roadmaps_table.get(user_id.lower())
    if not roadmap:
        raise HTTPException(status_code=404, detail="Learning roadmap not found. Please personalize first.")
        
    milestone_week = payload.get("week")
    task_id = payload.get("task_id")
    completed = payload.get("completed", True)
    
    updated = False
    
    if milestone_week is not None:
        for m in roadmap.get("milestones", []):
            if m.get("week") == milestone_week:
                m["completed"] = completed
                updated = True
                
    if task_id is not None:
        for t in roadmap.get("daily_checklist", []):
            if t.get("task_id") == task_id:
                t["completed"] = completed
                updated = True
                
    # Recalculate progress percent
    milestones = roadmap.get("milestones", [])
    total_milestones = len(milestones)
    completed_milestones = sum(1 for m in milestones if m.get("completed", False))
    
    progress_percent = (completed_milestones / total_milestones * 100) if total_milestones > 0 else 0.0
    roadmap["progress_percent"] = round(progress_percent, 1)
    
    learning_roadmaps_table[user_id.lower()] = roadmap
    
    return success_response(
        data={
            "success": True, 
            "updated": updated, 
            "progress_percent": roadmap["progress_percent"],
            "roadmap": roadmap
        },
        request_id=request_id,
        message="Learning progress updated successfully"
    )


# ─── GET /mentors ─────────────────────────────────────────────────────────────
@router.get("/mentors")
async def get_mentors(request: Request, request_id: str = Depends(get_request_id)) -> Dict[str, Any]:
    """Get personalized mentor matches."""
    user_id = request.state.user_id
    from services.db import mentor_matches_table
    from services.orchestrator import run_sprint3_pipeline
    
    matches = mentor_matches_table.get(user_id.lower())
    if not matches:
        res = await run_sprint3_pipeline(user_id)
        matches = res.get("mentor_matches", {})
        
    return success_response(data=matches, request_id=request_id)


# ─── POST /mentor/request ─────────────────────────────────────────────────────
@router.post("/mentor/request")
async def request_mentor(
    request: Request,
    payload: Dict[str, Any],
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """Submit a mentor guidance request."""
    user_id = request.state.user_id
    mentor_id = payload.get("mentor_id")
    if not mentor_id:
        raise HTTPException(status_code=400, detail="Missing mentor_id in request payload.")
        
    from services.db import mentor_requests_table, get_mentors_by_community
    community_id = request.state.community_id
    
    # Verify mentor belongs to the user's community
    community_mentors = get_mentors_by_community(community_id)
    mentor_exists = any(m["mentor_id"] == mentor_id for m in community_mentors)
    if not mentor_exists:
        raise HTTPException(status_code=400, detail="Mentor not found in your community catalog.")
        
    # Check if a request already exists
    for r in mentor_requests_table:
        if r["user_id"].lower() == user_id.lower() and r["mentor_id"] == mentor_id:
            return success_response(
                data=r, 
                request_id=request_id, 
                message="Mentor request already pending."
            )
            
    import uuid
    new_request = {
        "request_id": f"req-{uuid.uuid4().hex[:8]}",
        "user_id": user_id,
        "mentor_id": mentor_id,
        "status": "pending",
        "requested_at": datetime.utcnow().isoformat()
    }
    mentor_requests_table.append(new_request)
    
    return success_response(
        data=new_request, 
        request_id=request_id, 
        message="Mentor request submitted successfully."
    )


# ─── GET /mentor/requests ─────────────────────────────────────────────────────
@router.get("/mentor/requests")
async def get_mentor_requests(request: Request, request_id: str = Depends(get_request_id)) -> Dict[str, Any]:
    """Get all mentor requests submitted by the user."""
    user_id = request.state.user_id
    from services.db import mentor_requests_table
    user_requests = [r for r in mentor_requests_table if r["user_id"].lower() == user_id.lower()]
    return success_response(data={"requests": user_requests}, request_id=request_id)
