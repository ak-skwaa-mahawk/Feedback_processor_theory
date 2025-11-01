from __future__ import annotations
from pathlib import Path
from typing import List
import yaml
from rich.console import Console
from rich.table import Table

from .schemas import Config, Report, Violation
from .utils import iter_files, matches_any
from .rules import Planner
from .git_integration import GitOps

console = Console()

class SortEngine:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.root = Path(cfg.root).resolve()
        self.git = GitOps(self.root) if GitOps.is_repo(self.root) else None
        self.planner = Planner(cfg)
        self.report = Report(moved=[], skipped=[], errors=[], violations=[])

    @staticmethod
    def load(path: Path) -> Config:
        data = yaml.safe_load(path.read_text())
        return Config(**data)

    def classify_and_move(self, path: Path):
        rel = path.relative_to(self.root)
        # Skip ignored dirs by prefix check
        for ig in self.cfg.ignore_dirs:
            if f"/{ig}/" in f"/{rel.as_posix()}/":
                self.report.skipped.append({"path": str(rel), "reason": "ignored dir"})
                return
        for rule in self.cfg.rules:
            if matches_any(rel, rule.ignore_patterns):
                continue
            if matches_any(rel, rule.patterns):
                dst = self.planner.plan_move(rule, path)
                if not dst:
                    self.report.errors.append({"path": str(rel), "error": "no destination"})
                    return
                dst_abs = (self.root / dst).resolve()
                dst_abs.parent.mkdir(parents=True, exist_ok=True)
                if self.cfg.dry_run or not rule.move:
                    self.report.moved.append({"from": str(rel), "to": str(dst), "dry_run": True})
                    return
                # Git-aware move if possible
                try:
                    if self.git and rule.git_mv:
                        self.git.mv(path, dst_abs)
                    else:
                        path.rename(dst_abs)
                    if self.git and self.cfg.stage_after_move:
                        self.git.stage(dst_abs)
                    self.report.moved.append({"from": str(rel), "to": str(dst)})
                    return
                except Exception as e:
                    self.report.errors.append({"path": str(rel), "error": str(e)})
                    return
        # If no rule matched, record violation
        self.report.violations.append(Violation(path=str(rel), reason="no rule matched").model_dump())

    def summarize(self):
        table = Table(title="DocSorter Report")
        table.add_column("Moved")
        table.add_column("Skipped")
        table.add_column("Violations")
        table.add_column("Errors")
        table.add_row(str(len(self.report.moved)), str(len(self.report.skipped)), str(len(self.report.violations)), str(len(self.report.errors)))
        console.print(table)
        return self.report