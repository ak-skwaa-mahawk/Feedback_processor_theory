# gwichin_glyph_sync_v2.py
# Gwich'in Glyph Syncing — Root Firmware v2

import sounddevice as sd
import numpy as np
from scipy.fft import fft
import time
import hashlib
import opentimestamps as ots

# Root (Circle, Alaska)
ROOT_FREQ = 60.0
SYNC_TIMEOUT = 7

# Glyph Map (Expanded)
GLYPH_MAP = {
    "ł": ("00", 60.0, 1.0, 0.0, 0.0),  # Land
    "zh": ("01", 120.0, 0.9, 0.1, 0.0), # Fire
    "ch": ("10", 90.0, 0.6, 0.8, 0.1),  # Water
    "tr": ("11", 180.0, 1.0, 0.0, 0.0), # Truth
    "sh": ("00", 40.0, 0.2, 0.1, 0.7),  # Shadow
    "łł": ("01", 75.0, 0.3, 1.0, 0.2)   # Indeterminate
}

def sync_gwichin_glyphs(chant_input):
    print("GWICH'IN GLYPH SYNC v2 INITIATED")

    # 1. Record drum
    print("RECORDING ROOT DRUM... (7 sec)")
    drum = sd.rec(int(SYNC_TIMEOUT * 44100), samplerate=44100, channels=1)
    sd.wait()
    drum = drum.flatten()

    # 2. Detect peak
    freqs = np.abs(fft(drum))[:len(drum)//2]
    peak_freq = np.argmax(freqs) * 44100 / len(drum)
    print(f"DRUM ROOT: {peak_freq:.1f} Hz")

    # 3. Parse chant
    glyphs = list(chant_input.lower().replace(" ", ""))
    binary_code = ""
    freq_sequence = []
    tif_sum = np.zeros(3)

    for g in glyphs:
        if g in GLYPH_MAP:
            bin_val, freq, T, I, F = GLYPH_MAP[g]
            binary_code += bin_val
            freq_sequence.append(freq)
            tif_sum += [T, I, F]

    # 4. Normalize T/I/F
    norm = max(tif_sum.sum(), 1)
    T, I, F = tif_sum / norm

    # 5. Resonance score
    resonance = T - 0.5*I - F
    print(f"GLYPH RESONANCE: T={T:.2f}, I={I:.2f}, F={F:.2f} → {resonance:.3f}")

    # 6. SYNC LOCK
    if abs(peak_freq - ROOT_FREQ) < 5 and resonance > 0.7:
        print("SYNC LOCK ACHIEVED — ROOT FIRMWARE ACTIVE")

        # 7. Emit sync pulse
        emit_sync_pulse(freq_sequence)

        # 8. Notarize
        proof = notarize_sync(binary_code, resonance)
        print(f"ROOT SYNC NOTARIZED: {proof}")

        return True, binary_code, proof
    else:
        print("SYNC FAILED — RESONANCE TOO LOW")
        return False, None, None

def emit_sync_pulse(freqs, duration=0.5):
    for freq in freqs:
        t = np.linspace(0, duration, int(44100 * duration))
        signal = np.sin(2 * np.pi * freq * t)
        sd.play(signal, 44100)
        sd.wait()

def notarize_sync(binary_code, resonance):
    data = f"{binary_code}|{resonance}|{time.time()}".encode()
    digest = hashlib.sha256(data).digest()
    calendar = ots.Calendar.from_known_opensource()
    timestamp = calendar.timestamp(ots.DetachedTimestampFile(digest))
    proof_file = f"gwichin_sync_{int(time.time())}.ots"
    timestamp.save(proof_file)
    return proof_file

if __name__ == "__main__":
    print("=== GWICH'IN GLYPH SYNC v2 ===")
    print("Circle, Alaska | Root Firmware")
    chant = input("Enter chant: ")
    sync_gwichin_glyphs(chant)