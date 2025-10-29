from blackbox_defense.defense import BlackBoxDefense
from src.scrape_theory.scrape_detector import ScrapeDetector

class ISSTDefense(BlackBoxDefense):
    """Extends BlackBoxDefense with ISST scrapes"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scrape_detector = ScrapeDetector()
    
    def robust_predict(self, x, black_box_query, use_smoothing=True):
        """Generate scrapes while predicting"""
        result = super().robust_predict(x, black_box_query, use_smoothing)
        scrape = self.scrape_detector.detect(x, x, result['prediction'])
        result['scrape'] = scrape
        return result