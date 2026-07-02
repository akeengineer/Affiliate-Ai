# Task 058 — Phase 8G Export Integrity Verifier Prototype

phase8g_status: success

phase7d_runtime_readiness: implemented_manual_gate

durable_audit_store_status: export_integrity_verifier

signing_implementation_status: not_implemented

## Purpose

Implement a local hash-only export integrity verifier for Phase 8E export
packs, following the design in
`docs/PHASE8F_EXPORT_INTEGRITY_SIGNING_DESIGN.md`. Phase 8G recomputes
sha256 hashes for source evidence and copied evidence files, recomputes a
canonical bundle hash, and best-effort recomputes a manifest hash when the
manifest already carries one. It implements no signing, generates no keys,
and changes no Phase 8E export or Phase 7D wrapper behavior.

## Scope

Phase 8G is a local hash-only verifier. It implements no signing, no
detached signature verification, no key generation, no private key
handling, and no encryption. It adds no KMS/Secrets Manager/backend/API/
database/SQLite/S3/DynamoDB, changes no Phase 8E export behavior, changes
no Phase 7D wrapper behavior, changes no approval logic, executes no
primitive, performs no vault read/write, and adds no new mutation path.

## Files

- `codex/tasks/058-phase8g-export-integrity-verifier.md`
- `docs/PHASE8G_EXPORT_INTEGRITY_VERIFIER.md`
- `scripts/dev/verify_phase8g_export_integrity.py`
- `scripts/dev/run_phase8g_export_integrity.sh`
- `tests/test_phase8g_export_integrity_verifier.py`
- additive updates to `docs/ROADMAP.md`
- additive updates to `docs/PROJECT_STATE.md`
- additive updates to `docs/PHASE8F_EXPORT_INTEGRITY_SIGNING_DESIGN.md`
- additive updates to `docs/PHASE8E_AUDIT_EXPORT_PACK.md`
- additive update to `.gitignore` (`tmp/phase8g-export-integrity/`,
  `tmp/phase8g-test-input/`)

## Status model

- `success`: the verifier and shell runner exist, verification is read-only
  over the export manifest and all referenced evidence, hash/size/bundle/
  manifest-hash checks behave as specified, output is confined to
  `tmp/phase8g-export-integrity/`, additive documentation pointers exist,
  protected runtime files (Phase 6-8F) stay unchanged, the shell runner is
  mode `100755` on disk and in the git index, and
  `phase7d_runtime_readiness` remains `implemented_manual_gate`.
- `failed`: the verifier mutates the export pack or source evidence, writes
  outside `tmp/phase8g-export-integrity/`, accepts an unsafe manifest/report
  path, misses a genuine hash/size mismatch, or a protected runtime surface
  changes.

## Local hash-only verification objective

Provide a deterministic, read-only integrity check over a Phase 8E export
pack's evidence hashes and a canonical bundle hash, as the first
implementation step recommended by the Phase 8F design, without
implementing any signing, key management, or encryption.

## Input export manifest contract

- default manifest path: `tmp/phase8e-audit-export/audit-export-manifest.json`
- a missing manifest path is not an error; it produces an empty report
  (`verification_status: empty`, `evidence_count: 0`, `issue_count: 0`,
  `hash_only_verification: true`)
- an existing manifest must be a JSON object; invalid JSON or a non-object
  body produces `verification_status: invalid` and a non-zero exit
- fields read best-effort: `source_evidence`, `source_hashes`,
  `copied_files`, `export_dir`, `phase8e_status`,
  `durable_audit_store_status`, `phase7d_runtime_readiness`,
  `record_count`, `verification_status`, `query_status`, `generated_at`,
  `bundle_hash` (if present), `manifest_hash` (if present)

## Export directory path safety model

Manifest-path rules:

- must resolve under the repository root
- must not resolve under `vault/`, `docs/`, `scripts/`, `tests/`, or `codex/`
- should normally be under `tmp/phase8e-audit-export/`
- symlinks are rejected
- path traversal is rejected
- absolute paths outside the repository are rejected
- a manifest-path safety violation produces an `invalid` report and a
  non-zero exit

