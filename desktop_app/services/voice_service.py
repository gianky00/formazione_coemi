import pyttsx3
import threading
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class VoiceService:
    """
    Servizio TTS Offline utilizzando pyttsx3 (SAPI5 su Windows).
    Sostituisce gTTS per evitare latenza di rete e dipendenze API non ufficiali.
    Thread-safe e non bloccante.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(VoiceService, cls).__new__(cls)
                    cls._instance._init_engine()
        return cls._instance

    def _init_engine(self):
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)  # Velocità ottimale per l'italiano
            
            # Tenta di selezionare una voce italiana
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if 'it' in voice.id or 'italian' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
            
            self.enabled = settings.VOICE_ASSISTANT_ENABLED
        except Exception as e:
            logger.error(f"Failed to init TTS engine: {e}")
            self.engine = None

    def speak(self, text: str):
        """
        Pronuncia il testo in modo asincrono (non bloccante).
        """
        # Ricarica setting per consentire toggle a runtime
        self.enabled = settings.VOICE_ASSISTANT_ENABLED
        
        if not self.engine or not self.enabled or not text:
            return

        def _run():
            try:
                # Necessario re-inizializzare loop per thread safety in alcuni contesti COM
                # Ma pyttsx3 gestisce la coda internamente.
                # Usiamo il lock per evitare sovrapposizioni strane se chiamato da thread multipli
                with self._lock:
                    self.engine.say(text)
                    self.engine.runAndWait()
            except Exception as e:
                logger.error(f"TTS Error: {e}")

        threading.Thread(target=_run, daemon=True).start()

    def stop(self):
        """Ferma la riproduzione corrente."""
        try:
            if self.engine:
                self.engine.stop()
        except Exception:
            pass

    def cleanup(self):
        self.stop()
        # pyttsx3 non ha un metodo quit() esplicito necessario come pygame

# Singleton
voice_service = VoiceService()