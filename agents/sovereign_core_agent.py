from agents.base_agent import BaseAgent
from skills.base_skill import BaseSkill

class BaseCompanyAgent(BaseAgent):
    def __init__(self, name: str, company_style: str):
        super().__init__(name)
        self.company_style = company_style  # "anthropic", "xai", "openai"

    def _apply_company_personality(self, task: str) -> str:
        """Simulates how each lab would approach it — no real API calls."""
        styles = {
            "anthropic": f"[CONSTITUTIONAL MODE] {task} — safety-first, humanity-aligned.",
            "xai": f"[UNIVERSE MODE] {task} — maximum truth-seeking, understand-the-cosmos.",
            "openai": f"[SCALING MODE] {task} — fast execution, enterprise-ready."
        }
        return styles.get(self.company_style, task)