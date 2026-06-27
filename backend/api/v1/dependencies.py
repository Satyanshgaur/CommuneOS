"""
CommuneOS API Dependencies
FastAPI dependency injection functions shared across endpoints.
"""
import uuid
from typing import Optional

from fastapi import Header, HTTPException, Request, status

from services.analytics import analytics_service
from utils.logger import get_logger

logger = get_logger("dependencies")


async def get_request_id(x_request_id: Optional[str] = Header(None)) -> str:
    """Extract or generate a request ID for tracking."""
    return x_request_id or str(uuid.uuid4())


async def log_request(request: Request) -> None:
    """Middleware-style dependency to log incoming requests."""
    logger.info(f"→ {request.method} {request.url.path}")
    analytics_service.record_api_call(request.url.path)


def validate_user_id_param(user_id: str) -> str:
    """Validate and normalize user_id path parameter."""
    import re
    if not re.match(r'^[a-zA-Z0-9_\-]+$', user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user_id format: '{user_id}'. Must be alphanumeric with underscores/hyphens."
        )
    return user_id.lower()
