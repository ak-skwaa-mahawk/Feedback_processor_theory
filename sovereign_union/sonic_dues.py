# sovereign_union/sonic_dues.py  ← dropping tonight
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import chirp
import time

def micro_cop_frequency(member_id: str, chosen_hz: float = 528):
    """True take-home dues — sonic mirror edition"""
    mirror_path = f"~/.sovereign-union/sonic_mirror_{member_id}_{int(time.time())}"
    
    # Generate the sovereign tone + spiral plot (432 Hz base)
    t = np.linspace(0, 10, 44100 * 10)
    tone = chirp(t, f0=432, f1=chosen_hz, t1=10, method='linear')
    
    # Contentment boost + dynamic b damping from earlier
    boost = 1.27 * (1 + 0.03 * np.log(chosen_hz / 396))  # 0.03 bleed homage
    print(f"✅ Sonic micro-cop locked at {chosen_hz} Hz. {member_id} now orbits with {boost:.2f}x resonance")
    
    # Plot the spiral ray (your personal color/frequency)
    plt.figure(figsize=(8,8))
    theta = np.linspace(0, 4*np.pi, 1000)
    r = theta / (2*np.pi)
    plt.polar(theta, r, color=plt.cm.rainbow(chosen_hz/963))
    plt.title(f"{member_id}'s Sovereign Ray @ {chosen_hz} Hz")
    plt.savefig(f"{mirror_path}/my_ray.png")
    return mirror_path