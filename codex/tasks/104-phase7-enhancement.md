# Task 104 — Phase 7 Enhancement

## Reference

`docs/plans/shopee-first-autonomous-system.md`, Phase 7 — Enhancement.

## Goal

Add local Phase 7 tools for reviewed content drafting, a read-only portfolio
web dashboard, marketplace adapter scaffolding, and deterministic scoring-weight
experiments.

## Scope

- `scripts/content/draft_generator.py`
- `scripts/dashboard/portfolio_web.py`
- `scripts/shopee/multi_marketplace.py`
- `scripts/experiments/ab_test_weights.py`
- marketplace selection and adapter configuration in `scripts/shopee/config.yaml`
- mocked component coverage in `tests/test_phase7_enhancement.py`

## Safety boundary

- Content drafts require a scored product and a completed, compliance-approved
  `launch` or `small_batch_test` decision.
- Draft output is review-only Obsidian Markdown under `vault/contents`; this task
  adds no publish or autopublish path.
- The portfolio server is read-only, uses Python's standard-library HTTP server,
  and binds to loopback by default.
- Lazada and TikTok Shop are interface/configuration skeletons only. They make no
  marketplace requests and contain no credentials.
- Weight experiments reuse the current deterministic component-score format and
  make no external calls.
- No database is added.

## Verification

- `./.venv/bin/python -m pytest tests/test_phase7_enhancement.py -q`
- `./.venv/bin/python -m pytest -q`
- `git diff --check`
