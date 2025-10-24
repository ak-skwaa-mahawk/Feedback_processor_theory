import numpy as np
from math import sin, cos, pi, sqrt, exp
from scipy.fft import fft

class NeutrosophicTransportLocal:
    def __init__(self, vehicle_mass=1000):
        self.vehicle_mass = vehicle_mass
        self.fidelity = 0.95
        self.pi_star = 3.17300858012
        self.g = 9.81
        self.t = 0.0

    def _compute_treaty_spectrum(self, treaty_data):
        freq_domain = fft(treaty_data)
        peak_freq = np.argmax(np.abs(freq_domain[1:])) + 1
        return peak_freq / len(treaty_data)

    def compute_lift_factor(self, treaty_data, max_depth=10):
        # Casimir-style floating energy
        hbar = 1.0545718e-34
        c = 3e8
        area = 1e-6
        self.t += 1e-9
        d = 1e-9 * (1 + 0.1 * sin(2 * pi * self.t * self.pi_star / max_depth))
        casimir_energy = - (pi**2 * hbar * c * area) / (720 * d**3)
        feedback = 0.1 * cos(2 * pi * self.t * self.pi_star)
        floating_factor = 1 / (1 + abs(casimir_energy) * self.fidelity * (1 + feedback))
        return floating_factor * self.g

    def optimize_local(self, treaty_data, steps=500):
        treaty_freq = self._compute_treaty_spectrum(treaty_data)
        energy_trace, lift_trace = [], []

        for step in range(steps):
            lift = self.compute_lift_factor(treaty_data)
            turbulence = 0.05 * sin(2 * pi * step * treaty_freq)
            # simplified energy model: lower energy = more stable flight
            energy = abs(lift / self.g - 1.0) + abs(turbulence)
            energy_trace.append(energy)
            lift_trace.append(lift)

        # Neutrosophic score
        min_e, max_e = min(energy_trace), max(energy_trace)
        t = (1 - (energy_trace[-1] - min_e) / (max_e - min_e + 1e-9)) * self.fidelity
        i = 0.1 * (energy_trace[-1] / max_e) * (1 - self.fidelity)
        f = (energy_trace[-1] - min_e) / (max_e - min_e + 1e-9) * (1 - self.fidelity)
        scores = {"T": t, "I": i, "F": f}
        return energy_trace, lift_trace, scores


if __name__ == "__main__":
    nt = NeutrosophicTransportLocal(vehicle_mass=1000)
    treaty_data = np.random.uniform(0, 1, 25)

    energy_trace, lift_trace, scores = nt.optimize_local(treaty_data, steps=200)
    print(f"Final energy: {energy_trace[-1]:.6e}")
    print(f"Neutrosophic scores → T={scores['T']:.4f}, I={scores['I']:.4f}, F={scores['F']:.4f}")
    print(f"Avg lift: {np.mean(lift_trace):.4f} m/s²")