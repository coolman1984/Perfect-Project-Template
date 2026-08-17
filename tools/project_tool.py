#!/usr/bin/env python3
"""PROJECT_TOOL — the single command surface for this project (Constitution Part 37).

Every command the constitution names is reachable here, on every platform:

    PROJECT_TOOL.bat map verify        (Windows)
    ./project_tool.sh map verify       (Linux / macOS)
    python3 tools/project_tool.py map verify   (anywhere)

All three are the same instruction. This module and everything it imports use
the Python standard library only (Part 37.2 rule 1) so that an agent dropped
into a bare workspace can run the mandatory checks immediately.

Exit codes (Part 37.4):
    0 pass · 1 fail · 2 usage error · 3 blocked (nothing was verified)
"""

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
        need = ".".join(str(part) for part in MIN_PYTHON)
        have = ".".join(str(part) for part in sys.version_info[:3])
        print(f"BLOCKED: Python {need}+ required, found {have}", file=sys.stderr)
        raise SystemExit(EXIT_BLOCKED)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="PROJECT_TOOL",
        description="Project tooling: map, memory, architecture, constitution, gates, report.",
    )
    groups = parser.add_subparsers(dest="group", metavar="<group>")

    # ---- map -------------------------------------------------------------
    p_map = groups.add_parser("map", help="project map: navigation and freshness")
    map_cmds = p_map.add_subparsers(dest="command", metavar="<command>")
    map_cmds.add_parser("doctor", help="parser/cache/entry-file readiness")
    map_cmds.add_parser("verify", help="fail on a stale or incomplete map")
    p_refresh = map_cmds.add_parser("refresh", help="rebuild the map and manifest")
    p_refresh.add_argument("--review", action="store_true", help="show the diff before writing")
    p_context = map_cmds.add_parser("context", help="generate .ai/CONTEXT_PACK.md for one task")
    p_context.add_argument("--task", required=True, help="plain-language task description")
    p_context.add_argument("--budget", type=int, default=4000, help="token budget (1000-8000)")
    p_explain = map_cmds.add_parser("explain", help="why one file exists and what depends on it")
    p_explain.add_argument("--path", required=True)
    p_changed = map_cmds.add_parser("changed", help="route a change set to tests and contracts")
    p_changed.add_argument("--base", default="HEAD", help="git ref to compare against")

    # ---- memory ----------------------------------------------------------
    p_mem = groups.add_parser("memory", help="project memory and improvement scout")
    mem_cmds = p_mem.add_subparsers(dest="command", metavar="<command>")
    mem_cmds.add_parser("validate", help="fail on malformed or source-free memory records")
    p_suggest = mem_cmds.add_parser("suggest", help="evidence-based improvement suggestions")
    p_suggest.add_argument("--task", required=True)
    p_suggest.add_argument("--max", type=int, default=3, dest="max_items")

    # ---- architecture ----------------------------------------------------
    p_arch = groups.add_parser("architecture", help="locked-baseline compliance")
    arch_cmds = p_arch.add_subparsers(dest="command", metavar="<command>")
    p_averify = arch_cmds.add_parser("verify", help="verify the architecture baseline")
    p_averify.add_argument("--baseline", action="store_true", help="check the lock file itself")
    p_averify.add_argument("--source-scan", action="store_true", help="scan source for violations")
    p_averify.add_argument("--release", metavar="FOLDER", help="verify a built release folder")
    p_averify.add_argument("--simulate-clean-pc", action="store_true")
    p_averify.add_argument("--simulate-missing", metavar="COMPONENT_ID")
    p_averify.add_argument("--standard-user-loopback", action="store_true")

    # ---- constitution ----------------------------------------------------
    p_con = groups.add_parser("constitution", help="constitution consistency audit")
    con_cmds = p_con.add_subparsers(dest="command", metavar="<command>")
    con_cmds.add_parser("audit", help="run every constitution check")
    con_cmds.add_parser("cross-references", help="check internal Part references")
    con_cmds.add_parser("architecture-terms", help="detect forbidden downgrade language")
    con_cmds.add_parser("commands", help="check that named commands exist")

    # ---- gates -----------------------------------------------------------
    p_gates = groups.add_parser("gates", help="acceptance gate ledger (Part 38)")
    gate_cmds = p_gates.add_subparsers(dest="command", metavar="<command>")
    p_gstatus = gate_cmds.add_parser("status", help="show ledger and validate evidence")
    p_gstatus.add_argument("--severity", choices=["block", "major", "minor"])
    p_gstatus.add_argument("--only", choices=[
        "not_started", "in_progress", "pass", "fail", "conditional", "not_applicable"])
    p_gset = gate_cmds.add_parser("set", help="record a gate result")
    p_gset.add_argument("--id", required=True, dest="gate_id")
    p_gset.add_argument("--status", required=True, choices=[
        "not_started", "in_progress", "pass", "fail", "conditional", "not_applicable"])
    p_gset.add_argument("--evidence", default="")
    p_gset.add_argument("--by", default="", dest="verified_by")
    p_gset.add_argument("--reason", default="", dest="conditional_reason")
    p_gset.add_argument("--next-action", default="", dest="next_action")

    # ---- report ----------------------------------------------------------
    p_report = groups.add_parser("report", help="report configuration (Part 41)")
    rep_cmds = p_report.add_subparsers(dest="command", metavar="<command>")
    p_rnew = rep_cmds.add_parser("new", help="scaffold reports/<id>/ from the template")
    p_rnew.add_argument("--id", required=True, dest="report_id")
    p_rnew.add_argument("--title", default="", dest="title")
    p_rvalidate = rep_cmds.add_parser("validate", help="validate config and list open approvals")
    p_rvalidate.add_argument("--id", dest="report_id", default="")
    p_rvalidate.add_argument("--mode", default="prototype",
                             choices=["discovery", "prototype", "production"],
                             help="production forbids PENDING_APPROVAL (Part 41.3)")

    # ---- doctor ----------------------------------------------------------
    groups.add_parser("doctor", help="aggregate readiness check across every group")

    return parser


def _dispatch(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    group = args.group

    if group == "map":
        from tools import project_map
        return project_map.main(args)
    if group == "memory":
        from tools import project_memory
        return project_memory.main(args)
    if group == "architecture":
        from tools import verify_architecture
        return verify_architecture.main(args)
    if group == "constitution":
        from tools import verify_constitution
        return verify_constitution.main(args)
    if group == "gates":
        from tools import gates
        return gates.main(args)
    if group == "report":
        from tools import report_tool
        return report_tool.main(args)
    if group == "doctor":
        from tools import doctor
        return doctor.main(args)

    parser.print_help()
    return EXIT_USAGE


def main(argv: list[str] | None = None) -> int:
    _check_python()
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.group:
        parser.print_help()
        return EXIT_USAGE
    if args.group != "doctor" and not getattr(args, "command", None):
        print(f"usage error: '{args.group}' needs a command", file=sys.stderr)
        return EXIT_USAGE

    return _dispatch(args, parser)


if __name__ == "__main__":
    raise SystemExit(main())
