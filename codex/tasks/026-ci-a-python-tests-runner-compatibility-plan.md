# Task 026 - Phase CI-A Python Tests Runner Compatibility Plan

## 1. Purpose

Document why the `Python Tests` GitHub Actions workflow cannot pass on a generic
runner, and plan the portability fix, before any script or test code is changed.
This is a documentation and contract-test phase only. It does not modify any
runtime script, any operator script, or any test under `tests/`.

## 2. Background

The `Python Tests` workflow runs `python -m pytest` on every pull request. After
the pip-cache setup fix, the suite executes on the runner but fails:

```
6 failed, 362 passed
```

The failures are not logic regressions. They come from scripts and tests that
assume they run on the operator's machine at a fixed absolute path, with a
specific git remote, and with `sudo hermes` installed. On a GitHub runner the
checkout lives at `/home/runner/work/Affiliate-Ai/Affiliate-Ai`, so those
assumptions break.

## 3. Root causes

1. `scripts/tmux/start-affiliate-warroom.sh` defaults `PROJECT_DIR` to a
   hardcoded `/home/ubuntu/Affiliate-Ai`. On the runner the agent-prompt paths
   resolve under that nonexistent directory, so the script fails with
   `Missing agent prompt: /home/ubuntu/Affiliate-Ai/prompts/agents/...`. This
   fails the two `tests/test_phase2c_warroom_proof.py` tests.
2. `scripts/dev/check_hermes_runtime.sh` hardcodes
   `EXPECTED_REPO_ROOT="/home/ubuntu/Affiliate-Ai"`, requires a specific git
   remote, and shells out to `sudo hermes skills list`. None hold on the runner,
   so it exits with `Must run from /home/ubuntu/Affiliate-Ai`. This fails the
   three `tests/test_phase2b_hermes_runtime.py` tests.
3. `tests/test_phase1_smoke.py` runs the full suite again as a nested
   subprocess. That nested run inherits the two failures above and reports
   `pytest: failed`, so the smoke test fails too.

Total: 6 failing tests, all traceable to operator-machine coupling, not to any
feature logic.

## 4. Scope of this task

- Author this task contract.
- Author `docs/CI_RUNNER_COMPATIBILITY_PLAN.md` describing the root causes,
  the portability principles, and the proposed subphases.
- Author a docs-contract test that asserts the plan documents the root causes
  and subphases.
- Do not change any script under `scripts/`.
- Do not change any test that exercises a script.
- Do not change the workflow file in this task.
- Do not add a database, a dependency, or a runtime entry point.

## 5. Portability principles (to apply in later subphases)

- Derive the repo root from the script location
  (`SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"`,
  `REPO_ROOT="$SCRIPT_DIR/../.."`) instead of hardcoding an absolute path.
- Make `PROJECT_DIR` default to the derived repo root, keeping the env override.
- Make operator-only checks (`sudo hermes`, exact git remote, fixed path)
  opt-in, so they are skipped on CI and enforced only on the operator machine.
- Keep the nested-suite smoke test runnable on CI, or guard it behind the same
  operator-only flag.

## 6. Proposed subphases

- **Phase CI-A: this plan** — document root causes and portability principles
  (docs/tests only).
- **Phase CI-B: portability fixes** — derive repo root and default `PROJECT_DIR`
  from script location; gate operator-only checks behind an env flag.
- **Phase CI-C: CI verification** — confirm `Python Tests` is green on the
  runner and add a guard test that fails closed if a hardcoded
  `/home/ubuntu/Affiliate-Ai` reappears in tracked scripts.

## 7. Acceptance criteria

- This task file and `docs/CI_RUNNER_COMPATIBILITY_PLAN.md` exist.
- The plan documents the three root causes and the subphases.
- `tests/test_ci_a_runner_compatibility_plan.py` passes.
- No script change, no workflow change, and no operator/test script change in
  this task.

## 8. Verification commands

```
python -m pytest -q tests/test_ci_a_runner_compatibility_plan.py
git status --short --branch
```

## 9. Known limitations

- Plan only; no portability fix is applied here.
- The `Python Tests` workflow stays red until Phase CI-B lands.

## 10. Final status target

`phase_ci_a_status: success`
