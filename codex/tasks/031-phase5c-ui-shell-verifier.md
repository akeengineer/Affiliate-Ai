# Task 031 - Phase 5C UI Shell Verifier / Acceptance Gate

## 1. Purpose

Verify the generated Phase 5B static shell and produce a local verification
report and JSON summary, in the spirit of the Phase 4D demo verifier. Read-only:
validate safety and readiness of the existing shell; never regenerate it, never
touch the vault, and never call external services.

## 2. Scope

- One Python stdlib verifier and a bash wrapper.
- Writes only `verification-report.md` and `verification-summary.json` under
  `tmp/phase5c-ui-shell-verifier/`.
- Docs and tests. No change to Phase 5B, Phase 4, or scoring/import/report
  semantics unless a verifier test exposes a real bug.

## 3. Files

- `codex/tasks/031-phase5c-ui-shell-verifier.md`
- `scripts/dev/verify_ui_shell.py`
- `scripts/dev/run_phase5c_ui_shell_verifier.sh`
- `tests/test_phase5c_ui_shell_verifier.py`
- `docs/UI_SHELL.md` (verifier section)
- `.gitignore` (+ `tmp/phase5c-ui-shell-verifier/`)
- `scripts/dev/README.md` (one index entry)

## 4. Data sources

Reads body of: `tmp/phase5b-ui-shell/index.html` and the four Phase 4 JSON
summaries (`demo-bundle-summary.json`, `manifest.json`, `catalog.json`,
`verification-summary.json`). Checks link targets
(`phase4b-ui-snapshot/index.html`, `phase4c-snapshot-catalog/index.html`,
`phase4d-demo-verifier/verification-report.md`,
`phase4e-demo-bundle/DEMO_BUNDLE.md`) by existence only — never body. Never
reads the vault, raw score JSON, Phase 3 artifacts, or raw Phase 4 HTML bodies.

## 5. Output structure

`tmp/phase5c-ui-shell-verifier/verification-report.md` (title, generated_at,
verdict, checks table PASS/FAIL/WARN, warnings, checked paths, guardrail
summary) and `tmp/phase5c-ui-shell-verifier/verification-summary.json`
(`type=phase5c_ui_shell_verification`, `generated_at`, `verdict`, `checks{}`,
`warnings[]`, `checked_paths[]`, `shell_path`).

## 6. Verification rules

Hard checks (any false -> `failed`): `shell_exists`, `output_under_expected_dir`,
`self_contained` (inline `<style`, no external `<link`/`<iframe`/`<form`),
`no_js` (no `<script`/`fetch(`/`XMLHttpRequest`/`import(`/event handlers),
`no_external_url`, `no_vault_path`, `no_secret`, `no_affiliate_marker`,
`no_approved_workflow_ref`, `required_sections` (READ-ONLY SHELL, demo
readiness, snapshot, catalog, verification, local links, guardrail footer),
`links_relative`, `sources_present_or_noticed` (a missing Phase 4 source without
a visible not-found notice is a hard failure).

Soft warnings (`warning` when hard checks pass): a referenced relative link
target is missing; a Phase 4 source JSON is missing but the shell shows a
not-found notice; a week-mismatch/staleness notice is present.

## 7. Command design

```
bash scripts/dev/run_phase5c_ui_shell_verifier.sh
```

Zero args; rejects guardrail flags (`ENABLE_AUTOPUBLISH`,
`ENABLE_OPENAI_API_DIRECT`, `APPROVE_PROMOTE`, `APPROVE_DECISION`,
`APPROVE_FINALIZE`); derives repo root, `cd "$REPO_ROOT"`; selects
`.venv/bin/python` -> `python3` -> `python`; execs `verify_ui_shell.py`. Prints
`verdict:` and `phase5c_status:`.

Verdict policy: `ready` -> exit 0; `warning` -> exit 0; `failed` -> exit 1. No
strict mode in Phase 5C.

## 8. Test strategy

Deterministic pytest with no network/Hermes/sudo: existence + executability +
`bash -n` + `py_compile`; `.gitignore`; wrong arg count; guardrail flags;
end-to-end (4E -> 5B -> 5C) verdict ready; report/summary content; output
self-safety; failed path (tampered shell); warning path (missing source with
notice); missing shell; cross-CWD; CI-C alignment; static boundary (wrapper has
no approved-workflow refs); no forbidden body ingestion (verifier does not
`read_text` Phase 4 HTML bodies).

## 9. Acceptance criteria

- `run_phase5c_ui_shell_verifier.sh` after 4E + 5B exits 0, prints
  `verdict: ready` and `phase5c_status: success`, and writes both outputs.
- Tampered/unsafe shell yields `verdict: failed` and exit 1.
- Missing Phase 4 source with a visible notice yields `verdict: warning`,
  exit 0.
- Focused Phase 5C, Phase 5B, and CI-C tests pass; full suite passes.
- No hardcoded operator path in scripts.

## 10. Verification commands

```
bash -n scripts/dev/run_phase5c_ui_shell_verifier.sh
python -m py_compile scripts/dev/verify_ui_shell.py
python -m pytest -q tests/test_phase5c_ui_shell_verifier.py
python -m pytest -q tests/test_phase5b_local_static_ui_shell_prototype.py tests/test_ci_c_runner_regression_guards.py
bash scripts/dev/run_phase4e_demo_bundle.sh 2026-W26
bash scripts/dev/run_phase5b_ui_shell.sh 2026-W26
bash scripts/dev/run_phase5c_ui_shell_verifier.sh
env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q
grep -RIn "/home/ubuntu/Affiliate-Ai" scripts/ || echo "scripts clean"
```

## 11. Known limitations

- Verifies an existing shell only; does not regenerate Phase 5B.
- Phase 4 summaries are single-run; a differing `report_week` surfaces as a
  staleness warning, not a failure.
- Link targets are checked by existence only, not by content.

## 12. Final status target

`phase5c_status: success`
