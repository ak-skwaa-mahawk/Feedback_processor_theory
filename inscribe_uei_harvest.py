import requests, base64, os

PAYMENT_ADDRESS = "bc1pwwwfuj6w7a262wzmajgjknykv9tjtd0nzqjmp3x75ma903c7wcvs27xgx0"
API_KEY = os.getenv("ORDINALSBOT_KEY") or "your_key"

files = {
    "uei_harvest_codex.md": open("uei_harvest_codex.md", "rb").read(),
    "uei_totem.svg": open("uei_totem.svg", "rb").read(),
}

payload = {
    "files": [
        {
            "data": base64.b64encode(files["uei_harvest_codex.md"]).decode(),
            "name": "uei_harvest_codex.md",
            "type": "text/markdown"
        },
        {
            "data": base64.b64encode(files["uei_totem.svg"]).decode(),
            "name": "uei_totem.svg",
            "type": "image/svg+xml"
        }
    ],
    "fee": 20,
    "receiveAddress": PAYMENT_ADDRESS,
    "metadata": {
        "title": "Two Mile UEI Harvest Eternal",
        "description": "UEI KYYKYAWHMH95 activated December 14, 2025 — Sovereign flame through federal gate"
    }
}

headers = {"x-api-key": API_KEY}
r = requests.post("https://api2.ordinalsbot.com/inscribe", json=payload, headers=headers)
print(r.json())