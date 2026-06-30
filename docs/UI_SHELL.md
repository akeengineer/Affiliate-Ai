# UI Shell (Phase 5B)

## Purpose

The UI shell is a **local, static, read-only** HTML entry point that summarizes
the Phase 4 demo pipeline (4E readiness, 4B snapshot, 4C catalog, 4D
verification) and links to the existing local static Phase 4 outputs. It is the
first implementation inside the boundary defined in
[`docs/UI_SHELL_BOUNDARY.md`](UI_SHELL_BOUNDARY.md) and stays within every rule
of that contract.

## Command

Regenerate the Phase 4 demo data first, then build the shell:

```
bash scripts/dev/run_phase4e_demo_bundle.sh 2026-W26
bash scripts/dev/run_phase5b_ui_shell.sh 2026-W26
```

The wrapper prints:

```
ui_shell_path: tmp/phase5b-ui-shell/index.html
phase5b_status: success
```

## Output path

`tmp/phase5b-ui-shell/index.html` — one self-contained file (inline CSS, zero
JavaScript). Open it directly in a local browser via `file://`.

## Data sources

Reads only these four Phase 4 JSON summary files:

- `tmp/phase4e-demo-bundle/demo-bundle-summary.json`
- `tmp/phase4b-ui-snapshot/manifest.json`
- `tmp/phase4c-snapshot-catalog/catalog.json`
- `tmp/phase4d-demo-verifier/verification-summary.json`

It links (relative, only when present) to:

- `../phase4b-ui-snapshot/index.html`
- `../phase4c-snapshot-catalog/index.html`
- `../phase4d-demo-verifier/verification-report.md`
- `../phase4e-demo-bundle/DEMO_BUNDLE.md`

## Guardrails

- local static only; read-only
- no backend, no API, no database
- no vault reads, no vault writes
- no external URLs, no external resources
- no JavaScript; self-contained inline CSS
- writes only under `tmp/phase5b-ui-shell/`
- a cleanliness assertion fails the build before writing if the page would
  contain a vault path, external URL, secret, affiliate/content marker, or any
  script/fetch/iframe/form/event-handler markup

## What it does NOT do

- no approval mutation; no Phase 2G/2H/2I triggering
- no affiliate content generation, autopublish, or campaign launch
- no marketplace connector; no raw artifact or raw score export
- does not read the vault, raw score JSON, Phase 3 artifacts, or raw Phase 4
  HTML bodies

## Relation to the boundary

`docs/UI_SHELL_BOUNDARY.md` defines what a future UI shell may and may not do.
This Phase 5B prototype implements the allowed subset only: display snapshot,
catalog, verification, and demo-readiness status, link to local static files
with relative links, and show guardrail status.

## Verifier (Phase 5C)

A read-only acceptance gate verifies the generated shell (it never regenerates
it):

```
bash scripts/dev/run_phase5c_ui_shell_verifier.sh
```

Outputs:

- `tmp/phase5c-ui-shell-verifier/verification-report.md`
- `tmp/phase5c-ui-shell-verifier/verification-summary.json`

Verdict policy:

- `ready` = success (exit 0); all checks pass, no warnings
- `warning` = success (exit 0); checks pass but a degraded/missing-source notice
  or staleness notice is present
- `failed` = non-zero (exit 1); a hard safety or structure check failed

Guardrails: no JS, no external URLs, no vault paths, no approved-workflow
references, and no backend/API/database. The verifier reads only the shell body
and the four Phase 4 JSON summaries, checks link targets by existence only, and
writes only under `tmp/phase5c-ui-shell-verifier/`.

## Demo bundle command (Phase 5D)

One operator command runs the complete local static UI shell demo chain:

```
bash scripts/dev/run_phase5d_ui_shell_demo.sh 2026-W26
```

Chain:

- Phase 4E demo bundle
- Phase 5B UI shell generation
- Phase 5C UI shell verifier (always run; never bypassed)
- Phase 5D summary/report writer

Outputs:

- `tmp/phase5d-ui-shell-demo/ui-shell-demo-summary.json`
- `tmp/phase5d-ui-shell-demo/UI_SHELL_DEMO.md`

Verdict policy:

- `ready` = success (exit 0)
- `warning` = success (exit 0) — degraded/missing-source notice, not a failure
- `failed` = non-zero (exit 1) — a hard check failed or a step exited non-zero

Guardrails: no backend, no API, no database, no vault writes, no external URLs,
no approved workflow. The verdict-to-status decision is owned by
`build_ui_shell_demo_summary.py`.

## Known limitations

- Static snapshot; reflects the Phase 4 JSON at build time and is stale until
  rebuilt.
- The Phase 4 summaries are single-run (not week-partitioned); a `report_week`
  that differs from the requested week is shown as a visible staleness notice.
- No live refresh; no interactivity; no production deployment.
