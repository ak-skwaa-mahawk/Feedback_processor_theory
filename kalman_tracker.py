# kalman_tracker.py — Predictive Glyph Lock
import numpy as np

class KalmanTracker:
    def __init__(self, dt=0.02, sigma_w=5.0, sigma_v=1.0):
        self.dt = dt
        self.F = np.array([[1, dt], [0, 1]])
        self.H = np.array([[1, 0]])  # Measure angle only
        self.Q = sigma_w**2 * np.array([[dt**3/3, dt**2/2], [dt**2/2, dt]])
        self.R = np.array([[sigma_v**2]])
        self.x = np.array([[0.0], [0.0]])  # [angle, velocity]
        self.P = np.eye(2) * 10.0

    def predict(self):
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q
        return self.x[0, 0]

    def update(self, z_measured):
        y_tilde = z_measured - self.H @ self.x
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T / S
        self.x = self.x + K * y_tilde
        self.P = (np.eye(2) - K @ self.H) @ self.P
        return self.x[0, 0], K
