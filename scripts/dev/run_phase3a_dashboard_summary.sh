#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

DASHBOARD_SCRIPT="$REPO_ROOT/scripts/dev/dashboard_summary.py"

fail() {
  echo "$1" >&2
  exit 1
}

usage() {
  echo "Usage: bash scripts/dev/run_phase3a_dashboard_summary.sh <product-id> <week> [--write]" >&2
  exit 1
}

if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
  usage
fi

PRODUCT_ID="$1"
REPORT_WEEK="$2"
WRITE_FLAG=""
if [ "$#" -eq 3 ]; then
  [ "$3" = "--write" ] || usage
  WRITE_FLAG="--write"
fi

# ── Guardrails (before any work) ─────────────────────────────────────────────
[ "${ENABLE_AUTOPUBLISH:-false}" != "true" ] || fail "ENABLE_AUTOPUBLISH=true is not allowed"
[ "${ENABLE_OPENAI_API_DIRECT:-false}" != "true" ] || fail "ENABLE_OPENAI_API_DIRECT=true is not allowed"

# ── Validate inputs before invoking Python ───────────────────────────────────
printf '%s' "$PRODUCT_ID" | grep -Eq '^[a-z0-9-]+$' \
  || fail "product-id must match ^[a-z0-9-]+\$, got: $PRODUCT_ID"
printf '%s' "$REPORT_WEEK" | grep -Eq '^[0-9]{4}-W[0-9]{2}$' \
  || fail "week must match ^[0-9]{4}-W[0-9]{2}\$, got: $REPORT_WEEK"

[ -f "$DASHBOARD_SCRIPT" ] || fail "Missing dashboard script: $DASHBOARD_SCRIPT"

# ── Select Python: .venv -> python3 -> python ────────────────────────────────
if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  PYTHON_BIN="$(command -v python)"
fi

cd "$REPO_ROOT"
if [ -n "$WRITE_FLAG" ]; then
  exec "$PYTHON_BIN" "$DASHBOARD_SCRIPT" --product-id "$PRODUCT_ID" --week "$REPORT_WEEK" --write
else
  exec "$PYTHON_BIN" "$DASHBOARD_SCRIPT" --product-id "$PRODUCT_ID" --week "$REPORT_WEEK"
fi
