# Python Tests Runner Compatibility Plan (Phase CI-A)

## 1. Purpose

Explain why the `Python Tests` workflow fails on a generic GitHub runner and
plan the portability fix before changing any code. This document is a plan and
boundary contract only. It changes no script and no test that exercises a
script.

## 2. Current state

- The pip-cache setup error is fixed, so pytest now runs on the runner.
- The run reports `6 failed, 362 passed`.
- All six failures come from operator-machine coupling, not from feature logic.

## 3. Root causes

### 3.1 Hardcoded `PROJECT_DIR` in the war-room script

`scripts/tmux/start-affiliate-warroom.sh` sets:

```
PROJECT_DIR="${PROJECT_DIR:-/home/ubuntu/Affiliate-Ai}"
```

On the runner the checkout is at `/home/runner/work/Affiliate-Ai/Affiliate-Ai`,
so agent-prompt paths resolve under a directory that does not exist and the
script fails with:

```
Missing agent prompt: /home/ubuntu/Affiliate-Ai/prompts/agents/product-miner-agent.md
```

This fails the two `tests/test_phase2c_warroom_proof.py` tests.

### 3.2 Operator-only guards in the Hermes runtime check

`scripts/dev/check_hermes_runtime.sh`:

- hardcodes `EXPECTED_REPO_ROOT="/home/ubuntu/Affiliate-Ai"`,
- requires a specific `origin` git remote, and
- runs `sudo hermes skills list`.

None of these hold on a runner, so it exits with `Must run from
/home/ubuntu/Affiliate-Ai`. This fails the three
`tests/test_phase2b_hermes_runtime.py` tests.

### 3.3 Nested full-suite smoke test

`tests/test_phase1_smoke.py` runs the whole suite again as a subprocess. That
nested run inherits the two failures above, reports `pytest: failed`, and the
smoke test fails too.

## 4. Portability principles

- Derive the repo root from the script location, never from a hardcoded
  absolute path:
  - `SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"`
  - `REPO_ROOT="$SCRIPT_DIR/../.."`
- Default `PROJECT_DIR` to the derived repo root while keeping the env override.
- Make operator-only checks (`sudo hermes`, exact git remote, fixed path)
  opt-in via an env flag so they are skipped on CI and enforced on the operator
  machine.
- Keep the nested smoke test runnable on CI, or guard it behind the same flag.

## 5. Subphases

- **Phase CI-A (this plan):** document root causes and principles. Docs/tests
  only.
- **Phase CI-B:** apply portability fixes to the two scripts and adjust the
  affected tests. Make `Python Tests` able to pass on the runner.
- **Phase CI-C:** verify `Python Tests` is green and add a guard test that fails
  closed if a hardcoded `/home/ubuntu/Affiliate-Ai` reappears in tracked
  scripts.

## 6. Non-goals

- No script change in this phase.
- No workflow change in this phase.
- No new dependency, database, or runtime entry point.
- No change to business logic or scoring.

## 7. Risks

- **Scope creep into a rewrite** — keep CI-B limited to repo-root derivation and
  an opt-in operator flag.
- **Silently disabling operator safety checks** — the operator-only guards must
  still run on the operator machine; CI-B only gates them, it does not delete
  them.
- **Regression in the smoke test** — keep one runnable check that the nested run
  still passes on the runner.

## 8. Acceptance for this plan

- This document and the Phase CI-A task file exist.
- The three root causes and the subphases are documented.
- `tests/test_ci_a_runner_compatibility_plan.py` passes.
- No script, workflow, or operator/test script changed in this phase.

## 9. Known limitations

- Plan only; `Python Tests` stays red until Phase CI-B lands.

## 10. CI-B status

Phase CI-B implements the fixes documented above:

- removes the unusable `cache: "pip"` from the `Python Tests` workflow,
- derives the repo root from script location in
  `scripts/dev/check_hermes_runtime.sh` and
  `scripts/tmux/start-affiliate-warroom.sh`,
- gates operator-only runtime checks behind
  `AFFILIATE_REQUIRE_OPERATOR_RUNTIME` (CI-safe default), and
- validates portable git remote identity instead of a machine-specific alias.

Phase CI-C will add regression guards against reintroduced hardcoded paths in
executable scripts and confirm the runner is green.
