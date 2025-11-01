from __future__ import annotations
import os
from pathlib import Path
import yaml
import typer
from rich import print

from .schemas import Config
from .utils import iter_files
from .sorter import SortEngine
from .watcher import WatchRunner

app = typer.Typer(add_completion=False, no_args_is_help=True)

DEFAULT_CFG = "sorter.yaml"

SAMPLE_CFG = {
    "root": ".",
    "ignore_dirs": [".git", "__pycache__", ".venv", ".mypy_cache", ".github"],
    "concurrent_workers": 8,
    "stage_after_move": True,
    "commit_message": "chore(sort): repo sort + normalize",
    "dry_run": False,
    "rules": [
        {
            "name": "PDFs to /docs/papers",
            "patterns": ["**/*.pdf"],
            "dest": "docs/papers",
            "move": True,
            "git_mv": True,
            "rename_slug": True,
            "preserve_ext": True,
            "lowercase_ext": True,
            "ignore_patterns": ["docs/**"],
        },
        {
            "name": "Images to /assets/images",
            "patterns": ["**/*.png", "**/*.jpg", "**/*.jpeg", "**/*.gif"],
            "dest": "assets/images",
            "move": True,
            "git_mv": True,
        },
        {
            "name": "Notebooks to /notebooks",
            "patterns": ["**/*.ipynb"],
            "dest": "notebooks",
            "move": True,
            "git_mv": True,
        },
        {
            "name": "Markdown to /docs",
            "patterns": ["**/*.md"],
            "dest": "docs",
            "move": True,
            "git_mv": True,
            "ignore_patterns": ["README.md", "docs/**"],
        },
    ],
}

@app.command()
def init(cfg: str = DEFAULT_CFG):
    """Create a starter sorter.yaml."""
    p = Path(cfg)
    if p.exists():
        print(f"[yellow]Config already exists:[/yellow] {p}")
        raise typer.Exit(code=0)
    p.write_text(yaml.safe_dump(SAMPLE_CFG, sort_keys=False))
    print(f"[green]Wrote[/green] {p}")

@app.command()
def sort(cfg: str = DEFAULT_CFG, apply: bool = typer.Option(False, help="apply changes"), dry_run: bool = typer.Option(False, help="simulate only")):
    """Sort the repository per rules. Use --apply to move files."""
    c = SortEngine.load(Path(cfg))
    if dry_run and apply:
        print("[red]Choose either --dry-run or --apply[/red]")
        raise typer.Exit(2)
    c.dry_run = dry_run or not apply
    c.cfg.dry_run = c.dry_run

    # Iterate files
    files = list(iter_files(Path(c.cfg.root).resolve(), c.cfg.ignore_dirs, c.cfg.follow_symlinks))
    for f in files:
        c.classify_and_move(f)

    rep = c.summarize()
    if apply and c.git:
        c.git.commit(c.cfg.commit_message)

@app.command()
def watch(cfg: str = DEFAULT_CFG):
    """Watch repo and auto-apply rules on file events.

    If you want auto-apply, set environment variable DOCSORT_APPLY=1.
    """
    c = SortEngine.load(Path(cfg))
    auto_apply = os.getenv("DOCSORT_APPLY", "0") == "1"
    c.cfg.dry_run = not auto_apply
    runner = WatchRunner(c)
    print("Watching... (Ctrl+C to stop)")
    runner.run()

@app.command("install-hook")
def install_hook(cfg: str = DEFAULT_CFG):
    """Install a pre-commit hook to enforce rules."""
    hook_path = Path(".git/hooks/pre-commit")
    hook_path.parent.mkdir(parents=True, exist_ok=True)
    script = f"""#!/usr/bin/env bash
set -euo pipefail
python -m sorter.cli check || (echo "Structure check failed. Run: docsort sort --apply" && exit 1)
"""
    hook_path.write_text(script)
    hook_path.chmod(0o755)
    print(f"[green]Installed hook:[/green] {hook_path}")

@app.command()
def check(cfg: str = DEFAULT_CFG) -> int:
    """Validate that every file matches at least one rule (non-zero exit on violation)."""
    c = SortEngine.load(Path(cfg))
    c.cfg.dry_run = True
    files = list(iter_files(Path(c.cfg.root).resolve(), c.cfg.ignore_dirs, c.cfg.follow_symlinks))
    for f in files:
        c.classify_and_move(f)
    rep = c.summarize()
    if rep["violations"] if isinstance(rep, dict) else rep.violations:
        print("[red]Violations found[/red]")
        raise typer.Exit(code=1)
    print("[green]OK: structure valid[/green]")
    return 0