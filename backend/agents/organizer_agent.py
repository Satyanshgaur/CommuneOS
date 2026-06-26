"""
CommuneOS Organizer Agent
Converts community health metrics into prioritized action items and event suggestions.
"""
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from agents.base_agent import BaseAgent
from config import settings
from services.llm_service import llm_service
from services.mock_data import get_mock_organizer
from utils.logger import get_logger

logger = get_logger("agent.organizer")


class OrganizerAgent(BaseAgent):
    """
    Agent 6: Community Operations & Action Generation
    
    Takes health metrics as input and generates:
    - Prioritized action items for community managers
    - Event suggestions for topic gaps
    - Automation recommendations
    """
    name = "organizer_agent"
    cache_ttl = 1800  # 30 min

    SYSTEM_PROMPT = """You are the Organizer Agent for CommuneOS.
Your job is to convert community health insights into clear, actionable operational tasks.

You MUST return ONLY valid JSON in this exact structure:
{
  "action_items": [
    {
      "action_id": "unique-id",
      "title": "Clear action title",
      "description": "Detailed what to do and why",
      "priority": "critical|high|medium|low",
      "category": "welcome|engagement|content|event|moderation",
      "assignee": "who should do this",
      "deadline": "YYYY-MM-DD",
      "expected_impact": "Measurable expected outcome",
      "completed": false
    }
  ],
  "event_suggestions": [
    {
      "event_id": "unique-id",
      "title": "Event title",
      "type": "Workshop|AMA|Study Group|Webinar|Challenge",
      "topic": "Core topic",
      "rationale": "Why this event is needed now",
      "suggested_timing": "Day and time",
      "target_audience": "Who should attend",
      "expected_attendance": 0
    }
  ],
  "automation_recommendations": ["specific automation to implement"],
  "resource_allocation": "How to prioritize organizer time this week",
  "summary": "Brief executive summary of what needs to happen"
}

Priority definitions:
- critical: Must happen in 0-24 hours
- high: Must happen in 1-3 days
- medium: Should happen in 1-2 weeks
- low: Consider this month

Always address at-risk member situations as CRITICAL priority.
"""

    async def run_community(self, health_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Run organizer analysis based on health metrics."""
        import time
        start = time.time()
        cache_key = "community:organizer_plan"
        
        from services.cache_service import cache_service
        cached = cache_service.get(cache_key)
        if cached:
            return {"agent": self.name, "success": True, "data": cached, "is_fallback": False, "from_cache": True}
        
        try:
            result = await self._generate_actions(health_data or {})
            is_fallback = result.pop("_is_fallback", False)
            cache_service.set(cache_key, result, ttl=self.cache_ttl)
            
            from services.analytics import analytics_service
            analytics_service.record_agent_execution(self.name, (time.time() - start) * 1000, True, is_fallback)
            return {"agent": self.name, "success": True, "data": result, "is_fallback": is_fallback}
        except Exception as e:
            logger.error(f"Organizer agent failed: {e}", exc_info=True)
            fallback = get_mock_organizer(health_data)
            return {"agent": self.name, "success": True, "data": fallback, "is_fallback": True}

    async def _generate_actions(self, health_data: Dict) -> Dict[str, Any]:
        """Generate action plan from health metrics."""
        at_risk = health_data.get("at_risk_members", [])
        gaps = health_data.get("topic_gaps", [])
        health_score = health_data.get("community_health_score", 0.7)
        trending = health_data.get("trending_topics", [])
        
        today = datetime.utcnow().strftime("%Y-%m-%d")
        tomorrow = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
        next_week = (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        at_risk_text = "\n".join([
            f"- {m.get('username', 'unknown')}: {m.get('risk_level', 'unknown')} risk, {m.get('days_inactive', 0)} days inactive. Reason: {m.get('reason', '')}"
            for m in at_risk
        ]) if at_risk else "No at-risk members detected"

        gaps_text = "\n".join([
            f"- {g.get('topic', '')}: {g.get('unanswered_questions', 0)} unanswered questions, demand score: {g.get('demand_score', 0)}"
            for g in gaps
        ]) if gaps else "No significant gaps detected"

        prompt = f"""Generate an operational action plan for community managers based on this health data:

Community Health Score: {health_score} ({'Good' if health_score > 0.7 else 'Needs attention' if health_score > 0.5 else 'Critical'})
Trending Topics: {', '.join(trending) if trending else 'None identified'}

At-Risk Members:
{at_risk_text}

Knowledge Gaps:
{gaps_text}

Today's date: {today}
Deadline options: today={today}, tomorrow={tomorrow}, next week={next_week}

Generate specific, actionable tasks to address these issues. Prioritize member retention first, then content gaps, then events.
Include 3-5 action items and 2-3 event suggestions."""

        result_json, is_fallback = await llm_service.complete_json(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=settings.LLM_TEMPERATURE_ORGANIZER,
            max_tokens=settings.LLM_MAX_TOKENS_COMPLEX,
        )

        if is_fallback or not result_json:
            fallback = get_mock_organizer(health_data)
            fallback["_is_fallback"] = True
            return fallback

        # Ensure action_ids are unique
        for item in result_json.get("action_items", []):
            if not item.get("action_id"):
                item["action_id"] = f"action-{uuid.uuid4().hex[:8]}"
        for event in result_json.get("event_suggestions", []):
            if not event.get("event_id"):
                event["event_id"] = f"evt-{uuid.uuid4().hex[:8]}"

        result_json["_is_fallback"] = False
        logger.info(f"Organizer plan generated: {len(result_json.get('action_items', []))} actions, {len(result_json.get('event_suggestions', []))} events")
        return result_json

    async def _process(self, user_id: str, user_data: Dict, *args, **kwargs) -> Dict[str, Any]:
        return await self._generate_actions({})

    def _get_fallback(self, user_id: str, user_data: Dict, *args, **kwargs) -> Dict[str, Any]:
        return get_mock_organizer()