Report-dir rules:

- default: `tmp/phase8g-export-integrity`
- must resolve under `tmp/phase8g-export-integrity` only
- created if missing
- a custom report dir outside `tmp/phase8g-export-integrity` is rejected
  with a non-zero exit and no report is written

Each referenced evidence path (source and copied) is independently
re-validated with the same traversal/symlink/outside-repo/rejected-root
checks before it is ever opened.

## Evidence hash verification model

For every `source_evidence` entry with `exists: true` and `allowed: true`:
the referenced path is re-validated for safety, then re-hashed and
re-measured from disk if it currently exists. The recomputed sha256 and
size are compared to the manifest's recorded `sha256`/`size_bytes`. A
missing file, a hash mismatch, a size mismatch, or a disallowed path all
become issues without crashing the run. An entry the manifest already
recorded as missing (`exists: false`) is reported as `not_applicable`
rather than re-flagged, since Phase 8E already disclosed it as missing.

For every `copied_files` entry, the destination path must resolve under
`tmp/phase8e-audit-export/evidence/` or under the manifest's own
`export_dir/evidence/`; otherwise it is a disallowed-path issue. A copy
that exists is re-hashed and compared against the corresponding
`source_evidence` entry's `sha256` (by label) when available, otherwise
against the copied entry's own recorded `sha256`.

## Bundle descriptor model

A canonical JSON descriptor (`sort_keys=True`, `separators=(",", ":")`,
`ensure_ascii=False`) built from: `source_evidence` reduced to `label`,
`path`, `sha256`, `size_bytes` (sorted by `label`); `copied_files` reduced
to destination `path` and `sha256` (sorted by `path`); and `record_count`,
`verification_status`, `query_status`, `phase8e_status`, and
`durable_audit_store_status` taken directly from the manifest.

## Computed bundle hash model

`computed_bundle_hash` is the sha256 of the canonical bundle descriptor,
always computed. If the manifest carries a `bundle_hash`, it is compared:
`bundle_hash_status` is `match` or `mismatch` (mismatch is an issue). If the
manifest carries no `bundle_hash`, `bundle_hash_status` is
`computed_only`.

## Manifest hash handling model

`computed_manifest_hash` is the sha256 of the canonical manifest JSON with
the `manifest_hash` key excluded, always computed. If the manifest carries
a `manifest_hash`, it is compared: `manifest_hash_status` is `match` or
`mismatch` (mismatch is an issue). If the manifest carries no
`manifest_hash` (the case for all current Phase 8E output, since Phase 8E
predates this field), `manifest_hash_status` is `not_present`.

## Missing evidence behavior

A `source_evidence` or `copied_files` entry whose file cannot be found on
disk (despite the manifest, or the copy step, claiming it should exist) is
recorded as `missing_file` / `missing_copied_evidence_file` and becomes a
`warning`-level issue; it never aborts the run.

## Hash mismatch behavior

A recomputed hash or size that differs from the manifest's recorded value
becomes an issue (`hash_mismatch`, `size_mismatch`, or
`copied_evidence_hash_mismatch`) and forces `verification_status` to
`warning`; it never aborts the run and never mutates the mismatched file.

## Verification report model

The JSON report carries: `phase8g_status`, `durable_audit_store_status`,
`phase7d_runtime_readiness`, `signing_implementation_status`,
`verification_status`, `hash_only_verification`, `manifest_path`,
`report_dir`, `evidence_count`, `copied_evidence_count`, `issue_count`,
`manifest_hash_status`, `bundle_hash_status`, `computed_manifest_hash`,
`manifest_manifest_hash`, `computed_bundle_hash`, `manifest_bundle_hash`,
`evidence_results`, `copied_evidence_results`, `issues`,
`safety_statement`, and `limitations`. Each evidence result carries
`label`, `path`, `exists`, `allowed`, `expected_sha256`, `actual_sha256`,
`expected_size_bytes`, `actual_size_bytes`, `hash_status`, and
`size_status`. Each issue carries `issue_type`, `message`, `path`, and
`label`. The Markdown report carries the same information plus an explicit
statement that a verified export is not approval.

