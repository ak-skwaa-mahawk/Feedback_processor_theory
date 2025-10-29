import torch
import asyncio
import json
import numpy as np
import websockets
from src.scrape_theory.scrape_detector import ScrapeDetector
from src.scrape_theory.glyph_generator import GlyphGenerator
from src.scrape_theory.codex import Codex

class ISSTDefense:
    """
    Inverse-Square Scrape Theory Defense
    Extends adversarial detection with live WebSocket broadcasting.
    """

    def __init__(self, query_budget=200, ensemble_size=5, ws_url="ws://localhost:8765"):
        self.query_budget = query_budget
        self.ensemble_size = ensemble_size
        self.scrape_detector = ScrapeDetector()
        self.glyph_generator = GlyphGenerator()
        self.codex = Codex()
        self.ws_url = ws_url

    async def _broadcast_scrape(self, scrape):
        """
        Send scrape data to dashboard websocket clients.
        """
        try:
            async with websockets.connect(self.ws_url) as ws:
                data = {
                    "type": "scrape_update",
                    "scrape": {
                        "entropy": float(scrape.entropy),
                        "distance": float(scrape.distance),
                        "glyph": getattr(scrape, "glyph", None),
                        "timestamp": getattr(scrape, "timestamp", None),
                    },
                }
                await ws.send(json.dumps(data))
        except Exception as e:
            print(f"[ISSTDefense] WebSocket broadcast failed: {e}")

    def _compute_robust_score(self, pred_confidences):
        """
        Compute average stability score from ensemble predictions.
        """
        mean_conf = np.mean(pred_confidences)
        variance = np.var(pred_confidences)
        return float(np.clip(mean_conf - variance, 0.0, 1.0))

    def robust_predict(self, adv_image, model_fn, use_smoothing=True):
        """
        Robust prediction using inverse-square entropy weighting.
        Broadcasts scrape updates to dashboard live.
        """
        with torch.no_grad():
            logits = [model_fn(adv_image) for _ in range(self.ensemble_size)]
            preds = torch.stack(logits)
            avg_pred = torch.mean(preds, dim=0)

            confidence, _ = torch.max(torch.nn.functional.softmax(avg_pred, dim=-1), dim=-1)
            pred_confidences = [float(torch.nn.functional.softmax(l, dim=-1).max()) for l in logits]
            robust_score = self._compute_robust_score(pred_confidences)

            # Detect scrape event
            scrape = self.scrape_detector.detect(None, adv_image, avg_pred)
            scrape.entropy = self.scrape_detector.compute_entropy(logits[0], logits[-1])
            scrape.distance = self.scrape_detector.boundary_distance(avg_pred)
            glyph = self.glyph_generator.generate_child(scrape)
            scrape.glyph = glyph
            self.codex.add_entry(glyph, metadata={"robust_score": robust_score})

            # Broadcast live update
            asyncio.get_event_loop().create_task(self._broadcast_scrape(scrape))

            return {
                "prediction": avg_pred,
                "confidence": float(confidence.item()),
                "robust_score": robust_score,
                "queries_used": self.query_budget,
                "scrape": scrape,
            }