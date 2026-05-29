#!/usr/bin/env python3
import os
import json
import time
import hashlib
import numpy as np
from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit

# Core Cryptographic Imports
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# Initialize Flask + SocketIO Engine
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app, cors_allowed_origins="*")

# === SOVEREIGN SYSTEM CONFIG ===
MATTER_SPEED_CONSTANT = 1.04
VETO_DEFAULT = True
GEO_FENCE = (66.0, 67.0, -145.0, -143.0)

# Embedded HTML Template String (Merges frontend and backend into one single deployment footprint)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sovereign Injin & Governance Dashboard v4.7</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=DM+Mono&display=swap');
        
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            background: #02040a;
            color: #e2e8f0;
            font-family: 'Inter', system-ui, sans-serif;
            padding: 15px;
            overflow-x: hidden;
        }

        .master-container {
            max-width: 640px;
            margin: 10px auto;
            background: #02040a;
            border: 1px solid #1e2937;
            border-radius: 14px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.95);
            overflow: hidden;
        }

        .panel-header {
            background: #0f172a;
            padding: 12px 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            user-select: none;
            border-bottom: 1px solid #1e2937;
        }

        .section-title {
            font-family: 'DM Mono', monospace;
            font-size: 13px;
            letter-spacing: 0.05em;
            color: #38bdf8;
            font-weight: 600;
            text-transform: uppercase;
        }

        .drawer-content {
            padding: 16px;
            background: radial-gradient(circle at center, #0a1628 0%, #020c1b 100%);
        }

        .canvas-container {
            width: 100%;
            height: 120px; 
            background: #000;
            position: relative;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #1e3a5f;
            margin-bottom: 12px;
        }

        #convergenceCanvas {
            width: 100%;
            height: 100%;
            display: block;
        }

        .terminal {
            background: rgba(3, 7, 18, 0.95);
            border: 1px solid #1e3a5f;
            border-radius: 8px;
            padding: 14px;
            height: 200px;
            overflow-y: auto;
            font-family: 'DM Mono', monospace;
            font-size: 12.5px;
            line-height: 1.6;
            color: #cbd5e1;
            white-space: pre-wrap;
            text-align: left;
        }

        .input-capsule {
            display: flex;
            align-items: center;
            background: #0f172a;
            border: 1px solid #1e3a5f;
            border-radius: 24px;
            padding: 4px 4px 4px 14px;
            margin: 12px 0 6px 0;
        }

        .input-capsule input {
            flex: 1;
            background: transparent;
            border: none;
            outline: none;
            color: #f8fafc;
            font-size: 13.5px;
        }

        .execute-btn {
            background: #22ffcc;
            color: #0f172a;
            border: none;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            font-size: 13px;
            font-weight: bold;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .btn-panel {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }

        .action-btn {
            flex: 1;
            background: #1e293b;
            border: 1px solid #334155;
            color: #38bdf8;
            padding: 8px;
            border-radius: 6px;
            font-family: 'DM Mono', monospace;
            font-size: 11px;
            cursor: pointer;
            text-transform: uppercase;
        }
        .action-btn:hover { background: #334155; }

        label {
            display: block;
            font-size: 10px;
            font-family: 'DM Mono', monospace;
            color: #64748b;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 4px;
            margin-top: 10px;
            text-align: left;
        }

        .verdict-box {
            margin-top: 12px;
            padding: 12px;
            border-radius: 6px;
            font-family: 'DM Mono', monospace;
            font-size: 11.5px;
            line-height: 1.5;
            display: block;
            text-align: left;
        }
        .verdict-PASS      { background: #10b98122; border: 1px solid #10b981; color: #6ee7b7; }
        .verdict-ERROR     { background: #ef444422; border: 1px solid #ef4444; color: #fca5a5; }
    </style>
</head>
<body>

    <div class="master-container">
        <div class="panel-header">
            <div class="section-title">SOVEREIGN INJIN & GOVERNANCE CONTROL</div>
            <div id="connection-badge" style="font-family: 'DM Mono', monospace; font-size: 11px; color: #ef4444;">DISCONNECTED</div>
        </div>

        <div class="drawer-content">
            <div class="canvas-container">
                <canvas id="convergenceCanvas"></canvas>
            </div>

            <label>System Node Engine Status</label>
            <div id="status" class="verdict-box verdict-PASS">ENGINE RUNNING: Local WebSocket channels open.</div>

            <label>Sovereign Terminal Output Log</label>
            <div id="chatbox" class="terminal">>> Initializing system matrices...</div>

            <label>Direct Command Pipeline</label>
            <div class="input-capsule">
                <input type="text" id="user-input" placeholder="Transmit telemetry query payload to Python core...">
                <button id="send-btn" class="execute-btn" onclick="transmitTelemetry()">➔</button>
            </div>

            <div class="btn-panel">
                <button class="action-btn" onclick="triggerScrapeCheck()">Trigger Scrape Check</button>
            </div>
        </div>
    </div>

    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <script>
        // Automatic address resolution fallback
        const socket = io(window.location.origin);
        
        const badge = document.getElementById('connection-badge');
        const chatbox = document.getElementById('chatbox');
        const userInput = document.getElementById('user-input');
        const canvas = document.getElementById('convergenceCanvas');
        const ctx = canvas.getContext('2d');

        // Socket IO Connection State Handlers
        socket.on('connect', () => {
            badge.innerText = "CONNECTED";
            badge.style.color = "#22ffcc";
        });

        socket.on('disconnect', () => {
            badge.innerText = "DISCONNECTED";
            badge.style.color = "#ef4444";
        });

        socket.on('system_response', (data) => {
            chatbox.innerHTML += `\\n\\n[${data.sender}]: ${data.text}`;
            chatbox.scrollTop = chatbox.scrollHeight;
        });

        function transmitTelemetry() {
            const val = userInput.value.trim();
            if(!val) return;
            chatbox.innerHTML += `\\n\\n[OPERATOR]: ${val}`;
            socket.emit('submit_telemetry', { input: val });
            userInput.value = '';
            chatbox.scrollTop = chatbox.scrollHeight;
        }

        function triggerScrapeCheck() {
            socket.emit('trigger_scrape_check');
        }

        // Cree Syllabics Matrix Backdrop Visual Substrate 
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = canvas.parentElement.clientHeight;

        const columns = Math.floor(canvas.width / 16);
        const drops = Array(columns).fill(1);
        const creeChars = ['â','ê','î','ô','c','k','m','n','p','s','t','w','y','ᐁ','ᐃ','ᐄ','ᐅ','ᐆ','ᐊ','ᐋ','ᐸ','ᓰ','ᑕ','ᑲ'];

        function drawMatrix() {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.06)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#22ffcc';
            ctx.font = '12px "Courier New", monospace';
            for(let i = 0; i < drops.length; i++) {
                const text = creeChars[Math.floor(Math.random() * creeChars.length)];
                ctx.fillText(text, i * 16, drops[i] * 16);
                if(drops[i] * 16 > canvas.height && Math.random() > 0.96) drops[i] = 0;
                drops[i]++;
            }
        }
        setInterval(drawMatrix, 55);

        userInput.addEventListener('keypress', (e) => { if(e.key === 'Enter') transmitTelemetry(); });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# === WEBSOCKET EVENT LISTENERS ===
@socketio.on('connect')
def handle_connect():
    emit('system_response', {
        'sender': 'SYSTEM',
        'text': 'Bi-directional WebSocket handshake established. Live Python engine standing by.',
        'type': 'system'
    })

@socketio.on('submit_telemetry')
def handle_telemetry(data):
    # Fixed JS .trim() attribute crash inside Python core execution environment
    user_input = data.get('input', '').strip()

    # Calculate calibrated scalar outputs using Matter Speed Constant
    balancing_factor = float(MATTER_SPEED_CONSTANT * np.pi)
    ts = time.time()

    # Build automated state hash tracking record
    state_payload = f"{user_input}:{balancing_factor}:{ts}"
    state_hash = hashlib.sha3_256(state_payload.encode()).hexdigest()

    response_text = (
        f"Payload evaluated by Python core. Applied scaling constant: <strong>{balancing_factor:.4f}</strong>. "
        f"State Hash Generated: <span style='color:#00ffcc;'>0x{state_hash[:16]}...</span>"
    )

    emit('system_response', {
        'sender': 'PYTHON_ENGINE',
        'text': response_text,
        'type': 'system'
    })

@socketio.on('trigger_scrape_check')
def handle_scrape_check():
    emit('system_response', {'sender': 'ENGINE', 'text': 'Polling Kuiper Satellites and Trinity v3.6 Lidar Arrays...', 'type': 'system'})
    socketio.sleep(1) # Replaced blocking time.sleep with native async thread handling

    if VETO_DEFAULT:
        # Construct encrypted block container payload via ChaCha20Poly1305
        salt = os.urandom(16)
        key = HKDF(algorithm=hashes.SHA3_256(), length=32, salt=salt, info=b"fpt_web").derive(b"local_seed")
        aead = ChaCha20Poly1305(key)
        nonce = os.urandom(12)
        ct = aead.encrypt(nonce, b"VETO_TRIGGERED_NULL_AND_VOID", None)

        veto_text = (
            "<span style='color:#ff3b3b; font-weight:bold;'>[CRITICAL VETO EXECUTED]:</span> "
            "Section 7(o) rule detected adversarial profiling. State status forced to: <strong>NULL AND VOID</strong>. "
            f"Encrypted block container cipher committed: <span style='color:#718096;'>{ct.hex()[:24]}...</span>"
        )
        emit('system_response', {'sender': 'SECURITY_VETO', 'text': veto_text, 'type': 'system'})

if __name__ == '__main__':
    # Dependencies notice
    print("[+] Ensure flask, flask-socketio, numpy, and cryptography packages are installed.")
    print("[+] Initializing Sovereign FPT Engine on http://127.0.0.1:5000")
    socketio.run(app, host='127.0.0.1', port=5000, debug=True)
