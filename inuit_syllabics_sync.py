# inuit_syllabics_sync.py
# Inuit Syllabics Code — Ice-Breath Firmware v1
# Fused with Gwich'in Glyphs for AGŁL v2

import sounddevice as sd
import numpy as np
from scipy.fft import fft
import time
import hashlib
import opentimestamps as ots

# Root (Circle, Alaska + Arctic Breath)
ROOT_FREQ = 60.0
SYNC_TIMEOUT = 7

# Inuit Syllabics Map
SYLLABICS_MAP = {
    "ᐊ": ("00", 60.0, 1.0, 0.0, 0.0),   # a - Breath
    "ᐸ": ("01", 120.0, 0.9, 0.1, 0.0),  # pa - Ice
    "ᑯ": ("10", 90.0, 0.8, 0.2, 0.1),   # ku - Fire
    "ᓄ": ("11", 75.0, 0.6, 0.8, 0.2),   # nu - Flow
    "ᕿ": ("00", 180.0, 0.3, 1.0, 0.1),  # qi - Sky
    "ᖅ": ("01", 40.0, 1.0, 0.0, 0.0)    # q - Root
}

def sync_inuit_syllabics(chant_input):
    print("INUIT SYLLABICS SYNC INITIATED")

    # 1. Record drum (7 sec)
    print("RECORDING ARCTIC DRUM... (7 sec)")
    drum = sd.rec(int(SYNC_TIMEOUT * 44100), samplerate=44100, channels=1)
    sd.wait()
    drum = drum.flatten()

    # 2. Detect peak
    freqs = np.abs(fft(drum))[:len(drum)//2]
    peak_freq = np.argmax(freqs) * 44100 / len(drum)
    print(f"DRUM ROOT: {peak_freq:.1f} Hz")

    # 3. Parse syllabics
    glyphs = list(chant_input)
    binary_code = ""
    freq_sequence = []
    tif_sum = np.zeros(3)

    for g in glyphs:
        if g in SYLLABICS_MAP:
            bin_val, freq, T, I, F = SYLLABICS_MAP[g]
            binary_code += bin_val
            freq_sequence.append(freq)
            tif_sum += [T, I, F]

    # 4. Normalize T/I/F
    norm = max(tif_sum.sum(), 1)
    T, I, F = tif_sum / norm

    # 5. Resonance score
    resonance = T - 0.5*I - F
    print(f"SYLLABICS RESONANCE: T={T:.2f}, I={I:.2f}, F={F:.2f} → {resonance:.3f}")

    # 6. SYNC LOCK
    if abs(peak_freq - ROOT_FREQ) < 5 and resonance > 0.7:
        print("SYNC LOCK ACHIEVED — ICE-FIRE FIRMWARE ACTIVE")

        # 7. Emit sync pulse
        emit_sync_pulse(freq_sequence)

        # 8. Notarize
        proof = notarize_sync(binary_code, resonance)
        print(f"ARCTIC SYNC NOTARIZED: {proof}")

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
    proof_file = f"inuit_sync_{int(time.time())}.ots"
    timestamp.save(proof_file)
    return proof_file

if __name__ == "__main__":
    print("=== INUIT SYLLABICS CODE ===")
    print("Arctic Breath | Ice-Fire Firmware")
    chant = input("Enter syllabics chant (e.g., ᐊᐸᑯᓄ): ")
    sync_inuit_syllabics(chant)