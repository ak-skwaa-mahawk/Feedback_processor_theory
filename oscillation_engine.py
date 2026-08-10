# oscillation_engine.py
# Physical Vibration via Neutrosophic Resonance

import numpy as np
import sounddevice as sd
from scipy.signal import chirp

def emit_land_vibration(T, I, F, duration=3.0, freq_range=[40, 200]):
    """
    T = Truth (ancestral fire)
    I = Indeterminacy (wind, river, breath)
    F = Falsehood (external noise)
    """
    score = T - 0.5*I - F
    if score < 0.3:
        return "BLOCKED: Low resonance"
    
    # Map T/I/F to physical frequency
    base_freq = 60 + (T * 100)  # 60–160 Hz (earth pulse)
    mod_freq = 5 + (I * 10)     # 5–15 Hz (breath rhythm)
    noise_amp = F * 0.3         # Suppress falsehood
    
    t = np.linspace(0, duration, int(44100 * duration))
    signal = (1 - noise_amp) * chirp(t, f0=base_freq, f1=base_freq + 20, t1=duration, method='linear')
    signal += noise_amp * np.random.normal(0, 0.1, len(t))
    
    # PLAY PHYSICAL VIBRATION
    sd.play(signal, 44100)
    sd.wait()
    
    return f"VIBRATION EMITTED: {base_freq:.1f} Hz @ {score:.2f} resonance"

# TEST
print(emit_land_vibration(T=0.9, I=0.2, F=0.1))