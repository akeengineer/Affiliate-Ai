#!/usr/bin/env bash
# Phase 9D Actor Attribution in Audit/Reports wrapper.
#
# Local-only, metadata-only, evidence-only. Forwards CLI arguments to
# scripts/dev/build_phase9d_actor_attribution_report.py, which reads an existing
# Phase 9C local operator registry and a local evidence/report reference file,
# attaches selected actor metadata to each evidence reference, and writes an
# actor-attributed report only under tmp/phase9d-actor-attribution/. It is not
# authentication, not RBAC, not login, not a session store, and not a user
# database. It never calls the Phase 7D wrapper or an approval primitive, never
# calls any Phase 8 runtime script, never writes the vault, never triggers the
# next gate, and never performs network, database, key-generation, or external
# signing/encryption behavior. Actor attribution is evidence only; it is not
# approval.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

BUILD_SCRIPT="$REPO_ROOT/scripts/dev/build_phase9d_actor_attribution_report.py"

fail() {
  echo "$1" >&2
  exit 1
}

# ── Guardrails (reject approval and automation flags) ────────────────────────
[ "${ENABLE_AUTOPUBLISH:-false}" != "true" ] || fail "ENABLE_AUTOPUBLISH=true is not allowed"
[ "${APPROVE_PROMOTE:-false}" != "true" ] || fail "APPROVE_PROMOTE is not allowed in this prototype command"
[ "${APPROVE_DECISION:-false}" != "true" ] || fail "APPROVE_DECISION is not allowed in this prototype command"
[ "${APPROVE_FINALIZE:-false}" != "true" ] || fail "APPROVE_FINALIZE is not allowed in this prototype command"

[ -f "$BUILD_SCRIPT" ] || fail "Missing Phase 9D build script: $BUILD_SCRIPT"

# ── Select Python: .venv -> python3 -> python ────────────────────────────────
if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  PYTHON_BIN="$(command -v python)"
fi

exec "$PYTHON_BIN" "$BUILD_SCRIPT" "$@"
