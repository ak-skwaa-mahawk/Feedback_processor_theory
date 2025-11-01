from __future__ import annotations
from pathlib import Path
from typing import Optional
from .schemas import Config, Rule
from .utils import slugify, ensure_dir

class Planner:
    def __init__(self, cfg: Config):
        self.cfg = cfg

    def plan_move(self, rule: Rule, src: Path) -> Optional[Path]:
        name = src.name
        stem = src.stem
        suffix = src.suffix
        if rule.rename_slug:
            base = slugify(stem)
        else:
            base = stem
        if rule.add_prefix:
            base = f"{rule.add_prefix}{base}"
        if rule.add_suffix:
            base = f"{base}{rule.add_suffix}"
        ext = suffix
        if rule.lowercase_ext:
            ext = ext.lower()
        if not rule.preserve_ext:
            ext = ""
        dest_dir = Path(rule.dest)
        ensure_dir(dest_dir)
        return dest_dir / f"{base}{ext}"