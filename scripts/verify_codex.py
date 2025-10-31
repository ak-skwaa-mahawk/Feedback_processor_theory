#!/usr/bin/env python3
# scripts/verify_codex.py — AGŁG ∞⁹: Verify FPT Codex
import requests
import json

def verify_inscription(inscription_id):
    response = requests.get(f"https://ordinals.com/api/inscription/{inscription_id}")
    if response.status_code == 200:
        artifact = response.json()
        R = float(artifact.get("resonance", 0.0))
        return {"verified": True, "R": R}
    return {"verified": False}

if __name__ == "__main__":
    test_id = "i999fptordv2"
    print(verify_inscription(test_id))