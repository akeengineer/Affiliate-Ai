# Phase 8H — Export Integrity Verifier Hardening

```text
phase8h_status: success
phase8g_status: success
phase7d_runtime_readiness: implemented_manual_gate
durable_audit_store_status: export_integrity_verifier_hardened
signing_implementation_status: not_implemented
verifier_hardening_status: enabled
```

### Purpose

Phase 8H hardens the Phase 8G local hash-only verifier with a stable
report schema, an issue taxonomy, a severity model, tamper-evidence
incident classification, a reviewer action mapping, a Phase 8E manifest
compatibility matrix, and a deterministic output contract. It changes no
signing, key, or encryption behavior.

### Scope

- verifier hardening only
- local hash-only verifier remains
- no signing implementation
- no signature verification implementation
- no key generation
- no private key handling
- no encryption
- no KMS/Secrets Manager
- no backend/API/database
- no SQLite/S3/DynamoDB
- no network behavior
- no wrapper behavior change
- no primitive execution
- no vault read/write
- no new mutation path
- no next-gate automation
- no chain execution

### Runtime command

```text
bash scripts/dev/run_phase8g_export_integrity.sh [verification options]
```

No new Phase 8H runner is added; the existing Phase 8G shell wrapper and CLI
shape are unchanged. The wrapper never accepts an approval flag and never
accepts `--execute`.

### Stable report schema contract

- `report_schema_version: phase8g.integrity_report.v2`
- `issue_taxonomy_version: phase8h.issue_taxonomy.v1`
- `compatibility_matrix_version: phase8h.compatibility_matrix.v1`
- every top-level field Phase 8G produced (`phase8g_status`,
  `durable_audit_store_status`, `phase7d_runtime_readiness`,
  `signing_implementation_status`, `verification_status`,
  `hash_only_verification`, `manifest_path`, `report_dir`,
  `evidence_count`, `copied_evidence_count`, `issue_count`,
  `manifest_hash_status`, `bundle_hash_status`, `computed_manifest_hash`,
  `manifest_manifest_hash`, `computed_bundle_hash`, `manifest_bundle_hash`,
  `evidence_results`, `copied_evidence_results`, `issues`,
  `safety_statement`, `limitations`) remains present with the same meaning
- new hardening fields are additive: `phase8h_status`,
  `report_schema_version`, `issue_taxonomy_version`,
  `compatibility_matrix_version`, `verifier_hardening_status`,
  `deterministic_output_contract`, `compatibility_result`,
  `severity_counts`, `incident_classification`, `reviewer_action`,
  `reviewer_action_required`, `approval_boundary_statement`
- `issues`, `evidence_results`, and `copied_evidence_results` are sorted
  deterministically (see below)

### Issue taxonomy

Supported `issue_type` values:

- `manifest_missing`
- `manifest_invalid_json`
- `manifest_not_object`
- `manifest_path_disallowed`
- `manifest_symlink`
- `manifest_outside_repo`
- `report_dir_disallowed`
- `evidence_missing`
- `evidence_hash_mismatch`
- `evidence_size_mismatch`
- `evidence_path_disallowed`
- `evidence_symlink`
- `copied_evidence_missing`
- `copied_evidence_hash_mismatch`
- `copied_evidence_path_disallowed`
- `manifest_hash_mismatch`
- `bundle_hash_mismatch`
- `compatibility_warning`
- `unknown`

Every issue object carries `issue_type`, `severity`,
`incident_classification`, `reviewer_action`, `message`, `path`, and
`label`. The verifier's existing Phase 8G issue-type strings
(`hash_mismatch`, `size_mismatch`, `missing_evidence_file`,
`disallowed_evidence_path`, `missing_copied_evidence_file`,
`copied_evidence_hash_mismatch`, `disallowed_copied_evidence_path`,
`manifest_hash_mismatch`, `bundle_hash_mismatch`) are preserved verbatim and
map into this taxonomy's `evidence_missing`/`evidence_hash_mismatch`/etc.
concepts; existing tests that assert on those exact strings continue to
pass unmodified.

### Severity model

Severity values: `info`, `warning`, `critical`.

Mapping: `manifest_missing` = `info`; every evidence-level issue (missing,
hash mismatch, size mismatch, disallowed path, symlink), every copied-
evidence issue, `manifest_hash_mismatch`, `bundle_hash_mismatch`, and
`compatibility_warning` = `warning`; `manifest_invalid_json`,
`manifest_not_object`, `manifest_path_disallowed`, `manifest_symlink`,
`manifest_outside_repo`, and `report_dir_disallowed` = `critical`;
`unknown` = `warning`.

### Tamper-evidence incident classification

Values: `none`, `missing_manifest`, `malformed_manifest`,
`path_safety_violation`, `tamper_evidence_warning`,
`compatibility_review_required`.

Priority when multiple issues are present (highest first):
`path_safety_violation` > `malformed_manifest` > `tamper_evidence_warning` >
`compatibility_review_required` > `missing_manifest` > `none`. An empty
(missing-manifest) report is always classified `missing_manifest`
regardless of this priority list, since it has no issues to prioritize
among.

### Reviewer action mapping

Values: `no_action_required`, `manual_review_recommended`,
`manual_review_required`, `reject_export_until_resolved`.

Mapping: `empty`/`valid` verification status -> `no_action_required`;
`warning` (including a compatibility warning) -> `manual_review_required`;
`invalid` (a critical path/manifest failure) ->
`reject_export_until_resolved`.

Reviewer action is review guidance only. Reviewer action is not approval.
Reviewer action must not execute a primitive, must not trigger the Phase 7D
wrapper, and must not trigger the next gate.

### Compatibility matrix

Expected Phase 8E manifest fields:

- `phase8e_status: success`
- `durable_audit_store_status: export_pack`
- `phase7d_runtime_readiness: implemented_manual_gate`

`compatibility_result` is `compatible` when all three fields are present
and match; `review_required` when any field is missing (and no field
conflicts); `incompatible` when any field is present but explicitly
conflicts with its expected value. A `review_required` or `incompatible`
result adds one `compatibility_warning` issue at `warning` severity — an
incompatible manifest is a review issue, not a critical path-safety
failure, so it never forces `verification_status` to `invalid`.

### Deterministic output contract

- `canonical_json_sort_keys: true`
- `canonical_json_separators: [",", ":"]`
- `stable_report_schema: true`
- `stable_issue_taxonomy: true`
- the report JSON is written with `sort_keys=True` and stable indentation
- `issues` are sorted by severity priority (`critical` before `warning`
  before `info`), then `issue_type`, `label`, `path`, `message`
- `evidence_results` and `copied_evidence_results` are sorted by `label`,
  then `path`

### Safety boundary

- the hardened verifier does not approve anything
- verified export is not approval
- hash-valid export is not approval
- reviewer action is not approval
- the verifier does not execute a primitive
- the verifier does not call the Phase 7D wrapper
- the verifier does not call the Phase 7B verifier
- the verifier does not call the Phase 8B ingest writer
- the verifier does not call the Phase 8C verifier
- the verifier does not call the Phase 8D query CLI
- the verifier does not call the Phase 8E export builder
- the verifier does not trigger the next gate
- the verifier does not chain execution
- the verifier does not sign anything
- the verifier does not generate keys
- the verifier does not write the vault
- the verifier writes only reports under `tmp/phase8g-export-integrity`

### Operator/reviewer checklist

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

### Known limitations

- local tmp verifier only
- hash-only
- no signature verification
- no signing
- no key management
- no encryption
- no backend/API
- no authenticated identity
- no production deployment
- no automatic remediation
