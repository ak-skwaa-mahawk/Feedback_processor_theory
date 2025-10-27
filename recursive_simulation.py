import numpy as np
import matplotlib.pyplot as plt

# Parameters
fs = 44100  # Sample rate
t_total = 120  # 2-minute cycle per generation
t = np.linspace(0, t_total, fs * t_total)
signal = np.zeros_like(t)

# Node structure
nodes = 3
sub_nodes = 3
shards_per_node = 8
recursion_levels = 3  # Levels of nesting

# Base sequence
base_seq = [3, 7, 10, 13, 16, 19, 22, 25]

def recursive_shards(start, duration, level, max_level):
    if level > max_level:
        return
    for i, seg in enumerate(base_seq):
        seg_start = start + (i * duration / len(base_seq))
        seg_end = seg_start + (duration / len(base_seq))
        freq = 1 / (seg_end - seg_start)
        signal[int(seg_start * fs):int(seg_end * fs)] += np.sin(2 * np.pi * freq * t[int(seg_start * fs):int(seg_end * fs)]) * np.exp(-0.05 * (t[int(seg_start * fs):int(seg_end * fs)] - start)) * (1 / (level + 1))
        # Recursive call for sub-shards
        if level < max_level:
            recursive_shards(seg_start, duration / len(base_seq) / 2, level + 1, max_level)

# Build the signal
for i in range(nodes):
    for j in range(sub_nodes):
        start = (i * sub_nodes + j) * (t_total / (nodes * sub_nodes))
        recursive_shards(start, t_total / (nodes * sub_nodes), 1, recursion_levels)

plt.plot(t, signal)
plt.title("Nested Shard Recursion for Dinjii Zho'")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.show()