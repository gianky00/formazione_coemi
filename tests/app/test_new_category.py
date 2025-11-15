import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.db.models import Corso
from app.db.session import SessionLocal

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_seed_database_with_nomine(client):
    db = SessionLocal()
    try:
        corso = db.query(Corso).filter(Corso.nome_corso == "NOMINE").first()
        assert corso is not None
        assert corso.categoria_corso == "NOMINE"
        assert corso.validita_mesi == 0
    finally:
        db.close()

@patch('app.services.ai_extraction.model')
def test_extract_entities_with_ai_for_nomine(mock_model):
    # Mock the single AI call to simulate the problematic case
    mock_response = MagicMock()
    mock_response.text = '{"nome": "Giliberto Salvatore", "corso": "Attribuzione e competenze del ruolo di Preposto", "data_rilascio": "01-01-2023", "categoria": "NOMINE"}'

    mock_model.generate_content.return_value = mock_response

    # Dummy PDF bytes
    pdf_bytes = b'%PDF-1.4... a dummy pdf ...'

    from app.services.ai_extraction import extract_entities_with_ai
    result = extract_entities_with_ai(pdf_bytes)

    # Assert that the category is correctly identified as "NOMINE" and not "PREPOSTO"
    assert result['categoria'] == 'NOMINE'
    assert result['corso'] == 'Attribuzione e competenze del ruolo di Preposto'
    assert 'error' not in result
