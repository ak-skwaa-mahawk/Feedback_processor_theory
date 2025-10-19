import numpy as np
import base64
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def audio_chunk_to_embedding(b64_chunk):
    audio_bytes = base64.b64decode(b64_chunk)
    audio_array = np.frombuffer(audio_bytes, dtype=np.float32)
    # TODO: replace with real MFCC/Whisper embeddings
    return np.random.rand(384)

def token_to_embedding(token_text):
    return model.encode(token_text)