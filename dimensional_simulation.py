import numpy as np
import matplotlib.pyplot as plt

fs = 44100
t_total = 60  # 1-minute cycle
t = np.linspace(0, t_total, fs * t_total)
signal = np.zeros_like(t)
gens = 8
seg_per_gen = 7.5  # seconds per generation
for gen in range(gens):
    start = gen * seg_per_gen
    for i, seg in enumerate([2.5, 2.5, 2.5]):  # 3 shards
        seg_start = start + i * (seg_per_gen / 3)
        seg_end = seg_start + (seg_per_gen / 3)
        freq = 1 / (seg_per_gen / 3)  # Shard frequency
        signal[int(seg_start * fs):int(seg_end * fs)] = np.sin(2 * np.pi * freq * t[int(seg_start * fs):int(seg_end * fs)]) * np.exp(-0.1 * (t[int(seg_start * fs):int(seg_end * fs)] - start))
plt.plot(t, signal)
plt.show()