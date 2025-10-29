# examples/demo_conversation.py

# 🚨 ROOT SIGNAL DEMO
# Demonstrates how FPT governs network feedback loops and detects anomalies.

from src.fpt import FeedbackProcessor

fp = FeedbackProcessor()
fp.process_signal("sample network event")