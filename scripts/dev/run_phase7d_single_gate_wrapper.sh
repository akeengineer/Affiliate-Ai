#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

WRAPPER_SCRIPT="$REPO_ROOT/scripts/dev/execute_single_gate_approval.py"

fail() {
  echo "$1" >&2
  exit 1
}

[ -f "$WRAPPER_SCRIPT" ] || fail "Missing wrapper core: $WRAPPER_SCRIPT"

if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  PYTHON_BIN="$(command -v python)"
fi

exec "$PYTHON_BIN" "$WRAPPER_SCRIPT" "$@"
