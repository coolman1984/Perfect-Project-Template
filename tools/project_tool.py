#!/usr/bin/env python3
"""PROJECT_TOOL — portable standard-library command surface."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

EXIT_PASS, EXIT_FAIL, EXIT_USAGE, EXIT_BLOCKED = 0, 1, 2, 3
MIN_PYTHON = (3, 11)


def _check_python() -> None:
    if sys.version_info < MIN_PYTHON:
        print("BLOCKED: Python 3.11+ required", file=sys.stderr)
        raise SystemExit(EXIT_BLOCKED)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="PROJECT_TOOL",
        description=(
            "Map, architecture, gates, V8.1 project adaptation and "
            "Git-independent template baseline/upgrade verification."),
    )
    groups = parser.add_subparsers(dest="group", metavar="<group>")

    p = groups.add_parser("map")
    c = p.add_subparsers(dest="command")
    c.add_parser("doctor")
    c.add_parser("verify")
    x = c.add_parser("refresh"); x.add_argument("--review", action="store_true")
    x = c.add_parser("context"); x.add_argument("--task", required=True); x.add_argument("--budget", type=int, default=4000)
    x = c.add_parser("explain"); x.add_argument("--path", required=True)
    x = c.add_parser("changed"); x.add_argument("--base", default="HEAD")

    p = groups.add_parser("memory")
    c = p.add_subparsers(dest="command")
    c.add_parser("validate")
    x = c.add_parser("suggest"); x.add_argument("--task", required=True); x.add_argument("--max", type=int, default=3, dest="max_items")

    p = groups.add_parser("architecture")
    c = p.add_subparsers(dest="command")
    x = c.add_parser("verify")
    x.add_argument("--baseline", action="store_true")
    x.add_argument("--source-scan", action="store_true")
    x.add_argument("--release")
    x.add_argument("--simulate-clean-pc", action="store_true")
    x.add_argument("--simulate-missing")
    x.add_argument("--standard-user-loopback", action="store_true")

    p = groups.add_parser("constitution")
    c = p.add_subparsers(dest="command")
    for name in ("audit", "cross-references", "architecture-terms", "commands"):
        c.add_parser(name)

    p = groups.add_parser("gates")
    c = p.add_subparsers(dest="command")
    x = c.add_parser("status")
    x.add_argument("--severity", choices=["block", "major", "minor"])
    x.add_argument("--only", choices=["not_started", "in_progress", "pass", "fail", "conditional", "not_applicable"])
    x = c.add_parser("set")
    x.add_argument("--id", required=True, dest="gate_id")
    x.add_argument("--status", required=True, choices=["not_started", "in_progress", "pass", "fail", "conditional", "not_applicable"])
    x.add_argument("--evidence", default="")
    x.add_argument("--by", default="", dest="verified_by")
    x.add_argument("--reason", default="", dest="conditional_reason")
    x.add_argument("--next-action", default="", dest="next_action")

    # Legacy report/factory commands remain reachable only while existing
    # executable references and migrations are being converted to projects/.
    p = groups.add_parser("report")
    c = p.add_subparsers(dest="command")
    x = c.add_parser("new"); x.add_argument("--id", required=True, dest="report_id"); x.add_argument("--title", default="")
    x = c.add_parser("validate"); x.add_argument("--id", dest="report_id", default=""); x.add_argument("--mode", default="prototype", choices=["discovery", "prototype", "production"])

    p = groups.add_parser("factory")
    c = p.add_subparsers(dest="command")
    x = c.add_parser("new"); x.add_argument("--id", required=True, dest="report_id"); x.add_argument("--title", default="")
    x = c.add_parser("interview"); x.add_argument("--id", required=True, dest="report_id"); x.add_argument("--question", required=True); x.add_argument("--answer", required=True)
    x = c.add_parser("review"); x.add_argument("--id", required=True, dest="report_id")
    x = c.add_parser("approve"); x.add_argument("--id", required=True, dest="report_id"); x.add_argument("--decision", required=True); x.add_argument("--by", required=True); x.add_argument("--method", required=True, choices=sorted({"wizard_confirmation", "signed_artifact", "pull_request_review", "external_workflow", "fixture"})); x.add_argument("--evidence", required=True); x.add_argument("--notes", default="")
    x = c.add_parser("generate"); x.add_argument("--id", required=True, dest="report_id"); x.add_argument("--title", default="")
    x = c.add_parser("brief"); x.add_argument("--id", required=True, dest="report_id")
    x = c.add_parser("status"); x.add_argument("--id", dest="report_id", default=None)
    x = c.add_parser("validate"); x.add_argument("--id", dest="report_id", default=None)
    x = c.add_parser("reference"); x.add_argument("reference_command", choices=["verify"])

    p = groups.add_parser("template-baseline", help="Git-independent sealed Universal Core baseline")
    c = p.add_subparsers(dest="command")
    c.add_parser("verify")
    x = c.add_parser("seal"); x.add_argument("--version", required=True)

    p = groups.add_parser("template-upgrade", help="upgrade/rollback sealed Universal Core while preserving project packs")
    c = p.add_subparsers(dest="command")
    x = c.add_parser("apply"); x.add_argument("--payload", required=True)
    x = c.add_parser("rollback"); x.add_argument("--backup", required=True)

    p = groups.add_parser("adaptation", help="V8.1 employee project-pack creation and verification")
    c = p.add_subparsers(dest="command")
    x = c.add_parser("new"); x.add_argument("--project", required=True, dest="project_id"); x.add_argument("--title", default="")
    for name in ("validate", "core-guard", "reuse-report"):
        x = c.add_parser(name); x.add_argument("--project", required=True, dest="project_id")

    p = groups.add_parser(
        "package", help="build or verify the simple final-user ZIP")
    c = p.add_subparsers(dest="command")
    x = c.add_parser("build")
    x.add_argument("--project-name", required=True)
    x.add_argument("--app-dir", required=True)
    x.add_argument("--output-dir", required=True)
    x.add_argument("--project-id")
    x.add_argument("--project-dir")
    x = c.add_parser("verify")
    x.add_argument("--zip", required=True, dest="zip_path")

    p = groups.add_parser(
        "master-template", help="build or verify the reusable AI-facing master ZIP")
    c = p.add_subparsers(dest="command")
    x = c.add_parser("build")
    x.add_argument("--source-root", default=".")
    x.add_argument("--release-dir", required=True)
    x.add_argument("--output-dir", required=True)
    x = c.add_parser("verify")
    x.add_argument("--zip", required=True, dest="zip_path")
    x = c.add_parser("verify-folder")
    x.add_argument("--root", required=True)

    p = groups.add_parser(
        "delivery", help="build the final offline ZIP from a verified master template")
    c = p.add_subparsers(dest="command")
    x = c.add_parser("build")
    x.add_argument("--project", required=True, dest="project_id")
    x.add_argument("--project-name", required=True)
    x.add_argument("--master-root", default=".")
    x.add_argument("--output-dir", default="dist")

    p = groups.add_parser(
        "wheelhouse", help="prepare or verify the pinned Windows build wheelhouse")
    c = p.add_subparsers(dest="command")
    x = c.add_parser("prepare")
    x.add_argument("--output-dir", default="offline_packages")
    x = c.add_parser("verify")
    x.add_argument("--wheelhouse", default="offline_packages")

    groups.add_parser("doctor")
    return parser


def _dispatch(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    if args.group == "map":
        from tools import project_map; return project_map.main(args)
    if args.group == "memory":
        from tools import project_memory; return project_memory.main(args)
    if args.group == "architecture":
        from tools import verify_architecture; return verify_architecture.main(args)
    if args.group == "constitution":
        from tools import verify_constitution; return verify_constitution.main(args)
    if args.group == "gates":
        from tools import gates; return gates.main(args)
    if args.group == "report":
        from tools import report_tool; return report_tool.main(args)
    if args.group == "factory":
        from tools import factory_tool; return factory_tool.main(args)
    if args.group == "template-baseline":
        from tools import template_baseline
        return template_baseline.verify() if args.command == "verify" else template_baseline.seal(template_version=args.version)
    if args.group == "template-upgrade":
        from tools import template_upgrade
        if args.command == "apply":
            try:
                backup = template_upgrade.apply_upgrade(REPO_ROOT, Path(args.payload))
            except template_upgrade.UpgradeError as error:
                print(f"template-upgrade: FAIL — {error}", file=sys.stderr); return EXIT_FAIL
            print(f"template-upgrade: PASS — rollback snapshot {backup}"); return EXIT_PASS
        try:
            template_upgrade.rollback_upgrade(REPO_ROOT, Path(args.backup))
        except template_upgrade.UpgradeError as error:
            print(f"template-upgrade rollback: FAIL — {error}", file=sys.stderr); return EXIT_FAIL
        print("template-upgrade rollback: PASS"); return EXIT_PASS
    if args.group == "adaptation":
        from tools import adaptation_tool; return adaptation_tool.main(args)
    if args.group == "package":
        from tools import operator_package; return operator_package.main(args)
    if args.group in {"master-template", "delivery"}:
        from tools import master_template_package; return master_template_package.main(args)
    if args.group == "wheelhouse":
        from tools import prepare_wheelhouse; return prepare_wheelhouse.main(args)
    if args.group == "doctor":
        from tools import doctor; return doctor.main(args)
    parser.print_help(); return EXIT_USAGE


def main(argv: list[str] | None = None) -> int:
    _check_python(); parser = build_parser(); args = parser.parse_args(argv)
    if not args.group:
        parser.print_help(); return EXIT_USAGE
    if args.group != "doctor" and not getattr(args, "command", None):
        print(f"usage error: '{args.group}' needs a command", file=sys.stderr); return EXIT_USAGE
    return _dispatch(args, parser)


if __name__ == "__main__":
    raise SystemExit(main())
