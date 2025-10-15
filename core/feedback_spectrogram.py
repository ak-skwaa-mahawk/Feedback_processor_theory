import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import spectrogram
import os, datetime, json

def feedback_spectrogram(conversation, output_dir="data/spectrograms"):
    os.makedirs(output_dir, exist_ok=True)

    energy_map = {
        '🔥': 1.0, '😎': 0.8, '!': 0.7, '?': 0.6,
        'kin': 0.5, 'loop': 0.4, 'push': 0.3,
        '(': 0.2, '.': 0.1
    }

    signal = []
    for speaker, text in conversation:
        base = 1.0 if speaker == "You" else 0.8
        strength = sum(energy_map.get(c, 0.05) for c in text.split())
        signal.append(base * strength)

    fs = 10
    f, t, Sxx = spectrogram(signal, fs)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/spectrogram_{timestamp}.png"

    plt.figure(figsize=(8,4))
    plt.pcolormesh(t, f, Sxx, shading='gouraud')
    plt.title("Conversational Resonance Spectrogram")
    plt.xlabel("Dialogue Time (turns)")
    plt.ylabel("Frequency (semantic intensity)")
    plt.savefig(filename, dpi=300)
    plt.close()

    return filename