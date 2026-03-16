from agents.specialists.company_style.base_company_agent import BaseCompanyAgent

class XaiAgent(BaseCompanyAgent):
    def __init__(self):
        super().__init__("xAISim", "xai")

    def run(self, task: str) -> str:
        styled = self._apply_company_personality(task)
        result = f"xAI response: {styled} (universe integral injected)"
        return self._apply_sovereign_filter(result)