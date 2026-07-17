# Task 104 — EC2 Agent and Task Monitoring

## Task ID

104-agent-task-monitoring

## Objective

Add a read-only local dashboard for AI agent processes, task progress, runtime services, recent repository activity, scraper results, and EC2 resource use.

## Scope

- Add `scripts/dev/monitor_agents.sh` with a one-shot dashboard and a 30-second `--watch` mode.
- Show `codex`, `claude`, and `agy` processes without exposing full prompt payloads or secret-bearing arguments.
- Show active tmux sessions, the five latest Git commits, and files modified under `scripts/` or `tests/` in the last 10 minutes.
- Summarize the newest JSON result under `.cache/shopee/scraped/` without printing product records.
- Show Cloudflare WARP proxy, root disk, and memory status.
- Add `scripts/dev/monitor_tasks.py` to classify every `codex/tasks/*.md` task from matching branch and Git-log evidence.
- Add focused automated tests and make both scripts executable.

## Status rules

- `DONE`: a matching task branch has a Git commit that changes the task file.
- `IN PROGRESS`: a matching task branch exists, but no task-file commit evidence exists.
- `PENDING`: no matching local or remote branch exists.

## Out of scope

- Do not manage, stop, restart, or dispatch agents.
- Do not mutate tmux, WARP, scraper, Git, or task state.
- Do not display full AI prompts, credentials, proxy authentication, tokens, or private scraper product records.
- Do not add a database or publishing behavior.

## Acceptance criteria

- [x] The shell dashboard includes all requested runtime sections and degrades gracefully when optional tools or outputs are absent.
- [x] `--watch` delegates to `watch` with a 30-second interval and color support.
- [x] Task output is a formatted table with task, status, matching branch, commit evidence, and title.
- [x] Task state is derived from read-only Git branch/log inspection.
- [x] Both scripts run successfully from outside the repository working directory.
- [x] Focused tests pass and no secret is hardcoded or emitted from full process arguments.

## Verification

```bash
NO_COLOR=1 scripts/dev/monitor_agents.sh
NO_COLOR=1 scripts/dev/monitor_tasks.py
python3 -m pytest tests/test_monitoring.py -q
git diff --check
```
