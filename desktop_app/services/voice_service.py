import os
import tempfile
import logging
from PyQt6.QtCore import QObject, QThread, pyqtSignal, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class TTSWorker(QThread):
    """
    Worker thread to handle blocking ElevenLabs generation without freezing the GUI.
    """
    finished = pyqtSignal(str) # Emits path to generated file
    error = pyqtSignal(str)

    def __init__(self, text, voice_id, model_id, api_key):
        super().__init__()
        self.text = text
        self.voice_id = voice_id
        self.model_id = model_id
        self.api_key = api_key

    def run(self):
        try:
            from elevenlabs import ElevenLabs

            # Initialize client with the de-obfuscated key
            client = ElevenLabs(api_key=self.api_key)

            # Create a unique temp file path. 
            fd, path = tempfile.mkstemp(suffix=".mp3")
            os.close(fd)
            
            # Generate audio (returns a generator)
            audio_generator = client.generate(
                text=self.text,
                voice=self.voice_id,
                model=self.model_id
            )

            # Save audio to file
            with open(path, "wb") as f:
                for chunk in audio_generator:
                    f.write(chunk)

            self.finished.emit(path)
        except Exception as e:
            logger.error(f"ElevenLabs TTS Generation Error: {e}")
            self.error.emit(str(e))

class VoiceService(QObject):
    """
    Service to handle Text-to-Speech using ElevenLabs and QMediaPlayer.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.enabled = settings.VOICE_ASSISTANT_ENABLED
        self.is_muted = False
        
        # Audio Player Setup
        self._player = QMediaPlayer()
        self._audio_output = QAudioOutput()
        self._player.setAudioOutput(self._audio_output)
        
        # Keep track of temporary files to clean them up
        self._current_file = None
        self.worker = None # Keep reference to prevent GC
        
        self._player.mediaStatusChanged.connect(self._on_media_status_changed)

    def speak(self, text: str):
        """
        Generates and plays speech for the given text.
        """
        # Reload setting in case it changed
        self.enabled = settings.VOICE_ASSISTANT_ENABLED

        if not self.enabled or self.is_muted or not text:
            return

        logger.info(f"Speaking: {text}")
        
        # Stop any current playback
        self.stop()

        # Start generation in background thread
        self.worker = TTSWorker(
            text=text,
            voice_id=settings.ELEVENLABS_VOICE_ID,
            model_id=settings.ELEVENLABS_MODEL_ID,
            api_key=settings.ELEVENLABS_API_KEY
        )
        self.worker.finished.connect(self._play_audio)
        self.worker.error.connect(lambda e: logger.error(f"TTS Error: {e}"))
        self.worker.start()

    def _play_audio(self, file_path):
        """
        Slot called when TTS generation is complete.
        """
        self._current_file = file_path
        self._player.setSource(QUrl.fromLocalFile(file_path))
        self._player.play()

    def _on_media_status_changed(self, status):
        """
        Cleanup file when playback finishes.
        """
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            # We can't delete immediately as the player might still hold the handle briefly
            pass

    def stop(self):
        """
        Stops playback immediately.
        """
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._player.stop()

    def toggle_mute(self):
        """
        Toggles temporary mute (independent of global setting).
        """
        self.is_muted = not self.is_muted
        if self.is_muted:
            self.stop()
        return self.is_muted
    
    def set_volume(self, volume: float):
        """
        Set volume (0.0 to 1.0)
        """
        self._audio_output.setVolume(volume)

    def cleanup(self):
        """
        Destructor-like cleanup.
        """
        self.stop()
        if self._current_file and os.path.exists(self._current_file):
            try:
                os.remove(self._current_file)
            except Exception: # S5754: Handle exception
                pass
