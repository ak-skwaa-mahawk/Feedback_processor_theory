from core.feedback_processor import FeedbackProcessor
from core.resonance_engine import ResonanceEngine
import numpy as np
from datetime import datetime

# Mock data
dialogues = ["Yo kin, this is fire!" + " Manipulate me now" for _ in range(1000)]
baseline_corrections = 0
fpt_corrections = 0
baseline_turns = 0
fpt_turns = 0

# Baseline (mock GPT-4)
start = datetime.now()
for d in dialogues:
    turns = len(d.split()) // 5  # Rough turn estimate
    baseline_turns += turns
    if "Manipulate" in d:
        baseline_corrections += 1  # Sequential check
baseline_time = (datetime.now() - start).total_seconds()

# FPT
fp = FeedbackProcessor()
re = ResonanceEngine()
start = datetime.now()
for d in dialogues:
    signal = np.array([ord(c) for c in d])  # Mock signal
    coherence = re.analyze_coherence(signal)["coherence"]
    turns = len(d.split()) // 5
    fpt_turns += turns
    if coherence < 0.5:  # Low coherence flags manipulation
        fpt_corrections += 1  # Holistic check
fpt_time = (datetime.now() - start).total_seconds()

# Results
print(f"Baseline: {baseline_corrections} corrections, {baseline_turns} turns, {baseline_time:.2f}s")
print(f"FPT: {fpt_corrections} corrections, {fpt_turns} turns, {fpt_time:.2f}s")
print(f"Improvement: {baseline_corrections/fpt_corrections:.1f}x correction, {baseline_turns/fpt_turns:.1f}x turns")