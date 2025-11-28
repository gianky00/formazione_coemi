import pytest
import json
from unittest.mock import MagicMock, patch
from google.api_core import exceptions
from app.services import ai_extraction

# --- Prompt Audit ---
def test_prompt_integrity():
    """
    Verifies that the AI prompt contains critical business logic anchors ("Hierarchical Logic").
    The "Brain" of the classification logic resides in the prompt, so we must ensure it's not corrupted.
    """
    prompt = ai_extraction._generate_prompt()

    # Critical Anchors
    assert "REGOLE DI CLASSIFICAZIONE ASSOLUTE" in prompt
    assert "D.M. 388" in prompt
    assert "NOMINA" in prompt
    assert "SCARTO (REJECT)" in prompt
    assert "ATEX" in prompt
    assert "COGNOME NOME" in prompt

    # Verify specific hierarchy rules
    assert "Se contiene \"IDROGENO SOLFORATO\"" in prompt
    assert "SE il documento è un programma generico" in prompt

# --- Functional Tests (Mocking AI Response) ---

def test_extraction_valid_nomina(mocker):
    """
    Simulates AI returning a valid 'NOMINA' document.
    Verifies the application correctly parses and returns the data.
    """
    # Mock the AI Model
    mock_model = MagicMock()
    mock_response = MagicMock()
    # Simulate Gemini wrapping JSON in markdown code blocks
    mock_response.text = '```json\n{"categoria": "NOMINA", "nome": "ROSSI MARIO", "data_rilascio": "01/01/2024"}\n```'
    mock_model.generate_content.return_value = mock_response

    # Patch the get_model function to return our mock
    mocker.patch("app.services.ai_extraction.get_gemini_model", return_value=mock_model)

    # Execute
    result = ai_extraction.extract_entities_with_ai(b"%PDF-fake")

    # Verify
    assert result["categoria"] == "NOMINA"
    assert result["nome"] == "ROSSI MARIO"
    assert "error" not in result

def test_extraction_reject_syllabus(mocker):
    """
    Simulates AI rejecting a document (Syllabus/Generic).
    Verifies the application correctly flags it as rejected.
    """
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = json.dumps({"status": "REJECT", "reason": "Syllabus/Generic"})
    mock_model.generate_content.return_value = mock_response

    mocker.patch("app.services.ai_extraction.get_gemini_model", return_value=mock_model)

    result = ai_extraction.extract_entities_with_ai(b"%PDF-fake")

    assert "error" in result
    assert result["is_rejected"] is True
    assert "Syllabus/Generic" in result["error"]

def test_extraction_list_response_handling(mocker):
    """
    Simulates AI returning a list of objects (occasional Gemini quirk).
    Verifies the application extracts the first item.
    """
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = json.dumps([{"categoria": "ATEX", "nome": "BIANCHI LUIGI"}])
    mock_model.generate_content.return_value = mock_response

    mocker.patch("app.services.ai_extraction.get_gemini_model", return_value=mock_model)

    result = ai_extraction.extract_entities_with_ai(b"%PDF-fake")

    assert result["categoria"] == "ATEX"
    assert result["nome"] == "BIANCHI LUIGI"

def test_extraction_invalid_category_fallback(mocker):
    """
    Simulates AI returning an unknown category.
    Verifies fallback to 'ALTRO'.
    """
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = json.dumps({"categoria": "SUPER_UNKNOWN_CERT", "nome": "VERDI ANNA"})
    mock_model.generate_content.return_value = mock_response

    mocker.patch("app.services.ai_extraction.get_gemini_model", return_value=mock_model)

    result = ai_extraction.extract_entities_with_ai(b"%PDF-fake")

    assert result["categoria"] == "ALTRO"
    assert result["nome"] == "VERDI ANNA"

def test_ai_extraction_retry_logic(mocker):
    """
    Test that the implementation retries on ResourceExhausted error
    and eventually returns a 429 status code structure.
    """
    mock_model = MagicMock()
    # Configure the mock to raise ResourceExhausted every time
    mock_model.generate_content.side_effect = exceptions.ResourceExhausted("Quota exceeded")

    # Patch get_gemini_model to return our mock model
    mocker.patch("app.services.ai_extraction.get_gemini_model", return_value=mock_model)

    pdf_bytes = b"fake pdf content"
    result = ai_extraction.extract_entities_with_ai(pdf_bytes)

    # Verify that it failed and returned the correct error structure
    assert "error" in result
    assert result.get("status_code") == 429

    # Verify it called generate_content 3 times (initial + 2 retries)
    # Note: tenacity retry behavior depends on config, assuming 3 attempts
    assert mock_model.generate_content.call_count == 3

def test_ai_extraction_success_after_retry(mocker):
    """
    Test that the implementation succeeds if a subsequent try works.
    """
    mock_model = MagicMock()
    success_response = MagicMock()
    success_response.text = '```json\n{"nome": "Mario", "categoria": "ATEX"}\n```'

    # Fail twice, then succeed
    mock_model.generate_content.side_effect = [
        exceptions.ResourceExhausted("Quota exceeded"),
        exceptions.ResourceExhausted("Quota exceeded"),
        success_response
    ]

    mocker.patch("app.services.ai_extraction.get_gemini_model", return_value=mock_model)

    pdf_bytes = b"fake pdf content"
    result = ai_extraction.extract_entities_with_ai(pdf_bytes)

    assert "error" not in result
    assert result["nome"] == "Mario"
    # Should be called 3 times
    assert mock_model.generate_content.call_count == 3
