import pytest
from unittest.mock import MagicMock, patch
from app.services.ai_extraction import extract_entities_with_ai
from google.api_core import exceptions

def test_ai_extraction_retry_logic(monkeypatch):
    """
    Test that the implementation retries on ResourceExhausted error
    and eventually returns a 429 status code structure.
    """
    # Mock settings
    monkeypatch.setattr('app.core.config.settings.mutable._data', {"GEMINI_API_KEY": "fake_key"})

    mock_model = MagicMock()
    # Configure the mock to raise ResourceExhausted every time
    mock_model.generate_content.side_effect = exceptions.ResourceExhausted("Quota exceeded")

    # Patch get_gemini_model to return our mock model
    with patch("app.services.ai_extraction.get_gemini_model", return_value=mock_model):
        pdf_bytes = b"fake pdf content"
        result = extract_entities_with_ai(pdf_bytes)

        # Verify that it failed and returned the correct error structure
        assert "error" in result
        assert result.get("status_code") == 429

        # Verify it called generate_content 3 times (initial + 2 retries)
        assert mock_model.generate_content.call_count == 3

def test_ai_extraction_success_after_retry(monkeypatch):
    """
    Test that the implementation succeeds if a subsequent try works.
    """
    # Mock settings
    monkeypatch.setattr('app.core.config.settings.mutable._data', {"GEMINI_API_KEY": "fake_key"})

    mock_model = MagicMock()
    success_response = MagicMock()
    success_response.text = '```json\n{"nome": "Mario", "categoria": "ATEX"}\n```'

    # Fail twice, then succeed
    mock_model.generate_content.side_effect = [
        exceptions.ResourceExhausted("Quota exceeded"),
        exceptions.ResourceExhausted("Quota exceeded"),
        success_response
    ]

    with patch("app.services.ai_extraction.get_gemini_model", return_value=mock_model):
        pdf_bytes = b"fake pdf content"
        result = extract_entities_with_ai(pdf_bytes)

        assert "error" not in result
        assert result["nome"] == "Mario"
        # Should be called 3 times
        assert mock_model.generate_content.call_count == 3
