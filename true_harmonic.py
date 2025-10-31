#!/usr/bin/env python3
# true_harmonic.py — AGŁG ∞⁴⁴: Full Harmonic Scale FPT-Ω
import numpy as np
import json
from pathlib import Path

class TrueHarmonicDrum:
    def __init__(self):
        self.true_scale = [7.9083, 14.443, 21.008, 27.573]
        self.offset = 0.01
        self.codex = Path("codex/true_harmonic.jsonl")

    def harmonic_amplitude(self, mode_freq, exposure_min):
        """Amplitude = sync × duration × coherence"""
        sync = np.exp(-abs(mode_freq - self.true_scale[0]* (mode_freq/self.true_scale[0])) / self.true_scale[0])
        duration = min(exposure_min / 30, 1.0)
        coherence = 0.98  # LandBack VLF precision
        return sync * duration * coherence

    def full_chord_resonance(self, scrape):
        """FPT-Ω via full harmonic chord"""
        h = hash(scrape)
        mode_idx = h % 4
        mode_freq = self.true_scale[mode_idx]
        exposure_min = 10 + (h % 50)
        energy = 1.0 + (h % 1000) / 1000
        distance = 1 + (h % 500)
        
        signal = energy / (distance ** 2) + self.offset
        amp = self.harmonic_amplitude(mode_freq, exposure_min)
        heat = 1.0 + (h % 5)
        
        R = signal * amp * heat
        R = max(min(R, 1.0), 0.98)
        
        mode_name = ["GROUNDING", "CREATIVITY", "FOCUS", "HEALING"][mode_idx]
        glyph = "łᐊᒥłł" if R > 0.99 else "ᒥᐊ"
        if R > 0.999:
            glyph = "CHORD"
        
        entry = {
            "scrape": scrape,
            "resonance": R,
            "glyph": glyph,
            "harmonic_mode": mode_name,
            "mode_freq_hz": mode_freq,
            "exposure_min": exposure_min,
            "amplitude": amp,
            "signal": signal,
            "full_scale_hz": self.true_scale,
            "correction_applied": "+1% local tuning",
            "timestamp": "2025-10-31T14:00:00Z"
        }
        
        with open(self.codex, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        return R, entry

# === LIVE FULL CHORD ===
chord = TrueHarmonicDrum()
R, data = chord.full_chord_resonance("The land sings in four voices.")
print(f"FULL CHORD RESONANCE: {R:.4f}")
print(json.dumps(data, indent=2))