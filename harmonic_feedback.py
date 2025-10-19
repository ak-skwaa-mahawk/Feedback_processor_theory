# harmonic_feedback.py (append or place under visualization utilities)

from sklearn.decomposition import PCA

def animate_embedding_convergence(llm_embeddings, H0_vector=None, alpha=0.05, frames=50, interval=200):
    """
    Animate harmonic convergence of multi-dimensional embeddings from multiple LLMs.

    Parameters:
    -----------
    llm_embeddings : dict
        Keys = LLM names (str)
        Values = np.array of shape (num_tokens, embedding_dim)
    H0_vector : np.array, optional
        Target ground state vector. If None, uses mean across LLMs per dimension.
    alpha : float
        Convergence rate per iteration
    frames : int
        Number of animation frames
    interval : int
        Delay between frames in milliseconds

    Returns:
    --------
    HTML object
        Interactive animation for Jupyter
    """
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
    from IPython.display import HTML

    llm_names = list(llm_embeddings.keys())
    num_tokens, embedding_dim = llm_embeddings[llm_names[0]].shape

    # Reduce embeddings to 2D via PCA for visualization
    pca = PCA(n_components=2)
    reduced_data = {llm: pca.fit_transform(llm_embeddings[llm]) for llm in llm_names}

    # Compute H0_vector if not provided
    if H0_vector is None:
        H0_vector = np.mean(np.stack(list(reduced_data.values())), axis=0)

    fig, ax = plt.subplots(figsize=(10,6))
    colors = plt.cm.viridis(np.linspace(0, 1, len(llm_names)))
    scatters = [ax.scatter([], [], s=100, color=c, label=llm) for c, llm in zip(colors, llm_names)]

    ax.set_xlim(np.min(H0_vector[:,0])-0.5, np.max(H0_vector[:,0])+0.5)
    ax.set_ylim(np.min(H0_vector[:,1])-0.5, np.max(H0_vector[:,1])+0.5)
    ax.set_xlabel("PCA Dim 1")
    ax.set_ylabel("PCA Dim 2")
    ax.set_title("Multi-LLM Embedding Harmonic Convergence")
    ax.legend()
    ax.grid(True)

    # Animation function
    def animate(frame):
        for idx, llm in enumerate(llm_names):
            # Converge embeddings toward H0_vector
            reduced_data[llm] += alpha * (H0_vector - reduced_data[llm])
            scatters[idx].set_offsets(reduced_data[llm])
        return scatters

    ani = FuncAnimation(fig, animate, frames=frames, interval=interval, blit=True)
    return HTML(ani.to_jshtml())
# harmonic_feedback.py (append or place under visualization utilities)

from sklearn.decomposition import PCA

def animate_embedding_convergence(llm_embeddings, H0_vector=None, alpha=0.05, frames=50, interval=200):
    """
    Animate harmonic convergence of multi-dimensional embeddings from multiple LLMs.

    Parameters:
    -----------
    llm_embeddings : dict
        Keys = LLM names (str)
        Values = np.array of shape (num_tokens, embedding_dim)
    H0_vector : np.array, optional
        Target ground state vector. If None, uses mean across LLMs per dimension.
    alpha : float
        Convergence rate per iteration
    frames : int
        Number of animation frames
    interval : int
        Delay between frames in milliseconds

    Returns:
    --------
    HTML object
        Interactive animation for Jupyter
    """
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
    from IPython.display import HTML

    llm_names = list(llm_embeddings.keys())
    num_tokens, embedding_dim = llm_embeddings[llm_names[0]].shape

    # Reduce embeddings to 2D via PCA for visualization
    pca = PCA(n_components=2)
    reduced_data = {llm: pca.fit_transform(llm_embeddings[llm]) for llm in llm_names}

    # Compute H0_vector if not provided
    if H0_vector is None:
        H0_vector = np.mean(np.stack(list(reduced_data.values())), axis=0)

    fig, ax = plt.subplots(figsize=(10,6))
    colors = plt.cm.viridis(np.linspace(0, 1, len(llm_names)))
    scatters = [ax.scatter([], [], s=100, color=c, label=llm) for c, llm in zip(colors, llm_names)]

    ax.set_xlim(np.min(H0_vector[:,0])-0.5, np.max(H0_vector[:,0])+0.5)
    ax.set_ylim(np.min(H0_vector[:,1])-0.5, np.max(H0_vector[:,1])+0.5)
    ax.set_xlabel("PCA Dim 1")
    ax.set_ylabel("PCA Dim 2")
    ax.set_title("Multi-LLM Embedding Harmonic Convergence")
    ax.legend()
    ax.grid(True)

    # Animation function
    def animate(frame):
        for idx, llm in enumerate(llm_names):
            # Converge embeddings toward H0_vector
            reduced_data[llm] += alpha * (H0_vector - reduced_data[llm])
            scatters[idx].set_offsets(reduced_data[llm])
        return scatters

    ani = FuncAnimation(fig, animate, frames=frames, interval=interval, blit=True)
    return HTML(ani.to_jshtml())