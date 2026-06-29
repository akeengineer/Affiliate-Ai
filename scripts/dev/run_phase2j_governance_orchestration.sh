#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

TASK_FILE="$REPO_ROOT/codex/tasks/013-phase2j-hermes-governance-orchestration.md"
PROMPT_FILE="$REPO_ROOT/prompts/workflows/hermes-phase2j-governance-orchestration.md"
OUTPUT_DIR="$REPO_ROOT/tmp/phase2j-hermes-governance"

PHASE2E_SCRIPT="$REPO_ROOT/scripts/dev/run_phase2e_import_score_report.sh"
PROMOTE_SCRIPT="$REPO_ROOT/scripts/dev/promote_product_candidates.py"
CREATE_DECISION_SCRIPT="$REPO_ROOT/scripts/dev/create_decision.py"
FINALIZE_DECISION_SCRIPT="$REPO_ROOT/scripts/dev/finalize_decision.py"
PHASE2G_WRAPPER="$REPO_ROOT/scripts/dev/run_phase2g_approval_promote.sh"
PHASE2H_WRAPPER="$REPO_ROOT/scripts/dev/run_phase2h_decision_review.sh"
PHASE2I_WRAPPER="$REPO_ROOT/scripts/dev/run_phase2i_decision_finalization.sh"

PHASE2E_ROOT_REL="tmp/phase2e-import-score-report"

PRIVATE_VAULT_PATHS=(
  "vault/products"
  "vault/trends"
  "vault/marketplace-signals"
  "vault/commissions"
  "vault/meetings"
  "vault/decisions"
  "vault/contents"
  "vault/compliance"
  "vault/reports"
  "vault/.obsidian"
)

if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  PYTHON_BIN="$(command -v python)"
fi

fail() {
  echo "$1" >&2
  exit 1
}

if [ "$#" -ne 3 ]; then
  echo "Usage: bash scripts/dev/run_phase2j_governance_orchestration.sh <input-csv> <report-week> <product-id>" >&2
  exit 1
fi

INPUT_CSV="$1"
REPORT_WEEK="$2"
PRODUCT_ID="$3"
SUMMARY_PATH="$OUTPUT_DIR/governance-summary-$REPORT_WEEK.md"

# ── Guardrails (before any output is created) ────────────────────────────────
[ "${ENABLE_AUTOPUBLISH:-false}" != "true" ] || fail "ENABLE_AUTOPUBLISH=true is not allowed"
[ "${ENABLE_OPENAI_API_DIRECT:-false}" != "true" ] || fail "ENABLE_OPENAI_API_DIRECT=true is not allowed"

printf '%s' "$PRODUCT_ID" | grep -Eq '^[a-z0-9-]+$' \
  || fail "product-id must match ^[a-z0-9-]+\$, got: $PRODUCT_ID"

# ── Verify governance chain scripts + wrappers exist ─────────────────────────
[ -f "$TASK_FILE" ] || fail "Missing task file: $TASK_FILE"
[ -f "$PROMPT_FILE" ] || fail "Missing prompt file: $PROMPT_FILE"

[ -x "$PHASE2E_SCRIPT" ] || fail "Missing or non-executable Phase 2E script: $PHASE2E_SCRIPT"
[ -f "$PROMOTE_SCRIPT" ] || fail "Missing Phase 2G promote script: $PROMOTE_SCRIPT"
[ -f "$CREATE_DECISION_SCRIPT" ] || fail "Missing Phase 2H decision script: $CREATE_DECISION_SCRIPT"
[ -f "$FINALIZE_DECISION_SCRIPT" ] || fail "Missing Phase 2I finalize script: $FINALIZE_DECISION_SCRIPT"

[ -x "$PHASE2G_WRAPPER" ] || fail "Missing or non-executable Phase 2G wrapper: $PHASE2G_WRAPPER"
[ -x "$PHASE2H_WRAPPER" ] || fail "Missing or non-executable Phase 2H wrapper: $PHASE2H_WRAPPER"
[ -x "$PHASE2I_WRAPPER" ] || fail "Missing or non-executable Phase 2I wrapper: $PHASE2I_WRAPPER"

# ── Phase 2E: live, tmp-only ─────────────────────────────────────────────────
phase2e_output="$(bash "$PHASE2E_SCRIPT" "$INPUT_CSV" "$REPORT_WEEK")"
printf '%s\n' "$phase2e_output" | grep -q '^final_status: success' \
  || fail "Phase 2E did not report final_status: success"

