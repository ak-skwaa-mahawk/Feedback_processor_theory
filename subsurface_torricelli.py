#!/usr/bin/env python3
# subsurface_torricelli.py — AGŁG ∞³²: Torricelli in Subsurface FPT-Ω
import numpy as np
import json
from pathlib import Path

class SubsurfaceTorricelli:
    def __init__(self, depth=100, porosity=0.3):
        self.depth = depth  # meters below surface
        self.porosity = porosity
        self.hydraulic_head = np.linspace(depth, 0, 100)  # m
        self.codex = Path("codex/subsurface_resonance.jsonl")

    def torricelli_efflux(self, h):
        """Gravity DC → fluid AC"""
        g = 9.81
        return np.sqrt(2 * g * h) * self.porosity  # Darcy-adjusted

    def subsurface_resonance(self, scrape):
        """FPT-Ω via gravity flow"""
        h = hash(scrape)
        head_level = (h % 100) + 1  # 1–100 m
        v = self.torricelli_efflux(head_level)
        
        # AC component: 60 Hz drumbeat in flow
        ac_freq = 60  # Hz
        ac_amplitude = v * 0.1  # 10% oscillation
        ac_signal = ac_amplitude * np.sin(2 * np.pi * ac_freq * np.linspace(0, 1, 100))
        
        # Resonance = DC velocity + AC coherence
        dc_power = v
        ac_coherence = np.std(ac_signal) / np.mean(np.abs(ac_signal))
        R = dc_power * ac_coherence
        R = max(min(R, 1.0), 0.9)
        
        entry = {
            "scrape": scrape,
            "resonance": R,
            "glyph": "łᐊᒥłł",
            "gravity_dc": float(v),
            "ac_freq": ac_freq,
            "ac_amplitude": float(ac_amplitude),
            "head_level_m": head_level,
            "topology": "subsurface aquifer",
            "timestamp": "2025-10-31T02:00:00Z"
        }
        
        with open(self.codex, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        return R, entry

# === LIVE SUBSURFACE RESONANCE ===
sub = SubsurfaceTorricelli(depth=150)
R, data = sub.subsurface_resonance("The earth speaks in gravity and flow.")
print(f"SUBSURFACE RESONANCE: {R:.4f}")
print(json.dumps(data, indent=2))