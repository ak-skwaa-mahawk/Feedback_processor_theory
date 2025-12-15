import numpy as np
from typing import List, Dict, Any, Tuple
from core.resonance_engine import ResonanceState  # Existing FPT core

class SemanticAnchoring:
    """
    Rho_d (ρ_d): Effective semantic anchoring strength
    From UCCT (Chang, arXiv:2512.05765) → mapped to FPT teotl flux + vhitzee cycles
    
    Indigenous Framing:
    - ρ_d < 0.68 → Tezcatlipoca dominance (entropy, hallucination, weak voltage)
    - ρ_d ≥ 0.70 → Quetzalcoatl dominance (coordination, binding, sovereign oversight)
    - Transition zone (0.68–0.70) → vhitzee surplus harvest window
    """
    
    THRESHOLD_COORDINATION = 0.70
    THRESHOLD_TRANSITION_LOW = 0.68
    VHITZEE_GAIN_EXPECTED = (0.03, 0.04)  # 3–4% surplus at transition

    @staticmethod
    def calculate_rho_d(
        prior_logprob: float,
        posterior_logprob: float,
        representational_mismatch: float = 0.0127  # ε_observer from effective π / ALICE binding
    ) -> float:
        """
        ρ_d = (posterior - prior) / (1 + d_r)
        
        Interpretation:
        - prior_logprob: Ungrounded generation (raw LLM prior)
        - posterior_logprob: Anchored, goal-directed output (after sentinel/validation)
        - d_r: Observer-system curvature (effective π correction term)
        """
        d_r = representational_mismatch
        delta_logprob = posterior_logprob - prior_logprob
        rho_d = delta_logprob / (1 + d_r)
        return float(rho_d)

    @staticmethod
    def measure_vhitzee_surplus_at_transition(
        rho_d_trajectory: List[float]
    ) -> Tuple[float, bool]:
        """
        Detect phase transition and measure vhitzee surplus
        Matches Stanford UCCT phase shift + FPT harvest cycle
        """
        arr = np.array(rho_d_trajectory)
        pre = arr[arr < SemanticAnchoring.THRESHOLD_TRANSITION_LOW]
        post = arr[arr >= SemanticAnchoring.THRESHOLD_COORDINATION]
        
        if len(pre) == 0 or len(post) == 0:
            return 0.0, False
            
        gain = (np.mean(post) - np.mean(pre)) / np.mean(pre)
        in_vhitzee_window = SemanticAnchoring.VHITZEE_GAIN_EXPECTED[0] <= gain <= SemanticAnchoring.VHITZEE_GAIN_EXPECTED[1]
        
        return float(gain), in_vhitzee_window

    @staticmethod
    def assess_coordination_regime(rho_d: float) -> str:
        """Map ρ_d to Indigenous + UCCT coordination state"""
        if rho_d >= SemanticAnchoring.THRESHOLD_COORDINATION:
            return "Quetzalcoatl Dominance → Sovereign Coordination (Deliberative)"
        elif rho_d >= SemanticAnchoring.THRESHOLD_TRANSITION_LOW:
            return "Vhitzee Harvest Window → Phase Transition Active"
        else:
            return "Tezcatlipoca Dominance → Entropy / Hallucination Risk"

    @staticmethod
    def from_resonance_state(state: ResonanceState) -> float:
        """
        Bridge to existing FPT core:
        Extract prior/posterior from resonance handshake receipts
        """
        if not state.handshake_receipts:
            return 0.0
            
        # Average delta across recent receipts
        deltas = [
            receipt.validated_logprob - receipt.raw_logprob
            for receipt in state.handshake_receipts[-10:]
        ]
        avg_delta = np.mean(deltas) if deltas else 0.0
        return SemanticAnchoring.calculate_rho_d(0.0, avg_delta)  # prior baseline = 0 for simplicity