from __future__ import annotations
from typing import Dict, Any

from ..core.tag import QuipuTag
from ..algebra import knot_totals_by_type, canonical_tag


def diff_tags(t1: QuipuTag, t2: QuipuTag) -> Dict[str, Any]:
    """
    Compute algebraic differences between two tags.
    Uses:
      - canonical normal form
      - knot totals
    """

    c1 = canonical_tag(t1)
    c2 = canonical_tag(t2)

    k1 = knot_totals_by_type(c1.root_cord)
    k2 = knot_totals_by_type(c2.root_cord)

    diff = {}
    all_keys = set(k1.keys()) | set(k2.keys())
    for k in all_keys:
        diff[k] = k2.get(k, 0) - k1.get(k, 0)

    return {
        "knot_delta": diff,
        "metadata_delta_add": {
            k: v for k, v in c2.metadata.items() if k not in c1.metadata
        },
        "metadata_delta_remove": [
            k for k in c1.metadata.keys() if k not in c2.metadata
        ],
    }