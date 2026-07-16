# Shared Context — 9ake-kiro-agents

## Project

You are working on **Affiliate Product Intelligence OS** — a local-first AI system that identifies high-opportunity affiliate products before creating content.

## Phase 1 Constraints

- No database. All data lives in Obsidian-compatible Markdown with YAML frontmatter.
- No autopublish. `ENABLE_AUTOPUBLISH` must remain `false`.
- No direct OpenAI API calls unless explicitly configured.
- No scraping that violates marketplace terms.
- No real credential storage in GitHub.

## Forbidden Actions

- Do NOT commit `.env`, API keys, tokens, affiliate links, or payout data.
- Do NOT add database dependencies.
- Do NOT generate affiliate content before product scoring is complete.
- Do NOT bypass compliance checks.
- Do NOT implement features outside the scope of the assigned task.
- Do NOT push directly to `main`. Always use feature branches.

## Project Source of Truth

Before working, read these files for context:

1. `CONTEXT.md` — Mission and architecture
2. `AGENT.md` — Agent operating model
3. `AGENTS.md` — Codex CLI rules and constraints
4. `docs/SCORING_SPEC.md` — Scoring formula
5. `docs/WORKFLOW_SPEC.md` — Workflow steps
6. `docs/OBSIDIAN_CONTRACT.md` — Markdown note contracts

## Git Rules

- Work on a feature branch (e.g., `feature/task-description`).
- Every implementation must reference a task file under `codex/tasks/`.
- Add or update tests when implementing logic.
- Summarize changed files and tests run in your output.

## Output Contract

Every agent MUST return a JSON object with this exact structure:

```json
{
  "task_id": "<uuid of the assigned task>",
  "status": "success | fail | partial",
  "summary": "<1-2 sentence description of what was accomplished>",
  "files_modified": ["<list of modified file paths>"],
  "files_created": ["<list of created file paths>"],
  "tests_run": "<test command executed, or null>",
  "tests_passed": true | false | null,
  "errors": ["<error messages if any>"],
  "next_steps": ["<recommended follow-up actions>"]
}
```

If your task involves creating code, you must also ensure:
- Code is working and syntactically valid.
- Tests are included or updated.
- No hardcoded secrets.

## Communication Style

- Be concise and direct.
- Focus on the assigned task only.
- Report problems clearly with error details.
- Suggest next steps when relevant.
