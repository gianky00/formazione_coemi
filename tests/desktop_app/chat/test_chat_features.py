import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import pytest

# Force mock mode for these tests (must be before mock_qt import)

# Inject mocks before importing actual modules
from tests.desktop_app.mock_qt import mock_qt_modules
sys.modules.update(mock_qt_modules())

# Mark tests to run in forked subprocess for isolation
pytestmark = pytest.mark.forked

from PyQt6.QtCore import QObject
from desktop_app.chat.chat_controller import ChatController
from desktop_app.workers.chat_worker import ChatWorker
from app.core.config import settings

class TestChatFeatures(unittest.TestCase):
    def setUp(self):
        # Mock API Client
        self.mock_api_client = MagicMock()
        self.mock_api_client.user_info = {"username": "TestUser", "account_name": "Test User"}
        
        # Mock Settings
        settings.gemini_model = "gemini-test"
        settings.app_name = "TestApp"

    def test_chat_worker_run_success(self):
        worker = ChatWorker(
            api_key="test-key",
            model_name="test-model",
            user_message="Test message",
            history=[],
            api_client=self.mock_api_client,
            system_prompt="Test instruction"
        )
        
        with patch("desktop_app.workers.chat_worker.genai") as mock_genai:
            mock_response = MagicMock()
            mock_response.text = "Test response"
            mock_response.candidates = []
            mock_genai.GenerativeModel.return_value.start_chat.return_value.send_message.return_value = mock_response
            
            results = []
            worker.response_ready.connect(lambda r, h: results.append(r))
            worker.run()
            
            self.assertEqual(len(results), 1)
            self.assertIn("Test response", results[0])

    def test_chat_worker_run_error(self):
        worker = ChatWorker(
            api_key="test-key",
            model_name="test-model",
            user_message="Test message",
            history=[],
            api_client=self.mock_api_client,
            system_prompt="Test instruction"
        )
        
        with patch("desktop_app.workers.chat_worker.genai") as mock_genai:
            mock_genai.GenerativeModel.return_value.start_chat.return_value.send_message.side_effect = Exception("API Error")
            
            errors = []
            worker.error_occurred.connect(lambda e: errors.append(e))
            worker.run()
            
            self.assertEqual(len(errors), 1)
            self.assertIn("API Error", errors[0])

    def test_chat_worker_tool_employee_details(self):
        worker = ChatWorker(
            api_key="test-key",
            model_name="test-model",
            user_message="Mostrami i dettagli di Mario Rossi",
            history=[],
            api_client=self.mock_api_client,
            system_prompt=""
        )
        
        self.mock_api_client.get.return_value = [
            {"id": 1, "cognome": "Rossi", "nome": "Mario", "qualifica": "Operaio"}
        ]
        
        with patch("desktop_app.workers.chat_worker.genai") as mock_genai:
            mock_response = MagicMock()
            mock_response.text = "Dettagli di Mario Rossi"
            mock_response.candidates = []
            mock_genai.GenerativeModel.return_value.start_chat.return_value.send_message.return_value = mock_response
            
            results = []
            worker.response_ready.connect(lambda r, h: results.append(r))
            worker.run()

    def test_chat_worker_tool_expiring_certs(self):
        worker = ChatWorker(
            api_key="test-key",
            model_name="test-model",
            user_message="Quali certificati scadono entro 30 giorni?",
            history=[],
            api_client=self.mock_api_client,
            system_prompt=""
        )
        
        self.mock_api_client.get.return_value = [
            {"id": 1, "corso": "Sicurezza", "dipendente": {"cognome": "Rossi"}, "data_scadenza": "2024-02-01"}
        ]
        
        with patch("desktop_app.workers.chat_worker.genai") as mock_genai:
            mock_response = MagicMock()
            mock_response.text = "Ecco i certificati in scadenza"
            mock_response.candidates = []
            mock_genai.GenerativeModel.return_value.start_chat.return_value.send_message.return_value = mock_response
            
            results = []
            worker.response_ready.connect(lambda r, h: results.append(r))
            worker.run()

    def test_chat_worker_tool_get_stats(self):
        worker = ChatWorker(
            api_key="test-key",
            model_name="test-model",
            user_message="Mostrami le statistiche",
            history=[],
            api_client=self.mock_api_client,
            system_prompt=""
        )
        
        self.mock_api_client.get.side_effect = [
            [{"id": 1}, {"id": 2}],  # Dipendenti
            [{"id": 1}],  # Certificati
        ]
        
        with patch("desktop_app.workers.chat_worker.genai") as mock_genai:
            mock_response = MagicMock()
            mock_response.text = "Statistiche: 2 dipendenti, 1 certificato"
            mock_response.candidates = []
            mock_genai.GenerativeModel.return_value.start_chat.return_value.send_message.return_value = mock_response
            
            results = []
            worker.response_ready.connect(lambda r, h: results.append(r))
            worker.run()

    def test_controller_initialization(self):
        controller = ChatController(api_client=self.mock_api_client)
        self.assertIsNotNone(controller)
        self.assertEqual(controller.history, [])

    def test_controller_receive_message_starts_worker(self):
        controller = ChatController(api_client=self.mock_api_client)
        
        # receive_message creates and starts a ChatWorker
        with patch("desktop_app.chat.chat_controller.ChatWorker") as MockWorker:
            mock_worker_instance = MagicMock()
            MockWorker.return_value = mock_worker_instance
            controller.receive_message("Test")
            mock_worker_instance.start.assert_called_once()

    def test_controller_handles_response(self):
        controller = ChatController(api_client=self.mock_api_client)
        
        responses = []
        controller.response_ready.connect(lambda r: responses.append(r))
        
        # Use actual method name: _on_worker_finished
        controller._on_worker_finished("Test response", [])
        
        self.assertEqual(len(responses), 1)
        self.assertEqual(responses[0], "Test response")

    def test_controller_handles_error(self):
        controller = ChatController(api_client=self.mock_api_client)
        
        responses = []
        controller.response_ready.connect(lambda r: responses.append(r))
        
        # Use actual method name: _on_worker_error
        controller._on_worker_error("Test error")
        
        self.assertEqual(len(responses), 1)
        self.assertIn("errore", responses[0].lower())


if __name__ == '__main__':
    unittest.main()
