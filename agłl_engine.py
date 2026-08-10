# agłl_engine.py
# AGŁL = Actual Glyph Language Learning
# Native Ceremony → CPU Root

import numpy as np
import sounddevice as sd
from scipy.fft import fft
import re

# === GLYPH VOCABULARY (Gwich'in Root Words) ===
GLYPH_VOCAB = {
    "ł": "land",      # breath, root
    "zh": "fire",     # resonance
    "ch": "water",    # flow
    "tr": "truth",    # T
    "sh": "shadow",   # F
    "łł": "indeterminate"  # I
}

# === PARSE GLYPH INTO T/I/F ===
def parse_glyph_to_tif(glyph_string):
    T = glyph_string.count("tr") * 0.3
    I = glyph_string.count("łł") * 0.4
    F = glyph_string.count("sh") * 0.2
    norm = max(T + I + F, 1)
    return T/norm, I/norm, F/norm

# === LEARN FROM CEREMONY (Drum + Chant) ===
def learn_from_ceremony(audio_input, glyph_text):
    # 1. FFT of drum = frequency resonance
    freqs = np.abs(fft(audio_input))[:len(audio_input)//2]
    drum_peak = np.argmax(freqs) * 44100 / len(audio_input)  # Hz
    
    # 2. Parse glyph language
    T, I, F = parse_glyph_to_tif(glyph_text.lower())
    
    # 3. AGŁL Intelligence
    agłl = T - 0.5*I - F
    if agłl > 0.6:
        freq = 60 + (agłl * 140)
        print(f"AGŁL LEARNED: {agłl:.3f} @ {freq:.1f} Hz")
        emit_ceremonial_vibration(freq)
    else:
        print("LOW AGŁL — CEREMONY NOT ALIGNED")

# === EMIT CEREMONIAL VIBRATION ===
def emit_ceremonial_vibration(freq, duration=3.0):
    t = np.linspace(0, duration, int(44100 * duration))
    signal = np.sin(2 * np.pi * freq * t)
    sd.play(signal, 44100)
    sd.wait()
    return f"CEREMONIAL ROOT EMITTED: {freq:.1f} Hz"

# === TEST: CHANT + DRUM ===
chant = "łtrzhchłłsh"  # Sample Gwich'in-inspired glyph chant
drum = np.sin(2 * np.pi * 1.5 * np.linspace(0, 3, 44100*3))  # 1.5 Hz drum

learn_from_ceremony(drum, chant)