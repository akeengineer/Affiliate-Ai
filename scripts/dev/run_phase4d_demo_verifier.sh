#!/usr/bin/env bash
# Phase 4D static demo bundle verifier wrapper.
#
# Read-only verifier over the Phase 4B snapshot and Phase 4C catalog. Never
# reads/writes the vault, never calls external services, never regenerates the
# bundle, and never triggers the approved Phase 2G/2H/2I workflows.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

VERIFY_SCRIPT="$REPO_ROOT/scripts/dev/verify_demo_bundle.py"

fail() {
  echo "$1" >&2
  exit 1
}

if [ "$#" -ne 0 ]; then
  echo "Usage: bash scripts/dev/run_phase4d_demo_verifier.sh" >&2
  exit 1
fi

# ── Guardrails ───────────────────────────────────────────────────────────────
[ "${ENABLE_AUTOPUBLISH:-false}" != "true" ] || fail "ENABLE_AUTOPUBLISH=true is not allowed"
[ "${ENABLE_OPENAI_API_DIRECT:-false}" != "true" ] || fail "ENABLE_OPENAI_API_DIRECT=true is not allowed"

[ -f "$VERIFY_SCRIPT" ] || fail "Missing verifier script: $VERIFY_SCRIPT"

# ── Select Python: .venv -> python3 -> python ────────────────────────────────
if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  PYTHON_BIN="$(command -v python)"
fi

cd "$REPO_ROOT"
exec "$PYTHON_BIN" "$VERIFY_SCRIPT"
