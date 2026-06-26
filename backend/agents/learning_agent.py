"""
CommuneOS Learning Agent
Creates personalized milestone-based learning roadmaps
tailored to individual goals, skill levels, and learning styles.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from agents.base_agent import BaseAgent
from config import settings
from services.llm_service import llm_service
from services.mock_data import get_mock_learning
from utils.logger import get_logger

logger = get_logger("agent.learning")


class LearningAgent(BaseAgent):
    """
    Agent 3: Learning Roadmap Creation
    
    Generates structured, milestone-based learning paths tailored to
    the user's skill level, goals, and discovery recommendations.
    """
    name = "learning_agent"
    cache_ttl = 3600

    SYSTEM_PROMPT = """You are the Learning Agent for CommuneOS.
Your job is to create a personalized learning roadmap for a community member.

You MUST return ONLY valid JSON in this exact structure:
{
  "roadmap_title": "Descriptive title for the learning path",
  "total_weeks": 8,
  "daily_commitment_minutes": 60,
  "milestones": [
    {
      "week": 1,
      "title": "Milestone title",
      "objectives": ["objective 1", "objective 2"],
      "resources": ["resource name or type"],
      "estimated_hours": 5.0
    }
  ],
  "daily_checklist": [
    {
      "task_id": "task-unique-id",
      "task": "Specific actionable task",
      "type": "reading|coding|discussion|watching",
      "duration_minutes": 30,
      "resource_link": null,
      "completed": false
    }
  ],
  "estimated_completion_date": "Month DD, YYYY"
}

Rules:
- Create 4-8 milestones covering the full learning arc
- Milestones should have progressive complexity (foundation → intermediate → advanced)
- Daily checklist should have 3-4 immediately actionable tasks for today
- Mix task types: reading, coding, discussion, watching
- Be realistic with time estimates
- The roadmap should directly address the user's stated goals
"""

    async def _process(
        self, user_id: str, user_data: Dict,
        identity_data: Optional[Dict] = None,
        *args, **kwargs
    ) -> Dict[str, Any]:
        """Create personalized learning roadmap."""
        skills_summary = []
        if identity_data:
            for skill in identity_data.get("detected_skills", []):
                skills_summary.append(f"{skill['name']} ({skill['proficiency']})")
        
        growth_areas = []
        learning_style = "visual"
        if identity_data:
            growth_areas = identity_data.get("growth_areas", [])
            learning_style = identity_data.get("learning_preference", "visual")

        completion_date = (datetime.utcnow() + timedelta(weeks=8)).strftime("%B %d, %Y")

        prompt = f"""Create a personalized learning roadmap for this community member:

Name: {user_data.get('username', 'Unknown')}
Skill level: {user_data.get('skill_level', 'Intermediate')}
Current skills: {', '.join(skills_summary) if skills_summary else ', '.join(user_data.get('tags', []))}
Goals: {', '.join(user_data.get('goals', ['General learning']))}
Interests: {', '.join(user_data.get('interests', []))}
Growth areas to develop: {', '.join(growth_areas) if growth_areas else 'Not specified'}
Learning style: {learning_style}
Target completion: around {completion_date}

Create a comprehensive 8-week learning roadmap that will help them achieve their goals.
Include 4-6 weekly milestones and 3-4 daily checklist tasks for today."""

        result_json, is_fallback = await llm_service.complete_json(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=settings.LLM_TEMPERATURE_LEARNING,
            max_tokens=settings.LLM_MAX_TOKENS_COMPLEX,
        )

        if is_fallback or not result_json:
            fallback = self._get_fallback(user_id, user_data)
            fallback["_is_fallback"] = True
            return fallback

        # Add user_id to checklist items if missing
        for i, item in enumerate(result_json.get("daily_checklist", [])):
            if not item.get("task_id"):
                item["task_id"] = f"task-{user_id}-{i}"

        result_json["user_id"] = user_id
        result_json["_is_fallback"] = False
        logger.info(f"Learning roadmap created for {user_id}: {result_json.get('total_weeks')} weeks, {len(result_json.get('milestones', []))} milestones")
        return result_json

    def _get_fallback(self, user_id: str, user_data: Dict, *args, **kwargs) -> Dict[str, Any]:
        return get_mock_learning(user_id, user_data)
