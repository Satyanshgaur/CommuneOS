"""
CommuneOS Memory Agent
Dedicated agent for querying User Vector DB and Community Vector DB, merging results, and returning context.
"""
from typing import Any, Dict, List, Optional
from agents.base_agent import BaseAgent
from services.vector_db import query_user_memory, query_community_memory
from utils.logger import get_logger

logger = get_logger("agent.memory")

class MemoryAgent(BaseAgent):
    """
    Memory Agent
    Responsible for retrieving relevant context from both the user's vector memory
    (resume chunks) and the community knowledge base, then merging them.
    """
    name = "memory_agent"
    cache_ttl = 600  # 10 minutes cache for specific queries

    async def _process(
        self, user_id: str, user_data: Dict,
        query: Optional[str] = None,
        filter_type: Optional[str] = None,
        n_user_results: int = 3,
        n_community_results: int = 4,
        *args, **kwargs
    ) -> Dict[str, Any]:
        """
        Query both user and community databases based on a search term / question.
        Returns a structured dictionary of relevant context.
        """
        # If query is not specified, construct it from user bio, interests, and goals
        if not query:
            bio = user_data.get("bio", "")
            goals = user_data.get("goals", [])
            if isinstance(goals, list):
                goals_str = " ".join(goals)
            else:
                goals_str = str(goals)
            interests = " ".join(user_data.get("interests", []))
            query = f"{bio} {goals_str} {interests}".strip()
            if not query:
                query = "technology and software engineering"

        logger.info(f"[{user_id}] Memory Agent querying with term: '{query}'")

        # 1. Search User Vector DB
        user_matches = query_user_memory(user_id=user_id, query_text=query, n_results=n_user_results)
        
        # 2. Search Community Vector DB
        community_matches = query_community_memory(query_text=query, n_results=n_community_results, filter_type=filter_type)

        # 3. Format contexts
        user_docs = [m["document"] for m in user_matches]
        community_docs = [m["document"] for m in community_matches]

        # Construct a combined readable text
        user_context_block = "\n---\n".join(user_docs) if user_docs else "No specific personal resume matches found."
        community_context_block = "\n---\n".join(community_docs) if community_docs else "No matching community resources found."

        merged_text = (
            f"=== RETRIEVED USER RESUME CONTEXT ===\n{user_context_block}\n\n"
            f"=== RETRIEVED COMMUNITY CONTEXT ===\n{community_context_block}"
        )

        return {
            "query": query,
            "user_matches": user_matches,
            "community_matches": community_matches,
            "user_context_block": user_context_block,
            "community_context_block": community_context_block,
            "merged_text": merged_text,
        }

    def _get_fallback(self, user_id: str, user_data: Dict, *args, **kwargs) -> Dict[str, Any]:
        """Deterministic fallback when database or model querying fails."""
        # Provide some basic context from mock data
        bio = user_data.get("bio", "No bio provided")
        goals = ", ".join(user_data.get("goals", [])) if isinstance(user_data.get("goals"), list) else user_data.get("goals", "")
        skills = ", ".join(user_data.get("skills", {}).keys()) if isinstance(user_data.get("skills"), dict) else ""
        
        return {
            "query": "fallback",
            "user_matches": [],
            "community_matches": [],
            "user_context_block": f"Section: Bio\nContent: {bio}\nSection: Goals\nContent: {goals}\nSection: Skills\nContent: {skills}",
            "community_context_block": "Mock community fallback resource list.",
            "merged_text": "ChromaDB fallback context.",
        }
