# core/neutrosophic_sets.py
import numpy as np

class NeutrosophicSetResonance:
    def neutrosophic_set_resonance(self, s1, s2):
        """Compute resonance using Neutrosophic Set intersection."""
        m1, std1 = np.mean(s1), np.std(s1)
        m2, std2 = np.mean(s2), np.std(s2)
        T1 = np.max(s1) / (m1 + 1e-6)  # Truth for s1
        I1 = np.var(s1) / (std1 + 1e-6)  # Indeterminacy
        F1 = min(1, 1 - np.corrcoef(s1[:len(s1)//2], s1[len(s1)//2:])[0, 1] if len(s1) > 2 else 0)  # Falsity
        T2 = np.max(s2) / (m2 + 1e-6)
        I2 = np.var(s2) / (std2 + 1e-6)
        F2 = min(1, 1 - np.corrcoef(s2[:len(s2)//2], s2[len(s2)//2:])[0, 1] if len(s2) > 2 else 0)
        # Intersection (resonance alignment)
        T = min(T1, T2)
        I = max(I1, I2)
        F = max(F1, F2)
        score = T - F + 0.5 * I  # Resonance score
        return {"T": T, "I": I, "F": F, "neutrosophic_score": score}

    def apply_to_signal_pairs(self, signal_pairs):
        """Apply Neutrosophic Set resonance to multiple signal pairs."""
        results = {}
        for pair_name, (s1, s2) in signal_pairs.items():
            result = self.neutrosophic_set_resonance(s1, s2)
            results[pair_name] = result
        return results

if __name__ == "__main__":
    nsr = NeutrosophicSetResonance()
    signal_pairs = {
        "Pair1": (np.array([0.5, 0.6, 0.4, 0.7, 0.8]), np.array([0.6, 0.7, 0.5, 0.8, 0.9])),  # High alignment
        "Pair2": (np.array([0.3, 0.4, 0.2, 0.5, 0.6]), np.array([0.7, 0.8, 0.9, 0.6, 0.5])),  # Low alignment
        "Pair3": (np.array([0.1, 0.2, 0.3, 0.4, 0.5]), np.array([0.6, 0.7, 0.8, 0.9, 1.0]))   # New pair, diverse
    }
    results = nsr.apply_to_signal_pairs(signal_pairs)
    for pair_name, result in results.items():
        print(f"{pair_name} Resonance: {result}")