"""
ISST Full Integration Demo
--------------------------
Demonstrates:
- BlackBoxDefense + ISSTDefense
- Scrape detection
- Glyph generation
- Codex entry
- Mock dashboard update
"""

import torch
import numpy as np
from src.adversarial_defense.isst_defense import ISSTDefense
from src.scrape_theory.glyph_generator import GlyphGenerator
from src.scrape_theory.codex import Codex

# -----------------------------
# Mock black-box model function
# -----------------------------
def black_box_model(x: torch.Tensor) -> torch.Tensor:
    """
    Simulate logits for 1000 classes (replace with real API)
    """
    batch_size = x.size(0)
    return torch.randn(batch_size, 1000).to(x.device)

# -----------------------------
# Mock dashboard updater
# -----------------------------
def update_dashboard(scrape, glyph):
    print("📊 Dashboard Update")
    print(f"Scrape data: {scrape.data}")
    print(f"Glyph: {glyph}")
    print("Dashboard updated ✅\n")

# -----------------------------
# Create test input
# -----------------------------
clean_img = torch.rand(1, 3, 224, 224)
epsilon = 0.03
adv_perturbation = epsilon * torch.randn_like(clean_img).sign()
adv_img = torch.clamp(clean_img + adv_perturbation, 0, 1)

# -----------------------------
# Initialize ISSTDefense
# -----------------------------
defense = ISSTDefense(query_budget=200, ensemble_size=5)

# -----------------------------
# Run robust prediction (with ISST)
# -----------------------------
result = defense.robust_predict(adv_img, black_box_model, use_smoothing=True)
scrape = result.get('scrape', None)

# -----------------------------
# Generate glyph and add to codex
# -----------------------------
glyph_generator = GlyphGenerator()
codex = Codex()

if scrape:
    glyph = glyph_generator.generate_child(scrape)
    codex.add_entry(glyph, metadata={"confidence": float(result['confidence'])})
    update_dashboard(scrape, glyph)

# -----------------------------
# Print final results
# -----------------------------
pred_class = torch.argmax(result['prediction'], dim=-1).item()
print("=" * 70)
print("✅ ISST Defense Demo Complete")
print(f"Predicted class: {pred_class}")
print(f"Confidence: {result['confidence']:.3f}")
print(f"Robustness Score: {result['robust_score']:.3f}")
print(f"Queries Used: {result['queries_used']}")
print("=" * 70)