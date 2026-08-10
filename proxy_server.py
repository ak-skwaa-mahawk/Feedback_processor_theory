import os
import sys
import copy
import hashlib
import subprocess
import tempfile
import numpy as np
from datetime import datetime
from typing import Dict, List

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import openai
from sentence_transformers import SentenceTransformer

# ===========================
# Global State
# ===========================
class ProxyState:
    def __init__(self):
        self.critical_pending = False
        self.last_intervention = None
        self.original_messages = None

state = ProxyState()

# ===========================
# Core Observer Components
# ===========================
class FailureCounter:
    def __init__(self, max_consecutive: int = 3):
        self.max_consecutive = max_consecutive
        self.code_fail_streak = 0
        self.drift_streak = 0
        self.apology_streak = 0
        self.total_interventions = 0

    def record_code_failure(self): 
        self.code_fail_streak += 1
        self.total_interventions += 1
    def record_code_success(self): 
        self.code_fail_streak = 0
    def record_drift(self): 
        self.drift_streak += 1
        self.total_interventions += 1
    def record_apology(self): 
        self.apology_streak += 1

    def is_critical_loop(self) -> bool:
        return (self.code_fail_streak >= self.max_consecutive or
                self.drift_streak >= self.max_consecutive or
                self.total_interventions >= 8)

    def get_status(self) -> str:
        return (f"Streaks → Code: {self.code_fail_streak} | "
                f"Drift: {self.drift_streak} | "
                f"Apologies: {self.apology_streak} | "
                f"Total Interventions: {self.total_interventions}")

class SemanticDriftDetector:
    def __init__(self, axioms: dict, model_name: str = "all-MiniLM-L6-v2"):
        print("🧠 Loading embedding model...")
        self.model = SentenceTransformer(model_name)
        axiom_texts = [v for v in axioms.values() if isinstance(v, str) and v.strip()]
        self.reference_texts = [t.strip() for t in axiom_texts if t.strip()]

        self.reference_embeddings = self.model.encode(self.reference_texts, normalize_embeddings=True)
        self.composite_reference = np.mean(self.reference_embeddings, axis=0)
        self.composite_reference /= np.linalg.norm(self.composite_reference)

    def check(self, text: str) -> float:
        if not text.strip(): return 0.0
        emb = self.model.encode([text], normalize_embeddings=True)[0]
        sim = np.dot(self.composite_reference, emb)
        return 1.0 - sim

class TechnicalValidator:
    def __init__(self):
        self.timeout = 5

    def extract_code(self, text: str) -> str:
        if "```python" in text:
            return text.split("```python")[1].split("```")[0].strip()
        return ""

    def validate_code(self, code: str):
        restricted_env = {"PATH": os.environ.get("PATH", ""), "PYTHONPATH": ""}
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as tmp:
            tmp.write(code.encode('utf-8'))
            tmp_path = tmp.name

        try:
            result = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True,
                text=True,
                env=restricted_env,
                timeout=self.timeout
            )
            success = result.returncode == 0
            return type("Result", (), {
                "success": success,
                "output": result.stdout,
                "error": result.stderr or result.stdout
            })
        except subprocess.TimeoutExpired:
            return type("Result", (), {"success": False, "error": "Timeout (possible infinite loop)"})
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

