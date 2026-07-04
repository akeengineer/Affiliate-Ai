#!/usr/bin/env bash
# Phase 10C local evidence bundle wrapper.
#
# Local-only derived evidence bundle runtime prototype. Reads one local manifest,
# validates safe evidence/context references, hashes present files, treats safe
# missing files as warnings, rejects unsafe paths, secrets, approval flags, and
# execution intent, and writes deterministic JSON + Markdown only under
# tmp/phase10c-local-evidence-bundle/. It never calls the Phase 7D wrapper, an
# approval primitive, or any Phase 8/9 runtime script. It is not authentication,
# not RBAC enforcement, and not approval.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

BUILD_SCRIPT="$REPO_ROOT/scripts/dev/build_phase10c_local_evidence_bundle.py"

fail() {
  echo "$1" >&2
  exit 1
}

[ "${ENABLE_AUTOPUBLISH:-false}" != "true" ] || fail "ENABLE_AUTOPUBLISH=true is not allowed"
[ "${APPROVE_PROMOTE:-false}" != "true" ] || fail "APPROVE_PROMOTE is not allowed in this prototype command"
[ "${APPROVE_DECISION:-false}" != "true" ] || fail "APPROVE_DECISION is not allowed in this prototype command"
[ "${APPROVE_FINALIZE:-false}" != "true" ] || fail "APPROVE_FINALIZE is not allowed in this prototype command"

[ -f "$BUILD_SCRIPT" ] || fail "Missing Phase 10C build script: $BUILD_SCRIPT"

if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  PYTHON_BIN="$(command -v python)"
fi

exec "$PYTHON_BIN" "$BUILD_SCRIPT" "$@"
