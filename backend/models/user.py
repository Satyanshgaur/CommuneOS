"""
CommuneOS User Profile Models
Pydantic schemas for user data validation and serialization.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, EmailStr
import uuid


class SkillEntry(BaseModel):
    """A single skill with name and proficiency level."""
    name: str = Field(..., description="Skill name, e.g. 'CUDA'")
    level: int = Field(..., ge=1, le=5, description="Proficiency 1-5 (1=Beginner, 5=Expert)")
    level_label: Optional[str] = Field(None, description="Human label: Beginner/Intermediate/Advanced/Expert")

    def model_post_init(self, __context: Any) -> None:
        if self.level_label is None:
            labels = {1: "Beginner", 2: "Beginner", 3: "Intermediate", 4: "Advanced", 5: "Expert"}
            self.level_label = labels.get(self.level, "Beginner")


class ChatMessage(BaseModel):
    """A single message in the user's chat history."""
    content: str = Field(..., max_length=5000)
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    channel: Optional[str] = Field(None, description="Channel where this was posted")


class UserProfile(BaseModel):
    """
    Complete user profile — the primary input for all AI agents.
    Represents both the stored profile and the API request body.
    """
    user_id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., min_length=1, max_length=64)
    email: Optional[str] = Field(None, description="User email (optional)")
    bio: Optional[str] = Field(None, max_length=2000, description="Free-text biography")
    avatar: Optional[str] = Field(None, description="Avatar initials or URL")

    # ─── Skills ───────────────────────────────────────────────────────────────
    skills: Dict[str, int] = Field(
        default_factory=dict,
        description="Map of skill name → proficiency level (1-5)"
    )
    verified_skills: Optional[List[SkillEntry]] = Field(default_factory=list)

    # ─── Preferences ──────────────────────────────────────────────────────────
    tags: List[str] = Field(default_factory=list, description="Self-identified interest tags")
    interests: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    skill_level: Optional[str] = Field(None, description="Overall: Beginner/Intermediate/Expert")
    learning_style: Optional[str] = Field(None, description="visual/auditory/kinesthetic/reading")

    # ─── Context ──────────────────────────────────────────────────────────────
    role: str = Field(default="member", description="member or organizer")
    timezone: Optional[str] = Field(None, description="e.g. 'Asia/Kolkata'")
    github_url: Optional[str] = Field(None)
    linkedin_url: Optional[str] = Field(None)

    # ─── Chat History ─────────────────────────────────────────────────────────
    chat_history: Optional[List[ChatMessage]] = Field(default_factory=list)
    recent_activity: Optional[List[str]] = Field(
        default_factory=list,
        description="Recent topics or channels the user interacted with"
    )

    # ─── Timestamps ───────────────────────────────────────────────────────────
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    last_active: Optional[datetime] = Field(default_factory=datetime.utcnow)

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        import re
        if not re.match(r'^[a-zA-Z0-9_\-]+$', v):
            raise ValueError("user_id must be alphanumeric with underscores/hyphens")
        return v.lower()

    @field_validator("skill_level")
    @classmethod
    def validate_skill_level_label(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in ["Beginner", "Intermediate", "Advanced", "Expert"]:
            raise ValueError("skill_level must be one of: Beginner, Intermediate, Advanced, Expert")
        return v

    def get_chat_context(self, max_messages: int = 10) -> str:
        """Return recent chat messages as a single text block for LLM prompts."""
        if not self.chat_history:
            return ""
        messages = self.chat_history[-max_messages:]
        return "\n".join([f"- {m.content}" for m in messages])

    def get_skills_summary(self) -> str:
        """Return skills as a readable summary for LLM prompts."""
        if not self.skills:
            return "No skills listed yet."
        parts = []
        for skill, level in self.skills.items():
            labels = {1: "Beginner", 2: "Beginner", 3: "Intermediate", 4: "Advanced", 5: "Expert"}
            parts.append(f"{skill} ({labels.get(level, 'Beginner')})")
        return ", ".join(parts)


class UserCreateRequest(BaseModel):
    """Request body for creating a new user profile."""
    user_id: Optional[str] = Field(None, description="Optional custom user ID (e.g. Supabase User UUID)")
    username: str = Field(..., min_length=1, max_length=64)
    email: Optional[str] = Field(None)
    bio: Optional[str] = Field(None, max_length=2000)
    tags: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    github_url: Optional[str] = Field(None)
    linkedin_url: Optional[str] = Field(None)
    timezone: Optional[str] = Field(None)

    def to_user_profile(self, user_id: Optional[str] = None) -> UserProfile:
        """Convert creation request to full UserProfile."""
        uid = user_id or str(uuid.uuid4())[:8]
        return UserProfile(
            user_id=uid,
            username=self.username,
            email=self.email,
            bio=self.bio,
            tags=self.tags,
            interests=self.interests,
            goals=self.goals,
            github_url=self.github_url,
            linkedin_url=self.linkedin_url,
            timezone=self.timezone,
        )


class MentalModel(BaseModel):
    """
    Inferred user profile built by Identity Agent.
    Used as input to Discovery, Learning, and Mentor agents.
    """
    user_id: str
    inferred_skills: Dict[str, str] = Field(
        default_factory=dict,
        description="Skill name → proficiency level label"
    )
    interests: List[str] = Field(default_factory=list)
    communication_preference: str = Field(default="text")
    timezone: Optional[str] = None
    availability: Optional[str] = None
    learning_style: str = Field(default="visual")
    expertise_areas: List[str] = Field(default_factory=list)
    growth_areas: List[str] = Field(default_factory=list)
    confidence_level: float = Field(default=0.6, ge=0.0, le=1.0)
