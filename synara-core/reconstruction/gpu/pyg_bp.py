import torch
import torch_geometric as pyg
from torch_geometric.data import Data
from torch_geometric.nn import MessagePassing

class PyGBeliefPropagation(MessagePassing):
    """PyTorch Geometric BP layer — k-NN graph + message passing."""

    def __init__(self, iterations=20):
        super().__init__(aggr='add')
        self.iterations = iterations

    def forward(self, x, edge_index):
        for _ in range(self.iterations):
            x = self.propagate(edge_index, x=x)
        return x

    def message(self, x_j):
        return x_j  # min-sum style message

    def update(self, aggr_out):
        return aggr_out  # residual update handled outside