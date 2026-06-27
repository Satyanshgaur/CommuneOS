"""
CommuneOS Discovery Agent
Matches users with community channels and learning resources by querying the Memory Agent.
Supports answering specific user questions with RAG personalization.
"""
import json
from typing import Any, Dict, List, Optional

from agents.base_agent import BaseAgent
from agents.memory_agent import MemoryAgent
from config import settings
from services.llm_service import llm_service
from services.mock_data import get_mock_discovery
from utils.constants import COMMUNITY_CHANNELS
from utils.logger import get_logger

logger = get_logger("agent.discovery")


class DiscoveryAgent(BaseAgent):
    """
    Agent 2: Channel & Resource Discovery
    
    Recommends channels, resources, and answers user questions
    by using RAG context retrieved via the Memory Agent.
    """
    name = "discovery_agent"
    cache_ttl = 3600

    SYSTEM_PROMPT = """You are the Discovery Agent for CommuneOS.
Your job is to match community members with the most relevant channels and resources based on their profile and resume context.
You must also answer their specific question using the retrieved context.

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
  "discovery_priority": ["channel/resource name to explore first", ...],
  "answer": "A highly personalized answer to the user's question, grounding the recommendation in their skills, goals, and experience.",
  "reasoning": "2 sentences summarizing why these recommendations are made."
}

Rules:
- Recommend 3-5 channels and 3-5 resources.
- Base your recommendation and your answer on the user's profile and the retrieved resume/community context.
"""

    async def _process(
        self, user_id: str, user_data: Dict,
        identity_data: Optional[Dict] = None,
        query: Optional[str] = None,
        *args, **kwargs
    ) -> Dict[str, Any]:
        """Match channels and resources using RAG context from Memory Agent."""
        # Use user question or build a default query
        search_query = query or user_data.get("user_question") or "Which event or channel should I attend?"
        
        # 1. Fetch personalization context from Memory Agent
        memory_agent = MemoryAgent()
        memory_res = await memory_agent.run(user_id, user_data, query=search_query)
        memory_data = memory_res.get("data", {})
        merged_context = memory_data.get("merged_text", "No context found.")

        # Build basic details
        bio = user_data.get("bio", "No bio provided")
        goals = user_data.get("goals", [])
        
        prompt = f"""Personalize recommendations and answer the user's question:

User ID: {user_id}
User Bio: {bio}
User Goals: {', '.join(goals) if isinstance(goals, list) else str(goals)}
User Question: "{search_query}"

RETRIEVED MEMORY CONTEXT (RESUME + COMMUNITY DATA):
{merged_context}

Based on this, return the personalized channels, resources, and the answer to the user's question in the JSON format required."""

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
        logger.info(f"Discovery complete for {user_id}: {len(result_json.get('recommended_channels', []))} channels recommended")
        return result_json

    def _get_fallback(self, user_id: str, user_data: Dict, *args, **kwargs) -> Dict[str, Any]:
        mock_disc = get_mock_discovery(user_id, user_data)
        mock_disc["answer"] = "You should attend the GPU Systems Workshop since your profile shows strong interest in low-level GPU programming."
        mock_disc["reasoning"] = "Matched user tags against available channels. Recommended machine learning and infrastructure topics."
        return mock_disc
