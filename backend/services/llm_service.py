"""
CommuneOS LLM Service
OpenRouter API wrapper with retry logic and fallback handling.
Supports google/gemma-4-31b-it:free as primary model.
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
    Async wrapper around the OpenRouter API.
    Handles: authentication, retries, timeouts, response parsing, fallback.
    """

    def __init__(self):
        self.base_url = settings.OPENROUTER_BASE_URL
        self.api_key = settings.OPENROUTER_API_KEY
        self.primary_model = settings.OPENROUTER_MODEL
        self.fallback_model = settings.OPENROUTER_FALLBACK_MODEL
        self.timeout = settings.LLM_TIMEOUT_SECONDS
        self.max_retries = settings.AGENT_MAX_RETRIES

    def _get_headers(self) -> Dict[str, str]:
        """Build request headers for OpenRouter API."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://communeos.ai",
            "X-Title": "CommuneOS Agent Backend",
        }

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
        Send a completion request to OpenRouter.
        
        Returns:
            (response_text, is_fallback)
        """
        if not self.api_key:
            logger.warning("No OPENROUTER_API_KEY configured — using mock data")
            return "", True

        # ─── Check cache ─────────────────────────────────────────────────────
        cache_key = None
        if use_cache:
            full_prompt = f"{system_prompt}\n{prompt}"
            cache_key = cache_service.llm_key(full_prompt)
            cached = cache_service.get(cache_key)
            if cached:
                logger.info("LLM cache hit")
                return cached, False

        selected_model = model or self.primary_model
        
        # ─── Build request ────────────────────────────────────────────────────
        payload = {
            "model": selected_model,
            "messages": [
                {"role": "system", "content": system_prompt or "You are a helpful AI assistant for CommuneOS, an intelligent community management platform."},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # ─── Retry loop ───────────────────────────────────────────────────────
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                start = time.time()
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=self._get_headers(),
                        json=payload,
                    )
                
                elapsed = round((time.time() - start) * 1000, 1)
                logger.info(f"LLM response: {response.status_code} in {elapsed}ms (attempt {attempt + 1})")

                if response.status_code == 200:
                    data = response.json()
                    text = data["choices"][0]["message"]["content"].strip()
                    
                    # Cache the successful response
                    if use_cache and cache_key:
                        cache_service.set(cache_key, text, ttl=settings.CACHE_TTL_LLM)
                    
                    return text, False

                elif response.status_code == 429:
                    logger.warning(f"LLM rate limited (attempt {attempt + 1})")
                    if attempt < self.max_retries:
                        await asyncio.sleep(2 ** attempt)  # exponential backoff
                    last_error = "Rate limited"

                elif response.status_code in (502, 503, 504):
                    logger.warning(f"LLM service unavailable {response.status_code}")
                    if attempt == 0 and selected_model == self.primary_model:
                        # Try fallback model
                        logger.info(f"Switching to fallback model: {self.fallback_model}")
                        payload["model"] = self.fallback_model
                    last_error = f"Service error {response.status_code}"

                else:
                    logger.error(f"LLM error {response.status_code}: {response.text[:200]}")
                    last_error = f"API error {response.status_code}"
                    break

            except httpx.TimeoutException:
                logger.warning(f"LLM timeout after {self.timeout}s (attempt {attempt + 1})")
                last_error = "Timeout"
                if attempt < self.max_retries:
                    await asyncio.sleep(1)

            except httpx.RequestError as e:
                logger.error(f"LLM network error: {e}")
                last_error = f"Network error: {str(e)}"
                break

            except Exception as e:
                logger.error(f"LLM unexpected error: {e}", exc_info=True)
                last_error = str(e)
                break

        logger.warning(f"LLM all attempts failed. Last error: {last_error}. Falling back to mock data.")
        return "", True

    async def complete_json(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.5,
        max_tokens: int = 1500,
        use_cache: bool = True,
    ) -> Tuple[Optional[Dict], bool]:
        """
        Complete a prompt and parse response as JSON.
        
        Returns:
            (parsed_dict_or_None, is_fallback)
        """
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

        # Try to parse JSON from the response
        try:
            # Strip potential markdown code fences
            cleaned = text.strip()
            if cleaned.startswith("```"):
                lines = cleaned.split("\n")
                cleaned = "\n".join(lines[1:-1])
            return json.loads(cleaned), False
        except json.JSONDecodeError as e:
            logger.warning(f"LLM returned invalid JSON: {e}. Text: {text[:200]}")
            return None, True

    async def health_check(self) -> Dict[str, Any]:
        """Check LLM service availability."""
        if not self.api_key:
            return {"status": "no_key", "available": False, "message": "No API key configured"}
        
        try:
            text, is_fallback = await self.complete(
                prompt="Say 'ok' in exactly one word.",
                max_tokens=10,
                use_cache=False,
                temperature=0.0,
            )
            if not is_fallback:
                return {"status": "healthy", "available": True, "model": self.primary_model}
        except Exception as e:
            pass
        
        return {"status": "unavailable", "available": False, "model": self.primary_model}


# Singleton instance
llm_service = LLMService()
