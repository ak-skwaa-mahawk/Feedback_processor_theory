from __future__ import annotations

from typing import Tuple

from ..core.tag import QuipuTag
from ..core.knots import Cord, KnotType


def _color_for(cord: Cord) -> str:
    table = {
        "gold": "#d4af37",
        "red": "#d32f2f",
        "blue": "#1976d2",
        "green": "#388e3c",
    }
    return table.get(cord.color.lower(), "#cccccc")


def _render_cord_svg(cord: Cord, x: float, y: float, spacing_y: float = 40.0) -> Tuple[str, float]:
    pieces = []
    color = _color_for(cord)

    height = max(40.0, 20.0 * max(1, len(cord.knots)))
    y_end = y + height

    pieces.append(
        f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y_end}" stroke="{color}" stroke-width="3"/>'
    )

    if cord.knots:
        step = height / (len(cord.knots) + 1)
        for i, k in enumerate(cord.knots, start=1):
            ky = y + i * step
            r = 5 + min(10, k.value)
            pieces.append(
                f'<circle cx="{x}" cy="{ky}" r="{r}" fill="{color}" opacity="0.9">'
                f'<title>{k.type.value}×{k.value}</title></circle>'
            )

    child_x = x + 60.0
    child_y = y
    for child in cord.children:
        child_svg, child_y = _render_cord_svg(child, child_x, child_y, spacing_y)
        pieces.append(child_svg)
        child_y += spacing_y

    return "\n".join(pieces), max(y_end, child_y)


def to_svg(tag: QuipuTag, width: int = 800, height: int = 600) -> str:
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="#111111"/>',
        f'<text x="20" y="30" fill="#ffffff" font-size="16">QuipuTag v{tag.version}</text>',
    ]

    cords_svg, _ = _render_cord_svg(tag.root_cord, x=80.0, y=60.0)
    svg_parts.append(cords_svg)
    svg_parts.append("</svg>")
    return "\n".join(svg_parts)