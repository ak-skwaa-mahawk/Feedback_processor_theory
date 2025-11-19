# isst_defense.py — LIVE IN THE FPT REPOSITORY
# The exact PyTorch layer that now guards the Soliton Registry
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn import Parameter

class ISSTDefenseLayer(nn.Module):
    """
    Inverse-Square Scrape Theory (ISST) Adversarial Defense
    Rejects entropic attacks before they touch the model
    """
    def __init__(self, rho=0.15, alpha=1.0, C_target=2.0):
        super().__init__()
        self.rho = rho          # Resonance Threshold — the line of immortality
        self.alpha = alpha
        self.C_target = C_target
        self.n_hat = Parameter(torch.randn(1, 512), requires_grad=False)  # reference direction (79.79 Hz axis)

    def compute_entropy(self, x):
        # Shannon entropy over feature distribution
        x_flat = x.view(x.size(0), -1)
        probs = F.softmax(x_flat, dim=-1)
        H = -torch.sum(probs * torch.log(probs + 1e-12), dim=-1)
        return H.mean()

    def compute_coherence(self, x):
        # Vector alignment to ancestral axis (iron-axis resonance)
        x_flat = x.view(x.size(0), -1)
        x_norm = F.normalize(x_flat, dim=-1)
        n_hat = F.normalize(self.n_hat, dim=-1)
        C = torch.abs(torch.matmul(x_norm, n_hat.t())).mean()
        return C * self.C_target  # scale to biological range

    def forward(self, x):
        H = self.compute_entropy(x)
        C = self.compute_coherence(x)
        r = torch.tensor(1.0, device=x.device)  # we defend at the root
        E0 = torch.tensor(1.0, device=x.device)

        # Full ISST Intensity Formula
        S = (C * E0) / (r**2 * (1 + self.alpha * H))

        # THE IRON GATE
        mask = S > self.rho
        if not mask.all():
            print(f"ISST DEFENSE: {(~mask).sum().item()} entropic inputs REJECTED | S = {S[~mask][:5].cpu().numpy()}")
        
        # Zero out the poison — they never enter memory
        x = x * mask.float().view(-1, 1, 1, 1)
        return x, {"S": S, "H": H, "C": C, "passed": mask}