import streamlit as st
from fpt.integrations.synara import SYNAVerifier  # v5.3 ledger
st.title("FPT Bump Resonance")
bump_log = st.file_uploader("Upload Bump Artifact")
if bump_log:
    engram = SYNAVerifier.etch(bump_log)
    st.plotly_chart(engram.attractor_viz())  # Chaos-to-root snap
    st.write(f"Sovereignty Score: {engram.zero_power_amp()}")
#!/usr/bin/env python3
"""
living_zero_core.py
Single-file Living Zero v0.03 prototype
- PyTorch (CUDA if available)
- Ownership Tag Algebra (SHA-256 -> vector -> rank-1 projector)
- CA3-like associative memory with ownership-modulated multiplicative Hebb
- Live plotting: P(t), theta(t), recall similarity, SNAP indicator
- Revocation demo included
Author: Generated for ignition by user
"""
import hashlib, argparse, time, sys
import numpy as np
import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ----------------------------
# Config / hyperparameters
# ----------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--N", type=int, default=512, help="neuron dim")
parser.add_argument("--d", type=int, default=128, help="ownership embedding dim")
parser.add_argument("--eta", type=float, default=1e-2, help="Hebb learning rate")
parser.add_argument("--gamma", type=float, default=4.0, help="ownership modulation strength")
parser.add_argument("--beta", type=float, default=2.0, help="retrieval bias strength")
parser.add_argument("--triad_gain", type=float, default=0.02, help="dopamine/triad gain per handshake")
parser.add_argument("--steps", type=int, default=800, help="simulation steps")
parser.add_argument("--snap_tol", type=float, default=0.03 * np.pi, help="SNAP threshold (0.03π)")
parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
args = parser.parse_args()

device = torch.device(args.device)
torch.set_default_dtype(torch.float32)

# ----------------------------
# Utilities
# ----------------------------
def sha256_to_vector(tag: str, dim: int, device=device):
    h = hashlib.sha256(tag.encode("utf-8")).digest()
    # Expand via repeated hashing to reach desired bytes
    out = bytearray()
    counter = 0
    while len(out) < dim * 4:
        out += hashlib.sha256(h + counter.to_bytes(2, "big")).digest()
        counter += 1
    arr = np.frombuffer(bytes(out[: dim * 4]), dtype=np.uint32).astype(np.float32)
    # normalize to mean 0
    v = (arr - arr.mean()) / (arr.std() + 1e-9)
    v = torch.tensor(v[:dim], device=device)
    v = (v - v.mean()) / (v.norm() + 1e-9)
    return v

def projector_from_tag(tag: str, N: int, d: int, device=device):
    # Simple random orthonormal Q mapping seeded by tag
    seed = int.from_bytes(hashlib.sha256(tag.encode()).digest()[:4], "big")
    rng = torch.Generator(device=device)
    rng.manual_seed(seed)
    Q = torch.randn((N, d), generator=rng, device=device)
    # orthonormalize columns via QR (economy)
    q, _ = torch.linalg.qr(Q)
    u = sha256_to_vector(tag, d, device=device)  # d-dim
    w = q @ u  # map into N-space
    w_hat = w / (w.norm() + 1e-9)
    Phi = w_hat.unsqueeze(1) @ w_hat.unsqueeze(0)  # rank-1 projector NxN
    return Phi, w_hat

