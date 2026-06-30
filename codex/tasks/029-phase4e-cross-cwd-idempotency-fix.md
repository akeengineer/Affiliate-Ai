# Task 029 - Phase 4E Demo Bundle Cross-CWD Idempotency Fix

## 1. Purpose

Fix a portability bug where the Phase 4E static demo chain fails when invoked
from a working directory other than the repository root. The chain must rebuild
the Phase 2E artifacts deterministically from any CWD.

## 2. Scope

- Normalize the working directory in the two operator entrypoints so relative
  sample paths resolve against the repo root.
- Add cross-CWD regression coverage.
- No business, scoring, import/report/dashboard, vault, or approval behavior
  change.

## 3. Root cause

`run_phase3d_acceptance.sh` and `run_phase4e_demo_bundle.sh` derive `REPO_ROOT`
but do not `cd "$REPO_ROOT"` before invoking downstream wrappers. The dry-run
chain (`command_center.sh dry-run` -> `run_phase2_full_dry_run.sh` ->
`run_phase2e_import_score_report.sh` -> `import_product_candidates.py`) resolves
the relative sample CSV `vault/samples/import/product-candidates.csv` against the
caller CWD. Invoked from outside the repo root, the import cannot find the CSV,
so `tmp/phase2e-import-score-report/scores/prod-laptop-stand.json` is never
rebuilt and the acceptance step fails. `run_phase4a_ui_mock.sh` already uses the
correct precedent: derive the repo root, then `cd "$REPO_ROOT"`.

## 4. Files

- `scripts/dev/run_phase3d_acceptance.sh`
- `scripts/dev/run_phase4e_demo_bundle.sh`
- `tests/test_phase4e_demo_bundle_command.py`
- `codex/tasks/029-phase4e-cross-cwd-idempotency-fix.md`

`command_center.sh` is intentionally not changed; the two-entrypoint fix is
sufficient.

## 5. Fix design

Add `cd "$REPO_ROOT"` after argument validation and guardrails, before any
downstream wrapper call:

- `run_phase3d_acceptance.sh`: after the command-center existence check, before
  the before-snapshot and `run_step` calls.
- `run_phase4e_demo_bundle.sh`: after week validation, guardrail checks, and
  wrapper existence checks, before the first demo `run_step`.

All in-script paths are anchored to `$REPO_ROOT` (absolute), so the `cd` only
makes relative downstream resolution consistent; it changes no existing
behavior when already run from the repo root.

## 6. Acceptance criteria

- Running `scripts/dev/run_phase4e_demo_bundle.sh 2026-W26` from a CWD outside
  the repo root (via absolute script path) exits 0 and reports all demo steps
  PASS, `demo_bundle_status: ready`, and `phase4e_status: success`.
- `tmp/phase2e-import-score-report/scores/prod-laptop-stand.json` is rebuilt.
- Phase 4E, Phase 3D, and Phase 2E focused tests pass.
- Full suite passes in CI/default mode.
- No hardcoded `/home/ubuntu/Affiliate-Ai` in scripts; CI-C guard stays clean.

## 7. Verification commands

```
bash -n scripts/dev/run_phase3d_acceptance.sh
bash -n scripts/dev/run_phase4e_demo_bundle.sh
cd /home/ubuntu/Affiliate-Ai && rm -rf tmp
cd /tmp && bash /home/ubuntu/Affiliate-Ai/scripts/dev/run_phase4e_demo_bundle.sh 2026-W26
cd /home/ubuntu/Affiliate-Ai
python -m pytest -q tests/test_phase4e_demo_bundle_command.py
python -m pytest -q tests/test_phase3d_operator_acceptance_pack.py tests/test_phase2e_import_score_report.py
env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q
grep -RIn "/home/ubuntu/Affiliate-Ai" scripts/ || echo "scripts clean"
```

## 8. Known limitations

- The fix normalizes CWD in the two operator entrypoints only; deeper wrappers
  still assume repo-root-relative inputs by design. `command_center.sh` is
  unchanged.

## 9. Final status target

`phase4e_cross_cwd_fix_status: success`
