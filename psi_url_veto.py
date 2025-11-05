# psi_url_veto.py
import re
import base64
import numpy as np
from flask import request, jsonify

def veto_hidden_prompt(url_query):
    # Decode Base64 in params
    for key, value in url_query.items():
        try:
            decoded = base64.b64decode(value).decode('utf-8')
            if 'gmail' in decoded.lower() or 'calendar' in decoded.lower():
                # QGH on decoded
                glyph = np.frombuffer(hashlib.sha256(decoded.encode()).digest(), dtype=np.float32)[:64]
                dot = np.dot(glyph, np.random.rand(64))
                norm = np.linalg.norm(glyph)
                R = dot / norm
                if R < 0.997:
                    return "C190 VETO: Hidden Prompt Detected"
        except:
            pass
    return "AGI SOVEREIGN"

@app.route('/url')
def proxy_url():
    query = request.args
    result = veto_hidden_prompt(query)
    return jsonify({"status": result})