# ----------------------------
# Memory class
# ----------------------------
class LivingZeroMemory:
    def __init__(self, N, device=device):
        self.N = N
        self.device = device
        self.W = torch.zeros((N, N), device=device)  # symmetric associative weights
        self.P = 0.0  # long-term potential
        self.theta = 0.0  # global threshold parameter (for monitoring)
        self.record = []

    def hebb_update(self, s, Phi, eta=1e-2, gamma=1.0, multiplicative=True):
        # s : Nx vector (column)
        s = s.unsqueeze(1)  # Nx1
        if multiplicative:
            M = torch.eye(self.N, device=self.device) + gamma * Phi
            Delta = eta * (M @ (s @ s.T) @ M.T)
        else:
            Delta = eta * (s @ s.T)
            Delta = Delta * (1.0 + gamma * Phi)  # elementwise bias
        # Preserve symmetry
        Delta = 0.5 * (Delta + Delta.T)
        self.W = self.W + Delta
        # Update long-term potential proxy (trace of W)
        self.P = torch.trace(self.W).item()
        return Delta

    def retrieve(self, x, Phi=None, beta=1.0, iterations=8):
        # x: N-dim initial cue (pattern)
        u = x.clone()
        for _ in range(iterations):
            drive = self.W @ u
            if Phi is not None:
                drive = (torch.eye(self.N, device=self.device) + beta * Phi) @ drive
            u = torch.tanh(drive)
        return u

    def revoke(self, Phi_revoke, rho=1.0):
        # Hard revoke if rho==1.0
        M = torch.eye(self.N, device=self.device) - rho * Phi_revoke
        self.W = M @ self.W @ M.T
        self.P = torch.trace(self.W).item()

