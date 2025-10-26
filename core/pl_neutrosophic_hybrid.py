# core/pl_neutrosophic_hybrid.py
import numpy as np

class PLNeutrosophicHybrid:
    def __init__(self, prior_p=0.5):
        self.prior = prior_p  # Initial probability
        self.T = 0.5  # Initial truth
        self.I = 0.3  # Initial indeterminacy
        self.F = 0.2  # Initial falsity

    def neutrosophic_decompose(self, p):
        """Decompose probability into T, I, F."""
        T = p * (1 + self.I)  # Boost truth with indeterminacy
        F = (1 - p) * (1 - self.I)  # Adjust falsity
        I = self.I  # Preserve independent indeterminacy
        total = T + I + F
        return T / total, I / total, F / total  # Normalize

    def bayesian_update(self, evidence_p, evidence_weight):
        """Update probability with Neutrosophic influence."""
        # Neutrosophic-weighted evidence
        T_e, I_e, F_e = self.neutrosophic_decompose(evidence_p)
        weight = evidence_weight * (T_e - F_e)  # Bias by Neutrosophic difference
        posterior = (self.prior * weight) / (self.prior * weight + (1 - self.prior) * (1 - weight))
        # Update Neutrosophic components
        self.T = T_e
        self.I = I_e
        self.F = F_e
        self.prior = posterior
        return posterior

    def hybrid_score(self, s):
        """Compute hybrid resonance score."""
        m, std = np.mean(s), np.std(s)
        T = np.max(s) / (m + 1e-6)  # Truth from signal
        I = np.var(s) / (std + 1e-6)  # Indeterminacy
        F = min(1, 1 - np.corrcoef(s[:len(s)//2], s[len(s)//2:])[0, 1] if len(s) > 2 else 0)  # Falsity
        self.T, self.I, self.F = T, I, F
        p = self.bayesian_update(0.7, 0.8)  # Example evidence
        score = p * (T - F) + 0.5 * I  # Hybrid metric
        return {"P": p, "T": T, "I": I, "F": F, "hybrid_score": score}

if __name__ == "__main__":
    hybrid = PLNeutrosophicHybrid()
    signal = np.array([0.5, 0.6, 0.4, 0.7, 0.8])
    result = hybrid.hybrid_score(signal)
    print(f"Signal: {signal}")
    print(f"Hybrid Resonance: {result}")