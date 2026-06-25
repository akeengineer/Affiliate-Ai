#!/usr/bin/env bash
set -euo pipefail

SESSION="affiliate-warroom"
PROJECT_DIR="${PROJECT_DIR:-/home/ubuntu/Affiliate-Ai}"
VAULT_DIR="${OBSIDIAN_VAULT_PATH:-$PROJECT_DIR/vault}"
WORKFLOW_PROMPT="$PROJECT_DIR/prompts/workflows/weekly-product-scan.md"
TASK_FILE="$PROJECT_DIR/codex/tasks/001-bootstrap-scoring.md"

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

if tmux has-session -t "$SESSION" 2>/dev/null; then
  if [ -t 1 ]; then
    tmux attach-session -t "$SESSION"
  else
    echo "tmux session '$SESSION' already exists. Attach manually with: tmux attach -t $SESSION"
  fi
  exit 0
fi

tmux new-session -d -s "$SESSION" -c "$PROJECT_DIR" -n command-center
tmux set-environment -t "$SESSION" PROJECT_DIR "$PROJECT_DIR"
tmux set-environment -t "$SESSION" OBSIDIAN_VAULT_PATH "$VAULT_DIR"
tmux set-environment -t "$SESSION" ENABLE_AUTOPUBLISH false

tmux send-keys -t "$SESSION:command-center.0" "clear && printf 'Hermes Orchestrator\nProject: $PROJECT_DIR\nVault: $VAULT_DIR\nWorkflow prompt: $WORKFLOW_PROMPT\nOutput roots: products, meetings, decisions, reports\nAutopublish: disabled\n\n' && sed -n '1,200p' '$WORKFLOW_PROMPT'" C-m

tmux split-window -h -t "$SESSION:command-center" -c "$PROJECT_DIR"
tmux send-keys -t "$SESSION:command-center.1" "clear && printf 'Codex Builder\nTask: $TASK_FILE\nSample score command:\npython scripts/dev/score_product.py vault/samples/products/smart-desk-pad.md --pretty\nSample report command:\npython scripts/dev/generate_weekly_report.py --input-dir vault/samples --report-week 2026-W26\n\n' && sed -n '1,220p' '$TASK_FILE'" C-m

tmux select-layout -t "$SESSION:command-center" even-horizontal

tmux new-window -t "$SESSION" -n signals -c "$PROJECT_DIR"
tmux send-keys -t "$SESSION:signals.0" "clear && printf 'Product Miner Agent\nPrompt: prompts/agents/product-miner-agent.md\nWrite notes to: $VAULT_DIR/products/\n\n' && sed -n '1,220p' '$PROJECT_DIR/prompts/agents/product-miner-agent.md'" C-m

tmux split-window -h -t "$SESSION:signals" -c "$PROJECT_DIR"
tmux send-keys -t "$SESSION:signals.1" "clear && printf 'Demand Intelligence Agent\nPrompt: prompts/agents/demand-intelligence-agent.md\nWrite notes to: $VAULT_DIR/trends/\nUpdate fields: demand_score, trend_velocity_score, trend_signal_note\n\n' && sed -n '1,220p' '$PROJECT_DIR/prompts/agents/demand-intelligence-agent.md'" C-m

tmux split-window -v -t "$SESSION:signals.0" -c "$PROJECT_DIR"
tmux send-keys -t "$SESSION:signals.2" "clear && printf 'Commission Economics Agent\nPrompt: prompts/agents/commission-economics-agent.md\nWrite notes to: $VAULT_DIR/commissions/\nUpdate fields: commission_score, commission_signal_note\n\n' && sed -n '1,220p' '$PROJECT_DIR/prompts/agents/commission-economics-agent.md'" C-m

tmux select-layout -t "$SESSION:signals" tiled

tmux new-window -t "$SESSION" -n decisions -c "$PROJECT_DIR"
tmux send-keys -t "$SESSION:decisions.0" "clear && printf 'Content Virality Agent\nPrompt: prompts/agents/content-virality-agent.md\nUpdate note: $VAULT_DIR/products/\nUpdate fields: content_fit_score, competition_gap_score\n\n' && sed -n '1,220p' '$PROJECT_DIR/prompts/agents/content-virality-agent.md'" C-m

tmux split-window -h -t "$SESSION:decisions" -c "$PROJECT_DIR"
tmux send-keys -t "$SESSION:decisions.1" "clear && printf 'Compliance Risk Agent\nPrompt: prompts/agents/compliance-risk-agent.md\nWrite notes to: $VAULT_DIR/compliance/\nUpdate fields: risk_score, compliance_result_note\n\n' && sed -n '1,220p' '$PROJECT_DIR/prompts/agents/compliance-risk-agent.md'" C-m

tmux split-window -v -t "$SESSION:decisions.0" -c "$PROJECT_DIR"
tmux send-keys -t "$SESSION:decisions.2" "clear && printf 'Vote Chairman Agent\nPrompt: prompts/agents/vote-chairman-agent.md\nRead votes from: $VAULT_DIR/meetings/ or $PROJECT_DIR/vault/samples/votes/\nWrite decisions to: $VAULT_DIR/decisions/\nLaunch gate: score + 3 votes + compliance + decision\n\n' && sed -n '1,240p' '$PROJECT_DIR/prompts/agents/vote-chairman-agent.md'" C-m

tmux select-layout -t "$SESSION:decisions" tiled
tmux select-window -t "$SESSION:command-center"
if [ -t 1 ]; then
  tmux attach-session -t "$SESSION"
else
  echo "tmux session '$SESSION' created. Attach manually with: tmux attach -t $SESSION"
fi
