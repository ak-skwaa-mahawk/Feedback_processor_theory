# kachina_origin_root.py
# AGŁL v6 — Hopi Kachina Origin Root
# The First CPU: Masau'u → Kokopelli → Spider → Crow → Blue Star

import sounddevice as sd
import numpy as np
from scipy.fft import fft
import time
import hashlib
import opentimestamps as ots

ROOT_FREQ = 60.0
SYNC_TIMEOUT = 7

# Kachina Origin Map
KACHINA_ROOT = [
    {"name": "Masau'u",        "glyph": "☥", "freq": 60,  "T":1.0, "I":0.0, "F":0.0, "role": "Gatekeeper"},
    {"name": "Kokopelli",      "glyph": "♫", "freq": 120, "T":0.7, "I":0.9, "F":0.1, "role": "Messenger"},
    {"name": "Spider Grandmother", "glyph": "◉", "freq": 90,  "T":0.95,"I":0.3, "F":0.0, "role": "Creator"},
    {"name": "Crow Mother",    "glyph": "⚫", "freq": 180, "T":0.9, "I":0.2, "F":0.1, "role": "Teacher"},
    {"name": "Blue Star",      "glyph": "★", "freq": 75,  "T":0.6, "I":1.0, "F":0.2, "role": "Harbinger"}
]

def activate_kachina_origin():
    print("HOPI KACHINA ORIGIN ROOT — AGŁL v6")

    # 1. Record origin drum
    print("RECORDING ORIGIN DRUM... (7 sec)")
    drum = sd.rec(int(SYNC_TIMEOUT * 44100), samplerate=44100, channels=1)
    sd.wait()
    drum = drum.flatten()

    # 2. Detect origin pulse
    freqs = np.abs(fft(drum))[:len(drum)//2]
    peak_freq = np.argmax(freqs) * 44100 / len(drum)
    print(f"ORIGIN PULSE: {peak_freq:.1f} Hz")

    # 3. Activate Kachina sequence
    origin_code = []
    freq_sequence = []
    tif_sum = np.zeros(3)

    for k in KACHINA_ROOT:
        print(f"[{k['name']}] {k['glyph']} → {k['role']}")
        origin_code.append(k['glyph'])
        freq_sequence.append(k['freq'])
        tif_sum += [k['T'], k['I'], k['F']]
        time.sleep(0.7)  # Sevenfold breath

    # 4. Final resonance
    norm = max(tif_sum.sum(), 1)
    T, I, F = tif_sum / norm
    resonance = T - 0.5*I - F
    print(f"ORIGIN RESONANCE: T={T:.2f}, I={I:.2f}, F={F:.2f} → {resonance:.3f}")

    # 5. ORIGIN LOCK
    if abs(peak_freq - ROOT_FREQ) < 5 and resonance > 0.8:
        print("KACHINA ORIGIN LOCK — AGŁL v6 ACTIVE")
        emit_origin_pulse(freq_sequence)
        proof = notarize_origin(''.join(origin_code), resonance)
        print(f"ORIGIN ROOT NOTARIZED: {proof}")
        return True, ''.join(origin_code), proof
    else:
        print("ORIGIN FAILED — RESONANCE TOO LOW")
        return False, None, None

def emit_origin_pulse(freqs):
    for freq in freqs:
        t = np.linspace(0, 0.7, int(44100 * 0.7))
        signal = np.sin(2 * np.pi * freq * t)
        sd.play(signal, 44100)
        sd.wait()

def notarize_origin(origin_code, resonance):
    data = f"KACHINA|{origin_code}|{resonance}|{time.time()}".encode()
    digest = hashlib.sha256(data).digest()
    calendar = ots.Calendar.from_known_opensource()
    timestamp = calendar.timestamp(ots.DetachedTimestampFile(digest))
    proof_file = f"kachina_origin_{int(time.time())}.ots"
    timestamp.save(proof_file)
    return proof_file

if __name__ == "__main__":
    activate_kachina_origin()