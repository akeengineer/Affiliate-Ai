#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TASK_FILE="$REPO_ROOT/codex/tasks/008-phase2e-import-score-report.md"
OUTPUT_ROOT="$REPO_ROOT/tmp/phase2e-import-score-report"
PRODUCTS_DIR="$OUTPUT_ROOT/products"
SCORES_DIR="$OUTPUT_ROOT/scores"
IMPORT_SCRIPT="$REPO_ROOT/scripts/dev/import_product_candidates.py"
SCORE_SCRIPT="$REPO_ROOT/scripts/dev/score_product.py"
REPORT_SCRIPT="$REPO_ROOT/scripts/dev/generate_weekly_report.py"

if [ "$#" -ne 2 ]; then
  echo "Usage: bash scripts/dev/run_phase2e_import_score_report.sh <input-csv> <report-week>" >&2
  exit 1
fi

if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  PYTHON_BIN="$(command -v python)"
fi

INPUT_CSV="$1"
REPORT_WEEK="$2"
REPORT_PATH="$OUTPUT_ROOT/weekly-report-$REPORT_WEEK.md"

if [ ! -f "$TASK_FILE" ]; then
  echo "Missing task file: $TASK_FILE" >&2
  exit 1
fi

if [ "${ENABLE_AUTOPUBLISH:-false}" = "true" ]; then
  echo "ENABLE_AUTOPUBLISH=true is not allowed" >&2
  exit 1
fi

rm -rf "$OUTPUT_ROOT"
mkdir -p "$PRODUCTS_DIR" "$SCORES_DIR"

"$PYTHON_BIN" "$IMPORT_SCRIPT" \
  --input-csv "$INPUT_CSV" \
  --output-dir "$PRODUCTS_DIR" \
  >/dev/null

shopt -s nullglob
product_notes=("$PRODUCTS_DIR"/*.md)
shopt -u nullglob

if [ "${#product_notes[@]}" -eq 0 ]; then
  echo "No imported product notes found in $PRODUCTS_DIR" >&2
  exit 1
fi

score_json_files=0
for note_path in "${product_notes[@]}"; do
  note_name="$(basename "$note_path" .md)"
  "$PYTHON_BIN" "$SCORE_SCRIPT" "$note_path" >"$SCORES_DIR/$note_name.json"
  score_json_files=$((score_json_files + 1))
done

if [ "$score_json_files" -ne "${#product_notes[@]}" ]; then
  echo "Score JSON count mismatch: imported=${#product_notes[@]} scored=$score_json_files" >&2
  exit 1
fi

"$PYTHON_BIN" "$REPORT_SCRIPT" \
  --input-dir "$OUTPUT_ROOT" \
  --report-week "$REPORT_WEEK" \
  --output "$REPORT_PATH"

if ! awk '
BEGIN { seen_type = 0; closed = 0 }
NR == 1 {
  if ($0 != "---") exit 1
  next
}
$0 == "type: weekly_report" { seen_type = 1 }
$0 == "---" {
  closed = 1
  exit(seen_type ? 0 : 1)
}
END {
  if (!closed) exit 1
}
' "$REPORT_PATH"; then
  echo "Weekly report validation failed: missing frontmatter type: weekly_report" >&2
  exit 1
fi

echo "imported_products: ${#product_notes[@]}"
echo "score_json_files: $score_json_files"
echo "report_path: $REPORT_PATH"
echo "final_status: success"
