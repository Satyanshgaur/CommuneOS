"""
CommuneOS Agent Response Models
Standardized output schemas for all 6 AI agents.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class AgentResponse(BaseModel):
    """
    Universal response wrapper for all agent outputs.
    Frontend always receives this shape regardless of which agent ran.
    """
    agent: str = Field(..., description="Agent identifier name")
    user_id: str = Field(..., description="User this response is for")
    success: bool = Field(default=True)
    data: Dict[str, Any] = Field(default_factory=dict, description="Agent-specific payload")
    error: Optional[str] = Field(None, description="Error message if failed")
    processing_time_ms: float = Field(default=0.0, description="Agent execution time in ms")
    is_fallback: bool = Field(default=False, description="True if mock/cached data used")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)


# ─── Identity Agent Output ─────────────────────────────────────────────────────

class DetectedSkill(BaseModel):
    """A skill detected by the Identity Agent."""
    name: str
    proficiency: str = Field(..., description="Beginner/Intermediate/Advanced/Expert")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    source: str = Field(default="inferred", description="stated/inferred/activity")


class IdentityAgentOutput(BaseModel):
    """Structured output from the Identity Agent."""
    user_id: str
    detected_skills: List[DetectedSkill] = Field(default_factory=list)
    expertise_areas: List[str] = Field(default_factory=list)
    growth_areas: List[str] = Field(default_factory=list)
    learning_preference: str = Field(default="visual", description="Primary learning style")
    overall_confidence: float = Field(default=0.6, ge=0.0, le=1.0)
    summary: Optional[str] = Field(None, description="Human-readable profile summary")


# ─── Discovery Agent Output ────────────────────────────────────────────────────

class RecommendedChannel(BaseModel):
    """A channel recommendation from the Discovery Agent."""
    channel_id: str
    name: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    reason: str = Field(..., description="Why this channel was recommended")
    difficulty: Optional[str] = None
    member_count: Optional[int] = None


class RecommendedResource(BaseModel):
    """A resource recommendation from the Discovery Agent."""
    resource_id: str
    title: str
    type: str = Field(..., description="Article/Video/Guide/Tutorial/Notebook")
    duration: Optional[str] = None
    difficulty: Optional[str] = None
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    reason: str


class DiscoveryAgentOutput(BaseModel):
    """Structured output from the Discovery Agent."""
    user_id: str
    recommended_channels: List[RecommendedChannel] = Field(default_factory=list)
    recommended_resources: List[RecommendedResource] = Field(default_factory=list)
    discovery_priority: List[str] = Field(default_factory=list, description="Ordered list of what to explore first")


# ─── Learning Agent Output ─────────────────────────────────────────────────────

class LearningMilestone(BaseModel):
    """A single learning milestone in the roadmap."""
    week: int = Field(..., description="Which week this milestone is for")
    title: str
    objectives: List[str] = Field(default_factory=list)
    resources: List[str] = Field(default_factory=list, description="Resource IDs or names")
    estimated_hours: Optional[float] = None


class DailyChecklistItem(BaseModel):
    """A single item on the user's daily checklist."""
    task_id: str
    task: str
    type: str = Field(..., description="reading/coding/discussion/watching")
    duration_minutes: int = Field(default=30)
    resource_link: Optional[str] = None
    completed: bool = Field(default=False)


class LearningAgentOutput(BaseModel):
    """Structured output from the Learning Agent."""
    user_id: str
    roadmap_title: str = Field(default="Personalized Learning Path")
    total_weeks: int = Field(default=8)
    daily_commitment_minutes: int = Field(default=60)
    milestones: List[LearningMilestone] = Field(default_factory=list)
    daily_checklist: List[DailyChecklistItem] = Field(default_factory=list)
    estimated_completion_date: Optional[str] = None


# ─── Mentor Agent Output ────────────────────────────────────────────────────────

