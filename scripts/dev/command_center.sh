#!/usr/bin/env bash
# Phase 3C Operator Command Center.
#
# One safe operator entrypoint that routes to existing safe wrappers.
# It implements no business logic and only routes to read-only / dry-run
# workflows. It never routes to the approved Phase 2G/2H/2I vault-writing
# workflows, never writes the vault, and never calls external APIs.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

DRY_RUN_WRAPPER="$REPO_ROOT/scripts/dev/run_phase2_full_dry_run.sh"
PRODUCT_WRAPPER="$REPO_ROOT/scripts/dev/run_phase3a_dashboard_summary.sh"
PORTFOLIO_WRAPPER="$REPO_ROOT/scripts/dev/run_phase3b_portfolio_dashboard.sh"

WEEK_RE='^[0-9]{4}-W[0-9]{2}$'
PRODUCT_ID_RE='^[a-z0-9-]+$'

fail() {
  echo "$1" >&2
  exit 1
}

usage() {
  cat <<'EOF'
Affiliate Product Intelligence OS — Operator Command Center

Usage: bash scripts/dev/command_center.sh <command> [args...]

Commands:
  help                                       Print this usage and exit
  status                                     Print read-only runtime inventory
  doctor                                     Validate scripts, wrappers, and guardrail flags
  dry-run <csv_path> <week> <product_id>     Run the safe Phase 2E/2F/2J dry-run chain
  product <product_id> <week> [--write]      Single-product Phase 3A dashboard
  portfolio <week> [--top N] [--write]       Multi-product Phase 3B portfolio dashboard
EOF
}

# ── Guardrail used by action commands (dry-run/product/portfolio) ─────────────
check_action_guardrails() {
  [ "${ENABLE_AUTOPUBLISH:-false}" != "true" ] || fail "ENABLE_AUTOPUBLISH=true is not allowed"
  [ "${ENABLE_OPENAI_API_DIRECT:-false}" != "true" ] || fail "ENABLE_OPENAI_API_DIRECT=true is not allowed"
}

flag_state() {
  # Print the literal value of an env var, or "unset".
  local name="$1"
  if [ -n "${!name+x}" ]; then
    printf '%s' "${!name}"
  else
    printf 'unset'
  fi
}

count_glob() {
  # Count matching files without tripping nullglob/set -u edge cases.
  local pattern="$1"
  local -a matches=()
  shopt -s nullglob
  matches=($pattern)
  shopt -u nullglob
  printf '%s' "${#matches[@]}"
}

