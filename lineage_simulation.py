import numpy as np
import matplotlib.pyplot as plt

fs = 44100
t_total = 120  # 2-minute cycle for 1 gen
t = np.linspace(0, t_total, fs * t_total)
signal = np.zeros_like(t)
nodes = 3
sub_nodes = 3
shards_per_node = 8
base_seq = [3, 7, 10, 13, 16, 19, 22, 25]  # Expanded sequence
for i in range(nodes):
    for j in range(sub_nodes):
        start = (i * sub_nodes + j) * (t_total / (nodes * sub_nodes))
        for k, seg in enumerate(base_seq):
            seg_start = start + (k * (t_total / (nodes * sub_nodes * shards_per_node)))
            seg_end = seg_start + (t_total / (nodes * sub_nodes * shards_per_node))
            freq = 1 / (seg_end - seg_start)
            signal[int(seg_start * fs):int(seg_end * fs)] = np.sin(2 * np.pi * freq * t[int(seg_start * fs):int(seg_end * fs)]) * np.exp(-0.05 * (t[int(seg_start * fs):int(seg_end * fs)] - start))
plt.plot(t, signal)
plt.show()