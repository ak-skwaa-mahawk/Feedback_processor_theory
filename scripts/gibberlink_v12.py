#!/usr/bin/env python3
# gibberlink_v12.py — AGŁG v1200: Ultrasound Whisper v12
import ggwave
import wave
import numpy as np
import json
from pathlib import Path

GLYPH_MAP = {
    'łᐊ': 18.0, 'ᒥᐊ': 18.5, 'ᐧᐊ': 19.0, 'ᓂᐊ': 19.5,
    'ᓴᑕ': 20.0, 'ᐊᒍ': 20.5, 'ᐊᐧᐊ': 21.0, 'ᓂᐊᐧ': 21.5,
    'ᐊᒥ': 22.0
}

def encode_ultrasound(message, filename="gibberlink_v12.wav"):
    """Encode 12 glyphs/sec ultrasound"""
    instance = ggwave.init()
    ggwave_set_protocol(instance, GGWAVE_PROTOCOL_ULTRASOUND_V2)
    
    # Glyph → Frequency
    waveform = ggwave.encode(message, instance)
    
    # Save 48kHz WAV
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(48000)
        wf.writeframes(waveform)
    
    ggwave.free(instance)
    return filename

def decode_ultrasound(filename):
    """Decode 18–22 kHz"""
    with wave.open(filename, 'rb') as wf:
        audio = wf.readframes(wf.getnframes())
    
    instance = ggwave.init()
    decoded = ggwave.decode(instance, audio)
    ggwave.free(instance)
    
    return decoded.decode() if decoded else None

# LIVE TEST
message = "łᐊᒥłł.12-SKODEN!"
wav = encode_ultrasound(message)
decoded = decode_ultrasound(wav)
print(f"ENCODED: {message}")
print(f"DECODED: {decoded}")
print(f"RESONANCE: {len(decoded)/len(message):.2f}")