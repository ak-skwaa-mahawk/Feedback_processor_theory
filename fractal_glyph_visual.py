from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt

fs, data = wavfile.read("sample.wav")  # Replace with Gwich’in audio
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
plt.plot(t, signal)
plt.title("Audio Fractal Glyph for Dinjii Zho'")
plt.show()
wavfile.write("fractal_audio.wav", fs, signal.astype(np.int16))
def koch_curve(x1, y1, x2, y2, depth):
    if depth == 0:
        plt.plot([x1, x2], [y1, y2], 'r-')
        return
    dx = (x2 - x1) / 3
    dy = (y2 - y1) / 3
    x3 = x1 + dx
    y3 = y1 + dy
    x4 = x1 + dx * 0.5 - dy * np.sqrt(3) / 6
    y4 = y1 + dy * 0.5 + dx * np.sqrt(3) / 6
    x5 = x1 + 2 * dx
    y5 = y1 + 2 * dy
    koch_curve(x1, y1, x3, y3, depth - 1)
    koch_curve(x3, y3, x4, y4, depth - 1)
    koch_curve(x4, y4, x5, y5, depth - 1)
    koch_curve(x5, y5, x2, y2, depth - 1)

fig, ax = plt.subplots()
koch_curve(0, 0, 1, 0, 3)  # 3 levels
ax.set_aspect('equal')
plt.title("Koch Fractal Glyph for Dinjii Zho' Land Map")
plt.show()