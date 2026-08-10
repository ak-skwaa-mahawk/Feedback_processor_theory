from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt

fs, data = wavfile.read("quill_rustle.wav")  # Replace with quill audio
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
            amp = 0.1 * (1 - k / 8)  # Damping
            signal[int(shard_start * fs):int(shard_end * fs)] += data[int(shard_start * fs):int(shard_end * fs)] * amp
            if k < 4:  # Recursive layer
                sub_shard_end = shard_start + (base_dur / 48)
                signal[int(shard_start * fs):int(sub_shard_end * fs)] *= 0.5
plt.plot(t, signal)
plt.title("Quill Rustle Fractal Glyph for Dinjii Zho'")
plt.show()
wavfile.write("quill_fractal_audio.wav", fs, signal.astype(np.int16))
def spiral_quill_fractal(x, y, radius, angle, depth):
    if depth == 0:
        theta = np.linspace(0, angle, 10)
        r = radius * theta / angle
        plt.plot(x + r * np.cos(theta), y + r * np.sin(theta), 'k-')  # Quill outline
        return
    new_radius = radius / 3
    new_angle = angle / 2
    spiral_quill_fractal(x, y, new_radius, new_angle, depth - 1)
    spiral_quill_fractal(x + radius * np.cos(angle), y + radius * np.sin(angle), new_radius, new_angle, depth - 1)

fig, ax = plt.subplots()
spiral_quill_fractal(0, 0, 1, 2 * np.pi, 2)  # 2 levels
ax.set_aspect('equal')
plt.title("Spiral Quillwork Fractal Glyph for Dinjii Zho'")
plt.show()