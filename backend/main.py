"""
CommuneOS — FastAPI Application Entry Point
Six-agent AI platform for intelligent community management.

Start with:
    uvicorn main:app --reload --port 8000
"""
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.errors import register_error_handlers
from api.v1.endpoints import agents, community, health, users
from config import settings
from utils.logger import get_logger, setup_logging

# Initialize logging first
setup_logging()
logger = get_logger("main")

# ─── FastAPI App ───────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ─── CORS Middleware ───────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Request Timing Middleware ─────────────────────────────────────────────────
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add X-Process-Time header to all responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    response.headers["X-Process-Time-Ms"] = str(round(process_time, 2))
    response.headers["X-Service"] = "CommuneOS-Backend"
    return response

# ─── Register Error Handlers ───────────────────────────────────────────────────
register_error_handlers(app)

# ─── Register API Routers ──────────────────────────────────────────────────────
API_PREFIX = "/api/v1"

app.include_router(users.router, prefix=API_PREFIX)
app.include_router(agents.router, prefix=API_PREFIX)
app.include_router(community.router, prefix=API_PREFIX)
app.include_router(health.router)  # /health, /metrics — no prefix

# ─── Startup / Shutdown Events ─────────────────────────────────────────────────
@app.on_event("startup")
async def on_startup():
    """Log startup info and warm up services."""
    logger.info("=" * 60)
    logger.info(f"  CommuneOS Agent Backend v{settings.APP_VERSION}")
    logger.info(f"  Running on http://{settings.HOST}:{settings.PORT}")
    logger.info(f"  API Docs: http://localhost:{settings.PORT}/docs")
    logger.info(f"  LLM Model: {settings.OPENROUTER_MODEL}")
    logger.info(f"  LLM Key: {'✅ Configured' if settings.has_llm_key else '⚠️  Missing (mock mode)'}")
    logger.info(f"  Mock Fallback: {'ON' if settings.USE_MOCK_DATA_FALLBACK else 'OFF'}")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def on_shutdown():
    """Clean up on shutdown."""
    from services.cache_service import cache_service
    cache_service.clear_all()
    logger.info("CommuneOS Backend shutdown complete")


# ─── Root Route ────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    """Root endpoint — API info."""
    return {
        "service": "CommuneOS Agent Backend",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "api": f"{API_PREFIX}/",
        "agents": [
            "identity_agent",
            "discovery_agent",
            "learning_agent",
            "mentor_agent",
            "health_agent",
            "organizer_agent",
        ],
    }


# ─── Development Runner ────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
    )
