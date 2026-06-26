"""
CommuneOS Identity Agent
Analyzes user profile, chat history, and interactions to detect:
- Skills with proficiency levels
- Learning preferences
- Expertise and growth areas
"""
import json
from typing import Any, Dict, Optional

from agents.base_agent import BaseAgent
from config import settings
from services.llm_service import llm_service
from services.mock_data import get_mock_identity
from utils.logger import get_logger

logger = get_logger("agent.identity")


class IdentityAgent(BaseAgent):
    """
    Agent 1: Identity / Profile Analysis
    
    Detects user skills, learning style, expertise areas, and growth opportunities
    by analyzing their bio, chat history, and interaction patterns.
    """
    name = "identity_agent"
    cache_ttl = 3600  # 1 hour

    SYSTEM_PROMPT = """You are the Identity Agent for CommuneOS, an intelligent community platform.
Your job is to analyze a community member's profile and extract a detailed understanding of them.

You MUST return ONLY valid JSON in this exact structure:
{
  "detected_skills": [
    {"name": "SkillName", "proficiency": "Beginner|Intermediate|Advanced|Expert", "confidence": 0.0-1.0, "source": "stated|inferred|activity"}
  ],
  "expertise_areas": ["Area1", "Area2"],
  "growth_areas": ["Area1", "Area2"],
  "learning_preference": "visual|auditory|kinesthetic|reading",
  "overall_confidence": 0.0-1.0,
  "summary": "One sentence profile summary"
}

Rules:
- Extract skills explicitly mentioned AND infer from context
- Be conservative with confidence scores (0.5-0.8 for inferred, 0.8-0.95 for stated)
- Expertise areas = things they know well
- Growth areas = things they want to learn or show gaps in
- Learning preference = infer from how they describe their learning
"""

    async def _process(self, user_id: str, user_data: Dict, *args, **kwargs) -> Dict[str, Any]:
        """Build LLM prompt and analyze user profile."""
        # Build context from user data
        bio = user_data.get("bio", "No bio provided")
        skills = user_data.get("skills", {})
        tags = user_data.get("tags", [])
        interests = user_data.get("interests", [])
        goals = user_data.get("goals", [])
        chat_history = user_data.get("chat_history", [])

        skills_text = ", ".join([f"{k} (level {v}/5)" for k, v in skills.items()]) if skills else "None listed"
        chat_text = "\n".join([f"- {m.get('content', '')}" for m in chat_history[-5:]]) if chat_history else "No chat history"

        prompt = f"""Analyze this community member's profile:

Name: {user_data.get('username', 'Unknown')}
Bio: {bio}
Self-reported skills: {skills_text}
Interest tags: {', '.join(tags) if tags else 'None'}
Stated interests: {', '.join(interests) if interests else 'None'}
Goals: {', '.join(goals) if goals else 'None'}
Recent messages:
{chat_text}

Based on all this information, provide a complete skill analysis in the required JSON format."""

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
        logger.info(f"Identity analysis complete for {user_id}: {len(result_json.get('detected_skills', []))} skills detected")
        return result_json

    def _get_fallback(self, user_id: str, user_data: Dict, *args, **kwargs) -> Dict[str, Any]:
        """Return mock identity data as fallback."""
        return get_mock_identity(user_id, user_data)
