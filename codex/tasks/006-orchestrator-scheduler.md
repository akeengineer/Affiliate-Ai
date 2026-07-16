# Codex Task: Orchestrator + Scheduler

## Task ID

006-orchestrator-scheduler

## Objective

Build the nightly orchestration pipeline and cron scheduler so the system runs fully unattended overnight, with state tracking and error recovery.

## Files to read first

- AGENTS.md
- CONTEXT.md
- docs/WORKFLOW_SPEC.md
- docs/plans/shopee-first-autonomous-system.md
- scripts/agents/agent_runner.py
- scripts/shopee/scraper.py

## Scope

- `scripts/orchestrator/nightly_run.py` — Full pipeline: scrape → analyze → score → vote → report
- `scripts/orchestrator/state.py` — Run state management (checkpoints, resume)
- `scripts/orchestrator/cron_setup.sh` — Crontab installation script
- `scripts/orchestrator/config.yaml` — Schedule config, retry limits, timeouts
- `tests/test_orchestrator.py` — Tests

## Out of scope

- Individual agent logic (Task 005)
- Scraper internals (Task 004)
- Notification delivery (Task 007)
- Shopee API (future)

## Acceptance criteria

- [ ] `python scripts/orchestrator/nightly_run.py` executes full pipeline end-to-end
- [ ] Pipeline stages: scrape → agent_analyze → score → vote → report (in order)
- [ ] Each stage writes checkpoint to state file
- [ ] `--resume` flag picks up from last successful checkpoint
- [ ] Error in one stage does not crash entire run; logs error and continues where safe
- [ ] Retry logic: 3 attempts per stage with exponential backoff
- [ ] Total run timeout: 2 hours max
- [ ] `cron_setup.sh` installs crontab entry for 02:00 daily
- [ ] Run log written as Obsidian note in `vault/logs/`
- [ ] Hermes can invoke `nightly_run.py` directly
- [ ] Tests pass with mocked stages
- [ ] No hardcoded paths; uses config.yaml for vault_dir, output_dir, etc.

## Tests required

- test_nightly_run_full_pipeline
- test_state_checkpoint_write
- test_state_resume_from_checkpoint
- test_stage_error_handling
- test_retry_logic
- test_timeout_enforcement
- test_run_log_output

## Security constraints

- State files stored locally only, not committed
- Run logs may contain product IDs but no credentials
- Cron runs under ubuntu user, not root
- No network calls outside Shopee + CLI APIs

## Notes

- Hermes is the high-level orchestrator; nightly_run.py is the execution script Hermes invokes
- State file format: JSON with stage_name, status, timestamp, error (if any)
- Run log note type: `nightly_run_log` (add to OBSIDIAN_CONTRACT if needed)
- This task references design doc: docs/plans/shopee-first-autonomous-system.md Phase 3
