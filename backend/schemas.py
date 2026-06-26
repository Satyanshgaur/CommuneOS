# backend/schemas.py

import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    id: str = Field(description="Unique username or ID (e.g. 'rahul123')")
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str

class UserLogin(BaseModel):
    id: str = Field(description="Username / Member ID")
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None

class UserProfile(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    bio: Optional[str] = None
    skills: List[str] = []
    skill_level: Optional[str] = "Beginner"
    goals: Optional[str] = None
    learning_style: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[List[str]] = None
    skill_level: Optional[str] = None
    goals: Optional[str] = None
    learning_style: Optional[str] = None

class CommunityCreate(BaseModel):
    id: str = Field(description="Unique identifier slug (e.g. 'systems-programming')")
    name: str
    category: str
    description: Optional[str] = None

class CommunityOut(BaseModel):
    id: str
    name: str
    category: str
    description: Optional[str] = None
    created_by: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class CommunityMemberOut(BaseModel):
    id: int
    user_id: str
    community_id: str
    role: str
    joined_at: datetime.datetime

    class Config:
        from_attributes = True
