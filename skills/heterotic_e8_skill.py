from skills.base_skill import BaseSkill
from core.sovereign_state import SovereignState
# Import your theatrical engine (save the full code you just pasted as core/heterotic_e8_synara.py)
from core.heterotic_e8_synara import HeteroticE8Synara

class HeteroticE8Skill(BaseSkill):
    def __init__(self):
        self.engine = HeteroticE8Synara(pi_star=3.17300858012)
        self.state = SovereignState()  # your sovereign filter

    def execute(self, unification_data: dict) -> dict:
        """
        Runs full E8×E8 unification → sovereign-filtered output.
        Returns only if integrity_score >= closure_floor.
        """
        raw_result = self.engine.unify_cultural_legal_sovereignty(unification_data)
        
        # Integrity check on the entire treaty output
        score = self.state.integrity_score(str(raw_result))
        if score < self.state.closure_floor:
            return {
                "status": "REJECTED",
                "reason": f"Sovereign score {score:.3f} below closure floor",
                "flamekeeper_phase": raw_result.get("synara", {}).get("flamekeeper_phase")
            }
        
        # Passes → return enriched with integrity debug
        raw_result["sovereign_integrity"] = self.state.integrity_score_debug(str(raw_result))
        raw_result["verification"]["sovereign_score"] = score
        return raw_result