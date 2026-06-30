# Task 030 - Phase 5B Local Static UI Shell Prototype

## 1. Purpose

First real implementation inside the Phase 5A UI Shell Boundary: a local,
static, read-only HTML shell that summarizes the Phase 4 demo pipeline and links
to existing local static Phase 4 outputs. It adds no backend, no framework, and
no JavaScript, and reads only Phase 4 JSON summaries.

## 2. Scope

- One Python stdlib static generator and a bash wrapper.
- One generated self-contained HTML file under `tmp/phase5b-ui-shell/`.
- Read-only over four Phase 4 JSON summary files; relative local links only.
- Docs and tests. No change to Phase 4, CI-A/B/C, or scoring/import/report
  semantics.

## 3. Files

- `codex/tasks/030-phase5b-local-static-ui-shell-prototype.md`
- `scripts/dev/build_ui_shell.py`
- `scripts/dev/run_phase5b_ui_shell.sh`
- `docs/UI_SHELL.md`
- `tests/test_phase5b_local_static_ui_shell_prototype.py`
- `.gitignore` (+ `tmp/phase5b-ui-shell/`)
- `scripts/dev/README.md` (one index entry)

## 4. Data sources

Reads only:

- `tmp/phase4e-demo-bundle/demo-bundle-summary.json`
- `tmp/phase4b-ui-snapshot/manifest.json`
- `tmp/phase4c-snapshot-catalog/catalog.json`
- `tmp/phase4d-demo-verifier/verification-summary.json`

Never reads the vault, raw score JSON, Phase 3 artifacts, or raw Phase 4 HTML
bodies. Missing sources render a visible not-found notice and exit 0; invalid
JSON fails non-zero.

## 5. Output structure

`tmp/phase5b-ui-shell/index.html` (inline CSS, zero JS), with: header +
`READ-ONLY SHELL` badge + week + timestamp; demo readiness (4E); snapshot status
(4B); catalog status (4C); verification status (4D); local links (relative, only
if the target exists); guardrail footer.

## 6. Guardrails

- output only under `tmp/phase5b-ui-shell/` (path-traversal guarded `--out`)
- `assert_static_shell_clean()` fails before write on any vault path, affiliate
  tracking/content marker, secret, `http(s)://`, `file://`,
  `/home/ubuntu/Affiliate-Ai`, `<script`, `fetch(`, `XMLHttpRequest`,
  `import(`, `<iframe`, `<form`, external `<link`, or event-handler attribute
- all dynamic fields HTML-escaped
- wrapper rejects `ENABLE_AUTOPUBLISH`, `ENABLE_OPENAI_API_DIRECT`,
  `APPROVE_PROMOTE`, `APPROVE_DECISION`, `APPROVE_FINALIZE`
- wrapper derives repo root and `cd "$REPO_ROOT"` (cross-CWD safe); no network
  tokens; no hardcoded operator path

## 7. Command design

```
bash scripts/dev/run_phase5b_ui_shell.sh <week>
```

Validates one `<week>` arg against `^[0-9]{4}-W[0-9]{2}$`, checks guardrail
flags, selects `.venv/bin/python` -> `python3` -> `python`, and execs
`build_ui_shell.py --week <week>`. The generator reuses `WEEK_RE`, `_now_utc`,
`DashboardError`, and the scrub-pattern constants from `dashboard_summary.py`.

## 8. Test strategy

Deterministic pytest with no network/Hermes/sudo: existence + executability +
`bash -n` + `py_compile`; invalid week / wrong arg count / guardrail flags fail
non-zero; end-to-end after Phase 4E; HTML content + relative links; self-
contained zero-JS; cleanliness; missing-output notice + exit 0; no vault
write/read (JSON-fixture only); cross-CWD exit 0; CI-C alignment (no hardcoded
path, no network tokens, derives repo root); no approved-workflow references.

## 9. Acceptance criteria

- `run_phase5b_ui_shell.sh 2026-W26` exits 0, prints `ui_shell_path:` and
  `phase5b_status: success`, and writes `tmp/phase5b-ui-shell/index.html`.
- The page is self-contained, zero-JS, and passes the cleanliness assertion.
- Focused Phase 5B, Phase 4E, and CI-C tests pass; full suite passes.
- No hardcoded operator path in scripts.

## 10. Verification commands

```
bash -n scripts/dev/run_phase5b_ui_shell.sh
python -m py_compile scripts/dev/build_ui_shell.py
python -m pytest -q tests/test_phase5b_local_static_ui_shell_prototype.py
python -m pytest -q tests/test_phase4e_demo_bundle_command.py tests/test_ci_c_runner_regression_guards.py
bash scripts/dev/run_phase4e_demo_bundle.sh 2026-W26
bash scripts/dev/run_phase5b_ui_shell.sh 2026-W26
env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q
grep -RIn "/home/ubuntu/Affiliate-Ai" scripts/ || echo "scripts clean"
```

## 11. Known limitations

- Static snapshot; stale until rebuilt; Phase 4 summaries are single-run, so a
  differing `report_week` is shown as a staleness notice.
- No live refresh, no interactivity, no production deployment.

## 12. Final status target

`phase5b_status: success`