## Failure behavior

`valid`, `warning`, and `empty` all exit `0`. Only a critical manifest-path
safety violation, a malformed manifest (invalid JSON or non-object), or a
report-dir rejection exits non-zero; a report-dir rejection additionally
means no report is written, since there is no verified-safe location to
write one.

## Non-goals

- no signing implementation
- no detached signature implementation
- no signature verifier implementation
- no key generation
- no private key handling
- no public key handling beyond design references
- no encryption implementation
- no KMS implementation
- no Secrets Manager implementation
- no database, no SQLite implementation, no S3 implementation, no DynamoDB
  implementation
- no backend, no FastAPI, no API routes
- no external APIs, no external URLs, no network behavior
- no new runtime mutation path
- no primitive execution
- no vault read/write
- no Phase 7D wrapper behavior change
- no Phase 8B ingest behavior change
- no Phase 8C verifier behavior change
- no Phase 8D query behavior change
- no Phase 8E export behavior change
- no approve-all, no global approval, no multi-gate execution
- no next-gate automation, no chain execution
- no affiliate content generation, no autopublish, no campaign launch
- no marketplace connector, no production deployment

## Phase 8E export boundary

Phase 8G does not modify, wrap, call, or execute
`scripts/dev/build_phase8e_audit_export_pack.py` or
`scripts/dev/run_phase8e_audit_export.sh`. It only reads the manifest and
evidence files that export pack produces.

## Phase 8F signing boundary

Phase 8G implements only the hash-only prerequisite that
`docs/PHASE8F_EXPORT_INTEGRITY_SIGNING_DESIGN.md` recommended as Phase 8G.
It implements no detached signature, no key generation, no private key
handling, and no encryption. The Phase 8F design remains the signing
governance source of truth; this phase adds no signing capability.

## Phase 7D approval boundary

A verified or hash-valid export is not approval. Verification never sets or
implies an approval flag, never calls the Phase 7D wrapper, and never
triggers the next gate. `phase7d_runtime_readiness` remains
`implemented_manual_gate`, unaffected by this phase.

## Operator/reviewer use model

1. use Phase 8B to ingest existing audit artifacts.
2. use Phase 8C to verify/report store integrity.
3. use Phase 8D to query relevant records.
4. use Phase 8E to generate a reviewable export pack.
5. use Phase 8G to verify the export pack's hash integrity.
6. treat a Phase 8G `valid` result as evidence integrity only, never as
   approval.
7. treat a Phase 8G `warning` or `invalid` result as a signal for manual
   review.

## Test strategy

Deterministic tests: file/status existence; scope/safety token coverage;
static safety of the verifier script and shell runner (no subprocess/
sqlite3/boto3/requests/httpx/urllib imports, no FastAPI, no signing/key-
generation/encryption commands, no primitive calls, no vault writes, no
`--execute`, no approval flags set truthy, no wrapper/primitive/Phase 7B/
Phase 8B/Phase 8C/Phase 8D/Phase 8E calls); executable-mode and
`bash -n`/`py_compile` checks; missing-manifest behavior; valid-export
behavior against a real Phase 8B→8E fixture chain (with and without
`--include-copies` semantics via a hand-built manifest); manifest-hash
match/mismatch behavior; bundle-hash computed-only/match/mismatch behavior;
evidence hash/size mismatch and missing-file detection; disallowed evidence
path detection; copied-evidence hash verification and disallowed-copy-path
detection; invalid-manifest handling (bad JSON, JSON array); path-safety
rejections; documentation regression; protected runtime file hash
regression (including Phase 8B/8C/8D/8E scripts); shell-runner permission
checks (filesystem mode and git index mode); and a static-safety scan over
only the new Phase 8G task/doc/script files.

## Acceptance criteria