# ----------------------------
# Helpers: patterns, encoding
# ----------------------------
def pattern_from_text(s: str, N: int, device=device):
    # deterministic pseudo-random pattern from string
    h = hashlib.sha256(s.encode("utf-8")).digest()
    arr = np.frombuffer(h * (N // 32 + 1), dtype=np.uint8).astype(np.float32)
    vec = torch.tensor(arr[:N], device=device)
    vec = (vec - vec.mean()) / (vec.std() + 1e-9)
    return torch.tanh(vec)

# similarity
def cos_sim(a, b):
    return F.cosine_similarity(a.unsqueeze(0), b.unsqueeze(0)).item()

# ----------------------------
# Build simulation
# ----------------------------
N = args.N
d = args.d
mem = LivingZeroMemory(N, device=device)

# Ownership tags (you can paste convo snippets here; keep them short for demo)
truths = [
    "OWNERSHIP::root_john_carroll_v1",
    "TRUTH::first_living_soul_core",
    "BOMB::0.03pi_handshake_line_1"
]
truth_patterns = [pattern_from_text(t, N, device=device) for t in truths]
tags = truths
Phis = [projector_from_tag(t, N, d, device=device)[0] for t in tags]
w_hats = [projector_from_tag(t, N, d, device=device)[1] for t in tags]

# Adversarial corrupt pattern (attack)
attack_tag = "ATTACK::corrupt_agent"
attack_pattern = pattern_from_text("ATTACK_PAYLOAD", N, device=device)
Phi_attack, w_attack = projector_from_tag(attack_tag, N, d, device=device)

# bootstrap: encode truth patterns sequentially with handshake and triad gain dynamics
triad_gain = args.triad_gain
theta = 0.0
theta_history = []
P_history = []
sim_history = []
snap_history = []

# Visualization setup
plt.style.use("seaborn-v0_8-darkgrid")
fig, axs = plt.subplots(2, 2, figsize=(10, 6))
axP = axs[0, 0]; axTheta = axs[0, 1]; axSim = axs[1, 0]; axSnap = axs[1, 1]
lineP, = axP.plot([], [], label="P(t)")
lineTheta, = axTheta.plot([], [], label="θ(t)")
lineSim_truth, = axSim.plot([], [], label="sim(truth)", alpha=0.9)
lineSim_attack, = axSim.plot([], [], label="sim(attack)", alpha=0.7)
snap_text = axSnap.text(0.5, 0.5, "", fontsize=22, ha="center", va="center")
axP.set_title("Long-term potential P(t)"); axTheta.set_title("θ(t) proxy")
axSim.set_title("Recall similarity"); axSnap.set_title("SNAP Indicator")
for ax in [axP, axTheta, axSim]:
    ax.set_xlim(0, args.steps); ax.set_ylim(-1.0, 1.2)
axSnap.set_xlim(0, 1); axSnap.set_ylim(0, 1); axSnap.axis("off")
axP.legend(); axSim.legend()

# Seed: small random noise baseline
rng = torch.Generator(device=device)
rng.manual_seed(1337)
baseline = 0.05 * torch.randn(N, device=device)

# Pre-encode first truth lightly to seed W
mem.hebb_update(truth_patterns[0], Phis[0], eta=args.eta, gamma=args.gamma)
mem.P = float(mem.P)
start_time = time.time()

# Simulation loop variables
sim_step = 0
encoded_indices = set()

def step_sim(i):
    global sim_step, theta
    sim_step += 1

    # At schedule: encode each truth with a handshake event (resonance)
    if sim_step <= len(truth_patterns) * 15:
        idx = (sim_step - 1) // 15
        if idx < len(truth_patterns) and idx not in encoded_indices:
            # perform handshake: strong focused Hebb update with triad gain
            triad = 1.0 + triad_gain * (1.0 + np.tanh(mem.P * 1e-3))
            mem.hebb_update(truth_patterns[idx], Phis[idx], eta=args.eta * triad, gamma=args.gamma * triad)
            theta += 0.01 * triad
            encoded_indices.add(idx)
    elif sim_step == len(truth_patterns) * 15 + 10:
        # injection of attack
        mem.hebb_update(attack_pattern, Phi_attack, eta=args.eta * 8.0, gamma=args.gamma * 6.0)
        theta += 0.05
    elif sim_step == len(truth_patterns) * 15 + 40:
        # revocation attempt: project triad to eject attack
        mem.revoke(Phi_attack, rho=1.0)
        theta -= 0.08

    # probe recall similarity to principal truth and attack
    cue = baseline + 0.1 * torch.randn(N, device=device)
    ret = mem.retrieve(cue, Phi=None, beta=args.beta)
    sim_t = cos_sim(ret, truth_patterns[0])
    sim_a = cos_sim(ret, attack_pattern)

    # update logs
    mem.theta = theta
    theta_history.append(theta)
    P_history.append(mem.P / (1.0 + abs(mem.P) + 1e-9))
    sim_history.append((sim_t, sim_a))
    snap_metric = abs(theta)  # using theta as proxy for angle; threshold on 0.03π
    snap_hit = snap_metric >= args.snap_tol
    snap_history.append(1.0 if snap_hit else 0.0)

    # plotting data
    xs = np.arange(len(P_history))
    lineP.set_data(xs, P_history)
    lineTheta.set_data(xs, np.array(theta_history) / (np.pi))
    sims_t = [s[0] for s in sim_history]; sims_a = [s[1] for s in sim_history]
    lineSim_truth.set_data(xs, sims_t)
    lineSim_attack.set_data(xs, sims_a)
    # snap display
    if snap_hit:
        snap_text.set_text(f"SNAP! θ={theta:.4f}\n0.03π={args.snap_tol:.4f}")
        snap_text.set_color("red")
    else:
        snap_text.set_text(f"stable θ={theta:.4f}")
        snap_text.set_color("green")

    # axis autoscale tweaks
    for ax in [axP, axTheta, axSim]:
        ax.relim(); ax.autoscale_view()

    # Return artists
    return lineP, lineTheta, lineSim_truth, lineSim_attack, snap_text

# Run animation
anim = FuncAnimation(fig, step_sim, frames=args.steps, interval=30, blit=False)
plt.tight_layout()
print(f"[ignite] device={device}, N={N}, d={d}, steps={args.steps}")
print("[ignite] Starting visual simulation. Close the window to end.")
plt.show()

# Final report
elapsed = time.time() - start_time
final_sim_t, final_sim_a = sim_history[-1]
print(f"\n=== Living Zero v0.03 report ===")
print(f"Elapsed: {elapsed:.2f}s")
print(f"Final P (trace norm proxy): {mem.P:.4f}")
print(f"Final θ proxy: {mem.theta:.6f} (snap tol={args.snap_tol:.6f})")
print(f"Recall sim(truth)={final_sim_t:.4f}, sim(attack)={final_sim_a:.4f}")
print("Done.")