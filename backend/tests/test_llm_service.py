"""
Unit Tests for llm_service.py Fallback and Retry Mechanics
"""
import pytest
import sys
import os
import httpx
from unittest.mock import AsyncMock, patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm_service import llm_service
from services.cache_service import cache_service


@pytest.fixture(autouse=True)
def configure_key():
    """
    Set API key and pin max_retries=0 so each model gets exactly ONE attempt.
    This makes fallback logic deterministic in tests (no retry noise).
    """
    from config import settings as s
    original_groq = s.GROQ_API_KEY
    original_or = s.OPENROUTER_API_KEY
    original_retries = llm_service.max_retries
    
    s.GROQ_API_KEY = "test-key-123"
    s.OPENROUTER_API_KEY = "test-key-123"
    llm_service.primary_model = s.GROQ_MODEL
    llm_service.fallback_model = s.GROQ_FALLBACK_MODEL
    llm_service.api_key = "test-key-123"
    llm_service.max_retries = 0
    cache_service.clear_prefix("")
    
    yield
    
    s.GROQ_API_KEY = original_groq
    s.OPENROUTER_API_KEY = original_or
    llm_service.max_retries = original_retries
    cache_service.clear_prefix("")


@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_llm_primary_success(mock_post):
    """Primary model succeeds on first attempt."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "Primary success response"}}]
    }
    mock_post.return_value = mock_resp

    text, is_fallback = await llm_service.complete(prompt="hello", use_cache=False)

    assert text == "Primary success response"
    assert is_fallback is False
    assert mock_post.call_count == 1
    called_json = mock_post.call_args[1]["json"]
    assert called_json["model"] == llm_service.primary_model


@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_llm_primary_fail_fallback_success(mock_post):
    """Primary model fails with 503, fallback model succeeds (max_retries=0 so 2 calls total)."""
    mock_resp_fail = MagicMock()
    mock_resp_fail.status_code = 503

    mock_resp_success = MagicMock()
    mock_resp_success.status_code = 200
    mock_resp_success.json.return_value = {
        "choices": [{"message": {"content": "Fallback success response"}}]
    }

    mock_post.side_effect = [mock_resp_fail, mock_resp_success]

    text, is_fallback = await llm_service.complete(prompt="hello", use_cache=False)

    assert text == "Fallback success response"
    assert is_fallback is False
    assert mock_post.call_count == 2

    first_json = mock_post.call_args_list[0][1]["json"]
    assert first_json["model"] == llm_service.primary_model

    second_json = mock_post.call_args_list[1][1]["json"]
    assert second_json["model"] in (llm_service.fallback_model, "google/gemma-4-31b-it:free")


@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_llm_primary_timeout_fallback_success(mock_post):
    """Primary model times out, fallback model succeeds."""
    mock_resp_success = MagicMock()
    mock_resp_success.status_code = 200
    mock_resp_success.json.return_value = {
        "choices": [{"message": {"content": "Fallback after primary timeout"}}]
    }

    mock_post.side_effect = [httpx.TimeoutException("Timeout!"), mock_resp_success]

    text, is_fallback = await llm_service.complete(prompt="hello", use_cache=False)

    assert text == "Fallback after primary timeout"
    assert is_fallback is False
    assert mock_post.call_count == 2


@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_llm_all_fail_trigger_fallback(mock_post):
    """Both primary and fallback fail — returns ('', is_fallback=True)."""
    mock_resp_fail1 = MagicMock()
    mock_resp_fail1.status_code = 503
    mock_resp_fail2 = MagicMock()
    mock_resp_fail2.status_code = 500

    mock_post.side_effect = [mock_resp_fail1, mock_resp_fail2]

    text, is_fallback = await llm_service.complete(prompt="hello", use_cache=False)

    assert text == ""
    assert is_fallback is True
    assert mock_post.call_count == 2
