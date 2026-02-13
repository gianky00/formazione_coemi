from unittest.mock import MagicMock, patch

from app.services import ai_extraction

# --- Bug 2, 9, 10: AI Extraction Tests ---


def test_ai_extraction_list_handling():
    """
    Bug 2: AI extraction discards data if the model returns a list, and does not warn user.
    Expectation: Process first item AND include warning in the result.
    """
    mock_response = MagicMock()
    # AI returns a JSON list with 2 items
    json_content = '[{"nome": "Item 1", "categoria": "A"}, {"nome": "Item 2", "categoria": "B"}]'
    mock_response.text = f"```json\n{json_content}\n```"

    with (
        patch("app.services.ai_extraction.get_gemini_model", return_value=MagicMock()),
        patch(
            "app.services.ai_extraction._generate_content_with_retry", return_value=mock_response
        ),
    ):
        result = ai_extraction.extract_entities_with_ai(b"fake_pdf_bytes")

        assert result["nome"] == "Item 1"
        assert "warning" in result
        assert "multiple_certificates_found" in result["warning"]


def test_ai_extraction_nested_json():
    """
    Bug 9 Fix Check: Ensure nested JSON extraction works (which greedy/non-greedy regex fails).
    """
    mock_response = MagicMock()
    # Nested JSON structure
    json_content = '{"nome": "T", "details": {"a": 1, "b": 2}}'
    mock_response.text = f"Wrapper ```json\n{json_content}\n``` garbage"

    with (
        patch("app.services.ai_extraction.get_gemini_model", return_value=MagicMock()),
        patch(
            "app.services.ai_extraction._generate_content_with_retry", return_value=mock_response
        ),
    ):
        result = ai_extraction.extract_entities_with_ai(b"fake")
        assert result["nome"] == "T"
        # If regex was broken, it might truncate at first '}'


def test_ai_dynamic_category():
    """
    Bug 10: AI extraction forces unknown categories to 'ALTRO'.
    Expectation: Should allow unknown categories.
    """
    mock_response = MagicMock()
    json_content = '{"nome": "T", "categoria": "NUOVO_CORSO"}'
    mock_response.text = f"```json\n{json_content}\n```"

    with (
        patch("app.services.ai_extraction.get_gemini_model", return_value=MagicMock()),
        patch(
            "app.services.ai_extraction._generate_content_with_retry", return_value=mock_response
        ),
    ):
        result = ai_extraction.extract_entities_with_ai(b"fake")
        assert result["categoria"] == "NUOVO_CORSO"
