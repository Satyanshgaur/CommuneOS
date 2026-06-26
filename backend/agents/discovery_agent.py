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

    async def run_sprint3(
        self, user_id: str, user_data: Dict, identity_data: Optional[Dict], community_id: str
    ) -> Dict[str, Any]:
        """
        Sprint 3 personalized discovery.
        Generates recommendations based on the user's identity profile and community catalog.
        """
        from services.db import (
            get_channels_by_community,
            get_resources_by_community,
            get_events_by_community,
            get_projects_by_community,
            learning_tracks_table,
        )

        channels = get_channels_by_community(community_id)
        resources = get_resources_by_community(community_id)
        events = get_events_by_community(community_id)
        projects = get_projects_by_community(community_id)
        track = learning_tracks_table.get(community_id)
        learning_tracks = [track] if track else []

        # Build prompt catalog
        channels_catalog = "\n".join([f"- [Channel] ID: {c['channel_id']}, Name: {c['name']}" for c in channels])
        resources_catalog = "\n".join([f"- [Resource] ID: {r['resource_id']}, Title: {r['title']}, Type: {r['type']}, Difficulty: {r['difficulty']}, Est: {r['duration']}" for r in resources])
        events_catalog = "\n".join([f"- [Event] ID: {e['event_id']}, Title: {e['title']}, Time: {e['time']}, Type: {e['type']}, Difficulty: {e['difficulty']}" for e in events])
        projects_catalog = "\n".join([f"- [Project] ID: {p['project_id']}, Title: {p['title']}, Desc: {p['description']}" for p in projects])
        tracks_catalog = "\n".join([f"- [Learning Track] ID: {t['track_id']}, Title: {t['roadmap_title']}, Weeks: {t['total_weeks']}" for t in learning_tracks])

        system_prompt = """You are the Discovery Agent for CommuneOS.
Your job is to match a community member with the most relevant channels, projects, events, resources, learning tracks, and study groups from their community.

You MUST return ONLY valid JSON in this exact structure:
{
  "channels": [
    {
      "title": "Channel Name",
      "description": "Short description of why it fits",
      "relevance_score": 0.0-1.0,
      "reason": "Why this was recommended",
      "category": "Channels"
    }
  ],
  "projects": [
    {
      "title": "Project Title",
      "description": "Short description of the project",
      "relevance_score": 0.0-1.0,
      "reason": "Why this project fits the user's goals",
      "category": "Projects"
    }
  ],
  "events": [
    {
      "title": "Event Title",
      "description": "Short description of the event",
      "relevance_score": 0.0-1.0,
      "reason": "Why the user should attend",
      "category": "Events"
    }
  ],
  "resources": [
    {
      "title": "Resource Title",
      "description": "Short description of the resource",
      "relevance_score": 0.0-1.0,
      "reason": "Why this resource is helpful",
      "category": "Resources"
    }
  ],
  "learning_tracks": [
    {
      "title": "Learning Track Title",
      "description": "Short description of the track",
      "relevance_score": 0.0-1.0,
      "reason": "Why this track matches",
      "category": "Learning Tracks"
    }
  ],
  "study_groups": [
    {
      "title": "Study Group Name",
      "description": "Short description of the study group",
      "relevance_score": 0.0-1.0,
      "reason": "Why the user should join",
      "category": "Study Groups"
    }
  ]
}

Rules:
- Select only from the provided community catalog.
- If there are no study groups, you can suggest forming one for a specific topic the user wants to learn (category: "Study Groups").
- Return 1-3 recommendations for each category.
- Match difficulty level to the user's skill level.
- Relevance scores must be float values between 0.0 and 1.0.
"""

        prompt = f"""Generate recommendations for the following member:

Member: {user_data.get('username', 'Unknown')}
Skills: {identity_data.get('inferred_skills', {}) if identity_data else user_data.get('skills', {})}
Interests: {identity_data.get('interests', []) if identity_data else user_data.get('interests', [])}
Goals: {user_data.get('goals', [])}
Growth Areas: {identity_data.get('growth_areas', []) if identity_data else []}
Timezone: {user_data.get('timezone')}

Community Catalog:
--- CHANNELS ---
{channels_catalog or 'None'}

--- RESOURCES ---
{resources_catalog or 'None'}

--- EVENTS ---
{events_catalog or 'None'}

--- PROJECTS ---
{projects_catalog or 'None'}

--- LEARNING TRACKS ---
{tracks_catalog or 'None'}
"""

        result_json, is_fallback = await llm_service.complete_json(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=settings.LLM_TEMPERATURE_DISCOVERY,
            max_tokens=settings.LLM_MAX_TOKENS_COMPLEX,
        )

        if is_fallback or not result_json:
            result_json = self._get_sprint3_fallback(user_data, channels, resources, events, projects, learning_tracks)

        return result_json

    def _get_sprint3_fallback(self, user_data: Dict, channels: List, resources: List, events: List, projects: List, learning_tracks: List) -> Dict[str, Any]:
        # Return fallback recommendations using actual db objects
        recs = {
            "channels": [],
            "projects": [],
            "events": [],
            "resources": [],
            "learning_tracks": [],
            "study_groups": []
        }
        for c in channels[:2]:
            recs["channels"].append({
                "title": c["name"],
                "description": f"Official channel for discussing {c['name']}.",
                "relevance_score": 0.85,
                "reason": "Relevant to your community interests.",
                "category": "Channels"
            })
        for p in projects[:2]:
            recs["projects"].append({
                "title": p["title"],
                "description": p["description"],
                "relevance_score": 0.90,
                "reason": "Matches your profile core goals.",
                "category": "Projects"
            })
        for e in events[:2]:
            if e.get("type") == "Study Group":
                recs["study_groups"].append({
                    "title": e["title"],
                    "description": f"Weekly study group sync for peer learning.",
                    "relevance_score": 0.88,
                    "reason": "Collaborate with other learners on similar tracks.",
                    "category": "Study Groups"
                })
            else:
                recs["events"].append({
                    "title": e["title"],
                    "description": f"Event on {e['time']}.",
                    "relevance_score": 0.88,
                    "reason": "Enhance your understanding of community domains.",
                    "category": "Events"
                })
        for r in resources[:2]:
            recs["resources"].append({
                "title": r["title"],
                "description": f"Recommended {r['type']} ({r['difficulty']}) - {r['duration']}.",
                "relevance_score": 0.92,
                "reason": r.get("reason") or "Highly relevant resource for study.",
                "category": "Resources"
            })
        for t in learning_tracks[:2]:
            recs["learning_tracks"].append({
                "title": t["roadmap_title"],
                "description": f"Structured learning track of {t['total_weeks']} weeks.",
                "relevance_score": 0.95,
                "reason": "Aligned with your career track goals.",
                "category": "Learning Tracks"
            })
            
        # Ensure we always have at least one study group
        if not recs["study_groups"]:
            recs["study_groups"].append({
                "title": "GPU & Systems Peer Study Group",
                "description": "Collaborative peer group for working through systems optimization tasks.",
                "relevance_score": 0.80,
                "reason": "Suggested study group for your active learning goals.",
                "category": "Study Groups"
            })
            
        return recs
