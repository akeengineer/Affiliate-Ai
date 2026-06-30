#!/usr/bin/env bash
# Phase 5D UI Shell Demo Bundle Command.
#
# One safe operator command that runs the complete local static UI shell demo
# chain: Phase 4E demo bundle -> Phase 5B UI shell -> Phase 5C verifier -> Phase
# 5D summary writer. Orchestration only: no business logic, no backend, no vault
# writes, no external services, no approved-workflow triggering. The Phase 5C
# verifier is always run and never bypassed; the verdict-to-status decision is
# owned by build_ui_shell_demo_summary.py.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

P4E_WRAPPER="$REPO_ROOT/scripts/dev/run_phase4e_demo_bundle.sh"
P5B_WRAPPER="$REPO_ROOT/scripts/dev/run_phase5b_ui_shell.sh"
P5C_WRAPPER="$REPO_ROOT/scripts/dev/run_phase5c_ui_shell_verifier.sh"
WRITER="$REPO_ROOT/scripts/dev/build_ui_shell_demo_summary.py"
WEEK_RE='^[0-9]{4}-W[0-9]{2}$'

TMP_OUT=""
cleanup() { [ -z "$TMP_OUT" ] || rm -f "$TMP_OUT"; }
trap cleanup EXIT

fail() {
  echo "$1" >&2
  exit 1
}

if [ "$#" -ne 1 ]; then
  echo "Usage: bash scripts/dev/run_phase5d_ui_shell_demo.sh <week>" >&2
  exit 1
fi

WEEK="$1"

# ── Guardrails ───────────────────────────────────────────────────────────────
[ "${ENABLE_AUTOPUBLISH:-false}" != "true" ] || fail "ENABLE_AUTOPUBLISH=true is not allowed"
[ "${ENABLE_OPENAI_API_DIRECT:-false}" != "true" ] || fail "ENABLE_OPENAI_API_DIRECT=true is not allowed"
[ "${APPROVE_PROMOTE:-false}" != "true" ] || fail "APPROVE_PROMOTE=true is not allowed"
[ "${APPROVE_DECISION:-false}" != "true" ] || fail "APPROVE_DECISION=true is not allowed"
[ "${APPROVE_FINALIZE:-false}" != "true" ] || fail "APPROVE_FINALIZE=true is not allowed"

printf '%s' "$WEEK" | grep -Eq "$WEEK_RE" || fail "week must match $WEEK_RE, got: $WEEK"

for wrapper in "$P4E_WRAPPER" "$P5B_WRAPPER" "$P5C_WRAPPER"; do
  [ -x "$wrapper" ] || fail "Missing or non-executable wrapper: $wrapper"
done
[ -f "$WRITER" ] || fail "Missing summary writer: $WRITER"

# ── Select Python: .venv -> python3 -> python ────────────────────────────────
if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  PYTHON_BIN="$(command -v python)"
fi

TMP_OUT="$(mktemp)"

# ── Run a chain step; echo its step line; return PASS/FAIL via exit code ─────
redact() { sed 's#vault/[A-Za-z0-9._/-]*#[vault-path-redacted]#g' "$TMP_OUT" >&2; }

write_and_exit() {
  local p4e="$1" p5b="$2" p5c="$3"
  shift 3
  set +e
  "$PYTHON_BIN" "$WRITER" --week "$WEEK" \
    --phase4e "$p4e" --phase5b "$p5b" --phase5c "$p5c" "$@"
  local rc=$?
  set -e
  exit "$rc"
}

# ── Step 1: Phase 4E ─────────────────────────────────────────────────────────
if bash "$P4E_WRAPPER" "$WEEK" >"$TMP_OUT" 2>&1 && grep -q '^phase4e_status: success' "$TMP_OUT"; then
  echo "ui_shell_demo_step: phase4e -> PASS"
else
  echo "ui_shell_demo_step: phase4e -> FAIL"
  redact
  echo "ui_shell_demo_step: phase5b -> FAIL"
  echo "ui_shell_demo_step: phase5c -> FAIL"
  write_and_exit FAIL FAIL FAIL --verdict failed
fi

# ── Step 2: Phase 5B ─────────────────────────────────────────────────────────
if bash "$P5B_WRAPPER" "$WEEK" >"$TMP_OUT" 2>&1 && grep -q '^phase5b_status: success' "$TMP_OUT"; then
  echo "ui_shell_demo_step: phase5b -> PASS"
else
  echo "ui_shell_demo_step: phase5b -> FAIL"
  redact
  echo "ui_shell_demo_step: phase5c -> FAIL"
  write_and_exit PASS FAIL FAIL --verdict failed
fi

# ── Step 3: Phase 5C (always run; never bypassed) ────────────────────────────
set +e
bash "$P5C_WRAPPER" >"$TMP_OUT" 2>&1
p5c_rc=$?
set -e
if [ "$p5c_rc" -eq 0 ] && grep -q '^phase5c_status: success' "$TMP_OUT"; then
  echo "ui_shell_demo_step: phase5c -> PASS"
  # verdict (ready|warning) is read from the Phase 5C summary by the writer.
  write_and_exit PASS PASS PASS
else
  echo "ui_shell_demo_step: phase5c -> FAIL"
  redact
  write_and_exit PASS PASS FAIL --verdict failed
fi
