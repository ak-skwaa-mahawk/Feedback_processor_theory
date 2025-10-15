import json
from collections import Counter

def analyze_resonance(log_path):
    """Analyze conversation log for word frequency patterns."""
    with open(log_path) as f:
        log = json.load(f)
    words = " ".join([text for _, text in log["conversation"]]).split()
    freq = Counter(words)
    return freq.most_common(15)