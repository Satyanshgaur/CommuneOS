"""
CommuneOS Local Authentication Endpoints
Completely replaces Supabase with local user store authentication.
"""
import hashlib
import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel, EmailStr

from services.mock_data import get_mock_user, save_mock_user
from utils.logger import get_logger

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = get_logger("endpoint.auth")

_TOKENS_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "tokens.json")
_TOKENS_FILE = os.path.normpath(_TOKENS_FILE)

# In-memory token database
_token_store: Dict[str, str] = {}


def load_tokens():
    global _token_store
    try:
        if os.path.exists(_TOKENS_FILE):
            with open(_TOKENS_FILE, "r") as f:
                _token_store = json.load(f)
    except Exception as e:
        logger.warning(f"Could not load tokens: {e}")


def save_tokens():
    try:
        os.makedirs(os.path.dirname(_TOKENS_FILE), exist_ok=True)
        with open(_TOKENS_FILE, "w") as f:
            json.dump(_token_store, f, indent=2)
    except Exception as e:
        logger.warning(f"Could not save tokens: {e}")


load_tokens()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class RegisterRequest(BaseModel):
    user_id: str
    email: EmailStr
    password: str
    full_name: str


class LoginRequest(BaseModel):
    user_id: str
    password: str


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    tags: Optional[List[str]] = None
    skill_level: Optional[str] = None
    goals: Optional[List[str]] = None
    learning_style: Optional[str] = None


def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization token",
        )
    token = authorization.split(" ")[1]
    user_id = _token_store.get(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid token",
        )
    return user_id


@router.post("/register")
async def register(req: RegisterRequest):
    user = get_mock_user(req.user_id)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    password_hash = hash_password(req.password)
    user_dict = {
        "user_id": req.user_id,
        "username": req.user_id,
        "email": req.email,
        "full_name": req.full_name,
        "password_hash": password_hash,
        "bio": "",
        "tags": [],
        "interests": [],
        "goals": [],
        "skill_level": "Beginner",
        "learning_style": "visual",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "role": "member"
    }
    save_mock_user(req.user_id, user_dict)
    return {"success": True, "message": "User registered successfully"}


@router.post("/login-json")
async def login_json(req: LoginRequest):
    user = get_mock_user(req.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Handle password validation (allow standard passwords for seed accounts)
    password_hash = hash_password(req.password)
    stored_hash = user.get("password_hash")
    
    # Seed accounts: default password is "password"
    if not stored_hash and req.user_id in ["rahul", "priya", "organizer"]:
        if req.password != "password":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials for seed account. Use password 'password'"
            )
    elif stored_hash and stored_hash != password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    token = f"tok_{uuid.uuid4().hex}"
    _token_store[token] = req.user_id
    save_tokens()
    
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
async def get_me(user_id: str = Depends(get_current_user_id)):
    user = get_mock_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/me")
async def update_me(req: ProfileUpdateRequest, user_id: str = Depends(get_current_user_id)):
    user = get_mock_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    update_data = req.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        user[k] = v
        if k == "tags":
            user["interests"] = v
            
    user["updated_at"] = datetime.utcnow().isoformat()
    save_mock_user(user_id, user)
    return user
