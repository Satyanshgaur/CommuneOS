"""
CommuneOS Community Data Models
Schemas for community-level metrics and admin data.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CommunityMetrics(BaseModel):
    """Aggregated community health metrics."""
    total_members: int = Field(default=0)
    active_members: int = Field(default=0, description="Active in last 7 days")
    new_members_this_week: int = Field(default=0)
    health_score: float = Field(default=0.75, ge=0.0, le=1.0)
    avg_engagement_score: float = Field(default=0.5, ge=0.0, le=1.0)
    churn_risk_count: int = Field(default=0)
    trending_topics: List[str] = Field(default_factory=list)
    underserved_areas: List[str] = Field(default_factory=list)
    response_time_median_hours: float = Field(default=2.0)
    generated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class ChannelMetrics(BaseModel):
    """Metrics for a single community channel."""
    channel_id: str
    name: str
    member_count: int = Field(default=0)
    messages_this_week: int = Field(default=0)
    active_members: int = Field(default=0)
    unanswered_questions: int = Field(default=0)
    trend: str = Field(default="stable", description="rising/stable/declining")


class LearningProgress(BaseModel):
    """User's learning progress data."""
    user_id: str
    path_name: str
    total_tasks: int = Field(default=10)
    completed_tasks: int = Field(default=0)
    progress_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    current_milestone: Optional[str] = None
    streak_days: int = Field(default=0)
    last_activity: Optional[datetime] = None


class ProgressUpdate(BaseModel):
    """Request body for logging learning progress."""
    task_id: str
    completed: bool = Field(default=True)
    time_spent_minutes: Optional[int] = None
    notes: Optional[str] = None


class CommunityProfile(BaseModel):
    """
    Complete community profile for the admin/organizer dashboard.
    Combines Health + Organizer agent outputs.
    """
    metrics: CommunityMetrics
    at_risk_member_count: int = Field(default=0)
    top_gaps: List[str] = Field(default_factory=list)
    pending_actions: int = Field(default=0)
    generated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class CommunityJoinRequest(BaseModel):
    """Payload to assign a member to a community."""
    user_id: str
    community_id: str
    role_id: Optional[str] = "role-member"


class Channel(BaseModel):
    channel_id: str
    community_id: str
    name: str


class Resource(BaseModel):
    resource_id: str
    community_id: str
    title: str
    type: str  # e.g., Article, Video, Guide
    duration: str
    difficulty: str
    relevance_score: Optional[float] = None
    reason: Optional[str] = None


class Project(BaseModel):
    project_id: str
    community_id: str
    title: str
    description: str


class Event(BaseModel):
    event_id: str
    community_id: str
    title: str
    time: str
    type: str
    difficulty: str
    score: Optional[int] = None
    reason: Optional[str] = None


class Mentor(BaseModel):
    mentor_id: str
    community_id: str
    name: str
    role: str
    expertise_areas: List[str]
    compatibility_score: Optional[float] = None
    match_reason: Optional[str] = None


class Milestone(BaseModel):
    week: int
    title: str
    objectives: List[str]
    resources: List[str]
    estimated_hours: float


class LearningTrack(BaseModel):
    track_id: str
    community_id: str
    roadmap_title: str
    total_weeks: int
    daily_commitment_minutes: int
    estimated_completion_date: str
    milestones: List[Milestone]


