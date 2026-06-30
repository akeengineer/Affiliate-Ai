#!/usr/bin/env bash
# Phase 5B Local Static UI Shell Prototype wrapper.
#
# Generates a self-contained, read-only static HTML shell that summarizes the
# Phase 4 demo pipeline and links to existing local static Phase 4 outputs.
# Read-only: no vault, no external services, no approved-workflow triggering.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

BUILD_SCRIPT="$REPO_ROOT/scripts/dev/build_ui_shell.py"
WEEK_RE='^[0-9]{4}-W[0-9]{2}$'

fail() {
  echo "$1" >&2
  exit 1
}

if [ "$#" -ne 1 ]; then
  echo "Usage: bash scripts/dev/run_phase5b_ui_shell.sh <week>" >&2
  exit 1
fi

WEEK="$1"

# ── Guardrails ───────────────────────────────────────────────────────────────
[ "${ENABLE_AUTOPUBLISH:-false}" != "true" ] || fail "ENABLE_AUTOPUBLISH=true is not allowed"
[ "${ENABLE_OPENAI_API_DIRECT:-false}" != "true" ] || fail "ENABLE_OPENAI_API_DIRECT=true is not allowed"
[ "${APPROVE_PROMOTE:-false}" != "true" ] || fail "APPROVE_PROMOTE=true is not allowed"
[ "${APPROVE_DECISION:-false}" != "true" ] || fail "APPROVE_DECISION=true is not allowed"
[ "${APPROVE_FINALIZE:-false}" != "true" ] || fail "APPROVE_FINALIZE=true is not allowed"

printf '%s' "$WEEK" | grep -Eq "$WEEK_RE" \
  || fail "week must match $WEEK_RE, got: $WEEK"

[ -f "$BUILD_SCRIPT" ] || fail "Missing build script: $BUILD_SCRIPT"

# ── Select Python: .venv -> python3 -> python ────────────────────────────────
if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  PYTHON_BIN="$(command -v python)"
fi

exec "$PYTHON_BIN" "$BUILD_SCRIPT" --week "$WEEK"
