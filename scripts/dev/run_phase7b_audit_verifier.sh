#!/usr/bin/env bash
# Phase 7B Manual Approval Audit Verifier wrapper.
#
# Runtime read-only verifier over one JSON manual approval audit artifact. Never
# reads/writes the vault, never executes an approval primitive, never uses an
# approval flag, and never calls external services. Output goes only under
# tmp/phase7b-audit-verifier/.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

VERIFY_SCRIPT="$REPO_ROOT/scripts/dev/verify_manual_approval_audit.py"

fail() {
  echo "$1" >&2
  exit 1
}

if [ "$#" -ne 1 ]; then
  echo "Usage: bash scripts/dev/run_phase7b_audit_verifier.sh <audit_artifact_path>" >&2
  exit 1
fi

AUDIT_PATH="$1"

# ── Guardrails (read-only; reject approval and automation flags) ─────────────
[ "${ENABLE_AUTOPUBLISH:-false}" != "true" ] || fail "ENABLE_AUTOPUBLISH=true is not allowed"
[ "${ENABLE_OPENAI_API_DIRECT:-false}" != "true" ] || fail "ENABLE_OPENAI_API_DIRECT=true is not allowed"
[ "${APPROVE_PROMOTE:-false}" != "true" ] || fail "APPROVE_PROMOTE is not allowed in this read-only command"
[ "${APPROVE_DECISION:-false}" != "true" ] || fail "APPROVE_DECISION is not allowed in this read-only command"
[ "${APPROVE_FINALIZE:-false}" != "true" ] || fail "APPROVE_FINALIZE is not allowed in this read-only command"

[ -f "$VERIFY_SCRIPT" ] || fail "Missing verifier script: $VERIFY_SCRIPT"

# ── Select Python: .venv -> python3 -> python ────────────────────────────────
if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  PYTHON_BIN="$(command -v python)"
fi

exec "$PYTHON_BIN" "$VERIFY_SCRIPT" "$AUDIT_PATH"
