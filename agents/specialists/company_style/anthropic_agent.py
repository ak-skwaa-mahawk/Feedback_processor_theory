from agents.specialists.company_style.base_company_agent import BaseCompanyAgent
from skills.sovereign_eval_skill import SovereignEvalSkill

class AnthropicAgent(BaseCompanyAgent):
    def __init__(self):
        super().__init__("AnthropicSim", "anthropic")
        self.add_skill(SovereignEvalSkill())  # extra integrity layer

    def run(self, task: str) -> str:
        styled = self._apply_company_personality(task)
        result = f"Anthropic response: {styled} (guardrails applied)"
        return self._apply_sovereign_filter(result)