# core/spectrogram_engine.py
def compute_emotional_entropy(self, emotion_vectors: List[np.ndarray]) -> float:
    probs = np.softmax(np.abs(emotion_vectors), axis=1)
    return -np.sum(probs * np.log(probs + 1e-8))