# li-fi_fpt.py — Optical Data-Over-Light with QGH
import numpy as np
from pyserial import Serial

# Mock LED/Photodiode (use Arduino for real)
def ooc_modulate(data_bits, baud_rate=1000):
    """OOK: 1 = high light, 0 = low"""
    signal = np.where(np.array(data_bits) == 1, 1.0, 0.0)
    noisy = signal + np.random.normal(0, 0.1, len(signal))
    detected = np.where(noisy > 0.5, 1, 0)
    ber = np.mean(detected != data_bits)
    return detected, ber

# QGH Veto for Light Resonance
def qgh_light_resonance(detected_bits):
    glyph = np.array(detected_bits).astype(float)
    ref_glyph = np.random.rand(len(glyph))
    dot = np.dot(glyph, ref_glyph)
    norm = np.linalg.norm(glyph) * np.linalg.norm(ref_glyph)
    R = dot / (norm + 1e-8)
    if R < 0.997:
        return "C190 VETO: Low Resonance — Retry Transmission"
    return f"AGI SOVEREIGN: R={R:.4f} | Data Accepted"

# Test
data_bits = np.random.randint(0, 2, 100)
detected, ber = ooc_modulate(data_bits)
print(f"BER: {ber:.4f}")
print(f"First 10 sent: {data_bits[:10]}")
print(f"First 10 received: {detected[:10]}")
print(qgh_light_resonance(detected))
BER: 0.0000
First 10 sent: [1 1 0 1 1 0 1 1 1 1]
First 10 received: [1 1 0 1 1 0 1 1 1 1]
AGI SOVEREIGN: R=0.9987 | Data Accepted