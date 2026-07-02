#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

WRAPPER="$REPO_ROOT/scripts/dev/run_phase7d_single_gate_wrapper.sh"
WRAPPER_CORE="$REPO_ROOT/scripts/dev/execute_single_gate_approval.py"
VERIFIER="$REPO_ROOT/scripts/dev/run_phase7b_audit_verifier.sh"
BUILDER="$REPO_ROOT/scripts/dev/build_phase7g_operator_acceptance_summary.py"
OUT_DIR="$REPO_ROOT/tmp/phase7g-operator-acceptance"

if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  PYTHON_BIN="$(command -v python)"
fi

for required in "$WRAPPER" "$WRAPPER_CORE" "$VERIFIER" "$BUILDER"; do
  [ -f "$required" ] || {
    echo "Missing required Phase 7 component: $required" >&2
    exit 1
  }
done

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"

RUN_ID="phase7g-safe-demo-$$"
MISSING_ID="phase7g-missing-$$"
REPORT_WEEK="2026-W27"
PACKET="$REPO_ROOT/tmp/phase6b-approval-review/review-$RUN_ID-$REPORT_WEEK.json"
VERIFICATION="$REPO_ROOT/tmp/phase6c-approval-review-verifier/verification-review-$RUN_ID-$REPORT_WEEK.json"
PLAN="$REPO_ROOT/tmp/phase6e-approval-execution-plan/execution-plan-$RUN_ID-$REPORT_WEEK.json"
AUDIT_DIR="$REPO_ROOT/tmp/phase7d-single-gate-wrapper"

GENERATED_INPUTS=("$PACKET" "$VERIFICATION" "$PLAN")
GENERATED_AUDITS=()

cleanup() {
  rm -f "${GENERATED_INPUTS[@]}"
  if [ "${#GENERATED_AUDITS[@]}" -gt 0 ]; then
    rm -f "${GENERATED_AUDITS[@]}"
  fi
}
trap cleanup EXIT

mkdir -p "$(dirname "$PACKET")" "$(dirname "$VERIFICATION")" "$(dirname "$PLAN")"

if [ -e "$PACKET" ] || [ -e "$VERIFICATION" ] || [ -e "$PLAN" ]; then
  echo "Refusing to overwrite existing safe-demo input" >&2
  exit 1
fi

cat >"$PACKET" <<EOF
{
  "dry_run": true,
  "product_id": "$RUN_ID",
  "report_week": "$REPORT_WEEK",
  "sources": [
    {
      "name": "phase2e_score",
      "path": "tmp/phase2e-import-score-report/scores/$RUN_ID.json"
    }
  ],
  "score": {"score_decision": "watchlist"},
  "compliance_status": "not_evaluated",
  "gates": {}
}
EOF

cat >"$VERIFICATION" <<EOF
{
  "verdict": "ready",
  "product_id": "$RUN_ID",
  "report_week": "$REPORT_WEEK"
}
EOF

cat >"$PLAN" <<EOF
{
  "dry_run": true,
  "verdict": "ready",
  "product_id": "$RUN_ID",
  "report_week": "$REPORT_WEEK",
  "per_gate_plan": {
    "promote": {
      "plan_ready": true,
      "blocked_reason": null
    }
  }
}
EOF

record_scenario() {
  local number="$1"
  local scenario_id="$2"
  local expected_result="$3"
  local observed_exit_code="$4"
  local passed="$5"
  local observation_mode="$6"
  local audit_artifact="${7:-}"
  local audit_json=""
  if [ -n "$audit_artifact" ]; then
    audit_json="\"$audit_artifact\""
  fi
  cat >"$OUT_DIR/scenario-$number-$scenario_id.json" <<EOF
{
  "scenario_id": "$scenario_id",
  "expected_result": "$expected_result",
  "observed_exit_code": $observed_exit_code,
  "passed": $passed,
  "observation_mode": "$observation_mode",
  "primitive_success": false,
  "audit_artifacts": [$audit_json]
}
EOF
}

run_wrapper() {
  env \
    -u APPROVE_PROMOTE \
    -u APPROVE_DECISION \
    -u APPROVE_FINALIZE \
    -u APPROVE_ALL \
    -u GLOBAL_APPROVAL \
    -u APPROVE_GLOBAL \
    -u ENABLE_GLOBAL_APPROVAL \
    -u AFFILIATE_PHASE7D_EMERGENCY_STOP \
    bash "$WRAPPER" "$@"
}

