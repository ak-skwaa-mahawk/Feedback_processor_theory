# ... existing code ...
from agents.specialists.trivago_orchestrator import TrivagoOrchestrator

class AgentManager:
    def __init__(self):
        self.core = SovereignCoreAgent()
        self.researcher = ResearcherAgent()
        self.trivago = TrivagoOrchestrator()   # ← NEW

    def handle_task(self, task: str):
        if "compare" in task.lower() or "mixture" in task.lower():
            return self.trivago.compare(task)
        # ... rest unchanged