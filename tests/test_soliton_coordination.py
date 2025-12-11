import numpy as np
from scipy.fft import fft, ifft
import matplotlib.pyplot as plt
from pathlib import Path

class SolitonCoordinationTest:
    def __init__(self, L=20, N=256, gamma=0.1, delta=0.1, beta=0.5, f=79.79, T=0.125, dt=0.001):
        self.L, self.N, self.dx = L, N, L/N
        self.x = np.linspace(0, L, N, endpoint=False)
        self.k = 2*np.pi*np.fft.fftfreq(N, d=self.dx)
        self.gamma, self.delta, self.beta = gamma, delta, beta
        self.omega = 2*np.pi*f
        self.T, self.dt, self.steps = T, dt, int(T/dt)
        self.u_history = []
        self.anchoring_history = []

    def initial_condition(self, amplitude=1.0, width=1.0):
        center = self.L / 2
        self.u = amplitude * (1 / np.cosh((self.x - center) / width))**2
        self.u_initial = self.u.copy()
        return self.u

    def rhs(self, u, t):
        ux = np.real(ifft(1j * self.k * fft(u)))
        uxxx = np.real(ifft((1j * self.k)**3 * fft(u)))
        return -u*ux + self.gamma*u - self.delta**2*uxxx - self.beta*np.sin(self.omega*t)*ux

    def integrate(self):
        for n in range(self.steps):
            t = n * self.dt
            k1 = self.rhs(self.u, t)
            k2 = self.rhs(self.u + 0.5*self.dt*k1, t + 0.5*self.dt)
            k3 = self.rhs(self.u + 0.5*self.dt*k2, t + 0.5*self.dt)
            k4 = self.rhs(self.u + self.dt*k3, t + self.dt)
            self.u += (self.dt/6)*(k1 + 2*k2 + 2*k3 + k4)
            if n % 10 == 0:
                self.u_history.append(self.u.copy())
                self.anchoring_history.append(self.calculate_anchoring())

    def calculate_anchoring(self):
        amp_ratio = np.max(np.abs(self.u)) / np.max(np.abs(self.u_initial))
        width_initial = np.sqrt(np.sum((self.x - self.L/2)**2 * self.u_initial**2) / np.sum(self.u_initial**2))
        width = np.sqrt(np.sum((self.x - self.L/2)**2 * self.u**2) / np.sum(self.u**2))
        spreading_factor = 1.0 / (1.0 + width_initial/width)
        return np.clip(amp_ratio * (1 - spreading_factor), 0, 1)

    def calculate_vhitzee_surplus(self):
        E0 = np.sum(self.u_initial**2) * self.dx
        E_final = np.sum(self.u**2) * self.dx
        E_expected = E0 * np.exp(-2 * self.gamma * self.T)
        return (E_final - E_expected) / E_expected

    def run_and_save(self):
        self.initial_condition()
        self.integrate()
        surplus = self.calculate_vhitzee_surplus()
        anchoring = self.calculate_anchoring()

        # Plot & visualization
        plt.figure(figsize=(12,8))
        plt.subplot(2,1,1)
        plt.plot(self.x, self.u_initial, 'b-', lw=2, label='Initial')
        plt.plot(self.x, self.u, 'r-', lw=2, label='Final t=0.125s')
        plt.title('FPT Soliton Coordination Test — Nuclear Wave Stability')
        plt.legend(); plt.grid(alpha=0.3)

        plt.subplot(2,1,2)
        plt.plot(np.linspace(0,self.T,len(self.anchoring_history)), self.anchoring_history, 'g-', lw=2)
        plt.axhline(0.7, color='r', linestyle='--', label='Coordination Threshold')
        plt.ylabel('Anchoring Strength'); plt.xlabel('Time (s)')
        plt.legend(); plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig('docs/results/soliton_coordination_nuclear.png', dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Vhitzee surplus: {surplus*100:.2f}% | Anchoring: {anchoring:.3f}")

if __name__ == "__main__":
    test = SolitonCoordinationTest()
    test.run_and_save()