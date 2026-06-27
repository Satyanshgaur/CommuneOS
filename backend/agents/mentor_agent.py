"""
CommuneOS Mentor Agent
Connects learners with the best-matching expert mentors by querying the Memory Agent (RAG).
"""
from typing import Any, Dict, List, Optional

from agents.base_agent import BaseAgent
from agents.memory_agent import MemoryAgent
from config import settings
from services.llm_service import llm_service
from services.mock_data import get_mock_mentor
from utils.logger import get_logger

logger = get_logger("agent.mentor")

# Fallback mentor list in case RAG or LLM fails
MENTOR_DATABASE = [
    {
        "mentor_id": "mentor-sarah",
        "name": "Sarah Jenkins",
        "role": "Principal GPU Engineer at NVIDIA",
        "avatar": "SJ",
        "expertise_areas": ["CUDA", "GPU Architecture", "Distributed Systems", "C++", "Linux Kernels"],
        "years_experience": 8,
        "teaching_style": "Hands-on projects with regular code reviews",
        "availability": "Weekdays 6-8 PM IST, some weekends",
        "timezone": "Asia/Kolkata",
        "languages": ["English", "Hindi"],
        "success_rate": 0.94,
    },
    {
        "mentor_id": "mentor-amit",
        "name": "Amit Sharma",
        "role": "AI Infrastructure Lead",
        "avatar": "AS",
        "expertise_areas": ["PyTorch", "MLOps", "Distributed Training", "Machine Learning", "Python"],
        "years_experience": 6,
        "teaching_style": "Theory-first with practical application examples",
        "availability": "Weekends 10 AM - 12 PM IST, flexible evenings",
        "timezone": "Asia/Kolkata",
        "languages": ["English", "Hindi"],
        "success_rate": 0.89,
    },
    {
        "mentor_id": "mentor-priya-n",
        "name": "Priya Nair",
        "role": "Senior Data Scientist",
        "avatar": "PN",
        "expertise_areas": ["Python", "Data Science", "Machine Learning", "Statistics", "Pandas", "NumPy"],
        "years_experience": 5,
        "teaching_style": "Structured curriculum with milestone checkpoints",
        "availability": "Flexible evenings, weekends",
        "timezone": "Asia/Kolkata",
        "languages": ["English", "Malayalam"],
        "success_rate": 0.87,
    },
    {
        "mentor_id": "mentor-alex-k",
        "name": "Alex Kim",
        "role": "Principal Systems Architect",
        "avatar": "AK",
        "expertise_areas": ["Rust", "Systems Design", "Linux", "C++", "Performance Optimization"],
        "years_experience": 10,
        "teaching_style": "First-principles reasoning, deep dives",
        "availability": "Weekdays 7-9 PM IST",
        "timezone": "Asia/Kolkata",
        "languages": ["English"],
        "success_rate": 0.92,
    },
]


class MentorAgent(BaseAgent):
    """
    Agent 4: Expert Mentor Matching
    
    Connects learners with the most compatible mentors based on:
    - RAG-retrieved mentor profiles matching user's skills and interests
    - Expertise alignment, availability, and teaching style
    """
    name = "mentor_agent"
    cache_ttl = 7200  # 2 hours

    SYSTEM_PROMPT = """You are the Mentor Agent for CommuneOS.
Your job is to match a community member with the best mentor from the available pool.

You MUST return ONLY valid JSON in this exact structure:
{
  "primary_mentor": {
    "mentor_id": "mentor-id",
    "name": "Mentor Full Name",
    "role": "Their role/title",
    "avatar": "initials",
    "expertise_areas": ["skill1", "skill2"],
    "compatibility_score": 0.0-1.0,
    "match_reason": "Specific reason why this mentor is ideal for this learner",
    "availability": "When they're available",
    "teaching_style": "How they teach",
    "years_experience": 5
  },
  "backup_mentors": [
    {
      "mentor_id": "mentor-id",
      "name": "Mentor Full Name",
      "role": "Their role/title",
      "compatibility_score": 0.0-1.0,
      "match_reason": "Brief reason"
    }
  ],
  "suggested_meeting_schedule": "Specific schedule suggestion",
  "introduction_template": "Template message to introduce the mentee to the mentor"
}

Rules:
- Select the best matching mentor from the list of mentors retrieved from the community database.
- Base your choice on the mentee's skills, resume context, and learning style.
- If the RAG results don't contain specific mentors, select from the default pool of Sarah Jenkins, Amit Sharma, Priya Nair, and Alex Kim.
"""

    async def _process(
        self, user_id: str, user_data: Dict,
        identity_data: Optional[Dict] = None,
        learning_data: Optional[Dict] = None,
        *args, **kwargs
    ) -> Dict[str, Any]:
        """Match user with best mentor using RAG."""
        # 1. Fetch personalization context from Memory Agent for mentors
        search_query = f"mentors matching skills: {', '.join(user_data.get('interests', []))} or goals: {', '.join(user_data.get('goals', []))}"
        
        memory_agent = MemoryAgent()
        memory_res = await memory_agent.run(user_id, user_data, query=search_query, filter_type="mentor")
        memory_data = memory_res.get("data", {})
        retrieved_mentors = memory_data.get("community_context_block", "")
        
        # If no mentors were found in RAG, fallback to the standard text representation of MENTOR_DATABASE
        if "No matching community resources found" in retrieved_mentors or not retrieved_mentors:
            retrieved_mentors = "\n".join([
                f"- {m['mentor_id']}: {m['name']} ({m['role']}) | Expertise: {', '.join(m['expertise_areas'])} | Style: {m['teaching_style']}"
                for m in MENTOR_DATABASE
            ])

        growth_areas = []
        learning_style = "visual"
        if identity_data:
            growth_areas = identity_data.get("growth_areas", [])
            learning_style = identity_data.get("learning_preference", "visual")

        roadmap_title = learning_data.get("roadmap_title", "General learning path") if learning_data else "General learning path"

        prompt = f"""Find the best mentor match for this community member:

Member Name: {user_data.get('username', 'Unknown')}
Self-reported Interests/Skills: {', '.join(user_data.get('interests', []))}
Goals: {', '.join(user_data.get('goals', []))}
Growth areas (needs mentoring in): {', '.join(growth_areas)}
Learning style: {learning_style}
Learning path: {roadmap_title}
Timezone: {user_data.get('timezone', 'Asia/Kolkata')}

AVAILABLE MENTORS IN COMMUNITY (RETRIEVED VIA RAG):
{retrieved_mentors}

Select the PRIMARY best match and 1-2 backup options. Be specific about compatibility."""

        result_json, is_fallback = await llm_service.complete_json(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.3,
            max_tokens=settings.LLM_MAX_TOKENS_COMPLEX,
        )

        if is_fallback or not result_json:
            fallback = self._get_fallback(user_id, user_data)
            fallback["_is_fallback"] = True
            return fallback

        result_json["user_id"] = user_id
        result_json["_is_fallback"] = False
        primary = result_json.get("primary_mentor", {})
        logger.info(f"Mentor matched for {user_id}: {primary.get('name', 'unknown')}")
        return result_json

    def _get_fallback(self, user_id: str, user_data: Dict, *args, **kwargs) -> Dict[str, Any]:
        return get_mock_mentor(user_id, user_data)
