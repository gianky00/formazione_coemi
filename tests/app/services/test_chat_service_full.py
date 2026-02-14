from unittest.mock import MagicMock, patch

from app.db.models import Dipendente, User
from app.services.chat_service import chat_service


def test_get_rag_context_simple(db_session):
    # Setup data
    emp = Dipendente(nome="Mario", cognome="Rossi", matricola="M123")
    db_session.add(emp)
    db_session.commit()

    mock_user = User(username="admin", is_admin=True)

    # Query without search
    context = chat_service.get_rag_context(db_session, mock_user)
    assert "Totale Dipendenti: 1" in context
    assert "Totale Documenti: 0" in context

    # Query with search
    context_search = chat_service.get_rag_context(db_session, mock_user, query="Chi è Mario?")
    assert "Rossi M." in context_search


def test_chat_with_intelleo_success():
    with (
        patch("app.services.chat_service.settings") as mock_settings,
        patch("app.services.chat_service.genai") as mock_genai,
    ):
        mock_settings.GEMINI_API_KEY_CHAT = "valid_key"
        mock_settings.GEMINI_API_KEY_ANALYSIS = "backup_key"

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
        mock_settings.GEMINI_API_KEY_ANALYSIS = ""

        reply = chat_service.chat_with_intelleo("Ciao", [], "Context")
        assert "Chiave API Chat non configurata" in reply


def test_chat_with_intelleo_error_handling():
    with (
        patch("app.services.chat_service.settings") as mock_settings,
        patch("app.services.chat_service.genai") as mock_genai,
    ):
        mock_settings.GEMINI_API_KEY_CHAT = "key"
        mock_genai.GenerativeModel.side_effect = Exception("Boom")

        reply = chat_service.chat_with_intelleo("Ciao", [], "Context")
        assert "Boom" in reply
