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

    async def run_sprint3(
        self, user_id: str, user_data: Dict, identity_data: Optional[Dict], community_id: str
    ) -> Dict[str, Any]:
        """
        Sprint 3 personalized learning roadmap.
        Generates roadmap based on the community track and user's profile.
        """
        import json
        from services.db import learning_tracks_table, get_resources_by_community
        track = learning_tracks_table.get(community_id)
        resources = get_resources_by_community(community_id)
        
        track_title = track["roadmap_title"] if track else "Custom Mastery Path"
        milestones_list = track["milestones"] if track else []
        resources_catalog = "\n".join([f"- {r['title']}" for r in resources])

        system_prompt = """You are the Learning Agent for CommuneOS.
Your job is to generate a personalized learning roadmap based on a community learning track template.

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
      "estimated_hours": 5.0,
      "completed": false
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
  "estimated_completion_date": "Month DD, YYYY",
  "progress_percent": 0.0
}

Rules:
- Personalize the milestones to fit the user's experience level (adjust objectives/hours).
- Include "completed": false for each milestone.
- Daily checklist should contain 3-4 immediately actionable tasks for today.
- Set progress_percent to 0.0 initially.
"""

        prompt = f"""Create a personalized learning roadmap for this member:

Member: {user_data.get('username', 'Unknown')}
Skill Level: {user_data.get('skill_level', 'Intermediate')}
Skills: {identity_data.get('inferred_skills', {}) if identity_data else user_data.get('skills', {})}
Goals: {user_data.get('goals', [])}
Interests: {identity_data.get('interests', []) if identity_data else user_data.get('interests', [])}

Community Learning Track Template:
Title: {track_title}
Milestones: {json.dumps(milestones_list)}

Available Resources:
{resources_catalog}
"""

        result_json, is_fallback = await llm_service.complete_json(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=settings.LLM_TEMPERATURE_LEARNING,
            max_tokens=settings.LLM_MAX_TOKENS_COMPLEX,
        )

        if is_fallback or not result_json:
            result_json = self._get_sprint3_fallback(user_id, user_data, track)

        # Ensure task_ids are set and completed fields are present
        for i, item in enumerate(result_json.get("daily_checklist", [])):
            if not item.get("task_id"):
                item["task_id"] = f"task-{user_id}-{i}"
            item["completed"] = item.get("completed", False)

        for m in result_json.get("milestones", []):
            m["completed"] = m.get("completed", False)

        result_json["progress_percent"] = result_json.get("progress_percent", 0.0)
        return result_json

    def _get_sprint3_fallback(self, user_id: str, user_data: Dict, track: Optional[Dict]) -> Dict[str, Any]:
        from datetime import datetime, timedelta
        completion_date = (datetime.utcnow() + timedelta(weeks=8)).strftime("%B %d, %Y")
        
        if track:
            milestones = []
            for m in track.get("milestones", []):
                milestones.append({
                    "week": m["week"],
                    "title": m["title"],
                    "objectives": m["objectives"],
                    "resources": m["resources"],
                    "estimated_hours": m["estimated_hours"],
                    "completed": False
                })
            
            # Add a Capstone Project milestone
            milestones.append({
                "week": len(milestones) + 1,
                "title": "Capstone Project: Practical Implementation",
                "objectives": ["Build a complete project using technologies learned", "Present to community mentors"],
                "resources": ["Official Documentation"],
                "estimated_hours": 12.0,
                "completed": False
            })
            
            roadmap_title = track["roadmap_title"]
            total_weeks = track["total_weeks"] + 1
            daily_commit = track["daily_commitment_minutes"]
        else:
            roadmap_title = "Custom Systems Mastery Path"
            total_weeks = 4
            daily_commit = 60
            milestones = [
                {
                    "week": 1,
                    "title": "Core Foundations",
                    "objectives": ["Understand core architectural layout", "Setup local development tools"],
                    "resources": ["Getting Started Guide"],
                    "estimated_hours": 5.0,
                    "completed": False
                },
                {
                    "week": 2,
                    "title": "Intermediate Optimizations",
                    "objectives": ["Implement performance modifications", "Benchmark resource usage"],
                    "resources": ["Optimization Cheat Sheet"],
                    "estimated_hours": 6.0,
                    "completed": False
                },
                {
                    "week": 3,
                    "title": "Capstone Project",
                    "objectives": ["Design and build personalized developer dashboard integration", "Validate isolate middleware endpoints"],
                    "resources": ["API Specification Guidelines"],
                    "estimated_hours": 10.0,
                    "completed": False
                }
            ]

        daily_checklist = [
            {
                "task_id": f"task-{user_id}-1",
                "task": "Read the community getting started resource and join active channels.",
                "type": "reading",
                "duration_minutes": 20,
                "resource_link": None,
                "completed": False
            },
            {
                "task_id": f"task-{user_id}-2",
                "task": "Set up your local code repository and install base dependencies.",
                "type": "coding",
                "duration_minutes": 30,
                "resource_link": None,
                "completed": False
            },
            {
                "task_id": f"task-{user_id}-3",
                "task": "Introduce yourself in the community main channel and meet other peers.",
                "type": "discussion",
                "duration_minutes": 10,
                "resource_link": None,
                "completed": False
            }
        ]

        return {
            "roadmap_title": roadmap_title,
            "total_weeks": total_weeks,
            "daily_commitment_minutes": daily_commit,
            "milestones": milestones,
            "daily_checklist": daily_checklist,
            "estimated_completion_date": completion_date,
            "progress_percent": 0.0
        }
