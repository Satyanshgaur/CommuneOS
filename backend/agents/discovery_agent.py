"""
CommuneOS Discovery Agent
Matches users with community channels and learning resources
based on their identity profile from the Identity Agent.
"""
import json
from typing import Any, Dict, List, Optional

from agents.base_agent import BaseAgent
from config import settings
from services.llm_service import llm_service
from services.mock_data import get_mock_discovery
from utils.constants import COMMUNITY_CHANNELS
from utils.logger import get_logger

logger = get_logger("agent.discovery")


class DiscoveryAgent(BaseAgent):
    """
    Agent 2: Channel & Resource Discovery
    
    Recommends channels and learning resources that match the user's
    skill level, interests, and learning style.
    """
    name = "discovery_agent"
    cache_ttl = 3600

    SYSTEM_PROMPT = """You are the Discovery Agent for CommuneOS.
Your job is to match community members with the most relevant channels and resources.

You MUST return ONLY valid JSON in this exact structure:
{
  "recommended_channels": [
    {
      "channel_id": "ch-id",
      "name": "Channel Name",
      "relevance_score": 0.0-1.0,
      "reason": "Why this channel is recommended",
      "difficulty": "Beginner|Intermediate|Advanced"
    }
  ],
  "recommended_resources": [
    {
      "resource_id": "res-id",
      "title": "Resource Title",
      "type": "Article|Video|Guide|Tutorial|Notebook",
      "duration": "X min",
      "difficulty": "Beginner|Intermediate|Advanced",
      "relevance_score": 0.0-1.0,
      "reason": "Why this resource helps"
    }
  ],
  "discovery_priority": ["channel/resource name to explore first", ...]
}

Rules:
- Recommend 3-5 channels and 3-5 resources
- Match difficulty level to user's skill level
- Prioritize channels with active discussions
- Give higher scores to exact skill matches
"""

    async def _process(
        self, user_id: str, user_data: Dict,
        identity_data: Optional[Dict] = None,
        *args, **kwargs
    ) -> Dict[str, Any]:
        """Match channels and resources based on identity profile."""
        # Build user context
        skills_summary = []
        if identity_data:
            for skill in identity_data.get("detected_skills", []):
                skills_summary.append(f"{skill['name']} ({skill['proficiency']})")
        elif user_data.get("skills"):
            for name, level in user_data["skills"].items():
                levels = {1: "Beginner", 2: "Beginner", 3: "Intermediate", 4: "Advanced", 5: "Expert"}
                skills_summary.append(f"{name} ({levels.get(level, 'Intermediate')})")

        expertise_areas = []
        growth_areas = []
        learning_style = "visual"
        if identity_data:
            expertise_areas = identity_data.get("expertise_areas", [])
            growth_areas = identity_data.get("growth_areas", [])
            learning_style = identity_data.get("learning_preference", "visual")

        channels_catalog = "\n".join([
            f"- {ch['id']}: {ch['name']} (topics: {', '.join(ch['topics'])}, difficulty: {ch['difficulty']})"
            for ch in COMMUNITY_CHANNELS
        ])

        prompt = f"""Match this community member with the best channels and resources:

Member: {user_data.get('username', 'Unknown')}
Skills: {', '.join(skills_summary) if skills_summary else 'Not specified'}
Interests: {', '.join(user_data.get('interests', []))}
Goals: {', '.join(user_data.get('goals', []))}
Expertise areas: {', '.join(expertise_areas)}
Growth areas (wants to learn): {', '.join(growth_areas)}
Learning style: {learning_style}
Skill level: {user_data.get('skill_level', 'Intermediate')}

Available channels:
{channels_catalog}

Recommend the best matches for this member. For resources, invent relevant titles that would help them."""

        result_json, is_fallback = await llm_service.complete_json(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=settings.LLM_TEMPERATURE_DISCOVERY,
            max_tokens=settings.LLM_MAX_TOKENS_COMPLEX,
        )

        if is_fallback or not result_json:
            fallback = self._get_fallback(user_id, user_data)
            fallback["_is_fallback"] = True
            return fallback

        result_json["user_id"] = user_id
        result_json["_is_fallback"] = False
        logger.info(f"Discovery complete for {user_id}: {len(result_json.get('recommended_channels', []))} channels, {len(result_json.get('recommended_resources', []))} resources")
        return result_json

    def _get_fallback(self, user_id: str, user_data: Dict, *args, **kwargs) -> Dict[str, Any]:
        return get_mock_discovery(user_id, user_data)
