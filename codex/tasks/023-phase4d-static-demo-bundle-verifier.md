# Task 023 - Phase 4D Static Demo Bundle Verifier

## 1. Purpose

Provide a read-only verifier that checks whether the static demo bundle from
Phase 4B (snapshot) and Phase 4C (catalog) is safe, internally consistent, and
ready to share. It is a gate, not a builder: it never regenerates the bundle,
reads no vault, writes no vault, and copies no raw artifacts.

## 2. Scope

- Verify Phase 4B `tmp/phase4b-ui-snapshot/` and Phase 4C
  `tmp/phase4c-snapshot-catalog/`.
- Recompute manifest hashes/bytes, confirm catalog↔snapshot consistency, resolve
  relative links, and run safety scans.
- Write `verification-report.md` and `verification-summary.json` under
  `tmp/phase4d-demo-verifier/`.

## 3. Files

Create:

- `codex/tasks/023-phase4d-static-demo-bundle-verifier.md`
- `scripts/dev/verify_demo_bundle.py`
- `scripts/dev/run_phase4d_demo_verifier.sh`
- `tests/test_phase4d_static_demo_bundle_verifier.py`

Modify:

- `.gitignore` (add `tmp/phase4d-demo-verifier/`)
- `scripts/dev/README.md` (script index entry)

Do not modify Phase 2 or Phase 3A/3B/3C/3D/3E or Phase 4A/4B/4C workflows unless
a real bug is found.

## 4. Verification rules

- Phase 4B contains exactly its five files; manifest is valid JSON with type
  `phase4b_ui_snapshot`, `vault_included: false`, and files[] hashes/bytes that
  match the actual files.
- Phase 4C contains exactly its four files; catalog is valid JSON with type
  `phase4c_snapshot_catalog`, at least one snapshot, an entry with
  `source_dir == tmp/phase4b-ui-snapshot` whose `index_sha256` matches the
  Phase 4B `index.html` hash.
- The Phase 4C relative link to `../phase4b-ui-snapshot/index.html` resolves.
- No bundle/output file contains external URL schemes, private vault paths,
  affiliate URL patterns, secrets, or content-field markers (the policy phrase
  `no autopublish` is allowed; `content_draft`/`campaign_copy`/`tiktok_script`/
  `hook_text`/`blog_post` are blocked).
- No raw artifact files (dashboard-*.md, portfolio-*.md, disallowed JSON, vault
  files) exist in the 4B/4C/4D directories.

## 5. Hard constraints

- no database, FastAPI, backend service, external APIs, external URLs, affiliate
  content, autopublish, campaign launch, vault reads, vault writes, approval
  mutation, Phase 2G/2H/2I triggering, marketplace connector, or raw artifact
  export.
- read-only only; verifier only.

## 6. Acceptance criteria

- `verify_demo_bundle.py` compiles; `run_phase4d_demo_verifier.sh` passes
  `bash -n`, is executable, and runs from a clean repo.
- On a valid bundle: exit 0, verdict ready, `verification-summary.json` with
  `status: success` and the documented structure, `verification-report.md` with
  a verification table.
- On any failed check (missing input, hash mismatch, broken reference, unsafe
  content, raw artifacts, `vault_included: true`): exit non-zero.
- The verifier's own output passes the same safety scan (class-name findings
  only; no echoed offending content).
- No vault reads or writes; output written only under a guarded
  `tmp/phase4d-demo-verifier/`; idempotent.

## 7. Verification commands

```
python -m py_compile scripts/dev/verify_demo_bundle.py
bash -n scripts/dev/run_phase4d_demo_verifier.sh
bash scripts/dev/run_phase4b_ui_snapshot.sh 2026-W26
bash scripts/dev/run_phase4c_snapshot_catalog.sh
bash scripts/dev/run_phase4d_demo_verifier.sh
find tmp/phase4d-demo-verifier -maxdepth 1 -type f -print | sort
python -m pytest -q tests/test_phase4d_static_demo_bundle_verifier.py
python -m pytest -q
```

## 8. Known limitations

- The verifier checks the existing generated bundle only; it does not regenerate
  Phase 4B or Phase 4C.
- Stale input remains stale until upstream phases are rebuilt.
- `verification-summary.json` carries a `generated_at` timestamp, so it is not
  byte-identical across runs.

## 9. Final status target

`phase4d_status: success`