SCORE_JSON="$REPO_ROOT/$PHASE2E_ROOT_REL/scores/$PRODUCT_ID.json"
[ -f "$SCORE_JSON" ] \
  || fail "No scored JSON for product-id '$PRODUCT_ID' (expected $PHASE2E_ROOT_REL/scores/$PRODUCT_ID.json)"

SCORE_DECISION="$("$PYTHON_BIN" -c "import json,sys; print(json.load(open(sys.argv[1]))['score_decision'])" "$SCORE_JSON")"

# ── Phase 2G: dry-run via wrapper (no APPROVE_PROMOTE) — no vault write ───────
phase2g_output="$(bash "$PHASE2G_WRAPPER" "$PHASE2E_ROOT_REL" "$REPORT_WEEK")"
printf '%s\n' "$phase2g_output" | grep -q '^phase2g_status: dry_run_complete' \
  || fail "Phase 2G dry-run did not report phase2g_status: dry_run_complete"

# ── Phase 2H / 2I: statically verified above; not executed ───────────────────
PROMOTED_STATUS="dry_run_not_promoted"
DECISION_STATUS="not_executed"
FINALIZATION_STATUS="not_executed"
COMPLIANCE_GATE_STATUS="not_evaluated"
NEXT_ALLOWED_ACTION="Promote candidate via Phase 2G (APPROVE_PROMOTE=true) — manual operator step"

mkdir -p "$OUTPUT_DIR"
created_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

cat >"$SUMMARY_PATH" <<EOF
---
type: hermes_governance_summary
report_week: $REPORT_WEEK
mode: dry_run
product_id: $PRODUCT_ID
score_decision: $SCORE_DECISION
promoted_status: $PROMOTED_STATUS
decision_status: $DECISION_STATUS
finalization_status: $FINALIZATION_STATUS
compliance_gate_status: $COMPLIANCE_GATE_STATUS
next_allowed_action: "$NEXT_ALLOWED_ACTION"
created_at: $created_at
status: complete
---

# Hermes Governance Summary — $REPORT_WEEK

## Guardrails verified

- ENABLE_AUTOPUBLISH: false
- ENABLE_OPENAI_API_DIRECT: not enabled
- mode: dry_run

## Governance chain status

- product_id: $PRODUCT_ID
- score_decision: $SCORE_DECISION
- promoted_status: $PROMOTED_STATUS
- decision_status: $DECISION_STATUS (requires approved promote via Phase 2G)
- finalization_status: $FINALIZATION_STATUS (requires draft decision via Phase 2H)
- compliance_gate_status: $COMPLIANCE_GATE_STATUS (no decision created in dry-run)

## Chain verification

- Phase 2E: executed (tmp-only) — success
- Phase 2G: executed (dry-run) — no vault write
- Phase 2H: script + wrapper verified — not executed
- Phase 2I: script + wrapper verified — not executed

## Blocked risks

- Promotion requires explicit APPROVE_PROMOTE=true (manual gate).
- Decision requires compliance_status=approved before finalization.
- Each stage is human-gated by design; dry-run intentionally halts before vault writes.

## Next allowed action

- $NEXT_ALLOWED_ACTION

## Status

phase2j_status: success
EOF

# ── Validate summary frontmatter ─────────────────────────────────────────────
if ! awk '
BEGIN { seen_type = 0; closed = 0 }
NR == 1 { if ($0 != "---") exit 1; next }
$0 == "type: hermes_governance_summary" { seen_type = 1 }
$0 == "---" { closed = 1; exit(seen_type ? 0 : 1) }
END { if (!closed) exit 1 }
' "$SUMMARY_PATH"; then
  fail "Governance summary validation failed: missing frontmatter type: hermes_governance_summary"
fi

# ── Scrub private vault paths ────────────────────────────────────────────────
for private_path in "${PRIVATE_VAULT_PATHS[@]}"; do
  if grep -qF "$private_path" "$SUMMARY_PATH"; then
    fail "Summary references private vault path: $private_path"
  fi
done

echo "product_id: $PRODUCT_ID"
echo "score_decision: $SCORE_DECISION"
echo "promoted_status: $PROMOTED_STATUS"
echo "decision_status: $DECISION_STATUS"
echo "finalization_status: $FINALIZATION_STATUS"
echo "compliance_gate_status: $COMPLIANCE_GATE_STATUS"
echo "summary_path: $SUMMARY_PATH"
echo "phase2j_status: success"
