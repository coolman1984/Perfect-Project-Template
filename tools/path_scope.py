#!/usr/bin/env python3
"""Machine-owned path scope classification from TEMPLATE_BASELINE.json.

The baseline manifest, not a hard-coded Python prefix list, is the authority for
Universal Core versus employee project ownership. This keeps the Core Change
Guard usable in copied folders with no Git history.
"""
from __future__ import annotations

import fnmatch
import json
from pathlib import Path
from typing import Any

from tools._common import REPO_ROOT, read_text

BASELINE_PATH = REPO_ROOT / "TEMPLATE_BASELINE.json"


def load_baseline(path: Path | None = None) -> dict[str, Any]:
    target = path or BASELINE_PATH
    if not target.exists():
        raise FileNotFoundError(f"missing template baseline: {target}")
    return json.loads(read_text(target))


def normalize_path(path: str | Path) -> str:
    return str(path).replace("\\", "/").lstrip("./")


def classify_scope(path: str | Path, *, baseline: dict[str, Any] | None = None) -> str:
    value = normalize_path(path)
    data = baseline or load_baseline()
    for rule in data.get("scope_rules", []):
        pattern = str(rule.get("pattern", ""))
        scope = str(rule.get("scope", "unknown"))
        if pattern and fnmatch.fnmatchcase(value, pattern):
            return scope
    return "unknown"


def is_core_owned(path: str | Path, *, baseline: dict[str, Any] | None = None) -> bool:
    return classify_scope(path, baseline=baseline) in {"universal_core", "tooling"}
