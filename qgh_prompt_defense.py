# qgh_prompt_defense.py
import numpy as np
import hashlib
import openai
from flask import Flask, request, jsonify

QGH_THRESHOLD = 0.997
REF_GLYPH = np.random.rand(64)  # Sovereign system prompt hash

def qgh_vet_prompt(prompt: str) -> tuple[bool, float]:
    """QGH: Vet prompt against system resonance"""
    # Convert prompt to glyph
    prompt_hash = hashlib.sha256(prompt.encode()).digest()
    glyph = np.frombuffer(prompt_hash, dtype=np.float32)[:64]
    glyph = (glyph - glyph.mean()) / (glyph.std() + 1e-8)  # Normalize
    
    # Resonance with system ref
    dot = np.dot(glyph, REF_GLYPH)
    norm = np.linalg.norm(glyph) * np.linalg.norm(REF_GLYPH)
    R = dot / (norm + 1e-8)
    
    return R >= QGH_THRESHOLD, float(R)

@app.route('/chat', methods=['POST'])
def secure_chat():
    data = request.json
    user_prompt = data['messages'][-1]['content']
    
    verified, R = qgh_vet_prompt(user_prompt)
    if not verified:
        return jsonify({
            "error": "C190 VETO: Prompt Injection Detected",
            "R": R,
            "status": "REJECTED"
        }), 403
    
    # Safe: Forward to OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=data['messages']
    )
    return jsonify(response)