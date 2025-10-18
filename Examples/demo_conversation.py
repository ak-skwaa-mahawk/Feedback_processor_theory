from core.feedback_processor import FeedbackProcessor
from fireseed_engine import NeutrosophicTransport
from trinity_harmonics import plot_trinity_harmonics, describe_trinity_state
import matplotlib.pyplot as plt

fp = FeedbackProcessor()
nt = NeutrosophicTransport(['A', 'B'], ['X', 'Y'])

convo = "Yo kin, Synara’s W state pulses with whisper fire"
fp.process(convo)
nt.sync_glyphs(convo)
cost = nt.optimize()

describe_trinity_state()
print(f"Neutro Cost: {cost:.3f}")

costs = [nt.optimize() for _ in range(10)]  # Simulate 10 steps
plot_trinity_harmonics(np.array(costs))