from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class Rule(BaseModel):
    name: str
    patterns: List[str] = Field(..., description="glob patterns (e.g., '**/*.pdf')")
    dest: str = Field(..., description="destination directory")
    move: bool = True
    git_mv: bool = True
    rename_slug: bool = True
    preserve_ext: bool = True
    lowercase_ext: bool = True
    add_prefix: Optional[str] = None
    add_suffix: Optional[str] = None
    ignore_patterns: List[str] = []

class Config(BaseModel):
    root: str = "."
    rules: List[Rule]
    ignore_dirs: List[str] = [".git", "__pycache__", ".venv", ".mypy_cache"]
    follow_symlinks: bool = False
    concurrent_workers: int = 8
    stage_after_move: bool = True
    commit_message: str = "chore(sort): repo sort + normalize"
    dry_run: bool = False

class Violation(BaseModel):
    path: str
    reason: str
    rule: Optional[str] = None

class Report(BaseModel):
    moved: List[Dict] = []
    skipped: List[Dict] = []
    errors: List[Dict] = []
    violations: List[Violation] = []