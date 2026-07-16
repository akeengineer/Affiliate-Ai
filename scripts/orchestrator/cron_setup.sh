#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ACTIVATE_PATH="$REPO_ROOT/.venv/bin/activate"
CONFIG_PATH="$SCRIPT_DIR/config.yaml"
RUNNER_PATH="$SCRIPT_DIR/nightly_run.py"
MARKER="# affiliate-ai-nightly"

if [[ ! -f "$ACTIVATE_PATH" ]]; then
  echo "Virtual environment activation script not found: $ACTIVATE_PATH" >&2
  exit 1
fi

# Every command in this installer and in the installed cron job uses the repo venv.
source "$ACTIVATE_PATH"

if [[ "$(id -u)" -eq 0 ]]; then
  echo "Refusing to install the nightly job in root's crontab." >&2
  exit 1
fi

if [[ "$(id -un)" != "ubuntu" ]]; then
  echo "Run this installer as the ubuntu user, not $(id -un)." >&2
  exit 1
fi

mapfile -t CONFIG_VALUES < <(python - "$CONFIG_PATH" "$REPO_ROOT" <<'PY'
import sys
from pathlib import Path

import yaml

config = yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8")) or {}
schedule = config.get("cron_schedule")
if not isinstance(schedule, str) or not schedule.strip():
    raise SystemExit("cron_schedule is missing from orchestrator config")
paths = config.get("paths", config)
if not isinstance(paths, dict):
    raise SystemExit("orchestrator path configuration must be a mapping")
output_value = paths.get("output_dir")
if not isinstance(output_value, str) or not output_value.strip():
    raise SystemExit("output_dir is missing from orchestrator config")
output_dir = Path(output_value).expanduser()
if not output_dir.is_absolute():
    output_dir = Path(sys.argv[2]) / output_dir
print(schedule.strip())
print(output_dir.resolve())
PY
)
CRON_SCHEDULE="${CONFIG_VALUES[0]:-}"
OUTPUT_DIR="${CONFIG_VALUES[1]:-}"

if [[ "$CRON_SCHEDULE" != "0 2 * * *" ]]; then
  echo "Expected the required daily 02:00 schedule, got: $CRON_SCHEDULE" >&2
  exit 1
fi

if [[ -z "$OUTPUT_DIR" ]]; then
  echo "Unable to resolve output_dir from orchestrator config." >&2
  exit 1
fi
mkdir -p "$OUTPUT_DIR"

printf -v REPO_QUOTED '%q' "$REPO_ROOT"
printf -v ACTIVATE_QUOTED '%q' "$ACTIVATE_PATH"
printf -v RUNNER_QUOTED '%q' "$RUNNER_PATH"
printf -v CONFIG_QUOTED '%q' "$CONFIG_PATH"
printf -v LOG_QUOTED '%q' "$OUTPUT_DIR/cron.log"

CRON_COMMAND="cd $REPO_QUOTED && source $ACTIVATE_QUOTED && python $RUNNER_QUOTED --config $CONFIG_QUOTED >> $LOG_QUOTED 2>&1"
CRON_ENTRY="$CRON_SCHEDULE $CRON_COMMAND $MARKER"
TEMP_CRONTAB="$(mktemp)"
trap 'rm -f "$TEMP_CRONTAB"' EXIT

(crontab -l 2>/dev/null || true) | awk -v marker="$MARKER" 'index($0, marker) == 0' > "$TEMP_CRONTAB"
printf '%s\n' "$CRON_ENTRY" >> "$TEMP_CRONTAB"
crontab "$TEMP_CRONTAB"

echo "Installed ubuntu crontab entry: $CRON_ENTRY"
