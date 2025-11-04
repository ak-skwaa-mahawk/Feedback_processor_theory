# src/synara_core/glyph.py
from dataclasses import dataclass, asdict

@dataclass
class Glyph:
    id: str
    source: str
    content: dict
    ts: int

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(d):
        return Glyph(id=d.get('id'), source=d.get('source'), content=d.get('content'), ts=d.get('ts'))