import numpy as np

class ContinuousFeedbackProcessor:
    def __init__(self, num_nodes: int = 8, natural_freqs: np.ndarray = None, coupling_strength: float = 0.5):
        self.num_nodes = num_nodes
        self.coupling_k = coupling_strength
        self.omega = natural_freqs if natural_freqs is not None else np.random.uniform(0.8, 1.2, num_nodes)
        self.phases = np.random.uniform(0, 2 * np.pi, num_nodes)

    def step_continuous_flow(self, dt: float = 0.01) -> np.ndarray:
        """
        Integrates continuous phase interaction:
        d(theta_i)/dt = omega_i + (K/N) * sum_j sin(theta_j - theta_i)
        """
        phase_diffs = self.phases[None, :] - self.phases[:, None]
        coupling_term = np.sum(np.sin(phase_diffs), axis=1) * (self.coupling_k / self.num_nodes)
        
        # Continuous phase evolution
        d_theta = self.omega + coupling_term
        self.phases = np.mod(self.phases + d_theta * dt, 2 * np.pi)
        return self.phases

    def order_parameter(self) -> float:
        """Computes phase coherence (1.0 = fully phase-locked, 0.0 = completely incoherent)."""
        complex_order = np.mean(np.exp(1j * self.phases))
        return float(np.abs(complex_order))
