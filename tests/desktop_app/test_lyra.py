
import sys
import pytest
import unittest
from unittest.mock import MagicMock, patch

# --- MOCK QT FIRST ---
from tests.desktop_app.mock_qt import mock_qt_modules
sys.modules.update(mock_qt_modules())

class TestLyraRefactor(unittest.TestCase):

    def test_voice_service_speak(self):
        """Test VoiceService speaks with correct params."""
        # Clean import to ensure patches take effect on the correct module object
        if 'desktop_app.services.voice_service' in sys.modules:
            del sys.modules['desktop_app.services.voice_service']

        from desktop_app.services.voice_service import VoiceService, TTSWorker

        # Patch settings where VoiceService imports it
        with patch('desktop_app.services.voice_service.settings') as mock_settings:
            mock_settings.VOICE_ASSISTANT_ENABLED = True

            # Patch TTSWorker class in the module
            with patch('desktop_app.services.voice_service.TTSWorker') as MockTTSWorker:
                # Patch QMediaPlayer via mock_qt injection or direct patch
                with patch('desktop_app.services.voice_service.QMediaPlayer'):

                    mock_worker_instance = MagicMock()
                    MockTTSWorker.return_value = mock_worker_instance

                    service = VoiceService()
                    service.speak("Hello")

                    # Verify - Updated for gTTS (only text arg)
                    MockTTSWorker.assert_called_with(text="Hello")
                    mock_worker_instance.start.assert_called_once()

    def test_voice_service_disabled(self):
        # Clean import
        if 'desktop_app.services.voice_service' in sys.modules:
            del sys.modules['desktop_app.services.voice_service']

        from desktop_app.services.voice_service import VoiceService

        with patch('desktop_app.services.voice_service.settings') as mock_settings:
            mock_settings.VOICE_ASSISTANT_ENABLED = False

            with patch('desktop_app.services.voice_service.TTSWorker') as MockTTSWorker:
                service = VoiceService()
                service.speak("Hello")
                MockTTSWorker.assert_not_called()

if __name__ == '__main__':
    unittest.main()
