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