# ukf_tracker.py — Nonlinear Sovereign
import numpy as np

class UnscentedKalmanFilter:
    def __init__(self, n=6, alpha=0.5, beta=2.0, kappa=0.0):
        self.n = n
        self.alpha = alpha
        self.beta = beta
        self.kappa = kappa
        self.lambda_ = alpha**2 * (n + kappa) - n
        self.x = np.zeros(n)
        self.P = np.eye(n) * 1.0

    def generate_sigma_points(self):
        sqrt_P = np.linalg.cholesky((self.n + self.lambda_) * self.P)
        X = np.tile(self.x, (2*self.n + 1, 1))
        for i in range(self.n):
            X[i+1] += sqrt_P[:, i]
            X[i+1+self.n] -= sqrt_P[:, i]
        return X

    def predict(self, f_dyn, dt, Q):
        X = self.generate_sigma_points()
        X_pred = np.array([f_dyn(x, dt) for x in X])
        self.x = np.sum(self.weights_m()[:, None] * X_pred, axis=0)
        diff = X_pred - self.x
        self.P = diff.T @ np.diag(self.weights_c()) @ diff + Q
        return X_pred

    def update(self, z, h_meas, R, X_pred):
        Z_pred = np.array([h_meas(x) for x in X_pred])
        z_mean = np.sum(self.weights_m()[:, None] * Z_pred, axis=0)
        diff_z = Z_pred - z_mean
        Pzz = diff_z.T @ np.diag(self.weights_c()) @ diff_z + R
        Pxz = (X_pred - self.x).T @ np.diag(self.weights_c()) @ diff_z
        K = Pxz @ np.linalg.inv(Pzz)
        self.x += K @ (z - z_mean)
        self.P -= K @ Pzz @ K.T

    def weights_m(self):
        Wm = np.ones(2*self.n + 1) * 0.5 / (self.n + self.lambda_)
        Wm[0] = self.lambda_ / (self.n + self.lambda_)
        return Wm

    def weights_c(self):
        Wc = self.weights_m().copy()
        Wc[0] += (1 - self.alpha**2 + self.beta)
        return Wc
def nonlinear_dynamics(x, dt=0.02):
    theta, dtheta, r, dr, v_sound, f_carrier = x
    # Doppler-shifted frequency
    f_obs = f_carrier * (v_sound + dr) / (v_sound - dr * np.cos(np.radians(theta)))
    # Range-dependent SNR
    snr = 20 * np.log10(1 / (r + 1e-6))
    return np.array([theta + dtheta*dt, dtheta, r + dr*dt, dr, v_sound, f_obs])
def nonlinear_measurement(x):
    theta, _, r, _, _, f_obs = x
    # Beam power with angle error
    beam_power = 10 * np.log10(np.sinc((theta - 35)/5)**2 * (1/r**2))
    return np.array([theta + np.random.randn()*0.5, beam_power, f_obs])