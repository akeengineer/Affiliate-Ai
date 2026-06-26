#!/usr/bin/env bash
set -euo pipefail

SESSION="${WARROOM_SESSION:-affiliate-warroom}"
PROJECT_DIR="${PROJECT_DIR:-/home/ubuntu/Affiliate-Ai}"
VAULT_DIR="${OBSIDIAN_VAULT_PATH:-$PROJECT_DIR/vault}"
WORKFLOW_PROMPT="${WARROOM_WORKFLOW_PROMPT:-$PROJECT_DIR/prompts/workflows/weekly-product-scan.md}"
TASK_FILE="${WARROOM_TASK_FILE:-$PROJECT_DIR/codex/tasks/001-bootstrap-scoring.md}"
OUTPUT_DISPLAY="${WARROOM_OUTPUT_DISPLAY:-vault/}"
READ_SCOPE="${WARROOM_READ_SCOPE:-vault/}"
PROOF_MODE="${WARROOM_PROOF_MODE:-false}"
PREPARE_VAULT_DIRS="${WARROOM_PREPARE_VAULT_DIRS:-true}"

fail() {
  echo "$1" >&2
  exit 1
}

repo_path() {
  local path="$1"
  case "$path" in
    "$PROJECT_DIR"/*) printf '%s\n' "${path#$PROJECT_DIR/}" ;;
    *) printf '%s\n' "$path" ;;
  esac
}

attach_or_print() {
  if [ -t 1 ]; then
    tmux attach-session -t "$SESSION"
  else
    echo "tmux attach -t $SESSION"
  fi
}

send_lines() {
  local target="$1"
  shift
  local line
  local command="printf '%s\n'"

  for line in "$@"; do
    command+=" $(printf '%q' "$line")"
  done

  tmux send-keys -t "$target" "$command" C-m
}

show_file() {
  local target="$1"
  local file_path="$2"

  tmux send-keys -t "$target" "sed -n '1,220p' $(printf '%q' "$file_path")" C-m
}

if [ "$PROOF_MODE" = "true" ]; then
  GUARDRAILS=(
    "read sanitized samples only"
    "write proof artifacts only to tmp/phase2c-warroom/"
    "do not call external APIs"
    "do not generate affiliate content"
    "do not touch private vault directories"
    "do not enable autopublish"
  )
else
  GUARDRAILS=(
    "use Obsidian-backed workflow inputs"
    "write workflow outputs to configured vault targets"
    "keep autopublish disabled"
  )
fi

render_pane() {
  local target="$1"
  local title="$2"
  local prompt_file="$3"
  shift 3
  local line

  tmux send-keys -t "$target" "clear" C-m
  send_lines "$target" "$title" "$@"
  send_lines "$target" "" "Guardrails:"

  for line in "${GUARDRAILS[@]}"; do
    send_lines "$target" "- $line"
  done

  send_lines "$target" ""
  show_file "$target" "$prompt_file"
}

[ -f "$WORKFLOW_PROMPT" ] || fail "Missing workflow prompt: $WORKFLOW_PROMPT"
[ -f "$TASK_FILE" ] || fail "Missing task file: $TASK_FILE"

for prompt_file in \
  "$PROJECT_DIR/prompts/agents/product-miner-agent.md" \
  "$PROJECT_DIR/prompts/agents/demand-intelligence-agent.md" \
  "$PROJECT_DIR/prompts/agents/commission-economics-agent.md" \
  "$PROJECT_DIR/prompts/agents/content-virality-agent.md" \
  "$PROJECT_DIR/prompts/agents/compliance-risk-agent.md" \
  "$PROJECT_DIR/prompts/agents/vote-chairman-agent.md"; do
  [ -f "$prompt_file" ] || fail "Missing agent prompt: $prompt_file"
done

if [ "$PREPARE_VAULT_DIRS" = "true" ]; then
  mkdir -p \
    "$VAULT_DIR/.obsidian" \
    "$VAULT_DIR/products" \
    "$VAULT_DIR/trends" \
    "$VAULT_DIR/marketplace-signals" \
    "$VAULT_DIR/commissions" \
    "$VAULT_DIR/meetings" \
    "$VAULT_DIR/decisions" \
    "$VAULT_DIR/contents" \
    "$VAULT_DIR/compliance" \
    "$VAULT_DIR/reports"
fi

if tmux has-session -t "$SESSION" 2>/dev/null; then
  attach_or_print
  exit 0
fi

tmux new-session -d -s "$SESSION" -c "$PROJECT_DIR" -n command-center
tmux set-environment -t "$SESSION" PROJECT_DIR "$PROJECT_DIR"
tmux set-environment -t "$SESSION" OBSIDIAN_VAULT_PATH "$VAULT_DIR"
tmux set-environment -t "$SESSION" ENABLE_AUTOPUBLISH false

tmux split-window -h -t "$SESSION:command-center" -c "$PROJECT_DIR"
tmux new-window -t "$SESSION" -n signals -c "$PROJECT_DIR"
tmux split-window -h -t "$SESSION:signals" -c "$PROJECT_DIR"
tmux split-window -v -t "$SESSION:signals.0" -c "$PROJECT_DIR"
tmux new-window -t "$SESSION" -n decisions -c "$PROJECT_DIR"
tmux split-window -h -t "$SESSION:decisions" -c "$PROJECT_DIR"
tmux split-window -v -t "$SESSION:decisions.0" -c "$PROJECT_DIR"

render_pane \
  "$SESSION:command-center.0" \
  "Hermes Orchestrator" \
  "$WORKFLOW_PROMPT" \
  "Project: $PROJECT_DIR" \
  "Vault: $VAULT_DIR" \
  "Workflow prompt: $(repo_path "$WORKFLOW_PROMPT")" \
  "Read scope: $READ_SCOPE" \
  "Write scope: $OUTPUT_DISPLAY"

render_pane \
  "$SESSION:command-center.1" \
  "Codex Builder" \
  "$TASK_FILE" \
  "Task: $(repo_path "$TASK_FILE")" \
  "Proof runner: scripts/dev/run_phase2c_warroom_proof.sh" \
  "Proof checker: scripts/dev/check_phase2c_warroom_outputs.sh" \
  "Write scope: $OUTPUT_DISPLAY"

render_pane \
  "$SESSION:signals.0" \
  "Product Miner Agent" \
  "$PROJECT_DIR/prompts/agents/product-miner-agent.md" \
  "Prompt: prompts/agents/product-miner-agent.md" \
  "Read scope: $READ_SCOPE" \
  "Write target: $OUTPUT_DISPLAY/votes/"

render_pane \
  "$SESSION:signals.1" \
  "Demand Intelligence Agent" \
  "$PROJECT_DIR/prompts/agents/demand-intelligence-agent.md" \
  "Prompt: prompts/agents/demand-intelligence-agent.md" \
  "Read scope: $READ_SCOPE" \
  "Write target: $OUTPUT_DISPLAY/votes/"

render_pane \
  "$SESSION:signals.2" \
  "Commission Economics Agent" \
  "$PROJECT_DIR/prompts/agents/commission-economics-agent.md" \
  "Prompt: prompts/agents/commission-economics-agent.md" \
  "Read scope: $READ_SCOPE" \
  "Write target: $OUTPUT_DISPLAY/votes/"

render_pane \
  "$SESSION:decisions.0" \
  "Content Virality Agent" \
  "$PROJECT_DIR/prompts/agents/content-virality-agent.md" \
  "Prompt: prompts/agents/content-virality-agent.md" \
  "Read scope: $READ_SCOPE" \
  "Write target: $OUTPUT_DISPLAY/votes/"

render_pane \
  "$SESSION:decisions.1" \
  "Compliance Risk Agent" \
  "$PROJECT_DIR/prompts/agents/compliance-risk-agent.md" \
  "Prompt: prompts/agents/compliance-risk-agent.md" \
  "Read scope: $READ_SCOPE" \
  "Write target: $OUTPUT_DISPLAY/votes/"

render_pane \
  "$SESSION:decisions.2" \
  "Vote Chairman Agent" \
  "$PROJECT_DIR/prompts/agents/vote-chairman-agent.md" \
  "Prompt: prompts/agents/vote-chairman-agent.md" \
  "Read scope: $READ_SCOPE" \
  "Write target: $OUTPUT_DISPLAY/decisions/"

tmux select-layout -t "$SESSION:command-center" even-horizontal
tmux select-layout -t "$SESSION:signals" tiled
tmux select-layout -t "$SESSION:decisions" tiled
tmux select-window -t "$SESSION:command-center"

attach_or_print
