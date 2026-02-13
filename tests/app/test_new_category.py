from unittest.mock import MagicMock, patch

from app.db.models import Corso
from app.db.seeding import seed_database


def test_seed_database_with_nomine(db_session):
    """
    Tests that the seed_database function correctly adds the 'NOMINA' course.
    """
    seed_database(db=db_session)
    corso = db_session.query(Corso).filter(Corso.nome_corso == "NOMINA").first()
    assert corso is not None
    assert corso.categoria_corso == "NOMINA"
    assert corso.validita_mesi == 0


@patch("app.services.ai_extraction.get_gemini_model")
def test_extract_entities_with_ai_for_nomine(mock_get_model):
    """
    Tests that the AI service correctly classifies a 'NOMINA' document.
    """
    mock_model = MagicMock()
    mock_get_model.return_value = mock_model

    mock_response = MagicMock()
    mock_response.text = '{"nome": "Giliberto Salvatore", "corso": "Attribuzione e competenze del ruolo di Preposto", "data_rilascio": "01-01-2023", "categoria": "NOMINA"}'
    mock_model.generate_content.return_value = mock_response

    from app.services.ai_extraction import extract_entities_with_ai

    result = extract_entities_with_ai(b"dummy pdf")

    assert result["categoria"] == "NOMINA"
    assert result["corso"] == "Attribuzione e competenze del ruolo di Preposto"
