import numpy as np
from scipy.integrate import odeint

def kdv(u, t, L):
    ux = np.fft.ifft(1j * (2*np.pi*np.fft.fftfreq(len(u), d=L/len(u))) * np.fft.fft(u))
    uxx = np.fft.ifft(- (2*np.pi*np.fft.fftfreq(len(u), d=L/len(u)))**2 * np.fft.fft(u))
    uxxx = np.fft.ifft(1j * (2*np.pi*np.fft.fftfreq(len(u), d=L/len(u)))**3 * np.fft.fft(u))
    return -6 * u * ux - uxxx  # Real parts for integration

# Mystic input: Sun ray profile as soliton u0
x = np.linspace(-10, 10, 100)
u0 = 0.5 / np.cosh(x)**2  # Sech-squared soliton
L = 20  # Domain
t = np.linspace(0, 5, 50)  # Time steps

sol = odeint(kdv, u0, t, args=(L,))
initial_norm = np.linalg.norm(u0)
final_norm = np.linalg.norm(sol[-1])
assert abs(initial_norm - final_norm) < 1e-6, "Mystic invariance failed"
print("Mystic soliton stable: PASS")