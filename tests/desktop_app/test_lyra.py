import sys
import unittest
from unittest.mock import MagicMock, patch

# --- Setup Mocks ---
from tests.desktop_app.mock_qt import mock_modules

# Patch sys.modules to mock PyQt6
patcher = patch.dict(sys.modules, mock_modules)
patcher.start()

# Now import the modules under test
try:
    from desktop_app.chat.chat_controller import ChatController
    from desktop_app.components.floating_chat_widget import FloatingChatWidget
    from desktop_app.workers.chat_worker import ChatWorker
    from desktop_app.services.voice_service import VoiceService
except ImportError as e:
    print(f"Import Error during test setup: {e}")
    raise e

class TestLyraRefactor(unittest.TestCase):
    def setUp(self):
        self.api_client = MagicMock()
        self.api_client.user_info = {"account_name": "TestUser"}
        self.voice_service = MagicMock()

    def test_chat_controller_init(self):
        """Test ChatController initialization."""
        controller = ChatController(self.api_client)
        self.assertEqual(controller.history, [])
        self.assertIsNone(controller.chat_worker)

        # Verify prompt construction (Case insensitive for username part)
        prompt = controller.get_system_prompt()
        self.assertIn("SEI LYRA", prompt)
        self.assertIn("Testuser", prompt) # Capitalize makes it Titlecase

    @patch('desktop_app.chat.chat_controller.ChatWorker')
    def test_chat_controller_receive_message(self, MockWorker):
        """Test that receive_message creates and starts the worker."""
        controller = ChatController(self.api_client)

        # Mock settings
        with patch('desktop_app.chat.chat_controller.settings') as mock_settings:
            mock_settings.GEMINI_API_KEY_CHAT = "test_key"

            mock_worker_instance = MockWorker.return_value

            controller.receive_message("Hello")

            # Check if MockWorker called
            if MockWorker.call_count == 0:
                print("DEBUG: ChatWorker not called.")

            MockWorker.assert_called_once()
            self.assertIsNotNone(controller.chat_worker)
            mock_worker_instance.start.assert_called_once()

    def test_floating_chat_widget_init(self):
        """Test FloatingChatWidget initialization and layout."""
        widget = FloatingChatWidget(self.api_client, self.voice_service)
        self.assertIsNotNone(widget)
        # Check if FAB is present
        self.assertTrue(hasattr(widget, 'fab'))
        # Check if user_has_moved flag exists
        self.assertFalse(widget.user_has_moved)

    @patch('desktop_app.workers.chat_worker.genai')
    def test_chat_worker_run(self, mock_genai):
        """Test ChatWorker run method and signal emission."""
        worker = ChatWorker("key", "model", "msg", [], self.api_client, "sys_prompt")

        mock_model = MagicMock()
        mock_chat = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_model.start_chat.return_value = mock_chat

        mock_response = MagicMock()
        mock_response.text = "Response"
        mock_chat.send_message.return_value = mock_response
        mock_chat.history = ["hist_entry"]

        # Create a slot to capture signals
        response_slot = MagicMock()
        worker.response_ready.connect(response_slot)

        worker.run()

        # Verify configure called
        mock_genai.configure.assert_called_with(api_key="key")

        # Verify send_message called
        mock_chat.send_message.assert_called_with("msg")

        # Verify signal emitted with text and history
        response_slot.assert_called_with("Response", ["hist_entry"])

    @patch('desktop_app.services.voice_service.TTSWorker')
    def test_voice_service_speak(self, MockTTSWorker):
        """Test VoiceService speaks with correct params."""
        # We need to mock settings import inside voice_service
        with patch('desktop_app.services.voice_service.settings') as mock_settings:
            mock_settings.VOICE_ASSISTANT_ENABLED = True

            service = VoiceService()
            service.speak("Hello")

            MockTTSWorker.assert_called_with("Hello", voice="it-IT-IsabellaNeural")

if __name__ == '__main__':
    unittest.main()
