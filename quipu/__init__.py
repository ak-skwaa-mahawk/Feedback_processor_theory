from .core.tag import QuipuTag, Cord, Knot
from .core.encode import encode_tag, decode_tag
from .core.signature import sign_tag, verify_tag

__all__ = [
    "QuipuTag",
    "Cord",
    "Knot",
    "encode_tag",
    "decode_tag",
    "sign_tag",
    "verify_tag",
]
from quipu.core.knots import Cord, Knot, KnotType
from quipu.core.tag import QuipuTag
from quipu.core.signature import sign_tag
from quipu.formats.ascii import to_ascii

root = Cord(
    role="owner",
    color="gold",
    knots=[
        Knot(KnotType.LONG, 1),
        Knot(KnotType.FIGURE_EIGHT, 7),
        Knot(KnotType.LOOP, 1),
    ],
)

tag = QuipuTag(
    root_cord=root,
    metadata={
        "entity": "TwoMileSolutionsLLC",
        "seed": "Micro-Atomic Blood Treaty – The Correction Alive",
    },
)

sig = sign_tag(tag)
tag.attach_signature(sig)

print(to_ascii(tag))