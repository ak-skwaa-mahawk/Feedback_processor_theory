import sys
msg = sys.argv[1] if len(sys.argv) > 1 else "Default message"
print(f"Feedback loop processed message: {msg}")
