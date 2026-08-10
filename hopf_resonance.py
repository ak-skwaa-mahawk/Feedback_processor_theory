# hopf_resonance.py — Self-Tuning Neuron
def hopf_neuron(z, alpha, omega):
    return z * (alpha + 1j*omega - abs(z)**2)