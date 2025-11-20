import pytest
from unittest.mock import patch, MagicMock
import json
from app.services.ai_extraction import extract_entities_with_ai, GeminiClient, get_gemini_model

@pytest.fixture
def mock_gemini_client():
    # We mock the entire GeminiClient class to control its behavior
    with patch('app.services.ai_extraction.GeminiClient') as MockClient:
        mock_instance = MagicMock()
        MockClient.return_value = mock_instance # Singleton instance
        mock_model = MagicMock()
        mock_instance.get_model.return_value = mock_model
        yield mock_model

def test_gemini_client_singleton():
    """Test that GeminiClient behaves as a singleton."""
    # We need to unpatch implicit mocks for this specific test to test the actual class logic
    # But since we can't easily unpatch in the middle of a test session if patching is done via decorator or fixture on the module,
    # we will test the logic by mocking the underlying 'genai' and 'settings'.

    with patch('app.services.ai_extraction.genai') as mock_genai, \
         patch('app.services.ai_extraction.settings') as mock_settings:

        # Reset singleton
        GeminiClient._instance = None
        mock_settings.GEMINI_API_KEY = "fake_key"

        client1 = GeminiClient()
        client2 = GeminiClient()

        assert client1 is client2
        mock_genai.configure.assert_called_once_with(api_key="fake_key")

def test_gemini_client_init_failure():
    """Test GeminiClient initialization failure (missing key)."""
    with patch('app.services.ai_extraction.genai'), \
         patch('app.services.ai_extraction.settings') as mock_settings:

        GeminiClient._instance = None
        mock_settings.GEMINI_API_KEY = None

        with pytest.raises(ValueError, match="GEMINI_API_KEY not configured"):
            GeminiClient()

def test_get_gemini_model_error():
    with patch('app.services.ai_extraction.GeminiClient', side_effect=ValueError("Init failed")):
        assert get_gemini_model() is None

def test_extract_entities_with_ai_success(mock_gemini_client):
    mock_response = MagicMock()
    mock_response.text = '{"nome": "Mario Rossi", "corso": "ANTINCENDIO", "data_rilascio": "14-11-2025", "categoria": "ANTINCENDIO"}'
    mock_gemini_client.generate_content.return_value = mock_response

    result = extract_entities_with_ai(b"dummy pdf")

    assert result == {
        "nome": "Mario Rossi", "corso": "ANTINCENDIO",
        "data_rilascio": "14-11-2025", "categoria": "ANTINCENDIO"
    }

def test_extract_entities_with_ai_list_response(mock_gemini_client):
    """Test when AI returns a list of objects."""
    mock_response = MagicMock()
    mock_response.text = '[{"nome": "Mario Rossi", "categoria": "ANTINCENDIO"}]'
    mock_gemini_client.generate_content.return_value = mock_response

    result = extract_entities_with_ai(b"dummy pdf")
    assert result["nome"] == "Mario Rossi"

def test_extract_entities_with_ai_empty_list_response(mock_gemini_client):
    """Test when AI returns an empty list."""
    mock_response = MagicMock()
    mock_response.text = '[]'
    mock_gemini_client.generate_content.return_value = mock_response

    result = extract_entities_with_ai(b"dummy pdf")
    assert "error" in result

def test_extract_entities_with_ai_fallback_category(mock_gemini_client):
    mock_response = MagicMock()
    mock_response.text = '{"categoria": "INVALID"}'
    mock_gemini_client.generate_content.return_value = mock_response

    result = extract_entities_with_ai(b"dummy pdf")

    assert result["categoria"] == "ALTRO"

def test_extract_entities_with_ai_json_error(mock_gemini_client):
    mock_response = MagicMock()
    mock_response.text = 'INVALID JSON'
    mock_gemini_client.generate_content.return_value = mock_response

    result = extract_entities_with_ai(b"dummy pdf")
    assert "error" in result
    assert "Invalid JSON" in result["error"]

def test_extract_entities_with_ai_model_none():
    with patch('app.services.ai_extraction.get_gemini_model', return_value=None):
        result = extract_entities_with_ai(b"pdf")
        assert result == {"error": "Modello Gemini non inizializzato."}

def test_extract_entities_with_ai_general_exception(mock_gemini_client):
    mock_gemini_client.generate_content.side_effect = Exception("API Error")
    result = extract_entities_with_ai(b"pdf")
    assert "error" in result
    assert "AI call failed" in result["error"]
