from unittest.mock import MagicMock, patch

from app.db.models import Corso
from app.db.seeding import seed_database
from app.services.ai_extraction import extract_entities_with_ai


def test_seed_database_with_nomine(db_session):
    """
    Tests that the seed_database function correctly adds the 'NOMINA' course.
    """
    seed_database(db=db_session)
    corso = db_session.query(Corso).filter(Corso.nome_corso == "NOMINA").first()
    assert corso is not None
    assert corso.categoria_corso == "NOMINA"


def test_extract_entities_with_ai_for_nomine():
    """
    Tests that extract_entities_with_ai correctly identifies the 'NOMINA' category.
    """
    # Mock content preview (must be > 50 chars)
    dummy_text = "Questo è un documento di nomina ufficiale per la sicurezza sul lavoro. " * 5
    with patch("app.utils.file_security.get_pdf_text_preview", return_value=dummy_text):
        # Mock the singleton instance return
        with patch("app.services.ai_extraction.GeminiClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.model = MagicMock()  # Ensure not None
            mock_client_class.return_value = mock_client

            # Mock the retry function that calls the model
            with patch("app.services.ai_extraction._generate_content_with_retry") as mock_gen:
                mock_gen.return_value = '{"nome": "Mario Rossi", "corso": "NOMINA", "categoria": "NOMINA", "data_rilascio": "01/01/2024"}'

                result = extract_entities_with_ai(b"fake pdf")

                assert "error" not in result, (
                    f"AI Extraction failed with error: {result.get('error')}"
                )
                assert result["categoria"] == "NOMINA"
                assert result["nome"] == "Mario Rossi"
