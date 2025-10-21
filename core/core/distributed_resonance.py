# core/distributed_resonance.py
def sparse_coupling(self, adjacency_matrix: np.ndarray):
    self.graph = nx.from_numpy_array(adjacency_matrix)
    self.K = self.K / self.graph.degree.mean()  # Normalize by connectivity