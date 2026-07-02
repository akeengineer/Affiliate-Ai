# Task 059 — Phase 8H Export Integrity Verifier Hardening

phase8h_status: success

phase7d_runtime_readiness: implemented_manual_gate

durable_audit_store_status: export_integrity_verifier_hardened

signing_implementation_status: not_implemented

## Purpose

Harden the Phase 8G local hash-only export integrity verifier with a stable
report schema contract, an issue taxonomy, a severity model, tamper-evidence
incident classification, a reviewer action mapping, a Phase 8E manifest
compatibility matrix, and a deterministic output contract. Phase 8H only
adds hardening metadata and stronger issue classification to the existing
verifier; it implements no signing, generates no keys, and changes no Phase
8E export or Phase 7D wrapper behavior.

## Scope

Phase 8H hardens `scripts/dev/verify_phase8g_export_integrity.py` only. It
implements no signing, no detached signature verification, no key
generation, no private key handling, and no encryption. It adds no KMS/
Secrets Manager/backend/API/database/SQLite/S3/DynamoDB, changes no Phase
8E export behavior, changes no Phase 7D wrapper behavior, executes no
primitive, performs no vault read/write, and adds no new mutation path. It
adds no new shell runner.

## Files

- `codex/tasks/059-phase8h-export-integrity-verifier-hardening.md`
- `docs/PHASE8H_EXPORT_INTEGRITY_VERIFIER_HARDENING.md`
- `scripts/dev/verify_phase8g_export_integrity.py` (hardened in place)
- `tests/test_phase8h_export_integrity_verifier_hardening.py`
- additive updates to `docs/ROADMAP.md`
- additive updates to `docs/PROJECT_STATE.md`
- additive updates to `docs/PHASE8G_EXPORT_INTEGRITY_VERIFIER.md`
- additive updates to `docs/PHASE8F_EXPORT_INTEGRITY_SIGNING_DESIGN.md`
- additive updates to `docs/PHASE8E_AUDIT_EXPORT_PACK.md`
- additive update to `.gitignore` (`tmp/phase8h-test-input/`)

## Status model

- `success`: the hardened verifier exists, the Phase 8G CLI shape, output
  file paths, and valid/warning/empty/invalid exit contract are unchanged,
  every Phase 8G top-level field is retained, the new hardening fields are
  present and correctly derived, additive documentation pointers exist, no
  new shell runner was added, the existing Phase 8G runner remains mode
  `100755` on disk and in the git index, and protected runtime files (Phase
  6-8G) stay unchanged.
- `failed`: any Phase 8G CLI flag, output path, or exit behavior changes, a
  Phase 8G top-level field is dropped or renamed, a hardening field is
  missing or incorrectly derived, a new shell runner is added, or a
  protected runtime surface changes.

## Hardening objective

Make the Phase 8G verifier's output self-describing and stable for
reviewers and future automation: a versioned schema, a fixed issue
vocabulary with severity and incident classification, a direct mapping from
verification outcome to reviewer action, a compatibility check against the
Phase 8E manifest shape it expects, and deterministic sorting so the same
input always produces the same report — all without adding any signing,
key, or encryption capability.

## Stable report schema contract

- `report_schema_version: phase8g.integrity_report.v2`
- `issue_taxonomy_version: phase8h.issue_taxonomy.v1`
- `compatibility_matrix_version: phase8h.compatibility_matrix.v1`
- every existing Phase 8G top-level field remains present with unchanged
  meaning: `phase8g_status`, `durable_audit_store_status`,
  `phase7d_runtime_readiness`, `signing_implementation_status`,
  `verification_status`, `hash_only_verification`, `manifest_path`,
  `report_dir`, `evidence_count`, `copied_evidence_count`, `issue_count`,
  `manifest_hash_status`, `bundle_hash_status`, `computed_manifest_hash`,
  `manifest_manifest_hash`, `computed_bundle_hash`, `manifest_bundle_hash`,
  `evidence_results`, `copied_evidence_results`, `issues`,
  `safety_statement`, `limitations`
- new fields are additive only: `phase8h_status`, `report_schema_version`,
  `issue_taxonomy_version`, `compatibility_matrix_version`,
  `verifier_hardening_status`, `deterministic_output_contract`,
  `compatibility_result`, `severity_counts`, `incident_classification`,
  `reviewer_action`, `reviewer_action_required`,
  `approval_boundary_statement`

## Issue taxonomy model

