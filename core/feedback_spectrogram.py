"""
Feedback Spectrogram Engine
Maps conversational text into frequency bands with XHT-421-FlameDrop passcode gate.
Author: John Carroll / Two Mile Solutions LLC
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import spectrogram
import json, os, datetime, hashlib, math
from typing import Dict, List, Optional

def validate_passcode(passcode: str) -> bool:
    """Validate passcode for resonance engine access."""
    return passcode == "XHT-421-FlameDrop"

def log_metadata(event: str, data: Dict, output_dir: str = "data/resonance_logs") -> str:
    """Log metadata with π-scaled hashed passcode."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    passcode = data.get("passcode", "")
    hashed = hashlib.sha256((passcode + str(math.pi)).encode()).hexdigest()
    data.update({
        "hashed_passcode": hashed,
        "event": event,
        "timestamp": timestamp,
        "pi_feedback_constant": math.pi
    })
    file_path = f"{output_dir}/metadata_{timestamp}.json"
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
    return file_path

class FeedbackSpectrogram:
    """Converts text into 3-band resonance analysis with passcode gate."""
    def __init__(self, output_dir: str = "data/resonance_logs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "../spectrograms"), exist_ok=True)

    def analyze(self, text: str, passcode: str) -> Dict[str, List[float]]:
        """Analyze text with passcode validation."""
        if not validate_passcode(passcode):
            raise ValueError("Whisper’s listening. Invalid passcode—flame clearance denied.")
        log_metadata("spectrogram_access", {"passcode": passcode}, self.output_dir)

        tokens = text.split()
        if not tokens:
            return {"low": [], "mid": [], "high": []}

        # Low: Thematic flow (with π-scaling for stability)
        window_size = min(20, max(3, len(tokens) // 10))
        kernel = np.ones(window_size) * math.pi / window_size
        signal = np.array([hash(t) % 100 for t in tokens])
        low = np.convolve(signal, kernel, mode="same")

        # Mid: Semantic rhythm
        mid = np.array([len(t) % 10 for t in tokens])

        # High: Emotional intensity (Null = human signal)
        energy_map = {'🔥': 1.0, '😎': 0.8, '!': 0.7, '?': 0.6, 'kin': 0.5, 'loop': 0.4}
        high = np.array([
            sum(energy_map.get(c, 0.05) for c in t) + 
            (1.0 if "You" in t else 0.8)  # Null human signal
            for t in tokens
        ])

        return {"low": low.tolist(), "mid": mid.tolist(), "high": high.tolist()}

    def plot(self, freq_data: Dict[str, List[float]], filename: str = "spectrogram.png") -> str:
        """Generate spectrogram plot."""
        plt.figure(figsize=(12, 6))
        if freq_data["low"]:
            plt.subplot(3, 1, 1)
            plt.plot(freq_data["low"], color='#2E86AB')
            plt.title("Low Frequency (Themes, π-scaled)")
            plt.subplot(3, 1, 2)
            plt.plot(freq_data["mid"], color='#A23B72')
            plt.title("Mid Frequency (Semantics)")
            plt.subplot(3, 1, 3)
            plt.plot(freq_data["high"], color='#F18F01')
            plt.title("High Frequency (Tone, Null-human)")
            plt.xlabel("Token Position")
        plt.tight_layout()
        outpath = os.path.join(self.output_dir, "../spectrograms", filename)
        plt.savefig(outpath, dpi=150)
        plt.close()
        return outpath

    def log(self, text: str, passcode: str, meta: Optional[Dict] = None) -> str:
        """Analyze, plot, and log with passcode."""
        freq_data = self.analyze(text, passcode)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        entry = {
            "timestamp": timestamp,
            "text_preview": text[:200] + "..." if len(text) > 200 else text,
            "token_count": len(text.split()),
            "analysis": freq_data,
            "meta": meta or {},
            "pi_feedback_constant": math.pi
        }
        json_path = f"{self.output_dir}/resonance_{timestamp}.json"
        with open(json_path, "w") as f:
            json.dump(entry, f, indent=4)
        self.plot(freq_data, f"spectrogram_{timestamp}.png")
        return json_path