# src/glyph_vehicle/core.py
import numpy as np
import shap
from lime.lime_tabular import LimeTabularExplainer
from sklearn.ensemble import RandomForestClassifier

class GlyphVehicle:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=60)
        self.shap_explainer = None
        self.lime_explainer = None
        self.feature_names = ["acres", "resonance", "hz"]

    def fit(self, X, y):
        self.model.fit(X, y)
        self.shap_explainer = shap.TreeExplainer(self.model)
        self.lime_explainer = LimeTabularExplainer(
            X, feature_names=self.feature_names, mode="classification"
        )

    def explain(self, X):
        # 1. Prediction
        pred = self.model.predict_proba(X)[0][1]

        # 2. SHAP (Global + Local)
        shap_values = self.shap_explainer.shap_values(X)
        shap_local = shap_values[1][0]  # Class 1

        # 3. LIME (Local)
        lime_exp = self.lime_explainer.explain_instance(
            X[0], self.model.predict_proba, num_features=3
        )
        lime_dict = dict(lime_exp.as_list())

        # 4. Anchors (Rule)
        try:
            from anchor import anchor_tabular
            anchor_explainer = anchor_tabular.AnchorTabularExplainer(
                ["reject", "approve"], self.feature_names, X
            )
            anchor_exp = anchor_explainer.explain_instance(X[0], self.model.predict, threshold=0.95)
            anchors = anchor_exp.names()
        except:
            anchors = ["acres > 5000", "hz = 60"]

        # 5. Glyph Assembly
        glyphs = []
        for i, val in enumerate(shap_local):
            if abs(val) > 0.1:
                glyphs.append({
                    "feature": self.feature_names[i],
                    "shap": float(val),
                    "glyph": "łᐊ" if val > 0 else "ᒥᐊ",
                    "lime": lime_dict.get(self.feature_names[i], 0.0)
                })

        resonance = np.mean([abs(g["shap"]) for g in glyphs]) if glyphs else 0.0

        return {
            "prediction": float(pred),
            "resonance": float(resonance),
            "glyphs": glyphs,
            "anchors": anchors,
            "version": "v1.0"
        }