Every issue carries `issue_type`, `severity`, `incident_classification`,
`reviewer_action`, `message`, `path`, and `label`. The taxonomy vocabulary
includes `manifest_missing`, `manifest_invalid_json`, `manifest_not_object`,
`manifest_path_disallowed`, `manifest_symlink`, `manifest_outside_repo`,
`report_dir_disallowed`, `evidence_missing`, `evidence_hash_mismatch`,
`evidence_size_mismatch`, `evidence_path_disallowed`, `evidence_symlink`,
`copied_evidence_missing`, `copied_evidence_hash_mismatch`,
`copied_evidence_path_disallowed`, `manifest_hash_mismatch`,
`bundle_hash_mismatch`, `compatibility_warning`, and `unknown`. The
verifier's existing Phase 8G `issue_type` strings (for example
`hash_mismatch`, `disallowed_evidence_path`, `missing_evidence_file`) are
preserved verbatim — Phase 8H attaches taxonomy metadata to them rather than
renaming them, so every existing Phase 8G test that asserts an exact
`issue_type` string continues to pass unmodified.

## Severity model

Severity values: `info`, `warning`, `critical`. `manifest_missing` is the
only `info`-severity concept (and, per backward compatibility, is never
materialized as a real issue in the empty-manifest report — see below).
Every evidence/copied-evidence/hash-mismatch/compatibility issue is
`warning`. Every manifest-parse or path-safety critical failure is
`critical`. `unknown` defaults to `warning`.

## Tamper-evidence incident classification

Values: `none`, `missing_manifest`, `malformed_manifest`,
`path_safety_violation`, `tamper_evidence_warning`,
`compatibility_review_required`. When a parsed manifest produces multiple
issues, the top-level `incident_classification` uses the highest-priority
classification present, in this order: `path_safety_violation` >
`malformed_manifest` > `tamper_evidence_warning` >
`compatibility_review_required` > `missing_manifest` > `none`. The empty
(missing-manifest) report is always `missing_manifest` directly, since it
has no manifest to derive issues from.

## Reviewer action mapping

Values: `no_action_required`, `manual_review_recommended`,
`manual_review_required`, `reject_export_until_resolved`. The top-level
`reviewer_action` and `reviewer_action_required` are derived directly from
`verification_status`: `valid`/`empty` -> `no_action_required` /
`reviewer_action_required: false`; `warning` -> `manual_review_required` /
`reviewer_action_required: true`; `invalid` ->
`reject_export_until_resolved` / `reviewer_action_required: true`. Each
individual issue also carries a `reviewer_action` derived the same way from
its own severity. Reviewer action is review guidance only, never approval,
and never executes a primitive, triggers the Phase 7D wrapper, or triggers
the next gate.

## Compatibility matrix model

Expected Phase 8E manifest fields: `phase8e_status: success`,
`durable_audit_store_status: export_pack`,
`phase7d_runtime_readiness: implemented_manual_gate`. `compatibility_result`
is `compatible` when all three match, `review_required` when any is
missing, or `incompatible` when any explicitly conflicts with its expected
value. A non-`compatible` result adds one `compatibility_warning` issue at
`warning` severity; it never forces `verification_status` to `invalid`,
since a compatibility mismatch is a review concern, not a path-safety
failure. Compatibility is evaluated only when a manifest was successfully
parsed; the empty and invalid-manifest reports set `compatibility_result:
review_required` as a neutral default without adding an issue.

## Deterministic output contract

`deterministic_output_contract` documents `canonical_json_sort_keys: true`,
`canonical_json_separators: [",", ":"]`, `stable_report_schema: true`, and
`stable_issue_taxonomy: true`. The report JSON is written with
`sort_keys=True`. `issues` are sorted by severity priority (critical,
warning, info), then `issue_type`, `label`, `path`, `message`.
`evidence_results` and `copied_evidence_results` are sorted by `label`,
then `path`. Running the verifier twice against unchanged input and
evidence produces byte-identical report content (the report carries no
wall-clock timestamp field).

## Backward compatibility with Phase 8G

The CLI shape (`--manifest-path`, `--report-dir`), the output file paths
(`tmp/phase8g-export-integrity/export-integrity-verification.json` and
`.md`), the valid/warning/empty/invalid exit-code contract, hash-only
behavior, and the no-signing/no-key/no-encryption posture are all
unchanged. Every existing Phase 8G test continues to pass without
modification.

## Failure behavior

Unchanged from Phase 8G: `valid`, `warning`, and `empty` all exit `0`. Only
a critical manifest-path safety violation, a malformed manifest, or a
report-dir rejection exits non-zero; a report-dir rejection still means no
report is written.

## Non-goals

- no signing implementation
- no detached signature implementation
- no signature verification implementation
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
- no new shell runner

## Phase 8G verifier boundary

