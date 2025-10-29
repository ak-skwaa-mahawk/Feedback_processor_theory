from src.scrape_theory.scrape_detector import ScrapeDetector
from src.scrape_theory.glyph_generator import GlyphGenerator
from src.scrape_theory.coherence import Coherence

class ISSTDefense:
    def __init__(self, query_budget=200):
        self.detector = ScrapeDetector()
        self.glyphs = GlyphGenerator()
        self.coherence = Coherence()
        self.query_budget = query_budget

    def robust_predict(self, x_adv, model):
        scrape = self.detector.detect(x_adv, x_adv * 0.99, model)
        glyph = self.glyphs.create_child_glyph(scrape)
        return {"prediction": model(x_adv), "scrape": scrape, "glyph": glyph}