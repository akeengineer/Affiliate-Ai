#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

SMOKE_SCRIPT="$REPO_ROOT/scripts/dev/run_phase1_smoke.sh"
REQUIRE_OPERATOR_RUNTIME="${AFFILIATE_REQUIRE_OPERATOR_RUNTIME:-false}"

fail() {
  echo "$1" >&2
  exit 1
}

require_skill() {
  local skills_output="$1"
  local skill_name="$2"

  if ! printf '%s\n' "$skills_output" | grep -q "$skill_name"; then
    fail "Missing Hermes skill: $skill_name"
  fi
}

# Portable repository identity check: accept any SSH or HTTPS remote that
# identifies akeengineer/Affiliate-Ai, with or without a .git suffix. This is
# not bound to one machine-specific remote alias.
remote_identifies_repo() {
  local url="$1"
  case "$url" in
    *akeengineer/Affiliate-Ai|*akeengineer/Affiliate-Ai.git)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

# Static contract checks run in every mode.
[ -d "$REPO_ROOT" ] || fail "Derived repo root is not a directory: $REPO_ROOT"
[ -f "$SMOKE_SCRIPT" ] || fail "Missing smoke script: $SMOKE_SCRIPT"
[ -x "$SMOKE_SCRIPT" ] || fail "Smoke script is not executable: $SMOKE_SCRIPT"

# Security guardrail: enforced in all modes before returning success.
[ "${ENABLE_AUTOPUBLISH:-false}" != "true" ] || fail "ENABLE_AUTOPUBLISH must not be true"

if [ "$REQUIRE_OPERATOR_RUNTIME" != "true" ]; then
  echo "repo_root: $REPO_ROOT"
  echo "smoke_script: $SMOKE_SCRIPT"
  echo "autopublish: ${ENABLE_AUTOPUBLISH:-unset}"
  echo "operator_runtime: skipped"
  echo "phase2b_runtime_check: ci-static"
  exit 0
fi

# Operator mode: enforce repository identity and live Hermes runtime checks.
remote_url="$(git remote get-url origin 2>/dev/null || true)"
[ -n "$remote_url" ] || fail "Missing git remote: origin"
remote_identifies_repo "$remote_url" || fail "Unexpected git remote: $remote_url"

skills_output="$(sudo hermes skills list)"
require_skill "$skills_output" "affiliate-growth-os"
require_skill "$skills_output" "obsidian"
require_skill "$skills_output" "codex"

echo "repo_root: $REPO_ROOT"
echo "git_remote: $remote_url"
echo "smoke_script: $SMOKE_SCRIPT"
echo "autopublish: ${ENABLE_AUTOPUBLISH:-unset}"
echo "operator_runtime: enforced"
echo "phase2b_runtime_check: success"
