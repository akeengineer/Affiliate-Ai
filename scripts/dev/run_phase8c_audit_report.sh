#!/usr/bin/env bash
# Phase 8C Audit Store Verifier / Reporting wrapper.
#
# Read-only verifier/reporting over the Phase 8B local append-only JSONL
# audit store. Never appends to or otherwise mutates the source JSONL,
# never calls the Phase 7D wrapper or an approval primitive, never runs the
# Phase 7B verifier automatically, never writes the vault, and never calls a
# backend/API/database or external service.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

VERIFY_SCRIPT="$REPO_ROOT/scripts/dev/verify_phase8c_audit_store.py"

fail() {
  echo "$1" >&2
  exit 1
}

if [ "$#" -gt 1 ]; then
  echo "Usage: bash scripts/dev/run_phase8c_audit_report.sh [store_path]" >&2
  exit 1
fi

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

if [ "$#" -eq 1 ]; then
  exec "$PYTHON_BIN" "$VERIFY_SCRIPT" --store-path "$1"
else
  exec "$PYTHON_BIN" "$VERIFY_SCRIPT"
fi
