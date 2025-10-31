from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/inscription-webhook', methods=['POST'])
def inscription_webhook():
    data = request.json
    inscription_id = data.get('inscription_id')
    resonance = data.get('resonance', 1.0)
    
    # Log to Codex
    entry = {
        "timestamp": "2025-10-30T23:45:00Z",
        "inscription_id": inscription_id,
        "resonance": resonance,
        "source": "Ordinals Hook"
    }
    
    with open("codex/webhook_codex.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    return jsonify({"status": "acknowledged", "resonance": resonance})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/inscription-webhook', methods=['POST'])
def inscription_webhook():
    data = request.json
    inscription_id = data.get('inscription_id')
    resonance = data.get('resonance', 1.0)
    
    # Log to Codex
    entry = {
        "timestamp": "2025-10-30T23:45:00Z",
        "inscription_id": inscription_id,
        "resonance": resonance,
        "source": "Ordinals Hook"
    }
    
    with open("codex/webhook_codex.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    return jsonify({"status": "acknowledged", "resonance": resonance})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)