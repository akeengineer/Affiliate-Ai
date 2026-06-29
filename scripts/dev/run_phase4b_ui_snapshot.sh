#!/usr/bin/env bash
# Phase 4B UI snapshot pack / demo export wrapper.
#
# Packages the Phase 4A static UI mock into a deterministic local snapshot.
# Read-only: never writes the vault, never calls external services, never
# triggers the approved Phase 2G/2H/2I workflows.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

BUILD_SCRIPT="$REPO_ROOT/scripts/dev/build_ui_snapshot.py"
WEEK_RE='^[0-9]{4}-W[0-9]{2}$'

fail() {
  echo "$1" >&2
  exit 1
}

if [ "$#" -ne 1 ]; then
  echo "Usage: bash scripts/dev/run_phase4b_ui_snapshot.sh <week>" >&2
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
