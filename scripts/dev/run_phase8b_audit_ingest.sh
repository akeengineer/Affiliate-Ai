#!/usr/bin/env bash
# Phase 8B Local Append-only Audit Store - ingest wrapper.
#
# Reads one existing audit artifact and appends a normalized durable audit
# record to the local ignored JSONL store under tmp/phase8b-audit-store/.
# Ingest-only: never calls the Phase 7D wrapper, never executes an approval
# primitive, never runs the Phase 7B verifier automatically, never writes the
# vault, and never calls a backend/API/database or external service.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

INGEST_SCRIPT="$REPO_ROOT/scripts/dev/ingest_phase8b_audit_record.py"

fail() {
  echo "$1" >&2
  exit 1
}

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "Usage: bash scripts/dev/run_phase8b_audit_ingest.sh <audit_artifact_path> [operator_note]" >&2
  exit 1
fi

AUDIT_PATH="$1"
OPERATOR_NOTE="${2:-}"

# ── Guardrails (ingest-only; reject approval and automation flags) ───────────
[ "${ENABLE_AUTOPUBLISH:-false}" != "true" ] || fail "ENABLE_AUTOPUBLISH=true is not allowed"
[ "${ENABLE_OPENAI_API_DIRECT:-false}" != "true" ] || fail "ENABLE_OPENAI_API_DIRECT=true is not allowed"
[ "${APPROVE_PROMOTE:-false}" != "true" ] || fail "APPROVE_PROMOTE is not allowed in this ingest-only command"
[ "${APPROVE_DECISION:-false}" != "true" ] || fail "APPROVE_DECISION is not allowed in this ingest-only command"
[ "${APPROVE_FINALIZE:-false}" != "true" ] || fail "APPROVE_FINALIZE is not allowed in this ingest-only command"

[ -f "$INGEST_SCRIPT" ] || fail "Missing ingest script: $INGEST_SCRIPT"

# ── Select Python: .venv -> python3 -> python ────────────────────────────────
if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  PYTHON_BIN="$(command -v python)"
fi

if [ -n "$OPERATOR_NOTE" ]; then
  exec "$PYTHON_BIN" "$INGEST_SCRIPT" --audit-artifact "$AUDIT_PATH" --operator-note "$OPERATOR_NOTE"
else
  exec "$PYTHON_BIN" "$INGEST_SCRIPT" --audit-artifact "$AUDIT_PATH"
fi
