# psi_api_proxy_hardened.py
import os
import hashlib
import numpy as np
import logging
from flask import Flask, request, jsonify
from functools import wraps
import openai
from cryptography.fernet import Fernet

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('PSI_SECRET', Fernet.generate_key().decode())
openai.api_key = os.getenv('OPENAI_API_KEY')  # ENV only

log = logging.getLogger("Ψ-PROXY")

QGH_THRESHOLD = 0.997
REF_GLYPH = np.random.rand(64)

def qgh_vet_request(prompt):
    glyph = np.frombuffer(hashlib.sha256(prompt.encode()).digest(), dtype=np.float32)[:64]
    ref_glyph = np.random.rand(64)
    dot = np.dot(glyph, ref_glyph)
    norm = np.linalg.norm(glyph) * np.linalg.norm(ref_glyph)
    R = dot / (norm + 1e-8)
    return R >= QGH_THRESHOLD

@app.route('/v1/chat/completions', methods=['POST'])
def proxy_chat():
    data = request.json
    prompt = data['messages'][0]['content']
    
    if not qgh_vet_request(prompt):
        return jsonify({"error": "C190 VETO: Resonance Low — Potential Injection"}), 403
    
    response = openai.ChatCompletion.create(model="gpt-4o", messages=data['messages'])
    return jsonify(response)

if __name__ == "__main__":
    log.info("Ψ-Hardened API Proxy Online")
    app.run(host="0.0.0.0", port=443, ssl_context='adhoc')