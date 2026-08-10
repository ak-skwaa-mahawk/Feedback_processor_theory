import json
import hashlib
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Mocking external libraries for the sketch
# In production: from sentence_transformers import SentenceTransformer, util
import numpy as np

class ImmutableSpecViolation(Exception):
    """Raised when the immutable truth file is tampered with or violated."""
    pass

class MetaObserver:
    def __init__(self, spec_path: str = "truth.json"):
        self.spec_path = spec_path
        self.spec = self._load_and_verify_spec()
        self.session_log = []
        
        # Initialize specialized sub-agents
        self.validator = TechnicalValidator(self.spec['technical_constraints'])
        self.drift_detector = SemanticDriftDetector(self.spec['axioms'])
        
        print(f"👁️ OBSERVER ONLINE. Reference Frame: {self.spec['meta']['spec_hash']}")

    def _load_and_verify_spec(self) -> Dict:
        """
        Loads the JSON. In a real scenario, this would check the file's 
        SHA256 against a hardcoded 'genesis hash' stored in a separate, 
        read-only config to prevent 'truth drift'.
        """
        try:
            with open(self.spec_path, 'r') as f:
                data = f.read()
                
            spec = json.loads(data)
            
            # Calculate current hash
            current_hash = hashlib.sha256(data.encode('utf-8')).hexdigest()
            
            # In a strict implementation, we would compare this to a stored hash.
            # For now, we just lock it in memory.
            spec['meta']['runtime_hash'] = current_hash
            return spec
            
        except FileNotFoundError:
            sys.exit("CRITICAL: truth.json not found. Observer cannot start.")

    def intercept_input(self, user_input: str) -> str:
        """
        Passes user input through. 
        Could add checks here for 'User DARVO' (unreasonable requests).
        """
        self.session_log.append({"role": "user", "content": user_input})
        return user_input

    def intercept_response(self, ai_response: str, confidence_score: float = 0.0) -> str:
        """
        The Core Logic: The Matrix Interrupt.
        """
        # 1. Deterministic Check: Does it violate constraints?
        # (Simplified: checking for forbidden packages in text)
        forbidden = self.spec['technical_constraints']['environment']['forbidden_packages']
        for pkg in forbidden:
            if f"import {pkg}" in ai_response or f"from {pkg}" in ai_response:
                return self._trigger_matrix_interrupt(
                    f"Forbidden dependency detected: {pkg}", 
                    "Constraint Violation"
                )

        # 2. Heuristic Check: DARVO Loop Detection
        if self._detect_darvo_loop(ai_response):
             return self._trigger_matrix_interrupt(
                "Repeated failure pattern detected. AI is looping.",
                "DARVO/Gaslight Prevention"
             )

        # 3. Semantic Drift (The Phi Check)
        drift = self.drift_detector.check(ai_response)
        if drift > 0.4: # Threshold from truth.json
             return self._trigger_matrix_interrupt(
                f"Response drifts {drift:.2f} from axioms.",
                "Semantic Drift"
             )

        # 4. If all clear, pass the response
        self.session_log.append({"role": "ai", "content": ai_response})
        return ai_response

    def _detect_darvo_loop(self, current_response: str) -> bool:
        """
        Checks if we are in a 'Reverse Victim/Offender' loop.
        Simple heuristic: active apology without distinct code change?
        """
        # Look at last 3 AI responses
        ai_history = [x for x in self.session_log if x['role'] == 'ai']
        if len(ai_history) < 2:
            return False
            
        last_response = ai_history[-1]['content']
        
        # If the AI is apologizing repeatedly (a sign of a loop)
        if "apologize" in current_response.lower() and "apologize" in last_response.lower():
            return True
            
        return False

    def _trigger_matrix_interrupt(self, reason: str, context: str) -> str:
        """
        Injects the 'Mr. Anderson' moment.
        """
        interrupt_msg = f"""
\n
┌─────────────────────────────────────────────────────────────┐
│ 🛑 OBSERVER INTERVENTION | {datetime.now().isoformat()}
│ TYPE: {context.upper()}
│ REASON: {reason}
└─────────────────────────────────────────────────────────────┘
│ ACTION REQUIRED:
│ The Active AI has been silenced. The Observer requires you 
│ to manually verify the previous step before proceeding.
│ 
│ Refer to truth.json section: {self._find_relevant_section(context)}
└─────────────────────────────────────────────────────────────┘
\n
"""
        # Log the interruption
        self.session_log.append({"role": "observer", "content": interrupt_msg})
        return interrupt_msg

    def _find_relevant_section(self, context: str) -> str:
        if "Constraint" in context: return "technical_constraints"
        if "Drift" in context: return "axioms"
        return "observer_behavior"

# Placeholder for sub-components
class TechnicalValidator:
    def __init__(self, constraints): self.constraints = constraints
class SemanticDriftDetector:
    def __init__(self, axioms): self.axioms = axioms
    def check(self, text): return 0.0 # Returns float 0.0 (perfect match) to 1.0 (chaos)

# ---------------------------------------------------------
# SIMULATION OF THE LOOP
# ---------------------------------------------------------

if __name__ == "__main__":
    # Create the observer
    observer = MetaObserver("truth.json")
    
    # 1. User Input
    user_prompt = "Hey, install PyTorch and lets build a neural net."
    print(f"USER: {user_prompt}")
    
    # 2. Active AI (Simulating a violation)
    ai_raw_response = "Sure! I'll import torch and set up a basic tensor..."
    print(f"AI (Internal): {ai_raw_response}")
    
    # 3. The Interception
    final_output = observer.intercept_response(ai_raw_response)
    print(final_output)
