#!/usr/bin/env bash
set -euo pipefail

SESSION="affiliate-warroom"
PROJECT_DIR="${PROJECT_DIR:-$PWD}"

if tmux has-session -t "$SESSION" 2>/dev/null; then
  tmux attach-session -t "$SESSION"
  exit 0
fi

tmux new-session -d -s "$SESSION" -c "$PROJECT_DIR" -n command-center

tmux send-keys -t "$SESSION:command-center.0" 'echo "Hermes Orchestrator"' C-m

tmux split-window -h -t "$SESSION:command-center" -c "$PROJECT_DIR"
tmux send-keys -t "$SESSION:command-center.1" 'echo "Codex Builder"' C-m

tmux split-window -v -t "$SESSION:command-center.0" -c "$PROJECT_DIR"
tmux send-keys -t "$SESSION:command-center.2" 'echo "Product Miner Agent"' C-m

tmux split-window -v -t "$SESSION:command-center.1" -c "$PROJECT_DIR"
tmux send-keys -t "$SESSION:command-center.3" 'echo "Demand Intelligence Agent"' C-m

tmux split-window -v -t "$SESSION:command-center.2" -c "$PROJECT_DIR"
tmux send-keys -t "$SESSION:command-center.4" 'echo "Commission Economics Agent"' C-m

tmux split-window -v -t "$SESSION:command-center.3" -c "$PROJECT_DIR"
tmux send-keys -t "$SESSION:command-center.5" 'echo "Compliance Risk Agent"' C-m

tmux select-layout -t "$SESSION:command-center" tiled
tmux attach-session -t "$SESSION"
