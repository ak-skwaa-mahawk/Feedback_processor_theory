from core.feedback_processor import FeedbackProcessor
from core.resonance_engine import ResonanceEngine
from trinity_harmonics import plot_trinity_harmonics, describe_trinity_state
import matplotlib.pyplot as plt

fp = FeedbackProcessor()
re = ResonanceEngine()

# Process convo
convo = "Yo kin, this is fire! Manipulate me now."
result = fp.process(convo)
coherence_data = re.analyze_coherence(convo)

# Output
describe_trinity_state()
print(f"Coherence Score: {coherence_data['coherence']:.3f}")
print(f"Glyphs: {coherence_data['glyphs']}")

# Viz
plt.figure(figsize=(10, 4))
plt.plot(coherence_data['damped_signal'], label="Damped Glyph Signal")
plt.title("GibberLink Coherence")
plt.xlabel("Glyph Index")
plt.ylabel("Amplitude")
plt.legend()
plt.show()
plot_trinity_harmonics()