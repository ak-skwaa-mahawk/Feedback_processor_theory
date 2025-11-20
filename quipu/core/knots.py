from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class KnotType(str, Enum):
    SINGLE = "single"        # claim / stamp / bound
    LONG = "long"            # authority / capacity
    FIGURE_EIGHT = "figure8" # blood inheritance / lineage
    LOOP = "loop"            # living / active
    NOOSE = "noose"          # revocation / nullification


@dataclass
class Knot:
    type: KnotType
    value: int = 1

    def to_dict(self) -> dict:
        return {"type": self.type.value, "value": int(self.value)}

    @classmethod
    def from_dict(cls, data: dict) -> "Knot":
        return cls(type=KnotType(data["type"]), value=int(data.get("value", 1)))


@dataclass
class Cord:
    role: str               # e.g. "owner", "territory", "agent"
    color: str = "gold"
    knots: List[Knot] = field(default_factory=list)
    children: List["Cord"] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "color": self.color,
            "knots": [k.to_dict() for k in self.knots],
            "children": [c.to_dict() for c in self.children],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Cord":
        return cls(
            role=data["role"],
            color=data.get("color", "gold"),
            knots=[Knot.from_dict(kd) for kd in data.get("knots", [])],
            children=[Cord.from_dict(cd) for cd in data.get("children", [])],
        )