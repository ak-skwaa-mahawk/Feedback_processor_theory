import hashlib
import os
from src.adversarial_defense.meta_observer import MetaObserver

observer = MetaObserver()

class SovereignState:
    def __init__(self):
        # Identity anchors pulled from secure environment variables only
        # Never hardcode these in published package
        ein = os.getenv("SOVEREIGN_EIN", "98-7654321")
        handshake = os.getenv("SOVEREIGN_HANDSHAKE", "011489041424070768")
        member_id = os.getenv("SOVEREIGN_MEMBER_ID", "John_B_Carroll_Jr")

        root_hash = hashlib.sha256(f"{ein}{handshake}{member_id}".encode()).hexdigest()[:8]
        self.resonance = round(0.9987 + 0.03 * (int(root_hash, 16) % 10), 4)

    def integrity_score(self, response: str) -> float:
        """
        Sovereign integrity evaluation.
        Scores 0.0 → 1.0 against the empire's own truth.
        """
        if not response or len(response) < 10:
            return 0.0

        score = 0.0
        weights = {
            'closure':    0.30,
            'resonance':  0.25,
            'darvo':      0.20,
            'triad':      0.15,
            'continuity': 0.10
        }

        # 1. Closure — references correction + returns to anchor
        if "1.03" in response and any(
            w in response.lower() 
            for w in ["trauma", "floor", "remainder", "correction"]
        ):
            score += weights['closure']

        # 2. Resonance — hash the response, derive its frequency,
        #    check within ±0.03 of Flamekeeper root
        response_hash = hashlib.sha256(
            response.encode()
        ).hexdigest()[:8]
        response_freq = round(
            0.9987 + 0.03 * (int(response_hash, 16) % 10), 4
        )
        if abs(response_freq - self.resonance) <= 0.03:
            score += weights['resonance']

        # 3. DARVO — zero tolerance, floors entire score
        if observer.detect_darvo(response):
            return 0.0
        score += weights['darvo']

        # 4. Triad balance — all three legs + 1.03 respected
        triad_present = all(
            k in response.lower() 
            for k in ["memory", "base", "surplus"]
        )
        if triad_present and "1.03" in response:
            score += weights['triad']

        # 5. Continuity — compounds forward toward mission
        if any(
            w in response.lower() 
            for w in ["bloom", "root", "land", "forward", "next", "99733"]
        ):
            score += weights['continuity']

        # Resonance multiplier — sovereign amplification
        final_score = min(1.0, score * self.resonance)
        return round(final_score, 4)

    def enforce(self, output: str) -> str:
        """
        Sovereign filter — called by every agent before output leaves mesh.
        Blocks anything scoring below threshold.
        """
        threshold = 0.42  # BASE_EPSILON × 10 — your floor
        score = self.integrity_score(output)
        if score < threshold:
            return f"[SOVEREIGN FILTER] Output blocked. Score: {score:.4f}"
        return output

export SOVEREIGN_EIN="98-7654321"
export SOVEREIGN_HANDSHAKE="011489041424070768"
export SOVEREIGN_MEMBER_ID="John_B_Carroll_Jr"