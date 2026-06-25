#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TASK_FILE="$REPO_ROOT/codex/tasks/004-phase2a-sample-workflow.md"
SAMPLE_ROOT="$REPO_ROOT/vault/samples"
SAMPLE_PRODUCTS_DIR="$SAMPLE_ROOT/products"
OUTPUT_ROOT="$REPO_ROOT/tmp/phase1-smoke"
SCORES_DIR="$OUTPUT_ROOT/scores"

if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  PYTHON_BIN="$(command -v python)"
fi

REPORT_WEEK="${1:-$(date -u +%G-W%V)}"
REPORT_PATH="$OUTPUT_ROOT/weekly-report-$REPORT_WEEK.md"

if [ ! -f "$TASK_FILE" ]; then
  echo "Missing task file: $TASK_FILE" >&2
  exit 1
fi

shopt -s nullglob
sample_notes=("$SAMPLE_PRODUCTS_DIR"/*.md)
shopt -u nullglob

if [ "${#sample_notes[@]}" -eq 0 ]; then
  echo "No sample product notes found in $SAMPLE_PRODUCTS_DIR" >&2
  exit 1
fi

rm -rf "$OUTPUT_ROOT"
mkdir -p "$SCORES_DIR"

scored_products=0
for note_path in "${sample_notes[@]}"; do
  note_name="$(basename "$note_path" .md)"
  "$PYTHON_BIN" "$REPO_ROOT/scripts/dev/score_product.py" "$note_path" >"$SCORES_DIR/$note_name.json"
  scored_products=$((scored_products + 1))
done

"$PYTHON_BIN" "$REPO_ROOT/scripts/dev/generate_weekly_report.py" \
  --input-dir "$SAMPLE_ROOT" \
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

if "$PYTHON_BIN" -m pytest -q; then
  pytest_status="passed"
  final_status="success"
else
  pytest_status="failed"
  final_status="failed"
fi

echo "scored_products: $scored_products"
echo "score_output_dir: $SCORES_DIR"
echo "weekly_report_path: $REPORT_PATH"
echo "pytest: $pytest_status"
echo "final_status: $final_status"

[ "$final_status" = "success" ]
