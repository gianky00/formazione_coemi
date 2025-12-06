
import sys
import unittest
from unittest.mock import MagicMock, patch

# --- MOCK QT FIRST ---
from tests.desktop_app.mock_qt import mock_qt_modules
sys.modules.update(mock_qt_modules())

from desktop_app.services.voice_service import VoiceService

class TestLyraRefactor(unittest.TestCase):

    @patch('desktop_app.services.voice_service.TTSWorker')
    @patch('desktop_app.services.voice_service.QMediaPlayer') # Mock Player to prevent segfaults/errors
    def test_voice_service_speak(self, MockPlayer, MockTTSWorker):
        """Test VoiceService speaks with correct params."""
        # We need to mock settings import inside voice_service
        with patch('desktop_app.services.voice_service.settings') as mock_settings:
            mock_settings.VOICE_ASSISTANT_ENABLED = True

            service = VoiceService()
            service.speak("Hello")

            MockTTSWorker.assert_called_with("Hello", voice="it-IT-IsabellaNeural")

    def test_voice_service_disabled(self):
        with patch('desktop_app.services.voice_service.settings') as mock_settings:
            mock_settings.VOICE_ASSISTANT_ENABLED = False

            with patch('desktop_app.services.voice_service.TTSWorker') as MockTTSWorker:
                service = VoiceService()
                service.speak("Hello")
                MockTTSWorker.assert_not_called()

if __name__ == '__main__':
    unittest.main()
