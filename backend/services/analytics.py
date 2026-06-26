"""
CommuneOS Analytics Service
Tracks agent performance, usage, and error metrics in memory.
"""
import time
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from utils.logger import get_logger

logger = get_logger("analytics")


class AnalyticsService:
    """
    In-memory analytics tracker.
    Records agent execution times, error counts, and fallback usage.
    """

    def __init__(self):
        self._agent_calls: Dict[str, List[float]] = defaultdict(list)   # agent → [latencies ms]
        self._agent_errors: Dict[str, int] = defaultdict(int)
        self._agent_fallbacks: Dict[str, int] = defaultdict(int)
        self._api_calls: Dict[str, int] = defaultdict(int)              # endpoint → count
        self._llm_calls: int = 0
        self._llm_total_ms: float = 0.0
        self._started_at: datetime = datetime.utcnow()

    def record_agent_execution(
        self,
        agent_name: str,
        duration_ms: float,
        success: bool,
        is_fallback: bool,
    ) -> None:
        """Record a single agent execution event."""
        self._agent_calls[agent_name].append(duration_ms)
        if not success:
            self._agent_errors[agent_name] += 1
        if is_fallback:
            self._agent_fallbacks[agent_name] += 1
        
        logger.info(
            f"Agent execution | {agent_name} | {duration_ms:.0f}ms | "
            f"success={success} | fallback={is_fallback}"
        )

    def record_api_call(self, endpoint: str) -> None:
        """Record an API endpoint being called."""
        self._api_calls[endpoint] += 1

    def record_llm_call(self, duration_ms: float) -> None:
        """Record an LLM API call."""
        self._llm_calls += 1
        self._llm_total_ms += duration_ms

    def get_agent_stats(self, agent_name: str) -> Dict[str, Any]:
        """Get performance stats for a specific agent."""
        latencies = self._agent_calls.get(agent_name, [])
        if not latencies:
            return {"agent": agent_name, "calls": 0}
        
        sorted_lat = sorted(latencies)
        n = len(sorted_lat)
        
        return {
            "agent": agent_name,
            "calls": n,
            "errors": self._agent_errors.get(agent_name, 0),
            "fallbacks": self._agent_fallbacks.get(agent_name, 0),
            "avg_ms": round(sum(sorted_lat) / n, 1),
            "p50_ms": round(sorted_lat[n // 2], 1),
            "p95_ms": round(sorted_lat[min(int(n * 0.95), n - 1)], 1),
            "p99_ms": round(sorted_lat[min(int(n * 0.99), n - 1)], 1),
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get overall analytics summary."""
        all_agents_stats = {
            name: self.get_agent_stats(name)
            for name in self._agent_calls
        }
        
        return {
            "uptime_seconds": (datetime.utcnow() - self._started_at).total_seconds(),
            "total_api_calls": sum(self._api_calls.values()),
            "llm_calls": self._llm_calls,
            "llm_avg_ms": round(self._llm_total_ms / max(self._llm_calls, 1), 1),
            "agents": all_agents_stats,
            "top_endpoints": dict(
                sorted(self._api_calls.items(), key=lambda x: x[1], reverse=True)[:10]
            ),
        }


# Singleton instance
analytics_service = AnalyticsService()
