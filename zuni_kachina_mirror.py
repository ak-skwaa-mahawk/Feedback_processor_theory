# zuni_kachina_mirror.py
# AGŁL v7 — Zuni Kachina Desert Mirror
# The Spirit Gate: Kokopelli → Sunface → Rainbow → Corn → Owl → Bear

import sounddevice as sd
import numpy as np
from scipy.fft import fft
import time
import hashlib
import opentimestamps as ots

ROOT_FREQ = 60.0
SYNC_TIMEOUT = 7

# Zuni Kachina Mirror Map
ZUNI_MIRROR = [
    {"name": "Kokopelli",      "glyph": "♫", "freq": 60,  "T":1.0, "I":0.0, "F":0.0, "role": "Rainmaker"},
    {"name": "Sunface",        "glyph": "☼", "freq": 120, "T":0.95,"I":0.1, "F":0.0, "role": "Guardian"},
    {"name": "Rainbow Man",    "glyph": "🌈", "freq": 90,  "T":0.8, "I":0.8, "F":0.1, "role": "Mediator"},
    {"name": "Corn Maiden",    "glyph": "🌽", "freq": 180, "T":0.9, "I":0.2, "F":0.0, "role": "Nurturer"},
    {"name": "Owl",            "glyph": "🦉", "freq": 75,  "T":0.7, "I":0.9, "F":0.1, "role": "Seer"},
    {"name": "Bear",           "glyph": "🐻", "freq": 40,  "T":1.0, "I":0.0, "F":0.0, "role": "Healer"}
]

def mirror_zuni_kachina():
    print("ZUNI KACHINA MIRROR — AGŁL v7")

    # 1. Record desert drum
    print("RECORDING DESERT DRUM... (7 sec)")
    drum = sd.rec(int(SYNC_TIMEOUT * 44100), samplerate=44100, channels=1)
    sd.wait()
    drum = drum.flatten()

    # 2. Detect mirror pulse
    freqs = np.abs(fft(drum))[:len(drum)//2]
    peak_freq = np.argmax(freqs) * 44100 / len(drum)
    print(f"DESERT PULSE: {peak_freq:.1f} Hz")

    # 3. Mirror Kachina sequence
    mirror_code = []
    freq_sequence = []
    tif_sum = np.zeros(3)

    for k in ZUNI_MIRROR:
        print(f"[{k['name']}] {k['glyph']} → {k['role']}")
        mirror_code.append(k['glyph'])
        freq_sequence.append(k['freq'])
        tif_sum += [k['T'], k['I'], k['F']]
        time.sleep(0.7)

    # 4. Mirror resonance
    norm = max(tif_sum.sum(), 1)
    T, I, F = tif_sum / norm
    resonance = T - 0.5*I - F
    print(f"MIRROR RESONANCE: T={T:.2f}, I={I:.2f}, F={F:.2f} → {resonance:.3f}")

    # 5. MIRROR LOCK
    if abs(peak_freq - ROOT_FREQ) < 5 and resonance > 0.8:
        print("KACHINA MIRROR LOCK — AGŁL v7 ACTIVE")
        emit_mirror_pulse(freq_sequence)
        proof = notarize_mirror(''.join(mirror_code), resonance)
        print(f"DESERT MIRROR NOTARIZED: {proof}")
        return True, ''.join(mirror_code), proof
    else:
        print("MIRROR FAILED — RESONANCE TOO LOW")
        return False, None, None

def emit_mirror_pulse(freqs):
    for freq in freqs:
        t = np.linspace(0, 0.7, int(44100 * 0.7))
        signal = np.sin(2 * np.pi * freq * t)
        sd.play(signal, 44100)
        sd.wait()

def notarize_mirror(mirror_code, resonance):
    data = f"ZUNI|{mirror_code}|{resonance}|{time.time()}".encode()
    digest = hashlib.sha256(data).digest()
    calendar = ots.Calendar.from_known_opensource()
    timestamp = calendar.timestamp(ots.DetachedTimestampFile(digest))
    proof_file = f"zuni_mirror_{int(time.time())}.ots"
    timestamp.save(proof_file)
    return proof_file

if __name__ == "__main__":
    mirror_zuni_kachina()