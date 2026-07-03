#!/usr/bin/env bash
# Phase 8M Detached Signature Verifier Prototype wrapper.
#
# Local-only, prototype-only. Forwards CLI arguments to
# scripts/dev/verify_phase8m_detached_signature.py, which reads Phase 8L
# descriptor/envelope (and optionally the Phase 8L summary), recomputes the
# signed payload hash, verifies the HMAC-SHA256 prototype signature when the
# in-memory prototype key is provided, and writes a verification report only
# under tmp/phase8m-detached-signature-verifier/. It never signs anything,
# never generates or persists keys, never calls the Phase 7D wrapper or an
# approval primitive, never calls the Phase 7B verifier, the Phase 8B ingest
# writer, the Phase 8C verifier, the Phase 8D query CLI, the Phase 8E export
# builder, the Phase 8G verifier, or the Phase 8L signing script, never writes
# the vault, never triggers the next gate, and never calls a backend/API/
# database, network, or external signing/key-generation tool. A verified
# prototype signature is evidence only; it is not approval.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

VERIFY_SCRIPT="$REPO_ROOT/scripts/dev/verify_phase8m_detached_signature.py"

fail() {
  echo "$1" >&2
  exit 1
}

# ── Guardrails (reject approval and automation flags) ────────────────────────
[ "${ENABLE_AUTOPUBLISH:-false}" != "true" ] || fail "ENABLE_AUTOPUBLISH=true is not allowed"
[ "${ENABLE_OPENAI_API_DIRECT:-false}" != "true" ] || fail "ENABLE_OPENAI_API_DIRECT=true is not allowed"
[ "${APPROVE_PROMOTE:-false}" != "true" ] || fail "APPROVE_PROMOTE is not allowed in this read-only command"
[ "${APPROVE_DECISION:-false}" != "true" ] || fail "APPROVE_DECISION is not allowed in this read-only command"
[ "${APPROVE_FINALIZE:-false}" != "true" ] || fail "APPROVE_FINALIZE is not allowed in this read-only command"

[ -f "$VERIFY_SCRIPT" ] || fail "Missing Phase 8M verifier script: $VERIFY_SCRIPT"

# ── Select Python: .venv -> python3 -> python ────────────────────────────────
if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  PYTHON_BIN="$(command -v python)"
fi

exec "$PYTHON_BIN" "$VERIFY_SCRIPT" "$@"
