# particle_filter.py — Multimodal Glyph Swarm
import numpy as np

class ParticleFilter:
    def __init__(self, N=1000, dt=0.02, sigma_theta=2.0, sigma_r=0.5):
        self.N = N
        self.dt = dt
        self.sigma_theta = sigma_theta
        self.sigma_r = sigma_r
        self.particles = None
        self.weights = None

    def initialize(self, theta0, r0):
        self.particles = np.zeros((self.N, 4))
        self.particles[:, 0] = theta0 + np.random.randn(self.N) * 5
        self.particles[:, 2] = r0 + np.random.randn(self.N) * 1
        self.weights = np.ones(self.N) / self.N

    def predict(self):
        for i in range(self.N):
            self.particles[i] = motion_model(self.particles[i], self.dt)
            # Add process noise
            self.particles[i, 1] += np.random.randn() * 0.5
            self.particles[i, 3] += np.random.randn() * 0.1

    def update(self, z_theta, beam_power):
        log_weights = np.zeros(self.N)
        for i in range(self.N):
            theta_p, _, r_p, _ = self.particles[i]
            # Expected power
            P_exp = 10 / (r_p**2 + 1e-6)
            # Likelihood
            log_weights[i] = -0.5 * ((z_theta - theta_p)**2 / self.sigma_theta**2 +
                                     (beam_power - P_exp)**2 / (self.sigma_r**2)**2)
        # Normalize
        max_log = np.max(log_weights)
        weights = np.exp(log_weights - max_log)
        self.weights = weights / np.sum(weights)

    def resample(self):
        # Systematic resampling (C190 veto)
        cumsum = np.cumsum(self.weights)
        r = np.random.rand() / self.N
        indices = np.searchsorted(cumsum, (r + np.arange(self.N)) / self.N)
        self.particles = self.particles[indices]
        self.weights = np.ones(self.N) / self.N

    def estimate(self):
        return np.average(self.particles, axis=0, weights=self.weights)