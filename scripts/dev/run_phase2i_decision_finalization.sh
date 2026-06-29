#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TASK_FILE="$REPO_ROOT/codex/tasks/012-phase2i-decision-finalization-gate.md"
FINALIZE_SCRIPT="$REPO_ROOT/scripts/dev/finalize_decision.py"

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

if [ "$#" -ne 1 ]; then
  echo "Usage: FINALIZATION_REASON=... bash scripts/dev/run_phase2i_decision_finalization.sh <decision-id>" >&2
  exit 1
fi

DECISION_ID="$1"

[ "${ENABLE_AUTOPUBLISH:-false}" != "true" ] || fail "ENABLE_AUTOPUBLISH=true is not allowed"
[ "${ENABLE_OPENAI_API_DIRECT:-false}" != "true" ] || fail "ENABLE_OPENAI_API_DIRECT=true is not allowed"
[ -f "$TASK_FILE" ] || fail "Missing task file: $TASK_FILE"
[ -f "$FINALIZE_SCRIPT" ] || fail "Missing finalize script: $FINALIZE_SCRIPT"
[ -n "${FINALIZATION_REASON:-}" ] || fail "FINALIZATION_REASON is required"

CMD=("$PYTHON_BIN" "$FINALIZE_SCRIPT"
  --decision-id "$DECISION_ID"
  --finalization-reason "$FINALIZATION_REASON"
)

if [ "${APPROVE_FINALIZE:-false}" = "true" ]; then
  CMD+=(--approve)
fi

"${CMD[@]}"
