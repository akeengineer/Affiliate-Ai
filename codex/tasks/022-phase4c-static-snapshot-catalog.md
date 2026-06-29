# Task 022 - Phase 4C Static UI Snapshot Catalog / Multi-snapshot Index

## 1. Purpose

Provide a static, read-only catalog/index over Phase 4B UI snapshot manifests.
It summarizes snapshot metadata only — no backend, server, UI shell, router, or
approval surface, and no copying of snapshot files or raw artifacts.

## 2. Scope

- Scan `tmp/phase4b-ui-snapshot*/manifest.json` (metadata only).
- Support zero, one, or multiple snapshots.
- Generate `index.html`, `catalog.json`, `README.md`, `GUARDRAILS.md`.
- Skip malformed/unsafe manifests; never read the vault or raw artifacts.

## 3. Files

Create:

- `codex/tasks/022-phase4c-static-snapshot-catalog.md`
- `scripts/dev/build_snapshot_catalog.py`
- `scripts/dev/run_phase4c_snapshot_catalog.sh`
- `tests/test_phase4c_static_snapshot_catalog.py`

Modify:

- `.gitignore` (add `tmp/phase4c-snapshot-catalog/`)
- `scripts/dev/README.md` (script index entry)

Do not modify Phase 2 or Phase 3A/3B/3C/3D/3E or Phase 4A/4B workflows unless a
real bug is found.

## 4. Data sources

Read-only: `tmp/phase4b-ui-snapshot*/manifest.json`.

Never read: the vault, score JSON, Phase 3A/3B markdown, or Phase 4B `index.html`
body. Never copy any snapshot file.

## 5. Hard constraints

- no database, FastAPI, backend service, external APIs, external URLs, affiliate
  content, autopublish, campaign launch, vault reads, vault writes, approval
  mutation, Phase 2G/2H/2I triggering, marketplace connector, or raw artifact
  export.
- read-only only; static files only.

## 6. Acceptance criteria

- `build_snapshot_catalog.py` compiles; `run_phase4c_snapshot_catalog.sh` passes
  `bash -n`, is executable, and runs from a clean repo.
- The catalog folder contains exactly: `index.html`, `catalog.json`, `README.md`,
  `GUARDRAILS.md`.
- `catalog.json` is valid JSON with `type: phase4c_snapshot_catalog`,
  `generated_at`, `snapshot_count`, `skipped_count`, and `snapshots[]` carrying
  per-snapshot metadata (source_dir, report_week, generated_at, file_count,
  total_bytes, index_sha256, source_summary with `vault_included: false`).
- Manifests are scanned via glob; malformed or `vault_included: true` manifests
  are skipped and counted.
- `index.html` is self-contained (no external URLs/script/fetch/link); snapshot
  links are relative local hrefs only.
- No snapshot/raw artifact files are copied into the catalog.
- Every catalog file is free of vault paths, affiliate URLs, secrets, content
  fields, and external URLs; failure aborts non-zero.
- No vault reads or writes occur; cleanup removes only known catalog files under
  a guarded output directory.

## 7. Verification commands

```
python -m py_compile scripts/dev/build_snapshot_catalog.py
bash -n scripts/dev/run_phase4c_snapshot_catalog.sh
bash scripts/dev/run_phase4b_ui_snapshot.sh 2026-W26
bash scripts/dev/run_phase4c_snapshot_catalog.sh
find tmp/phase4c-snapshot-catalog -maxdepth 1 -type f -print | sort
python -m pytest -q tests/test_phase4c_static_snapshot_catalog.py
python -m pytest -q
```

## 8. Known limitations

- The catalog uses existing manifests; it does not regenerate snapshots.
- It is stale if the snapshot manifests are stale; no live refresh.
- `catalog.json` carries a `generated_at` timestamp, so it is not byte-identical
  across rebuilds.
- There is no UI shell, router, or approval action.

## 9. Final status target

`phase4c_status: success`
