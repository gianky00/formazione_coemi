import os
import struct
import math
import tempfile
import threading
from PyQt6.QtCore import QUrl, QObject
from PyQt6.QtMultimedia import QSoundEffect

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

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
        self.effects_cache = [] # Keep references to playing sounds
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
        # Hover: High tech chirp (2kHz to 3kHz)
        self.sounds['hover'] = self._generate_wav('hover.wav', lambda t: 2000 + t*5000, 0.03, 0.1)

        # Click: Digital impact (800Hz drop)
        self.sounds['click'] = self._generate_wav('click.wav', lambda t: 800 - t*8000 if t < 0.05 else 0, 0.05, 0.2)

        # Success: Ascending chime
        self.sounds['success'] = self._generate_wav('success.wav', lambda t: 400 + t*2000, 0.4, 0.2)

        # Analysis: Data stream noise
        self.sounds['scan'] = self._generate_wav('scan.wav', lambda t: 1000 + math.sin(t*100)*500, 0.1, 0.05)

    def play_sound(self, sound_name):
        if sound_name not in self.sounds: return

        # Clean cache
        self.effects_cache = [e for e in self.effects_cache if e.isPlaying()]

        effect = QSoundEffect(self)
        effect.setSource(self.sounds[sound_name])
        effect.setVolume(0.5)
        effect.play()
        self.effects_cache.append(effect) # Prevent GC

    def speak(self, text):
        if not pyttsx3: return

        def _run():
            try:
                # Initialize engine locally in thread
                engine = pyttsx3.init()
                # Try to set a robotic voice if available?
                # voices = engine.getProperty('voices')
                # engine.setProperty('rate', 150)
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                print(f"[SoundManager] TTS Error: {e}")

        threading.Thread(target=_run, daemon=True).start()
