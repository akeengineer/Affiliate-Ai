#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TASK_FILE="$REPO_ROOT/codex/tasks/010-phase2g-approval-promote-gate.md"
PROMOTE_SCRIPT="$REPO_ROOT/scripts/dev/promote_product_candidates.py"

if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  PYTHON_BIN="$(command -v python)"
fi

fail() {
  echo "$1" >&2
  exit 1
}

if [ "$#" -ne 2 ]; then
  echo "Usage: bash scripts/dev/run_phase2g_approval_promote.sh <source-dir> <report-week>" >&2
  exit 1
fi

SOURCE_DIR="$1"
REPORT_WEEK="$2"

[ "${ENABLE_AUTOPUBLISH:-false}" != "true" ] || fail "ENABLE_AUTOPUBLISH=true is not allowed"
[ "${ENABLE_OPENAI_API_DIRECT:-false}" != "true" ] || fail "ENABLE_OPENAI_API_DIRECT=true is not allowed"
[ -f "$TASK_FILE" ] || fail "Missing task file: $TASK_FILE"
[ -f "$PROMOTE_SCRIPT" ] || fail "Missing promote script: $PROMOTE_SCRIPT"

CMD=("$PYTHON_BIN" "$PROMOTE_SCRIPT" --source-dir "$SOURCE_DIR" --report-week "$REPORT_WEEK")
if [ "${APPROVE_PROMOTE:-false}" = "true" ]; then
  CMD+=(--approve)
fi

"${CMD[@]}"
