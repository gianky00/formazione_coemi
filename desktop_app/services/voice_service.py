import os
import threading
import tempfile
import logging
import pygame
from gtts import gTTS
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class VoiceService:
    """
    Service to handle Text-to-Speech using gTTS and Pygame (better for Tkinter than QtMultimedia).
    """
    def __init__(self):
        self.enabled = settings.VOICE_ASSISTANT_ENABLED
        self.is_muted = False

        # Initialize mixer
        try:
            pygame.mixer.init()
        except Exception:
            pass

    def speak(self, text: str):
        """
        Generates and plays speech for the given text.
        """
        self.enabled = settings.VOICE_ASSISTANT_ENABLED
        if not self.enabled or self.is_muted or not text:
            return

        # Run in thread
        threading.Thread(target=self._speak_thread, args=(text,), daemon=True).start()

    def _speak_thread(self, text):
        try:
            # Generate
            fd, path = tempfile.mkstemp(suffix=".mp3")
            os.close(fd)

            tts = gTTS(text=text, lang='it', tld='com', slow=False)
            tts.save(path)

            # Play
            self._play_file(path)

        except Exception as e:
            logger.error(f"TTS Error: {e}")

    def _play_file(self, path):
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.load(path)
                pygame.mixer.music.play()
                # Wait for finish? No, let it play in background.
                # Cleanup is tricky if we don't wait.
                # For simplicity, we just leave temp files for OS to clean or clean on exit.
                # Or use a queue.
        except Exception as e:
            logger.error(f"Audio Playback Error: {e}")

    def stop(self):
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
        except Exception:
            pass

    def cleanup(self):
        self.stop()
        try:
            pygame.mixer.quit()
        except Exception:
            pass
