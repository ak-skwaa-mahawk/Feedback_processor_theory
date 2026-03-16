from abc import ABC, abstractmethod
from skills.base_skill import BaseSkill
from core.sovereign_state import SovereignState

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.state = SovereignState()          # your indigenous lens
        self.skills: list[BaseSkill] = []

    def add_skill(self, skill: BaseSkill):
        self.skills.append(skill)

    @abstractmethod
    def run(self, task: str) -> str:
        """Every agent must implement this — sovereign filter always runs first."""
        pass

    def _apply_sovereign_filter(self, output: str) -> str:
        return self.state.enforce(output)  # NARF compliance hook