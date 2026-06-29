# UI Mock (Phase 4A)

## 1. Purpose

The UI mock is a **local, read-only, static HTML** view over the artifacts that
the CLI already generates. It exists to demo the product intelligence output
visually without adding any server, API, database, or interactivity. It reads
generated artifacts only and never touches the vault.

## 2. Generate the mock

```
bash scripts/dev/run_phase4a_ui_mock.sh 2026-W26
```

This writes `tmp/phase4a-ui/index.html` and prints:

```
ui_mock_path: tmp/phase4a-ui/index.html
phase4a_status: success
```

## 3. Generate the required artifacts first

The mock renders whatever artifacts exist for the week. To produce a fully
populated page, run the acceptance pack first:

```
bash scripts/dev/run_phase3d_acceptance.sh
```

That creates the Phase 3A dashboard and Phase 3B portfolio artifacts for
`2026-W26`. Then build the mock as in section 2.

## 4. Open the mock

Open the generated file directly in a browser (no server needed):

```
file://<repo-root>/tmp/phase4a-ui/index.html
```

For example: `file:///home/ubuntu/Affiliate-Ai/tmp/phase4a-ui/index.html`.

## 5. What the mock displays

- **Header**: system name, report week, and a `READ-ONLY MOCK` badge.
- **Portfolio overview**: total, launch, small_batch_test, watchlist, reject,
  promoted, decision draft, and decision complete counts (from the Phase 3B
  artifact).
- **Top products table**: rank, product_id, product_name, score, score_decision,
  confidence.
- **By-decision sections**: Launch, Small Batch Test, Watchlist, Reject.
- **Per-product pipeline cards**: score, decision, confidence, and the pipeline
  statuses (report, hermes, governance, promote, decision, finalization) plus the
  next allowed action (from Phase 3A artifacts where available).
- **Footer**: generated timestamp, "generated from tmp artifacts", and a
  guardrail notice.

## 6. What the mock does NOT do

- no server
- no API
- no database
- no external resources
- no approval mutation
- no vault writes
- no affiliate content generation
- no campaign launch

## 7. Demo instructions

1. Run the acceptance pack: `bash scripts/dev/run_phase3d_acceptance.sh`.
2. Build the UI mock: `bash scripts/dev/run_phase4a_ui_mock.sh 2026-W26`.
3. Open `tmp/phase4a-ui/index.html` in a local browser via `file://`.
4. Talk through the page:
   - Point out the **portfolio overview** metrics at the top.
   - Show the **top products** table and how it ranks by score.
   - Open a **per-product pipeline card** and read its statuses and the
     `next_allowed_action`.
   - Finish on the **guardrail footer** — emphasize that nothing here mutates
     state; it is a read-only snapshot.

### Textual screenshot guidance (no binary screenshots committed)

Describe, do not capture:

- "Top of page: dark header bar with the system name and a red `READ-ONLY MOCK`
  badge."
- "First card: a grid of eight metric tiles (counts)."
- "Middle: a six-column top-products table."
- "Lower: stacked per-product cards listing pipeline statuses."
- "Bottom: a small grey guardrail footer."

## 8. Known limitations

- It is a **static snapshot**; it reflects the artifacts at build time.
- It becomes **stale if the artifacts are stale**; rebuild after regenerating.
- There is **no interactivity** (zero JavaScript).
- There is **no live refresh**; re-run the build to update.
- **No screenshots are committed**; use the textual guidance above.
