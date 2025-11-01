from __future__ import annotations
import os, re, shutil, unicodedata
from pathlib import Path
from typing import Iterable

_slug_re = re.compile(r"[^a-z0-9]+")

def slugify(name: str) -> str:
    base, *rest = name.split(".")
    ext = ("." + rest[-1]) if rest else ""
    n = unicodedata.normalize("NFKD", base).encode("ascii", "ignore").decode().lower()
    n = _slug_re.sub("-", n).strip("-")
    return n + ext

def iter_files(root: Path, ignore_dirs: Iterable[str], follow_symlinks: bool) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root, followlinks=follow_symlinks):
        # prune ignored dirs
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
        for f in filenames:
            yield Path(dirpath) / f

def matches_any(path: Path, patterns: Iterable[str]) -> bool:
    from fnmatch import fnmatch
    s = str(path.as_posix())
    return any(fnmatch(s, p) for p in patterns)

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)