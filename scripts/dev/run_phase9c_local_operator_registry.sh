#!/usr/bin/env bash
# Phase 9C Local Operator Registry Prototype wrapper.
#
# Local-only, metadata-only, evidence-only. Forwards CLI arguments to
# scripts/dev/manage_phase9c_local_operator_registry.py, which reads a local
# JSON file of conceptual Phase 9B actor_metadata records, validates a local
# subset of that schema, optionally builds a deterministic local registry file,
# and writes reports only under tmp/phase9c-local-operator-registry/. It is not
# authentication, not RBAC, not login, not a session store, and not a user
# database. It never calls the Phase 7D wrapper or an approval primitive, never
# calls any Phase 8 runtime script, never writes the vault, never triggers the
# next gate, and never performs network, database, key-generation, or external
# signing/encryption behavior. A registry record is evidence only; it is not
# approval.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

MANAGE_SCRIPT="$REPO_ROOT/scripts/dev/manage_phase9c_local_operator_registry.py"

fail() {
  echo "$1" >&2
  exit 1
}

# ── Guardrails (reject approval and automation flags) ────────────────────────
[ "${ENABLE_AUTOPUBLISH:-false}" != "true" ] || fail "ENABLE_AUTOPUBLISH=true is not allowed"
[ "${APPROVE_PROMOTE:-false}" != "true" ] || fail "APPROVE_PROMOTE is not allowed in this prototype command"
[ "${APPROVE_DECISION:-false}" != "true" ] || fail "APPROVE_DECISION is not allowed in this prototype command"
[ "${APPROVE_FINALIZE:-false}" != "true" ] || fail "APPROVE_FINALIZE is not allowed in this prototype command"

[ -f "$MANAGE_SCRIPT" ] || fail "Missing Phase 9C manage script: $MANAGE_SCRIPT"

# ── Select Python: .venv -> python3 -> python ────────────────────────────────
if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  PYTHON_BIN="$(command -v python)"
fi

exec "$PYTHON_BIN" "$MANAGE_SCRIPT" "$@"
