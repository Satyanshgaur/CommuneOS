"""
CommuneOS Backend Configuration Management
Handles all environment variables and application settings.
"""
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from .env or environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # ─── API Metadata ──────────────────────────────────────────────────────────
    APP_TITLE: str = "CommuneOS Agent Backend"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Six-agent AI platform for intelligent community management"

    # ─── Server Settings ───────────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    RELOAD: bool = True

    # ─── CORS Configuration ────────────────────────────────────────────────────
    FRONTEND_URL: str = "http://localhost:3000"
    FRONTEND_URL_DEV: str = "http://127.0.0.1:5500"

    @property
    def cors_origins(self) -> List[str]:
        return [
            self.FRONTEND_URL,
            self.FRONTEND_URL_DEV,
            "http://localhost:8080",
            "http://127.0.0.1:8080",
            "http://localhost:5500",
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:3002",
            "http://localhost:3003",
            "http://127.0.0.1:3001",
            "http://127.0.0.1:3002",
            "http://127.0.0.1:3003",
            "null",  # file:// origins for local HTML files
        ]

    # ─── OpenRouter LLM Settings ───────────────────────────────────────────────
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "google/gemma-4-31b-it:free"
    OPENROUTER_FALLBACK_MODEL: str = "meta-llama/llama-3-8b-instruct:free"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # ─── LLM Tuning ───────────────────────────────────────────────────────────
    LLM_TIMEOUT_SECONDS: int = 30
    LLM_MAX_TOKENS_SIMPLE: int = 500
    LLM_MAX_TOKENS_COMPLEX: int = 2000
    LLM_TEMPERATURE_IDENTITY: float = 0.3
    LLM_TEMPERATURE_HEALTH: float = 0.3
    LLM_TEMPERATURE_DISCOVERY: float = 0.5
    LLM_TEMPERATURE_LEARNING: float = 0.5
    LLM_TEMPERATURE_ORGANIZER: float = 0.6

    # ─── Agent Settings ────────────────────────────────────────────────────────
    AGENT_TIMEOUT_SECONDS: int = 30
    AGENT_MAX_RETRIES: int = 2
    USE_MOCK_DATA_FALLBACK: bool = True

    # ─── Cache Settings ────────────────────────────────────────────────────────
    CACHE_TTL_AGENT: int = 3600       # 1 hour
    CACHE_TTL_LLM: int = 86400        # 24 hours
    CACHE_TTL_DATA: int = 1800        # 30 minutes
    USE_REDIS: bool = False
    REDIS_URL: str = "redis://localhost:6379"

    # ─── Supabase Configuration ────────────────────────────────────────────────
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""

    # ─── Logging ───────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/communeos.log"

    # ─── Feature Flags ─────────────────────────────────────────────────────────
    ENABLE_ANALYTICS: bool = True
    ENABLE_MOCK_DATA: bool = True

    @property
    def has_llm_key(self) -> bool:
        """Check if LLM API key is configured."""
        return bool(self.OPENROUTER_API_KEY)


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — singleton pattern."""
    return Settings()


# Global settings instance
settings = get_settings()
