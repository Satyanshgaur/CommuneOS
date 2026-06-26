"""
CommuneOS Profile and Knowledge Endpoints
Includes profile CRUD, resume upload, identity agent, and community scoped data.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File

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
    
    # Trigger IdentityAgent run to update identities_table
    from agents.identity_agent import IdentityAgent
    try:
        await IdentityAgent().run_stateless(user_id)
    except Exception as e:
        logger.error(f"Failed to run IdentityAgent on profile update: {e}")
        
    return success_response(
        data={"user_id": user_id, "updated": True},
        request_id=request_id,
        message="Profile updated successfully"
    )


# ─── POST /resume ─────────────────────────────────────────────────────────────
@router.post("/resume")
async def upload_resume(
    request: Request,
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
