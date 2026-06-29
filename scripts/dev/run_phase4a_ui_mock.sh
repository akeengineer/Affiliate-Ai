#!/usr/bin/env bash
# Phase 4A local read-only UI mock wrapper.
#
# Generates a self-contained static HTML mock from existing tmp artifacts.
# Read-only: never writes the vault, never calls external services, and never
# triggers the approved Phase 2G/2H/2I workflows.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

BUILD_SCRIPT="$REPO_ROOT/scripts/dev/build_ui_mock.py"
WEEK_RE='^[0-9]{4}-W[0-9]{2}$'

fail() {
  echo "$1" >&2
  exit 1
}

if [ "$#" -ne 1 ]; then
  echo "Usage: bash scripts/dev/run_phase4a_ui_mock.sh <week>" >&2
  exit 1
fi

REPORT_WEEK="$1"

# ── Guardrails ───────────────────────────────────────────────────────────────
[ "${ENABLE_AUTOPUBLISH:-false}" != "true" ] || fail "ENABLE_AUTOPUBLISH=true is not allowed"
[ "${ENABLE_OPENAI_API_DIRECT:-false}" != "true" ] || fail "ENABLE_OPENAI_API_DIRECT=true is not allowed"

printf '%s' "$REPORT_WEEK" | grep -Eq "$WEEK_RE" \
  || fail "week must match $WEEK_RE, got: $REPORT_WEEK"

[ -f "$BUILD_SCRIPT" ] || fail "Missing build script: $BUILD_SCRIPT"

# ── Select Python: .venv -> python3 -> python ────────────────────────────────
if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  PYTHON_BIN="$(command -v python)"
fi

cd "$REPO_ROOT"
exec "$PYTHON_BIN" "$BUILD_SCRIPT" --week "$REPORT_WEEK"