Phase 8H hardens `scripts/dev/verify_phase8g_export_integrity.py` in place;
it does not add a second verifier script and does not touch
`scripts/dev/run_phase8g_export_integrity.sh`. Every Phase 8G behavioral
guarantee (read-only evidence access, path safety, hash-only verification)
is preserved.

## Phase 8F signing boundary

Phase 8H implements no detached signature, no key generation, no private
key handling, and no encryption. It hardens only the hash-only prerequisite
Phase 8F recommended as Phase 8G; the Phase 8F design remains the signing
governance source of truth.

## Phase 8E export boundary

Phase 8H does not modify, wrap, call, or execute
`scripts/dev/build_phase8e_audit_export_pack.py` or
`scripts/dev/run_phase8e_audit_export.sh`.

## Phase 7D approval boundary

A verified, hash-valid, or hardened-verification export result is not
approval. Reviewer action is review guidance only, not approval. Nothing in
this hardening sets or implies an approval flag, calls the Phase 7D
wrapper, or triggers the next gate. `phase7d_runtime_readiness` remains
`implemented_manual_gate`, unaffected by this phase.

## Operator/reviewer use model

1. Generate the Phase 8E export pack.
2. Run the Phase 8G/8H hardened verifier.
3. Confirm `verification_status`.
4. Confirm `compatibility_result`.
5. Review `severity_counts`.
6. Review `incident_classification`.
7. Follow `reviewer_action`.
8. If `warning` or `invalid`, perform manual review.
9. Do not treat a verified export as approval.
10. Do not trigger the wrapper based on verifier output.

## Test strategy

Deterministic tests: file/status existence; no new Phase 8H shell runner;
scope/safety token coverage; static safety of the hardened verifier and the
unchanged shell runner; hardened schema field presence for both the
missing-manifest and valid-export cases; missing-manifest hardening
(`incident_classification: missing_manifest`,
`reviewer_action: no_action_required`, `reviewer_action_required: false`);
valid-export hardening (`compatibility_result: compatible`,
`incident_classification: none`, zero warning/critical severities);
issue-taxonomy and severity-mapping coverage across evidence hash/size
mismatch, missing evidence, manifest-hash mismatch, and bundle-hash
mismatch; critical path/manifest behavior (invalid JSON, JSON array,
rejected-root manifest path, symlinked manifest, out-of-bounds report dir);
compatibility-matrix behavior across compatible/missing/unknown/conflicting
manifest fields; deterministic output behavior across repeated runs;
documentation regression; protected runtime file hash regression; and a
static-safety scan over only the new Phase 8H task/doc files and the
modified verifier script.

## Acceptance criteria

- the hardened verifier exists with every required new field, correctly
  derived, alongside every retained Phase 8G field
- the Phase 8G CLI shape, output paths, and exit-code contract are
  unchanged
- issue taxonomy, severity, incident classification, and reviewer action
  are correctly mapped for every exercised issue type
- the compatibility matrix correctly distinguishes compatible/
  review_required/incompatible
- deterministic sorting holds across repeated runs on unchanged input
- design doc contains `phase8h_status: success`, `phase8g_status: success`,
  `phase7d_runtime_readiness: implemented_manual_gate`,
  `durable_audit_store_status: export_integrity_verifier_hardened`,
  `signing_implementation_status: not_implemented`, and
  `verifier_hardening_status: enabled`
- ROADMAP, PROJECT_STATE, the Phase 8G doc, the Phase 8F doc, and the Phase
  8E doc all reference Phase 8H additively
- protected Phase 6B/6C/6E/7B/7D/7G/8B/8C/8D/8E runtime files remain
  unchanged
- no new shell runner is added by Phase 8H
- the existing Phase 8G runner remains mode `100755` on disk and in the git
  index
- no signing implementation, key file, or certificate file is added
- no backend/API/database file is added
- all runtime writes remain confined to `tmp/phase8g-export-integrity/`

## Verification commands

```text
source .venv/bin/activate
umask 022

python -m pytest -q tests/test_phase8h_export_integrity_verifier_hardening.py
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

find scripts/dev -type f -name "*.sh" -exec chmod 755 {} \;
test "$(stat -c '%a' scripts/dev/run_phase8g_export_integrity.sh)" = "755"
git ls-files -s scripts/dev/run_phase8g_export_integrity.sh | grep "^100755 "

env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q

grep -RInE "/home/[^/]+/Affiliate-Ai" scripts/ || echo "scripts clean"
git diff --check
git status --short --branch
```

## Known limitations

Phase 8H is verifier hardening only: no signature verification, no
signing, no key management, no encryption, no backend/API, no
authenticated identity, no production deployment, and no automatic
remediation.

## Final status target

phase8h_status: success
