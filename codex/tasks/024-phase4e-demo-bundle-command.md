# Task 024 - Phase 4E Static Demo Bundle Operator Command

## 1. Purpose

Provide a single operator command that safely runs the existing static demo
chain end-to-end (Phase 3D acceptance → 4B snapshot → 4C catalog → 4D verifier)
and writes a concise operator summary. Orchestration only: no new business
logic, UI, backend, artifact semantics, or approval routing.

## 2. Scope

- Validate inputs and guardrail flags, then run the four existing safe wrappers
  in order, requiring each step's success token.
- On full success, write `demo-bundle-summary.json` and `DEMO_BUNDLE.md` under
  `tmp/phase4e-demo-bundle/` and print a concise status.
- On any step failure, fail non-zero without writing the summary.

## 3. Files

Create:

- `codex/tasks/024-phase4e-demo-bundle-command.md`
- `scripts/dev/run_phase4e_demo_bundle.sh`
- `tests/test_phase4e_demo_bundle_command.py`

Modify:

- `.gitignore` (add `tmp/phase4e-demo-bundle/`)
- `scripts/dev/README.md` (script index entry)

Do not modify Phase 2 or Phase 3A/3B/3C/3D/3E or Phase 4A/4B/4C/4D workflows
unless a real bug is found.

## 4. Command

```
bash scripts/dev/run_phase4e_demo_bundle.sh <YYYY-Www>
```

## 5. Orchestration sequence

1. `run_phase3d_acceptance.sh` → require `acceptance_status: success`
2. `run_phase4b_ui_snapshot.sh <week>` → require `phase4b_status: success`
3. `run_phase4c_snapshot_catalog.sh` → require `phase4c_status: success`
4. `run_phase4d_demo_verifier.sh` → require `phase4d_status: success`

## 6. Guardrails

- Validate `week` (`^[0-9]{4}-W[0-9]{2}$`).
- Fail if any of `ENABLE_AUTOPUBLISH`, `ENABLE_OPENAI_API_DIRECT`,
  `APPROVE_PROMOTE`, `APPROVE_DECISION`, `APPROVE_FINALIZE` is `true`.
- Call only the four allowed wrappers; never reference 2G/2H/2I or approved
  scripts; never use curl/wget/nc or external URLs.
- Write only under a guarded `tmp/phase4e-demo-bundle/`; no vault writes.
- Output files must contain no external URLs, vault paths, secrets, affiliate
  URLs, or content markers (self-safety grep guard).

## 7. Acceptance criteria

- `run_phase4e_demo_bundle.sh` passes `bash -n`, is executable, runs from a
  clean repo, and on success exits 0 with the documented stdout and exactly two
  output files.
- `demo-bundle-summary.json` is valid JSON with `type: phase4e_demo_bundle`,
  `status: ready`, the input `report_week`, all steps PASS, the Phase 4B/4C/4D
  artifact paths, and the guardrail booleans.
- `DEMO_BUNDLE.md` documents status, week, commands run, demo outputs,
  verification outputs, guardrails, and known limitations.
- Invalid week and unsafe guardrail flags fail non-zero.
- No vault writes; idempotent overwrite.

## 8. Verification commands

```
bash -n scripts/dev/run_phase4e_demo_bundle.sh
bash scripts/dev/run_phase4e_demo_bundle.sh 2026-W26
find tmp/phase4e-demo-bundle -maxdepth 1 -type f -print | sort
python -m pytest -q tests/test_phase4e_demo_bundle_command.py
python -m pytest -q
```

## 9. Known limitations

- The chain runs the real acceptance/snapshot/catalog/verifier steps (tmp-only),
  so it takes several seconds.
- `generated_at` makes the summary non-byte-deterministic.
- A forced mid-chain step failure is not injected in tests (the failure branch
  is covered via guardrail non-zero paths); sub-wrappers are not modified to test.
- Static snapshot only; stale until rebuilt; no live refresh.

## 10. Final status target

`phase4e_status: success`
