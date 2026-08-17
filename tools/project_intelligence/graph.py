"""Dependency graph across project files (Constitution Part 20.8).

Python edges come from the stdlib `ast` module. Other supported text formats
contribute edges from explicit path references. Tree-sitter would give richer
symbol-level edges and is an optional accelerator, never a requirement
(Part 37.2 rule 4).
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

# Path-shaped references inside SQL/TOML/JSON/MD/JS/HTML/CSS files.
PATH_REFERENCE = re.compile(r"""["'`(\s]([\w./-]+\.(?:py|sql|toml|json|md|js|css|html))["'`)\s]""")


def _module_to_path(module: str, known: set[str]) -> str | None:
    """Map a dotted module name onto a repo-relative file path, if we own it."""
    candidate = module.replace(".", "/")
    for suffix in (f"{candidate}.py", f"{candidate}/__init__.py"):
        if suffix in known:
            return suffix
    return None


def _python_edges(source: str, path: Path, known: set[str]) -> set[str]:
    edges: set[str] = set()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return edges

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                resolved = _module_to_path(alias.name, known)
                if resolved:
                    edges.add(resolved)
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                # Relative import: resolve against this file's package.
                base = path.parent
                for _ in range(node.level - 1):
                    base = base.parent
                module = str(base).replace("\\", "/")
                if node.module:
                    module = f"{module}/{node.module.replace('.', '/')}"
                for suffix in (f"{module}.py", f"{module}/__init__.py"):
                    if suffix in known:
                        edges.add(suffix)
            elif node.module:
                resolved = _module_to_path(node.module, known)
                if resolved:
                    edges.add(resolved)
    return edges


def build(root: Path, files: list[Path]) -> dict[str, set[str]]:
    """Return {file: {files it depends on}} using repo-relative POSIX paths."""
    known = {str(path).replace("\\", "/") for path in files}
    edges: dict[str, set[str]] = {key: set() for key in known}

    for relative in files:
        key = str(relative).replace("\\", "/")
        absolute = root / relative
        try:
            source = absolute.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        if absolute.suffix == ".py":
            edges[key] |= _python_edges(source, relative, known)

        for match in PATH_REFERENCE.findall(source):
            normalized = match.lstrip("./")
            if normalized in known and normalized != key:
                edges[key].add(normalized)

    return edges


def dependants(graph: dict[str, set[str]], target: str) -> set[str]:
    return {source for source, targets in graph.items() if target in targets}
