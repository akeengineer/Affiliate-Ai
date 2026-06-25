# Affiliate Product Intelligence OS

Local-first Affiliate Product Intelligence OS for product discovery, trend intelligence, commission scoring, agent voting, compliance review, and content planning.

## Core rules

- Obsidian is the only backend/project memory in Phase 1.
- Do not use PostgreSQL, MySQL, DynamoDB, or any external database in Phase 1.
- Hermes Agent is the orchestrator.
- Codex CLI is the implementation engine.
- GitHub is for source control, tasks, PR reviews, CI checks, and audit trail.
- Do not generate affiliate content before product scoring.
- Do not launch campaigns before agent voting.
- Do not autopublish in Phase 1.

## First run

```bash
cp .env.example .env
mkdir -p vendor
git clone https://github.com/Affitor/affiliate-skills.git vendor/affiliate-skills
```

Then run Codex from the project root and ask it to read `AGENTS.md` before doing any work.
