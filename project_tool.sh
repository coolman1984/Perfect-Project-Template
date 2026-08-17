#!/usr/bin/env bash
# PROJECT_TOOL — POSIX wrapper (Constitution Part 37.2).
# Adds nothing but interpreter discovery and argument pass-through:
# ./project_tool.sh map verify  ==  PROJECT_TOOL.bat map verify
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Prefer a bundled private runtime when one exists, exactly as the Windows
# wrapper does; fall back to a discoverable Python 3.11+ for development.
if [ -x "${HERE}/runtime/bin/python3" ]; then
  PY="${HERE}/runtime/bin/python3"
elif command -v python3 >/dev/null 2>&1; then
  PY="python3"
elif command -v python >/dev/null 2>&1; then
  PY="python"
else
  echo "BLOCKED: no Python 3.11+ interpreter found (Part 37.4 exit code 3)" >&2
  exit 3
fi

exec "${PY}" "${HERE}/tools/project_tool.py" "$@"
