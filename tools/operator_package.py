"""Build and verify the simple final-user ZIP from a sealed release folder."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

from tools._common import REPO_ROOT

CONTRACT_PATH = REPO_ROOT / "contracts" / "operator_package.json"
SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 _.-]{0,79}$")


class PackageError(RuntimeError):
    """The candidate cannot become a safe operator package."""


def contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def validate_project_name(name: str) -> str:
    candidate = name.strip()
    if not SAFE_NAME.fullmatch(candidate) or candidate.endswith((".", " ")):
        raise PackageError(
            "Project name must be 1-80 characters using letters, numbers, spaces, "
            "dot, dash, or underscore; it must not contain a path.")
    return candidate


def start_script(executable_name: str = "excel-intelligence.exe") -> str:
    return (
        "@echo off\r\n"
        "setlocal\r\n"
        "set \"APP_ROOT=%~dp0Application\"\r\n"
        f"if not exist \"%APP_ROOT%\\app\\{executable_name}\" (\r\n"
        "  echo The application is incomplete. Please contact support.\r\n"
        "  echo Your files and previous results were not changed.\r\n"
        "  pause\r\n"
        "  exit /b 1\r\n"
        ")\r\n"
        f"\"%APP_ROOT%\\app\\{executable_name}\" --start\r\n"
        "set \"APP_EXIT=%ERRORLEVEL%\"\r\n"
        "if not \"%APP_EXIT%\"==\"0\" (\r\n"
        "  echo The application could not start. Please use the support code shown above.\r\n"
        "  echo Your files and previous results were not changed.\r\n"
        "  pause\r\n"
        ")\r\n"
        "exit /b %APP_EXIT%\r\n"
    )


def quick_start(project_name: str) -> str:
    title = html.escape(project_name)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — Quick Start</title>
<style>body{{font-family:Segoe UI,Arial,sans-serif;max-width:760px;margin:8vh auto;padding:24px;color:#14213d}}h1{{font-size:2rem}}ol{{font-size:1.2rem;line-height:2}}.note{{background:#f3f6fb;border-left:5px solid #2563eb;padding:16px;border-radius:8px}}</style>
</head><body><h1>{title}</h1><ol><li>Extract the ZIP file.</li><li>Double-click <strong>START.bat</strong>.</li><li>Your browser opens automatically.</li><li>Add your Excel files and follow the screen.</li></ol><p class="note">The application works locally and does not need the internet. If a run fails, your previous approved result remains safe.</p></body></html>"""


def verify_folder(root: Path) -> list[str]:
    spec = contract()
    problems: list[str] = []
    if not root.is_dir():
        return [f"package root does not exist: {root}"]

    actual = {item.name for item in root.iterdir()}
    expected = set(spec["root_entries"])
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        if missing:
            problems.append(f"missing root entries: {', '.join(missing)}")
        if extra:
            problems.append(f"unexpected root entries: {', '.join(extra)}")

    forbidden = actual.intersection(spec["forbidden_root_entries"])
    if forbidden:
        problems.append(
            "developer folders exposed at package root: "
            + ", ".join(sorted(forbidden)))

    executable = root / Path(spec["required_application_entry"])
    if not executable.is_file():
        problems.append(
            f"missing application executable: {executable.relative_to(root)}")

    launcher = root / "START.bat"
    if launcher.is_file():
        launcher_text = launcher.read_text(encoding="utf-8").lower()
        for term in spec["forbidden_start_terms"]:
            if term.lower() in launcher_text:
                problems.append(
                    f"START.bat exposes a forbidden runtime tool: {term.strip()}")
    return problems


def build(project_name: str, app_dir: Path, output_dir: Path) -> Path:
    name = validate_project_name(project_name)
    source = app_dir.resolve()
    if not source.is_dir():
        raise PackageError(f"sealed application folder does not exist: {source}")
    executable = source / "app" / "excel-intelligence.exe"
    if not executable.is_file():
        raise PackageError(f"sealed application is missing {executable.relative_to(source)}")

    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / f"{name}.zip"
    with tempfile.TemporaryDirectory(prefix="operator-package-") as temporary:
        root = Path(temporary) / name
        shutil.copytree(source, root / "Application")
        (root / "START.bat").write_text(
            start_script(), encoding="utf-8", newline="")
        (root / "QUICK_START.html").write_text(
            quick_start(name), encoding="utf-8")

        problems = verify_folder(root)
        if problems:
            raise PackageError("; ".join(problems))

        candidate = Path(temporary) / f"{name}.zip"
        with zipfile.ZipFile(
                candidate, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(root.rglob("*")):
                if path.is_file():
                    archive.write(path, Path(name) / path.relative_to(root))
        candidate.replace(destination)
    return destination


def verify_zip(path: Path) -> list[str]:
    if not path.is_file():
        return [f"ZIP does not exist: {path}"]
    try:
        with tempfile.TemporaryDirectory(prefix="operator-verify-") as temporary:
            with zipfile.ZipFile(path) as archive:
                names = archive.namelist()
                if any(
                    name.startswith(("/", "\\"))
                    or "\\" in name
                    or re.match(r"^[A-Za-z]:", name)
                    or ".." in PurePosixPath(name).parts
                    for name in names
                ):
                    return ["ZIP contains an unsafe path"]
                archive.extractall(temporary)
            roots = [item for item in Path(temporary).iterdir() if item.is_dir()]
            if len(roots) != 1:
                return ["ZIP must contain exactly one project folder"]
            return verify_folder(roots[0])
    except (OSError, zipfile.BadZipFile) as error:
        return [f"ZIP cannot be verified: {error}"]


def main(args: argparse.Namespace) -> int:
    if args.command == "build":
        try:
            result = build(
                args.project_name, Path(args.app_dir), Path(args.output_dir))
        except (OSError, PackageError, zipfile.BadZipFile) as error:
            print(f"package build: FAIL — {error}")
            return 1
        print(f"package build: PASS — {result}")
        return 0
    if args.command == "verify":
        problems = verify_zip(Path(args.zip_path))
        if problems:
            for problem in problems:
                print(f"  ! {problem}")
            print("package verify: FAIL")
            return 1
        print("package verify: PASS")
        return 0
    print("package: usage error")
    return 2
