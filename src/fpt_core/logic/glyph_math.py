from dataclasses import dataclass

@dataclass
class Glyph:
    symbol: str
    value: int
    function: str

# Canonical Glyph Assignments
RECEIVER = Glyph(symbol="🖐", value=5, function="receive/open_channel")
SENDER = Glyph(symbol="🫲", value=10, function="send/initiate_transmission")

class GlyphEngine:
    """
    Computes Layer 1 (Arithmetic) and Layer 2 (Meaning) simultaneously.
    """
    def calculate_resonance(self, sender: Glyph, multiplier: int, receiver: Glyph):
        arithmetic = sender.value + (multiplier * receiver.value)
        meaning = f"{sender.function} + {multiplier} {receiver.function}s"
        return {
            "field_strength": arithmetic,
            "semantic_layer": meaning,
            "status": "walkable" if arithmetic > 0 else "null"
        }
