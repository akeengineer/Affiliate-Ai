# .agents/ — Multi-Agent Orchestration Directory

## Overview

This directory contains the configuration and runtime state for the **9ake-kiro-agents** orchestration system. Kiro acts as the Orchestrator, dispatching tasks to Claude-CLI and Codex-CLI agents.

## Structure

```
.agents/
├── README.md          # (git-tracked) This file
├── config.yaml        # (git-tracked) Project-specific agent settings
├── prompts/           # (git-tracked) Agent system prompts
│   ├── claude-cli-agent.md
│   ├── codex-cli-agent.md
│   └── shared-context.md
├── schemas/           # (git-tracked) JSON schemas for validation
│   ├── task.schema.json
│   └── result.schema.json
├── queue/             # (gitignored) Pending task files
├── results/           # (gitignored) Agent output/results
├── state/             # (gitignored) Runtime state (active tasks, agent status)
└── reports/           # (gitignored) Generated reports
```

## Tracked vs Gitignored

| Directory    | Tracked | Purpose                          |
|-------------|---------|----------------------------------|
| `prompts/`  | Yes     | Agent system prompts             |
| `schemas/`  | Yes     | JSON schemas for task/result     |
| `config.yaml` | Yes  | Project settings                 |
| `queue/`    | No      | Runtime task queue               |
| `results/`  | No      | Agent execution results          |
| `state/`    | No      | Active task/agent state          |
| `reports/`  | No      | Generated orchestration reports  |

## Usage

```bash
# Initialize in a new project (future)
9ake-kiro-agents init

# Create a task
python scripts/agents/create_task.py --title "..." --type implementation

# Dispatch queued tasks
python scripts/agents/orchestrate.py dispatch

# Full E2E pipeline
python scripts/agents/orchestrate.py run "description"

# Check status
python scripts/agents/orchestrate.py status
```

## Portability

This system is designed to be extracted into a standalone package (`9ake-kiro-agents`) once proven. The engine lives in `scripts/agents/core/` and is project-agnostic. Per-project config lives here in `.agents/`.
