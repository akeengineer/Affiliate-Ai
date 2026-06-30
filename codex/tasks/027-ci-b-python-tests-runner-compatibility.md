# Task 027 - CI-B Python Tests Runner Compatibility

## 1. Purpose

Make the `Python Tests` GitHub Actions workflow runner-compatible by removing
operator-machine assumptions, without weakening the local operator workflow or
any security guardrail. This implements the fixes that Phase CI-A documented.

## 2. Scope

- Remove the unusable pip cache from the workflow.
- Derive the repo root from script location in the two runner-coupled scripts.
- Gate operator-only runtime checks (`sudo hermes`, git remote identity) behind
  an explicit env flag that defaults to a CI-safe mode.
- Update the affected Phase 2B tests and the CI-A tripwire test to cover both
  CI mode and operator mode.

## 3. Files

Change:

- `.github/workflows/python-tests.yml`
- `scripts/dev/check_hermes_runtime.sh`
- `scripts/tmux/start-affiliate-warroom.sh`
- `tests/test_phase2b_hermes_runtime.py`
- `tests/test_ci_a_runner_compatibility_plan.py`
- `codex/tasks/027-ci-b-python-tests-runner-compatibility.md`
- `docs/CI_RUNNER_COMPATIBILITY_PLAN.md` (minimal CI-B status note)

Do not change Phase 2/3/4/5 application logic. Do not modify
`tests/test_phase2c_warroom_proof.py`, `tests/test_phase1_smoke.py`, or
`tests/test_phase3b_portfolio_cli_dashboard.py`.

## 4. Hard constraints

- no business/scoring/import/report/dashboard/promotion/approval behavior change
- no relaxed security guardrails
- no broad test skipping; no loss of Phase 2B/2C coverage
- no database/backend/UI/API/external services
- no new dependencies; no `requirements.txt`/`pyproject.toml` added for cache
- no Hermes required in CI by default; no `sudo` in CI mode
- no Phase 5A doc change; no unnecessary CI-A doc rewrite

## 5. Runner compatibility design

- **Workflow:** remove `cache: "pip"` from `actions/setup-python`; there is no
  dependency lockfile to key the cache. Guarded install steps stay.
- **Repo-root derivation:** both scripts use
  `SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"` and
  `REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"`.
- **War-room default:** `PROJECT_DIR="${PROJECT_DIR:-$REPO_ROOT}"`; the env
  override is preserved. The hardcoded operator path is removed.

## 6. Operator-runtime mode

`scripts/dev/check_hermes_runtime.sh` reads
`REQUIRE_OPERATOR_RUNTIME="${AFFILIATE_REQUIRE_OPERATOR_RUNTIME:-false}"`.

- **CI/default mode (unset or false):** does not call `sudo` or `hermes` and
  does not require an operator git remote alias. It validates the static
  contract (derived repo root valid, smoke script present and executable) and
  enforces the autopublish guardrail, then prints
  `phase2b_runtime_check: ci-static` and exits 0.
- **Operator mode (`true`):** enforces portable repository identity, runs
  `sudo hermes skills list`, requires the `affiliate-growth-os`, `obsidian`, and
  `codex` skills, then prints `phase2b_runtime_check: success`.
- **All modes:** `ENABLE_AUTOPUBLISH=true` fails non-zero before any success.

Git remote check (operator mode) validates portable identity: it accepts any
SSH or HTTPS remote that identifies `akeengineer/Affiliate-Ai` (with or without
a `.git` suffix) and rejects anything that does not. It is not bound to a
machine-specific alias.

## 7. Test strategy

`tests/test_phase2b_hermes_runtime.py`:

- keep artifact existence checks
- CI-mode pass: flag unset, a `sudo` tripwire stub that fails if called; assert
  exit 0, `phase2b_runtime_check: ci-static`, and that `sudo` was never called
- operator-mode pass: flag true, `sudo` skills stub and a `git` stub returning a
  valid remote; assert exit 0 and `phase2b_runtime_check: success`
- operator-mode missing-skill fail: flag true, stub missing `codex`; assert
  non-zero
- autopublish guard: `ENABLE_AUTOPUBLISH=true` with flag unset; assert non-zero

`tests/test_ci_a_runner_compatibility_plan.py`: the CI-A tripwire is replaced by
a guard that confirms the war-room script now derives the repo root, defaults
`PROJECT_DIR` to it, and no longer contains the hardcoded operator path. CI-A
root-cause documentation tests are preserved.

## 8. Acceptance criteria

- Workflow no longer sets `cache: "pip"`.
- No `/home/ubuntu/Affiliate-Ai` remains in the two changed executable scripts.
- Phase 2B, Phase 2C, and CI-A tests pass.
- The CI-equivalent full suite passes with the operator flag unset.
- No business logic, scoring, or vault/approval behavior changed.

## 9. Verification commands

```
bash -n scripts/dev/check_hermes_runtime.sh
bash -n scripts/tmux/start-affiliate-warroom.sh
python -m pytest -q tests/test_phase2b_hermes_runtime.py
python -m pytest -q tests/test_phase2c_warroom_proof.py
python -m pytest -q tests/test_ci_a_runner_compatibility_plan.py
env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q
AFFILIATE_REQUIRE_OPERATOR_RUNTIME=true bash scripts/dev/check_hermes_runtime.sh
grep -R "/home/ubuntu/Affiliate-Ai" -n scripts/dev/check_hermes_runtime.sh scripts/tmux/start-affiliate-warroom.sh
```

## 10. Known limitations

- Operator mode still requires real `sudo`/Hermes on the operator machine; it is
  covered in CI only via stubs.
- A broad regression guard against reintroducing hardcoded paths in executable
  scripts is deferred to Phase CI-C.

## 11. Final status target

`ci_b_status: success`
