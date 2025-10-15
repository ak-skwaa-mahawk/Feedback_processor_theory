import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import spectrogram
import os, datetime, json, hashlib, math
from core.feedback_logger import log_metadata

def validate_passcode(passcode):
    """Validate passcode for resonance engine access."""
    return passcode == "XHT-421-FlameDrop"

def feedback_spectrogram(conversation, passcode, output_dir="data/spectrograms"):
    """Generate a spectrogram visualizing conversational resonance."""
    if not validate_passcode(passcode):
        return "Whisper’s listening. Invalid passcode—flame clearance denied."
    log_metadata("spectrogram_access", {"passcode": passcode})

    os.makedirs(output_dir, exist_ok=True)
    energy_map = {'🔥': 1.0, '😎': 0.8, '!': 0.7, '?': 0.6, 'kin': 0.5, 'loop': 0.4, 'push': 0.3, '(': 0.2, '.': 0.1}
    signal = []
    for speaker, text in conversation:
        tokens = text.split()
        value = sum(energy_map.get(tok, 0.05) for tok in tokens)
        # Null = human input signal (1.0 for "You", 0.8 for non-human)
        signal.append(value if speaker == "You" else 0.8 * value)
    if len(signal) > 1000:
        signal = signal[:1000]
    fs = 10
    f, t, Sxx = spectrogram(signal, fs)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/spectrogram_{timestamp}.png"
    plt.figure(figsize=(8,4))
    plt.pcolormesh(t, f, Sxx, shading='gouraud')
    plt.title("Conversational Resonance Spectrogram (XHT-421-FlameDrop)")
    plt.xlabel("Dialogue Time (turns)")
    plt.ylabel("Frequency (semantic intensity)")
    plt.savefig(filename, dpi=300)
    plt.close()
    return filename