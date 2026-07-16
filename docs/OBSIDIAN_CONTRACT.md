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
- nightly_run_log

## Required frontmatter

Every note must include:

```yaml
type:
created_at:
updated_at:
status:
```

Timestamps use ISO-8601 UTC strings, for example `2026-06-25T15:00:00Z`.

## Per-note contracts

### `product_candidate`

Purpose: single source note for deterministic scoring input.

Required frontmatter:

```yaml
type: product_candidate
product_id:
product_name:
marketplace:
currency:
demand_score:
trend_velocity_score:
marketplace_rank_score:
commission_score:
content_fit_score:
competition_gap_score:
risk_score:
created_at:
updated_at:
status:
```

Optional frontmatter:

```yaml
brand:
niche:
product_url:
trend_signal_note:
marketplace_signal_note:
commission_signal_note:
compliance_result_note:
product_opportunity_score:
score_decision:
confidence_score:
missing_signal_count:
last_scored_at:
```

Rules:

- All score fields are numeric `0-100`.
- Deterministic scoring reads only the note frontmatter.
- Missing note refs do not block scoring, but they reduce confidence.
- Missing any required score field fails scoring validation.

### `trend_signal`

Required frontmatter:

```yaml
type: trend_signal
signal_id:
product_id:
source:
signal_date:
trend_velocity_score:
created_at:
updated_at:
status:
```

Optional frontmatter:

```yaml
evidence_summary:
source_url:
```

### `marketplace_signal`

Required frontmatter:

```yaml
type: marketplace_signal
signal_id:
product_id:
marketplace:
category_rank:
marketplace_rank_score:
source:
created_at:
updated_at:
status:
```

Optional frontmatter:

```yaml
evidence_summary:
source_url:
```

### `commission_signal`

Required frontmatter:

```yaml
type: commission_signal
signal_id:
product_id:
program_name:
commission_score:
payout_window_days:
created_at:
updated_at:
status:
```

Optional frontmatter:

```yaml
commission_rate_text:
network:
evidence_summary:
source_url:
```

### `agent_vote`

Required frontmatter:

```yaml
type: agent_vote
vote_id:
product_id:
agent_name:
vote:
confidence_score:
created_at:
updated_at:
status:
```

Optional frontmatter:

```yaml
blocking_issues:
required_actions:
```

Rules:

- `vote` must be one of `launch`, `small_batch_test`, `watchlist`, `reject`.
- `confidence_score` is numeric `0-100`.

### `decision`

Required frontmatter:

```yaml
type: decision
decision_id:
product_id:
final_decision:
vote_count:
compliance_status:
created_at:
updated_at:
status:
```

Optional frontmatter:

```yaml
required_actions:
decision_summary:
```

### `compliance_result`

Required frontmatter:

```yaml
type: compliance_result
compliance_id:
product_id:
compliance_status:
disclosure_required:
risk_score:
created_at:
updated_at:
status:
```

Optional frontmatter:

```yaml
blocked_reasons:
notes:
```

Rules:

- `compliance_status` must be one of `approved`, `needs_review`, `blocked`.
- `risk_score` is numeric `0-100`.

### `weekly_report`

Required frontmatter:

```yaml
type: weekly_report
report_id:
report_week:
generated_at:
candidate_count:
launch_count:
small_batch_test_count:
watchlist_count:
reject_count:
created_at:
updated_at:
status:
```

Optional frontmatter:

```yaml
source_root:
```

### `agent_meeting`

Required frontmatter:

```yaml
type: agent_meeting
meeting_id:
meeting_date:
product_ids:
created_at:
updated_at:
status:
```

### `nightly_run_log`

Required frontmatter:

```yaml
type: nightly_run_log
run_id:
pipeline_status:
resumed:
successful_stage_count:
started_at:
finished_at:
created_at:
updated_at:
status:
```

Optional frontmatter:

```yaml
failed_stage:
```

Rules:

- `pipeline_status` must be one of `completed`, `failed`, or `timed_out`.
- Run logs may contain product IDs and sanitized errors, but never credentials or tokens.

## Private data policy

Real business data under `vault/products`, `vault/trends`, `vault/meetings`, `vault/decisions`, `vault/contents`, `vault/reports`, and `vault/logs` must not be committed to GitHub.
Only templates and sanitized samples may be committed.
