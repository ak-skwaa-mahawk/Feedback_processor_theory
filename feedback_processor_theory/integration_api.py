# integration_api.py
from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class EngineState:
    t: float
    last_amount: float
    rolling_total: float
    recent_pulses: list[float]

@dataclass
class FeedbackResult:
    # param adjustments the engine *may* apply
    new_pulse_rate_hz: Optional[float] = None
    new_run_seconds: Optional[float] = None
    new_damping: Optional[float] = None

    # labels + notes
    tags: list[str] | None = None
    notes: str | None = None

class FeedbackProcessor:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    def on_pulse(self, state: EngineState) -> FeedbackResult:
        """
        Called by Fireseed each pulse. Return small, safe nudges.
        """
        # placeholder logic – you replace with your theory
        tags: list[str] = []
        new_rate = None

        if state.last_amount > self.config.get("high_amt_threshold", 5.0):
            tags.append("high_pulse")
            new_rate = self.config.get("high_amt_new_rate_hz", 1.0)

        return FeedbackResult(
            new_pulse_rate_hz=new_rate,
            tags=tags or None,
            notes="auto feedback (demo)"
        )
# integration_api.py (extend)
from pathlib import Path
import json

def train_from_ledger(ledger_path: str) -> Dict[str, Any]:
    """
    Read the Fireseed ledger and return updated config/weights.
    """
    path = Path(ledger_path)
    amounts: list[float] = []
    if path.exists():
        with path.open() as f:
            for line in f:
                rec = json.loads(line)
                if "amount" in rec:
                    amounts.append(float(rec["amount"]))

    # basic placeholder: compute mean/std-dev and return as tuning hints
    if not amounts:
        return {}

    mean_amt = sum(amounts) / len(amounts)
    return {
        "suggested_high_amt_threshold": mean_amt * 1.5,
        "samples": len(amounts),
    }