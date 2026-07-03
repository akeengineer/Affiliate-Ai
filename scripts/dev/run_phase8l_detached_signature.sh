#!/usr/bin/env bash
# Phase 8L Local Detached Signature Prototype wrapper.
#
# Local-only, prototype-only. Forwards CLI arguments to
# scripts/dev/build_phase8l_detached_signature.py, which reads a Phase 8E
# export manifest (and optionally a Phase 8G/8H integrity report) and writes a
# signed payload descriptor, a detached signature envelope, and a summary only
# under tmp/phase8l-detached-signature/. It never signs with real key material,
# never generates or persists keys, never calls the Phase 7D wrapper or an
# approval primitive, never calls the Phase 7B verifier, the Phase 8B ingest
# writer, the Phase 8C verifier, the Phase 8D query CLI, the Phase 8E export
# builder, or the Phase 8G verifier, never writes the vault, never triggers the
# next gate, and never calls a backend/API/database, network, or external
# signing/key-generation tool. A prototype signature is evidence only; it is
# not approval.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

BUILD_SCRIPT="$REPO_ROOT/scripts/dev/build_phase8l_detached_signature.py"

fail() {
  echo "$1" >&2
  exit 1
}

# ── Guardrails (reject approval and automation flags) ────────────────────────
[ "${ENABLE_AUTOPUBLISH:-false}" != "true" ] || fail "ENABLE_AUTOPUBLISH=true is not allowed"
[ "${ENABLE_OPENAI_API_DIRECT:-false}" != "true" ] || fail "ENABLE_OPENAI_API_DIRECT=true is not allowed"
[ "${APPROVE_PROMOTE:-false}" != "true" ] || fail "APPROVE_PROMOTE is not allowed in this prototype command"
[ "${APPROVE_DECISION:-false}" != "true" ] || fail "APPROVE_DECISION is not allowed in this prototype command"
[ "${APPROVE_FINALIZE:-false}" != "true" ] || fail "APPROVE_FINALIZE is not allowed in this prototype command"

[ -f "$BUILD_SCRIPT" ] || fail "Missing Phase 8L build script: $BUILD_SCRIPT"

# ── Select Python: .venv -> python3 -> python ────────────────────────────────
if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  PYTHON_BIN="$(command -v python)"
fi

exec "$PYTHON_BIN" "$BUILD_SCRIPT" "$@"
