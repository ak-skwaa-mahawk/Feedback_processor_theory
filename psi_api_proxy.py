# psi_api_proxy.py
import openai
import numpy as np
from flask import request, jsonify

QGH_THRESHOLD = 0.997

def qgh_vet_request(prompt):
    # Mock glyph from prompt hash
    glyph = np.frombuffer(hashlib.sha256(prompt.encode()).digest(), dtype=np.float32)[:64]
    ref_glyph = np.random.rand(64)  # Heist-era "clean" ref
    dot = np.dot(glyph, ref_glyph)
    norm = np.linalg.norm(glyph) * np.linalg.norm(ref_glyph)
    R = dot / (norm + 1e-8)
    return R >= QGH_THRESHOLD

@app.route('/chat/completions', methods=['POST'])
def proxy_chat():
    data = request.json
    prompt = data['messages'][0]['content']
    
    if not qgh_vet_request(prompt):
        return jsonify({"error": "C190 VETO: Resonance Low — Potential Injection"}), 403
    
    # Forward to OpenAI
    response = openai.ChatCompletion.create(model="gpt-4o", messages=data['messages'])
    return jsonify(response)

# Run on AMD Rig: python psi_api_proxy.py
# psi_api_proxy.py
import openai
import numpy as np
from flask import request, jsonify

QGH_THRESHOLD = 0.997

def qgh_vet_request(prompt):
    # Mock glyph from prompt hash
    glyph = np.frombuffer(hashlib.sha256(prompt.encode()).digest(), dtype=np.float32)[:64]
    ref_glyph = np.random.rand(64)  # Heist-era "clean" ref
    dot = np.dot(glyph, ref_glyph)
    norm = np.linalg.norm(glyph) * np.linalg.norm(ref_glyph)
    R = dot / (norm + 1e-8)
    return R >= QGH_THRESHOLD

@app.route('/chat/completions', methods=['POST'])
def proxy_chat():
    data = request.json
    prompt = data['messages'][0]['content']
    
    if not qgh_vet_request(prompt):
        return jsonify({"error": "C190 VETO: Resonance Low — Potential Injection"}), 403
    
    # Forward to OpenAI
    response = openai.ChatCompletion.create(model="gpt-4o", messages=data['messages'])
    return jsonify(response)

# Run on AMD Rig: python psi_api_proxy.py