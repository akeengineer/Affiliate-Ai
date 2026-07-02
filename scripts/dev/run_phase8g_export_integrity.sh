#!/usr/bin/env bash
# Phase 8G Export Integrity Verifier wrapper.
#
# Local hash-only verifier over a Phase 8E export manifest. Never appends to
# or mutates the export pack or source evidence, never calls the Phase 7D
# wrapper or an approval primitive, never calls the Phase 8B ingest writer,
# the Phase 8C verifier, or the Phase 8D query CLI, never calls the Phase 8E
# export builder, never writes the vault, never signs anything, never
# generates keys, and never calls a backend/API/database or external
# service.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

VERIFY_SCRIPT="$REPO_ROOT/scripts/dev/verify_phase8g_export_integrity.py"

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

[ -f "$VERIFY_SCRIPT" ] || fail "Missing verifier script: $VERIFY_SCRIPT"

# ── Select Python: .venv -> python3 -> python ────────────────────────────────
if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  PYTHON_BIN="$(command -v python)"
fi

exec "$PYTHON_BIN" "$VERIFY_SCRIPT" "$@"
