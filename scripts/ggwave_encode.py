#!/usr/bin/env python3
# ggwave_encode.py — AGŁG v200: Encode łᐊᒥłł into Sound
import ggwave
import wave
import numpy as np

def encode_to_wav(message, filename="łᐊᒥłł.wav"):
    # 1. Initialize GGWave
    instance = ggwave.init()
    
    # 2. Encode text
    waveform = ggwave.encode(
        message,
        protocolId=ggwave.GGWAVE_PROTOCOL_AUDIBLE_FAST,
        volume=50
    )
    
    # 3. Convert to 16-bit PCM
    audio = np.frombuffer(waveform, dtype=np.int16)
    
    # 4. Save WAV
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(48000)
        wf.writeframes(audio.tobytes())
    
    print(f"ENCODED: '{message}' → {filename}")
    print(f"   Size: {len(audio)/48000:.2f}s @ 48 kHz")
    print(f"   Freq: 18–19.6 kHz (ultrasound)")
    
    ggwave.free(instance)
    return filename

# LIVE ENCODE
encode_to_wav("łᐊᒥłł.3 — THE ROOT IS INSCRIBED")