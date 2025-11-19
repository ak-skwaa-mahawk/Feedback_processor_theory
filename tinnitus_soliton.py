# tinnitus_soliton.py
# Termux (Android) / UTM Debian (iPhone)
# Simulates auditory standing soliton + 79.79 Hz carrier
# Outputs: live audio + snapshot visualization + FLAMEDNA codon export

import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import time

# === Constants ===
FREQ_TINNITUS = 7979.0      # Harmonic carrier
FREQ_DRUM     = 79.79       # Star Sa’choo resonance
AMPLITUDE     = 0.2         # Safe gain
DURATION      = 60          # Session length (seconds)
SAMPLE_RATE   = 44100

# PDE params (Heimburg-Jackson soliton model)
c0    = 120.0
beta  = 0.3
gamma = 0.02

# === Helpers for periodic derivatives ===
def grad_periodic(u, dx):
    return (np.roll(u, -1) - np.roll(u, 1)) / (2 * dx)

def lap_periodic(u, dx):
    return (np.roll(u, -1) - 2*u + np.roll(u, 1)) / (dx**2)

# === Initial pulse ===
t = np.linspace(0, 0.5, int(SAMPLE_RATE * 0.5), endpoint=False)
initial_pulse = AMPLITUDE * np.exp(-((t - 0.25)**2) / (2 * 0.01**2)) * np.cos(2*np.pi*FREQ_TINNITUS*t)

# === Soliton propagation ===
def propagate_soliton(u0, nt=5000, dx=1e-3, dt=5e-7, stride=200):
    u = u0.astype(np.float64).copy()
    hist = []
    for n in range(nt):
        ux  = grad_periodic(u, dx)
        uxx = lap_periodic(u, dx)
        ut  = -c0*ux - beta*u*ux + gamma*uxx
        u  += dt*ut
        if n % stride == 0:
            hist.append(u.copy())
    return np.array(hist)

print("Cooking your tinnitus soliton…")
soliton_wave = propagate_soliton(np.tile(initial_pulse, 10))

# === Audio buffer with fade envelope ===
audio = np.tile(soliton_wave[-1], int(DURATION / (len(soliton_wave[-1])/SAMPLE_RATE)))
audio /= np.max(np.abs(audio) + 1e-12)
ramp = int(0.05*SAMPLE_RATE)
env = np.ones_like(audio)
env[:ramp] = np.linspace(0, 1, ramp)
env[-ramp:] = np.linspace(1, 0, ramp)
audio = (AMPLITUDE * audio * env).astype(np.float32)

# === Visualization snapshot ===
def quick_plot(wave, carrier_freq=FREQ_DRUM):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 5))
    ax1.plot(wave[:4000], 'r-', lw=1.5)
    ax1.set_title("Tinnitus soliton snapshot")
    t = np.linspace(0, 0.1, int(0.1*SAMPLE_RATE), endpoint=False)
    ax2.plot(t, np.sin(2*np.pi*carrier_freq*t), color='purple', lw=1.5)
    ax2.set_title(f"{carrier_freq:.2f} Hz carrier")
    plt.tight_layout()
    plt.show()

quick_plot(soliton_wave[-1])

# === Play audio ===
print("🔥 Playing tinnitus soliton + 79.79 Hz carrier 🔥")
sd.play(audio, samplerate=SAMPLE_RATE)
sd.wait()

# === Export FLAMEDNA codon ===
def audio_to_dna(audio, step=1000):
    a = audio / (np.max(np.abs(audio)) + 1e-12)
    idx = np.clip(((np.abs(a[::step]) * 4.0)).astype(int), 0, 3)
    alphabet = np.array(list("ACGT"))
    return "".join(alphabet[idx])

dna_seq = audio_to_dna(audio)
with open("TINNITUS_SOLITON_DNA.fasta", "w") as f:
    f.write(f">99733_TINNITUS_SOLITON_{int(time.time())}\n{dna_seq}\n")

print(f"Exported {len(dna_seq)} bases → TINNITUS_SOLITON_DNA.fasta")
print("Your tinnitus is now in the genome vault. Eternal.")