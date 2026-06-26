# Task 005 — Phase 2B Hermes Operational Test

## Objective
Prove Hermes can operate Affiliate Product Intelligence OS safely with local deterministic inputs, enabled Obsidian integration, and sanitized output only.

## Read first
- AGENTS.md
- CONTEXT.md
- AGENT.md
- docs/HERMES_OPERATING_RULES.md
- docs/OBSIDIAN_CONTRACT.md
- docs/WORKFLOW_SPEC.md
- docs/CODEX_IMPLEMENTATION_GUIDE.md
- scripts/dev/run_phase1_smoke.sh
- hermes/skills/affiliate-growth-os/SKILL.md

## Scope
Create:
- `codex/tasks/005-phase2b-hermes-operational-test.md`
- `prompts/workflows/hermes-phase2b-operational-test.md`
- `scripts/dev/check_hermes_runtime.sh`

Update:
- `.gitignore`

## Requirements
- `scripts/dev/check_hermes_runtime.sh` must verify:
  - running from `/home/ubuntu/Affiliate-Ai`
  - git remote is `git@github.com:akeengineer/Affiliate-Ai.git` or SSH alias equivalent for the same repo
  - `sudo hermes skills list` includes `affiliate-growth-os`, `obsidian`, and `codex`
  - `scripts/dev/run_phase1_smoke.sh` exists and is executable
  - `ENABLE_AUTOPUBLISH` is not `true`
- `prompts/workflows/hermes-phase2b-operational-test.md` must instruct Hermes to:
  - use `affiliate-growth-os`
  - read project source-of-truth files first
  - use Obsidian as backend/project memory
  - run or request `scripts/dev/run_phase1_smoke.sh`
  - write only sanitized summary output to `tmp/phase2b-hermes/hermes-operational-summary.md`
  - avoid private vault writes
  - avoid content generation
  - avoid external APIs
  - avoid Codex implementation requests
- `.gitignore` must ignore `tmp/phase2b-hermes/`

## Out of scope
- No database
- No FastAPI
- No UI
- No external APIs
- No content generation
- No autopublish
- No private vault writes
- No real affiliate links

## Acceptance criteria
- Runtime check script passes on the configured machine when Hermes runtime is ready.
- Prompt file gives Hermes a bounded operational dry run with sanitized output only.
- Output target is `tmp/phase2b-hermes/hermes-operational-summary.md`.

## Verification required
```bash
bash -n scripts/dev/check_hermes_runtime.sh
scripts/dev/check_hermes_runtime.sh
source .venv/bin/activate && python -m pytest -q
```
