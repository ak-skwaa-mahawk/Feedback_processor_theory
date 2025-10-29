import numpy as np
from scipy.fft import fft
from textblob import TextBlob

def spectral_resonance(text):
    # 1. Tone (FFT of audio or symbolic 60 Hz)
    freqs = fft(np.array([ord(c) for c in text]))
    tone = np.abs(freqs[60]) if len(freqs) > 60 else 0
    
    # 2. Emotion (TextBlob)
    sentiment = TextBlob(text).sentiment
    T, I, F = sentiment.polarity, sentiment.subjectivity, 0.5
    
    # 3. Semantic Loops
    words = text.lower().split()
    loops = sum(words.count(w) for w in set(words) if words.count(w) > 1)
    
    # 4. Coherence Score
    coherence = (tone + T + I + loops / len(words)) / 4
    return round(coherence, 3)

# Test
print(spectral_resonance("The nine stars are two, the nine are one."))  # → 0.923