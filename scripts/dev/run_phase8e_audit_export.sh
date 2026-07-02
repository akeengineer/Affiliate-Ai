#!/usr/bin/env bash
# Phase 8E Audit Export Pack wrapper.
#
# Read-only export pack builder over Phase 8B/8C/8D local audit evidence.
# Never appends to or otherwise mutates any source evidence file, never
# calls the Phase 7D wrapper or an approval primitive, never calls the
# Phase 8B ingest writer, never calls the Phase 8C verifier, never calls the
# Phase 8D query CLI, never writes the vault, and never calls a backend/API/
# database or external service.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

EXPORT_SCRIPT="$REPO_ROOT/scripts/dev/build_phase8e_audit_export_pack.py"

fail() {
  echo "$1" >&2
  exit 1
}

# ── Guardrails (read-only; reject approval and automation flags) ─────────────
[ "${ENABLE_AUTOPUBLISH:-false}" != "true" ] || fail "ENABLE_AUTOPUBLISH=true is not allowed"
[ "${ENABLE_OPENAI_API_DIRECT:-false}" != "true" ] || fail "ENABLE_OPENAI_API_DIRECT=true is not allowed"
[ "${APPROVE_PROMOTE:-false}" != "true" ] || fail "APPROVE_PROMOTE is not allowed in this read-only command"
[ "${APPROVE_DECISION:-false}" != "true" ] || fail "APPROVE_DECISION is not allowed in this read-only command"
[ "${APPROVE_FINALIZE:-false}" != "true" ] || fail "APPROVE_FINALIZE is not allowed in this read-only command"

[ -f "$EXPORT_SCRIPT" ] || fail "Missing export script: $EXPORT_SCRIPT"

# ── Select Python: .venv -> python3 -> python ────────────────────────────────
if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  PYTHON_BIN="$(command -v python)"
fi

exec "$PYTHON_BIN" "$EXPORT_SCRIPT" "$@"
