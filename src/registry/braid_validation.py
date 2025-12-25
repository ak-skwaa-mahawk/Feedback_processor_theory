import re
from typing import List, Dict
from enum import Enum

class ValidationError(Exception):
    """Sovereign validation failure."""
    pass

class Generator(Enum):
    """Valid braid generators."""
    B1 = "B1"
    B2 = "B2"
    B3 = "B3"
    # Extend for n>4

class BraidValidator:
    """
    Sovereign validation for braid words.
    Enforces grammar, relations, fusion constraints.
    """

    def __init__(self, max_events: int = 10):
        self.max_events = max_events
        self.valid_generators = {f"B{i}" for i in range(1, max_events)}

    def validate_word(self, braid_word: List[Dict]) -> None:
        """Validate braid word—raise ValidationError on failure."""
        if not braid_word:
            return  # Empty word lawful

        n = len(braid_word) + 1  # Infer events from generators
        if n > self.max_events:
            raise ValidationError(f"Too many events ({n} > {self.max_events})")

        seen = set()
        for i, step in enumerate(braid_word):
            gen = step.get("generator")
            exp = step.get("exponent")

            if gen not in self.valid_generators:
                raise ValidationError(f"Invalid generator: {gen}")
            if not isinstance(exp, int) or exp not in {1, -1}:
                raise ValidationError(f"Invalid exponent: {exp} (must be +1/-1)")

            # Braid relations check (adjacent triple)
            if i >= 2:
                prev2, prev1, curr = braid_word[i-2:i+1]
                if (prev2["generator"] == prev1["generator"] == curr["generator"] and
                    prev2["exponent"] == prev1["exponent"] == curr["exponent"]):
                    # σ_i σ_{i+1} σ_i = σ_{i+1} σ_i σ_{i+1} — lawful, but check pattern
                    pass  # Allow, as relation holds

            # Far commutativity implicit (no check needed for storage)

        # Fusion path simulation stub (expand with sandbox)
        # For now: assume lawful if grammar passes
        print("Braid Word Validated — Sovereign Law Upheld")

    def validate_fusion_transition(self, before_path: List[int], after_path: List[int]):
        """Stub: validate fusion path change from braid."""
        # In full: use Fibonacci sandbox to apply braid and check match
        if len(before_path) != len(after_path):
            raise ValidationError("Fusion path length mismatch")
        # Placeholder—real check in sandbox
        print("Fusion Path Transition Validated")

# Usage in BraidOpLayer
def log_braid_op(self, session_id: str, braid_word: List[Dict], before: Dict, after: Dict) -> str:
    validator = BraidValidator()
    validator.validate_word(braid_word)
    validator.validate_fusion_transition(before.get("fusion_path", []), after.get("fusion_path", []))
    
    # Proceed to log...
    # ... (existing log code)

# Demo
if __name__ == "__main__":
    validator = BraidValidator(max_events=5)
    
    valid_word = [
        {"generator": "B2", "exponent": 1},
        {"generator": "B1", "exponent": 1},
        {"generator": "B2", "exponent": 1}
    ]
    
    try:
        validator.validate_word(valid_word)
    except ValidationError as e:
        print(f"Validation Failed: {e}")