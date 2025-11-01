from __future__ import annotations
from pathlib import Path
from typing import Optional
from git import Repo, GitCommandError

class GitOps:
    def __init__(self, root: Path):
        self.root = root
        self.repo = Repo(str(root))

    def mv(self, src: Path, dst: Path):
        rel_src = str(src.relative_to(self.root))
        rel_dst = str(dst.relative_to(self.root))
        self.repo.git.mv(rel_src, rel_dst)

    def stage(self, path: Path):
        rel = str(path.relative_to(self.root))
        self.repo.git.add(rel)

    def commit(self, message: str):
        if self.repo.is_dirty(index=True, working_tree=True, untracked_files=True):
            self.repo.index.commit(message)

    @staticmethod
    def is_repo(path: Path) -> bool:
        try:
            Repo(str(path))
            return True
        except Exception:
            return False