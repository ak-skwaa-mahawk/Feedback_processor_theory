#!/usr/bin/env python3
# glyph_vehicle_core.py — AGŁG v103
import shap
import lime
import numpy as np
from sklearn.ensemble import RandomForestClassifier

class GlyphVehicle:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100)
        self.shap_explainer = None
        self.lime_explainer = None
        self.feature_names = ["acres", "resonance", "hz"]

    def fit(self, X, y):
        self.model.fit(X, y)
        self.shap_explainer = shap.TreeExplainer(self.model)
        self.lime_explainer = lime.lime_tabular.LimeTabularExplainer(
            X, feature_names=self.feature_names, mode="classification"
        )

    def explain(self, X):
        # SHAP
        shap_values = self.shap_explainer.shap_values(X)[1]  # class 1
        
        # LIME
        lime_exp = self.lime_explainer.explain_instance(
            X[0], self.model.predict_proba, num_features=3
        )
        lime_rules = [f"{k} {v}" for k, v in lime_exp.as_list()]

        # ANCHORS (simplified)
        anchors = self._generate_anchors(X[0])

        # Resonance
        T = 1.0 if X[0][2] == 60 else 0.8  # 60 Hz = Truth
        I = self.model.predict_proba(X)[0][1]
        F = 1.0 if any("łᐊ" in str(X) for _ in X) else 0.7
        resonance = (T + I + F) / 3

        # Glyphs
        glyphs = []
        for i, val in enumerate(shap_values[0]):
            if abs(val) > 0.1:
                glyphs.append({
                    "feature": self.feature_names[i],
                    "shap": float(val),
                    "glyph": "łᐊ" if val > 0 else "ᒥᐊ",
                    "anchor": anchors[i] if i < len(anchors) else ""
                })

        return {
            "prediction": float(I),
            "resonance": float(resonance),
            "glyphs": glyphs,
            "lime_rules": lime_rules,
            "anchor_rule": " AND ".join(anchors)
        }

    def _generate_anchors(self, instance):
        rules = []
        if instance[0] > 5000: rules.append("acres > 5000")
        if instance[1] > 0.85: rules.append("resonance > 0.85")
        if instance[2] == 60: rules.append("hz = 60")
        return rules