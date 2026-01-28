import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

class CouncilConsensus:
    def __init__(self, threshold=3.173):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.epsilon_pi = threshold

    def calculate_resonance(self, responses: dict) -> float:
        """
        Calculates the 5-cloud resonance score based on semantic similarity.
        """
        texts = list(responses.values())
        embeddings = self.model.encode(texts)
        
        # Compute all pairwise similarities (10 pairs for 5 models)
        sim_matrix = cosine_similarity(embeddings)
        indices = np.triu_indices(len(texts), k=1)
        mean_similarity = np.mean(sim_matrix[indices])
        
        # Scale similarity (0-1) to the 5-cloud field (0-5)
        resonance_score = mean_similarity * 5
        return resonance_score

    def is_sealed(self, resonance_score: float) -> bool:
        """True if the council reaches the Epsilon Pi threshold."""
        return resonance_score >= self.epsilon_pi
