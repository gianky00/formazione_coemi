import pytest
from unittest.mock import patch, MagicMock
import json
from app.services.ai_extraction import (
    extract_entities_with_ai,
    GeminiClient,
    get_gemini_model,
    AIExtractionError,
    AIInvalidJSONError,
    AIModelInitializationError,
)

@pytest.fixture
def mock_gemini_client():
    """Fixture to mock the entire GeminiClient and its model."""
    with patch('app.services.ai_extraction.GeminiClient') as MockClient:
        mock_instance = MagicMock()
        MockClient.return_value = mock_instance
        mock_model = MagicMock()
        mock_instance.get_model.return_value = mock_model
        yield mock_model

def test_extract_entities_with_ai_success(mock_gemini_client):
    """Test successful extraction."""
    mock_response = MagicMock()
    mock_response.text = '{"nome": "Mario Rossi", "corso": "ANTINCENDIO", "data_rilascio": "14-11-2025", "categoria": "ANTINCENDIO"}'
    mock_gemini_client.generate_content.return_value = mock_response

    result = extract_entities_with_ai(b"dummy pdf")
    assert result == {
        "nome": "Mario Rossi", "corso": "ANTINCENDIO",
        "data_rilascio": "14-11-2025", "categoria": "ANTINCENDIO"
    }

def test_extract_entities_with_ai_list_response(mock_gemini_client):
    """Test correct handling of a list response from the AI."""
    mock_response = MagicMock()
    mock_response.text = '[{"nome": "Giuseppe Verdi", "categoria": "PREPOSTO"}]'
    mock_gemini_client.generate_content.return_value = mock_response

    result = extract_entities_with_ai(b"dummy pdf")
    assert result["nome"] == "Giuseppe Verdi"
    assert result["categoria"] == "PREPOSTO"

def test_extract_entities_with_ai_invalid_json_raises_exception(mock_gemini_client):
    """Test that malformed JSON raises AIInvalidJSONError."""
    raw_bad_json = '{"nome": "Luigi Bianchi", "categoria": "VISITA MEDICA"' # Missing closing brace
    mock_response = MagicMock()
    mock_response.text = raw_bad_json
    mock_gemini_client.generate_content.return_value = mock_response

    with pytest.raises(AIInvalidJSONError) as excinfo:
        extract_entities_with_ai(b"dummy pdf")
    
    # Check that the raw response is attached to the exception for debugging
    assert excinfo.value.raw_response == raw_bad_json
    assert "Invalid JSON" in str(excinfo.value)

def test_extract_entities_with_ai_model_initialization_fails(mock_gemini_client):
    """Test that a failure to get the model raises AIModelInitializationError."""
    with patch('app.services.ai_extraction.get_gemini_model', return_value=None):
        with pytest.raises(AIModelInitializationError, match="Gemini model is not initialized"):
            extract_entities_with_ai(b"dummy pdf")

def test_extract_entities_with_ai_general_api_error(mock_gemini_client):
    """Test that a generic API error raises AIExtractionError."""
    mock_gemini_client.generate_content.side_effect = Exception("Internal Server Error")
    
    with pytest.raises(AIExtractionError, match="An unexpected AI call failed"):
        extract_entities_with_ai(b"dummy pdf")

def test_extract_entities_with_ai_empty_list_response_error(mock_gemini_client):
    """Test that an empty list from the AI raises AIExtractionError."""
    mock_response = MagicMock()
    mock_response.text = '[]'
    mock_gemini_client.generate_content.return_value = mock_response

    with pytest.raises(AIExtractionError, match="AI returned an empty list"):
        extract_entities_with_ai(b"dummy pdf")

def test_extract_entities_with_ai_fallback_category(mock_gemini_client):
    """Test that an invalid category from the AI is corrected to 'ALTRO'."""
    mock_response = MagicMock()
    mock_response.text = '{"nome": "Carlo Neri", "categoria": "CATEGORIA_INESISTENTE"}'
    mock_gemini_client.generate_content.return_value = mock_response

    result = extract_entities_with_ai(b"dummy pdf")
    assert result["categoria"] == "ALTRO"

def test_gemini_client_init_failure_raises_exception():
    """Test GeminiClient initialization failure (missing key) raises an exception."""
    with patch('app.services.ai_extraction.genai'), \
         patch('app.services.ai_extraction.settings') as mock_settings:

        GeminiClient._instance = None
        mock_settings.GEMINI_API_KEY = None

        with pytest.raises(ValueError, match="GEMINI_API_KEY not configured"):
            GeminiClient()

def test_get_gemini_model_handles_exception():
    """Test that get_gemini_model returns None if the client fails to initialize."""
    with patch('app.services.ai_extraction.GeminiClient', side_effect=ValueError("Init failed")):
        model = get_gemini_model()
        assert model is None