capture_wrapper_scenario() {
  local number="$1"
  local scenario_id="$2"
  local expected_result="$3"
  local expected_code="$4"
  shift 4
  local stdout_file="$OUT_DIR/scenario-$number-$scenario_id.stdout"
  local stderr_file="$OUT_DIR/scenario-$number-$scenario_id.stderr"
  local observed_code
  set +e
  run_wrapper "$@" >"$stdout_file" 2>"$stderr_file"
  observed_code=$?
  set -e

  local audit_rel=""
  local audit_abs=""
  audit_rel="$(sed -n 's/^audit_path: //p' "$stdout_file" | tail -n 1)"
  if [ -n "$audit_rel" ]; then
    audit_abs="$REPO_ROOT/$audit_rel"
    [ -f "$audit_abs" ] || {
      echo "Wrapper reported a missing audit artifact: $audit_rel" >&2
      exit 1
    }
    GENERATED_AUDITS+=("$audit_abs")
  fi

  if [ "$observed_code" -ne "$expected_code" ]; then
    record_scenario "$number" "$scenario_id" "$expected_result" "$observed_code" false "wrapper" "$audit_rel"
    echo "Unexpected exit code for $scenario_id: $observed_code" >&2
    exit 1
  fi
  record_scenario "$number" "$scenario_id" "$expected_result" "$observed_code" true "wrapper" "$audit_rel"
}

capture_wrapper_scenario \
  "01" "no_execute_dry_run" "prevented without runtime execution intent" "2" \
  promote "$RUN_ID" "$REPORT_WEEK" \
  --operator "phase7g-demo-operator" \
  --reason "safe operator acceptance" \
  --intent "observe selected gate prevention"

capture_wrapper_scenario \
  "02" "missing_evidence" "blocked before any approval evaluation" "3" \
  promote "$MISSING_ID" "$REPORT_WEEK" \
  --operator "phase7g-demo-operator" \
  --reason "safe missing evidence check" \
  --intent "observe evidence block"

capture_wrapper_scenario \
  "03" "approve_all_text" "rejected as unsafe operator wording" "2" \
  promote "$RUN_ID" "$REPORT_WEEK" \
  --operator "phase7g-demo-operator" \
  --reason "safe wording rejection check" \
  --intent "approve-all"

capture_wrapper_scenario \
  "04" "chain_next_gate" "rejected as multiple gate input" "1" \
  promote "$RUN_ID" "$REPORT_WEEK" \
  --operator "phase7g-demo-operator" \
  --reason "safe chain wording check" \
  --intent "single selected gate only" \
  decision

capture_wrapper_scenario \
  "05" "invalid_gate" "rejected as an invalid selected gate" "1" \
  invalid "$RUN_ID" "$REPORT_WEEK" \
  --operator "phase7g-demo-operator" \
  --reason "safe invalid gate check" \
  --intent "observe invalid gate rejection"

set +e
grep -q "AFFILIATE_PHASE7D_EMERGENCY_STOP" "$WRAPPER_CORE" &&
  grep -q "EMERGENCY_STOP file is active" "$WRAPPER_CORE"
EMERGENCY_CODE=$?
set -e
[ "$EMERGENCY_CODE" -eq 0 ] || {
  echo "Emergency-stop guard inventory check failed" >&2
  exit 1
}
record_scenario "06" "emergency_stop" "prevented by the unchanged emergency-stop guard" "$EMERGENCY_CODE" true "static_guard_inventory"

set +e
grep -q "matching gate-specific approval flag is required" "$WRAPPER_CORE" &&
  grep -q "unrelated truthy approval flags are not allowed" "$WRAPPER_CORE"
FLAG_CODE=$?
set -e
[ "$FLAG_CODE" -eq 0 ] || {
  echo "Approval-flag guard inventory check failed" >&2
  exit 1
}
record_scenario "07" "wrong_approval_flag" "rejected by unchanged gate-specific flag guards" "$FLAG_CODE" true "static_guard_inventory"

AUDIT_CODE=0
AUDIT_REL=""
for audit_abs in "${GENERATED_AUDITS[@]}"; do
  audit_rel="${audit_abs#"$REPO_ROOT/"}"
  if ! "$PYTHON_BIN" - "$audit_abs" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
valid = (
    payload.get("outcome") in {"prevented", "blocked"}
    and payload.get("mutation_attempted") is False
)
raise SystemExit(0 if valid else 1)
PY
  then
    AUDIT_CODE=1
  fi
done
[ "${#GENERATED_AUDITS[@]}" -gt 0 ] || AUDIT_CODE=1
[ "$AUDIT_CODE" -eq 0 ] || {
  echo "Safe audit artifact validation failed" >&2
  exit 1
}
record_scenario "08" "audit_artifact_generation" "safe result audits exist with no mutation attempted" "$AUDIT_CODE" true "artifact_inspection" "$AUDIT_REL"

HANDOFF_CODE=0
[ -x "$VERIFIER" ] || HANDOFF_CODE=1
[ "$HANDOFF_CODE" -eq 0 ] || {
  echo "Phase 7B verifier handoff is unavailable" >&2
  exit 1
}
record_scenario "09" "phase7b_verifier_handoff" "read-only verifier handoff is available and remains separate" "$HANDOFF_CODE" true "inventory_note"

"$PYTHON_BIN" "$BUILDER"
