# Task 032 - Phase 5D UI Shell Demo Bundle Command

## 1. Purpose

Provide one safe operator command that runs the complete local static UI shell
demo chain (Phase 4E -> Phase 5B -> Phase 5C) and writes a Phase 5D
summary/report. Orchestration only: no business logic, no backend, no vault
writes, no external services, no approved-workflow triggering. Phase 5C is
always run and never bypassed.

## 2. Scope

- A bash orchestrator that runs the three real safe wrappers in order and
  captures each step result and the Phase 5C verdict.
- A Python stdlib summary writer that owns the verdict-to-status mapping and
  writes outputs under `tmp/phase5d-ui-shell-demo/`.
- Docs and tests. No change to Phase 4E/5B/5C behavior.

## 3. Files

- `codex/tasks/032-phase5d-ui-shell-demo-command.md`
- `scripts/dev/run_phase5d_ui_shell_demo.sh`
- `scripts/dev/build_ui_shell_demo_summary.py`
- `tests/test_phase5d_ui_shell_demo_command.py`
- `docs/UI_SHELL.md` (Phase 5D section)
- `.gitignore` (+ `tmp/phase5d-ui-shell-demo/`)
- `scripts/dev/README.md` (one index entry)

## 4. Command design

```
bash scripts/dev/run_phase5d_ui_shell_demo.sh <week>
```

One `<week>` arg validated against `^[0-9]{4}-W[0-9]{2}$`; rejects guardrail
flags; derives repo root and `cd "$REPO_ROOT"`; selects
`.venv/bin/python` -> `python3` -> `python`. Runs:

```
bash scripts/dev/run_phase4e_demo_bundle.sh "$WEEK"
bash scripts/dev/run_phase5b_ui_shell.sh "$WEEK"
bash scripts/dev/run_phase5c_ui_shell_verifier.sh
```

Each step prints `ui_shell_demo_step: <phase> -> PASS|FAIL`. The final
status/exit decision is delegated to `build_ui_shell_demo_summary.py`, which
reads the Phase 5C verdict from its summary JSON when not passed `--verdict`.

## 5. Data sources

Reads local summary files only: `demo-bundle-summary.json` (Phase 4E) and
`verification-summary.json` (Phase 5C, authoritative verdict). Existence checks
only for `tmp/phase5b-ui-shell/index.html` and the Phase 5C report. Never reads
the vault, raw scores, Phase 3 artifacts, raw Phase 4 HTML, or the Phase 5B
shell body.

## 6. Output structure

`tmp/phase5d-ui-shell-demo/ui-shell-demo-summary.json` (`type`,
`report_week`, `generated_at`, `steps{}`, `ui_shell_verdict`, `status`,
`phase5d_status`, `artifacts{}`, `guardrails{}`) and
`tmp/phase5d-ui-shell-demo/UI_SHELL_DEMO.md` (title, week, commands run, step
statuses, verdict, demo status, artifacts, how-to-open, guardrail footer).

## 7. Guardrails

- rejects `ENABLE_AUTOPUBLISH`, `ENABLE_OPENAI_API_DIRECT`, `APPROVE_PROMOTE`,
  `APPROVE_DECISION`, `APPROVE_FINALIZE`
- writes only under `tmp/phase5d-ui-shell-demo/` (guarded output dir)
- output self-safety: both files are scanned before write; no external URL,
  `file://`, operator path, vault path, affiliate/secret marker, approved-
  workflow name, or script/JS markup may appear
- `cd "$REPO_ROOT"` (cross-CWD safe); no network; no hardcoded operator path
- calls only the three safe wrappers; never `run_phase2g/h/i`,
  `promote_product_candidates.py`, `create_decision.py`, `finalize_decision.py`
- Phase 5C is always run; never bypassed
- self-reference: operator-path and approved-workflow denylist tokens are
  composed so no contiguous literal appears in source

## 8. Verdict/status policy

```
verdict ready   + all steps PASS -> status ready,   phase5d_status success, exit 0
verdict warning + all steps PASS -> status warning, phase5d_status success, exit 0
verdict failed  or any step FAIL -> status failed,  phase5d_status failed,  exit 1
```

`warning` is success, not a failure. The mapping lives in
`build_ui_shell_demo_summary.py` and is unit-testable in isolation.

## 9. Test strategy

Deterministic pytest with no network/Hermes/sudo: existence + executability +
`bash -n` + `py_compile`; `.gitignore`; invalid week / wrong arg count;
guardrail flags; end-to-end ready; summary/report content; output self-safety;
verdict-mapping unit tests (`ready`/`warning`/`failed`/step-FAIL) via the writer;
failed path; no-bypass of Phase 5C; cross-CWD; CI-C alignment; static boundary
(no approved-workflow refs in orchestrator/writer source).

## 10. Acceptance criteria

- `run_phase5d_ui_shell_demo.sh 2026-W26` exits 0 and prints the three step PASS
  lines, `ui_shell_verdict: ready`, `ui_shell_demo_status: ready`, and
  `phase5d_status: success`; both outputs exist with `status: ready`.
- Writer maps `warning` -> success/exit 0 and `failed`/step-FAIL -> failed/exit 1.
- Focused Phase 5D, Phase 5C, Phase 5B, and CI-C tests pass; full suite passes.
- No hardcoded operator path in scripts.

## 11. Verification commands

```
bash -n scripts/dev/run_phase5d_ui_shell_demo.sh
python -m py_compile scripts/dev/build_ui_shell_demo_summary.py
python -m pytest -q tests/test_phase5d_ui_shell_demo_command.py
python -m pytest -q tests/test_phase5c_ui_shell_verifier.py tests/test_phase5b_local_static_ui_shell_prototype.py tests/test_ci_c_runner_regression_guards.py
bash scripts/dev/run_phase5d_ui_shell_demo.sh 2026-W26
env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q
grep -RIn "/home/ubuntu/Affiliate-Ai" scripts/ || echo "scripts clean"
```

## 12. Known limitations

- A clean fresh chain yields `ready`; `warning`/`failed` verdicts are defensive
  branches, exercised deterministically via the writer's unit tests rather than
  through the fresh chain.
- Reads local summary files only; does not re-verify Phase 4/5B/5C internals.

## 13. Final status target

`phase5d_status: success`
