"""Build and verify the AI-facing master template and cloud delivery."""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import shutil
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

from tools._common import REPO_ROOT, iter_source_files, sha256_file, utc_now
from tools.operator_package import (
    PackageError,
    _verify_checksums,
    build as build_operator,
    validate_project_id,
)
from tools.path_scope import classify_scope

CONTRACT_PATH = REPO_ROOT / "contracts" / "master_template_package.json"


class MasterTemplateError(RuntimeError):
    """The candidate cannot become a safe reusable master template."""


def contract(root: Path = REPO_ROOT) -> dict:
    path = root / "contracts" / "master_template_package.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _matches(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def _reference_source_files(source_root: Path) -> list[Path]:
    result: list[Path] = []
    for relative in iter_source_files(source_root):
        parts = relative.parts
        if parts and parts[0] == "projects" and len(parts) > 1:
            if not parts[1].startswith("_REFERENCE_"):
                continue
        if len(parts) > 2 and parts[:2] == ("tests", "projects"):
            if not parts[2].startswith("_REFERENCE_"):
                continue
        result.append(relative)
    return result


def _verify_sealed_core(root: Path) -> list[str]:
    problems: list[str] = []
    baseline_path = root / "TEMPLATE_BASELINE.json"
    if not baseline_path.is_file():
        return ["missing TEMPLATE_BASELINE.json"]
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    if not baseline.get("sealed") or baseline.get("status") != "sealed_master_template":
        return ["template baseline is not sealed"]

    expected = baseline.get("core_files", {})
    actual: dict[str, str] = {}
    for relative in iter_source_files(root):
        key = relative.as_posix()
        if key in {"TEMPLATE_BASELINE.json", "MASTER_TEMPLATE_MANIFEST.json"}:
            continue
        if classify_scope(key, baseline=baseline) in {"universal_core", "tooling"}:
            actual[key] = sha256_file(root / relative)
    for path in sorted(set(expected) - set(actual)):
        problems.append(f"sealed core file missing: {path}")
    for path in sorted(set(actual) - set(expected)):
        problems.append(f"new core/tooling file outside sealed baseline: {path}")
    for path in sorted(set(expected) & set(actual)):
        if expected[path] != actual[path]:
            problems.append(f"sealed core file changed: {path}")
    return problems


def _clean_runtime(runtime: Path, *, keep_references: bool) -> None:
    projects = runtime / "projects"
    if projects.is_dir():
        for child in list(projects.iterdir()):
            keep = keep_references and child.name.startswith("_REFERENCE_")
            if not keep:
                if child.is_dir():
                    shutil.rmtree(child)
                else:
                    child.unlink()
    for name in ("data", "inbox", "output", "runs"):
        directory = runtime / name
        if not directory.is_dir():
            continue
        for child in list(directory.iterdir()):
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()

    version_path = runtime / "VERSION.json"
    if version_path.is_file():
        version = json.loads(version_path.read_text(encoding="utf-8"))
        version["master_template_runtime"] = True
        version.pop("delivery_project_id", None)
        version_path.write_text(
            json.dumps(version, indent=2) + "\n", encoding="utf-8")

    from tools.build_release import repair_payload, write_checksums, write_setup

    payload_hash = repair_payload(runtime)
    write_setup(runtime, payload_hash)
    write_checksums(runtime)


def verify_folder(root: Path) -> list[str]:
    root = root.resolve()
    if not root.is_dir():
        return [f"master template root does not exist: {root}"]
    try:
        spec = contract(root)
    except (OSError, json.JSONDecodeError) as error:
        return [f"master template contract cannot be read: {error}"]

    problems = _verify_sealed_core(root)
    for entry in spec["required_root_entries"]:
        if not (root / entry).exists():
            problems.append(f"missing master-template entry: {entry}")
    runtime = root / "sealed_runtime"
    for entry in spec["required_runtime_entries"]:
        if not (runtime / entry).exists():
            problems.append(f"missing sealed-runtime entry: {entry}")
    if runtime.is_dir():
        problems.extend(
            f"sealed runtime: {problem}"
            for problem in _verify_checksums(runtime))

    manifest_path = root / "MASTER_TEMPLATE_MANIFEST.json"
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            problems.append(f"invalid master manifest: {error}")
        else:
            for path, expected in manifest.get("immutable_source_sha256", {}).items():
                target = root / path
                if not target.is_file():
                    problems.append(f"immutable master file missing: {path}")
                elif sha256_file(target) != expected:
                    problems.append(f"immutable master file changed: {path}")

    forbidden_names = set(spec["forbidden_anywhere"])
    forbidden_suffixes = set(spec["forbidden_source_suffixes"])
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if set(relative.parts) & forbidden_names:
            problems.append(f"forbidden generated/developer path: {relative}")
        if (path.is_file() and path.suffix.lower() in forbidden_suffixes
                and relative.parts[0] != "sealed_runtime"):
            problems.append(f"business/runtime data leaked into master source: {relative}")
    return sorted(set(problems))


