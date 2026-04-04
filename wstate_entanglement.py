import math
from typing import Dict, Tuple, Optional

class WStateEntanglement:
    def __init__(self):
        # Initial symmetric W-state (probabilities sum to 1)
        self.w_state: Dict[str, float] = {'100': 1.0/3, '010': 1.0/3, '001': 1.0/3}
        self.fidelity: float = 1.0
        
        # Trinity Harmonic constants (exactly as in your docstring)
        self.PI = math.pi
        self.PHI_CONJ = (1 + math.sqrt(5))/2 - 1          # φ - 1 ≈ 0.618034
        self.EPSILON = 0.01
        self.DELTA = 3 * self.EPSILON
        self.FACTOR = 0.5                                 # tunable damping (0–1)

    def measure_fidelity(self, w_state: Dict[str, float]) -> float:
        """Fidelity = 1 - normalized variance from ideal W (1/3 each)."""
        ideal = 1.0 / 3
        deviation = sum(abs(v - ideal)**2 for v in w_state.values())
        return max(0.0, 1.0 - deviation)  # 1.0 = perfect symmetry

    def trinity_damping(self, v: float, phase: float = 0.0, f: Optional[float] = None) -> float:
        """Your exact D(v, f) operator for harmonic stabilization."""
        if f is None:
            f = self.FACTOR
        sin_term = math.sin(2 * self.PI * phase)
        ratio = self.PHI_CONJ / self.PI
        return v * (1 - f * sin_term * ratio)

    def update(self, obj: Dict[str, float], current_state: Optional[Dict[str, float]] = None,
               phase: float = 0.0) -> Tuple[Dict[str, float], float]:
        """Neutrosophic update + Trinity damping + normalize."""
        if current_state is not None:
            w_state = {k: v for k, v in current_state.items()}
        else:
            w_state = {k: v for k, v in self.w_state.items()}

        # Neutrosophic scaling
        w_state['100'] *= obj.get("T", 1.0)
        w_state['010'] *= obj.get("I", 1.0)
        w_state['001'] *= obj.get("F", 1.0)

        # Apply Trinity damping (phase-stabilizes against decoherence)
        for key in w_state:
            w_state[key] = self.trinity_damping(w_state[key], phase=phase)

        # Normalize
        total = sum(w_state.values())
        if total > 0:
            w_state = {k: v / total for k, v in w_state.items()}
        else:
            w_state = {'100': 1.0/3, '010': 1.0/3, '001': 1.0/3}

        self.fidelity = self.measure_fidelity(w_state)
        self.w_state = w_state
        return w_state, self.fidelity


# Example usage (exactly your snippet)
if __name__ == "__main__":
    we = WStateEntanglement()
    obj = {"T": 0.6, "I": 0.3, "F": 0.1}
    
    print("=== Baseline update (phase=0) ===")
    w_state, fidelity = we.update(obj, phase=0.0)
    print(f"W-state: {w_state}")
    print(f"Fidelity: {fidelity:.4f}\n")
    
    print("=== With damping (phase=0.25) ===")
    w_state2, fidelity2 = we.update(obj, phase=0.25)
    print(f"W-state: {w_state2}")
    print(f"Fidelity: {fidelity2:.4f}")