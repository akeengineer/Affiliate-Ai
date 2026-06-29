#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

PHASE2E_SCRIPT="$REPO_ROOT/scripts/dev/run_phase2e_import_score_report.sh"
PHASE2F_SCRIPT="$REPO_ROOT/scripts/dev/run_phase2f_hermes_orchestration.sh"
PHASE2J_SCRIPT="$REPO_ROOT/scripts/dev/run_phase2j_governance_orchestration.sh"

fail() {
  echo "$1" >&2
  exit 1
}

if [ "$#" -ne 3 ]; then
  echo "Usage: bash scripts/dev/run_phase2_full_dry_run.sh <input-csv> <report-week> <product-id>" >&2
  exit 1
fi

INPUT_CSV="$1"
REPORT_WEEK="$2"
PRODUCT_ID="$3"

# ── Guardrails (before running anything) ─────────────────────────────────────
[ "${ENABLE_AUTOPUBLISH:-false}" != "true" ] || fail "ENABLE_AUTOPUBLISH=true is not allowed"
[ "${ENABLE_OPENAI_API_DIRECT:-false}" != "true" ] || fail "ENABLE_OPENAI_API_DIRECT=true is not allowed"

[ -x "$PHASE2E_SCRIPT" ] || fail "Missing or non-executable Phase 2E script: $PHASE2E_SCRIPT"
[ -x "$PHASE2F_SCRIPT" ] || fail "Missing or non-executable Phase 2F script: $PHASE2F_SCRIPT"
[ -x "$PHASE2J_SCRIPT" ] || fail "Missing or non-executable Phase 2J script: $PHASE2J_SCRIPT"

# ── Safe dry-run workflows only (no approved 2G/2H/2I, no vault writes) ───────
phase2e_output="$(bash "$PHASE2E_SCRIPT" "$INPUT_CSV" "$REPORT_WEEK")"
printf '%s\n' "$phase2e_output" | grep -q '^final_status: success' \
  || fail "Phase 2E dry-run did not report final_status: success"

phase2f_output="$(bash "$PHASE2F_SCRIPT" "$INPUT_CSV" "$REPORT_WEEK")"
printf '%s\n' "$phase2f_output" | grep -q '^phase2f_status: success' \
  || fail "Phase 2F dry-run did not report phase2f_status: success"

phase2j_output="$(bash "$PHASE2J_SCRIPT" "$INPUT_CSV" "$REPORT_WEEK" "$PRODUCT_ID")"
printf '%s\n' "$phase2j_output" | grep -q '^phase2j_status: success' \
  || fail "Phase 2J dry-run did not report phase2j_status: success"

# ── Concise summary ──────────────────────────────────────────────────────────
echo "phase2e_status: success"
echo "phase2f_status: success"
echo "phase2j_status: success"
echo "final_status: success"
