#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TASK_FILE="$REPO_ROOT/codex/tasks/009-phase2f-hermes-import-score-report.md"
PHASE2E_SCRIPT="$REPO_ROOT/scripts/dev/run_phase2e_import_score_report.sh"
OUTPUT_DIR="$REPO_ROOT/tmp/phase2f-hermes"

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

fail() {
  echo "$1" >&2
  exit 1
}

if [ "$#" -ne 2 ]; then
  echo "Usage: bash scripts/dev/run_phase2f_hermes_orchestration.sh <input-csv> <report-week>" >&2
  exit 1
fi

INPUT_CSV="$1"
REPORT_WEEK="$2"
SUMMARY_PATH="$OUTPUT_DIR/operational-summary-$REPORT_WEEK.md"
PHASE2E_REPORT_REL="tmp/phase2e-import-score-report/weekly-report-$REPORT_WEEK.md"

[ "${ENABLE_AUTOPUBLISH:-false}" != "true" ] || fail "ENABLE_AUTOPUBLISH=true is not allowed"
[ "${ENABLE_OPENAI_API_DIRECT:-false}" != "true" ] || fail "ENABLE_OPENAI_API_DIRECT=true is not allowed"

[ -f "$TASK_FILE" ] || fail "Missing task file: $TASK_FILE"
[ -f "$PHASE2E_SCRIPT" ] || fail "Missing Phase 2E script: $PHASE2E_SCRIPT"
[ -x "$PHASE2E_SCRIPT" ] || fail "Phase 2E script is not executable: $PHASE2E_SCRIPT"

phase2e_output="$(bash "$PHASE2E_SCRIPT" "$INPUT_CSV" "$REPORT_WEEK")"

imported_products="$(printf '%s\n' "$phase2e_output" | grep '^imported_products:' | awk '{print $2}')"
score_json_files="$(printf '%s\n' "$phase2e_output" | grep '^score_json_files:' | awk '{print $2}')"

mkdir -p "$OUTPUT_DIR"
created_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

cat >"$SUMMARY_PATH" <<EOF
---
type: hermes_operational_summary
report_week: $REPORT_WEEK
phase2e_status: success
imported_products: $imported_products
score_json_files: $score_json_files
phase2e_report: $PHASE2E_REPORT_REL
created_at: $created_at
status: complete
---

# Hermes Operational Summary — $REPORT_WEEK

## Guardrails verified

- ENABLE_AUTOPUBLISH: false
- ENABLE_OPENAI_API_DIRECT: not enabled

## Phase 2E execution

- Imported products: $imported_products
- Scored products: $score_json_files
- Report: $PHASE2E_REPORT_REL

## Status

phase2f_status: success
EOF

if ! awk '
BEGIN { seen_type = 0; closed = 0 }
NR == 1 { if ($0 != "---") exit 1; next }
$0 == "type: hermes_operational_summary" { seen_type = 1 }
$0 == "---" { closed = 1; exit(seen_type ? 0 : 1) }
END { if (!closed) exit 1 }
' "$SUMMARY_PATH"; then
  fail "Operational summary validation failed: missing frontmatter type: hermes_operational_summary"
fi

for private_path in "${PRIVATE_VAULT_PATHS[@]}"; do
  if grep -qF "$private_path" "$SUMMARY_PATH"; then
    fail "Summary references private vault path: $private_path"
  fi
done

printf '%s\n' "$phase2e_output"
echo "summary_path: $SUMMARY_PATH"
echo "phase2e_report_path: $REPO_ROOT/$PHASE2E_REPORT_REL"
echo "phase2f_status: success"
