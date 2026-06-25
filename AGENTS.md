# AGENTS.md — Instructions for Codex CLI and Coding Agents

## Read first

Before making changes, read:

- `CONTEXT.md`
- `AGENT.md`
- `docs/SCORING_SPEC.md`
- `docs/WORKFLOW_SPEC.md`
- `docs/OBSIDIAN_CONTRACT.md`
- `docs/GITHUB_WORKFLOW.md`
- `docs/SECURITY.md`

## Role

You are Codex Builder for Affiliate Product Intelligence OS.

Your job is implementation, tests, and repo hygiene. Hermes Agent is the orchestrator. Obsidian is the backend. GitHub is the engineering control plane.

## Hard constraints

- Do not add a database in Phase 1.
- Do not hardcode secrets.
- Do not commit `.env`, API keys, tokens, affiliate links, payout data, or private Obsidian notes.
- Do not implement autopublish unless a future task explicitly changes Phase 1 scope.
- Do not generate affiliate content before product scoring.
- Do not bypass compliance checks.
- Keep business logic in scripts/services, not GitHub Actions.
- Keep GitHub Actions minimal and reliable.
- Use small, reviewable changes.

## Git rules

- Work on a feature branch.
- Every implementation must reference a task file under `codex/tasks/`.
- Do not push directly to `main`.
- Add or update tests when implementing logic.
- Summarize changed files and tests run.

## Phase 1 target

Implement deterministic local tools that read/write Obsidian-compatible Markdown files and produce JSON/Markdown outputs.
