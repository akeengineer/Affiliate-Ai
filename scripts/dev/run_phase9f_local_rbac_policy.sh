#!/usr/bin/env bash
# Phase 9F Local RBAC Policy Prototype wrapper.
#
# Local-only, advisory-only, metadata-only, evidence-only. Forwards CLI
# arguments to scripts/dev/evaluate_phase9f_local_rbac_policy.py, which reads a
# local RBAC policy JSON and a local subject/resource/action request JSON,
# optionally consults an existing Phase 9C operator registry and/or Phase 9D
# actor attribution report as advisory context, evaluates advisory RBAC
# eligibility, and writes an advisory decision report only under
# tmp/phase9f-local-rbac-policy/. It is not enforcement, not authentication, not
# RBAC runtime permission gating, not login, not a session store, and not a user
# database. It never calls the Phase 7D wrapper or an approval primitive, never
# calls any Phase 8 runtime script, never calls the Phase 9C registry tool or
# the Phase 9D attribution tool, never writes the vault, never triggers the next
# gate, and never performs network, database, key-generation, or external
# signing/encryption behavior. An advisory allow decision is not approval, and
# the advisory report is evidence only.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

EVAL_SCRIPT="$REPO_ROOT/scripts/dev/evaluate_phase9f_local_rbac_policy.py"

fail() {
  echo "$1" >&2
  exit 1
}

# ── Guardrails (reject approval and automation flags) ────────────────────────
[ "${ENABLE_AUTOPUBLISH:-false}" != "true" ] || fail "ENABLE_AUTOPUBLISH=true is not allowed"
[ "${APPROVE_PROMOTE:-false}" != "true" ] || fail "APPROVE_PROMOTE is not allowed in this prototype command"
[ "${APPROVE_DECISION:-false}" != "true" ] || fail "APPROVE_DECISION is not allowed in this prototype command"
[ "${APPROVE_FINALIZE:-false}" != "true" ] || fail "APPROVE_FINALIZE is not allowed in this prototype command"

[ -f "$EVAL_SCRIPT" ] || fail "Missing Phase 9F evaluator script: $EVAL_SCRIPT"

# ── Select Python: .venv -> python3 -> python ────────────────────────────────
if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  PYTHON_BIN="$(command -v python)"
fi

exec "$PYTHON_BIN" "$EVAL_SCRIPT" "$@"
