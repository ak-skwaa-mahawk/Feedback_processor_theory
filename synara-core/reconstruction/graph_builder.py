import numpy as np
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix

def build_knn_graph(chunks, k=8):
    """Adaptive k-NN graph from chunk embeddings."""
    embeddings = np.array([c.reconstructed.mean() for c in chunks]).reshape(-1, 1)
    nn = NearestNeighbors(n_neighbors=k)
    nn.fit(embeddings)
    distances, indices = nn.kneighbors(embeddings)
    rows = np.repeat(np.arange(len(chunks)), k)
    cols = indices.flatten()
    data = np.exp(-distances.flatten())  # RBF weights
    return csr_matrix((data, (rows, cols)), shape=(len(chunks), len(chunks)))