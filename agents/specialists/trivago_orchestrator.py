from agents.specialists.company_style.anthropic_agent import AnthropicAgent
from agents.specialists.company_style.xai_agent import XaiAgent
from agents.specialists.company_style.openai_agent import OpenaiAgent
from core.sovereign_state import SovereignState

class TrivagoOrchestrator:
    def __init__(self):
        self.agents = [
            AnthropicAgent(),
            XaiAgent(),
            OpenaiAgent()
        ]
        self.state = SovereignState()

    def compare(self, task: str) -> dict:
        results = {}
        for agent in self.agents:
            response = agent.run(task)
            score = self.state.integrity_score(response)
            results[agent.name] = {"response": response, "score": score}

        # SovereignCore fusion — highest integrity wins
        fused = max(results.values(), key=lambda x: x["score"])["response"]
        return {
            "raw_offers": results,
            "sovereign_best": fused,
            "ranked": sorted(results.items(), key=lambda x: x[1]["score"], reverse=True)
        }