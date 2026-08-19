"""Build the reproducible Windows one-folder release from the local wheelhouse."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import venv
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from tools._common import REPO_ROOT

RELEASE_VERSION = "0.3.0-rc.1"
BUILD_ROOT = REPO_ROOT / "work" / "release-build"
WHEELHOUSE = REPO_ROOT / "offline_packages"
RELEASES = REPO_ROOT / "release" / "versions"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def tree_hash(paths: list[Path], root: Path) -> str:
    digest = hashlib.sha256()
    files: list[Path] = []
    for path in paths:
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(item for item in path.rglob("*") if item.is_file())
    for path in sorted(set(files), key=lambda item: item.as_posix().casefold()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(bytes.fromhex(sha256(path)))
    return digest.hexdigest()


def run(command: list[str], *, cwd: Path = REPO_ROOT) -> None:
    print("  +", " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


def copy_tree(name: str, destination: Path) -> None:
    source = REPO_ROOT / name
    if source.exists():
        shutil.copytree(source, destination / name)


def build_environment() -> Path:
    environment = BUILD_ROOT / "venv"
    venv.EnvBuilder(with_pip=True, clear=True).create(environment)
    python = environment / "Scripts" / "python.exe"
    for lock in ("requirements-lock.txt", "requirements-build-lock.txt"):
        run([
            str(python), "-m", "pip", "install", "--no-index",
            "--find-links", str(WHEELHOUSE), "--require-hashes",
            "-r", str(REPO_ROOT / lock),
        ])
    return python


def freeze(python: Path) -> Path:
    distribution = BUILD_ROOT / "dist"
    run([
        str(python), "-m", "PyInstaller", "--noconfirm", "--clean",
        "--onedir", "--name", "excel-intelligence",
        "--distpath", str(distribution),
        "--workpath", str(BUILD_ROOT / "pyinstaller"),
        "--specpath", str(BUILD_ROOT),
        "--paths", str(REPO_ROOT),
        "--hidden-import", "win32com.client",
        "--hidden-import", "win32process",
        "--hidden-import", "win32api",
        "--hidden-import", "win32con",
        "--hidden-import", "pythoncom",
        "--hidden-import", "pywintypes",
        "--exclude-module", "tzdata",
        "--exclude-module", "app.excel.fixture_adapter",
        "--add-data", f"{REPO_ROOT / 'contracts'}{os.pathsep}contracts",
        str(REPO_ROOT / "app" / "release_main.py"),
    ])
    return distribution / "excel-intelligence"


def write_sbom(destination: Path) -> None:
    packages = []
    for wheel in sorted(WHEELHOUSE.glob("*.whl")):
        packages.append({
            "SPDXID": "SPDXRef-Package-" + wheel.stem.replace("_", "-"),
            "name": wheel.name,
            "downloadLocation": "NOASSERTION",
            "filesAnalyzed": False,
            "checksums": [{"algorithm": "SHA256", "checksumValue": sha256(wheel)}],
        })
    document = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": f"excel-intelligence-{RELEASE_VERSION}",
        "documentNamespace": (
            "https://local.invalid/spdx/excel-intelligence/" + RELEASE_VERSION),
        "creationInfo": {
            "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "creators": ["Tool: tools/build_release.py"],
        },
        "packages": packages,
    }
    (destination / "sbom.spdx.json").write_text(
        json.dumps(document, indent=2) + "\n", encoding="utf-8")


def write_licenses(destination: Path) -> None:
    license_root = destination / "licenses"
    license_root.mkdir()
    rows = []
    for wheel in sorted(WHEELHOUSE.glob("*.whl")):
        with zipfile.ZipFile(wheel) as archive:
            metadata_name = next(
                (name for name in archive.namelist()
                 if name.endswith(".dist-info/METADATA")), None)
            metadata = (
                archive.read(metadata_name).decode("utf-8", errors="replace")
                if metadata_name else "")
            fields = {}
            for line in metadata.splitlines():
                if ": " in line:
                    key, value = line.split(": ", 1)
                    fields.setdefault(key, value)
            package = fields.get("Name", wheel.stem)
            version = fields.get("Version", "locked")
            expression = fields.get(
                "License-Expression", fields.get("License", "SEE-WHEEL-METADATA"))
            target = license_root / package.replace("/", "-")
            target.mkdir(exist_ok=True)
            extracted = []
            for name in archive.namelist():
                base = Path(name).name
                if not base or not any(
                    token in base.casefold()
                    for token in ("license", "copying", "notice")
                ):
                    continue
                output = target / base
                output.write_bytes(archive.read(name))
                extracted.append(output.relative_to(destination).as_posix())
            rows.append((package, version, expression, sha256(wheel), ", ".join(extracted)))

    python_license = Path(sys.base_prefix) / "LICENSE.txt"
    if python_license.is_file():
        shutil.copy2(python_license, license_root / "python.txt")
    shutil.copy2(REPO_ROOT / "licenses" / "README.md", license_root / "README.md")
    header = [
        "# Third-party notices", "",
        "Generated from the exact locked wheels in the release update kit.", "",
        "| Component | Version | License | SHA-256 | Extracted notices |",
        "|---|---:|---|---|---|",
    ]
    body = [
        f"| {name} | `{version}` | {license_name} | `{digest}` | {files or 'wheel metadata'} |"
        for name, version, license_name, digest, files in rows
    ]
    body.append(
        "| Apache ECharts | `6.1.0` | Apache-2.0 | `"
        + sha256(destination / "web" / "vendor" / "echarts.min.js")
        + "` | `web/vendor/README.md` and licensed source header |")
    (destination / "THIRD_PARTY_NOTICES.md").write_text(
        "\n".join(header + body) + "\n", encoding="utf-8")


def release_baseline(destination: Path) -> None:
    baseline = json.loads(
        (REPO_ROOT / "IMPLEMENTATION_BASELINE.lock.json").read_text("utf-8"))
    component_paths = {
        "python-runtime": [destination / "app" / "excel-intelligence.exe"],
        "native-runtime-dlls": list((destination / "app").rglob("*.dll")),
        "pywin32": list((destination / "app").rglob("*win32*")),
        "duckdb": list((destination / "app").rglob("*duckdb*")),
        "parquet": list((destination / "app").rglob("*duckdb*")),
        "fastapi-stack": [destination / "app"],
        "loopback-transport": [destination / "app" / "excel-intelligence.exe"],
        "echarts": [destination / "web" / "vendor" / "echarts.min.js"],
        "web-frontend": [destination / "web"],
        "config-validation": [destination / "contracts"],
        "pyinstaller": list(WHEELHOUSE.glob("pyinstaller-6.21.0-*.whl")),
        "wheelhouse": [destination / "update_kit" / "offline_packages"],
        "project-intelligence": [REPO_ROOT / ".ai" / "MAP_MANIFEST.json"],
    }
    versions = {
        "python-runtime": sys.version.split()[0],
        "pyinstaller": "6.21.0",
        "wheelhouse": "requirements-lock+requirements-build-lock",
        "web-frontend": RELEASE_VERSION,
        "config-validation": RELEASE_VERSION,
        "loopback-transport": RELEASE_VERSION,
        "fastapi-stack": "locked",
        "duckdb": "1.5.5",
        "parquet": "DuckDB 1.5.5",
        "pywin32": "312",
        "echarts": "6.1.0",
        "project-intelligence": "1.0.0",
    }
    for component in baseline["required_components"]:
        identifier = component["id"]
        if identifier == "browser-renderer":
            chrome = Path("C:/Program Files/Google/Chrome/Application/chrome.exe")
            if chrome.is_file():
                component["sha256"] = sha256(chrome)
                component["version"] = "build-machine Chrome (exact binary hash)"
                component["environment_evidence_only"] = True
            continue
        paths = component_paths.get(identifier)
        if paths:
            root = destination if all(destination in path.parents or path == destination
                                      for path in paths) else REPO_ROOT
            component["sha256"] = tree_hash(paths, root)
            component["version"] = versions.get(identifier, RELEASE_VERSION)
        elif component.get("sha256") == "POPULATE_FROM_RELEASE":
            component["sha256"] = "ENVIRONMENT_BOUND_NOT_BUNDLED"
            component["version"] = "ENVIRONMENT_PROOF_REQUIRED"
    (destination / "IMPLEMENTATION_BASELINE.lock.json").write_text(
        json.dumps(baseline, indent=2) + "\n", encoding="utf-8")


def repair_payload(destination: Path) -> str:
    payload = destination / "repair_payload.zip"
    included = [
        destination / "app", destination / "web", destination / "projects",
        destination / "contracts", destination / "START_APP.bat",
        destination / "licenses", destination / "THIRD_PARTY_NOTICES.md",
        destination / "VERSION.json", destination / "sbom.spdx.json",
        destination / "IMPLEMENTATION_BASELINE.lock.json",
    ]
    with zipfile.ZipFile(payload, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for item in included:
            files = [item] if item.is_file() else [p for p in item.rglob("*") if p.is_file()]
            for path in files:
                archive.write(path, path.relative_to(destination).as_posix())
    return sha256(payload)


def write_setup(destination: Path, payload_hash: str) -> None:
    content = rf"""@echo off
