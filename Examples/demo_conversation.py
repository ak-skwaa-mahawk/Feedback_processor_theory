from core.feedback_spectrogram import feedback_spectrogram
from core.feedback_logger import log_feedback
from core.feedback_analyzer import analyze_resonance

conversation = [
    ("You", "Do you want me to give a ready-to-run Git commands script?"),
    ("Me", "Yo kin, you came in hot with this one! 🔥 Ready to push this live?")
]

log_file = log_feedback(conversation)
spec_file = feedback_spectrogram(conversation)
freqs = analyze_resonance(log_file)

print(f"Spectrogram saved to: {spec_file}")
print(f"Top 15 words: {freqs}")