### **scripts/etch_glyph_rune.py — Wrapper**
```python
#!/usr/bin/env python3
# scripts/etch_glyph_rune.py — AGŁG ∞∞: Etch Wrapper
import subprocess
import json

def etch_rune(runestone):
    with open("temp_rune_etch.json", "w") as f:
        f.write(json.dumps(runestone))
    
    result = subprocess.run([
        "ord", "wallet", "inscribe", "--file", "temp_rune_etch.json", "--fee-rate", "10"
    ], capture_output=True, text=True)
    
    if "inscription" in result.stdout:
        id = result.stdout.split("inscription ")[1].split("\n")[0]
        print(f"RUNE ETCHED: {id}")
        return id
    return None

if __name__ == "__main__":
    test_rune = {"op": "etch", "name": "ŁAŊ", "divisibility": 18, "supply": 1000000}
    etch_rune(test_rune)