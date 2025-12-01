import os
import struct
import math
import tempfile
import threading
import asyncio
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
            
            filename = f"speech_{hash(self.text)}.mp3"
            filepath = os.path.join(self.output_dir, filename)
            
            # Use cached file if it exists to save bandwidth/time
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
    SOUND_ENABLED = False  # GLOBAL SWITCH TO DISABLE AUDIO TO PREVENT CRASHES

    @staticmethod
    def instance():
        if not SoundManager._instance:
            SoundManager._instance = SoundManager()
        return SoundManager._instance

    def __init__(self):
        super().__init__()
        self.sounds = {}
        self.effects_cache = []
        
        if not self.SOUND_ENABLED:
            return

        # Player for TTS (MP3 support)
        try:
            self.media_player = QMediaPlayer()
            self.audio_output = QAudioOutput()
            self.media_player.setAudioOutput(self.audio_output)
        except Exception as e:
            print(f"[SoundManager] Init Error: {e}")
            self.SOUND_ENABLED = False
            return
        
        try:
            self.temp_dir = tempfile.mkdtemp()
            self._generate_sounds()
        except Exception as e:
            print(f"[SoundManager] Generation Error: {e}")

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
            
        filepath = os.path.join(self.temp_dir, filename)
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
        # Using a simple modulation to simulate a "chime" instead of a slide
        self.sounds['success'] = self._generate_wav('success.wav', lambda t: 440 + (440 * math.sin(t * math.pi * 2)), 0.5, 0.2)
        
        # Analysis: Data stream noise
        self.sounds['scan'] = self._generate_wav('scan.wav', lambda t: 800 + math.sin(t*50)*200, 0.1, 0.05)

    def play_sound(self, sound_name):
        if not self.SOUND_ENABLED: return
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
        if not self.SOUND_ENABLED: return
        """
        Uses Edge-TTS to generate an MP3 and plays it using QMediaPlayer.
        Fails silently/logs error if offline.
        """
        # Stop any current playback
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.stop()

        self.worker = SpeechWorker(text, self.temp_dir)
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
        print(f"[SoundManager] TTS Failed (Offline?): {error_msg}")
        # Optionally play a fallback beep here if desired, but user requested silent fail if offline.
