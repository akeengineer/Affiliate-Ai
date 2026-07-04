#!/usr/bin/env bash
# Phase 10E export sidecar wrapper.
#
# Local-only derived export sidecar prototype. Reads one local manifest,
# validates safe export/context references, hashes present files, extracts safe
# summary fields from optional JSON context files, treats safe missing files as
# warnings, rejects unsafe paths, secrets, approval flags, and execution
# intent, and writes deterministic JSON + Markdown only under
# tmp/phase10e-export-sidecar/. It never calls the Phase 7D wrapper, approval
# primitives, or any Phase 8/9/10C/10D runtime script. It is not
# authentication, not RBAC enforcement, and not approval.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

BUILD_SCRIPT="$REPO_ROOT/scripts/dev/build_phase10e_export_sidecar.py"

fail() {
  echo "$1" >&2
  exit 1
}

[ "${ENABLE_AUTOPUBLISH:-false}" != "true" ] || fail "ENABLE_AUTOPUBLISH=true is not allowed"
[ "${APPROVE_PROMOTE:-false}" != "true" ] || fail "APPROVE_PROMOTE is not allowed in this prototype command"
[ "${APPROVE_DECISION:-false}" != "true" ] || fail "APPROVE_DECISION is not allowed in this prototype command"
[ "${APPROVE_FINALIZE:-false}" != "true" ] || fail "APPROVE_FINALIZE is not allowed in this prototype command"

[ -f "$BUILD_SCRIPT" ] || fail "Missing Phase 10E build script: $BUILD_SCRIPT"

if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  PYTHON_BIN="$(command -v python)"
fi

exec "$PYTHON_BIN" "$BUILD_SCRIPT" "$@"
