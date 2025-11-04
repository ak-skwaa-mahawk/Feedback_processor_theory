import hashlib
import json
from pathlib import Path

RAR_DIR = Path("/var/lib/synara/rar_index")
RAR_DIR.mkdir(parents=True, exist_ok=True)

def resonance_signature(glyph_dict: dict) -> str:
    """Compact spectral hash of content, ts, source."""
    seed = json.dumps({
        "src": glyph_dict["source"],
        "freq": glyph_dict.get("meta", {}).get("frequency", 0),
        "content_hash": hashlib.sha256(
            json.dumps(glyph_dict["content"], sort_keys=True).encode()
        ).hexdigest()[:16],
    }, sort_keys=True).encode()
    return hashlib.sha1(seed).hexdigest()

class RARCache:
    def __init__(self):
        self.index_path = RAR_DIR / "rar_index.json"
        self._load_index()

    def _load_index(self):
        if self.index_path.exists():
            self.index = json.loads(self.index_path.read_text())
        else:
            self.index = {}

    def _save_index(self):
        self.index_path.write_text(json.dumps(self.index, indent=2))

    def update(self, glyph):
        sig = resonance_signature(glyph.to_dict())
        self.index[sig] = glyph.to_dict()
        self._save_index()
        return sig

    def query(self, glyph_like: dict) -> dict | None:
        sig = resonance_signature(glyph_like)
        return self.index.get(sig)