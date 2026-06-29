# Task 019 - Phase 3E Release Snapshot / Project State Report

## 1. Purpose

Produce release-ready documentation that summarizes the current system state,
capabilities, operator commands, guardrails, limitations, and roadmap as a
Phase 3 release freeze. Add docs-contract tests and a read-only convenience
script. No business logic and no workflow changes.

## 2. Scope

- Author `docs/PROJECT_STATE.md`, `docs/RELEASE_SNAPSHOT_PHASE3.md`,
  `docs/ROADMAP.md`.
- Add `scripts/dev/show_release_snapshot.sh` (read-only: prints
  `docs/PROJECT_STATE.md`, then live `command_center.sh status`).
- Add `tests/test_phase3e_release_snapshot.py` (docs-contract).
- Add one `scripts/dev/README.md` index line.

## 3. Files

Create:

- `codex/tasks/019-phase3e-release-snapshot.md`
- `docs/PROJECT_STATE.md`
- `docs/RELEASE_SNAPSHOT_PHASE3.md`
- `docs/ROADMAP.md`
- `tests/test_phase3e_release_snapshot.py`
- `scripts/dev/show_release_snapshot.sh`

Modify:

- `scripts/dev/README.md`

Do not modify `.gitignore`, Phase 2 workflows, or Phase 3A/3B/3C/3D workflows
unless a real bug is found.

## 4. Hard constraints

- no database
- no FastAPI
- no UI implementation
- no external APIs
- no affiliate content generation
- no autopublish
- no campaign launch
- no vault writes
- no new business logic
- no `.gitignore` modification (no new tmp directory introduced)

## 5. Acceptance criteria

- All three docs and the task file exist.
- `show_release_snapshot.sh` is executable, passes `bash -n`, exits 0, prints the
  project state followed by live `command_center.sh status` (`status_command: success`).
- `PROJECT_STATE.md` documents architecture, operator commands, the artifact map
  (tmp / vault / docs / scripts), all eight guardrails, capabilities, gaps,
  limitations, and security posture.
- `RELEASE_SNAPSHOT_PHASE3.md` includes the Phase 1 → 3D matrix and the expected
  acceptance output tokens.
- `ROADMAP.md` includes Phase 4A/4B/4C/5 and the read-only / manual-approved
  principles.
- The docs-contract test suite passes; the full suite stays green.
- No vault writes occur during any of the above.

## 6. Verification commands

```
bash -n scripts/dev/show_release_snapshot.sh
bash scripts/dev/show_release_snapshot.sh
source .venv/bin/activate && python -m pytest -q tests/test_phase3e_release_snapshot.py
source .venv/bin/activate && python -m pytest -q
```

## 7. Known limitations

- Docs are a point-in-time snapshot; dynamic facts (e.g. exact test count) are
  intentionally not asserted to avoid drift.
- `show_release_snapshot.sh` reflects the live tmp state via `status`, which is a
  snapshot and not week-scoped.
- The release is documentation-only; it adds no new runtime capability.

## 8. Final status target

`phase3e_status: documentation_release_complete`
