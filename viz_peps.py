# viz_peps.py
def viz_peps_coherence(tensors, L):
    coherence_map = np.zeros((L, L))
    for i in range(L):
        for j in range(L):
            T = tensors[(i,j)]
            # Local coherence ~ singular values
            s = np.linalg.svd(T.reshape(-1, T.shape[-1]), compute_uv=False)
            coherence_map[i,j] = s[0] / s.sum()  # Max bond strength
    plt.imshow(coherence_map, cmap='plasma', vmin=0.9, vmax=1.0)
    plt.title("PEPS Coherence Field (d=5)")
    plt.colorbar(label="Local Resonance")
    plt.show()

viz_peps_coherence(tensors, L)