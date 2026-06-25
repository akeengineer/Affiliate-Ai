# Task 003 - Operational AI Agents Runtime

## Task ID

003-operational-ai-agents-runtime

## Objective

Prepare the project so Hermes, Codex CLI, tmux, GitHub, and Obsidian-compatible Markdown artifacts can work together as a real Phase 1 AI agent operating loop.

This task is about runtime readiness, contracts, and executable documentation. It must not implement affiliate scoring logic or content generation directly.

## Files to read first

- AGENTS.md
- CONTEXT.md
- AGENT.md
- docs/SCORING_SPEC.md
- docs/WORKFLOW_SPEC.md
- docs/OBSIDIAN_CONTRACT.md
- docs/HERMES_OPERATING_RULES.md
- docs/CODEX_IMPLEMENTATION_GUIDE.md
- docs/GITHUB_WORKFLOW.md
- docs/SECURITY.md
- docs/plans/operational-ai-agents.md
- codex/tasks/001-bootstrap-scoring.md

## Scope

- Verify EC2 Ubuntu runtime assumptions from `docs/plans/operational-ai-agents.md`.
- Document exact setup commands needed for GitHub deploy key, repo clone, Codex CLI, Python venv, and baseline tests.
- Update project documentation only where needed to make the runtime workflow repeatable.
- Prepare follow-up task boundaries for scoring, Obsidian templates, weekly reports, agent prompts, and tmux warroom execution.
- Keep all changes small and reviewable.

## Out of scope

- Do not implement `scripts/dev/score_product.py`.
- Do not implement weekly report generation.
- Do not implement content generation.
- Do not enable autopublish.
- Do not add any database.
- Do not commit `.env`, SSH keys, API keys, OAuth tokens, affiliate links, payout data, or private Obsidian notes.
- Do not create a custom Obsidian plugin in Phase 1.

## Acceptance criteria

- `docs/plans/operational-ai-agents.md` exists and describes the operational runtime target.
- The plan states that EC2 Ubuntu is the runtime and Windows is only the access workstation.
- The plan states that the GitHub repository is the source of truth.
- The plan states that the EC2 working copy should live at `/home/ubuntu/Affiliate-Ai`.
- The plan states that Hermes orchestration uses the root profile at `/root/.hermes`.
- The plan lists commands to verify `tmux`, `hermes`, `python3`, `git`, `node`, `npm`, and `codex`.
- The plan lists commands to clone the repository and prepare Python dev dependencies.
- The plan preserves Phase 1 constraints: no database, no autopublish, no private Obsidian data in GitHub.
- No product code is implemented as part of this task.

## Tests required

Documentation-only verification:

```bash
git status --short
git grep -n "Operational AI Agents Plan" docs/plans/operational-ai-agents.md
git grep -n "003-operational-ai-agents-runtime" codex/tasks/003-operational-ai-agents-runtime.md
```

Runtime commands to run manually on EC2 after deploy key and clone are configured:

```bash
ssh god-of-ai 'tmux -V && hermes --version && python3 --version && git --version'
ssh god-of-ai 'codex --version'
ssh god-of-ai 'cd /home/ubuntu/Affiliate-Ai && git status'
ssh god-of-ai 'sudo hermes status'
```

No Python unit tests are required for this task because it does not implement application logic.

## Security constraints

- Never commit EC2 private keys or public deploy-key material unless it is explicitly documented as safe. Prefer not committing any key material.
- Never copy `/root/.hermes/.env`, `/root/.hermes/auth.json`, or Obsidian credentials into the repository.
- Keep GitHub limited to source code, specs, task files, workflows, templates, and sanitized samples.
- Keep private Obsidian business data out of GitHub.
- Keep `ENABLE_AUTOPUBLISH=false`.
- Keep `ENABLE_OPENAI_API_DIRECT=false`.

## Notes

- This task exists because the repository previously had a good architecture scaffold but not a working agent runtime.
- The next implementation task should revise `codex/tasks/001-bootstrap-scoring.md` before writing scoring code, because scoring field names and missing-signal behavior need to be explicit.
- After scoring works, create separate small tasks for Obsidian template hardening, weekly reports, agent prompt contracts, and tmux warroom execution.
