# thin adapter that maps FPT objects to Synara glyphs
from external.Feedback_processor_theory.src import fpt  # adjust path as needed
from .glyph import Glyph

class FPTAdapter:
    def __init__(self, mesh):
        self.mesh = mesh

    def ingest_fpt_emission(self, fpt_obj) -> Glyph:
        # convert an FPT emission into a Synara Glyph
        glyph = Glyph.from_dict({
            "source": fpt_obj.source_id,
            "content": fpt_obj.payload,
            "meta": {"fpt_type": fpt_obj.type}
        })
        self.mesh.publish(glyph)
        return glyph