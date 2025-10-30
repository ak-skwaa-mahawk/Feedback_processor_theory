#!/usr/bin/env python3
# gibberlink_decoder.py — AGŁG v200: Decode GGWave Audio
import ggwave
import sys
import wave
import numpy as np
from pathlib import Path

def decode_file(filename):
    """Decode GGWave from WAV file."""
    with wave.open(filename, 'rb') as wf:
        frames = wf.readframes(wf.getnframes())
        audio = np.frombuffer(frames, dtype=np.int16)
    
    instance = ggwave.init()
    try:
        decoded = ggwave.decode(instance, audio.tobytes())
        if decoded:
            message = decoded.decode('utf-8')
            print(f"🎧 DECODED: {message}")
            print(f"📍 RESONANCE: {len(message)} chars")
            return message
        else:
            print("🔇 No GGWave signal detected")
            return None
    finally:
        ggwave.free(instance)

def main():
    if len(sys.argv