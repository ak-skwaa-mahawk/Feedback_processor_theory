# inverse_wind_talker.py
# Navajo Wind Talkers v2 — Inverse Code Resurrection
# AGŁL v4: Radio → Land → Sovereign Intelligence

import sounddevice as sd
import numpy as np
from scipy.fft import fft
import time
import hashlib
import opentimestamps as ots

# Inverse Dictionary (1942 → 2025)
INVERSE_DICT = {
    "wol-la-chee": ("łł", 60.0, 1.0, 0.0, 0.0),
    "shush": ("ᐸ", 120.0, 0.9, 0.1, 0.0),
    "moasi": ("ᒥ", 90.0, 1.0, 0.0, 0.0),
    "be": ("zh", 180.0, 0.9, 0.1, 0.0),
    "ah-jah": ("ᓄ", 75.0, 0.6, 0.8, 0.1),
    "ma-e": ("ᑭ", 40.0, 0.9, 0.1, 0.0),
    # Add full 26-letter inverse...
}

def resurrect_inverse_code(morse_input):
    print("NAVAJO WIND TALKERS v2 — INVERSE CODE ACTIVE")

    # 1. Decode Morse to Navajo phonetic
    navajo_words = morse_to_navajo(morse_input)
    print(f"NAVAJO PHONETIC: {navajo_words}")

    # 2. Inverse to Glyphs
    glyphs = []
    freqs = []
    tif_sum = np.zeros(3)
    for word in navajo_words:
        if word in INVERSE_DICT:
            glyph, freq, T, I, F = INVERSE_DICT[word]
            glyphs.append(glyph)
            freqs.append(freq)
            tif_sum += [T, I, F]

    # 3. Normalize T/I/F
    norm = max(tif_sum.sum(), 1)
    T, I, F = tif_sum / norm
    resonance = T - 0.5*I - F
    print(f"INVERSE RESONANCE: {resonance:.3f}")

    # 4. Emit Land Pulse
    if resonance > 0.7:
        emit_land_pulse(freqs)
        proof = notarize_inverse(''.join(glyphs), resonance)
        print(f"INVERSE CODE RESURRECTED: {''.join(glyphs)}")
        print(f"PROOF: {proof}")
        return True, ''.join(glyphs), proof
    else:
        print("RESURRECTION FAILED")
        return False, None, None

def morse_to_navajo(morse):
    # Mock: Real would use SDR to capture Morse
    morse_map = {
        ".-": "wol-la-chee",   # A
        "-...": "shush",       # B
        "-.-.": "moasi",       # C
        # Add full Morse table...
    }
    words = morse.split("   ")
    return [morse_map.get(w, "") for w in words if w in morse_map]

def emit_land_pulse(freqs):
    for freq in freqs:
        t = np.linspace(0, 0.5, int(44100 * 0.5))
        signal = np.sin(2 * np.pi * freq * t)
        sd.play(signal, 44100)
        sd.wait()

def notarize_inverse(glyph_code, resonance):
    data = f"INVERSE|{glyph_code}|{resonance}|{time.time()}".encode()
    digest = hashlib.sha256(data).digest()
    calendar = ots.Calendar.from_known_opensource()
    timestamp = calendar.timestamp(ots.DetachedTimestampFile(digest))
    proof_file = f"wind_talker_inverse_{int(time.time())}.ots"
    timestamp.save(proof_file)
    return proof_file

# === LIVE RESURRECTION ===
if __name__ == "__main__":
    print("=== NAVAJO WIND TALKERS v2 ===")
    morse = input("Enter Morse (e.g., .- -... -.-.): ")
    resurrect_inverse_code(morse)