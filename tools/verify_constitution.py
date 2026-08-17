#!/usr/bin/env python3
"""Constitution consistency audit (Constitution Part 34.3, amended by 36.2).

Machine checks only. Part 34.3 is explicit that automation cannot fully
understand meaning: after every material constitution change the agent must
also perform the semantic review against Part 34.2 and record it in
`docs/CONSTITUTION_AUDIT.md`.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from tools._common import EXIT_FAIL, REPO_ROOT, Report, read_text

CONSTITUTION_PATH = REPO_ROOT / "constitution" / "EXCEL_AUTOMATION_CONSTITUTION.md"
CHANGELOG_PATH = REPO_ROOT / "docs" / "CONSTITUTION_CHANGELOG.md"

PART_HEADING = re.compile(r"^## PART (\d+)\b", re.MULTILINE)
PART_REFERENCE = re.compile(r"\bPart (\d+)(?:\.\d+)*\b")
VERSION_LINE = re.compile(r"\*\*Version:\*\*\s*([\d.]+)")

# Language that signals a locked component is being argued away (Part 34.3).
DOWNGRADE_PHRASES = (
    "windows and excel only",
    "excel-only product",
    "serverless local mode",
    "direct windows connection",
    "no-server mode",
    "remove the local server",
    "static html instead",
)


def _load() -> str | None:
    if not CONSTITUTION_PATH.exists():
        return None
    return read_text(CONSTITUTION_PATH)


def check_structure(text: str, report: Report) -> None:
    if text.count("```") % 2 != 0:
        report.fail("unbalanced ``` code fences (Part 34.3)")

    front_matter = text.lstrip().startswith("---")
    if not front_matter:
        report.fail("missing YAML front matter — the constitution doubles as a skill (Part 0.3)")

    parts = [int(number) for number in PART_HEADING.findall(text)]
    if not parts:
        report.fail("no '## PART n' headings found")
        return

    duplicates = {number for number in parts if parts.count(number) > 1}
    if duplicates:
        report.fail(f"duplicate Part numbers: {sorted(duplicates)} (Part 34.3)")

    expected = list(range(min(parts), max(parts) + 1))
    missing = sorted(set(expected) - set(parts))
    if missing:
        report.fail(f"missing Part numbers: {missing} (Part 34.3)")

    if parts != sorted(parts):
        report.fail("Part headings are out of order (Part 34.3)")

    report.note(f"{len(parts)} Parts, {min(parts)}-{max(parts)}, in order")


def check_cross_references(text: str, report: Report) -> None:
    defined = {int(number) for number in PART_HEADING.findall(text)}
    referenced = {int(number) for number in PART_REFERENCE.findall(text)}
    dangling = sorted(referenced - defined)
    if dangling:
        report.fail(f"references to Parts that do not exist: {dangling} (Part 34.3)")
    else:
        report.note(f"{len(referenced)} distinct Part references, all resolve")


FORBIDDING_MARKERS = (
    "forbidden", "never", "reject", "violation", "not permission",
    "does not mean", "do not", "treated as", "must not", "blocked",
    "is itself evidence", "without an approved deviation",
)


def _forbidding_context(lines: list[str], index: int) -> str:
    """Text that governs line `index`, for judging whether a phrase is forbidden.

    Markdown tables put the governing sense in the *header* ("It does **not**
    mean"), which can sit many rows above the offending cell. A fixed character
    window either misses it or grows so large it swallows unrelated prose, so
    we walk back to the header of the containing table instead.
    """
    window = lines[max(0, index - 3):index + 2]
    if lines[index].lstrip().startswith("|"):
        for cursor in range(index - 1, max(-1, index - 40), -1):
            if not lines[cursor].lstrip().startswith("|"):
                break
            window.append(lines[cursor])
    return " ".join(window).lower().replace("*", "").replace("_", " ")


def check_architecture_terms(text: str, report: Report) -> None:
    lowered = text.lower()
    lines = text.splitlines()
    for phrase in DOWNGRADE_PHRASES:
        for match in re.finditer(re.escape(phrase), lowered):
            line_index = lowered[:match.start()].count("\n")
            window = _forbidding_context(lines, line_index)
            # These phrases are legitimate when the governing text forbids them.
            if any(marker in window for marker in FORBIDDING_MARKERS):
                continue
            report.fail(f"line {line_index + 1}: downgrade language '{phrase}' "
                        f"without a forbidding context (Part 34.3)")
    report.note(f"checked {len(DOWNGRADE_PHRASES)} downgrade phrases in context")


def check_commands(text: str, report: Report) -> None:
    """Every named PROJECT_TOOL command group must be reachable (Part 37.3)."""
    # Anchor to line start so that a file-tree row such as
    # "├── PROJECT_TOOL.bat    private project-tool runtime wrapper"
    # is not misread as a command named 'private'. Real command examples in the
    # constitution always begin their line inside a code block.
    named = set(re.findall(r"^\s*PROJECT_TOOL(?:\.bat)?\s+([a-z][a-z-]*)",
                           text, re.MULTILINE))
    try:
        from tools import project_tool
    except ImportError as error:
        report.fail(f"cannot import the dispatcher: {error}")
        return

    parser = project_tool.build_parser()
    implemented: set[str] = set()
    for action in parser._subparsers._group_actions:  # noqa: SLF001 - argparse has no public API
        implemented |= set(action.choices)

    for command in sorted(named - implemented):
        report.fail(f"constitution names 'PROJECT_TOOL {command}' but the "
                    f"dispatcher has no such group (Part 37.3)")

    for group in sorted(implemented - named):
        report.note(f"dispatcher group '{group}' is not named in the constitution")

    report.note(f"{len(named)} command group(s) named, {len(implemented)} implemented")


def check_version_and_changelog(text: str, report: Report) -> None:
    match = VERSION_LINE.search(text)
    if not match:
        report.fail("no '**Version:**' line in the constitution header (Part 36.2)")
        return
    version = match.group(1)
    report.note(f"constitution version {version}")

    if not CHANGELOG_PATH.exists():
        report.fail(f"missing {CHANGELOG_PATH.relative_to(REPO_ROOT)} (Part 36.2)")
        return
    changelog = read_text(CHANGELOG_PATH)
    if version not in changelog:
        report.fail(f"version {version} has no row in CONSTITUTION_CHANGELOG.md (Part 36.2)")

    # The amendment index in Part 36.1 must cover every amended Part.
    parts = {int(number) for number in PART_HEADING.findall(text)}
    amendment_parts = {number for number in parts if number >= 36}
    index_section = text.split("### 36.1")[-1].split("### 36.2")[0] if "### 36.1" in text else ""
    for number in sorted(amendment_parts):
        if number == 36:
            continue
        if f"Part {number}" not in index_section:
            report.warn(f"Part {number} is an amendment but is not listed in the "
                        f"Part 36.1 index")


def cmd_audit() -> int:
    report = Report("constitution audit")
    text = _load()
    if text is None:
        report.fail(f"missing {CONSTITUTION_PATH.relative_to(REPO_ROOT)}")
        return report.emit()

    check_structure(text, report)
    check_cross_references(text, report)
    check_architecture_terms(text, report)
    check_commands(text, report)
    check_version_and_changelog(text, report)

    report.note("Machine checks only. Part 34.3 also requires a semantic review "
                "against Part 34.2, recorded in docs/CONSTITUTION_AUDIT.md.")
    return report.emit()


def _single(title: str, check) -> int:
    report = Report(title)
    text = _load()
    if text is None:
        report.fail(f"missing {CONSTITUTION_PATH.relative_to(REPO_ROOT)}")
        return report.emit()
    check(text, report)
    return report.emit()


def main(args: argparse.Namespace) -> int:
    if args.command == "audit":
        return cmd_audit()
    if args.command == "cross-references":
        return _single("constitution cross-references", check_cross_references)
    if args.command == "architecture-terms":
        return _single("constitution architecture-terms", check_architecture_terms)
    if args.command == "commands":
        return _single("constitution commands", check_commands)
    print(f"usage error: unknown constitution command {args.command!r}")
    return EXIT_FAIL
