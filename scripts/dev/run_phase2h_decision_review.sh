#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TASK_FILE="$REPO_ROOT/codex/tasks/011-phase2h-manual-decision-review.md"
DECISION_SCRIPT="$REPO_ROOT/scripts/dev/create_decision.py"

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

if [ "$#" -ne 3 ]; then
  echo "Usage: bash scripts/dev/run_phase2h_decision_review.sh <product-id> <decision> <report-week>" >&2
  exit 1
fi

PRODUCT_ID="$1"
DECISION="$2"
REPORT_WEEK="$3"

[ "${ENABLE_AUTOPUBLISH:-false}" != "true" ] || fail "ENABLE_AUTOPUBLISH=true is not allowed"
[ "${ENABLE_OPENAI_API_DIRECT:-false}" != "true" ] || fail "ENABLE_OPENAI_API_DIRECT=true is not allowed"
[ -f "$TASK_FILE" ] || fail "Missing task file: $TASK_FILE"
[ -f "$DECISION_SCRIPT" ] || fail "Missing decision script: $DECISION_SCRIPT"

CMD=("$PYTHON_BIN" "$DECISION_SCRIPT"
  --product-id "$PRODUCT_ID"
  --decision "$DECISION"
  --report-week "$REPORT_WEEK"
)

if [ -n "${OVERRIDE_REASON:-}" ]; then
  CMD+=(--override-reason "$OVERRIDE_REASON")
fi

if [ "${APPROVE_DECISION:-false}" = "true" ]; then
  CMD+=(--approve)
fi

"${CMD[@]}"
