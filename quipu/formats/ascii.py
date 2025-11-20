from __future__ import annotations

from typing import List

from ..core.tag import QuipuTag
from ..core.knots import Cord, KnotType


def _knot_symbol(knot_type: KnotType) -> str:
    if knot_type is KnotType.SINGLE:
        return "•"
    if knot_type is KnotType.LONG:
        return "━"
    if knot_type is KnotType.FIGURE_EIGHT:
        return "∞"
    if knot_type is KnotType.LOOP:
        return "○"
    if knot_type is KnotType.NOOSE:
        return "✕"
    return "?"


def _render_cord(cord: Cord, indent: int = 0) -> List[str]:
    pad = "  " * indent
    base = f"{pad}{cord.role} ({cord.color}): "
    if cord.knots:
        knot_str = " ".join(f"{_knot_symbol(k.type)}×{k.value}" for k in cord.knots)
    else:
        knot_str = "[no knots]"
    lines = [base + knot_str]
    for child in cord.children:
        lines.extend(_render_cord(child, indent + 1))
    return lines


def to_ascii(tag: QuipuTag) -> str:
    lines = [f"QuipuTag v{tag.version}"]
    lines.extend(_render_cord(tag.root_cord, indent=0))
    if tag.signature:
        lines.append(f"signature: {tag.signature[:16]}…")
    return "\n".join(lines)