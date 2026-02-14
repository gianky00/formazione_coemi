import json
from unittest.mock import MagicMock, patch

import pytest

from app.services.ai_extraction import GeminiClient, extract_entities_with_ai


@pytest.fixture
def mock_pdf_text():
    return "Contenuto del certificato di formazione professionale molto lungo e dettagliato per superare i test di validità."


def test_gemini_client_singleton():
    GeminiClient._instance = None
    with patch("app.services.ai_extraction.genai.GenerativeModel"):
        with patch("app.services.ai_extraction.settings") as mock_settings:
            mock_settings.GEMINI_API_KEY_ANALYSIS = "key"
            c1 = GeminiClient()
            c2 = GeminiClient()
            assert c1 is c2


def test_extract_entities_valid_json(mock_pdf_text):
    expected_data = {
        "nome": "ROSSI MARIO",
        "categoria": "ANTINCENDIO",
        "data_scadenza": "31/12/2025",
    }
    ai_response = json.dumps(expected_data)

    with (
        patch("app.utils.file_security.get_pdf_text_preview", return_value=mock_pdf_text),
        patch("app.services.ai_extraction.GeminiClient") as mock_client_class,
        patch("app.services.ai_extraction._generate_content_with_retry", return_value=ai_response),
    ):
        mock_client = MagicMock()
        mock_client.model = MagicMock()
        mock_client_class.return_value = mock_client

        result = extract_entities_with_ai(b"fake pdf")
        assert result["nome"] == "ROSSI MARIO"
        assert result["categoria"] == "ANTINCENDIO"


def test_extract_entities_list_response(mock_pdf_text):
    expected_data = {"nome": "BIANCHI LUIGI", "categoria": "FORMAZIONE"}
    ai_response = json.dumps([expected_data, {"nome": "OTHER"}])

    with (
        patch("app.utils.file_security.get_pdf_text_preview", return_value=mock_pdf_text),
        patch("app.services.ai_extraction.GeminiClient") as mock_client_class,
        patch("app.services.ai_extraction._generate_content_with_retry", return_value=ai_response),
    ):
        mock_client = MagicMock()
        mock_client.model = MagicMock()
        mock_client_class.return_value = mock_client

        result = extract_entities_with_ai(b"fake pdf")
        assert result["nome"] == "BIANCHI LUIGI"
        assert "warnings" in result


def test_extract_entities_invalid_json(mock_pdf_text):
    ai_response = "Not a JSON"

    with (
        patch("app.utils.file_security.get_pdf_text_preview", return_value=mock_pdf_text),
        patch("app.services.ai_extraction.GeminiClient") as mock_client_class,
        patch("app.services.ai_extraction._generate_content_with_retry", return_value=ai_response),
    ):
        mock_client = MagicMock()
        mock_client.model = MagicMock()
        mock_client_class.return_value = mock_client

        result = extract_entities_with_ai(b"fake pdf")
        assert "error" in result


def test_extract_entities_empty_pdf():
    with patch("app.utils.file_security.get_pdf_text_preview", return_value=""):
        result = extract_entities_with_ai(b"empty")
        assert "error" in result
        assert "vuoto" in result["error"]


def test_model_not_initialized():
    GeminiClient._instance = None
    with patch("app.services.ai_extraction.GeminiClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client.model = None
        mock_client_class.return_value = mock_client
        result = extract_entities_with_ai(b"fake")
        assert "error" in result
        assert "not configured" in result["error"]
