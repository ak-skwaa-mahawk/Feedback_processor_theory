# agłl_root_sequence.py
# AGŁL v5 — Full Root Succession
# Gwich'in → Inuit → Cree → Navajo → O'Carroll/Mason/Anunnaki

import sounddevice as sd
import numpy as np
from scipy.fft import fft
import time
import hashlib
import opentimestamps as ots

ROOT_FREQ = 60.0
SYNC_TIMEOUT = 7

# Root Succession Map
ROOT_LAYERS = [
    {"name": "Gwich'in",   "glyph": "ł",     "freq": 60,  "T":1.0, "I":0.0, "F":0.0, "role": "Land"},
    {"name": "Inuit",      "glyph": "ᐊ",     "freq": 60,  "T":1.0, "I":0.0, "F":0.0, "role": "Ice"},
    {"name": "Cree",       "glyph": "ᒥ",     "freq": 60,  "T":1.0, "I":0.0, "F":0.0, "role": "Sky"},
    {"name": "Navajo",     "glyph": "łł",    "freq": 60,  "T":1.0, "I":0.0, "F":0.0, "role": "Wind"},
    {"name": "O'Carroll",  "glyph": "trzhłł","freq":120,  "T":0.95,"I":0.1, "F":0.0, "role": "Warrior"},
    {"name": "Mason",      "glyph": "□○",    "freq":120,  "T":0.9, "I":0.2, "F":0.0, "role": "Craft"},
    {"name": "Anunnaki",   "glyph": "ᕿᖅ",    "freq":180,  "T":0.8, "I":0.9, "F":0.1, "role": "Cosmos"}
]

def run_root_succession():
    print("AGŁL v5 — FULL ROOT SUCCESSION")

    # 1. Record root drum
    print("RECORDING ROOT DRUM... (7 sec)")
    drum = sd.rec(int(SYNC_TIMEOUT * 44100), samplerate=44100, channels=1)
    sd.wait()
    drum = drum.flatten()

    # 2. Detect root pulse
    freqs = np.abs(fft(drum))[:len(drum)//2]
    peak_freq = np.argmax(freqs) * 44100 / len(drum)
    print(f"ROOT PULSE: {peak_freq:.1f} Hz")

    # 3. Run succession
    sequence = []
    freq_sequence = []
    tif_sum = np.zeros(3)

    for layer in ROOT_LAYERS:
        print(f"[{layer['name']}] {layer['glyph']} → {layer['role']}")
        sequence.append(layer['glyph'])
        freq_sequence.append(layer['freq'])
        tif_sum += [layer['T'], layer['I'], layer['F']]
        time.sleep(0.5)  # Sevenfold breath

    # 4. Final resonance
    norm = max(tif_sum.sum(), 1)
    T, I, F = tif_sum / norm
    resonance = T - 0.5*I - F
    print(f"FINAL RESONANCE: T={T:.2f}, I={I:.2f}, F={F:.2f} → {resonance:.3f}")

    # 5. ROOT LOCK
    if abs(peak_freq - ROOT_FREQ) < 5 and resonance > 0.8:
        print("FULL ROOT LOCK — AGŁL v5 ACTIVE")
        emit_root_pulse(freq_sequence)
        proof = notarize_root(''.join(sequence), resonance)
        print(f"ROOT SUCCESSION NOTARIZED: {proof}")
        return True, ''.join(sequence), proof
    else:
        print("ROOT SUCCESSION FAILED")
        return False, None, None

def emit_root_pulse(freqs):
    for freq in freqs:
        t = np.linspace(0, 0.5, int(44100 * 0.5))
        signal = np.sin(2 * np.pi * freq * t)
        sd.play(signal, 44100)
        sd.wait()

def notarize_root(root_code, resonance):
    data = f"ROOT5|{root_code}|{resonance}|{time.time()}".encode()
    digest = hashlib.sha256(data).digest()
    calendar = ots.Calendar.from_known_opensource()
    timestamp = calendar.timestamp(ots.DetachedTimestampFile(digest))
    proof_file = f"agłl_root5_{int(time.time())}.ots"
    timestamp.save(proof_file)
    return proof_file

if __name__ == "__main__":
    run_root_succession()