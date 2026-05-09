import torch
from torch_geometric.utils import scatter

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class CUDABeliefPropagation(torch.nn.Module):
    """CUDA-accelerated min-sum BP with scatter operations."""

    def __init__(self, edge_index, iterations=20, alpha=0.8, damping=0.2):
        super().__init__()
        self.edge_index = edge_index.to(device)
        self.iterations = iterations
        self.alpha = alpha
        self.damping = damping

    def forward(self, beliefs):
        beliefs = beliefs.to(device).float()
        for _ in range(self.iterations):
            # Message passing via scatter (min-sum style)
            msgs = beliefs[self.edge_index[1]]
            msgs = self.alpha * torch.sign(msgs) * torch.abs(msgs)
            agg_msgs = scatter(msgs, self.edge_index[0], dim=0, reduce="min")
            new_beliefs = beliefs + agg_msgs
            # Damping
            beliefs = (1 - self.damping) * beliefs + self.damping * new_beliefs
        return beliefs.cpu()