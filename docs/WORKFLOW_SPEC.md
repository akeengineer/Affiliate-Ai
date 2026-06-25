# Workflow Spec

## Weekly product scan

1. Ingest or create product candidates in Obsidian.
2. Add trend, marketplace, and commission signals.
3. Run deterministic scoring.
4. Select top candidates.
5. Run agent warroom for candidates above threshold.
6. Store meeting and votes in Obsidian.
7. Generate decision notes.
8. Generate content drafts only for `launch` or `small_batch_test` products.
9. Run compliance check.
10. Generate weekly report.

## Campaign launch rule

A campaign cannot be launched without:

- product score
- at least 3 agent votes
- decision note
- compliance result
