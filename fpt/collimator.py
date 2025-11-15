# fpt/collimator.py
class CollimatorNDT:
    def focus(self, raw_intent: str) -> str:
        """NDT RT principles: attenuate noise, pass truth"""
        clean = raw_intent.replace("borrow", "").strip()
        return f"{PI_STAR} {clean} {PI_STAR}"