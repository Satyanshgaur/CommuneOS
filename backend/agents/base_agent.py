"""
CommuneOS Base Agent
All 6 agents inherit from this class for common functionality:
- Execution timing
- Caching
- Fallback to mock data
- Error handling
- Analytics tracking
"""
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple

from config import settings
from services.analytics import analytics_service
from services.cache_service import cache_service
from utils.logger import get_logger

logger = get_logger("base_agent")


class BaseAgent(ABC):
    """
    Abstract base class for all CommuneOS agents.
    Provides common infrastructure: caching, timing, error handling, fallback.
    """

    name: str = "base_agent"
    cache_ttl: int = 3600  # 1 hour default

    def __init__(self):
        self.logger = get_logger(f"agent.{self.name}")

    # ─── Abstract Methods (to be implemented by each agent) ───────────────────

    @abstractmethod
    async def _process(self, user_id: str, user_data: Dict, *args, **kwargs) -> Dict[str, Any]:
        """Core processing logic — must be implemented by each agent."""
        ...

    @abstractmethod
    def _get_fallback(self, user_id: str, user_data: Dict, *args, **kwargs) -> Dict[str, Any]:
        """Return deterministic fallback data when LLM fails."""
        ...

    # ─── Public run() method ──────────────────────────────────────────────────

    async def run(self, user_id: str, user_data: Dict, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute the agent with full lifecycle:
        1. Check cache
        2. Run processing (with LLM)
        3. On failure, use fallback
        4. Cache result
        5. Record analytics
        
        Returns a standardized response dict.
        """
        start_time = time.time()
        cache_key = cache_service.agent_key(self.name, user_id)
        is_fallback = False

        # ─── Step 1: Cache check ──────────────────────────────────────────────
        cached = cache_service.get(cache_key)
        if cached:
            self.logger.info(f"Cache hit for {user_id}")
            return self._build_response(user_id, cached, is_fallback=False, from_cache=True, start_time=start_time)

        # ─── Step 2: Attempt LLM processing ──────────────────────────────────
        try:
            data = await self._process(user_id, user_data, *args, **kwargs)
            is_fallback = data.pop("_is_fallback", False)
        except Exception as e:
            self.logger.error(f"Agent {self.name} failed for {user_id}: {e}", exc_info=True)
            data = self._get_fallback(user_id, user_data, *args, **kwargs)
            data.pop("_is_fallback", None)
            is_fallback = True

        # ─── Step 3: Cache result ─────────────────────────────────────────────
        cache_service.set(cache_key, data, ttl=self.cache_ttl)

        # ─── Step 4: Record analytics ─────────────────────────────────────────
        elapsed_ms = (time.time() - start_time) * 1000
        analytics_service.record_agent_execution(
            agent_name=self.name,
            duration_ms=elapsed_ms,
            success=True,
            is_fallback=is_fallback,
        )

        return self._build_response(user_id, data, is_fallback=is_fallback, start_time=start_time)

    def _build_response(
        self,
        user_id: str,
        data: Dict,
        is_fallback: bool = False,
        from_cache: bool = False,
        start_time: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Build the standardized agent response envelope."""
        elapsed_ms = (time.time() - start_time) * 1000 if start_time else 0
        return {
            "agent": self.name,
            "user_id": user_id,
            "success": True,
            "data": data,
            "error": None,
            "processing_time_ms": round(elapsed_ms, 1),
            "is_fallback": is_fallback,
            "from_cache": from_cache,
        }
