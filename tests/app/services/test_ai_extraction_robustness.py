import json
from unittest.mock import MagicMock, patch

import pytest
from google.api_core import exceptions

from app.services.ai_extraction import GeminiClient, extract_entities_with_ai

# --- Fixtures for Mocking ---


@pytest.fixture
def mock_settings(monkeypatch):
    """Mocks the settings object in the module."""
    mock_settings_obj = MagicMock()
    # We need to mock the property access.
    # Since we are replacing the instance, we can just set the attribute if it's not a class property on the mock.
    # MagicMock attributes are mocks by default. We can set a return value for them.
    # However, if the code accesses it as a property, we might need PropertyMock if we want to change it dynamically
    # or if we are patching the class.
    # Here we are patching the instance 'settings' in the module.

    # Simple attribute setting is enough for an instance mock
    mock_settings_obj.GEMINI_API_KEY_ANALYSIS = "fake_key"

    monkeypatch.setattr("app.services.ai_extraction.settings", mock_settings_obj)
    return mock_settings_obj


@pytest.fixture
def mock_genai(monkeypatch):
    """Mocks the google.generativeai module."""
    mock_genai_mod = MagicMock()
    monkeypatch.setattr("app.services.ai_extraction.genai", mock_genai_mod)
    return mock_genai_mod


@pytest.fixture
def reset_singleton():
    """Resets the GeminiClient singleton before and after each test."""
    GeminiClient._instance = None
    GeminiClient._model = None
    yield
    GeminiClient._instance = None
    GeminiClient._model = None


# --- Tests for Singleton Initialization ---


def test_gemini_client_initialization_success(mock_settings, mock_genai, reset_singleton):
    """Test successful initialization of the GeminiClient singleton."""
    client = GeminiClient()
    assert client is not None
    assert client.get_model() is not None
    mock_genai.configure.assert_called_with(api_key="fake_key")
    mock_genai.GenerativeModel.assert_called_with("models/gemini-2.5-pro")


def test_gemini_client_initialization_failure_no_key(mock_settings, mock_genai, reset_singleton):
    """Test initialization failure when API key is missing in settings."""
    # Set the key to empty string
    mock_settings.GEMINI_API_KEY_ANALYSIS = ""

    with pytest.raises(ValueError, match="GEMINI_API_KEY_ANALYSIS not configured"):
        GeminiClient()

    assert GeminiClient._instance is None


def test_gemini_client_initialization_generic_exception(mock_settings, mock_genai, reset_singleton):
    """Test initialization failure when genai raises an exception."""
    mock_genai.configure.side_effect = Exception("Google API Error")

    with pytest.raises(Exception, match="Google API Error"):
        GeminiClient()

    assert GeminiClient._instance is None


# --- Tests for Extraction Logic ---


@pytest.fixture
def mock_model(mock_settings, mock_genai, reset_singleton):
    """Initializes the client and returns the mocked model."""
    client = GeminiClient()
    mock_model_instance = mock_genai.GenerativeModel.return_value
    return mock_model_instance


def test_extract_entities_valid_json(mock_model):
    """Test extraction with a valid JSON response from AI."""
    mock_response = MagicMock()
    expected_data = {
        "nome": "ROSSI MARIO",
        "categoria": "ANTINCENDIO",
        "data_scadenza": "31-12-2025",
    }
    mock_response.text = f"```json\n{json.dumps(expected_data)}\n```"
    mock_model.generate_content.return_value = mock_response

    result = extract_entities_with_ai(b"fake_pdf_bytes")

    assert result == expected_data
    assert result["categoria"] == "ANTINCENDIO"
    mock_model.generate_content.assert_called_once()


def test_extract_entities_list_response(mock_model):
    """Test extraction when AI returns a list of objects (taking the first one)."""
    mock_response = MagicMock()
    expected_data = {"nome": "BIANCHI LUIGI", "categoria": "PRIMO SOCCORSO"}
    mock_response.text = json.dumps([expected_data])
    mock_model.generate_content.return_value = mock_response

    result = extract_entities_with_ai(b"fake_pdf_bytes")
    assert result == expected_data


