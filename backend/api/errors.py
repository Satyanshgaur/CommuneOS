"""
CommuneOS Global Error Handling
FastAPI exception handlers for all error categories.
"""
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from utils.logger import get_logger

logger = get_logger("errors")


def _error_body(status_code: int, error: str, detail: str = None) -> dict:
    return {
        "success": False,
        "data": None,
        "error": error,
        "detail": detail,
        "message": None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": str(uuid.uuid4()),
    }


def register_error_handlers(app: FastAPI) -> None:
    """Register all global exception handlers on the FastAPI app."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle Pydantic/FastAPI request validation errors → 422."""
        errors = exc.errors()
        logger.warning(f"Validation error on {request.url}: {errors}")
        detail = "; ".join([f"{'.'.join(str(l) for l in e['loc'])}: {e['msg']}" for e in errors])
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_body(422, "Validation Error", detail),
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle value errors → 400 Bad Request."""
        logger.warning(f"ValueError on {request.url}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=_error_body(400, "Bad Request", str(exc)),
        )

    @app.exception_handler(KeyError)
    async def key_error_handler(request: Request, exc: KeyError):
        """Handle missing key errors → 404 Not Found."""
        logger.warning(f"KeyError on {request.url}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=_error_body(404, "Not Found", f"Resource not found: {exc}"),
        )

    @app.exception_handler(TimeoutError)
    async def timeout_error_handler(request: Request, exc: TimeoutError):
        """Handle timeout errors → 503 Service Unavailable."""
        logger.error(f"Timeout on {request.url}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=_error_body(503, "Service Unavailable", "Operation timed out. Fallback data may be returned."),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Catch-all for unexpected exceptions → 500 Internal Server Error."""
        logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_body(500, "Internal Server Error", "An unexpected error occurred."),
        )
