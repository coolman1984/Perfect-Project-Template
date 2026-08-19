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

from tools._common import REPO_ROOT, sha256_file

CONTRACT_PATH = REPO_ROOT / "contracts" / "operator_package.json"
SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 _.-]{0,79}$")
SAFE_PROJECT_ID = re.compile(r"^[a-z][a-z0-9_]{1,63}$")


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


def validate_project_id(project_id: str) -> str:
    candidate = project_id.strip()
    if not SAFE_PROJECT_ID.fullmatch(candidate):
        raise PackageError(
            "Project id must use 2-64 lowercase letters, numbers, or underscores.")
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


def _verify_checksums(application: Path) -> list[str]:
    manifest = application / "checksums.sha256"
    if not manifest.is_file():
        return ["Application/checksums.sha256 is missing"]
    problems: list[str] = []
    for number, line in enumerate(
            manifest.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            expected, relative = line.split(" *", 1)
        except ValueError:
            problems.append(f"invalid application checksum line {number}")
            continue
        normalized = relative.replace("\\", "/")
        relative_path = PurePosixPath(normalized)
        if (relative_path.is_absolute() or ".." in relative_path.parts
                or re.match(r"^[A-Za-z]:", normalized)):
            problems.append(f"unsafe application checksum path: {relative}")
            continue
        target = application / Path(*relative_path.parts)
        if not target.is_file():
            problems.append(f"application checksum target is missing: {relative}")
            continue
        actual = sha256_file(target)
        if actual != expected:
            problems.append(f"application checksum mismatch: {relative}")
    return problems


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

    required = spec.get(
        "required_application_entries", [spec["required_application_entry"]])
    for entry in required:
        target = root / Path(entry)
        if not target.is_file():
            problems.append(f"missing application entry: {entry}")
    if not problems:
        problems.extend(_verify_checksums(root / "Application"))

    launcher = root / "START.bat"
    if launcher.is_file():
        launcher_text = launcher.read_text(encoding="utf-8").lower()
        for term in spec["forbidden_start_terms"]:
            if term.lower() in launcher_text:
                problems.append(
                    f"START.bat exposes a forbidden runtime tool: {term.strip()}")
    return problems


def _prepare_project_runtime(
        application: Path,
        *,
        project_id: str | None,
        project_dir: Path | None) -> None:
    if project_id is None:
        if project_dir is not None:
            raise PackageError("project_dir requires project_id")
        return

    identifier = validate_project_id(project_id)
    projects = application / "projects"
    projects.mkdir(exist_ok=True)
    source_override = project_dir.resolve() if project_dir else None
    if source_override is not None:
        if not source_override.is_dir():
            raise PackageError(f"project directory does not exist: {source_override}")
        declared = source_override / "project.toml"
        if not declared.is_file():
            raise PackageError(f"project directory is missing {declared.name}")

    target = projects / identifier
    for child in list(projects.iterdir()):
        if child != target:
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    if source_override is not None:
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source_override, target)
    if not target.is_dir():
        raise PackageError(f"sealed application does not contain project {identifier}")

    version_path = application / "VERSION.json"
    if version_path.is_file():
        version = json.loads(version_path.read_text(encoding="utf-8"))
        version["delivery_project_id"] = identifier
        version_path.write_text(
            json.dumps(version, indent=2) + "\n", encoding="utf-8")

    # Project composition changes the sealed repair payload and checksums, so
    # regenerate both inside the private copy before creating the operator ZIP.
    from tools.build_release import repair_payload, write_checksums, write_setup

    payload_hash = repair_payload(application)
    write_setup(application, payload_hash)
    write_checksums(application)


def build(
        project_name: str,
        app_dir: Path,
        output_dir: Path,
        *,
        project_id: str | None = None,
        project_dir: Path | None = None) -> Path:
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
        _prepare_project_runtime(
            root / "Application",
            project_id=project_id,
            project_dir=project_dir)
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
                args.project_name,
                Path(args.app_dir),
                Path(args.output_dir),
                project_id=getattr(args, "project_id", None),
                project_dir=(
                    Path(args.project_dir)
                    if getattr(args, "project_dir", None) else None))
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
