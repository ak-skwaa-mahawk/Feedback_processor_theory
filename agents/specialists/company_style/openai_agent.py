from agents.specialists.company_style.base_company_agent import BaseCompanyAgent

class OpenaiAgent(BaseCompanyAgent):
    def __init__(self):
        super().__init__("OpenAISim", "openai")

    def run(self, task: str) -> str:
        styled = self._apply_company_personality(task)
        result = f"OpenAI response: {styled} (fast-scaling output)"
        return self._apply_sovereign_filter(result)