class MentorProfile(BaseModel):
    """A mentor match from the Mentor Agent."""
    mentor_id: str
    name: str
    role: str
    avatar: Optional[str] = None
    expertise_areas: List[str] = Field(default_factory=list)
    compatibility_score: float = Field(..., ge=0.0, le=1.0)
    match_reason: str
    availability: Optional[str] = None
    teaching_style: Optional[str] = None
    years_experience: Optional[int] = None


class MentorAgentOutput(BaseModel):
    """Structured output from the Mentor Agent."""
    user_id: str
    primary_mentor: Optional[MentorProfile] = None
    backup_mentors: List[MentorProfile] = Field(default_factory=list)
    suggested_meeting_schedule: Optional[str] = None
    introduction_template: Optional[str] = None


# ─── Health Agent Output ────────────────────────────────────────────────────────

class AtRiskMember(BaseModel):
    """A member flagged as at-risk of churning."""
    user_id: str
    username: str
    risk_level: str = Field(..., description="high/medium/low")
    days_inactive: int
    last_seen: Optional[str] = None
    reason: str


class TopicGap(BaseModel):
    """An underserved topic area in the community."""
    topic: str
    unanswered_questions: int
    demand_score: float = Field(..., ge=0.0, le=1.0)
    suggestion: str


class HealthAgentOutput(BaseModel):
    """Structured output from the Health Agent."""
    community_health_score: float = Field(..., ge=0.0, le=1.0)
    total_members: int = Field(default=0)
    active_members_7d: int = Field(default=0)
    at_risk_members: List[AtRiskMember] = Field(default_factory=list)
    topic_gaps: List[TopicGap] = Field(default_factory=list)
    trending_topics: List[str] = Field(default_factory=list)
    engagement_trend: str = Field(default="stable", description="rising/stable/declining")
    summary: Optional[str] = None


# ─── Organizer Agent Output ─────────────────────────────────────────────────────

class ActionItem(BaseModel):
    """A prioritized action item for community organizers."""
    action_id: str
    title: str
    description: str
    priority: str = Field(..., description="critical/high/medium/low")
    category: str = Field(..., description="welcome/engagement/content/event/moderation")
    assignee: Optional[str] = None
    deadline: Optional[str] = None
    expected_impact: Optional[str] = None
    completed: bool = Field(default=False)


class EventSuggestion(BaseModel):
    """A suggested community event."""
    event_id: str
    title: str
    type: str = Field(..., description="Workshop/AMA/Study Group/Webinar/Challenge")
    topic: str
    rationale: str
    suggested_timing: Optional[str] = None
    target_audience: Optional[str] = None
    expected_attendance: Optional[int] = None


class OrganizerAgentOutput(BaseModel):
    """Structured output from the Organizer Agent."""
    action_items: List[ActionItem] = Field(default_factory=list)
    event_suggestions: List[EventSuggestion] = Field(default_factory=list)
    automation_recommendations: List[str] = Field(default_factory=list)
    resource_allocation: Optional[str] = None
    summary: Optional[str] = None


# ─── Combined Personalization Profile ──────────────────────────────────────────

class PersonalizationProfile(BaseModel):
    """
    Complete personalization profile combining all member-facing agent outputs.
    This is what the member dashboard receives.
    """
    user_id: str
    identity: Optional[IdentityAgentOutput] = None
    discovery: Optional[DiscoveryAgentOutput] = None
    learning: Optional[LearningAgentOutput] = None
    mentor: Optional[MentorAgentOutput] = None
    pipeline_time_ms: float = Field(default=0.0)
    is_partial: bool = Field(default=False, description="True if some agents failed")
    fallback_used: bool = Field(default=False)
    generated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class AgentStatus(BaseModel):
    """Status object for polling long-running agent pipelines."""
    user_id: str
    status: str = Field(..., description="pending/running/completed/failed")
    progress_percent: int = Field(default=0, ge=0, le=100)
    current_agent: Optional[str] = None
    error_message: Optional[str] = None
    estimated_completion_seconds: Optional[int] = None
    started_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
