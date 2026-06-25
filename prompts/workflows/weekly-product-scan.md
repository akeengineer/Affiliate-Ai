# Weekly Product Scan Workflow

1. Collect or update `product_candidate` notes in `vault/products/` or `vault/samples/products/`.
2. Add `trend_signal`, `marketplace_signal`, and `commission_signal` notes with exact frontmatter contracts.
3. Run deterministic scoring with `python scripts/dev/score_product.py <product-note> --pretty`.
4. Send only scored candidates to the agent warroom.
5. Record at least 3 `agent_vote` notes and 1 `compliance_result` note before creating a `decision` note.
6. Generate the weekly report with `python scripts/dev/generate_weekly_report.py --input-dir vault/samples --report-week YYYY-Www`.

## Launch gate

A candidate is not launch-ready until all of these exist:

- deterministic score
- at least 3 votes
- compliance result
- decision note
