# backend/main.py

import os
from typing import List
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Load env variables from .env if present
load_dotenv()

from backend.database import get_db, engine, Base
from backend.models import User, Community, CommunityMember
from backend.schemas import (
    UserRegister, UserLogin, Token, UserProfile, UserProfileUpdate,
    CommunityCreate, CommunityOut, CommunityMemberOut
)
from backend.auth import (
    verify_password, get_password_hash, create_access_token, get_current_user
)
from backend.agents import get_member_dashboard, get_organizer_dashboard

# Ensure database tables exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CommunityOS API",
    description="SaaS Backend with Authentication and Multi-Tenant Community Pipelines.",
    version="1.0.0"
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Root Endpoint ---
@app.get("/")
async def root():
    return {"message": "Welcome to CommunityOS API backend. Running successfully!"}

# --- Authentication & Profiles ---
@app.post("/api/auth/register", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserRegister, db: Session = Depends(get_db)):
    user_id_clean = user_in.id.lower().strip()
    if db.query(User).filter(User.id == user_id_clean).first():
        raise HTTPException(status_code=400, detail="Username/ID already exists.")
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered.")
        
    db_user = User(
        id=user_id_clean,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserProfile(
        id=db_user.id,
        email=db_user.email,
        full_name=db_user.full_name,
        bio=db_user.bio,
        skills=[],
        skill_level=db_user.skill_level,
        goals=db_user.goals,
        learning_style=db_user.learning_style,
        created_at=db_user.created_at
    )

@app.post("/api/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_id_clean = form_data.username.lower().strip()
    user = db.query(User).filter(User.id == user_id_clean).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
        
    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/auth/login-json", response_model=Token)
async def login_json(credentials: UserLogin, db: Session = Depends(get_db)):
    user_id_clean = credentials.id.lower().strip()
    user = db.query(User).filter(User.id == user_id_clean).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
        
    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=UserProfile)
async def get_me(current_user: User = Depends(get_current_user)):
    skills_list = [s.strip() for s in current_user.skills.split(",") if s.strip()] if current_user.skills else []
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        bio=current_user.bio,
        skills=skills_list,
        skill_level=current_user.skill_level,
        goals=current_user.goals,
        learning_style=current_user.learning_style,
        created_at=current_user.created_at
    )

@app.put("/api/auth/me", response_model=UserProfile)
async def update_me(profile_update: UserProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if profile_update.full_name is not None:
        current_user.full_name = profile_update.full_name
    if profile_update.bio is not None:
        current_user.bio = profile_update.bio
    if profile_update.skills is not None:
        current_user.skills = ",".join(profile_update.skills)
    if profile_update.skill_level is not None:
        current_user.skill_level = profile_update.skill_level
    if profile_update.goals is not None:
        current_user.goals = profile_update.goals
    if profile_update.learning_style is not None:
        current_user.learning_style = profile_update.learning_style
        
    db.commit()
    db.refresh(current_user)
    
    skills_list = [s.strip() for s in current_user.skills.split(",") if s.strip()] if current_user.skills else []
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        bio=current_user.bio,
        skills=skills_list,
        skill_level=current_user.skill_level,
        goals=current_user.goals,
        learning_style=current_user.learning_style,
        created_at=current_user.created_at
    )

# --- Multi-Tenant Communities ---
@app.post("/api/communities", response_model=CommunityOut)
async def create_community(comm: CommunityCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    slug_clean = comm.id.lower().strip()
    if db.query(Community).filter(Community.id == slug_clean).first():
        raise HTTPException(status_code=400, detail="Community slug already exists.")
    if db.query(Community).filter(Community.name == comm.name).first():
        raise HTTPException(status_code=400, detail="Community name already exists.")
        
    db_comm = Community(
        id=slug_clean,
        name=comm.name,
        category=comm.category,
        description=comm.description,
        created_by=current_user.id
    )
    db.add(db_comm)
    
    # Auto join creator as 'Owner'
    membership = CommunityMember(
        user_id=current_user.id,
        community_id=db_comm.id,
        role="Owner"
    )
    db.add(membership)
    db.commit()
    db.refresh(db_comm)
    return db_comm

@app.get("/api/communities", response_model=List[CommunityOut])
async def list_communities(db: Session = Depends(get_db)):
    return db.query(Community).all()

@app.post("/api/communities/{community_id}/join", response_model=CommunityMemberOut)
async def join_community(community_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    community_id_clean = community_id.lower().strip()
    community = db.query(Community).filter(Community.id == community_id_clean).first()
    if not community:
        raise HTTPException(status_code=404, detail="Community not found.")
        
    # Check if already joined
    existing = db.query(CommunityMember).filter(
        CommunityMember.user_id == current_user.id,
        CommunityMember.community_id == community_id_clean
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already a member of this community.")
        
    db_member = CommunityMember(
        user_id=current_user.id,
        community_id=community_id_clean,
        role="Member"
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

@app.get("/api/communities/my", response_model=List[CommunityOut])
async def list_my_communities(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    memberships = db.query(CommunityMember).filter(CommunityMember.user_id == current_user.id).all()
    community_ids = [m.community_id for m in memberships]
    return db.query(Community).filter(Community.id.in_(community_ids)).all()

# --- Agent Dashboard Pipelines ---
@app.get("/api/members/{member_id}")
async def get_member(member_id: str):
    member_id = member_id.lower().strip()
    if member_id not in ["rahul", "priya"]:
        raise HTTPException(status_code=404, detail="Member persona not found. Select 'rahul' or 'priya'.")
    try:
        data = await get_member_dashboard(member_id)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent runtime error: {str(e)}")

@app.get("/api/organizer")
async def get_organizer():
    try:
        data = await get_organizer_dashboard()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent runtime error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Allow running directly via python -m backend.main
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
