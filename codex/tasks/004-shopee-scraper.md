# Codex Task: Shopee Scraper + Pipeline Integration

## Task ID

004-shopee-scraper

## Objective

Build a Playwright-based Shopee product scraper that outputs Obsidian-compatible product_candidate Markdown notes, integrated with the existing scoring pipeline.

## Files to read first

- AGENTS.md
- CONTEXT.md
- docs/SCORING_SPEC.md
- docs/WORKFLOW_SPEC.md
- docs/OBSIDIAN_CONTRACT.md
- docs/plans/shopee-first-autonomous-system.md
- vault/templates/product-candidate-template.md
- scripts/dev/score_product.py

## Scope

- `scripts/shopee/scraper.py` — Playwright scraper for Shopee Thailand (.co.th)
- `scripts/shopee/config.yaml` — Target niches, keywords, categories, limits
- `scripts/shopee/to_candidate.py` — Transform scraped JSON → product_candidate Markdown note
- `tests/test_shopee_scraper.py` — Unit + integration tests
- `requirements-shopee.txt` — Dependencies (playwright, etc.)

## Out of scope

- Shopee Affiliate API integration (Task 006)
- Agent AI analysis (Task 005)
- Notification (Task 007)
- Autopublish

## Acceptance criteria

- [ ] `python scripts/shopee/scraper.py --config scripts/shopee/config.yaml` runs without error
- [ ] Outputs scraped product data as JSON (product name, price, sold count, rating, category, shop name, product URL)
- [ ] `python scripts/shopee/to_candidate.py --input scraped.json --output-dir vault/candidates/` produces valid product_candidate notes
- [ ] Output notes pass `python scripts/dev/score_product.py <note>` without error
- [ ] Rate limiting: minimum 2s delay between requests, randomized
- [ ] User-agent rotation from configurable list
- [ ] Handles network errors gracefully (retry 3x with exponential backoff)
- [ ] Tests pass: `pytest tests/test_shopee_scraper.py -v`
- [ ] No hardcoded credentials or affiliate links
- [ ] `.gitignore` updated to exclude scraped data cache

## Tests required

- test_scraper_config_loading
- test_scraper_rate_limiting
- test_scraper_retry_on_failure
- test_to_candidate_valid_output
- test_to_candidate_frontmatter_schema
- test_pipeline_integration (scrape → candidate → score)

## Security constraints

- No credentials in source code
- Scraped data stored locally only, not committed
- Respect robots.txt where possible
- No PII collection from shop owners

## Notes

- Start with Shopee Thailand (.co.th) as primary target
- Focus on trending/bestseller categories initially
- config.yaml should support multiple niches for overnight batch scanning
- This task references design doc: docs/plans/shopee-first-autonomous-system.md Phase 1