cmd_status() {
  echo "repo_root: $REPO_ROOT"
  echo "branch: $(git -C "$REPO_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || printf 'unknown')"
  echo "enable_autopublish: $(flag_state ENABLE_AUTOPUBLISH)"
  echo "enable_openai_api_direct: $(flag_state ENABLE_OPENAI_API_DIRECT)"
  echo "approve_promote: $(flag_state APPROVE_PROMOTE)"
  echo "approve_decision: $(flag_state APPROVE_DECISION)"
  echo "approve_finalize: $(flag_state APPROVE_FINALIZE)"
  echo "phase2e_score_files: $(count_glob "$REPO_ROOT/tmp/phase2e-import-score-report/scores/*.json")"
  echo "phase2f_hermes_summaries: $(count_glob "$REPO_ROOT/tmp/phase2f-hermes/*.md")"
  echo "phase2j_governance_summaries: $(count_glob "$REPO_ROOT/tmp/phase2j-hermes-governance/*.md")"
  echo "phase3a_dashboards: $(count_glob "$REPO_ROOT/tmp/phase3a-dashboard/*.md")"
  echo "phase3b_portfolios: $(count_glob "$REPO_ROOT/tmp/phase3b-portfolio-dashboard/*.md")"
  echo "status_command: success"
}

cmd_doctor() {
  local failures=0

  check_file_exec() {
    local label="$1" path="$2"
    if [ -x "$path" ]; then
      echo "check: $label -> PASS"
    else
      echo "check: $label -> FAIL"
      failures=$((failures + 1))
    fi
  }

  check_file_exists() {
    local label="$1" path="$2"
    if [ -f "$path" ]; then
      echo "check: $label -> PASS"
    else
      echo "check: $label -> FAIL"
      failures=$((failures + 1))
    fi
  }

  check_flag_safe() {
    local name="$1"
    if [ "$(flag_state "$name")" = "true" ]; then
      echo "check: $name safe -> FAIL"
      failures=$((failures + 1))
    else
      echo "check: $name safe -> PASS"
    fi
  }

  check_file_exec "run_phase2_full_dry_run.sh" "$DRY_RUN_WRAPPER"
  check_file_exec "run_phase3a_dashboard_summary.sh" "$PRODUCT_WRAPPER"
  check_file_exec "run_phase3b_portfolio_dashboard.sh" "$PORTFOLIO_WRAPPER"
  check_file_exists "dashboard_summary.py" "$REPO_ROOT/scripts/dev/dashboard_summary.py"
  check_file_exists "portfolio_dashboard.py" "$REPO_ROOT/scripts/dev/portfolio_dashboard.py"
  check_flag_safe "ENABLE_AUTOPUBLISH"
  check_flag_safe "ENABLE_OPENAI_API_DIRECT"
  check_flag_safe "APPROVE_PROMOTE"
  check_flag_safe "APPROVE_DECISION"
  check_flag_safe "APPROVE_FINALIZE"

  if [ "$failures" -ne 0 ]; then
    echo "doctor_status: failed"
    exit 1
  fi
  echo "doctor_status: success"
}

cmd_dry_run() {
  [ "$#" -eq 3 ] || fail "Usage: command_center.sh dry-run <csv_path> <week> <product_id>"
  local csv_path="$1" week="$2" product_id="$3"
  [ -f "$csv_path" ] || fail "csv_path does not exist or is not a file: $csv_path"
  printf '%s' "$week" | grep -Eq "$WEEK_RE" || fail "week must match $WEEK_RE, got: $week"
  printf '%s' "$product_id" | grep -Eq "$PRODUCT_ID_RE" || fail "product_id must match $PRODUCT_ID_RE, got: $product_id"
  [ -x "$DRY_RUN_WRAPPER" ] || fail "Missing or non-executable wrapper: $DRY_RUN_WRAPPER"
  exec bash "$DRY_RUN_WRAPPER" "$csv_path" "$week" "$product_id"
}

cmd_product() {
  [ "$#" -ge 2 ] || fail "Usage: command_center.sh product <product_id> <week> [--write]"
  local product_id="$1" week="$2"
  shift 2
  local -a passthrough=()
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --write) passthrough+=(--write); shift ;;
      *) fail "Unknown flag for product: $1" ;;
    esac
  done
  printf '%s' "$product_id" | grep -Eq "$PRODUCT_ID_RE" || fail "product_id must match $PRODUCT_ID_RE, got: $product_id"
  printf '%s' "$week" | grep -Eq "$WEEK_RE" || fail "week must match $WEEK_RE, got: $week"
  [ -x "$PRODUCT_WRAPPER" ] || fail "Missing or non-executable wrapper: $PRODUCT_WRAPPER"
  exec bash "$PRODUCT_WRAPPER" "$product_id" "$week" ${passthrough[@]+"${passthrough[@]}"}
}

cmd_portfolio() {
  [ "$#" -ge 1 ] || fail "Usage: command_center.sh portfolio <week> [--top N] [--write]"
  local week="$1"
  shift
  local -a passthrough=()
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --top)
        shift
        [ "$#" -ge 1 ] || fail "--top requires a value"
        passthrough+=(--top "$1")
        shift
        ;;
      --write) passthrough+=(--write); shift ;;
      *) fail "Unknown flag for portfolio: $1" ;;
    esac
  done
  printf '%s' "$week" | grep -Eq "$WEEK_RE" || fail "week must match $WEEK_RE, got: $week"
  [ -x "$PORTFOLIO_WRAPPER" ] || fail "Missing or non-executable wrapper: $PORTFOLIO_WRAPPER"
  exec bash "$PORTFOLIO_WRAPPER" "$week" ${passthrough[@]+"${passthrough[@]}"}
}

main() {
  local command="${1:-help}"
  case "$command" in
    help|-h|--help)
      usage
      ;;
    status)
      cmd_status
      ;;
    doctor)
      cmd_doctor
      ;;
    dry-run)
      shift
      check_action_guardrails
      cmd_dry_run "$@"
      ;;
    product)
      shift
      check_action_guardrails
      cmd_product "$@"
      ;;
    portfolio)
      shift
      check_action_guardrails
      cmd_portfolio "$@"
      ;;
    *)
      echo "Unknown command: $command" >&2
      usage >&2
      exit 1
      ;;
  esac
}

main "$@"
