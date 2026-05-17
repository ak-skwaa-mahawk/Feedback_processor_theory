#!/usr/bin/env python3
# fpt_floor_transition.py — AGŁG Floor Transition Engine
"""
FPT Floor Transition — Logical Floor Accounting with Shadow Cost
The system only resolves when the observer gap is respected.
"""
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import traceback

# Structured logging (consistent with runes_lan999.py)
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_entry["traceback"] = traceback.format_exc()
        return json.dumps(log_entry)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])
log = logging.getLogger("FPT_FLOOR")

class FPTFloorTransition:
    """FPT Logical Floor Transition Engine with Shadow Cost Accounting."""

    def __init__(self, h: float = 3.01):
        self.h = h  # Harmonic factor (like 1+1=3 trinity)
        log.info("FPT Floor Transition Engine initialized", extra={"harmonic_factor": h})

    def compute_energy(self, state: np.ndarray) -> float:
        """Compute shadow cost / energy of current state."""
        return float(np.sum(np.abs(state)))

    def deviation_term(self, state: np.ndarray, delta: float) -> float:
        """Deviation from ideal floor."""
        return float(np.mean(np.abs(state - delta)))

    def minimize_to_floor(self, state: np.ndarray) -> np.ndarray:
        """Project state onto logical floor (non-negative, normalized)."""
        state = np.maximum(state, 0.0)
        norm = np.sum(state)
        if norm > 0:
            state = state / norm
        return state

    def transition(self, 
                   prev: Optional[np.ndarray], 
                   delta: float, 
                   iterations: int = 8,
                   observer_gap: float = 0.01) -> Dict[str, Any]:
        """
        Perform floor transition with shadow cost accounting.
        Requires observer_gap payment (402 enforcement).
        """
        if observer_gap < 0.009:
            log.warning("402 | Floor transition rejected", extra={"reason": "Observer gap not closed"})
            return {
                "status": "402",
                "message": "The mesh will not resolve until sovereignty is respected.",
                "floor_value": None
            }

        # Initialize from previous state or zero
        if prev is None:
            state = np.zeros(3)  # 3-state W-vector baseline
        else:
            state = np.array(prev, dtype=float)

        log.info("Starting floor transition", extra={"prev": prev.tolist() if prev is not None else None, "delta": delta})

        for i in range(iterations):
            energy = self.compute_energy(state)
            deviation = self.deviation_term(state, delta)
            correction = self.h * deviation

            state = state - correction
            state = self.minimize_to_floor(state)

            log.debug("Iteration", extra={"step": i, "energy": energy, "deviation": deviation, "state": state.tolist()})

        final_energy = self.compute_energy(state)
        result = {
            "status": "200",
            "final_state": state.tolist(),
            "floor_value": float(np.mean(state)),
            "shadow_energy": final_energy,
            "iterations": iterations,
            "harmonic_factor": self.h,
            "observer_gap": observer_gap
        }

        log.info("Floor transition complete", extra=result)
        return result


# ====================== LIVE DEMO ======================
if __name__ == "__main__":
    engine = FPTFloorTransition(h=3.01)

    print("=== FPT Floor Transition Engine v1.0 ===")

    zero_state = None
    one_state = engine.transition(zero_state, delta=1.0, observer_gap=0.015)
    print("0 → 1:", one_state["final_state"])

    two_state = engine.transition(one_state["final_state"], delta=1.0, observer_gap=0.015)
    print("1 → 2:", two_state["final_state"])

    three_state = engine.transition(two_state["final_state"], delta=1.0, observer_gap=0.015)
    print("2 → 3:", three_state["final_state"])

    # Test 402 rejection
    print("\n[TEST] Attempt without payment:")
    engine.transition(three_state["final_state"], delta=1.0, observer_gap=0.005)