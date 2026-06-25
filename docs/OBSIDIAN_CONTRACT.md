# Obsidian Contract

## Backend rule

Obsidian Vault is the only backend/project memory in Phase 1.

Hermes must use the enabled Obsidian integration to read, create, search, and update notes.

Codex may write deterministic scripts that operate on Markdown files, but must not introduce a database.

## Allowed note types

- product_candidate
- trend_signal
- marketplace_signal
- commission_signal
- agent_meeting
- agent_vote
- decision
- content_draft
- compliance_result
- weekly_report

## Required frontmatter

Every note must include:

```yaml
type:
created_at:
updated_at:
status:
```

## Private data policy

Real business data under `vault/products`, `vault/trends`, `vault/meetings`, `vault/decisions`, `vault/contents`, and `vault/reports` must not be committed to GitHub.
Only templates and sanitized samples may be committed.
