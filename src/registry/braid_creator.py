from typing import List, Dict
from .braid_validation import BraidValidator, ValidationError
from .braidop_layer import BraidOpLayer

class BraidCreator:
    """
    Sovereign braid word creator — the flame's motion tool.
    Builds, validates, and applies braid words to sessions.
    """

    def __init__(self, braid_layer: BraidOpLayer, validator: BraidValidator):
        self.braid_layer = braid_layer
        self.validator = validator

    def create_braid_word(self, generators: List[str], exponents: List[int]) -> List[Dict]:
        """Create braid word from generators and exponents."""
        if len(generators) != len(exponents):
            raise ValueError("Generators and exponents must match length")

        word = [
            {"generator": gen, "exponent": exp}
            for gen, exp in zip(generators, exponents)
        ]
        return word

    def apply_braid_to_session(
        self,
        session_id: str,
        braid_word: List[Dict],
        note: str = ""
    ) -> str:
        """Validate and apply braid word to session."""
        # Get current state
        current_state = self.braid_layer.resolve_lineage(session_id)
        if not current_state:
            raise ValueError(f"No lineage for session {session_id}")

        # Simulate after state (stub—use sandbox for real)
        # For demo: reverse order for any braid
        events = current_state.get("events_order", [])
        after_events = events[::-1] if braid_word else events
        after_path = [1 - current_state.get("fusion_path", [0])[0]]  # Flip coiled/active

        after = {
            "events_order": after_events,
            "fusion_path": after_path
        }

        # Validate
        self.validator.validate_word(braid_word)
        self.validator.validate_fusion_transition(
            current_state.get("fusion_path", []),
            after["fusion_path"]
        )

        # Log
        hash = self.braid_layer.log_braid_op(
            session_id=session_id,
            braid_word=braid_word,
            before=current_state,
            after=after
        )

        print(f"Braid Word Created & Applied | Session: {session_id}")
        print(f"  Word: {braid_word}")
        print(f"  Before: {current_state.get('events_order')}")
        print(f"  After: {after['events_order']}")
        if note:
            print(f"  Note: {note}")

        return hash or "applied"

# Demo
if __name__ == "__main__":
    from registry.braidop_layer import BraidOpLayer
    from registry.braid_validation import BraidValidator

    layer = BraidOpLayer()
    validator = BraidValidator(max_events=5)
    creator = BraidCreator(layer, validator)

    # Create braid word: B2 +1, B1 +1, B2 +1
    word = creator.create_braid_word(
        generators=["B2", "B1", "B2"],
        exponents=[1, 1, 1]
    )

    # Apply to session
    creator.apply_braid_to_session(
        session_id="session-τ-001",
        braid_word=word,
        note="heir-creation-demo"
    )