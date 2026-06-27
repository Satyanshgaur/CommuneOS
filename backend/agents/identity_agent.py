"""
CommuneOS Identity Agent
Analyzes user profile, resume context from Memory Agent, and interests to detect:
- Current Skill Level
- Learning Goals
- Primary Interests
- Technology Stack
- Detected Skills (legacy)
- Learning Preference (legacy)
"""
import json
from typing import Any, Dict, Optional

from agents.base_agent import BaseAgent
from agents.memory_agent import MemoryAgent
from config import settings
from services.llm_service import llm_service
from services.mock_data import get_mock_identity
from utils.logger import get_logger

logger = get_logger("agent.identity")


class IdentityAgent(BaseAgent):
    """
    Agent 1: Identity / Profile Analysis
    
    Detects user skills, learning goals, primary interests, and tech stack
    by querying the Memory Agent for resume context and parsing the profile.
    """
    name = "identity_agent"
    cache_ttl = 3600  # 1 hour

    SYSTEM_PROMPT = """You are the Identity Agent for CommuneOS.
Your job is to analyze a community member's profile and resume context to extract a detailed understanding of them.

You MUST return ONLY valid JSON in this exact structure:
{
  "current_skill_level": "Beginner|Intermediate|Advanced|Expert",
  "learning_goals": ["Goal1", "Goal2"],
  "primary_interests": ["Interest1", "Interest2"],
  "technology_stack": ["Tech1", "Tech2"],
  "inferred_skills": {
    "Skill1": "Beginner|Intermediate|Advanced|Expert"
  },
  "detected_skills": [
    {"name": "SkillName", "proficiency": "Beginner|Intermediate|Advanced|Expert", "confidence": 0.9, "source": "stated"}
  ],
  "learning_preference": "visual|auditory|kinesthetic|reading",
  "insights": ["Insight1", "Insight2"],
  "reasoning": "A short summary of the user's background and what we detected from their profile/resume."
}

Rules:
- Extract skills, programming languages, and frameworks from the resume context and user profile.
- Infer their current skill level based on experience and project complexity in the resume.
- Identify primary interests, learning/career goals, and learning preference.
"""

    async def _process(self, user_id: str, user_data: Dict, *args, **kwargs) -> Dict[str, Any]:
        """Build LLM prompt and analyze user profile using RAG memory."""
        # 1. Fetch resume and personal context via Memory Agent
        memory_agent = MemoryAgent()
        memory_res = await memory_agent.run(user_id, user_data)
        memory_data = memory_res.get("data", {})
        user_context = memory_data.get("user_context_block", "No resume context found.")

        # Build context from user data
        bio = user_data.get("bio", "No bio provided")
        interests = user_data.get("interests", [])
        goals = user_data.get("goals", [])
        current_role = user_data.get("current_role", "") or user_data.get("role", "")
        skill_level = user_data.get("skill_level", "")

        prompt = f"""Analyze this community member's profile and resume:

Name: {user_data.get('username', 'Unknown')}
Bio: {bio}
Stated Current Role: {current_role}
Stated Skill Level: {skill_level}
Stated Interests: {', '.join(interests) if isinstance(interests, list) else str(interests)}
Stated Goals: {', '.join(goals) if isinstance(goals, list) else str(goals)}

RETRIEVED RESUME CONTEXT:
{user_context}

Based on this information, provide a complete identity analysis in the required JSON format."""

        result_json, is_fallback = await llm_service.complete_json(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=settings.LLM_TEMPERATURE_IDENTITY,
            max_tokens=settings.LLM_MAX_TOKENS_COMPLEX,
        )

        if is_fallback or not result_json:
            fallback = self._get_fallback(user_id, user_data)
            fallback["_is_fallback"] = True
            return fallback

        result_json["user_id"] = user_id
        result_json["_is_fallback"] = False
        logger.info(f"Identity analysis complete for {user_id}: Tech stack {result_json.get('technology_stack', [])}")
        return result_json

    def _get_fallback(self, user_id: str, user_data: Dict, *args, **kwargs) -> Dict[str, Any]:
        """Return mock identity data as fallback, but adapted to new schema."""
        mock_id = get_mock_identity(user_id, user_data)
        
        detected_skills = mock_id.get("detected_skills", [])
        tech_stack = [s["name"] for s in detected_skills] if detected_skills else ["Python", "Systems"]
        inferred = {s["name"]: s["proficiency"] for s in detected_skills} if detected_skills else {"Python": "Intermediate"}
        
        return {
            "current_skill_level": user_data.get("skill_level") or mock_id.get("learning_preference", "Intermediate"),
            "learning_goals": user_data.get("goals") or ["Become an AI Systems Engineer"],
            "primary_interests": user_data.get("interests") or ["AI", "Systems"],
            "technology_stack": tech_stack,
            "inferred_skills": inferred,
            "detected_skills": detected_skills or [{"name": "Python", "proficiency": "Intermediate", "confidence": 0.9, "source": "stated"}],
            "learning_preference": mock_id.get("learning_preference", "visual"),
            "insights": [f"Has interest in {', '.join(user_data.get('interests', ['AI']))}"],
            "reasoning": mock_id.get("summary", "Fallback profile generated."),
        }
