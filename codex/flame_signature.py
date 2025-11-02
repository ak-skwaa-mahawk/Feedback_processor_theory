"""
Flame Signature Generator
Two Mile Solutions LLC - FPT
"""

import hashlib, json
from datetime import datetime
from typing import Dict, Any, Optional

class FlameSignature:
    def __init__(self, algorithm: str = "sha256"):
        self.algorithm = algorithm

    def generate(self, entry_data: Dict[str, Any], previous_signature: Optional[str] = None) -> str:
        normalized = self._normalize(entry_data)
        if previous_signature:
            normalized["previous_flame"] = previous_signature
        s = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
        h = hashlib.new(self.algorithm)
        h.update(s.encode("utf-8"))
        return "0x" + h.hexdigest()

    def verify(self, entry_data: Dict[str, Any], signature: str, previous_signature: Optional[str] = None) -> bool:
        return self.generate(entry_data, previous_signature) == signature

    def _normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for k in sorted(data.keys()):
            if k == "flame_signature":
                continue
            v = data[k]
            if isinstance(v, datetime):
                out[k] = v.isoformat()
            else:
                out[k] = v
        return out