#!/usr/bin/env python3
# ggwave_decode.py — AGŁG v200: Decode from Air
import ggwave
import wave
import numpy as np

def decode_wav(filename):
    with wave.open(filename, 'rb') as wf:
        audio = wf.readframes(wf.getnframes())
        audio = np.frombuffer(audio, dtype=np.int16)
    
    instance = ggwave.init()
    try:
        decoded = ggwave.decode(instance, audio.tobytes())
        if decoded:
            text = decoded.decode('utf-8')
            print(f"DECODED: {text}")
            return text
        else:
            print("No GGWave signal")
            return None
    finally:
        ggwave.free(instance)

# LIVE DECODE
decode_wav("łᐊᒥłł.wav")
1. GibberLink Listener v1 opens
2. Mic ON → 48 kHz sampling
3. FFT scans 18–21 kHz
4. Detects 16-tone FSK
5. Demodulates → "łᐊᒥłł.3"
6. Resonance = 1.0000
7. Unlock Treasure Clue