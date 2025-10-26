# core/pythagorean_fuzzy_sets.py
import numpy as np

class PythagoreanFuzzySet:
    def pythagorean_fuzzy_resonance(self, s1, s2):
        """Compute resonance using Pythagorean Fuzzy Set intersection."""
        m1, std1 = np.mean(s1), np.std(s1)
        m2, std2 = np.mean(s2), np.std(s2)
        mu1 = np.max(s1) / (m1 + 1e-6)  # Membership for s1
        nu1 = min(1, 1 - np.corrcoef(s1[:len(s1)//2], s1[len(s1)//2:])[0, 1] if len(s1) > 2 else 0)  # Non-membership
        if mu1**2 + nu1**2 > 1:  # Normalize if invalid
            norm = np.sqrt(mu1**2 + nu1**2)
            mu1, nu1 = mu1 / norm, nu1 / norm
        pi1 = np.sqrt(1 - mu1**2 - nu1**2)  # Hesitation
        mu2 = np.max(s2) / (m2 + 1e-6)
        nu2 = min(1, 1 - np.corrcoef(s2[:len(s2)//2], s2[len(s2)//2:])[0, 1] if len(s2) > 2 else 0)
        if mu2**2 + nu2**2 > 1:
            norm = np.sqrt(mu2**2 + nu2**2)
            mu2, nu2 = mu2 / norm, nu2 / norm
        pi2 = np.sqrt(1 - mu2**2 - nu2**2)
        # Intersection
        mu_int = np.sqrt(mu1**2 * mu2**2)
        nu_int = np.sqrt(nu1**2 + nu2**2 - nu1**2 * nu2**2)
        pi_int = np.sqrt(1 - mu_int**2 - nu_int**2)
        # Union
        mu_uni = np.sqrt(mu1**2 + mu2**2 - mu1**2 * mu2**2)
        nu_uni = np.sqrt(nu1**2 * nu2**2)
        pi_uni = np.sqrt(1 - mu_uni**2 - nu_uni**2)
        # Complement of s1
        mu_com = nu1
        nu_com = mu1
        pi_com = pi1
        # Scores
        score_int = mu_int - nu_int + 0.5 * pi_int
        score_uni = mu_uni - nu_uni + 0.5 * pi_uni
        score_com = mu_com - nu_com + 0.5 * pi_com
        return {
            "intersection": {"mu": mu_int, "nu": nu_int, "pi": pi_int, "score": score_int},
            "union": {"mu": mu_uni, "nu": nu_uni, "pi": pi_uni, "score": score_uni},
            "complement_s1": {"mu": mu_com, "nu": nu_com, "pi": pi_com, "score": score_com}
        }

    def test_pfs_operations(self):
        """Test PFS operations on signal pairs."""
        test_signals = [
            (np.array([0.5, 0.6, 0.4, 0.7, 0.8]), np.array([0.6, 0.7, 0.5, 0.8, 0.9])),  # High alignment
            (np.array([0.3, 0.4, 0.2, 0.5, 0.6]), np.array([0.7, 0.8, 0.9, 0.6, 0.5])),  # Low alignment
            (np.array([0.1, 0.2, 0.3, 0.4, 0.5]), np.array([0.6, 0.7, 0.8, 0.9, 1.0]))   # Diverse
        ]
        results = {}
        for i, (s1, s2) in enumerate(test_signals):
            result = self.pythagorean_fuzzy_resonance(s1, s2)
            results[f"Test {i+1}"] = result
        return results

if __name__ == "__main__":
    pfs = PythagoreanFuzzySet()
    results = pfs.test_pfs_operations()
    for test_name, result in results.items():
        print(f"{test_name} Results:")
        for op_name, op_result in result.items():
            print(f"  {op_name}: mu={op_result['mu']:.4f}, nu={op_result['nu']:.4f}, pi={op_result['pi']:.4f}, score={op_result['score']:.4f}")
        print()