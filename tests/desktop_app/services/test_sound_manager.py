import unittest
from unittest.mock import MagicMock, patch, ANY
import os
import tempfile
import shutil

# Mock PyQt modules BEFORE importing the service
import sys
from tests.desktop_app.mock_qt import DummyQObject, DummySignal

# Create mocks for QSoundEffect, QMediaPlayer, QAudioOutput
# Must use MagicMock() to create an INSTANCE that acts as the class/module part
mock_qt_multimedia = MagicMock()
mock_qt_multimedia.QSoundEffect = MagicMock() 
mock_qt_multimedia.QMediaPlayer = MagicMock()
mock_qt_multimedia.QAudioOutput = MagicMock()

# Patch sys.modules
sys.modules["PyQt6.QtMultimedia"] = mock_qt_multimedia

# Now import the service
from desktop_app.services.sound_manager import SoundManager, SpeechWorker

class TestSoundManager(unittest.TestCase):
    def setUp(self):
        # Reset the singleton instance before each test
        SoundManager._instance = None
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        SoundManager._instance = None

    def test_singleton_initialization(self):
        """Test that SoundManager is a singleton."""
        mgr1 = SoundManager.instance()
        mgr2 = SoundManager.instance()
        self.assertIs(mgr1, mgr2)
        self.assertTrue(hasattr(mgr1, 'sounds'))

    def test_generate_sounds_on_init(self):
        """Test that sounds are generated (cached to dict) on init."""
        with patch.object(SoundManager, '_generate_wav', return_value="mock_url") as m_gen:
            mgr = SoundManager()
            self.assertIn('hover', mgr.sounds)
            self.assertIn('click', mgr.sounds)
            self.assertIn('success', mgr.sounds)
            self.assertIn('scan', mgr.sounds)
            self.assertEqual(mgr.sounds['hover'], "mock_url")

    def test_play_sound_enabled(self):
        """Test playing a sound when enabled."""
        mgr = SoundManager()
        # Manually inject a sound
        mgr.sounds['test'] = "test_url"
        
        # Mock QSoundEffect instance
        mock_effect_instance = mock_qt_multimedia.QSoundEffect.return_value
        
        mgr.play_sound('test')
        
        mock_qt_multimedia.QSoundEffect.assert_called_with(mgr)
        mock_effect_instance.setSource.assert_called_with("test_url")
        mock_effect_instance.play.assert_called_once()
        
        # Check it was added to cache to prevent GC
        self.assertIn(mock_effect_instance, mgr.effects_cache)

    def test_play_sound_disabled(self):
        """Test playing a sound when globally disabled."""
        mgr = SoundManager()
        mgr.SOUND_ENABLED = False
        mgr.sounds['test'] = "test_url"
        
        mgr.play_sound('test')
        
        mock_qt_multimedia.QSoundEffect.assert_not_called()

    def test_play_sound_missing(self):
        """Test playing a non-existent sound."""
        # Reset mock call count from previous tests
        mock_qt_multimedia.QSoundEffect.reset_mock()
        
        mgr = SoundManager()
        mgr.play_sound('non_existent')
        mock_qt_multimedia.QSoundEffect.assert_not_called()

    @patch('desktop_app.services.sound_manager.SpeechWorker')
    def test_speak_starts_worker(self, MockWorker):
        """Test that speak method starts the SpeechWorker."""
        mgr = SoundManager()
        
        # Mock PlaybackState enum which is accessed
        mock_qt_multimedia.QMediaPlayer.PlaybackState.PlayingState = 1
        mgr.media_player.playbackState.return_value = 0 # Not playing
        
        mgr.speak("Hello World")
        
        MockWorker.assert_called_with("Hello World", mgr.temp_dir)
        worker_instance = MockWorker.return_value
        worker_instance.start.assert_called_once()
        
        # Verify signals connected
        worker_instance.finished.connect.assert_called_with(mgr._on_speech_ready)
        worker_instance.error.connect.assert_called_with(mgr._on_speech_error)

    def test_on_speech_ready(self):
        """Test callback when speech file is ready."""
        mgr = SoundManager()
        
        fake_path = "/tmp/speech.mp3"
        mgr._on_speech_ready(fake_path)
        
        mgr.media_player.setSource.assert_called()
        mgr.media_player.play.assert_called_once()

    def test_worker_run_no_edge_tts(self):
        """Test SpeechWorker behavior when edge_tts is missing."""
        # Force HAS_EDGE_TTS = False in the module
        with patch('desktop_app.services.sound_manager.HAS_EDGE_TTS', False):
            worker = SpeechWorker("text", "/out")
            
            # Create mock signals
            worker.error = MagicMock()
            worker.finished = MagicMock()
            
            worker.run()
            
            worker.error.emit.assert_called_with("edge-tts module not found")
            worker.finished.emit.assert_not_called()

    @patch('desktop_app.services.sound_manager.HAS_EDGE_TTS', True)
    def test_worker_run_success(self):
        """Test SpeechWorker success path."""
        # Force inject the edge_tts mock into the module since it might be missing
        import desktop_app.services.sound_manager as sm_module
        
        mock_edge_tts = MagicMock()
        original_edge_tts = getattr(sm_module, 'edge_tts', None)
        sm_module.edge_tts = mock_edge_tts
        
        try:
            worker = SpeechWorker("text", self.temp_dir)
            worker.error = MagicMock()
            worker.finished = MagicMock()
            
            # Mock asyncio loop
            with patch('asyncio.new_event_loop') as m_loop:
                with patch('asyncio.set_event_loop'): # Patch to avoid type check error
                    mock_loop = MagicMock()
                    m_loop.return_value = mock_loop

                    worker.run()

                # Verify that it called communicate.save() inside the loop
                # communicate instance is returned by mock_edge_tts.Communicate(...)
                communicate_instance = mock_edge_tts.Communicate.return_value
                
                mock_loop.run_until_complete.assert_called()
                communicate_instance.save.assert_called()

                worker.finished.emit.assert_called()
                mock_loop.close.assert_called()
        finally:
            if original_edge_tts:
                sm_module.edge_tts = original_edge_tts
            else:
                del sm_module.edge_tts

