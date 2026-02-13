from unittest.mock import MagicMock, patch

import pytest

from app.services import ai_extraction


def test_gemini_client_singleton():
    # Reset singleton
    ai_extraction.GeminiClient._instance = None

    with (
        patch("google.generativeai.configure") as mock_conf,
        patch("google.generativeai.GenerativeModel") as mock_model,
    ):
        client1 = ai_extraction.GeminiClient()
        client2 = ai_extraction.GeminiClient()

        assert client1 is client2
        mock_conf.assert_called_once()
        mock_model.assert_called_once()


def test_gemini_client_missing_key():
    ai_extraction.GeminiClient._instance = None

    # Mock settings to return empty key
    # We need to patch the settings object that GeminiClient imports
    with patch("app.services.ai_extraction.settings") as mock_settings:
        mock_settings.GEMINI_API_KEY_ANALYSIS = None

        with pytest.raises(ValueError, match="GEMINI_API_KEY_ANALYSIS not configured"):
            ai_extraction.GeminiClient()


def test_extract_entities_json_decode_error(mocker):
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Not JSON"
    mock_model.generate_content.return_value = mock_response

    mocker.patch("app.services.ai_extraction.get_gemini_model", return_value=mock_model)

    result = ai_extraction.extract_entities_with_ai(b"pdf")
    assert "error" in result
    assert "Invalid JSON" in result["error"]


def test_extract_entities_generic_exception(mocker):
    mock_model = MagicMock()
    mock_model.generate_content.side_effect = Exception("Boom")

    mocker.patch("app.services.ai_extraction.get_gemini_model", return_value=mock_model)

    result = ai_extraction.extract_entities_with_ai(b"pdf")
    assert "error" in result
    assert "AI call failed" in result["error"]
