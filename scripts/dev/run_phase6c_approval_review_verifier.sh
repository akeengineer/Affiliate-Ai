#!/usr/bin/env bash
# Phase 6C Approval Review Packet Verifier wrapper.
#
# Read-only verifier over the Phase 6B dry-run review packet. Never reads/writes
# the vault, never executes an approval primitive, never uses an approval flag,
# and never calls external services.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

VERIFY_SCRIPT="$REPO_ROOT/scripts/dev/verify_approval_review_packet.py"
PRODUCT_ID_RE='^[a-z0-9-]+$'
WEEK_RE='^[0-9]{4}-W[0-9]{2}$'

fail() {
  echo "$1" >&2
  exit 1
}

if [ "$#" -ne 2 ]; then
  echo "Usage: bash scripts/dev/run_phase6c_approval_review_verifier.sh <product_id> <week>" >&2
  exit 1
fi

PRODUCT_ID="$1"
WEEK="$2"

# ── Guardrails (read-only; reject approval flags) ────────────────────────────
[ "${ENABLE_AUTOPUBLISH:-false}" != "true" ] || fail "ENABLE_AUTOPUBLISH=true is not allowed"
[ "${ENABLE_OPENAI_API_DIRECT:-false}" != "true" ] || fail "ENABLE_OPENAI_API_DIRECT=true is not allowed"
[ "${APPROVE_PROMOTE:-false}" != "true" ] || fail "APPROVE_PROMOTE is not allowed in this read-only command"
[ "${APPROVE_DECISION:-false}" != "true" ] || fail "APPROVE_DECISION is not allowed in this read-only command"
[ "${APPROVE_FINALIZE:-false}" != "true" ] || fail "APPROVE_FINALIZE is not allowed in this read-only command"

printf '%s' "$PRODUCT_ID" | grep -Eq "$PRODUCT_ID_RE" || fail "product_id must match $PRODUCT_ID_RE, got: $PRODUCT_ID"
printf '%s' "$WEEK" | grep -Eq "$WEEK_RE" || fail "week must match $WEEK_RE, got: $WEEK"

[ -f "$VERIFY_SCRIPT" ] || fail "Missing verifier script: $VERIFY_SCRIPT"

# ── Select Python: .venv -> python3 -> python ────────────────────────────────
if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  PYTHON_BIN="$(command -v python)"
fi

exec "$PYTHON_BIN" "$VERIFY_SCRIPT" --product-id "$PRODUCT_ID" --week "$WEEK"
