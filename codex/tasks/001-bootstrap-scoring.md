# Task 001 — Bootstrap Product Scoring

## Objective

Implement a deterministic product scoring utility that reads Obsidian-compatible product candidate notes and calculates Product Opportunity Score.

## Read first

- AGENTS.md
- docs/SCORING_SPEC.md
- docs/OBSIDIAN_CONTRACT.md

## Scope

Create:

- `scripts/dev/score_product.py`
- `tests/test_score_product.py`

## Requirements

- Parse YAML frontmatter from Markdown files.
- Validate score inputs are 0-100.
- Calculate Product Opportunity Score using `docs/SCORING_SPEC.md`.
- Return decision: `launch`, `small_batch_test`, `watchlist`, or `reject`.
- No external API calls.
- No database.

## Product candidate schema

The scoring input is a single `product_candidate` note.

Required frontmatter fields:

- `type=product_candidate`
- `product_id`
- `product_name`
- `marketplace`
- `currency`
- `demand_score`
- `trend_velocity_score`
- `marketplace_rank_score`
- `commission_score`
- `content_fit_score`
- `competition_gap_score`
- `risk_score`
- `created_at`
- `updated_at`
- `status`

Optional frontmatter fields:

- `brand`
- `niche`
- `product_url`
- `trend_signal_note`
- `marketplace_signal_note`
- `commission_signal_note`
- `compliance_result_note`

## Missing-signal behavior

- Missing any required score field fails validation.
- Missing any of `trend_signal_note`, `marketplace_signal_note`, or `commission_signal_note` reduces confidence by `20` each.
- Missing `compliance_result_note` reduces confidence by `10`.
- Confidence starts at `100` and bottoms out at `0`.
- Missing-signal behavior changes `confidence_score` only. It does not change the weighted product opportunity score.

## JSON output

The CLI must print JSON with exactly these top-level keys:

- `input_path`
- `product_id`
- `product_name`
- `marketplace`
- `currency`
- `product_opportunity_score`
- `score_decision`
- `confidence_score`
- `missing_signal_count`
- `missing_signals`
- `component_scores`
- `note_refs`

`component_scores` must contain:

- `demand_score`
- `trend_velocity_score`
- `marketplace_rank_score`
- `commission_score`
- `content_fit_score`
- `competition_gap_score`
- `risk_score`

`note_refs` must contain:

- `trend_signal_note`
- `marketplace_signal_note`
- `commission_signal_note`
- `compliance_result_note`

## CLI usage

```bash
python scripts/dev/score_product.py <path-to-product-candidate.md>
```

Optional flag:

```bash
python scripts/dev/score_product.py <path> --pretty
```

## Sample input path

- `vault/samples/products/smart-desk-pad.md`

## Acceptance criteria

- Unit tests cover all thresholds.
- Missing optional note refs reduce confidence exactly as documented above.
- Script can run against a sample markdown file.
- Malformed frontmatter fails with a clear error.
