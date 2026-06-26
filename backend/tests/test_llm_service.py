"""
Unit Tests for llm_service.py Fallback and Retry Mechanics
"""
import pytest
import sys
import os
import httpx
from unittest.mock import AsyncMock, patch, MagicMock

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm_service import llm_service
from services.cache_service import cache_service


@pytest.fixture(autouse=True)
def configure_key():
    """Ensure API key is configured and max_retries is 0 for tests."""
    original_key = llm_service.api_key
    original_retries = llm_service.max_retries
    llm_service.api_key = "test-key-123"
    llm_service.max_retries = 0
    cache_service.clear_prefix("")
    yield
    llm_service.api_key = original_key
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

    text, is_fallback = await llm_service.complete(
        prompt="hello", use_cache=False
    )

    assert text == "Primary success response"
    assert is_fallback is False
    assert mock_post.call_count == 1
    # Check that it called the primary model (google/gemma-4-31b-it:free)
    called_json = mock_post.call_args[1]["json"]
    assert called_json["model"] == llm_service.primary_model


@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_llm_primary_fail_fallback_success(mock_post):
    """Primary model fails with 503, fallback model succeeds."""
    # First response is a 503 error
    mock_resp_fail = MagicMock()
    mock_resp_fail.status_code = 503
    
    # Second response is a 200 success
    mock_resp_success = MagicMock()
    mock_resp_success.status_code = 200
    mock_resp_success.json.return_value = {
        "choices": [{"message": {"content": "Fallback success response"}}]
    }

    mock_post.side_effect = [mock_resp_fail, mock_resp_success]

    text, is_fallback = await llm_service.complete(
        prompt="hello", use_cache=False
    )

    assert text == "Fallback success response"
    assert is_fallback is False
    assert mock_post.call_count == 2
    
    # First call was to primary model
    first_called_json = mock_post.call_args_list[0][1]["json"]
    assert first_called_json["model"] == llm_service.primary_model
    
    # Second call was to fallback model
    second_called_json = mock_post.call_args_list[1][1]["json"]
    assert second_called_json["model"] == llm_service.fallback_model


@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_llm_primary_timeout_fallback_success(mock_post):
    """Primary model times out, fallback model succeeds."""
    # First response raises timeout
    # Second response is a 200 success
    mock_resp_success = MagicMock()
    mock_resp_success.status_code = 200
    mock_resp_success.json.return_value = {
        "choices": [{"message": {"content": "Fallback after primary timeout"}}]
    }

    mock_post.side_effect = [httpx.TimeoutException("Timeout!"), mock_resp_success]

    text, is_fallback = await llm_service.complete(
        prompt="hello", use_cache=False
    )

    assert text == "Fallback after primary timeout"
    assert is_fallback is False
    assert mock_post.call_count == 2


@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_llm_all_fail_trigger_fallback(mock_post):
    """Primary model fails, fallback model fails, returns fallback trigger (empty string, is_fallback=True)."""
    mock_resp_fail1 = MagicMock()
    mock_resp_fail1.status_code = 503
    mock_resp_fail2 = MagicMock()
    mock_resp_fail2.status_code = 500

    mock_post.side_effect = [mock_resp_fail1, mock_resp_fail2]

    text, is_fallback = await llm_service.complete(
        prompt="hello", use_cache=False
    )

    assert text == ""
    assert is_fallback is True
    assert mock_post.call_count == 2
