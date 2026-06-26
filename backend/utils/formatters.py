"""
CommuneOS Response Formatters
Standardized response envelope builders for all API endpoints.
"""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def success_response(
    data: Any,
    request_id: Optional[str] = None,
    message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Build a standardized success response envelope.
    
    Shape:
    {
        "success": true,
        "data": {...},
        "error": null,
        "message": "...",
        "timestamp": "ISO8601",
        "request_id": "UUID"
    }
    """
    return {
        "success": True,
        "data": data,
        "error": None,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": request_id or str(uuid.uuid4()),
    }


def error_response(
    error: str,
    request_id: Optional[str] = None,
    data: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Build a standardized error response envelope.
    
    Shape:
    {
        "success": false,
        "data": null,
        "error": "...",
        "timestamp": "ISO8601",
        "request_id": "UUID"
    }
    """
    return {
        "success": False,
        "data": data,
        "error": error,
        "message": None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": request_id or str(uuid.uuid4()),
    }


def agent_response_envelope(
    agent_name: str,
    user_id: str,
    data: Any,
    success: bool = True,
    error_msg: Optional[str] = None,
    processing_time_ms: float = 0,
    is_fallback: bool = False,
) -> Dict[str, Any]:
    """
    Build a standardized agent response.
    Used internally before wrapping in the API envelope.
    """
    return {
        "agent": agent_name,
        "user_id": user_id,
        "success": success,
        "data": data,
        "error": error_msg,
        "processing_time_ms": round(processing_time_ms, 2),
        "is_fallback": is_fallback,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def format_processing_time(start_time: float, end_time: float) -> float:
    """Convert start/end timestamps to milliseconds."""
    return round((end_time - start_time) * 1000, 2)