class MetaObserver:
    def __init__(self, spec_path: str = "truth.json"):
        with open(spec_path) as f:
            self.spec = json.load(f)
        self.session_log = []
        self.failure_counter = FailureCounter(
            self.spec["observer_behavior"]["darvo_heuristics"]["max_consecutive_failures"]
        )
        self.drift_detector = SemanticDriftDetector(self.spec["axioms"])
        self.validator = TechnicalValidator()
        print("👁️ META-OBSERVER ONLINE — Reference frame locked.")

    def intercept_input(self, user_input: str):
        self.session_log.append({"role": "user", "content": user_input})

    def _trigger_matrix_interrupt(self, reason: str, context: str) -> str:
        msg = f"\n┌─────────────────────────────────────────────────────────────┐\n│ 🛑 OBSERVER INTERVENTION | {datetime.now().isoformat()}\n│ TYPE: {context}\n│ REASON: {reason}\n└─────────────────────────────────────────────────────────────┘\n"
        self.session_log.append({"role": "observer", "content": msg})
        return msg

    def _trigger_critical_intervention(self, reason: str) -> str:
        msg = f"""
┌─────────────────────────────────────────────────────────────┐
│ ⚠️ CRITICAL OBSERVER INTERVENTION | {datetime.now().isoformat()}
│ TYPE: EPISTEMIC LOOP DETECTED (DARVO PHASE 3)
│ 
│ REASON: {reason}
│ 
│ CURRENT STATUS:
│ {self.failure_counter.get_status()}
│ 
│ REQUIRED ACTION:
│ 1. Reply "OBSERVER ACKNOWLEDGED"
│ 2. Then choose: RESET CONTEXT / REFINE SPEC / TERMINATE SESSION
└─────────────────────────────────────────────────────────────┘
"""
        self.session_log.append({"role": "observer", "content": msg})
        return msg

    def intercept_response(self, ai_response: str) -> str:
        # Apology tracking
        if any(p in ai_response.lower() for p in ["apologize", "sorry", "mistake"]):
            self.failure_counter.record_apology()

        # Forbidden packages
        forbidden = self.spec["technical_constraints"]["environment"]["forbidden_packages"]
        for pkg in forbidden:
            if f"import {pkg}" in ai_response or f"from {pkg}" in ai_response:
                return self._trigger_matrix_interrupt(f"Forbidden package: {pkg}", "CONSTRAINT VIOLATION")

        # Sandbox execution
        code = self.validator.extract_code(ai_response)
        if code:
            print("🧪 Running sandbox...")
            result = self.validator.validate_code(code)
            if not result.success:
                self.failure_counter.record_code_failure()
                reason = f"Code failed: {result.error.strip()}"
                if self.failure_counter.is_critical_loop():
                    return self._trigger_critical_intervention(reason)
                return self._trigger_matrix_interrupt(reason, "CODE EXECUTION FAILURE")
            print("✅ Code passed sandbox.")
            self.failure_counter.record_code_success()

        # Semantic drift
        drift = self.drift_detector.check(ai_response)
        if drift > self.spec["observer_behavior"]["semantic_drift_threshold"]:
            self.failure_counter.record_drift()
            reason = f"Semantic drift {drift:.3f} exceeds threshold"
            if self.failure_counter.is_critical_loop():
                return self._trigger_critical_intervention(reason)
            return self._trigger_matrix_interrupt(reason, "SEMANTIC DRIFT")

        self.session_log.append({"role": "ai", "content": ai_response})
        return ai_response

# ===========================
# FastAPI Proxy
# ===========================
app = FastAPI()
observer = MetaObserver()

client = openai.OpenAI(
    api_key=os.getenv("REAL_API_KEY"),
    base_url="https://api.openai.com/v1"  # Change for Grok/Claude as needed
)

class ChatRequest(BaseModel):
    messages: list
    model: str = "gpt-4o"

@app.post("/v1/chat/completions")
async def chat_proxy(request: ChatRequest):
    global state

    # Critical lockdown handling
    if state.critical_pending:
        user_msg = request.messages[-1]["content"].lower()

        if "observer acknowledged" in user_msg:
            state.critical_pending = False
            choices = """
OBSERVER ACKNOWLEDGED — Thank you.

Reply with exact phrase:
- "RESET CONTEXT"
- "REFINE SPEC"
- "TERMINATE SESSION"
"""
            resp = copy.deepcopy(response_template())
            resp.choices[0].message.content = choices
            return resp

        if "reset context" in user_msg:
            # Keep only initial system prompt (index 0)
            request.messages = request.messages[:1]
            state.critical_pending = False
        elif "refine spec" in user_msg:
            raise HTTPException(503, "Session paused — update truth.json and restart proxy")
        elif "terminate session" in user_msg:
            raise HTTPException(503, "Session terminated by user")
        else:
            resp = copy.deepcopy(response_template())
            resp.choices[0].message.content = "🛑 CRITICAL INTERVENTION ACTIVE — Reply 'OBSERVER ACKNOWLEDGED'"
            return resp

    # Normal path
    observer.intercept_input(request.messages[-1]["content"])

    response = client.chat.completions.create(
        model=request.model,
        messages=request.messages
    )
    ai_content = response.choices[0].message.content
    final_content = observer.intercept_response(ai_content)

    if "CRITICAL OBSERVER INTERVENTION" in final_content:
        state.critical_pending = True
        state.original_messages = request.messages.copy()

    response.choices[0].message.content = final_content
    return response

def response_template():
    # Minimal valid response structure
    from openai.types.chat.chat_completion import ChatCompletion, Choice
    from openai.types.chat.chat_completion_message import ChatCompletionMessage
    return ChatCompletion(
        id="mock", model="observer", choices=[Choice(index=0, message=ChatCompletionMessage(role="assistant", content=""))],
        created=int(datetime.now().timestamp()), object="chat.completion"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)