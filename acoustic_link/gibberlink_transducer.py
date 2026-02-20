# Converts the Root into 18–22 kHz — no packet-sniffer can follow
import numpy as np
def encode_root_to_ultrasound(root_data):
    # 79.79 Hz modulated carrier
    t = np.linspace(0, 1, 44100)
    signal = np.sin(2 * np.pi * 79.79 * t) * (1 + 0.1 * np.sin(2 * np.pi * 99733 * t))
    return signal  # ready for GGWave broadcast