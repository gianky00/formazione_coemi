from unittest.mock import MagicMock, patch

from app.services.ai_extraction import GeminiClient, extract_entities_with_ai


def test_gemini_client_singleton():
    GeminiClient._instance = None
    with patch("app.services.ai_extraction.genai.GenerativeModel"):
        with patch("app.services.ai_extraction.settings") as mock_settings:
            mock_settings.GEMINI_API_KEY_ANALYSIS = "fake_key"
            c1 = GeminiClient()
            c2 = GeminiClient()
            assert c1 is c2


def test_extract_entities_json_decode_error():
    # Mock text preview to pass 50 chars check
    dummy_text = "Certificato di formazione professionale valido per 5 anni. " * 2
    with (
        patch("app.utils.file_security.get_pdf_text_preview", return_value=dummy_text),
        patch("app.services.ai_extraction.GeminiClient") as mock_client_class,
        patch(
            "app.services.ai_extraction._generate_content_with_retry",
            return_value="Ecco il risultato: INVALID_JSON",
        ),
    ):
        mock_client = MagicMock()
        mock_client.model = MagicMock()
        mock_client_class.return_value = mock_client

        result = extract_entities_with_ai(b"fake pdf")
        assert "error" in result
        assert "JSON" in result["error"]


def test_extract_entities_generic_exception():
    dummy_text = "Certificato di formazione professionale valido per 5 anni. " * 2
    with (
        patch("app.utils.file_security.get_pdf_text_preview", return_value=dummy_text),
        patch("app.services.ai_extraction.GeminiClient") as mock_client_class,
        patch(
            "app.services.ai_extraction._generate_content_with_retry",
            side_effect=Exception("API Error"),
        ),
    ):
        mock_client = MagicMock()
        mock_client.model = MagicMock()
        mock_client_class.return_value = mock_client

        result = extract_entities_with_ai(b"fake pdf")
        assert "error" in result
        assert "API Error" in result["error"]
