import requests, base64, json, os

# Your BTC receive address (for change/fees)
PAYMENT_ADDRESS = "bc1q..."  # ← PUT YOURS HERE

# OrdinalsBot API key (get free at ordinalsbot.com)
API_KEY = os.getenv("ORDINALSBOT_KEY") or "YOUR_KEY_HERE"

# Files
files = {
    "totem_codex.md": open("totem_codex.md", "rb").read(),
    "totem_pole.svg": open("totem_pole.svg", "rb").read(),
}

payload = {
    "files": [
        {
            "data": base64.b64encode(files["totem_codex.md"]).decode(),
            "name": "totem_codex.md",
            "type": "text/markdown"
        },
        {
            "data": base64.b64encode(files["totem_pole.svg"]).decode(),
            "name": "totem_pole.svg",
            "type": "image/svg+xml"
        }
    ],
    "fee": 20,  # sat/vB — raise for speed
    "receiveAddress": PAYMENT_ADDRESS,
    "metadata": {
        "title": "Totem Glyph Codex: Sovereign Flame-Wire Eternal",
        "description": "AGŁL Trinity · Teotl Flux · Vhitzee Locked · Quetzalcoatl Code 813667"
    }
}

headers = {"x-api-key": API_KEY}

r = requests.post("https://api2.ordinalsbot.com/inscribe", json=payload, headers=headers)
print(json.dumps(r.json(), indent=2))