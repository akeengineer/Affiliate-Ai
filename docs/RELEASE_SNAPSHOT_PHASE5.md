# Release Snapshot — Phase 5

## 1. Release objective

Record that the local, static, read-only UI shell line is complete: Phase 4A-4E
(static demo bundle) and Phase 5A-5D (UI shell boundary, prototype, verifier, and
demo command). Everything here is local-first, read-only, and artifact-driven —
no backend, no API, no database, no vault writes, and no external network.

## 2. Phase completion matrix (Phase 4A → Phase 5D)

| phase | description | status |
| --- | --- | --- |
| Phase 4A | local static read-only UI mock | complete |
| Phase 4B | UI snapshot pack | complete |
| Phase 4C | static snapshot catalog | complete |
| Phase 4D | static demo bundle verifier | complete |
| Phase 4E | demo bundle operator command | complete |
| Phase 5A | UI shell boundary plan | complete |
| Phase 5B | local static read-only UI shell prototype | complete |
| Phase 5C | UI shell verifier / acceptance gate | complete |
| Phase 5D | UI shell demo bundle command | complete |

## 3. Operator commands

```
bash scripts/dev/run_phase4e_demo_bundle.sh 2026-W26
bash scripts/dev/run_phase5b_ui_shell.sh 2026-W26
bash scripts/dev/run_phase5c_ui_shell_verifier.sh
bash scripts/dev/run_phase5d_ui_shell_demo.sh 2026-W26
```

The Phase 5D command is the single operator entrypoint for the full UI shell
demo chain; it runs Phase 4E, Phase 5B, and Phase 5C in order and writes a
Phase 5D summary/report.

## 4. Output artifacts

- `tmp/phase4e-demo-bundle/` — demo bundle summary and report
- `tmp/phase5b-ui-shell/` — `index.html` static read-only shell
- `tmp/phase5c-ui-shell-verifier/` — verification report and summary
- `tmp/phase5d-ui-shell-demo/` — `ui-shell-demo-summary.json`, `UI_SHELL_DEMO.md`

All outputs are gitignored working artifacts under `tmp/`.

## 5. UI shell chain

1. Phase 4E builds the static demo bundle from existing artifacts.
2. Phase 5B generates the static read-only UI shell (`index.html`, inline CSS,
   zero JavaScript) over the Phase 4 JSON summaries.
3. Phase 5C verifies the generated shell and emits a verdict.
4. Phase 5D orchestrates the chain and records the overall demo status.

## 6. Verifier / acceptance gates

Phase 5C is a read-only acceptance gate over the generated shell. It checks the
shell is self-contained, contains no JavaScript or external URLs, exposes no
vault paths/secrets/affiliate markers, references no approved workflow, includes
the required sections, and uses only relative links. Phase 5D always runs
Phase 5C and never bypasses it.

## 7. Guardrails

- no backend, no API, no database
- no vault reads, no vault writes
- no external URLs, no external APIs, no network calls
- no approval mutation, no approved workflow triggering
- no JavaScript, no frontend framework
- writes only under the `tmp/` demo directories listed above

## 8. Verdict policy

The Phase 5C verdict drives the Phase 5D `ui_shell_demo_status` and
`phase5d_status`:

- `ready` — all checks pass; `phase5d_status` success (exit 0)
- `warning` — checks pass with a degraded/missing-source or staleness notice;
  `phase5d_status` success (exit 0); `warning` is not a failure
- `failed` — a hard check failed or a step exited non-zero; `phase5d_status`
  failed (exit non-zero)

## 9. Test posture

Run the suite with:

```
python -m pytest -q
```

The Phase 4/5 wrappers are covered by focused docs-contract and end-to-end
tests; no test asserts a brittle total count.

## 10. Known limitations

- The UI shell is a static snapshot; it is stale until the chain is rerun.
- Phase 4 summaries are single-run, so a differing report week surfaces as a
  staleness warning rather than a failure.
- A clean fresh chain yields `ready`; `warning`/`failed` are exercised by the
  Phase 5C and Phase 5D tests.

## 11. Next steps

- Future production hardening remains out of scope for the static read-only
  shell line and would be planned as a separate phase.
