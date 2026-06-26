# Task 006 — Phase 2C Tmux Warroom Proof

## Objective

Prove the tmux warroom opens with the expected panes, task/prompt targets, and safe proof-only instructions while writing deterministic mock vote and decision artifacts to `tmp/phase2c-warroom/`.

## Read first

- `AGENTS.md`
- `AGENT.md`
- `CONTEXT.md`
- `docs/WORKFLOW_SPEC.md`
- `docs/OBSIDIAN_CONTRACT.md`
- `docs/HERMES_OPERATING_RULES.md`
- `docs/CODEX_IMPLEMENTATION_GUIDE.md`
- `prompts/agents/product-miner-agent.md`
- `prompts/agents/demand-intelligence-agent.md`
- `prompts/agents/commission-economics-agent.md`
- `prompts/agents/content-virality-agent.md`
- `prompts/agents/compliance-risk-agent.md`
- `prompts/agents/vote-chairman-agent.md`
- `scripts/tmux/start-affiliate-warroom.sh`
- `scripts/dev/run_phase1_smoke.sh`
- `scripts/dev/check_hermes_runtime.sh`

## Scope

Create:

- `codex/tasks/006-phase2c-warroom-proof.md`
- `prompts/workflows/phase2c-warroom-proof.md`
- `scripts/dev/run_phase2c_warroom_proof.sh`
- `scripts/dev/check_phase2c_warroom_outputs.sh`
- `tests/test_phase2c_warroom_proof.py`

Modify if needed:

- `scripts/tmux/start-affiliate-warroom.sh`
- `.gitignore`

## Requirements

- `run_phase2c_warroom_proof.sh` must fail fast if `ENABLE_AUTOPUBLISH=true`.
- The proof must clear and recreate `tmp/phase2c-warroom/`.
- The proof must read sanitized sample inputs from `vault/samples/` only.
- The proof must not read private vault directories.
- The proof must not write anywhere under `vault/`.
- The proof must write exactly five mock vote artifacts and one mock decision artifact.
- The proof must start a dedicated tmux session named `affiliate-warroom-phase2c`.
- The proof must not collide with the default `affiliate-warroom` session.
- The proof must print all generated artifact paths.
- The proof must exit `0` when artifacts and tmux setup succeed.

## Expected output files

- `tmp/phase2c-warroom/votes/vote-product-miner-smart-desk-pad.md`
- `tmp/phase2c-warroom/votes/vote-demand-intelligence-smart-desk-pad.md`
- `tmp/phase2c-warroom/votes/vote-commission-economics-smart-desk-pad.md`
- `tmp/phase2c-warroom/votes/vote-content-virality-smart-desk-pad.md`
- `tmp/phase2c-warroom/votes/vote-compliance-risk-smart-desk-pad.md`
- `tmp/phase2c-warroom/decisions/decision-smart-desk-pad.md`

## Hard constraints

- No database
- No FastAPI
- No UI
- No external APIs
- No affiliate content generation
- No autopublish
- No private vault writes
- No real affiliate links
- No live marketplace data
- No network calls
- No modification of runtime private Obsidian directories

## Verification

```bash
bash -n scripts/tmux/start-affiliate-warroom.sh
bash -n scripts/dev/run_phase2c_warroom_proof.sh
bash -n scripts/dev/check_phase2c_warroom_outputs.sh
bash scripts/dev/run_phase2c_warroom_proof.sh
bash scripts/dev/check_phase2c_warroom_outputs.sh
source .venv/bin/activate && python -m pytest -q tests/test_phase2c_warroom_proof.py
source .venv/bin/activate && python -m pytest -q tests/test_phase1_smoke.py tests/test_phase2b_hermes_runtime.py tests/test_phase2c_warroom_proof.py
source .venv/bin/activate && python -m pytest -q
```
