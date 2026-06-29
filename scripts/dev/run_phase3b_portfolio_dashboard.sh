#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

PORTFOLIO_SCRIPT="$REPO_ROOT/scripts/dev/portfolio_dashboard.py"

fail() {
  echo "$1" >&2
  exit 1
}

usage() {
  echo "Usage: bash scripts/dev/run_phase3b_portfolio_dashboard.sh <week> [--top N] [--write]" >&2
  exit 1
}

if [ "$#" -lt 1 ]; then
  usage
fi

REPORT_WEEK="$1"
shift

# ── Guardrails (before any work) ─────────────────────────────────────────────
[ "${ENABLE_AUTOPUBLISH:-false}" != "true" ] || fail "ENABLE_AUTOPUBLISH=true is not allowed"
[ "${ENABLE_OPENAI_API_DIRECT:-false}" != "true" ] || fail "ENABLE_OPENAI_API_DIRECT=true is not allowed"

# ── Validate week before invoking Python ─────────────────────────────────────
printf '%s' "$REPORT_WEEK" | grep -Eq '^[0-9]{4}-W[0-9]{2}$' \
  || fail "week must match ^[0-9]{4}-W[0-9]{2}\$, got: $REPORT_WEEK"

# ── Parse optional flags (--top N, --write) ──────────────────────────────────
PY_ARGS=()
while [ "$#" -gt 0 ]; do
  case "$1" in
    --top)
      shift
      [ "$#" -ge 1 ] || usage
      printf '%s' "$1" | grep -Eq '^[1-9][0-9]*$' \
        || fail "--top must be an integer >= 1, got: $1"
      PY_ARGS+=(--top "$1")
      shift
      ;;
    --write)
      PY_ARGS+=(--write)
      shift
      ;;
    *)
      usage
      ;;
  esac
done

[ -f "$PORTFOLIO_SCRIPT" ] || fail "Missing portfolio script: $PORTFOLIO_SCRIPT"

# ── Select Python: .venv -> python3 -> python ────────────────────────────────
if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  PYTHON_BIN="$(command -v python)"
fi

cd "$REPO_ROOT"
exec "$PYTHON_BIN" "$PORTFOLIO_SCRIPT" --week "$REPORT_WEEK" ${PY_ARGS[@]+"${PY_ARGS[@]}"}
