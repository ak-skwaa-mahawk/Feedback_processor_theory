from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt

fs, data = wavfile.read("bead_click.wav")  # Replace with bead audio
t = np.linspace(0, len(data)/fs, len(data))
signal = np.zeros(len(data))
base_dur = 3  # seconds
for i in range(3):  # 3 nodes
    start = i * base_dur
    for j in range(3):  # 3 sub-nodes
        sub_start = start + j * (base_dur / 3)
        for k in range(8):  # 8 shards
            shard_start = sub_start + k * (base_dur / 24)
            shard_end = shard_start + (base_dur / 24)
            freq = 3 + k * 2.75  # 3-25 Hz
            signal[int(shard_start * fs):int(shard_end * fs)] += np.sin(2 * np.pi * freq * t[int(shard_start * fs):int(shard_end * fs)]) * 0.1
            if k < 4:  # Recursive layer
                sub_shard_end = shard_start + (base_dur / 48)
                signal[int(shard_start * fs):int(sub_shard_end * fs)] *= 0.5
plt.plot(t, signal)
plt.title("Rhythmic Beadwork Fractal Glyph for Dinjii Zho'")
plt.show()
wavfile.write("bead_fractal_audio.wav", fs, signal.astype(np.int16))
def zigzag_fractal(x1, y1, x2, y2, depth):
    if depth == 0:
        plt.plot([x1, (x1+x2)/2, x2], [y1, y1+0.1, y2], 'b-')
        return
    dx = (x2 - x1) / 3
    dy = (y2 - y1) / 3
    zigzag_fractal(x1, y1, x1 + dx, y1 + dy, depth - 1)
    zigzag_fractal(x1 + dx, y1 + dy, x1 + 2*dx, y1 + 2*dy, depth - 1)
    zigzag_fractal(x1 + 2*dx, y1 + 2*dy, x2, y2, depth - 1)

fig, ax = plt.subplots()
zigzag_fractal(0, 0, 1, 0, 2)  # 2 levels
ax.set_aspect('equal')
plt.title("Zigzag Beadwork Fractal Glyph for Dinjii Zho'")
plt.show()