- verifier script and shell runner exist and are executable/well-formed
- verification is strictly read-only over the manifest and all evidence
- hash, size, bundle-hash, and manifest-hash checks behave as specified
  against real Phase 8B→8E output
- missing-evidence, hash-mismatch, and disallowed-path handling behave as
  specified
- unsafe manifest/report paths are rejected appropriately
- design doc contains `phase8g_status: success`,
  `phase7d_runtime_readiness: implemented_manual_gate`,
  `durable_audit_store_status: export_integrity_verifier`, and
  `signing_implementation_status: not_implemented`
- ROADMAP, PROJECT_STATE, the Phase 8F doc, and the Phase 8E doc all
  reference Phase 8G additively
- protected Phase 6B/6C/6E/7B/7D/7G/8B/8C/8D/8E runtime files remain
  unchanged
- no signing implementation, key file, or certificate file is added
- no backend/API/database file is added
- all runtime writes are confined to `tmp/phase8g-export-integrity/`
- the shell runner is mode `100755` on disk and in the git index

## Verification commands

```text
source .venv/bin/activate
umask 022

python -m pytest -q tests/test_phase8g_export_integrity_verifier.py
python -m pytest -q tests/test_phase8f_export_integrity_signing_design.py
python -m pytest -q tests/test_phase8e_audit_export_pack.py
python -m pytest -q tests/test_phase8d_audit_store_query_cli.py
python -m pytest -q tests/test_phase8c_audit_store_verifier_reporting.py
python -m pytest -q tests/test_phase8b_local_append_only_audit_store.py
python -m pytest -q tests/test_phase8a_durable_audit_store_design.py
python -m pytest -q tests/test_phase7h_operator_runbook_hardening.py
python -m pytest -q tests/test_phase7g_operator_acceptance_demo_pack.py
python -m pytest -q tests/test_phase7f_runtime_wrapper_live_snapshot.py
python -m pytest -q tests/test_phase7d_single_gate_wrapper.py
python -m pytest -q tests/test_phase7e_release_snapshot_runtime_blocked.py
python -m pytest -q tests/test_phase7d_implementation_plan_finalization.py
python -m pytest -q tests/test_phase7d_r_high_risk_readiness_review.py
python -m pytest -q tests/test_phase7c_single_gate_wrapper_implementation_plan.py
python -m pytest -q tests/test_phase7b_audit_verifier.py
python -m pytest -q tests/test_phase7a_audit_verifier_implementation_plan.py
python -m pytest -q tests/test_phase6h_release_snapshot.py tests/test_phase6g_manual_approval_audit_verifier_boundary.py tests/test_phase6f_single_gate_manual_approval_wrapper_boundary.py tests/test_phase6e_dry_run_approval_execution_planner.py tests/test_phase6d_manual_approval_execution_boundary.py tests/test_phase6c_approval_review_packet_verifier.py tests/test_phase6b_dry_run_approval_review_packet.py tests/test_phase6a_manual_approved_workflow_boundary.py
python -m pytest -q tests/test_phase5e_release_snapshot.py tests/test_phase3e_release_snapshot.py

python -m py_compile scripts/dev/verify_phase8g_export_integrity.py
bash -n scripts/dev/run_phase8g_export_integrity.sh

chmod 755 scripts/dev/run_phase8g_export_integrity.sh
test "$(stat -c '%a' scripts/dev/run_phase8g_export_integrity.sh)" = "755"
git ls-files -s scripts/dev/run_phase8g_export_integrity.sh | grep "^100755 "

find scripts/dev -type f -name "*.sh" -exec chmod 755 {} \;

env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q

grep -RInE "/home/[^/]+/Affiliate-Ai" scripts/ || echo "scripts clean"
git diff --check
git status --short --branch
```

## Known limitations

Phase 8G is a local hash-only prototype: no signature verification, no
signing, no key management, no encryption, no backend/API, no
authenticated identity, no production deployment, and no automatic
remediation.

## Final status target

phase8g_status: success
