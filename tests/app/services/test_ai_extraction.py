import pytest
from unittest.mock import patch, MagicMock
from app.services.ai_extraction import extract_entities_with_ai

@pytest.fixture
def mock_gemini_client():
    with patch('app.services.ai_extraction.GeminiClient') as mock_client:
        mock_model = MagicMock()
        mock_client.return_value.get_model.return_value = mock_model
        yield mock_model

def test_extract_entities_with_ai_success(mock_gemini_client):
    mock_response = MagicMock()
    mock_response.text = '{"nome": "Mario Rossi", "corso": "ANTINCENDIO", "data_rilascio": "14-11-2025", "categoria": "ANTINCENDIO"}'
    mock_gemini_client.generate_content.return_value = mock_response

    result = extract_entities_with_ai(b"dummy pdf")

    assert result == {
        "nome": "Mario Rossi", "corso": "ANTINCENDIO",
        "data_rilascio": "14-11-2025", "categoria": "ANTINCENDIO"
    }

def test_extract_entities_with_ai_fallback_category(mock_gemini_client):
    mock_response = MagicMock()
    mock_response.text = '{"categoria": "INVALID"}'
    mock_gemini_client.generate_content.return_value = mock_response

    result = extract_entities_with_ai(b"dummy pdf")

    assert result["categoria"] == "ALTRO"

def test_extract_entities_with_ai_incomplete_json(mock_gemini_client):
    mock_response = MagicMock()
    mock_response.text = '{"nome": "Mario Rossi"}'
    mock_gemini_client.generate_content.return_value = mock_response

    result = extract_entities_with_ai(b"dummy pdf")

    assert result == {"nome": "Mario Rossi", "categoria": "ALTRO"}
