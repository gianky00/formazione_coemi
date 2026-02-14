from unittest.mock import MagicMock, patch

import pytest

from app.services.ai_extraction import extract_entities_with_ai


@pytest.fixture
def mock_pdf_text():
    return "Questo è un certificato di prova molto lungo per superare i 50 caratteri di controllo."


def test_ai_extraction_list_handling(mock_pdf_text):
    """
    Bug 2: AI extraction discards data if the model returns a list.
    Expectation: Process first item AND include warning in the result.
    """
    # AI returns a JSON list with 2 items
    json_content = '[{"nome": "Item 1", "categoria": "FORMAZIONE"}, {"nome": "Item 2", "categoria": "ADDESTRAMENTO"}]'

    with (
        patch("app.utils.file_security.get_pdf_text_preview", return_value=mock_pdf_text),
        patch("app.services.ai_extraction.GeminiClient") as mock_client_class,
        patch("app.services.ai_extraction._generate_content_with_retry", return_value=json_content),
    ):
        mock_client = MagicMock()
        mock_client.model = MagicMock()
        mock_client_class.return_value = mock_client

        result = extract_entities_with_ai(b"fake pdf")

        assert result["nome"] == "Item 1"
        assert "warnings" in result
        assert "più certificati" in result["warnings"][0]


def test_ai_extraction_nested_json(mock_pdf_text):
    """
    Bug 9 Fix Check: Ensure JSON extraction works even with surrounding text.
    """
    json_content = '{"nome": "Mario Rossi", "categoria": "FORMAZIONE"}'
    ai_response = f"Ecco il risultato: ```json\n{json_content}\n``` Spero sia utile."

    with (
        patch("app.utils.file_security.get_pdf_text_preview", return_value=mock_pdf_text),
        patch("app.services.ai_extraction.GeminiClient") as mock_client_class,
        patch("app.services.ai_extraction._generate_content_with_retry", return_value=ai_response),
    ):
        mock_client = MagicMock()
        mock_client.model = MagicMock()
        mock_client_class.return_value = mock_client

        result = extract_entities_with_ai(b"fake pdf")
        assert result["nome"] == "Mario Rossi"


def test_ai_dynamic_category(mock_pdf_text):
    """
    Bug 10: AI extraction forces unknown categories to 'ALTRO'.
    Expectation: Should allow unknown categories.
    """
    json_content = '{"nome": "Test", "categoria": "NUOVA_CATEGORIA"}'

    with (
        patch("app.utils.file_security.get_pdf_text_preview", return_value=mock_pdf_text),
        patch("app.services.ai_extraction.GeminiClient") as mock_client_class,
        patch("app.services.ai_extraction._generate_content_with_retry", return_value=json_content),
    ):
        mock_client = MagicMock()
        mock_client.model = MagicMock()
        mock_client_class.return_value = mock_client

        result = extract_entities_with_ai(b"fake pdf")
        assert result["categoria"] == "NUOVA_CATEGORIA"
