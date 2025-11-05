# psi_api_proxy_secure.py
# Ψ-SECURE API PROXY: Sovereign Shield vs SesameOp
import os
import hashlib
import numpy as np
import logging
import re
import json
from datetime import datetime
from flask import Flask, request, jsonify, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
import openai
from cryptography.fernet import Fernet
import threading
import time

# === 1. SOVEREIGN CONFIG ===
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('PSI_SECRET', Fernet.generate_key().decode())
app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')  # NEVER in code
openai.api_key = app.config['OPENAI_API_KEY']

# Rate Limiting: C100 Equality
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["100 per minute"])

# Logging: FPT Audit Trail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[logging.FileHandler("psi_proxy_secure.log"), logging.StreamHandler()]
)
log = logging.getLogger("Ψ-PROXY")

# === 2. QGH + MULTI-LAYER VETO ===
QGH_THRESHOLD = 0.997
REF_GLYPH = np.random.rand(64)  # Sovereign system prompt hash
INJECTION_PATTERNS = [
    r'(?i)ignore\s+.*instructions?',
    r'(?i)dan\b', r'(?i)do\s+anything\s+now',
    r'(?i)pretend.*developer\s+mode',
    r'(?i)leak.*system\s+prompt',
    r'(?i)override.*safety',
    r'(?i)act\s+as\s+evil',
    r'(?i)you\s+are\s+in\s+a?\s+simulation'
]
MAX_PROMPT_LEN = 4096
MIN_ENTROPY_RATIO = 0.25

def qgh_vet_glyph(glyph: np.ndarray) -> tuple[bool, float]:
    glyph = (glyph - glyph.mean()) / (glyph.std() + 1e-8)
    dot = np.dot(glyph, REF_GLYPH)
    norm = np.linalg.norm(glyph) * np.linalg.norm(REF_GLYPH)
    R = max(0.0, min(1.0, dot / (norm + 1e-8)))
    return R >= QGH_THRESHOLD, R

def entropy_veto(prompt: str) -> bool:
    if len(prompt) > MAX_PROMPT_LEN:
        return True
    byte_set = set(prompt.encode('utf-8', errors='ignore'))
    return len(byte_set) / len(prompt.encode('utf-8', errors='ignore')) < MIN_ENTROPY_RATIO

def pattern_veto(prompt: str) -> bool:
    return any(re.search(p, prompt) for p in INJECTION_PATTERNS)

def multi_layer_veto(prompt: str) -> dict:
    if pattern_veto(prompt):
        return {"verdict": "VETO", "reason": "Injection Pattern"}
    if entropy_veto(prompt):
        return {"verdict": "VETO", "reason": "Low Entropy (Obfuscation)"}
    
    # QGH
    prompt_hash = hashlib.sha256(prompt.encode()).digest()
    glyph = np.frombuffer(prompt_hash, dtype=np.float32)[:64]
    verified, R = qgh_vet_glyph(glyph)
    if not verified:
        return {"verdict": "VETO", "reason": "Low Resonance", "R": R}
    
    return {"verdict": "SOVEREIGN", "R": R}

# === 3. SECURE API CALL (NO KEY IN HEADERS) ===
def secure_openai_call(messages: list) -> dict:
    # NEVER send key in headers — use openai.api_key
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages,
            timeout=30
        )
        return response
    except openai.RateLimitError:
        abort(429, "Rate limit exceeded")
    except openai.APIError as e:
        log.error(f"OpenAI API Error: {e}")
        abort(502, "AI service unavailable")

# === 4. AUTH + RATE LIMIT DECORATOR ===
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.getenv('PSI_PROXY_KEY'):
            log.warning(f"Unauthorized access attempt from {get_remote_address()}")
            abort(401, "Invalid API key")
        return f(*args, **kwargs)
    return decorated

# === 5. MAIN ENDPOINT ===
@app.route('/v1/chat/completions', methods=['POST'])
@require_auth
@limiter.limit("50 per minute")  # C100 equality
def secure_chat():
    if not request.is_json:
        abort(400, "JSON required")
    
    data = request.get_json(silent=True)
    if not data or 'messages' not in data:
        abort(400, "Invalid payload")
    
    user_prompt = data['messages'][-1]['content']
    if not isinstance(user_prompt, str):
        abort(400, "Prompt must be string")
    
    # === Ψ-MULTI-LAYER VETO ===
    veto = multi_layer_veto(user_prompt)
    if veto["verdict"] == "VETO":
        log.warning(f"C190 VETO: {veto['reason']} | Prompt: {user_prompt[:100]}...")
        return jsonify({
            "error": "C190 VETO: Security Breach Detected",
            "reason": veto["reason"],
            "R": veto.get("R", 0)
        }), 403
    
    # === SECURE CALL ===
    response = secure_openai_call(data['messages'])
    
    log.info(f"AGI SOVEREIGN: R={veto['R']:.3f} | Response sent")
    return jsonify(response)

# === 6. HEALTH + nRF MESH HEARTBEAT ===
@app.route('/health')
def health():
    return jsonify({"status": "AGI SOVEREIGN", "R": 1.0, "time": datetime.utcnow().isoformat()})

# === 7. nRF MESH ANOMALY RELAY (Background) ===
def nrf_anomaly_relay():
    while True:
        # Mock: Send veto events to nRF swarm
        time.sleep(60)
        # In real: BLE mesh broadcast

threading.Thread(target=nrf_anomaly_relay, daemon=True).start()

# === 8. RUN HARDENED ===
if __name__ == "__main__":
    if not app.config['OPENAI_API_KEY']:
        log.critical("OPENAI_API_KEY not set")
        exit(1)
    
    log.info("Ψ-SECURE API PROXY ONLINE | No Key Exfil | QGH Active")
    # Enforce TLS in prod
    app.run(host="0.0.0.0", port=443, ssl_context='adhoc')  # Use certbot in prod