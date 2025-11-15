import pytest
import importlib

def test_extract_entities_with_ai_success(monkeypatch, mocker):
    """
    Testa l'estrazione di entità con una risposta AI simulata valida.
    """
    # Mock della configurazione e del modello
    mock_genai = importlib.import_module('google.generativeai')
    mock_model_instance = mocker.Mock()

    def mock_configure(*args, **kwargs):
        pass

    monkeypatch.setattr(mock_genai, 'configure', mock_configure)
    monkeypatch.setattr(mock_genai, 'GenerativeModel', lambda *args, **kwargs: mock_model_instance)

    # Risposta simulata
    mock_response = mocker.Mock()
    mock_response.text = '{"nome": "Mario Rossi", "corso": "ANTINCENDIO", "data_rilascio": "14-11-2025", "categoria": "ANTINCENDIO"}'

    mock_model_instance.generate_content.return_value = mock_response

    # Ricarica il modulo con i mock attivi
    from app.services import ai_extraction
    importlib.reload(ai_extraction)

    # Esegui la funzione
    pdf_bytes = b"dummy pdf content"
    result = ai_extraction.extract_entities_with_ai(pdf_bytes)

    # Verifica il risultato
    assert result == {
        "nome": "Mario Rossi",
        "corso": "ANTINCENDIO",
        "data_rilascio": "14-11-2025",
        "data_scadenza": None,
        "categoria": "ANTINCENDIO"
    }

def test_extract_entities_with_ai_fallback_category(monkeypatch, mocker):
    """
    Testa la logica di fallback della categoria quando la classificazione fallisce.
    """
    mock_genai = importlib.import_module('google.generativeai')
    mock_model_instance = mocker.Mock()

    def mock_configure(*args, **kwargs):
        pass

    monkeypatch.setattr(mock_genai, 'configure', mock_configure)
    monkeypatch.setattr(mock_genai, 'GenerativeModel', lambda *args, **kwargs: mock_model_instance)

    mock_response = mocker.Mock()
    mock_response.text = '{"nome": "Mario Rossi", "corso": "Corso Sconosciuto", "data_rilascio": "14-11-2025", "categoria": "CATEGORIA_INESISTENTE"}'

    mock_model_instance.generate_content.return_value = mock_response

    from app.services import ai_extraction
    importlib.reload(ai_extraction)

    pdf_bytes = b"dummy pdf content"
    result = ai_extraction.extract_entities_with_ai(pdf_bytes)

    assert result["categoria"] == "ALTRO"

def test_extract_entities_with_ai_incomplete_json(monkeypatch, mocker):
    """
    Testa la gestione di una risposta JSON incompleta dall'AI.
    """
    mock_genai = importlib.import_module('google.generativeai')
    mock_model_instance = mocker.Mock()

    def mock_configure(*args, **kwargs):
        pass

    monkeypatch.setattr(mock_genai, 'configure', mock_configure)
    monkeypatch.setattr(mock_genai, 'GenerativeModel', lambda *args, **kwargs: mock_model_instance)

    mock_response = mocker.Mock()
    mock_response.text = '{"nome": "Mario Rossi", "categoria": "ALTRO"}'

    mock_model_instance.generate_content.return_value = mock_response

    from app.services import ai_extraction
    importlib.reload(ai_extraction)

    pdf_bytes = b"dummy pdf content"
    result = ai_extraction.extract_entities_with_ai(pdf_bytes)

    assert result == {
        "nome": "Mario Rossi",
        "corso": None,
        "data_rilascio": None,
        "data_scadenza": None,
        "categoria": "ALTRO"
    }
