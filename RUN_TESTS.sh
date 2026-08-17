#!/usr/bin/env bash
# Offline verification suite (Constitution Parts 20.9, 30.3).
# POSIX twin of RUN_TESTS.bat — same checks, same exit codes (Part 37.2).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"${HERE}/project_tool.sh" doctor
python3 -m unittest discover -s "${HERE}/tests" -t "${HERE}"

echo
echo "All checks passed."