setlocal
set "ROOT=%~dp0"
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command "$zip=[IO.Path]::Combine('%ROOT%','repair_payload.zip'); if(-not (Test-Path -LiteralPath $zip)){{exit 2}}; $actual=(Get-FileHash -Algorithm SHA256 -LiteralPath $zip).Hash.ToLowerInvariant(); if($actual -ne '{payload_hash}'){{exit 3}}; Expand-Archive -LiteralPath $zip -DestinationPath '%ROOT%' -Force"
if %ERRORLEVEL% NEQ 0 (
  echo PACKAGE_COMPONENT_MISSING
  echo The sealed repair payload is missing or damaged. Contact IT.
  exit /b 1
)
echo Repair completed from the sealed local payload.
exit /b 0
"""
    (destination / "SETUP_OFFLINE.bat").write_text(content, encoding="utf-8")


def write_checksums(destination: Path) -> None:
    excluded_roots = {"data", "inbox", "output", "runs"}
    files = [
        path for path in destination.rglob("*")
        if path.is_file()
        and path.name != "checksums.sha256"
        and path.relative_to(destination).parts[0] not in excluded_roots
    ]
    lines = [
        f"{sha256(path)} *{path.relative_to(destination).as_posix()}"
        for path in sorted(files, key=lambda item: item.as_posix().casefold())
    ]
    (destination / "checksums.sha256").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")


def build() -> Path:
    if os.name != "nt" or sys.version_info[:2] != (3, 12):
        raise SystemExit("release build requires Windows x64 and Python 3.12")
    if not WHEELHOUSE.is_dir():
        raise SystemExit("offline_packages is missing; prepare the pinned wheelhouse first")
    if BUILD_ROOT.exists():
        shutil.rmtree(BUILD_ROOT)
    BUILD_ROOT.mkdir(parents=True)
    python = build_environment()
    frozen = freeze(python)

    destination = RELEASES / RELEASE_VERSION
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    shutil.copytree(frozen, destination / "app")
    for name in ("web", "projects", "contracts"):
        copy_tree(name, destination)
    for directory in ("data", "inbox", "output", "runs"):
        (destination / directory).mkdir()
    shutil.copy2(REPO_ROOT / "START_APP.bat", destination / "START_APP.bat")
    update_kit = destination / "update_kit"
    shutil.copytree(WHEELHOUSE, update_kit / "offline_packages")
    for lock in ("requirements-lock.txt", "requirements-build-lock.txt"):
        shutil.copy2(REPO_ROOT / lock, update_kit / lock)

    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True,
            stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        baseline = json.loads(
            (REPO_ROOT / "TEMPLATE_BASELINE.json").read_text(encoding="utf-8"))
        commit = baseline.get("source_commit") or "downloaded-source-without-git"
    version = {
        "version": RELEASE_VERSION,
        "source_commit": commit,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "platform": "win_amd64",
        "python": sys.version.split()[0],
        "status": "release_candidate_external_gates_conditional",
    }
    (destination / "VERSION.json").write_text(
        json.dumps(version, indent=2) + "\n", encoding="utf-8")
    write_sbom(destination)
    write_licenses(destination)
    release_baseline(destination)
    payload_hash = repair_payload(destination)
    write_setup(destination, payload_hash)
    write_checksums(destination)

    current = REPO_ROOT / "release" / "current"
    if current.exists():
        shutil.rmtree(current)
    shutil.copytree(destination, current)
    print(f"\nRelease built: {current}")
    return current


if __name__ == "__main__":
    build()
