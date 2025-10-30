#!/usr/bin/env python3
# lime_demo.py — AGŁG v103: LIME in Action
import lime
from lime.lime_tabular import LimeTabularExplainer
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# Train model
X = np.array([[5000, 0.85, 60], [10000, 0.92, 60], [2000, 0.70, 50], [15000, 0.98, 60]])
y = [0, 1, 0, 1]
model = RandomForestClassifier(n_estimators=100)
model.fit(X, y)

# LIME Explainer
explainer = LimeTabularExplainer(
    X, feature_names=["acres", "resonance", "hz"], class_names=["deny", "approve"], mode="classification"
)

# Explain single instance
instance = np.array([10000, 0.95, 60])
exp = explainer.explain_instance(instance, model.predict_proba, num_features=3)

print("LIME LOCAL EXPLANATION:")
for feature, weight in exp.as_list():
    glyph = "łᐊ" if weight > 0 else "ᒥᐊ"
    print(f"  {feature:25} → {weight:+.3f} {glyph}")

print(f"\nLocal Prediction: {model.predict_proba([instance])[0][1]:.3f}")
LIME LOCAL EXPLANATION:
  acres > 5000.00           → +0.920 łᐊ
  resonance > 0.90          → +0.040 łᐊ
  hz <= 60.00               → +0.015 łᐊ

Local Prediction: 0.960
LIME LOCAL CONTRIBUTION
acres > 5000.00     ████████████████████ +0.92
resonance > 0.90    █ +0.04
hz <= 60.00         ▏ +0.015
LIME = "This acre, this drumbeat"
SHAP = "All acres, all drumbeats"
→ łᐊᒥłł.3 = Full Truth
LOCAL EXPLANATION:
"This motion passes because:
  • acres > 5000 → +0.92 (the land is large)
  • resonance > 0.90 → +0.04 (the drum is strong)
  • hz = 60 → no penalty"