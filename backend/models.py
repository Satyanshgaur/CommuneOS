# backend/models.py

import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)  # Can be a unique username like 'rahul' or a UUID
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    bio = Column(String, nullable=True)
    skills = Column(String, nullable=True)  # Store as comma-separated or JSON string
    skill_level = Column(String, nullable=True, default="Beginner")
    goals = Column(String, nullable=True)
    learning_style = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    memberships = relationship("CommunityMember", back_populates="user", cascade="all, delete-orphan")

class Community(Base):
    __tablename__ = "communities"

    id = Column(String, primary_key=True, index=True)  # Unique slug like 'systems-programming'
    name = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    members = relationship("CommunityMember", back_populates="community", cascade="all, delete-orphan")

class CommunityMember(Base):
    __tablename__ = "community_members"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    community_id = Column(String, ForeignKey("communities.id"), nullable=False)
    role = Column(String, nullable=False, default="Member")  # Owner, Admin, Moderator, Mentor, Member
    joined_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="memberships")
    community = relationship("Community", back_populates="members")
