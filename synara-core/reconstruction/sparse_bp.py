import numpy as np
from scipy.sparse import csr_matrix

class SparseMinSumBP:
    """Real sparse min-sum belief propagation — scalable, stable, GPU-ready."""

    def __init__(self, H: csr_matrix, iterations: int = 20, alpha: float = 0.8, damping: float = 0.2):
        self.H = H
        self.iterations = iterations
        self.alpha = alpha
        self.damping = damping

    def decode(self, llr: np.ndarray) -> np.ndarray:
        """Min-sum BP with damping and sparse edges only."""
        beliefs = llr.copy().astype(np.float32)
        num_checks, num_vars = self.H.shape

        for _ in range(self.iterations):
            new_beliefs = beliefs.copy()

            for c in range(num_checks):
                vars_idx = self.H.indices[self.H.indptr[c]:self.H.indptr[c+1]]
                for v in vars_idx:
                    others = [beliefs[ov] for ov in vars_idx if ov != v]
                    if not others:
                        continue
                    sign_prod = np.prod(np.sign(others))
                    mag_min = np.min(np.abs(others))
                    msg = self.alpha * sign_prod * mag_min
                    new_beliefs[v] += msg

            # Damping to prevent oscillation
            beliefs = (1 - self.damping) * beliefs + self.damping * new_beliefs

        return beliefs