def test_extract_entities_empty_list_response(mock_model):
    """Test extraction when AI returns an empty list."""
    mock_response = MagicMock()
    mock_response.text = "[]"
    mock_model.generate_content.return_value = mock_response

    result = extract_entities_with_ai(b"fake_pdf_bytes")
    assert "error" in result
    assert "AI returned an empty list" in result["error"]


def test_extract_entities_reject_status(mock_model):
    """Test handling of REJECT status from AI."""
    mock_response = MagicMock()
    mock_response.text = json.dumps({"status": "REJECT", "reason": "Syllabus only"})
    mock_model.generate_content.return_value = mock_response

    result = extract_entities_with_ai(b"fake_pdf_bytes")
    assert result.get("is_rejected") is True
    assert "REJECTED: Syllabus only" in result.get("error")


def test_extract_entities_invalid_json(mock_model):
    """Test handling of invalid JSON response."""
    mock_response = MagicMock()
    mock_response.text = "Not a JSON string"
    mock_model.generate_content.return_value = mock_response

    result = extract_entities_with_ai(b"fake_pdf_bytes")
    assert "error" in result
    assert "Invalid JSON" in result["error"]


def test_extract_entities_unknown_category_fallback(mock_model):
    """Test that unknown categories fall back to ALTRO."""
    mock_response = MagicMock()
    mock_response.text = json.dumps({"nome": "VERDI ANNA", "categoria": "UNKNOWN_CAT"})
    mock_model.generate_content.return_value = mock_response

    result = extract_entities_with_ai(b"fake_pdf_bytes")
    # Bug 10 Fix: Dynamic categories are now allowed, so "UNKNOWN_CAT" is preserved instead of coerced to "ALTRO"
    assert result["categoria"] == "UNKNOWN_CAT"


def test_extract_entities_atex_category(mock_model):
    """Test that ATEX is recognized as a valid category."""
    mock_response = MagicMock()
    mock_response.text = json.dumps({"nome": "NERI PAOLO", "categoria": "ATEX"})
    mock_model.generate_content.return_value = mock_response

    result = extract_entities_with_ai(b"fake_pdf_bytes")
    assert result["categoria"] == "ATEX"


# --- Tests for Retry Logic and Exceptions ---


def test_extract_entities_resource_exhausted_retry(mock_model):
    """
    Test that ResourceExhausted triggers retries and eventually fails.
    """
    # Simulate persistent failure
    mock_model.generate_content.side_effect = exceptions.ResourceExhausted("Quota exceeded")

    # We patch tenacity's sleep to avoid waiting during tests
    with patch(
        "app.services.ai_extraction.wait_exponential", return_value=lambda *args, **kwargs: 0
    ):
        result = extract_entities_with_ai(b"fake_pdf_bytes")

    assert "error" in result
    assert "status_code" in result
    assert result["status_code"] == 429
    # Bug 10 Fix: Retry policy increased to 6 attempts
    assert mock_model.generate_content.call_count == 6


def test_extract_entities_generic_exception(mock_model):
    """Test handling of generic exceptions during API call."""
    mock_model.generate_content.side_effect = Exception("Unexpected network error")

    result = extract_entities_with_ai(b"fake_pdf_bytes")
    assert "error" in result
    assert "AI call failed: Unexpected network error" in result["error"]


def test_model_not_initialized(mock_settings, reset_singleton):
    """Test extraction when model is not initialized."""
    # Simulate get_gemini_model returning None by patching it
    with patch("app.services.ai_extraction.get_gemini_model", return_value=None):
        result = extract_entities_with_ai(b"fake_pdf_bytes")
        assert result == {"error": "Modello Gemini non inizializzato."}
