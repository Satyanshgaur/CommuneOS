"""
CommuneOS Input Validators
Custom validation functions used across the application.
"""
import re
from typing import Any, Dict, List, Optional
from pydantic import validator


def validate_user_id(user_id: str) -> str:
    """Validate user ID format (alphanumeric + underscores/hyphens)."""
    if not user_id:
        raise ValueError("user_id cannot be empty")
    if not re.match(r'^[a-zA-Z0-9_\-]+$', user_id):
        raise ValueError("user_id must be alphanumeric with underscores/hyphens only")
    if len(user_id) > 64:
        raise ValueError("user_id must be 64 characters or fewer")
    return user_id.lower()


def validate_skill_level(level: int) -> int:
    """Validate skill proficiency level is in 1-5 range."""
    if not 1 <= level <= 5:
        raise ValueError("Skill level must be between 1 and 5")
    return level


def validate_confidence_score(score: float) -> float:
    """Validate confidence/match score is in 0.0-1.0 range."""
    if not 0.0 <= score <= 1.0:
        raise ValueError("Confidence score must be between 0.0 and 1.0")
    return round(score, 4)


def validate_email(email: str) -> str:
    """Basic email format validation."""
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValueError(f"Invalid email format: {email}")
    return email.lower()


def sanitize_text(text: str, max_length: int = 2000) -> str:
    """Sanitize and truncate text input."""
    if not text:
        return ""
    # Remove null bytes
    text = text.replace('\x00', '')
    # Truncate to max length
    if len(text) > max_length:
        text = text[:max_length] + "..."
    return text.strip()


def validate_skills_dict(skills: Dict[str, Any]) -> Dict[str, Any]:
    """Validate skills dictionary structure."""
    if not isinstance(skills, dict):
        raise ValueError("skills must be a dictionary")
    validated = {}
    for skill_name, level in skills.items():
        if isinstance(level, int):
            validated[skill_name] = validate_skill_level(level)
        elif isinstance(level, str) and level in ["Beginner", "Intermediate", "Advanced", "Expert"]:
            validated[skill_name] = level
        else:
            # Default to Beginner if unknown
            validated[skill_name] = "Beginner"
    return validated
