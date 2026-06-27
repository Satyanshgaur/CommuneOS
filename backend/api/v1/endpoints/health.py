"""
CommuneOS Health & Metrics Endpoints
Service health checks and performance metrics.
"""
import time
from typing import Any, Dict

from fastapi import APIRouter, Depends

from api.v1.dependencies import get_request_id
from services.analytics import analytics_service
from services.cache_service import cache_service
from services.llm_service import llm_service
from utils.formatters import success_response
from utils.logger import get_logger

router = APIRouter(tags=["Health & Metrics"])
logger = get_logger("endpoint.health")

_startup_time = time.time()


@router.get("/health")
async def health_check(request_id: str = Depends(get_request_id)) -> Dict[str, Any]:
    """
    Overall service health check.
    Returns: status, uptime, version info.
    """
    uptime_s = round(time.time() - _startup_time, 1)
    return success_response(
        data={
            "status": "healthy",
            "version": "1.0.0",
            "uptime_seconds": uptime_s,
            "service": "CommuneOS Agent Backend",
        },
        request_id=request_id,
        message="All systems operational"
    )


@router.get("/health/agents")
async def agents_health(request_id: str = Depends(get_request_id)) -> Dict[str, Any]:
    """
    Individual agent health status.
    Returns performance stats per agent.
    """
    from utils.constants import ALL_AGENTS
    agent_stats = {
        agent: analytics_service.get_agent_stats(agent)
        for agent in ALL_AGENTS
    }
    return success_response(
        data={"agents": agent_stats},
        request_id=request_id
    )


@router.get("/health/llm")
async def llm_health(request_id: str = Depends(get_request_id)) -> Dict[str, Any]:
    """
    LLM service status check.
    Makes a lightweight test call to OpenRouter.
    """
    llm_status = await llm_service.health_check()
    return success_response(data=llm_status, request_id=request_id)


@router.get("/health/cache")
async def cache_health(request_id: str = Depends(get_request_id)) -> Dict[str, Any]:
    """Cache service statistics."""
    stats = cache_service.stats()
    return success_response(data=stats, request_id=request_id)


@router.get("/metrics/performance")
async def performance_metrics(request_id: str = Depends(get_request_id)) -> Dict[str, Any]:
    """
    Full performance metrics summary.
    Includes agent latencies, API call counts, error rates.
    """
    summary = analytics_service.get_summary()
    return success_response(data=summary, request_id=request_id)


@router.delete("/cache/clear")
async def clear_cache(request_id: str = Depends(get_request_id)) -> Dict[str, Any]:
    """Clear all cached data (admin endpoint)."""
    cache_service.clear_all()
    logger.warning("All cache cleared via admin endpoint")
    return success_response(
        data={"cleared": True},
        request_id=request_id,
        message="Cache cleared"
    )
