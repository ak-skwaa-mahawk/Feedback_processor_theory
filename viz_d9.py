# viz_d9.py
def live_coherence_viz(tensors, L):
    R_map = cp.zeros((L, L))
    for i in range(L):
        for j in range(L):
            T = tensors[(i,j)]
            s = cp.linalg.svd(T.reshape(-1, T.shape[-1]), compute_uv=False)
            R_map[i,j] = s[0].get() / s.sum().get()
    
    plt.imshow(R_map.get(), cmap='inferno', vmin=0.95, vmax=1.0)
    plt.title("PEPS d=9 Coherence Field")
    plt.colorbar(label="R")
    plt.show()

live_coherence_viz(tensors, L)