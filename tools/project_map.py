#!/usr/bin/env python3
"""Project map: navigation, freshness enforcement, task-ranked context.

Implements Constitution Parts 20.5 (freshness), 20.8 (intelligence engine),
20.9 (commands) and 20.10 (context pack) in the portable tool tier (Part 37).

The map is trusted navigation, not blind authority: it tells an agent which
files to open, and the agent still reads every file it edits (Part 20.6).
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from tools._common import (
    EXIT_FAIL, EXIT_PASS, REPO_ROOT, Report, git_available, git_changed_files,
    iter_source_files, read_text, sha256_file, utc_now,
)
from tools.project_intelligence import graph as pi_graph
from tools.project_intelligence import rank as pi_rank

MANIFEST_PATH = REPO_ROOT / ".ai" / "MAP_MANIFEST.json"
MAP_PATH = REPO_ROOT / ".ai" / "PROJECT_MAP.md"
CONTEXT_PATH = REPO_ROOT / ".ai" / "CONTEXT_PACK.md"
STATE_PATH = REPO_ROOT / ".ai" / "CURRENT_STATE.md"

GENERATED_BEGIN = "<!-- GENERATED:BEGIN file-catalog — PROJECT_TOOL map refresh owns this block -->"
GENERATED_END = "<!-- GENERATED:END file-catalog -->"

# Part 20.2: every agent entry file must exist and point at the same truth.
ENTRY_POINTERS = (
    "AGENTS.md",
    "CLAUDE.md",
    ".clinerules",
    ".github/copilot-instructions.md",
    "PROJECT_SKILL.md",
)

REQUIRED_AI_FILES = (
    ".ai/READ_FIRST.md",
    ".ai/PROJECT_MAP.md",
    ".ai/CURRENT_STATE.md",
    ".ai/CONTRACTS.md",
    ".ai/LESSONS.md",
    ".ai/OPPORTUNITIES.md",
    ".ai/MEMORY.jsonl",
)


# --------------------------------------------------------------------------
# manifest
# --------------------------------------------------------------------------

#: The manifest cannot meaningfully hash itself, and PROJECT_MAP.md's generated
#: block is rewritten by the same refresh that computes the hashes. Including
#: either verbatim makes `verify` fail immediately after every `refresh`.
SELF_REFERENTIAL = {".ai/MAP_MANIFEST.json"}


def _manifest_digest(relative: Path, absolute: Path) -> str:
    """Hash the *authored* content of a file.

    For `.ai/PROJECT_MAP.md` the generated catalog block is stripped first, so
    the manifest tracks the human-written sections — the part that can actually
    drift from reality. The generated block is derived output and is rebuilt
    from the tree on every refresh anyway.
    """
    key = str(relative).replace("\\", "/")
    if key != ".ai/PROJECT_MAP.md":
        return sha256_file(absolute)

    text = read_text(absolute)
    if GENERATED_BEGIN in text and GENERATED_END in text:
        start = text.index(GENERATED_BEGIN)
        end = text.index(GENERATED_END) + len(GENERATED_END)
        text = text[:start] + text[end:]
    import hashlib
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_manifest() -> dict:
    files = iter_source_files()
    entries = {}
    for relative in files:
        key = str(relative).replace("\\", "/")
        if key in SELF_REFERENTIAL:
            continue
        absolute = REPO_ROOT / relative
        entries[key] = {
            "sha256": _manifest_digest(relative, absolute),
            "bytes": absolute.stat().st_size,
        }
    return {
        "schema_version": 1,
        "generated_at": utc_now(),
        "file_count": len(entries),
        "files": entries,
    }


def load_manifest() -> dict | None:
    if not MANIFEST_PATH.exists():
        return None
    try:
        return json.loads(read_text(MANIFEST_PATH))
    except json.JSONDecodeError:
        return None


def diff_manifest(old: dict, new: dict) -> dict[str, list[str]]:
    old_files = old.get("files", {})
    new_files = new.get("files", {})
    added = sorted(set(new_files) - set(old_files))
    removed = sorted(set(old_files) - set(new_files))
    changed = sorted(
        path for path in set(old_files) & set(new_files)
        if old_files[path].get("sha256") != new_files[path].get("sha256")
    )
    return {"added": added, "removed": removed, "changed": changed}


# --------------------------------------------------------------------------
# commands
# --------------------------------------------------------------------------

def cmd_verify() -> int:
    report = Report("map verify")

    for pointer in ENTRY_POINTERS:
        if not (REPO_ROOT / pointer).exists():
            report.fail(f"missing agent entry pointer: {pointer} (Part 20.2)")
    for required in REQUIRED_AI_FILES:
        if not (REPO_ROOT / required).exists():
            report.fail(f"missing project-intelligence file: {required} (Part 20.2)")

    old = load_manifest()
    if old is None:
        report.fail(
            "no readable .ai/MAP_MANIFEST.json — run 'PROJECT_TOOL map refresh --review'")
        return report.emit()

    new = build_manifest()
    delta = diff_manifest(old, new)

    for path in delta["added"]:
        report.fail(f"file exists but is not in the manifest: {path} (Part 20.5)")
    for path in delta["removed"]:
        report.fail(f"manifest lists a file that no longer exists: {path} (Part 20.5)")
    for path in delta["changed"]:
        report.fail(f"file changed since the manifest was refreshed: {path} (Part 20.5)")

    if MAP_PATH.exists():
        map_text = read_text(MAP_PATH)
        if GENERATED_BEGIN not in map_text or GENERATED_END not in map_text:
            report.fail(".ai/PROJECT_MAP.md has no generated-block markers (Part 24.2 rule 1)")
        for referenced in re.findall(r"`([\w./-]+\.(?:py|sql|toml|json|md|js|css|html))`", map_text):
            candidate = REPO_ROOT / referenced
            if "<" in referenced or referenced.endswith("/"):
                continue
            if not candidate.exists() and referenced not in ("PROJECT_SKILL.md",):
                report.warn(f"map references a path that does not exist: {referenced}")

    if STATE_PATH.exists() and "PENDING_APPROVAL" in read_text(STATE_PATH):
        report.note("CURRENT_STATE.md still carries PENDING_APPROVAL items (expected pre-Phase 0)")

    if not delta["added"] and not delta["removed"] and not delta["changed"]:
        report.note(f"manifest matches the working tree ({new['file_count']} files)")

    return report.emit()


def cmd_refresh(review: bool) -> int:
    old = load_manifest() or {"files": {}}
    new = build_manifest()
    delta = diff_manifest(old, new)

    print("=== map refresh ===")
    print(f"  files tracked: {new['file_count']}")
    for label, key in (("added", "added"), ("removed", "removed"), ("changed", "changed")):
        items = delta[key]
        if items:
            print(f"  {label} ({len(items)}):")
            for path in items[:40]:
                print(f"    - {path}")
            if len(items) > 40:
                print(f"    ... and {len(items) - 40} more")

    if review and (delta["added"] or delta["removed"] or delta["changed"]):
        print("\n  --review: the diff above is the change set you are accepting.")
        print("  Part 20.5 rule 7: the manifest updates only after the agent reviews it.")

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(new, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _refresh_map_catalog(new)
    print(f"\n  wrote {MANIFEST_PATH.relative_to(REPO_ROOT)}")
    print(f"  wrote generated catalog block in {MAP_PATH.relative_to(REPO_ROOT)}")
    print("\nmap refresh: PASS")
    return EXIT_PASS


def _refresh_map_catalog(manifest: dict) -> None:
    """Replace only the generated block; human sections are preserved (Part 24.2)."""
    grouped: dict[str, list[str]] = {}
    for path in sorted(manifest["files"]):
        top = path.split("/")[0] if "/" in path else "(root)"
        grouped.setdefault(top, []).append(path)

    lines = [GENERATED_BEGIN, ""]
    lines.append(f"_Generated by `PROJECT_TOOL map refresh` at {manifest['generated_at']}. "
                 f"{manifest['file_count']} tracked files. Do not hand-edit this block._")
    lines.append("")
    for group in sorted(grouped):
        lines.append(f"#### `{group}`")
        lines.append("")
        for path in grouped[group]:
            lines.append(f"- `{path}`")
        lines.append("")
    lines.append(GENERATED_END)
    block = "\n".join(lines)

    if MAP_PATH.exists():
        text = read_text(MAP_PATH)
        if GENERATED_BEGIN in text and GENERATED_END in text:
            start = text.index(GENERATED_BEGIN)
            end = text.index(GENERATED_END) + len(GENERATED_END)
            MAP_PATH.write_text(text[:start] + block + text[end:], encoding="utf-8")
            return
        MAP_PATH.write_text(text.rstrip() + "\n\n" + block + "\n", encoding="utf-8")
        return
    MAP_PATH.parent.mkdir(parents=True, exist_ok=True)
    MAP_PATH.write_text(block + "\n", encoding="utf-8")


def cmd_context(task: str, budget: int) -> int:
    if not 1000 <= budget <= 8000:
        print(f"usage error: --budget must be 1000-8000 (Part 20.10), got {budget}")
        return EXIT_FAIL

    files = iter_source_files()
    dependency_graph = pi_graph.build(REPO_ROOT, files)
    ranked = pi_rank.rank_files(task, files, dependency_graph, REPO_ROOT)

    selected: list[tuple[Path, float, str]] = []
    used = 0
    for path, score, reason in ranked:
        estimate = pi_rank.estimate_tokens(REPO_ROOT / path)
        if used + estimate > budget and selected:
            continue
        selected.append((path, score, reason))
        used += estimate
        if used >= budget:
            break

    lines = [
        "# CONTEXT PACK (generated)",
        "",
        f"- **Task:** {task}",
        f"- **Generated:** {utc_now()}",
        f"- **Budget:** {budget} tokens · **Estimated selected:** ~{used} tokens",
        "- **Generator:** `PROJECT_TOOL map context`",
        "",
        "> Regenerate this per task. It is a ranked *starting point*: read every file",
        "> you edit, plus its direct contracts and tests (Part 20.6). Expand one",
        "> dependency boundary at a time and record why (Part 0.2).",
        "",
        "## Ranked files",
        "",
        "| # | File | Score | Why it ranked |",
        "|---:|---|---:|---|",
    ]
    for index, (path, score, reason) in enumerate(selected, start=1):
        lines.append(f"| {index} | `{path}` | {score:.2f} | {reason} |")

    lines += ["", "## Contracts at risk", ""]
    contracts = [p for p, _, _ in selected if str(p).startswith(("contracts/", "reports/"))]
    if contracts:
        lines += [f"- `{p}`" for p in contracts]
    else:
        lines.append("- None ranked. If your change alters a public shape, open `.ai/CONTRACTS.md`.")

    lines += ["", "## Tests to run", ""]
    tests = [p for p, _, _ in selected if str(p).startswith("tests/")]
    if tests:
        lines += [f"- `{p}`" for p in tests]
    else:
        lines.append("- None ranked directly. Run the suite for the layer you touched.")

    lines += [
        "",
        "## Before you report done",
        "",
        "```text",
        "PROJECT_TOOL map verify",
        "PROJECT_TOOL architecture verify --source-scan",
        "PROJECT_TOOL constitution audit",
        "PROJECT_TOOL gates status",
        "```",
        "",
    ]

    CONTEXT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONTEXT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"=== map context ===\n  task: {task}")
    print(f"  ranked {len(ranked)} files, selected {len(selected)} within ~{used}/{budget} tokens")
    print(f"  wrote {CONTEXT_PATH.relative_to(REPO_ROOT)}")
    print("\nmap context: PASS")
    return EXIT_PASS


def cmd_explain(path_arg: str) -> int:
    target = Path(path_arg)
    absolute = REPO_ROOT / target
    report = Report(f"map explain {target}")
    if not absolute.exists():
        report.fail(f"path does not exist: {target}")
        return report.emit()

    files = iter_source_files()
    dependency_graph = pi_graph.build(REPO_ROOT, files)
    key = str(target).replace("\\", "/")

    print(f"=== map explain: {key} ===")
    print(f"  size: {absolute.stat().st_size} bytes")
    print(f"  sha256: {sha256_file(absolute)[:16]}...")

    imports = dependency_graph.get(key, set())
    print(f"\n  imports / references ({len(imports)}):")
    for dependency in sorted(imports):
        print(f"    -> {dependency}")

    dependants = sorted(src for src, dsts in dependency_graph.items() if key in dsts)
    print(f"\n  depended on by ({len(dependants)}):")
    for dependant in dependants:
        print(f"    <- {dependant}")

    related_tests = [str(p) for p in files
                     if str(p).startswith("tests/") and target.stem in str(p)]
    print(f"\n  likely tests ({len(related_tests)}):")
    for test in related_tests:
        print(f"    *  {test}")
    if not related_tests:
        print("    (none found by name — Part 20.3 requires every important file to name its tests)")

    print("\nmap explain: PASS")
    return EXIT_PASS


def cmd_changed(base: str) -> int:
    report = Report(f"map changed --base {base}")
    if not git_available():
        report.block("git is not available, cannot compute a change set")
        return report.emit()

    changed = git_changed_files(base)
    if not changed:
        report.note(f"no tracked changes against {base}")
        return report.emit()

    report.note(f"{len(changed)} changed file(s) against {base}")
    routes = {
        "app/excel/": "extraction tests + protected-file fixture + cleanup test (Part 20.4)",
        "app/data/": "history rerun/correction tests + migration review (Part 20.4)",
        "app/quality/": "quality rule tests + population equation (Part 25.3)",
        "app/analytics/": "golden tests + metric registry version (Part 10.2)",
        "app/dashboard/": "JSON contract + browser/offline verification (Part 11.5)",
        "web/": "browser tests: keyboard, RTL, theme, print (Part 26.10)",
        "contracts/": "contract version bump + every consumer (Part 25.7)",
        "reports/": "report validate + golden tests (Part 41)",
        "constitution/": "constitution audit + changelog entry (Part 36.2)",
        "tools/": "tool self-tests + map verify",
    }
    for path in changed:
        matched = [advice for prefix, advice in routes.items() if path.startswith(prefix)]
        report.note(f"{path} -> {matched[0] if matched else 'no route; add one to Part 20.4'}")

    report.note("Also required in the same change set: tests, contracts, "
                ".ai/CURRENT_STATE.md, map refresh (Part 21.5)")
    return report.emit()


def cmd_doctor() -> int:
    report = Report("map doctor")
    report.note(f"repo root: {REPO_ROOT}")
    report.note(f"git available: {git_available()}")
    report.note(f"manifest present: {MANIFEST_PATH.exists()}")

    try:
        import ast  # noqa: F401
        report.note("python AST parser: available (baseline structural parsing)")
    except ImportError:  # pragma: no cover
        report.fail("python AST parser unavailable")

    try:
        import tree_sitter  # noqa: F401
        report.note("tree-sitter: available (optional accelerator)")
    except ImportError:
        report.note("tree-sitter: absent — degrading to stdlib AST parsing, "
                    "which is expected and not a failure (Part 37.2 rule 4)")

    files = iter_source_files()
    report.note(f"source files discoverable: {len(files)}")
    if not files:
        report.fail("no source files found — is this the repository root?")
    return report.emit()


def main(args: argparse.Namespace) -> int:
    command = args.command
    if command == "verify":
        return cmd_verify()
    if command == "refresh":
        return cmd_refresh(review=getattr(args, "review", False))
    if command == "context":
        return cmd_context(args.task, args.budget)
    if command == "explain":
        return cmd_explain(args.path)
    if command == "changed":
        return cmd_changed(args.base)
    if command == "doctor":
        return cmd_doctor()
    print(f"usage error: unknown map command {command!r}")
    return EXIT_FAIL
