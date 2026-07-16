# Orchestration System — 9ake-kiro-agents

## Overview

Kiro acts as the Orchestrator, dispatching coding tasks to two CLI agents:

- **Claude-CLI Agent** — Handles reasoning, design, and code review tasks
- **Codex-CLI Agent** — Handles implementation, testing, and refactoring tasks

Both agents run in the terminal (locally or on EC2 via SSH) and return structured JSON results.

## Architecture

```
Kiro (Orchestrator)
  |
  |-- orchestrate.py (CLI)
  |       |
  |       |-- create_task.py (enqueue)
  |       |-- dispatcher.py (select agent, build CLI command, execute)
  |       |-- collector.py (parse output, validate, save results)
  |       |-- retry.py (retry + fallback)
  |       |-- ssh_bridge.py (remote execution)
  |       |-- reporter.py (generate reports)
  |
  |-- .agents/ (per-project config + runtime)
```

## Quick Start

```bash
# Run the demo (mocked agents)
python scripts/agents/demo.py

# Create a task
python scripts/agents/orchestrate.py create \
  --title "Implement scoring script" \
  --type implementation \
  --prompt "Create scripts/dev/score_product.py following docs/SCORING_SPEC.md"

# Show what would be dispatched
python scripts/agents/orchestrate.py dispatch --dry-run

# Dispatch all queued tasks
python scripts/agents/orchestrate.py dispatch

# Check status
python scripts/agents/orchestrate.py status

# View results
python scripts/agents/orchestrate.py results

# Generate report
python scripts/agents/orchestrate.py report

# Full pipeline (create + dispatch + report)
python scripts/agents/orchestrate.py run "implement scoring script"
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `init` | Initialize `.agents/` in a new project |
| `create` | Create and enqueue a task |
| `dispatch` | Dispatch queued tasks to agents |
| `dispatch --dry-run` | Show plan without executing |
| `status` | Show queue and execution state |
| `results` | Show collected results |
| `report` | Generate Markdown + JSON report |
| `run "desc"` | Full E2E pipeline for a single task |
| `remote-status` | Check EC2 agent availability via SSH |

## Agent Selection

Tasks are routed based on their `type`:

| Task Type | Agent | Reasoning |
|-----------|-------|-----------|
| `reasoning` | Claude | Deep thinking, analysis |
| `design` | Claude | Architecture, interfaces |
| `review` | Claude | Code review, quality |
| `implementation` | Codex | Write production code |
| `test` | Codex | Create test suites |
| `refactor` | Codex | Restructure code |

Override with `--agent claude` or `--agent codex` when creating a task.

## Retry and Fallback

1. If an agent fails, retry up to `retry_max` times (default: 2) with exponential backoff
2. If all retries fail and `fallback_enabled` is true, try the other agent
3. Fallback gets one attempt with context about the previous failure
4. All attempts are logged in `.agents/state/retries/`

## Parallel vs Sequential

- Independent tasks (no dependencies) run in parallel (up to `parallel_max`)
- Dependent tasks (specified via `--depends-on`) run after their prerequisites complete
- Priority ordering within parallel groups: critical > high > medium > low

## Remote Execution (SSH)

Configure in `.agents/config.yaml`:

```yaml
ssh:
  host: "god-of-ai"
  project_path: "/home/ubuntu/Affiliate-Ai"
  user: "ubuntu"
```

Then: `python scripts/agents/orchestrate.py remote-status`

## Configuration

All settings live in `.agents/config.yaml`. Key sections:

- `agents` — CLI commands, flags, system prompts, task types per agent
- `dispatch` — Retry limits, backoff, fallback, parallelism
- `ssh` — Remote host for EC2 execution
- `validation` — Test runner, file existence checks
- `paths` — Directory layout

## Adding to a New Project

```bash
cd /path/to/new-project
python /path/to/orchestrate.py init --project-name "My Project"
```

This creates `.agents/` with default config and template prompts. Customize as needed.

## Future: Standalone Package

When proven, `scripts/agents/core/` will be extracted to `9ake-kiro-agents`:

```bash
pip install git+https://github.com/akeengineer/9ake-kiro-agents.git
9ake-kiro-agents init
```

## Running Tests

```bash
python -m pytest tests/agents/ -v
```

189 tests cover all components including integration E2E flows.
