#!/usr/bin/env bash
# Phase 4C static UI snapshot catalog wrapper.
#
# Builds a static metadata catalog over Phase 4B snapshot manifests. Read-only:
# never reads/writes the vault, never calls external services, never triggers the
# approved Phase 2G/2H/2I workflows.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

BUILD_SCRIPT="$REPO_ROOT/scripts/dev/build_snapshot_catalog.py"

fail() {
  echo "$1" >&2
  exit 1
}

if [ "$#" -ne 0 ]; then
  echo "Usage: bash scripts/dev/run_phase4c_snapshot_catalog.sh" >&2
  exit 1
fi

# ── Guardrails ───────────────────────────────────────────────────────────────
[ "${ENABLE_AUTOPUBLISH:-false}" != "true" ] || fail "ENABLE_AUTOPUBLISH=true is not allowed"
[ "${ENABLE_OPENAI_API_DIRECT:-false}" != "true" ] || fail "ENABLE_OPENAI_API_DIRECT=true is not allowed"

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
exec "$PYTHON_BIN" "$BUILD_SCRIPT"
