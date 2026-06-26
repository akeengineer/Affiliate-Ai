#!/usr/bin/env bash
set -euo pipefail

EXPECTED_REPO_ROOT="/home/ubuntu/Affiliate-Ai"
EXPECTED_REMOTE="git@github.com:akeengineer/Affiliate-Ai.git"
SMOKE_SCRIPT="scripts/dev/run_phase1_smoke.sh"

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

current_dir="$(pwd -P)"
[ "$current_dir" = "$EXPECTED_REPO_ROOT" ] || fail "Must run from $EXPECTED_REPO_ROOT"

remote_url="$(git remote get-url origin 2>/dev/null || true)"
[ -n "$remote_url" ] || fail "Missing git remote: origin"

case "$remote_url" in
  "$EXPECTED_REMOTE"|git@*:akeengineer/Affiliate-Ai.git)
    ;;
  *)
    fail "Unexpected git remote: $remote_url"
    ;;
esac

skills_output="$(sudo hermes skills list)"
require_skill "$skills_output" "affiliate-growth-os"
require_skill "$skills_output" "obsidian"
require_skill "$skills_output" "codex"

[ -f "$SMOKE_SCRIPT" ] || fail "Missing smoke script: $SMOKE_SCRIPT"
[ -x "$SMOKE_SCRIPT" ] || fail "Smoke script is not executable: $SMOKE_SCRIPT"

[ "${ENABLE_AUTOPUBLISH:-false}" != "true" ] || fail "ENABLE_AUTOPUBLISH must not be true"

echo "repo_root: $current_dir"
echo "git_remote: $remote_url"
echo "smoke_script: $SMOKE_SCRIPT"
echo "autopublish: ${ENABLE_AUTOPUBLISH:-unset}"
echo "phase2b_runtime_check: success"
