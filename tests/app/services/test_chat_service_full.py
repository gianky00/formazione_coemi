import pytest
from unittest.mock import MagicMock, patch
from datetime import date
from app.services.chat_service import chat_service
from app.db.models import User, Certificato, Dipendente, Corso

def test_get_rag_context_empty_db():
    mock_db = MagicMock()
    # Mock counts
    mock_db.query.return_value.count.return_value = 0
    # Mock queries for lists
    mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = []
    mock_db.query.return_value.filter.return_value.all.return_value = []

    mock_user = User(username="admin", account_name="Admin User")

    context = chat_service.get_rag_context(mock_db, mock_user)

    assert "Totale Dipendenti: 0" in context
    assert "Totale Documenti: 0" in context
    assert "DOCUMENTI SCADUTI (0)" in context

def test_get_rag_context_with_data():
    mock_db = MagicMock()
    mock_user = User(username="test", account_name="Tester")

    # Mock counts
    # Code calls Certificato count first, then Dipendente count
    mock_db.query.return_value.count.side_effect = [50, 10] # Certs=50, Employees=10
    # We need to simulate the objects structure
    cert_expired = MagicMock(spec=Certificato)
    cert_expired.id = 1
    cert_expired.dipendente.nome = "ROSSI MARIO"
    cert_expired.corso.nome_corso = "ANTINCENDIO"
    cert_expired.data_scadenza_calcolata = date(2020, 1, 1) # Expired
    cert_expired.dipendente_id = 1

    cert_expiring = MagicMock(spec=Certificato)
    cert_expiring.id = 2
    cert_expiring.dipendente.nome = "BIANCHI LUIGI"
    cert_expiring.corso.nome_corso = "HLO"
    cert_expiring.data_scadenza_calcolata = date(2025, 12, 31) # Expiring soon (assuming threshold)
    cert_expiring.dipendente_id = 2

    # Mock Orphans
    cert_orphan = MagicMock(spec=Certificato)
    cert_orphan.id = 3
    cert_orphan.dipendente = None
    cert_orphan.dipendente_id = None
    cert_orphan.nome_dipendente_raw = "SCONOSCIUTO"
    cert_orphan.corso.nome_corso = "ATEX"

    # Setup query returns
    # First query is for relevant_certs (expired/expiring)
    mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = [cert_expired, cert_expiring]

    # Second query is for orphans
    mock_db.query.return_value.filter.return_value.all.return_value = [cert_orphan]

    # Mock status calculation
    with patch("app.services.chat_service.get_bulk_certificate_statuses") as mock_statuses:
        mock_statuses.return_value = {
            1: "scaduto",
            2: "in_scadenza"
        }

        context = chat_service.get_rag_context(mock_db, mock_user)

    assert "Totale Dipendenti: 10" in context
    assert "Totale Documenti: 50" in context
    assert "DOCUMENTI SCADUTI (1)" in context
    assert "ROSSI MARIO" in context
    assert "DOCUMENTI IN SCADENZA (1)" in context
    assert "BIANCHI LUIGI" in context
    assert "DOCUMENTI DA VALIDARE/ORFANI (1)" in context
    assert "ATEX" in context

def test_chat_with_intelleo_success():
    with patch("app.services.chat_service.settings") as mock_settings, \
         patch("app.services.chat_service.genai") as mock_genai:

        mock_settings.GEMINI_API_KEY_CHAT = "valid_key"

        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_chat = MagicMock()
        mock_model.start_chat.return_value = mock_chat
        mock_chat.send_message.return_value.text = "Risposta AI"

        reply = chat_service.chat_with_intelleo("Ciao", [], "Context")

        assert reply == "Risposta AI"
        mock_genai.configure.assert_called_with(api_key="valid_key")

def test_chat_with_intelleo_missing_key():
    with patch("app.services.chat_service.settings") as mock_settings:
        mock_settings.GEMINI_API_KEY_CHAT = ""

        reply = chat_service.chat_with_intelleo("Ciao", [], "Context")
        assert "Errore: Chiave API Chat non configurata" in reply

def test_chat_with_intelleo_init_error():
    with patch("app.services.chat_service.settings") as mock_settings, \
         patch("app.services.chat_service.genai") as mock_genai:

        mock_settings.GEMINI_API_KEY_CHAT = "valid_key"
        mock_genai.GenerativeModel.side_effect = Exception("Init Fail")

        reply = chat_service.chat_with_intelleo("Ciao", [], "Context")
        assert "Errore inizializzazione AI: Init Fail" in reply

def test_chat_with_intelleo_runtime_error():
    with patch("app.services.chat_service.settings") as mock_settings, \
         patch("app.services.chat_service.genai") as mock_genai:

        mock_settings.GEMINI_API_KEY_CHAT = "valid_key"

        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_chat = MagicMock()
        mock_model.start_chat.return_value = mock_chat
        mock_chat.send_message.side_effect = Exception("Runtime Fail")

        reply = chat_service.chat_with_intelleo("Ciao", [], "Context")
        assert "Errore durante la generazione della risposta: Runtime Fail" in reply
