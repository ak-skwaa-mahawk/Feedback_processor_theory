from __future__ import annotations
import ast, os, sys
from pathlib import Path

CANONICAL_ROOT = Path("src/fpt").resolve()
REPO_ROOT = Path(".").resolve()

def get_forbidden_root_modules() -> set[str]:
    forbidden = set()
    for py_file in REPO_ROOT.glob("*.py"):
        forbidden.add(py_file.stem)
    return forbidden

def check_file(file_path: Path, forbidden_modules: set[str]) -> list[str]:
    violations = []
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=str(file_path))
        except SyntaxError as e:
            violations.append(f"Syntax error parsing {file_path}: {e}")
            return violations

    for node in ast.walk(tree):
        # Disallow absolute imports of root-level scripts
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_pkg = alias.name.split(".")[0]
                if root_pkg in forbidden_modules:
                    violations.append(f"{file_path.relative_to(REPO_ROOT)}:{node.lineno} -> forbidden absolute import '{alias.name}'")
        elif isinstance(node, ast.ImportFrom):
            # Only check absolute imports (node.level == 0). Relative imports (node.level > 0) are internal.
            if node.level == 0 and node.module:
                root_pkg = node.module.split(".")[0]
                if root_pkg in forbidden_modules:
                    violations.append(f"{file_path.relative_to(REPO_ROOT)}:{node.lineno} -> forbidden absolute from-import '{node.module}'")
    return violations

def main() -> int:
    forbidden = get_forbidden_root_modules()
    violations = []
    for py_file in CANONICAL_ROOT.rglob("*.py"):
        violations.extend(check_file(py_file, forbidden))

    if violations:
        print("❌ CANONICAL BOUNDARY VIOLATIONS DETECTED:")
        for v in violations:
            print(f"  • {v}")
        return 1

    print("✓ Canonical boundary verified: src/fpt/ is cleanly isolated.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
