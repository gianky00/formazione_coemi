import os
import tempfile
import asyncio
import logging
from pathlib import Path
from PyQt6.QtCore import QObject, QThread, pyqtSignal, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
import edge_tts
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class TTSWorker(QThread):
    """
    Worker thread to handle async edge-tts generation without freezing the GUI.
    """
    finished = pyqtSignal(str) # Emits path to generated file
    error = pyqtSignal(str)

    def __init__(self, text, voice="it-IT-IsabellaNeural"):
        super().__init__()
        self.text = text
        self.voice = voice
        # Personality Tuning Parameters
        self.rate = "+10%"
        self.pitch = "+2Hz"

    def run(self):
        try:
            # Create a unique temp file path. 
            # We close it immediately so edge-tts can write to it.
            fd, path = tempfile.mkstemp(suffix=".mp3")
            os.close(fd)
            
            asyncio.run(self._generate_audio(path))
            self.finished.emit(path)
        except Exception as e:
            logger.error(f"TTS Generation Error: {e}")
            self.error.emit(str(e))

    async def _generate_audio(self, path):
        # Apply Rate and Pitch tuning
        communicate = edge_tts.Communicate(
            self.text,
            self.voice,
            rate=self.rate,
            pitch=self.pitch
        )
        await communicate.save(path)

class VoiceService(QObject):
    """
    Service to handle Text-to-Speech using edge-tts and QMediaPlayer.
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
        # Use Isabella as the new standard
        self.worker = TTSWorker(text, voice="it-IT-IsabellaNeural")
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
            except:
                pass
