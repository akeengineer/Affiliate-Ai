# Task 004 — Multi-Agent Orchestration System (9ake-kiro-agents)

## Task ID

004-multi-agent-orchestration

## Objective

Build a multi-agent orchestration system where Kiro acts as Orchestrator, dispatching coding tasks to Claude-CLI and Codex-CLI agents running in the terminal. The system supports parallel/sequential execution, retry with fallback, and remote execution via SSH.

## Status

Completed.

## Implementation Summary

### Engine (scripts/agents/core/) — Reusable

| Module | Purpose |
|--------|---------|
| `models/config.py` | Config loader with auto-discovery |
| `models/task.py` | Task dataclass with state machine |
| `models/result.py` | AgentResult dataclass |
| `dispatcher.py` | Task-to-agent mapping, CLI command building, parallel/sequential dispatch |
| `collector.py` | Result parsing (JSON extraction), validation, persistence |
| `retry.py` | Retry with backoff + cross-agent fallback |
| `ssh_bridge.py` | SSH/SCP remote execution bridge |
| `reporter.py` | Markdown + JSON report generation |

### CLI (scripts/agents/) — Entry Points

| Script | Purpose |
|--------|---------|
| `orchestrate.py` | Main CLI (init, create, dispatch, status, results, report, run, remote-status) |
| `create_task.py` | Task creation utility (CLI args, JSON file, stdin) |
| `demo.py` | Runnable demo with mocked agents |

### Config (.agents/) — Per-Project

| Path | Tracked | Purpose |
|------|---------|---------|
| `config.yaml` | Yes | Agent settings, dispatch rules, SSH, validation |
| `prompts/` | Yes | System prompts for Claude and Codex |
| `schemas/` | Yes | JSON schemas for task/result validation |
| `queue/` | No | Runtime task queue |
| `results/` | No | Agent execution results |
| `state/` | No | Active task state + retry logs |
| `reports/` | No | Generated reports |

## Tests

189 tests total (all passing):
- `test_config.py` — 22 tests
- `test_models.py` — 17 tests
- `test_create_task.py` — 18 tests
- `test_dispatcher.py` — 30 tests
- `test_collector.py` — 21 tests
- `test_retry.py` — 14 tests
- `test_ssh_bridge.py` — 26 tests
- `test_orchestrate.py` — 15 tests
- `test_reporter.py` — 21 tests
- `integration/test_e2e_pipeline.py` — 5 tests

## Portability

Designed for future extraction to standalone package `9ake-kiro-agents`:
1. Engine in `scripts/agents/core/` is project-agnostic
2. `orchestrate init` scaffolds `.agents/` in any new project
3. Per-project config in `.agents/config.yaml`

## Security Constraints

- No secrets in config or prompts
- No private Obsidian data committed
- SSH keys not stored in repo
- Full-auto agent permissions validated by Kiro post-execution