def build(
        source_root: Path,
        release_dir: Path,
        output_dir: Path) -> Path:
    source = source_root.resolve()
    release = release_dir.resolve()
    if not source.is_dir():
        raise MasterTemplateError(f"source root does not exist: {source}")
    if not release.is_dir():
        raise MasterTemplateError(f"sealed release does not exist: {release}")
    core_problems = _verify_sealed_core(source)
    if core_problems:
        raise MasterTemplateError("; ".join(core_problems))
    if not (release / "app" / "excel-intelligence.exe").is_file():
        raise MasterTemplateError("sealed release is missing app/excel-intelligence.exe")

    spec = contract(source)
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / spec["archive_name"]
    with tempfile.TemporaryDirectory(prefix="master-template-") as temporary:
        root = Path(temporary) / spec["root_name"]
        root.mkdir()
        copied: list[str] = []
        for relative in _reference_source_files(source):
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / relative, target)
            copied.append(relative.as_posix())

        shutil.copytree(release, root / "sealed_runtime")
        _clean_runtime(root / "sealed_runtime", keep_references=True)

        mutable = spec["mutable_patterns"]
        immutable = {
            path: sha256_file(root / path)
            for path in copied
            if not _matches(path, mutable)
        }
        baseline = json.loads(
            (root / "TEMPLATE_BASELINE.json").read_text(encoding="utf-8"))
        manifest = {
            "schema_version": 1,
            "created_at": utc_now(),
            "template_id": baseline.get("template_id"),
            "template_version": baseline.get("template_version"),
            "source_commit": baseline.get("source_commit"),
            "canonical_instruction": "00_START_HERE_AI_AGENT.md",
            "sealed_runtime_version": json.loads(
                (root / "sealed_runtime" / "VERSION.json").read_text(
                    encoding="utf-8")).get("version"),
            "mutable_patterns": mutable,
            "immutable_source_sha256": dict(sorted(immutable.items())),
        }
        (root / "MASTER_TEMPLATE_MANIFEST.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

        problems = verify_folder(root)
        if problems:
            raise MasterTemplateError("; ".join(problems))

        candidate = Path(temporary) / spec["archive_name"]
        with zipfile.ZipFile(
                candidate, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(root.rglob("*")):
                if path.is_file():
                    archive.write(path, Path(spec["root_name"]) / path.relative_to(root))
        candidate.replace(destination)
    return destination


def verify_zip(path: Path) -> list[str]:
    if not path.is_file():
        return [f"master ZIP does not exist: {path}"]
    try:
        with tempfile.TemporaryDirectory(prefix="master-verify-") as temporary:
            with zipfile.ZipFile(path) as archive:
                names = archive.namelist()
                if any(
                    name.startswith(("/", "\\"))
                    or "\\" in name
                    or re.match(r"^[A-Za-z]:", name)
                    or ".." in PurePosixPath(name).parts
                    for name in names
                ):
                    return ["master ZIP contains an unsafe path"]
                archive.extractall(temporary)
            roots = [item for item in Path(temporary).iterdir() if item.is_dir()]
            if len(roots) != 1:
                return ["master ZIP must contain exactly one root folder"]
            return verify_folder(roots[0])
    except (OSError, zipfile.BadZipFile) as error:
        return [f"master ZIP cannot be verified: {error}"]


def build_delivery(
        master_root: Path,
        project_id: str,
        project_name: str,
    output_dir: Path) -> Path:
    root = master_root.resolve()
    try:
        project_id = validate_project_id(project_id)
    except PackageError as error:
        raise MasterTemplateError(str(error)) from error
    problems = verify_folder(root)
    if problems:
        raise MasterTemplateError("; ".join(problems))
    project_dir = root / "projects" / project_id
    if not project_dir.is_dir():
        raise MasterTemplateError(f"project pack does not exist: projects/{project_id}")
    try:
        result = build_operator(
            project_name,
            root / "sealed_runtime",
            output_dir,
            project_id=project_id,
            project_dir=project_dir)
    except PackageError as error:
        raise MasterTemplateError(str(error)) from error
    return result


def _print_problems(problems: list[str], label: str) -> int:
    if not problems:
        print(f"{label}: PASS")
        return 0
    for problem in problems:
        print(f"  ! {problem}")
    print(f"{label}: FAIL")
    return 1


def main(args: argparse.Namespace) -> int:
    try:
        if args.group == "master-template" and args.command == "build":
            result = build(
                Path(args.source_root),
                Path(args.release_dir),
                Path(args.output_dir))
            print(f"master-template build: PASS — {result}")
            return 0
        if args.group == "master-template" and args.command == "verify":
            return _print_problems(
                verify_zip(Path(args.zip_path)), "master-template verify")
        if args.group == "master-template" and args.command == "verify-folder":
            return _print_problems(
                verify_folder(Path(args.root)), "master-template verify-folder")
        if args.group == "delivery" and args.command == "build":
            result = build_delivery(
                Path(args.master_root),
                args.project_id,
                args.project_name,
                Path(args.output_dir))
            print(f"delivery build: PASS — {result}")
            return 0
    except (OSError, MasterTemplateError, json.JSONDecodeError) as error:
        print(f"{args.group} {args.command}: FAIL — {error}")
        return 1
    print(f"{args.group}: usage error")
    return 2
