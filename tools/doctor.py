#!/usr/bin/env python3
"""Aggregate readiness check (Constitution Part 37.3, Phase −2 exit gate Part 39.2).

`PROJECT_TOOL doctor` is the single command an agent runs first. It executes
every other verifier and reports one combined verdict, so "is this project in a
sane state?" takes one command instead of six.
"""

from __future__ import annotations

import argparse
from types import SimpleNamespace

from tools._common import EXIT_BLOCKED, EXIT_FAIL, EXIT_PASS


def main(args: argparse.Namespace) -> int:  # noqa: ARG001 - uniform dispatch signature
    from tools import gates, project_map, project_memory, report_tool
    from tools import verify_architecture, verify_constitution

    checks: list[tuple[str, int]] = []

    print("#" * 72)
    print("# PROJECT_TOOL doctor — aggregate readiness")
    print("#" * 72)

    checks.append(("map doctor", project_map.main(SimpleNamespace(command="doctor"))))
    checks.append(("map verify", project_map.main(SimpleNamespace(command="verify"))))
    checks.append(("constitution audit",
                   verify_constitution.main(SimpleNamespace(command="audit"))))
    checks.append(("architecture --baseline", verify_architecture.main(SimpleNamespace(
        command="verify", baseline=True, source_scan=False, release=None,
        simulate_clean_pc=False, simulate_missing=None, standard_user_loopback=False))))
    checks.append(("architecture --source-scan", verify_architecture.main(SimpleNamespace(
        command="verify", baseline=False, source_scan=True, release=None,
        simulate_clean_pc=False, simulate_missing=None, standard_user_loopback=False))))
    checks.append(("memory validate", project_memory.main(SimpleNamespace(command="validate"))))
    checks.append(("gates status", gates.main(SimpleNamespace(
        command="status", severity=None, only=None))))
    checks.append(("report validate", report_tool.main(SimpleNamespace(
        command="validate", report_id="", mode="prototype"))))

    print("\n" + "#" * 72)
    print("# SUMMARY")
    print("#" * 72)
    labels = {EXIT_PASS: "PASS", EXIT_FAIL: "FAIL", 2: "USAGE", EXIT_BLOCKED: "BLOCKED"}
    for name, code in checks:
        print(f"  {labels.get(code, code):<8} {name}")

    worst = max(code for _, code in checks)
    if worst == EXIT_PASS:
        print("\ndoctor: PASS — the project is in a verifiable state.")
    elif worst == EXIT_BLOCKED:
        print("\ndoctor: BLOCKED — a prerequisite is missing and something was NOT "
              "verified.\nDo not report this as a pass (Part 37.4).")
    else:
        print("\ndoctor: FAIL — fix the failures above before feature work "
              "(Part 0.1 step 7).")
    return worst
