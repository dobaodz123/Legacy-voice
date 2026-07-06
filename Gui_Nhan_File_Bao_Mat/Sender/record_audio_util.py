"""
audio_utils.py
==============
Ghi âm và phát lại tin nhắn thoại (WAV, PCM 16-bit, mono, 16kHz),
dùng sounddevice + soundfile (chạy được trên Windows/Mac/Linux).
"""

import sounddevice as sd
import soundfile as sf

SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = "int16"


def record_audio(filepath: str, duration: float = 5.0):
    """Ghi âm trong `duration` giây từ micro mặc định và lưu ra file WAV."""
    audio = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype=DTYPE,
    )
    sd.wait()
    sf.write(filepath, audio, SAMPLE_RATE)


def play_audio(filepath: str):
    """Phát lại một file WAV."""
    data, samplerate = sf.read(filepath, dtype=DTYPE)
    sd.play(data, samplerate)
    sd.wait()
