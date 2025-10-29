import hashlib
import random

class GlyphGenerator:
    def create_child_glyph(self, scrape):
        base = f"{scrape.energy:.4f}-{scrape.entropy:.4f}-{scrape.distance:.4f}"
        h = hashlib.sha256(base.encode()).hexdigest()[:8]
        return f"AGŁL-{h}"

    def spawn_meta_glyph(self, glyph1, glyph2):
        combined = f"{glyph1}{glyph2}{random.random()}"
        h = hashlib.sha256(combined.encode()).hexdigest()[:12]
        return f"MG-{h}"