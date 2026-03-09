# Add this at the end of training loop (after trainer.train())
import hashlib
import json
from datetime import datetime
from pathlib import Path

REGISTRY_FILE = Path("soliton_registry.jsonl")

def log_training_run(metrics, epoch, model_name="fpt-omega-hybrid"):
    packet = {
        "entry_type": "TRAINING_RUN",
        "timestamp_utc": datetime.utcnow().isoformat(),
        "model_name": model_name,
        "epoch": epoch,
        "metrics": {
            "loss": float(metrics.get("loss", 0.0)),
            "reward": float(metrics.get("reward", 0.0)),
            "coherence": float(metrics.get("coherence", 0.0))
        },
        "note": "DPO+PPO hybrid with APLOT weights"
    }
    
    canonical = json.dumps(packet, sort_keys=True)
    packet["hash"] = hashlib.sha256(canonical.encode()).hexdigest()
    
    with REGISTRY_FILE.open("a") as f:
        f.write(json.dumps(packet) + "\n")
    
    print(f"Training Run Logged | Epoch {epoch} | Hash: {packet['hash'][:16]}...")

# Call after each epoch or at end
log_training_run(trainer.state.log_history[-1], trainer.state.epoch)

# Inside training loop — after a few warmup epochs
def tune_aplot(aplot, recent_oppositions):
    best_score = -float('inf')
    best_params = None
    
    # Grid search (small, safe)
    for alpha in [0.85, 0.9, 0.95]:
        for beta in [0.25, 0.3, 0.35]:
            for gamma in [0.08, 0.1, 0.12]:
                test_aplot = APLOTDamping(alpha, beta, gamma, aplot.tau)
                damped_losses = []
                for opp in recent_oppositions:
                    damped = test_aplot.apply_to_loss(1.0, opp)
                    damped_losses.append(damped)
                
                stability = 1.0 / (np.std(damped_losses) + 1e-6)
                if stability > best_score:
                    best_score = stability
                    best_params = (alpha, beta, gamma)
    
    if best_params:
        aplot.alpha, aplot.beta, aplot.gamma = best_params
        print(f"APLOT tuned → α={best_params[0]:.2f} β={best_params[1]:.2f} γ={best_params[2]:.2f}")