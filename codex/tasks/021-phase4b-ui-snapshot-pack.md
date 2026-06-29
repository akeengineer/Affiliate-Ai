# Task 021 - Phase 4B UI Snapshot Pack / Demo Export

## 1. Purpose

Package the Phase 4A static UI mock into a deterministic, read-only local
snapshot folder with supporting demo metadata (manifest, README, inventory,
guardrail statement). It is a packaging/export layer only — no server, backend,
database, external APIs, vault access, or approval mutation.

## 2. Scope

- Regenerate the Phase 4A mock first (safe source path), then copy only the
  scrubbed static `index.html` into the snapshot.
- Write `manifest.json`, `README.md`, `INVENTORY.md`, `GUARDRAILS.md`.
- Never copy raw score JSON, Phase 3A markdown, Phase 3B markdown, or vault files.

## 3. Files

Create:

- `codex/tasks/021-phase4b-ui-snapshot-pack.md`
- `scripts/dev/build_ui_snapshot.py`
- `scripts/dev/run_phase4b_ui_snapshot.sh`
- `tests/test_phase4b_ui_snapshot_pack.py`

Modify:

- `.gitignore` (add `tmp/phase4b-ui-snapshot/`)
- `scripts/dev/README.md` (script index entry)

Do not modify Phase 2 or Phase 3A/3B/3C/3D/3E or Phase 4A workflows unless a
real bug is found.

## 4. Data sources

Read-only:

- `tmp/phase4a-ui/index.html` (after regeneration)
- presence of `tmp/phase3b-portfolio-dashboard/portfolio-<week>.md`
- count of `tmp/phase3a-dashboard/dashboard-*-<week>.md`
- count of `tmp/phase2e-import-score-report/scores/*.json`

The vault is never read. Only the copied static HTML carries artifact-derived
content; everything else is a summary.

## 5. Hard constraints

- no database, FastAPI, backend service, external APIs, external URLs, affiliate
  content, autopublish, campaign launch, vault writes, approval mutation,
  Phase 2G/2H/2I triggering, or marketplace connector.
- read-only only; no raw artifact export except the copied static HTML mock.

## 6. Acceptance criteria

- `build_ui_snapshot.py` compiles; `run_phase4b_ui_snapshot.sh` passes `bash -n`,
  is executable, and runs from a clean repo.
- The snapshot folder contains exactly: `index.html`, `manifest.json`,
  `README.md`, `INVENTORY.md`, `GUARDRAILS.md`.
- `index.html` is byte-identical to the regenerated Phase 4A mock.
- `manifest.json` is valid JSON with `type: phase4b_ui_snapshot`, `report_week`,
  `generated_at`, `files[]` (name/sha256/bytes matching the written files), and
  `source_summary` including `vault_included: false`.
- Every snapshot file is free of vault paths, affiliate URLs, secrets, affiliate
  content fields, and external URLs (`http://`/`https://`); failure aborts non-zero.
- Missing artifacts still produce a degraded snapshot, exit 0.
- Invalid week and unsafe guardrail flags fail non-zero.
- No vault writes occur; cleanup removes only known snapshot files under a guarded
  output directory.

## 7. Verification commands

```
python -m py_compile scripts/dev/build_ui_snapshot.py
bash -n scripts/dev/run_phase4b_ui_snapshot.sh
bash scripts/dev/run_phase3d_acceptance.sh
bash scripts/dev/run_phase4a_ui_mock.sh 2026-W26
bash scripts/dev/run_phase4b_ui_snapshot.sh 2026-W26
find tmp/phase4b-ui-snapshot -maxdepth 1 -type f -print | sort
python -m pytest -q tests/test_phase4b_ui_snapshot_pack.py
python -m pytest -q
```

## 8. Known limitations

- Static snapshot; stale if upstream artifacts are stale; no interactivity.
- `manifest.json` carries a `generated_at` timestamp, so it is not byte-identical
  across rebuilds.
- Regenerating the Phase 4A mock writes `tmp/phase4a-ui/` as a side effect (tmp
  only, gitignored).

## 9. Final status target

`phase4b_status: success`
