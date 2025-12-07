import sys
import unittest
from unittest.mock import MagicMock, patch

# Inject mocks before importing actual modules
from tests.desktop_app.mock_qt import mock_qt_modules
sys.modules.update(mock_qt_modules())

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
        self.settings_patcher = patch('desktop_app.chat.chat_controller.settings')
        self.mock_settings = self.settings_patcher.start()
        self.mock_settings.GEMINI_API_KEY_CHAT = "fake_key"
        self.mock_settings.VOICE_ASSISTANT_ENABLED = True
        
        # Mock Google Generative AI
        self.genai_patcher = patch('desktop_app.workers.chat_worker.genai')
        self.mock_genai = self.genai_patcher.start()

        # Mock Phonetic Normalizer
        self.phonetic_patcher = patch('desktop_app.chat.chat_controller.PhoneticNormalizer')
        self.mock_phonetic = self.phonetic_patcher.start()
        self.mock_phonetic.normalize.side_effect = lambda x: x # Identity function

    def tearDown(self):
        self.settings_patcher.stop()
        self.genai_patcher.stop()
        self.phonetic_patcher.stop()

    def test_controller_initialization(self):
        controller = ChatController(self.mock_api_client)
        self.assertIsNotNone(controller)
        self.assertEqual(controller._get_user_first_name(), "Test")

    def test_controller_receive_message_starts_worker(self):
        controller = ChatController(self.mock_api_client)
        
        # Mock the worker class to verify instantiation
        with patch('desktop_app.chat.chat_controller.ChatWorker') as MockWorker:
            mock_worker_instance = MockWorker.return_value
            mock_worker_instance.response_ready = MagicMock() # Mock signals
            mock_worker_instance.error_occurred = MagicMock()
            mock_worker_instance.finished = MagicMock()

            controller.receive_message("Hello")

            MockWorker.assert_called_once()
            mock_worker_instance.start.assert_called_once()
            
            # Verify signals connected
            mock_worker_instance.response_ready.connect.assert_called()
            mock_worker_instance.error_occurred.connect.assert_called()

    def test_controller_handles_response(self):
        controller = ChatController(self.mock_api_client)
        
        # Spy on controller signals
        response_slot = MagicMock()
        speech_slot = MagicMock()
        controller.response_ready.connect(response_slot)
        controller.speech_ready.connect(speech_slot)

        # Simulate worker finished
        fake_response = "Ciao! |||SPEECH||| Ciao!"
        fake_history = [{"role": "user", "parts": ["Hello"]}, {"role": "model", "parts": ["Ciao!"]}]
        
        controller._on_worker_finished(fake_response, fake_history)

        response_slot.assert_called_with("Ciao!")
        speech_slot.assert_called_with("Ciao!")
        self.assertEqual(controller.history, fake_history)

    def test_controller_handles_error(self):
        controller = ChatController(self.mock_api_client)
        response_slot = MagicMock()
        controller.response_ready.connect(response_slot)

        controller._on_worker_error("Network Error")
        
        response_slot.assert_called_with("Errore: Network Error")

    def test_chat_worker_run_success(self):
        worker = ChatWorker("api_key", "model", "Hello", [], self.mock_api_client, "system_prompt")
        
        # Mock GenerativeModel and ChatSession
        mock_model = self.mock_genai.GenerativeModel.return_value
        mock_chat = mock_model.start_chat.return_value
        mock_response = MagicMock()
        mock_response.text = "Response Text"
        mock_chat.send_message.return_value = mock_response
        mock_chat.history = ["history"]

        # Spy signals
        response_signal_slot = MagicMock()
        worker.response_ready.connect(response_signal_slot)

        worker.run()

        self.mock_genai.configure.assert_called_with(api_key="api_key")
        mock_chat.send_message.assert_called_with("Hello")
        response_signal_slot.assert_called_with("Response Text", ["history"])

    def test_chat_worker_run_error(self):
        worker = ChatWorker("api_key", "model", "Hello", [], self.mock_api_client, "system_prompt")
        
        # Simulate Exception
        self.mock_genai.configure.side_effect = Exception("API key is invalid")
        
        error_signal_slot = MagicMock()
        worker.error_occurred.connect(error_signal_slot)

        worker.run()

        error_signal_slot.assert_called()
        args = error_signal_slot.call_args[0][0]
        # Check that logic mapped "API key" to user friendly message
        self.assertIn("Chiave API non valida", args)

    def test_chat_worker_tool_get_stats(self):
        worker = ChatWorker("k", "m", "u", [], self.mock_api_client, "p")
        
        self.mock_api_client.get_dipendenti_list.return_value = [{"id": 1}]
        self.mock_api_client.get.return_value = [{"id": 101}, {"id": 102}]

        stats = worker.get_employee_stats()
        
        self.assertEqual(stats["total_employees"], 1)
        self.assertEqual(stats["total_certificates"], 2)

    def test_chat_worker_tool_expiring_certs(self):
        worker = ChatWorker("k", "m", "u", [], self.mock_api_client, "p")
        
        # Mock API return
        fake_certs = [
            {"nome": "Mario", "nome_corso": "HLO", "data_scadenza": "01/01/2020", "stato_certificato": "scaduto"}, # Expired
            {"nome": "Luigi", "nome_corso": "ANTINCENDIO", "data_scadenza": "01/01/2099", "stato_certificato": "attivo"} # Valid
        ]
        self.mock_api_client.get.return_value = fake_certs

        # We are testing logic relative to 'today', so expired should appear
        results = worker.get_expiring_certificates(days_limit=30)
        
        self.assertEqual(len(results), 1)
        self.assertIn("Mario", results[0])
        self.assertIn("⚠️", results[0])

    def test_chat_worker_tool_employee_details(self):
        worker = ChatWorker("k", "m", "u", [], self.mock_api_client, "p")
        
        self.mock_api_client.get_dipendenti_list.return_value = [
            {"id": 1, "nome": "Mario", "cognome": "Rossi"}
        ]
        self.mock_api_client.get_dipendente_detail.return_value = {
            "nome": "Mario", "cognome": "Rossi", "matricola": "123", "certificati": []
        }

        # Match
        details = worker.get_employee_details("Mario")
        self.assertIsInstance(details, dict)
        self.assertEqual(details["matricola"], "123")

        # No Match
        details_none = worker.get_employee_details("Luigi")
        self.assertIsInstance(details_none, str)
        self.assertIn("Nessun dipendente trovato", details_none)

if __name__ == '__main__':
    unittest.main()
