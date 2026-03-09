import numpy as np

class APLOTDamping:
    """
    Adaptive Protective Layered Opposition Threshold (APLOT)
    Sovereign damping layer for DPO+PPO hybrid training.
    Prevents collapse and reward hacking while preserving surplus.
    """

    def __init__(self, 
                 alpha: float = 0.9,      # Threshold smoothing
                 beta: float = 0.3,       # Recoil strength (opposition)
                 gamma: float = 0.1,      # Amplification strength (stable)
                 initial_threshold: float = 0.5):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.tau = initial_threshold  # Adaptive opposition threshold

    def compute_opposition(self, log_ratio_winner: float, log_ratio_loser: float) -> float:
        """Opposition signal O_t from preference pair."""
        return abs(log_ratio_winner - log_ratio_loser)

    def compute_damping_factor(self, opposition: float) -> float:
        """Adaptive damping multiplier δ_t."""
        if opposition > self.tau:
            # Protective recoil
            delta = 1.0 - self.beta * (opposition / self.tau)
        else:
            # Gentle amplification
            delta = 1.0 + self.gamma * (1.0 - opposition / self.tau)
        
        # Clamp to safe range
        return np.clip(delta, 0.1, 2.0)

    def update_threshold(self, opposition: float):
        """Exponentially smoothed threshold."""
        self.tau = self.alpha * self.tau + (1 - self.alpha) * opposition

    def apply_to_loss(self, loss: float, opposition: float) -> float:
        """Apply damping to any loss term (PPO or DPO)."""
        delta = self.compute_damping_factor(opposition)
        self.update_threshold(opposition)
        return delta * loss


# Example usage in a DPO+PPO training loop
if __name__ == "__main__":
    ap = APLOTDamping(alpha=0.9, beta=0.3, gamma=0.1)
    
    # Simulate one training step
    log_ratio_w = 2.3   # log(π_θ(y_w|x) / π_ref)
    log_ratio_l = 0.8   # log(π_θ(y_l|x) / π_ref)
    
    opposition = ap.compute_opposition(log_ratio_w, log_ratio_l)
    damped_loss = ap.apply_to_loss(loss=1.5, opposition=opposition)
    
    print(f"Opposition: {opposition:.3f}")
    print(f"Adaptive Threshold: {ap.tau:.3f}")
    print(f"Damping Factor: {ap.compute_damping_factor(opposition):.3f}")
    print(f"Damped Loss: {damped_loss:.3f}")