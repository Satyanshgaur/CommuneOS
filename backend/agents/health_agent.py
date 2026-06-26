"""
CommuneOS Health Agent
Monitors community health: detects churn risk, engagement gaps, and trending topics.
Runs at community level (not per-user).
"""
from typing import Any, Dict, Optional

from agents.base_agent import BaseAgent
from config import settings
from services.llm_service import llm_service
from services.mock_data import get_mock_health
from utils.logger import get_logger

logger = get_logger("agent.health")

# Sample community activity data (in Phase 4 this comes from database)
SAMPLE_COMMUNITY_DATA = {
    "total_members": 247,
    "active_7d": 89,
    "new_this_week": 12,
    "unanswered_questions": [
        {"topic": "CUDA optimization", "count": 12, "oldest_days": 3},
        {"topic": "MLOps deployment", "count": 8, "oldest_days": 2},
        {"topic": "Rust for systems", "count": 5, "oldest_days": 5},
        {"topic": "PyTorch DataLoaders", "count": 6, "oldest_days": 1},
    ],
    "inactive_members": [
        {"user_id": "user-456", "username": "inactive_dev", "days_inactive": 18},
        {"user_id": "user-789", "username": "new_joiner_jan", "days_inactive": 9},
        {"user_id": "user-321", "username": "casual_learner", "days_inactive": 6},
    ],
    "channel_activity": [
        {"channel": "Machine Learning", "messages_7d": 145, "trend": "rising"},
        {"channel": "Systems Programming", "messages_7d": 89, "trend": "stable"},
        {"channel": "GPU & Accelerators", "messages_7d": 67, "trend": "declining"},
        {"channel": "Data Science", "messages_7d": 102, "trend": "rising"},
    ],
    "member_satisfaction_avg": 4.2,
}


class HealthAgent(BaseAgent):
    """
    Agent 5: Community Health Monitor
    
    Analyzes community-level data to detect:
    - Members at risk of churning
    - Topic gaps and underserved areas
    - Engagement trends
    - Overall community health score
    """
    name = "health_agent"
    cache_ttl = 1800  # 30 min (health data refreshes more often)

    SYSTEM_PROMPT = """You are the Community Health Agent for CommuneOS.
Your job is to analyze community activity data and produce a health report.

You MUST return ONLY valid JSON in this exact structure:
{
  "community_health_score": 0.0-1.0,
  "total_members": 0,
  "active_members_7d": 0,
  "at_risk_members": [
    {
      "user_id": "id",
      "username": "name",
      "risk_level": "high|medium|low",
      "days_inactive": 0,
      "last_seen": "YYYY-MM-DD",
      "reason": "Why they are at risk"
    }
  ],
  "topic_gaps": [
    {
      "topic": "Topic name",
      "unanswered_questions": 0,
      "demand_score": 0.0-1.0,
      "suggestion": "Specific action to address this gap"
    }
  ],
  "trending_topics": ["topic1", "topic2"],
  "engagement_trend": "rising|stable|declining",
  "summary": "One paragraph health summary with key insights"
}

Churn thresholds:
- High risk: 14+ days inactive
- Medium risk: 7-13 days inactive
- Low risk: 4-6 days inactive

Health score calculation:
- 0.8-1.0: Excellent (>50% active, low churn, topics well-served)
- 0.6-0.8: Good (30-50% active, some churn, minor gaps)
- 0.4-0.6: Moderate (20-30% active, noticeable churn)
- <0.4: Poor (<20% active, high churn, significant gaps)
"""

    async def run_community(self, community_id: str = "comm-gpu", community_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Run health analysis on community-level data (not per-user)."""
        import time
        start = time.time()
        cache_key = f"community:health_report:{community_id}"
        
        from services.cache_service import cache_service
        cached = cache_service.get(cache_key)
        if cached:
            return {"agent": self.name, "success": True, "data": cached, "is_fallback": False, "from_cache": True}
        
        try:
            data = community_data or SAMPLE_COMMUNITY_DATA
            result = await self._analyze_community(community_id, data)
            is_fallback = result.pop("_is_fallback", False)
            cache_service.set(cache_key, result, ttl=self.cache_ttl)
            
            from services.analytics import analytics_service
            analytics_service.record_agent_execution(self.name, (time.time() - start) * 1000, True, is_fallback)
            return {"agent": self.name, "success": True, "data": result, "is_fallback": is_fallback}
        except Exception as e:
            logger.error(f"Health agent failed: {e}", exc_info=True)
            fallback = get_mock_health(community_id)
            return {"agent": self.name, "success": True, "data": fallback, "is_fallback": True}

    async def _analyze_community(self, community_id: str, community_data: Dict) -> Dict[str, Any]:
        """Run LLM analysis on community data."""
        inactive_text = "\n".join([
            f"- {m['username']}: {m['days_inactive']} days inactive"
            for m in community_data.get("inactive_members", [])
        ])
        
        questions_text = "\n".join([
            f"- {q['topic']}: {q['count']} unanswered questions (oldest: {q['oldest_days']} days)"
            for q in community_data.get("unanswered_questions", [])
        ])
        
        channels_text = "\n".join([
            f"- {c['channel']}: {c['messages_7d']} messages this week (trend: {c['trend']})"
            for c in community_data.get("channel_activity", [])
        ])

        prompt = f"""Analyze this community's health data:

Community Overview:
- Total members: {community_data.get('total_members', 0)}
- Active last 7 days: {community_data.get('active_7d', 0)} ({round(community_data.get('active_7d', 0) / max(community_data.get('total_members', 1), 1) * 100)}%)
- New members this week: {community_data.get('new_this_week', 0)}
- Member satisfaction avg: {community_data.get('member_satisfaction_avg', 'N/A')}/5

Inactive Members:
{inactive_text if inactive_text else 'None'}

Unanswered Questions by Topic:
{questions_text if questions_text else 'None'}

Channel Activity:
{channels_text if channels_text else 'None'}

Provide a comprehensive community health analysis with specific, actionable insights."""

        result_json, is_fallback = await llm_service.complete_json(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=settings.LLM_TEMPERATURE_HEALTH,
            max_tokens=settings.LLM_MAX_TOKENS_COMPLEX,
        )

        if is_fallback or not result_json:
            fallback = get_mock_health(community_id)
            fallback["_is_fallback"] = True
            return fallback

        result_json["_is_fallback"] = False
        logger.info(f"Health analysis complete: score={result_json.get('community_health_score', 0)}, at_risk={len(result_json.get('at_risk_members', []))}")
        return result_json

    # Implement abstract methods (health agent is community-level, not per-user)
    async def _process(self, user_id: str, user_data: Dict, *args, **kwargs) -> Dict[str, Any]:
        return await self._analyze_community(SAMPLE_COMMUNITY_DATA)

    def _get_fallback(self, user_id: str, user_data: Dict, *args, **kwargs) -> Dict[str, Any]:
        return get_mock_health()
