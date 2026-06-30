#!/usr/bin/env bash
# Phase 3D Operator Acceptance Pack.
#
# Deterministic acceptance/demo proof. Drives the operator entrypoint
# (command_center.sh) through doctor -> dry-run -> product --write ->
# portfolio --top 5 --write, verifies the expected tmp artifacts exist, and
# proves the run wrote nothing to the vault via a before/after snapshot diff.
#
# It routes through command_center.sh ONLY. It never calls downstream wrappers
# directly, never routes to approved Phase 2G/2H/2I workflows, and never writes
# the vault.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

COMMAND_CENTER="$REPO_ROOT/scripts/dev/command_center.sh"

WEEK_RE='^[0-9]{4}-W[0-9]{2}$'
PRODUCT_ID_RE='^[a-z0-9-]+$'

DEFAULT_CSV="vault/samples/import/product-candidates.csv"
DEFAULT_WEEK="2026-W26"
DEFAULT_PRODUCT_ID="prod-laptop-stand"

VAULT_PRODUCTS_DIR="$REPO_ROOT/vault/products"
VAULT_DECISIONS_DIR="$REPO_ROOT/vault/decisions"

TMP_OUT=""
cleanup() {
  [ -z "$TMP_OUT" ] || rm -f "$TMP_OUT"
}
trap cleanup EXIT

fail_acceptance() {
  echo "$1"
  echo "acceptance_status: failed"
  exit 1
}

usage() {
  cat <<'EOF' >&2
Usage:
  bash scripts/dev/run_phase3d_acceptance.sh
  bash scripts/dev/run_phase3d_acceptance.sh <csv_path> <week> <product_id>

Accepts either 0 args (deterministic defaults) or exactly 3 args.
EOF
}

# ── 1. Validate arguments ────────────────────────────────────────────────────
if [ "$#" -eq 0 ]; then
  CSV_PATH="$DEFAULT_CSV"
  WEEK="$DEFAULT_WEEK"
  PRODUCT_ID="$DEFAULT_PRODUCT_ID"
elif [ "$#" -eq 3 ]; then
  CSV_PATH="$1"
  WEEK="$2"
  PRODUCT_ID="$3"
else
  usage
  exit 1
fi

[ -f "$REPO_ROOT/$CSV_PATH" ] || [ -f "$CSV_PATH" ] \
  || { echo "csv_path does not exist or is not a file: $CSV_PATH" >&2; exit 1; }
printf '%s' "$WEEK" | grep -Eq "$WEEK_RE" \
  || { echo "week must match $WEEK_RE, got: $WEEK" >&2; exit 1; }
printf '%s' "$PRODUCT_ID" | grep -Eq "$PRODUCT_ID_RE" \
  || { echo "product_id must match $PRODUCT_ID_RE, got: $PRODUCT_ID" >&2; exit 1; }

[ -x "$COMMAND_CENTER" ] || { echo "Missing or non-executable command center: $COMMAND_CENTER" >&2; exit 1; }

# Resolve all relative sample/artifact paths against the repo root, not the
# caller CWD, so the chain rebuilds Phase 2E identically from any directory.
cd "$REPO_ROOT"

TMP_OUT="$(mktemp)"

# ── 2. Before snapshot (count only; never emit vault paths) ──────────────────
count_files() {
  local dir="$1"
  if [ -d "$dir" ]; then
    find "$dir" -maxdepth 1 -type f | wc -l | tr -d ' '
  else
    printf '0'
  fi
}

before_products="$(count_files "$VAULT_PRODUCTS_DIR")"
before_decisions="$(count_files "$VAULT_DECISIONS_DIR")"

# ── 3-6. Drive command_center.sh and require the success token ───────────────
run_step() {
  local label="$1" token="$2"
  shift 2
  if bash "$COMMAND_CENTER" "$@" >"$TMP_OUT" 2>&1 && grep -q "$token" "$TMP_OUT"; then
    echo "step: $label -> PASS"
  else
    echo "step: $label -> FAIL"
    sed 's#vault/[A-Za-z0-9._/-]*#[vault-path-redacted]#g' "$TMP_OUT" >&2
    fail_acceptance "step: $label -> FAIL"
  fi
}

run_step "doctor" "doctor_status: success" doctor
run_step "dry-run" "final_status: success" dry-run "$CSV_PATH" "$WEEK" "$PRODUCT_ID"
run_step "product --write" "phase3a_status: success" product "$PRODUCT_ID" "$WEEK" --write
run_step "portfolio --top 5 --write" "phase3b_status: success" portfolio "$WEEK" --top 5 --write

# ── 7. Verify expected tmp artifacts ─────────────────────────────────────────
EXPECTED_ARTIFACTS=(
  "tmp/phase2e-import-score-report/scores/$PRODUCT_ID.json"
  "tmp/phase2e-import-score-report/weekly-report-$WEEK.md"
  "tmp/phase2f-hermes/operational-summary-$WEEK.md"
  "tmp/phase2j-hermes-governance/governance-summary-$WEEK.md"
  "tmp/phase3a-dashboard/dashboard-$PRODUCT_ID-$WEEK.md"
  "tmp/phase3b-portfolio-dashboard/portfolio-$WEEK.md"
)

for artifact in "${EXPECTED_ARTIFACTS[@]}"; do
  if [ -f "$REPO_ROOT/$artifact" ]; then
    echo "artifact: $artifact -> PRESENT"
  else
    echo "artifact: $artifact -> FAIL"
    fail_acceptance "artifact: $artifact -> FAIL"
  fi
done

# ── 8-9. After snapshot + diff ───────────────────────────────────────────────
after_products="$(count_files "$VAULT_PRODUCTS_DIR")"
after_decisions="$(count_files "$VAULT_DECISIONS_DIR")"

products_writes="$((after_products - before_products))"
decisions_writes="$((after_decisions - before_decisions))"

echo "vault_products_writes: $products_writes"
echo "vault_decisions_writes: $decisions_writes"

if [ "$products_writes" -ne 0 ] || [ "$decisions_writes" -ne 0 ]; then
  fail_acceptance "vault diff detected (products_writes=$products_writes decisions_writes=$decisions_writes)"
fi

# ── 10. Success ──────────────────────────────────────────────────────────────
echo "acceptance_status: success"
