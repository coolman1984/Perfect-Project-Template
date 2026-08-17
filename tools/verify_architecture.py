#!/usr/bin/env python3
"""Architecture compliance verifier (Constitution Parts 0.8, 23.10, 44).

This is the tool that stops the two failure modes the constitution spends the
most words forbidding: silently deleting a locked component to make the app
"simpler/more portable", and quietly reaching for the network at runtime.

Scanning boundary: executable code, launchers, runtime web assets and
configuration. Markdown documentation is NOT scanned for URLs — Part 23.10
explicitly allows reference hyperlinks as text and warns against mistaking them
for runtime network calls.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from tools._common import (
    EXIT_FAIL, EXIT_PASS, REPO_ROOT, Report, iter_source_files, read_text,
)

BASELINE_PATH = REPO_ROOT / "IMPLEMENTATION_BASELINE.lock.json"

# Suffixes that can actually execute or be loaded at runtime.
EXECUTABLE_SUFFIXES = {".py", ".js", ".bat", ".sh", ".ps1", ".html", ".css"}

REMOTE_URL = re.compile(r"""["'(=\s](https?://[^\s"'`)<>]+)""", re.IGNORECASE)
ALLOWED_URL_HOSTS = (
    "127.0.0.1", "localhost", "www.w3.org",           # loopback + SVG/XML namespaces
    "schemas.microsoft.com", "json-schema.org",
)

DOWNLOAD_COMMANDS = re.compile(
    r"\b(pip\s+install|pip3\s+install|npm\s+install|npm\s+i\b|yarn\s+add|"
    r"curl\s+-|wget\s+|Invoke-WebRequest|iwr\s|Start-BitsTransfer|"
    r"nuget\s+install|choco\s+install|winget\s+install)",
    re.IGNORECASE,
)
# `pip install --no-index --find-links` against the local wheelhouse is the
# approved developer rebuild path (Part 23.6) and is not a runtime download.
OFFLINE_PIP = re.compile(r"--no-index|--find-links", re.IGNORECASE)

FORBIDDEN_BIND = re.compile(
    r"""["']0\.0\.0\.0["']|["']::["']|["']\[::\]["']|host\s*=\s*["']0\.0\.0\.0["']""")
PRIVILEGED_PORT = re.compile(r"""\bport\s*[=:]\s*(80|443)\b""", re.IGNORECASE)

ELEVATION = re.compile(
    r"\b(requireAdministrator|highestAvailable|runas\s|netsh\s+advfirewall|"
    r"netsh\s+http\s+add\s+urlacl|New-Service|sc\.exe\s+create|Register-ScheduledTask)\b",
    re.IGNORECASE,
)

SECRET_PATTERN = re.compile(
    r"""(password|pwd|api[_-]?key|secret|access[_-]?token)\s*[=:]\s*["'][^"'{}$<>\s]{6,}["']""",
    re.IGNORECASE,
)
# Placeholders in templates are the correct way to show shape without a secret.
SECRET_PLACEHOLDER = re.compile(
    r"PENDING_APPROVAL|CHANGE_ME|<[^>]+>|\$\{[^}]+\}|%[A-Z_]+%|INTEGRATED|EXAMPLE",
    re.IGNORECASE,
)

COM_IMPORTS = re.compile(r"\b(import\s+win32com|from\s+win32com|import\s+pythoncom|"
                         r"import\s+win32api|from\s+win32api)\b")


#: This file necessarily contains every pattern it searches for, so it is the
#: one file excluded from its own scans. Everything else, including the rest of
#: the tool tier, is scanned.
SCANNER_SELF = "tools/verify_architecture.py"


def _scan_targets() -> list[Path]:
    return [
        p for p in iter_source_files()
        if p.suffix in EXECUTABLE_SUFFIXES
        and str(p).replace("\\", "/") != SCANNER_SELF
    ]


def _is_runtime_web_asset(path: Path) -> bool:
    return str(path).startswith("web/") and path.suffix in {".html", ".css", ".js"}


def _docstring_lines(path: Path, text: str) -> set[int]:
    """1-based line numbers covered by Python docstrings.

    Part 23.10 already establishes the principle: documentation that *mentions*
    a forbidden thing is not the forbidden thing. A doctest proving that
    ``0.0.0.0`` is rejected, or a checklist saying "never run pip install", is
    documentation. Scanning it produces false positives, and a verifier that
    cries wolf is one that gets ignored.

    Executable code is still scanned in full — this only exempts docstrings,
    which cannot execute.
    """
    if path.suffix != ".py":
        return set()

    import ast as _ast
    try:
        tree = _ast.parse(text)
    except SyntaxError:
        return set()

    covered: set[int] = set()
    for node in _ast.walk(tree):
        if not isinstance(node, (_ast.Module, _ast.ClassDef,
                                 _ast.FunctionDef, _ast.AsyncFunctionDef)):
            continue
        body = getattr(node, "body", None)
        if not body:
            continue
        first = body[0]
        if (isinstance(first, _ast.Expr)
                and isinstance(first.value, _ast.Constant)
                and isinstance(first.value.value, str)):
            end = first.end_lineno or first.lineno
            covered.update(range(first.lineno, end + 1))
    return covered


def check_no_remote_assets(report: Report) -> None:
    """Part 23.10: no CDN, remote font, icon, telemetry or API in runtime code."""
    for relative in _scan_targets():
        if str(relative).startswith(("tools/", "tests/", "scripts/")):
            continue
        text = read_text(REPO_ROOT / relative)
        for url in REMOTE_URL.findall(text):
            if any(host in url for host in ALLOWED_URL_HOSTS):
                continue
            line = next((i for i, l in enumerate(text.splitlines(), 1) if url in l), 0)
            severity = report.fail if _is_runtime_web_asset(relative) else report.warn
            severity(f"{relative}:{line} remote URL in runtime code: {url} (Part 23.10)")


def check_no_runtime_downloads(report: Report) -> None:
    """Part 23.6: no run command may download a package, browser or asset."""
    for relative in _scan_targets():
        if str(relative).startswith("tests/"):
            continue
        text = read_text(REPO_ROOT / relative)
        documentation = _docstring_lines(relative, text)
        for lineno, line in enumerate(text.splitlines(), start=1):
            if lineno in documentation:
                continue
            if line.lstrip().startswith(("#", "//", "rem ", "REM ", "::")):
                continue
            match = DOWNLOAD_COMMANDS.search(line)
            if not match:
                continue
            if OFFLINE_PIP.search(line):
                continue  # approved offline wheelhouse rebuild (Part 23.6)
            report.fail(f"{relative}:{lineno} runtime download command "
                        f"'{match.group(1).strip()}' (Part 23.6)")


def check_loopback_only(report: Report) -> None:
    """Parts 0.9, 22.10: bind only to 127.0.0.1; never 0.0.0.0, ::, or 80/443."""
    for relative in _scan_targets():
        if str(relative).startswith("tests/"):
            continue  # tests must be able to assert that these are rejected
        text = read_text(REPO_ROOT / relative)
        documentation = _docstring_lines(relative, text)
        for lineno, line in enumerate(text.splitlines(), start=1):
            if lineno in documentation:
                continue
            if "FORBIDDEN" in line or "forbidden" in line or line.lstrip().startswith("#"):
                continue
            if FORBIDDEN_BIND.search(line):
                report.fail(f"{relative}:{lineno} non-loopback bind address (Part 22.10)")
            if PRIVILEGED_PORT.search(line):
                report.fail(f"{relative}:{lineno} privileged/default web port (Part 22.10)")


def check_no_elevation(report: Report) -> None:
    """Parts 0.9, 30.7: no elevation, service, firewall or URL reservation."""
    for relative in _scan_targets():
        if str(relative).startswith(("tests/", "tools/")):
            continue
        text = read_text(REPO_ROOT / relative)
        documentation = _docstring_lines(relative, text)
        for lineno, line in enumerate(text.splitlines(), start=1):
            if lineno in documentation:
                continue
            if line.lstrip().startswith(("#", "::", "rem ", "REM ", "//")):
                continue
            match = ELEVATION.search(line)
            if match:
                report.fail(f"{relative}:{lineno} machine mutation / elevation: "
                            f"'{match.group(1).strip()}' (Part 33)")


def check_extraction_port(report: Report) -> None:
    """Part 44.2: only the COM adapter may import COM; layers 3-10 never do."""
    allowed = {"app/excel/com_adapter.py", "app/excel/session.py"}
    for relative in _scan_targets():
        key = str(relative).replace("\\", "/")
        if not key.startswith("app/") or key in allowed:
            continue
        text = read_text(REPO_ROOT / relative)
        for lineno, line in enumerate(text.splitlines(), start=1):
            if line.lstrip().startswith("#"):
                continue
            if COM_IMPORTS.search(line):
                report.fail(
                    f"{key}:{lineno} imports COM outside the extraction adapter. "
                    f"Layers 3-10 depend on ExtractionPort only (Part 44.2)")


def check_dev_tools_isolated(report: Report) -> None:
    """Part 20.8 rule 10: production code never imports project intelligence."""
    for relative in _scan_targets():
        key = str(relative).replace("\\", "/")
        if not key.startswith(("app/", "web/")):
            continue
        text = read_text(REPO_ROOT / relative)
        for lineno, line in enumerate(text.splitlines(), start=1):
            if line.lstrip().startswith("#"):
                continue
            if "project_intelligence" in line or re.search(r"\bfrom tools\b|\bimport tools\b", line):
                report.fail(f"{key}:{lineno} production code imports development tooling "
                            f"(Part 20.8 rule 10)")


def check_portable_tool_tier(report: Report) -> None:
    """Part 37.2 rule 1: the portable tool tier is standard library only."""
    stdlib_ok = {
        "argparse", "ast", "collections", "dataclasses", "datetime", "fnmatch",
        "hashlib", "json", "os", "pathlib", "re", "subprocess", "sys",
        "tomllib", "typing", "textwrap", "shutil", "itertools", "math",
        "unittest", "difflib", "string", "time", "urllib", "sqlite3", "csv",
        "types", "enum", "functools", "contextlib", "tempfile", "io",
        "__future__",
    }
    for relative in _scan_targets():
        key = str(relative).replace("\\", "/")
        if not key.startswith("tools/") or relative.suffix != ".py":
            continue
        text = read_text(REPO_ROOT / relative)
        # Parse imports rather than pattern-matching lines: prose such as
        # "from the tree on every refresh" is not an import statement, and a
        # regex cannot tell the difference.
        import ast as _ast
        try:
            tree = _ast.parse(text)
        except SyntaxError as error:
            report.fail(f"{key}: cannot parse ({error})")
            continue

        # Optional accelerators (Part 37.2 rule 4) are legal only inside a
        # guarded import, so collect the nodes that sit under a try block.
        guarded: set[int] = set()
        for node in _ast.walk(tree):
            if isinstance(node, _ast.Try):
                for child in _ast.walk(node):
                    if isinstance(child, (_ast.Import, _ast.ImportFrom)):
                        guarded.add(id(child))

        for node in _ast.walk(tree):
            if isinstance(node, _ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, _ast.ImportFrom):
                if node.level:      # relative import, always our own code
                    continue
                modules = [node.module or ""]
            else:
                continue

            if id(node) in guarded:
                continue

            for module in modules:
                root_module = module.split(".")[0]
                if not root_module or root_module in stdlib_ok or root_module == "tools":
                    continue
                report.fail(f"{key}:{node.lineno} third-party import "
                            f"'{root_module}' in the portable tool tier "
                            f"(Part 37.2 rule 1)")


def check_no_secrets(report: Report) -> None:
    """Part 43: no credential-shaped string in source, config or launchers."""
    for relative in _scan_targets():
        if str(relative).startswith("tools/verify_architecture.py"):
            continue  # this file necessarily contains the patterns themselves
        text = read_text(REPO_ROOT / relative)
        for lineno, line in enumerate(text.splitlines(), start=1):
            match = SECRET_PATTERN.search(line)
            if match and not SECRET_PLACEHOLDER.search(line):
                report.fail(f"{relative}:{lineno} credential-shaped literal "
                            f"'{match.group(1)}' (Part 43 rule 3)")


def check_baseline(report: Report) -> dict | None:
    if not BASELINE_PATH.exists():
        report.fail(f"missing {BASELINE_PATH.name} (Part 0.8) — Phase −1 is incomplete")
        return None
    try:
        baseline = json.loads(read_text(BASELINE_PATH))
    except json.JSONDecodeError as error:
        report.fail(f"{BASELINE_PATH.name} is not valid JSON: {error}")
        return None

    for field in ("schema_version", "baseline_version", "approved_external_prerequisites",
                  "forbidden_runtime_requirements", "required_components"):
        if field not in baseline:
            report.fail(f"{BASELINE_PATH.name}: missing '{field}' (Part 23.9)")

    components = baseline.get("required_components", [])
    if not isinstance(components, list) or not components:
        report.fail(f"{BASELINE_PATH.name}: required_components is empty (Part 23.8)")
        return baseline

    # Every row of Part 23.8 must be represented (Part 23.9).
    mandatory_ids = {
        "python-runtime", "pywin32", "duckdb", "fastapi-stack",
        "loopback-transport", "echarts", "web-frontend", "config-validation",
        "pyinstaller", "wheelhouse", "browser-renderer", "project-intelligence",
    }
    present = {c.get("id") for c in components if isinstance(c, dict)}
    for missing in sorted(mandatory_ids - present):
        report.fail(f"{BASELINE_PATH.name}: locked component '{missing}' is absent "
                    f"(Part 23.8) — a component may not be dropped to reduce package size")

    for component in components:
        if not isinstance(component, dict):
            report.fail(f"{BASELINE_PATH.name}: a component entry is not an object")
            continue
        for field in ("id", "capability", "delivery", "version", "smoke_test"):
            if field not in component:
                report.fail(f"{BASELINE_PATH.name}: component "
                            f"'{component.get('id', '?')}' missing '{field}'")

    deviations = baseline.get("approved_deviations", [])
    for deviation in deviations:
        if isinstance(deviation, dict) and not deviation.get("user_approved"):
            report.fail(f"{BASELINE_PATH.name}: deviation "
                        f"'{deviation.get('id', '?')}' is not user-approved. "
                        f"An agent cannot self-authorize one (Part 23.9)")

    report.note(f"baseline v{baseline.get('baseline_version')}: "
                f"{len(components)} required component(s), "
                f"{len(deviations)} approved deviation(s)")
    return baseline


def cmd_source_scan() -> int:
    report = Report("architecture verify --source-scan")
    check_no_remote_assets(report)
    check_no_runtime_downloads(report)
    check_loopback_only(report)
    check_no_elevation(report)
    check_extraction_port(report)
    check_dev_tools_isolated(report)
    check_portable_tool_tier(report)
    check_no_secrets(report)
    report.note(f"scanned {len(_scan_targets())} executable/runtime file(s)")
    return report.emit()


def cmd_baseline() -> int:
    report = Report("architecture verify --baseline")
    check_baseline(report)
    return report.emit()


def cmd_release(folder: str) -> int:
    report = Report(f"architecture verify --release {folder}")
    release_root = Path(folder)
    if not release_root.is_absolute():
        release_root = REPO_ROOT / release_root
    if not release_root.exists():
        report.block(f"release folder does not exist: {folder}. "
                     f"Build it with BUILD_RELEASE first.")
        return report.emit()

    # Part 44.3 rule 1: the dev adapter must never ship.
    for path in release_root.rglob("fixture_adapter.py"):
        report.fail(f"fixture adapter present in a release: "
                    f"{path.relative_to(release_root)} (Part 44.3 rule 1)")

    for required in ("checksums.sha256", "sbom.spdx.json", "VERSION.json",
                     "IMPLEMENTATION_BASELINE.lock.json"):
        if not (release_root / required).exists():
            report.fail(f"release is missing {required} (Part 30.7)")

    report.note("Full release verification also requires the clean-PC gate "
                "(Part 30.4) on a real offline Windows machine.")
    return report.emit()


def main(args: argparse.Namespace) -> int:
    if args.command != "verify":
        print(f"usage error: unknown architecture command {args.command!r}")
        return EXIT_FAIL

    ran = False
    worst = EXIT_PASS

    if args.baseline:
        worst = max(worst, cmd_baseline())
        ran = True
    if args.source_scan:
        worst = max(worst, cmd_source_scan())
        ran = True
    if args.release:
        worst = max(worst, cmd_release(args.release))
        ran = True

    for flag, part in (("simulate_clean_pc", "30.4"),
                       ("simulate_missing", "23.10"),
                       ("standard_user_loopback", "31.1")):
        if getattr(args, flag, None):
            print(f"\n=== architecture verify --{flag.replace('_', '-')} ===")
            print(f"  BLOCKED: this gate requires a real Windows target (Part {part}).")
            print("  It cannot be satisfied from this workspace and must stay")
            print("  CONDITIONAL in acceptance/gates.yaml until it runs there.")
            worst = max(worst, 3)
            ran = True

    if not ran:
        worst = max(cmd_baseline(), cmd_source_scan())

    return worst
