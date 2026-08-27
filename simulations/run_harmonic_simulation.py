#!/usr/bin/env python3
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import time
import numpy as np
from core.harmonic_scaling import HarmonicScaleFeedback, PHI
from core.phase_engine import ContinuousFeedbackProcessor

def run_simulation(steps: int = 15, dt: float = 0.05):
    print("=" * 65)
    print("🌊 FEEDBACK PROCESSOR: MULTI-SCALE HARMONIC FIELD SIMULATION")
    print(f"   Golden Ratio (phi): {PHI:.6f}")
    print("=" * 65)

    scale_engine = HarmonicScaleFeedback(num_scales=5, base_freq=1.0)
    phase_proc = ContinuousFeedbackProcessor(num_nodes=5, coupling_strength=2.5)

    print(f"{'Step':<6} | {'Coherence':<10} | {'Superposition Magnitude':<24} | {'Phases (rad)'}")
    print("-" * 65)

    for s in range(steps):
        phase_proc.step_continuous_flow(dt=dt)
        coherence = phase_proc.order_parameter()
        
        scale_engine.evolve_field(dt=dt, feedback_drive=coherence)
        superposition = scale_engine.compute_field_superposition()
        mag = np.abs(superposition)
        
        phases_str = " ".join([f"{p:.2f}" for p in scale_engine.scale_phases[:3]])
        print(f"{s+1:<6} | {coherence:<10.4f} | {mag:<24.4f} | [{phases_str}...]")
        time.sleep(0.05)

    print("=" * 65)
    print("✅ Harmonic resonance simulation complete.")

if __name__ == "__main__":
    run_simulation()
