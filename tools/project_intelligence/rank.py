"""Task-seeded ranking for the context pack (Constitution Parts 20.8, 20.10).

Personalized PageRank over the file dependency graph, seeded by how well each
file matches the task text. Generated, runtime, vendor and data paths receive
zero rank (Part 20.10), so they can never consume an agent's token budget.
"""

from __future__ import annotations

import re
from pathlib import Path

DAMPING = 0.85
ITERATIONS = 24

# Words too common in this domain to discriminate between files.
STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "for", "of", "in", "on", "is", "it",
    "add", "fix", "change", "update", "make", "with", "from", "when", "that",
    "this", "new", "use", "run", "do", "be", "we", "i", "my", "so", "if",
    "excel", "project", "file", "files", "data",
}

ZERO_RANK_PREFIXES = (
    "runtime/", "offline_packages/", "repair_payload/", "inbox/", "workspace/",
    "data/", "archive/", "output/", "runs/", "logs/", "release/", "web/vendor/",
)

# Task words that reliably imply a layer, so a plain-language task routes even
# when it shares no vocabulary with any filename (Part 20.4).
CONCEPT_ROUTES = {
    "extract": "app/excel/", "extraction": "app/excel/", "com": "app/excel/",
    "workbook": "app/excel/", "sheet": "app/excel/", "chunk": "app/excel/",
    "column": "app/excel/", "value2": "app/excel/",
    "history": "app/data/", "duplicate": "app/data/", "upsert": "app/data/",
    "duckdb": "app/data/", "archive": "app/data/", "migration": "app/data/",
    "parquet": "app/data/", "snapshot": "app/data/",
    "quality": "app/quality/", "check": "app/quality/", "control": "app/quality/",
    "quarantine": "app/quality/", "reconcile": "app/quality/", "total": "app/quality/",
    "kpi": "app/analytics/", "metric": "app/analytics/", "insight": "app/analytics/",
    "calendar": "app/analytics/", "pareto": "app/analytics/",
    "dashboard": "app/dashboard/", "json": "app/dashboard/", "html": "app/dashboard/",
    "chart": "web/", "filter": "web/", "rtl": "web/", "arabic": "web/",
    "theme": "web/", "accessibility": "web/", "motion": "web/", "story": "web/",
    "api": "app/", "server": "app/", "loopback": "app/", "port": "app/",
    "upload": "app/", "progress": "app/", "event": "app/", "state": "app/",
    "contract": "contracts/", "schema": "contracts/", "error": "contracts/",
    "test": "tests/", "golden": "tests/golden/", "fixture": "tests/fixtures/",
    "gate": "acceptance/", "acceptance": "acceptance/", "release": "acceptance/",
    "map": "tools/", "memory": "tools/", "tool": "tools/",
}


def tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {word for word in words if len(word) > 2 and word not in STOPWORDS}


def estimate_tokens(path: Path) -> int:
    """Rough token estimate: ~4 characters per token, floor of 40."""
    try:
        return max(40, path.stat().st_size // 4)
    except OSError:
        return 40


def _seed_scores(task: str, files: list[Path]) -> dict[str, float]:
    task_words = tokenize(task)
    seeds: dict[str, float] = {}

    for relative in files:
        key = str(relative).replace("\\", "/")
        if key.startswith(ZERO_RANK_PREFIXES):
            seeds[key] = 0.0
            continue

        score = 0.0
        path_words = tokenize(key.replace("/", " ").replace("_", " "))
        overlap = task_words & path_words
        score += 6.0 * len(overlap)

        for word, prefix in CONCEPT_ROUTES.items():
            if word in task_words and key.startswith(prefix):
                score += 3.0

        # A small floor keeps every eligible file reachable rather than invisible.
        seeds[key] = score + 0.1

    total = sum(seeds.values()) or 1.0
    return {key: value / total for key, value in seeds.items()}


def rank_files(
    task: str,
    files: list[Path],
    graph: dict[str, set[str]],
    root: Path,
) -> list[tuple[Path, float, str]]:
    """Return [(path, score, reason)] ordered most relevant first."""
    seeds = _seed_scores(task, files)
    nodes = list(seeds)
    if not nodes:
        return []

    scores = dict(seeds)
    out_degree = {node: len(graph.get(node, set())) for node in nodes}

    for _ in range(ITERATIONS):
        contribution = {node: 0.0 for node in nodes}
        for node in nodes:
            degree = out_degree.get(node, 0)
            if not degree:
                continue
            share = scores[node] / degree
            for neighbour in graph.get(node, set()):
                if neighbour in contribution:
                    contribution[neighbour] += share
        scores = {
            node: (1 - DAMPING) * seeds[node] + DAMPING * contribution[node]
            for node in nodes
        }

    task_words = tokenize(task)
    ranked: list[tuple[Path, float, str]] = []
    for node, score in scores.items():
        if node.startswith(ZERO_RANK_PREFIXES):
            continue
        ranked.append((Path(node), score * 1000, _reason(node, task_words, graph)))

    ranked.sort(key=lambda item: (-item[1], str(item[0])))
    return ranked


def _reason(node: str, task_words: set[str], graph: dict[str, set[str]]) -> str:
    reasons: list[str] = []
    path_words = tokenize(node.replace("/", " ").replace("_", " "))
    overlap = sorted(task_words & path_words)
    if overlap:
        reasons.append("matches " + ", ".join(f"`{word}`" for word in overlap[:3]))

    for word, prefix in CONCEPT_ROUTES.items():
        if word in task_words and node.startswith(prefix):
            reasons.append(f"`{word}` routes to `{prefix}`")
            break

    incoming = sum(1 for targets in graph.values() if node in targets)
    if incoming >= 2:
        reasons.append(f"{incoming} dependants")

    return "; ".join(reasons) if reasons else "structural neighbour"
