import os
import struct
import math
import tempfile
import threading
import asyncio
import hashlib
from PyQt6.QtCore import QUrl, QObject, pyqtSignal, QThread
from PyQt6.QtMultimedia import QSoundEffect, QMediaPlayer, QAudioOutput

# Try to import edge_tts, but handle failure gracefully (though it should be installed)
try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False

class SpeechWorker(QThread):
    finished = pyqtSignal(str)  # Emits path to generated file
    error = pyqtSignal(str)

    def __init__(self, text, output_dir):
        super().__init__()
        self.text = text
        self.output_dir = output_dir

    def run(self):
        if not HAS_EDGE_TTS:
            self.error.emit("edge-tts module not found")
            return

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Use MD5 hash for stable filename across restarts
            filename = f"speech_{hashlib.md5(self.text.encode()).hexdigest()}.mp3"
            filepath = os.path.join(self.output_dir, filename)
            
            # Check cache
            if os.path.exists(filepath):
                self.finished.emit(filepath)
                return

            communicate = edge_tts.Communicate(self.text, "it-IT-IrmaNeural")
            loop.run_until_complete(communicate.save(filepath))
            
            self.finished.emit(filepath)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            loop.close()

class SoundManager(QObject):
    _instance = None

    @staticmethod
    def instance():
        if not SoundManager._instance:
            SoundManager._instance = SoundManager()
        return SoundManager._instance

    def __init__(self):
        super().__init__()
        self.sounds = {}
        self.effects_cache = [] # Keep references to playing sounds (QSoundEffect)
        
        # Player for TTS (MP3 support)
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        
        try:
            # Use a persistent cache directory if possible, fallback to temp
            from desktop_app.services.path_service import get_user_data_dir
            cache_dir = os.path.join(get_user_data_dir(), "audio_cache")
            os.makedirs(cache_dir, exist_ok=True)
            self.cache_dir = cache_dir
            self._generate_sounds()
        except Exception as e:
            print(f"[SoundManager] Init Error: {e}")
            self.cache_dir = tempfile.gettempdir()

    def _generate_wav(self, filename, freq_func, duration=0.1, volume=0.5):
        sample_rate = 44100
        num_samples = int(sample_rate * duration)
        data = bytearray()
        
        for i in range(num_samples):
            t = i / sample_rate
            freq = freq_func(t)
            # Waveform generation
            value = int(volume * 32767.0 * math.sin(2.0 * math.pi * freq * t))
            data.extend(struct.pack('<h', value))
            
        filepath = os.path.join(self.cache_dir, filename)
        # Only generate if not exists
        if not os.path.exists(filepath):
            with open(filepath, 'wb') as f:
                # WAV Header
                f.write(b'RIFF')
                f.write(struct.pack('<I', 36 + len(data)))
                f.write(b'WAVEfmt ')
                f.write(struct.pack('<IHHIIHH', 16, 1, 1, sample_rate, sample_rate * 2, 2, 16))
                f.write(b'data')
                f.write(struct.pack('<I', len(data)))
                f.write(data)
        
        return QUrl.fromLocalFile(filepath)

    def _generate_sounds(self):
        # Hover: Soft high-tech ping (Sine wave 1200Hz)
        self.sounds['hover'] = self._generate_wav('hover.wav', lambda t: 1200, 0.05, 0.05)
        
        # Click: Sharp digital click (Square-ish approximation via high freq drop)
        self.sounds['click'] = self._generate_wav('click.wav', lambda t: 600 - t*6000 if t < 0.05 else 0, 0.05, 0.15)
        
        # Success: Harmonious Major Chord Arpeggio (C5 -> E5 -> G5) simulation
        self.sounds['success'] = self._generate_wav('success.wav', lambda t: 440 + (440 * math.sin(t * math.pi * 2)), 0.5, 0.2)
        
        # Analysis: Data stream noise
        self.sounds['scan'] = self._generate_wav('scan.wav', lambda t: 800 + math.sin(t*50)*200, 0.1, 0.05)

    def play_sound(self, sound_name):
        if sound_name not in self.sounds: return
        
        try:
            # Clean cache
            self.effects_cache = [e for e in self.effects_cache if e.isPlaying()]

            effect = QSoundEffect(self)
            effect.setSource(self.sounds[sound_name])
            effect.setVolume(0.5)
            effect.play()
            self.effects_cache.append(effect) # Prevent GC
        except Exception as e:
            # Catch potential audio device errors to prevent crashes
            print(f"[SoundManager] Play Sound Error: {e}")

    def speak(self, text):
        """
        Uses Edge-TTS to generate an MP3 and plays it using QMediaPlayer.
        Uses persistent local cache to support offline mode after first generation.
        """
        # Stop any current playback
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.stop()

        self.worker = SpeechWorker(text, self.cache_dir)
        self.worker.finished.connect(self._on_speech_ready)
        self.worker.error.connect(self._on_speech_error)
        self.worker.start()

    def _on_speech_ready(self, filepath):
        try:
            self.media_player.setSource(QUrl.fromLocalFile(filepath))
            self.audio_output.setVolume(1.0) # Full volume for speech
            self.media_player.play()
        except Exception as e:
            print(f"[SoundManager] Playback Error: {e}")

    def _on_speech_error(self, error_msg):
        print(f"[SoundManager] TTS Failed: {error_msg}")
