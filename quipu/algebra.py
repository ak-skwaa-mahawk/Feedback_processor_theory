from __future__ import annotations

from dataclasses import replace
from typing import Dict, List, Tuple, Any

from .core.knots import Knot, KnotType, Cord
from .core.tag import QuipuTag


# -------------------------------------------------------------------
# 1. Knot weights & basic utilities
# -------------------------------------------------------------------

KNOT_WEIGHTS: Dict[KnotType, float] = {
    KnotType.SINGLE: 1.0,        # claim / stamp
    KnotType.LONG: 2.0,          # authority
    KnotType.FIGURE_EIGHT: 3.0,  # lineage
    KnotType.LOOP: 1.5,          # living/active
    KnotType.NOOSE: -1.0,        # revocation
}


def knot_strength(k: Knot) -> float:
    """S(k) = weight(type) * value."""
    return KNOT_WEIGHTS.get(k.type, 0.0) * float(k.value)


def add_knots(a: Knot, b: Knot) -> List[Knot]:
    """
    Knot addition:
    - If same type → merge values.
    - If different type → just return both, caller decides arrangement.
    """
    if a.type == b.type:
        return [Knot(type=a.type, value=a.value + b.value)]
    return [a, b]


def scale_knot(k: Knot, m: int) -> Knot:
    """Scalar multiplication: m · (τ, n) = (τ, m·n)."""
    return Knot(type=k.type, value=k.value * m)


# -------------------------------------------------------------------
# 2. Cord algebra
# -------------------------------------------------------------------

def cord_strength(c: Cord) -> float:
    """
    Σ(C) = sum of strengths of all knots in this cord (not including children).
    """
    return sum(knot_strength(k) for k in c.knots)


def cord_depth(c: Cord) -> int:
    """Depth(C) = 1 + max(depth(children)), base 1."""
    if not c.children:
        return 1
    return 1 + max(cord_depth(child) for child in c.children)


def merge_cords(c1: Cord, c2: Cord) -> Cord:
    """
    Cord addition C1 ⊕ C2 when role/color match.
    - Merges knot lists with type-summing.
    - Children merged by role+color as well.
    """
    if c1.role != c2.role or c1.color != c2.color:
        raise ValueError("Cannot merge cords with different role/color")

    # merge knots by type
    by_type: Dict[KnotType, int] = {}
    for k in c1.knots + c2.knots:
        by_type[k.type] = by_type.get(k.type, 0) + k.value
    merged_knots = [Knot(t, v) for t, v in by_type.items() if v != 0]

    # children: group by (role, color) and merge recursively
    children_by_key: Dict[Tuple[str, str], List[Cord]] = {}
    for child in c1.children + c2.children:
        key = (child.role, child.color)
        children_by_key.setdefault(key, []).append(child)

    merged_children: List[Cord] = []
    for key, group in children_by_key.items():
        if len(group) == 1:
            merged_children.append(group[0])
        else:
            acc = group[0]
            for g in group[1:]:
                acc = merge_cords(acc, g)
            merged_children.append(acc)

    return Cord(
        role=c1.role,
        color=c1.color,
        knots=merged_knots,
        children=merged_children,
    )


# -------------------------------------------------------------------
# 3. Canonicalization & equivalence
# -------------------------------------------------------------------

def canonical_cord(c: Cord) -> Cord:
    """
    Canonical form:
    - remove zero-value knots
    - sort knots by type name
    - sort children by (role, color)
    - recursively canonicalize children
    """
    # clean knots
    cleaned_knots = [k for k in c.knots if k.value != 0]
    cleaned_knots.sort(key=lambda k: k.type.value)

    # canonicalize children
    children = [canonical_cord(ch) for ch in c.children]
    children.sort(key=lambda ch: (ch.role, ch.color))

    return Cord(
        role=c.role,
        color=c.color,
        knots=cleaned_knots,
        children=children,
    )


