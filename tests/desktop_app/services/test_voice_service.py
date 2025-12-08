import pytest
import os
import sys
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock, ANY

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# Mock PyQt classes before importing the service
from tests.desktop_app.mock_qt import QtCore, mock_modules

# Patch QMediaPlayer and QAudioOutput in the service module
with patch.dict(sys.modules, {
    'PyQt6.QtMultimedia': mock_modules['PyQt6.QtMultimedia'],
    'PyQt6.QtCore': QtCore
}):
    from desktop_app.services import voice_service # Import module
    from desktop_app.services.voice_service import VoiceService, TTSWorker

# Helper to mock ElevenLabs client
@patch('desktop_app.services.voice_service.TTSWorker.run') # We can patch run or the internal logic. Patching run is easiest to avoid importing elevenlabs in test if not installed.
def test_tts_worker_logic(mock_run):
    # Actually, we want to test the logic INSIDE run.
    # So we need to patch elevenlabs.ElevenLabs
    pass

def test_voice_service_speak():
    """
    Test that speak() instantiates a worker and starts it.
    """
    service = VoiceService()
    service._player = MagicMock() 
    
    # Use patch.object on the imported module to ensure we hit the right reference
    with patch.object(voice_service, 'TTSWorker') as MockWorkerClass:
        with patch.object(voice_service, 'settings') as mock_settings:
            mock_settings.VOICE_ASSISTANT_ENABLED = True
            mock_settings.ELEVENLABS_VOICE_ID = "v_id"
            mock_settings.ELEVENLABS_MODEL_ID = "m_id"
            mock_settings.ELEVENLABS_API_KEY = "k_id"
            
            # Return a mock instance that behaves like a thread
            mock_worker_instance = MagicMock()
            MockWorkerClass.return_value = mock_worker_instance
            
            # Case 1: Enabled
            service.speak("Test")
            
            # Assert called with correct args
            MockWorkerClass.assert_called_with(
                text="Test",
                voice_id="v_id",
                model_id="m_id",
                api_key="k_id"
            )
            mock_worker_instance.start.assert_called_once()

            # Case 2: Disabled via Settings
            MockWorkerClass.reset_mock()
            mock_settings.VOICE_ASSISTANT_ENABLED = False
            service.speak("Test")
            MockWorkerClass.assert_not_called()

            # Case 3: Muted
            MockWorkerClass.reset_mock()
            mock_settings.VOICE_ASSISTANT_ENABLED = True
            service.toggle_mute() # Now muted
            service.speak("Test")
            MockWorkerClass.assert_not_called()

def test_voice_service_mute_toggle():
    # Need to patch settings for init
    with patch.object(voice_service, 'settings') as mock_settings:
        mock_settings.VOICE_ASSISTANT_ENABLED = True
        service = VoiceService()
        assert service.is_muted == False
        
        state = service.toggle_mute()
        assert state == True
        assert service.is_muted == True
        
        state = service.toggle_mute()
        assert state == False
        assert service.is_muted == False

@patch.dict(sys.modules, {'elevenlabs': MagicMock()})
def test_tts_worker_run():
    """
    Test the TTSWorker run method mocking ElevenLabs.
    """
    # We need to re-import or use the class from the module where we patched sys.modules
    # But since we already imported TTSWorker, the patch dict might not affect it if the import happened before.
    # However, the code does `from elevenlabs import ElevenLabs` INSIDE run().
    # So patching sys.modules should work if we ensure it's in place when run() is called.

    worker = TTSWorker("text", "vid", "mid", "key")

    # Mock the ElevenLabs module
    mock_elevenlabs_module = MagicMock()
    mock_client_class = MagicMock()
    mock_client_instance = MagicMock()
    mock_elevenlabs_module.ElevenLabs = mock_client_class
    mock_client_class.return_value = mock_client_instance

    # Mock generate to return an iterator of bytes
    mock_client_instance.generate.return_value = [b"chunk1", b"chunk2"]

    with patch.dict(sys.modules, {'elevenlabs': mock_elevenlabs_module}):
        with patch('desktop_app.services.voice_service.tempfile.mkstemp', return_value=(1, "/tmp/test_el.mp3")):
            with patch('desktop_app.services.voice_service.os.close'):
                with patch('builtins.open', new_callable=MagicMock) as mock_open:
                    # Mock file handle
                    mock_file_handle = MagicMock()
                    mock_open.return_value.__enter__.return_value = mock_file_handle

                    worker.run()

                    # Verify ElevenLabs init
                    mock_client_class.assert_called_with(api_key="key")

                    # Verify generate call
                    mock_client_instance.generate.assert_called_with(
                        text="text",
                        voice="vid",
                        model="mid"
                    )

                    # Verify file write
                    assert mock_file_handle.write.call_count == 2
                    mock_file_handle.write.assert_any_call(b"chunk1")
                    mock_file_handle.write.assert_any_call(b"chunk2")
