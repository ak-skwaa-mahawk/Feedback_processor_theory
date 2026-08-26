import numpy as np

PHI = (1.0 + np.sqrt(5.0)) / 2.0

class HarmonicScaleFeedback:
    """
    Couples circular phase rotation with recursive geometric scaling (Golden Ratio phi)
    to process continuous field harmonics across hierarchical octaves.
    """
    def __init__(self, num_scales: int = 5, base_freq: float = 1.0):
        self.num_scales = num_scales
        self.phi = PHI
        # Exponential geometric octave frequencies: f_k = f_0 * phi^k
        self.scale_frequencies = base_freq * (self.phi ** np.arange(num_scales))
        self.scale_phases = np.zeros(num_scales, dtype=np.float64)

    def evolve_field(self, dt: float = 0.01, feedback_drive: float = 0.0) -> np.ndarray:
        """
        Evolves multi-scale wave dynamics with recursive cross-scale feedback.
        """
        # Cross-scale coupling matrix weighted by inverse geometric distance
        n = self.num_scales
        idx = np.arange(n)
        dist_matrix = np.abs(idx[:, None] - idx[None, :])
        coupling_weights = 1.0 / (self.phi ** dist_matrix)
        np.fill_diagonal(coupling_weights, 0.0)

        phase_diffs = self.scale_phases[None, :] - self.scale_phases[:, None]
        hierarchical_pull = np.sum(coupling_weights * np.sin(phase_diffs), axis=1) / n

        # d(theta_k)/dt = omega_k + feedback_drive * cos(theta_k) + inter-scale coupling
        d_theta = self.scale_frequencies + (feedback_drive * np.cos(self.scale_phases)) + hierarchical_pull
        self.scale_phases = np.mod(self.scale_phases + d_theta * dt, 2 * np.pi)
        return self.scale_phases

    def compute_field_superposition(self) -> complex:
        """Computes the instantaneous complex wave interference pattern across all scales."""
        scale_weights = 1.0 / (np.sqrt(self.phi) ** np.arange(self.num_scales))
        complex_waves = scale_weights * np.exp(1j * self.scale_phases)
        return complex(np.sum(complex_waves))