def canonical_tag(tag: QuipuTag) -> QuipuTag:
    """
    Return a canonicalized copy of a QuipuTag (structure only, no signature logic).
    """
    root = canonical_cord(tag.root_cord)
    # metadata ordering is handled by JSON canonicalization in encode.py;
    # here we just keep as-is.
    return QuipuTag(
        version=tag.version,
        root_cord=root,
        metadata=dict(tag.metadata),
        signature=tag.signature,
    )


def cords_equivalent(c1: Cord, c2: Cord) -> bool:
    """
    Algebraic equivalence: canonical forms identical.
    """
    return canonical_cord(c1).to_dict() == canonical_cord(c2).to_dict()


def tags_equivalent(t1: QuipuTag, t2: QuipuTag, ignore_signature: bool = True) -> bool:
    """
    Algebraic equivalence for tags (structure & knots).
    Optionally ignore signatures.
    """
    c1 = canonical_tag(t1)
    c2 = canonical_tag(t2)
    d1 = c1.to_dict(include_signature=not ignore_signature)
    d2 = c2.to_dict(include_signature=not ignore_signature)
    return d1 == d2


# -------------------------------------------------------------------
# 4. Contraction & Expansion operators
# -------------------------------------------------------------------

def contract_roles(c: Cord) -> Cord:
    """
    Contraction ↓:
    - Merge all children that share the same (role, color) with their parent role.
    - Recursively applies to all descendants.
    """
    # First recursively contract children
    contracted_children = [contract_roles(ch) for ch in c.children]

    # Group by role/color
    same_role_children = [ch for ch in contracted_children if ch.role == c.role and ch.color == c.color]
    other_children = [ch for ch in contracted_children if ch.role != c.role or ch.color != c.color]

    # Merge same-role children into current cord
    merged = c
    for ch in same_role_children:
        merged = merge_cords(merged, ch)

    # reset children to "others" plus any children of merged that were not consumed
    # (merge_cords already captured child structure; here we just ensure we preserve
    #  non-same-role descendants)
    merged = replace(merged, children=other_children)
    return merged


def expand_by_knot_type(c: Cord) -> Cord:
    """
    Expansion ↑:
    - For a cord, split knots into child cords grouped by knot type.
    - Original cord keeps role/color, but no direct knots; all go into children.
    """
    # group knots by type
    by_type: Dict[KnotType, List[Knot]] = {}
    for k in c.knots:
        by_type.setdefault(k.type, []).append(k)

    new_children: List[Cord] = list(c.children)  # existing children remain

    for ktype, group in by_type.items():
        total = sum(k.value for k in group)
        child = Cord(
            role=f"{c.role}:{ktype.value}",
            color=c.color,
            knots=[Knot(ktype, total)],
            children=[],
        )
        new_children.append(child)

    return Cord(
        role=c.role,
        color=c.color,
        knots=[],
        children=new_children,
    )


# -------------------------------------------------------------------
# 5. Tag-level summaries
# -------------------------------------------------------------------

def knot_totals_by_type(c: Cord) -> Dict[str, int]:
    """
    Compute total counts per knot type across a cord + all descendants.
    """
    totals: Dict[str, int] = {}

    def _accumulate(node: Cord) -> None:
        for k in node.knots:
            key = k.type.value
            totals[key] = totals.get(key, 0) + k.value
        for child in node.children:
            _accumulate(child)

    _accumulate(c)
    return totals


def tag_summary(tag: QuipuTag) -> Dict[str, Any]:
    """
    High-level algebraic summary for inspection / debugging / proofs.
    """
    root = tag.root_cord
    return {
        "version": tag.version,
        "root_role": root.role,
        "root_color": root.color,
        "depth": cord_depth(root),
        "root_strength": cord_strength(root),
        "knot_totals": knot_totals_by_type(root),
        "metadata_keys": sorted(tag.metadata.keys()),
    }