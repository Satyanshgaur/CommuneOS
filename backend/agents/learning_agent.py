"""
CommuneOS Learning Agent
Creates personalized milestone-based learning roadmaps by querying the Memory Agent (RAG) for community resources.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from agents.base_agent import BaseAgent
from agents.memory_agent import MemoryAgent
from config import settings
from services.llm_service import llm_service
from services.mock_data import get_mock_learning
from utils.logger import get_logger

logger = get_logger("agent.learning")


class LearningAgent(BaseAgent):
    """
    Agent 3: Learning Roadmap Creation
    
    Generates structured, milestone-based learning paths tailored to
    the user's skill level, goals, and RAG-retrieved community resources.
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
- Create 4-8 milestones covering the full learning arc.
- Incorporate the RAG-retrieved community resources where appropriate.
- Include a daily checklist with 3-4 immediately actionable tasks for today.
"""

    async def _process(
        self, user_id: str, user_data: Dict,
        identity_data: Optional[Dict] = None,
        *args, **kwargs
    ) -> Dict[str, Any]:
        """Create personalized learning roadmap."""
        # 1. Fetch personalization context from Memory Agent for resources
        search_query = f"learning resources for skills: {', '.join(user_data.get('interests', []))} or goals: {', '.join(user_data.get('goals', []))}"
        
        memory_agent = MemoryAgent()
        memory_res = await memory_agent.run(user_id, user_data, query=search_query, filter_type="resource")
        memory_data = memory_res.get("data", {})
        retrieved_resources = memory_data.get("community_context_block", "No specific resources found.")

        skills_summary = []
        if identity_data and identity_data.get("technology_stack"):
            skills_summary = identity_data.get("technology_stack", [])
        else:
            skills_summary = user_data.get("interests", [])

        growth_areas = identity_data.get("growth_areas", []) if identity_data else []
        learning_style = identity_data.get("learning_preference", "visual") if identity_data else "visual"

        completion_date = (datetime.utcnow() + timedelta(weeks=8)).strftime("%B %d, %Y")

        prompt = f"""Create a personalized learning roadmap for this community member:

Name: {user_data.get('username', 'Unknown')}
Skill level: {user_data.get('skill_level', 'Intermediate')}
Current skills/Tech stack: {', '.join(skills_summary)}
Goals: {', '.join(user_data.get('goals', ['General learning']))}
Growth areas to develop: {', '.join(growth_areas) if growth_areas else 'Not specified'}
Learning style: {learning_style}
Target completion: around {completion_date}

RETRIEVED COMMUNITY RESOURCES (RETRIEVED VIA RAG):
{retrieved_resources}

Create a comprehensive 8-week learning roadmap that helps them achieve their goals using the resources provided.
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
