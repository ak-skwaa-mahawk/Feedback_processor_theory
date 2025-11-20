from __future__ import annotations

import json
from typing import Union

from .tag import QuipuTag


def encode_tag(tag: QuipuTag, pretty: bool = False) -> str:
    data = tag.to_dict(include_signature=True)
    if pretty:
        return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2)
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def decode_tag(s: Union[str, bytes]) -> QuipuTag:
    if isinstance(s, bytes):
        s = s.decode("utf-8")
    data = json.loads(s)
    return QuipuTag.from_dict(data)


def canonical_payload(tag: QuipuTag) -> bytes:
    data = tag.without_signature().to_dict(include_signature=False)
    s = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return s.encode("utf-8")