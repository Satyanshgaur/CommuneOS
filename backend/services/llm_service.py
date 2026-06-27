"""
CommuneOS LLM Service
Groq primary (30 RPM free tier, fast inference) → OpenRouter fallback.
Both providers use OpenAI-compatible API.
"""
import asyncio
import json
import time
from typing import Any, Dict, Optional, Tuple

import httpx

from config import settings
from services.cache_service import cache_service
from utils.logger import get_logger

logger = get_logger("llm_service")


class LLMService:
    """
    Async LLM wrapper: Groq first (fast, generous free tier), OpenRouter fallback.
    """

    def __init__(self):
        self.timeout = settings.LLM_TIMEOUT_SECONDS
        self.max_retries = settings.AGENT_MAX_RETRIES

    def _groq_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json",
        }

    def _openrouter_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://communeos.ai",
            "X-Title": "CommuneOS Agent Backend",
        }

    async def _call(
        self,
        base_url: str,
        headers: Dict[str, str],
        model: str,
        messages: list,
        temperature: float,
        max_tokens: int,
        extra_payload: Optional[Dict] = None,
    ) -> Tuple[Optional[str], Optional[str]]:
        """Single API call. Returns (text, error_message)."""
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if extra_payload:
            payload.update(extra_payload)

        try:
            start = time.time()
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
            elapsed = round((time.time() - start) * 1000, 1)
            logger.info(f"LLM {model} response: {response.status_code} in {elapsed}ms")

            if response.status_code == 200:
                text = response.json()["choices"][0]["message"]["content"].strip()
                return text, None

            if response.status_code == 429:
                logger.warning(f"LLM {model} rate limited — failing fast")
                return None, "Rate limited"

            logger.error(f"LLM {model} error {response.status_code}: {response.text[:200]}")
            return None, f"API error {response.status_code}"

        except httpx.TimeoutException:
            logger.warning(f"LLM {model} timeout after {self.timeout}s")
            return None, "Timeout"
        except Exception as e:
            logger.error(f"LLM {model} unexpected error: {e}")
            return None, str(e)

    async def complete(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.5,
        max_tokens: int = 1500,
        use_cache: bool = True,
        model: Optional[str] = None,
    ) -> Tuple[str, bool]:
        """
        Send a completion. Tries Groq first, then OpenRouter.
        Returns (response_text, is_fallback).
        """
        messages = [
            {"role": "system", "content": system_prompt or "You are a helpful AI assistant for CommuneOS, an intelligent community management platform."},
            {"role": "user", "content": prompt},
        ]

        # ─── Cache check ─────────────────────────────────────────────────────
        cache_key = None
        if use_cache:
            cache_key = cache_service.llm_key(f"{system_prompt}\n{prompt}")
            cached = cache_service.get(cache_key)
            if cached:
                logger.info("LLM cache hit")
                return cached, False

        # ─── Groq (primary) ─────────────────────────────────────────────────
        if settings.GROQ_API_KEY:
            for groq_model in (settings.GROQ_MODEL, settings.GROQ_FALLBACK_MODEL):
                text, err = await self._call(
                    base_url=settings.GROQ_BASE_URL,
                    headers=self._groq_headers(),
                    model=groq_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                if text:
                    if use_cache and cache_key:
                        cache_service.set(cache_key, text, ttl=settings.CACHE_TTL_LLM)
                    logger.info(f"Groq success: {groq_model}")
                    return text, False
                if err == "Rate limited":
                    continue  # try next Groq model
                break  # non-retryable error, move to OpenRouter

        # ─── OpenRouter (fallback) ───────────────────────────────────────────
        if settings.OPENROUTER_API_KEY:
            extra_models = [
                m.strip() for m in settings.OPENROUTER_EXTRA_MODELS.split(",") if m.strip()
            ]
            or_models = list(dict.fromkeys(
                [settings.OPENROUTER_MODEL, settings.OPENROUTER_FALLBACK_MODEL] + extra_models
            ))[:3]

            text, err = await self._call(
                base_url=settings.OPENROUTER_BASE_URL,
                headers=self._openrouter_headers(),
                model=or_models[0],
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                extra_payload={"models": or_models, "route": "fallback"},
            )
            if text:
                if use_cache and cache_key:
                    cache_service.set(cache_key, text, ttl=settings.CACHE_TTL_LLM)
                return text, False

        logger.warning("LLM all providers failed — using mock data")
        return "", True

    async def complete_json(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.5,
        max_tokens: int = 1500,
        use_cache: bool = True,
    ) -> Tuple[Optional[Dict], bool]:
        """Complete and parse response as JSON. Returns (dict_or_None, is_fallback)."""
        json_system = (
            (system_prompt or "") +
            "\n\nIMPORTANT: You MUST respond with ONLY valid JSON. No markdown, no explanation, no code blocks. Pure JSON only."
        )

        text, is_fallback = await self.complete(
            prompt=prompt,
            system_prompt=json_system,
            temperature=temperature,
            max_tokens=max_tokens,
            use_cache=use_cache,
        )

        if is_fallback or not text:
            return None, True

        # Strip markdown fences if model wrapped JSON
        clean = text.strip()
        if clean.startswith("```"):
            parts = clean.split("```")
            clean = parts[2] if len(parts) > 2 else parts[-1]
            if clean.startswith("json"):
                clean = clean[4:]
            clean = clean.strip()

        try:
            return json.loads(clean), False
        except json.JSONDecodeError as e:
            logger.warning(f"LLM JSON parse failed: {e} | text[:200]={text[:200]}")
            return None, True


# Module-level singleton
llm_service = LLMService()
