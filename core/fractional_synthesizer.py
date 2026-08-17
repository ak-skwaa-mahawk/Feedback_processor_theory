import math
from typing import Tuple

class MASH111Modulator:
    """3rd-order Multi-stAge noise SHaping (MASH 1-1-1) digital delta-sigma modulator."""
    def __init__(self):
        self.acc1: float = 0.0
        self.acc2: float = 0.0
        self.acc3: float = 0.0

    def step(self, frac_word: float) -> Tuple[int, float]:
        self.acc1 += frac_word
        o1 = int(self.acc1)
        self.acc1 -= o1

        self.acc2 += self.acc1
        o2 = int(self.acc2)
        self.acc2 -= o2

        self.acc3 += self.acc2
        o3 = int(self.acc3)
        self.acc3 -= o3

        div_offset = o1 + o2 + o3
        quant_error = frac_word - div_offset
        return div_offset, quant_error

class DigitalFractionalNPhaseLock:
    """Type-II Software PLL with feed-forward digital phase-error cancellation."""
    def __init__(self, sample_rate_hz: float = 79.0, k_p: float = 0.042, k_i: float = 0.0018):
        self.dt = 1.0 / sample_rate_hz
        self.k_p = k_p
        self.k_i = k_i
        self.modulator = MASH111Modulator()
        self.integrator_state: float = 0.0
        self.nco_phase: float = 0.0
        self.spur_phase_accum: float = 0.0

    def process_tick(self, reference_phase: float, base_n: int, frac_k_m: float) -> dict:
        div_offset, quant_error = self.modulator.step(frac_k_m)
        self.spur_phase_accum = (self.spur_phase_accum + 2.0 * math.pi * quant_error * self.dt) % (2.0 * math.pi)

        raw_phase_error = reference_phase - self.nco_phase
        clean_phase_error = raw_phase_error - self.spur_phase_accum

        self.integrator_state += self.k_i * clean_phase_error
        control_freq = (self.k_p * clean_phase_error) + self.integrator_state

        inst_freq = base_n + frac_k_m + control_freq
        self.nco_phase = (self.nco_phase + 2.0 * math.pi * inst_freq * self.dt) % (2.0 * math.pi)

        return {
            "clean_phase_error": round(clean_phase_error, 6),
            "inst_freq": round(inst_freq, 6),
            "nco_phase": round(self.nco_phase, 4)
        }
