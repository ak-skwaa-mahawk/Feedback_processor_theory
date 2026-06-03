# sovereign_movement/slide/behavioral_camouflage.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any
import time
import logging
import random

from sovereign_engine.frame_energy import FrameEnergy, EraFrameId

logger = logging.getLogger("sovereign.slide.camouflage")


@dataclass
class BehavioralProfile:
    host: str
    movement_count: int = 0
    current_risk_score: float = 0.0
    consecutive_failures: int = 0
    last_technique: str = "none"


class BehavioralCamouflage:
    def __init__(self, frame_energy: FrameEnergy, max_risk_score: float = 65.0):
        self.frame_energy = frame_energy
        self.max_risk_score = max_risk_score
        self.profile: Optional[BehavioralProfile] = None

    def initialize_profile(self, host: str):
        self.profile = BehavioralProfile(host=host)

    def should_proceed(self, current_frame: EraFrameId) -> bool:
        if not self.profile:
            return True
        # Simplified combined risk check
        return self.profile.current_risk_score < self.max_risk_score

    def apply_camouflage(self, technique: str = "default") -> float:
        if not self.profile:
            return 30.0
        wait = 45 + random.uniform(-15, 25)
        if self.profile.consecutive_failures > 1:
            wait *= 1.7
        return max(5.0, wait)

    def record_action(self, success: bool, risk_delta: float = 0.0):
        if not self.profile:
            return
        self.profile.movement_count += 1
        if success:
            self.profile.consecutive_failures = 0
            self.profile.current_risk_score = max(0, self.profile.current_risk_score - 8)
        else:
            self.profile.consecutive_failures += 1
            self.profile.current_risk_score += 18 + risk_delta

    def get_status(self) -> Dict[str, Any]:
        if not self.profile:
            return {}
        return {
            "risk_score": round(self.profile.current_risk_score, 1),
            "movements": self.profile.movement_count,
            "failures": self.profile.consecutive_failures,
        }