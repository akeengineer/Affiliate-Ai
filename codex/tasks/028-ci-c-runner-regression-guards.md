# Task 028 - CI-C Runner Regression Guards

## 1. Purpose

Add regression guards that prevent the CI-B runner-compatibility fixes from
silently regressing. CI-C is a guard-only phase: it adds tests, a task contract,
and a minimal docs note. It does not change runtime behavior unless a guard
exposes a very small, clear bug.

## 2. Scope

- Add `tests/test_ci_c_runner_regression_guards.py` with structural guards over
  the workflow and the two CI-B scripts.
- Add this task contract.
- Add a minimal `## 11. CI-C guard policy` section to the CI compatibility doc.

## 3. Files

Create:

- `tests/test_ci_c_runner_regression_guards.py`
- `codex/tasks/028-ci-c-runner-regression-guards.md`

Modify (minimal):

- `docs/CI_RUNNER_COMPATIBILITY_PLAN.md`

Do not modify runtime files unless a guard reveals a real bug:
`.github/workflows/python-tests.yml`, `scripts/dev/check_hermes_runtime.sh`,
`scripts/tmux/start-affiliate-warroom.sh`, or any Phase 2/3/4/5 runtime script.
Do not modify `tests/test_phase1_smoke.py`.

## 4. Hard constraints

- no business/scoring/import/report/dashboard/promotion/approval behavior change
- no Phase 4/5 demo behavior change
- no CI-B runtime change unless a clear bug is found
- no broad test skips; no weakened operator-runtime checks
- no Hermes required on the GitHub runner
- no new dependencies; no backend/UI/database/API
- docs/tests negative fixtures must not be scanned as runtime leaks

## 5. Regression guard policy

The guards are intentional, format-sensitive tripwires. If a future change edits
a CI-B script or the workflow, the corresponding guard must be updated in the
same change. Guards are static (read files, assert structure); they do not run
Hermes, `sudo`, or any network call.

## 6. Paths scanned and paths excluded

- **Hardcoded path guard:** scans `scripts/**/*.sh` and `scripts/**/*.py` only.
- **No-network guard:** scans only `scripts/dev/check_hermes_runtime.sh` and
  `scripts/tmux/start-affiliate-warroom.sh`.
- **No-broad-skip guard:** scans `tests/*.py` and the workflow.
- **Excluded:** `docs/`, `codex/tasks/`, `prompts/`, and test negative fixtures
  (e.g. `tests/test_phase3b_portfolio_cli_dashboard.py`). The CI-C guard file
  itself is excluded from selector scans because it names selectors as data.

## 7. Guard list

1. Workflow cache: no `cache: pip` (any quoting) without a dependency lockfile;
   workflow still runs `python -m pytest`.
2. Hardcoded operator path: no `/home/ubuntu/Affiliate-Ai` in executable scripts
   under `scripts/`.
3. Operator-runtime gate: `AFFILIATE_REQUIRE_OPERATOR_RUNTIME` present, defaults
   to `false`, CI-static output and an `exit 0` precede `sudo hermes`.
4. Repo-root derivation: both CI-B scripts derive `SCRIPT_DIR`/`REPO_ROOT`;
   war-room defaults `PROJECT_DIR` to `$REPO_ROOT` while preserving the override.
5. No broad skip: banned `-k` exclusions of runner-compat tests are absent;
   `not phase1_smoke` is allowed only in `tests/test_phase1_smoke.py`; the
   workflow has no `-k`/`--ignore`/`-m` exclusions.
6. No network: no `curl`/`wget`/`nc`/`netcat`/`http(s)://` in the two scripts.
7. Operator-mode preservation: `sudo hermes skills list` and the required skills
   (`affiliate-growth-os`, `obsidian`, `codex`) remain.

## 8. Acceptance criteria

- `tests/test_ci_c_runner_regression_guards.py` passes.
- Phase 2B and CI-A tests still pass.
- The full suite passes in CI/default mode.
- No runtime file changed.

## 9. Verification commands

```
python -m pytest -q tests/test_ci_c_runner_regression_guards.py
python -m pytest -q tests/test_phase2b_hermes_runtime.py tests/test_ci_a_runner_compatibility_plan.py
env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q
grep -RIn "/home/ubuntu/Affiliate-Ai" scripts/ || echo "scripts clean"
git status --short --branch
```

## 10. Known limitations

- Guards are format-sensitive by design; reformatting a CI-B script requires a
  matching guard update.
- Guards assert structure, not live runtime; operator mode is exercised
  behaviorally by the Phase 2B stub tests, which CI-C does not duplicate.

## 11. Final status target

`ci_c_status: success`
