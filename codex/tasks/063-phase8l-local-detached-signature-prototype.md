# Task 063 — Phase 8L Local Detached Signature Prototype

phase8l_status: success

phase7d_runtime_readiness: implemented_manual_gate

durable_audit_store_status: local_detached_signature_prototype

signing_implementation_status: prototype_local_only

signature_runtime_status: local_prototype

signature_verifier_runtime_status: not_implemented

key_management_runtime_status: not_implemented

major_phase_branch_workflow: enabled

## Purpose

Phase 8L implements a local-only detached signature prototype over Phase
8E export packs: a signed payload descriptor builder, a detached signature
envelope builder, and an HMAC-SHA256 prototype signature produced only
when an in-memory prototype key is present. Phase 8L does not implement
production signing, a signature verifier, or key management runtime.

## Scope

- local-only detached signature prototype
- signed payload descriptor generation
- detached signature envelope generation
- HMAC-SHA256 prototype signature only
- no committed private keys
- no key generation
- no KMS/Secrets Manager
- no backend/API/database
- no signature verifier implementation
- no wrapper behavior change
- no primitive execution
- no vault read/write
- no new mutation path
- no next-gate automation
- no chain execution

## Files

- `scripts/dev/build_phase8l_detached_signature.py`
- `scripts/dev/run_phase8l_detached_signature.sh`
- `tests/test_phase8l_local_detached_signature_prototype.py`
- `codex/tasks/063-phase8l-local-detached-signature-prototype.md`
- `docs/PHASE8L_LOCAL_DETACHED_SIGNATURE_PROTOTYPE.md`
- additive updates to `docs/ROADMAP.md`
- additive updates to `docs/PROJECT_STATE.md`
- additive updates to `docs/PHASE8K_KEY_MANAGEMENT_DESIGN.md`
- additive updates to `docs/PHASE8J_DETACHED_SIGNATURE_VERIFIER_DESIGN.md`
- additive updates to `docs/PHASE8I_DETACHED_SIGNATURE_DESIGN_FINALIZATION.md`
- additive updates to `.gitignore`

## Status model

- `phase8l_status: success` — the local detached signature prototype
  exists, additive documentation pointers exist, and protected runtime
  files stay unchanged.
- `phase7d_runtime_readiness: implemented_manual_gate` — the Phase 7D
  single-gate manual approval wrapper remains the only implemented
  approval runtime; Phase 8L does not change it.
- `durable_audit_store_status: local_detached_signature_prototype` — the
  durable audit store status token advances to reflect that a local
  detached signature prototype now exists.
- `signing_implementation_status: prototype_local_only` — signing exists
  only as a local, non-production HMAC-SHA256 prototype.
- `signature_runtime_status: local_prototype` — a detached signature
  runtime now exists, but only as a local prototype.
- `signature_verifier_runtime_status: not_implemented` — no signature
  verifier runtime exists.
- `key_management_runtime_status: not_implemented` — no key management
  runtime exists.
- `major_phase_branch_workflow: enabled` — Phase 8L follows the
  major-phase checkpoint-commit-only workflow; no PR is opened for this
  sub-phase alone.

## Local detached signature prototype objective

Provide a working, local-only reference implementation of the Phase 8I
signed payload descriptor and detached signature envelope, using a
prototype HMAC-SHA256 signature over an in-memory environment-variable
key, so future phases can build a real verifier and key management
runtime against a concrete, tested output shape without any production
signing, key generation, or KMS/Secrets Manager integration.

## Current trust boundary

- Phase 8I finalized the detached signature design
- Phase 8J designed detached signature verifier interpretation
- Phase 8K designed key management governance
- a local prototype signing runtime now exists
- no signature verifier runtime exists
- no key management runtime exists
- no authenticated operator identity exists
- no governed key custody exists
- no enterprise non-repudiation exists
- a prototype signature is evidence only, not approval
- durable audit remains a local/tmp workflow

## Runtime input contract

`scripts/dev/build_phase8l_detached_signature.py` accepts
`--manifest-path`, `--integrity-report-path`, `--output-dir`,
`--signer-id`, `--signer-role`, `--signer-identity-assurance`, `--key-id`,
`--key-version`, and `--signing-policy-version`. Defaults: manifest-path
`tmp/phase8e-audit-export/audit-export-manifest.json`;
integrity-report-path
`tmp/phase8g-export-integrity/export-integrity-verification.json`;
output-dir `tmp/phase8l-detached-signature`; `signer_id`
`operator_declared`; `signer_role` `operator`;
`signer_identity_assurance` `operator_declared`; `key_id`
`phase8l-prototype-key`; `key_version` `prototype-v1`;
`signing_policy_version` `phase8l.prototype.signing_policy.v1`.
`scripts/dev/run_phase8l_detached_signature.sh` forwards all CLI
arguments unchanged to the build script.

## Signed payload descriptor model

Fields: `payload_schema_version`, `export_manifest_path`,
`export_manifest_sha256`, `bundle_hash`, `computed_manifest_hash`,
`report_schema_version`, `issue_taxonomy_version`,
`compatibility_matrix_version`, `verifier_hardening_status`,
`verification_status`, `compatibility_result`, `incident_classification`,
`reviewer_action`, `reviewer_action_required`, `generated_from_phase`,
`generated_by_tool`, `created_at_utc`, `signing_policy_version`,
`signer_id`, `signer_role`, `signer_identity_assurance`, `key_id`,
`key_version`, `approval_boundary_statement`. The integrity-report-derived
fields are populated from an optional Phase 8G/8H report and are `null`
when no report is available.

## Prototype signature model

`signed_payload_sha256` is the SHA-256 hex digest of the canonical JSON
serialization of the descriptor (`sort_keys=True`,
`separators=(",", ":")`, `ensure_ascii=False`). When the prototype key
env var is set, the detached signature is an HMAC-SHA256 hex digest over
`signed_payload_sha256`, using `prototype_signature_algorithm:
hmac-sha256-prototype`.

## Detached signature envelope model

Fields: `signature_schema_version`, `signed_payload_sha256`,
`signed_payload_descriptor_path`, `detached_signature_path`,
`signature_algorithm`, `signature_encoding`, `key_id`, `key_version`,
`signer_id`, `signer_role`, `signer_identity_assurance`,
`signing_policy_version`, `signing_timestamp_utc`, `signature_status`,
`signing_status`, `verification_status` (`not_verified`),
`revocation_status` (`not_checked`), `rotation_epoch` (`prototype`),
`approval_boundary_statement`, `signature_runtime_status`
(`local_prototype`), `signing_implementation_status`
(`prototype_local_only`), `detached_signature_value` (the HMAC hex digest
when signed, else `null`).

## Prototype key handling model

The prototype key is read only from the `AFFILIATE_PHASE8L_PROTOTYPE_KEY`
environment variable, used only in memory, and never written to any
output file or logged. No key files are created and no key material is
committed. When the env var is unset, signing is skipped
(`signing_status: skipped_missing_prototype_key`,
`signature_status: not_ready`) and the tool exits 0. When the env var is
set, signing proceeds (`signing_status: signed_local_prototype`,
`signature_status: present`) and the tool exits 0.

## Output report model

Outputs are written only under `tmp/phase8l-detached-signature/`:
`signed-payload-descriptor.json`, `detached-signature-envelope.json`,
`detached-signature-summary.json`, `detached-signature-summary.md`, and
(only when a prototype signature is produced) `detached-signature.sig`.
The summary JSON/Markdown carry the eight status tokens, `signing_status`,
`signature_status`, `prototype_signature_algorithm`,
`signed_payload_sha256`, signer/key metadata, output paths, a safety
statement, an approval boundary statement, and known limitations.

## Path safety model

The manifest path and integrity-report path are rejected if empty, if
they contain a `..` traversal segment, if they are symlinks, if they
resolve outside the repository, or if they resolve under a rejected
source root (`vault`, `docs`, `scripts`, `tests`, `codex`); a path that
resolves safely but does not exist is treated as "missing" rather than an
error. The output directory is rejected if empty, if it contains a `..`
traversal segment, if it is a symlink, or if it does not resolve to
`tmp/phase8l-detached-signature` or a path beneath it.

## Missing manifest behavior

When the manifest path resolves safely but the file does not exist, the
tool writes only a summary with `signing_status:
skipped_missing_manifest`, `signature_status: not_present`, and
`phase8l_status: success`, and exits 0.

## Invalid manifest behavior

When the manifest file exists but is not valid JSON, or the parsed JSON
is not an object (for example a JSON array), the tool writes a summary
with `signing_status: invalid_manifest`, `signature_status: not_present`,
and exits nonzero.

## Failure behavior

An unsafe manifest path, an unsafe integrity-report path, or an unsafe
output-dir causes the tool to write a summary with `signing_status:
invalid_manifest_path` (with a `path_error_category`) or to fail before
any output is written, and to exit nonzero. All other recognized input
states (missing manifest, present manifest with or without the prototype
key) exit 0.

## Non-goals

Phase 8L does not implement production signing, does not implement a
signature verifier, does not implement key management runtime, does not
generate or persist keys, does not implement KMS/Secrets Manager, does
not implement backend/API/database, does not change Phase 7D wrapper
behavior, does not change Phase 8B/8C/8D/8E/8G/8H runtime behavior, does
not execute primitives, does not read or write the vault, does not
trigger the next gate, and does not add chain execution.

## Phase 8K key management boundary

Phase 8K remains design-only key management governance. Phase 8L does not
implement key management; it uses an env-var prototype key only.
`key_management_runtime_status` remains `not_implemented`.

## Phase 8J verifier design boundary

Phase 8J remains design-only detached signature verifier interpretation.
Phase 8L does not implement a signature verifier.
`signature_verifier_runtime_status` remains `not_implemented`.

## Phase 8I signature design boundary

Phase 8I remains the detached signature envelope/payload design source.
Phase 8L is the first local runtime implementation of that design and
does not change the Phase 8I design document.

## Phase 8H verifier boundary

Phase 8H remains the hash-only export integrity verifier. Phase 8L may
read a Phase 8G/8H integrity report if provided but does not change
Phase 8H runtime behavior.

## Phase 8E export boundary

Phase 8E remains the export pack builder. Phase 8L consumes the Phase 8E
export manifest read-only and does not modify the Phase 8E export pack or
call Phase 8E export automatically.

## Phase 7D approval boundary

Approval remains the Phase 7D selected-gate manual boundary. Phase 8L
does not call the Phase 7D wrapper, does not call primitives, does not
write the vault, and does not trigger the next gate.

## Operator/reviewer use model

An operator runs the Phase 8L runner against an existing Phase 8E export
manifest to produce a signed payload descriptor and detached signature
envelope as local evidence. A reviewer treats the resulting signature and
envelope as supplementary evidence only; the signature does not replace,
bypass, or substitute for the Phase 7D selected-gate manual approval
boundary.

## Test strategy

Deterministic tests in
`tests/test_phase8l_local_detached_signature_prototype.py` exercise: a
missing manifest, a present manifest with the prototype key unset, a
present manifest with the prototype key set, an invalid (non-JSON or
non-object) manifest, unsafe manifest/integrity-report/output-dir paths,
canonical hash determinism, descriptor and envelope field coverage,
output-file placement under `tmp/phase8l-detached-signature/` only, doc
cross-reference regression across
ROADMAP/PROJECT_STATE/PHASE8K/PHASE8J/PHASE8I, protected-runtime-file
non-modification, and a static safety scan of the new files rejecting
secrets, private-key material, and unrelated executable command examples.

## Acceptance criteria

- task exists
- design doc exists
- runtime script exists and is importable/compilable
- shell runner exists and passes `bash -n`
- design doc contains `phase8l_status: success`
- design doc contains `phase7d_runtime_readiness: implemented_manual_gate`
- design doc contains `durable_audit_store_status:
  local_detached_signature_prototype`
- design doc contains `signing_implementation_status: prototype_local_only`
- design doc contains `signature_runtime_status: local_prototype`
- design doc contains `signature_verifier_runtime_status: not_implemented`
- design doc contains `key_management_runtime_status: not_implemented`
- design doc contains `major_phase_branch_workflow: enabled`
- missing manifest produces `skipped_missing_manifest` and exit 0
- unset prototype key produces `skipped_missing_prototype_key` and exit 0
- set prototype key produces `signed_local_prototype` and exit 0
- invalid manifest produces `invalid_manifest` and a nonzero exit
- unsafe paths produce a nonzero exit
- outputs are written only under `tmp/phase8l-detached-signature/`
- ROADMAP, PROJECT_STATE, PHASE8K, PHASE8J, and PHASE8I all reference
  Phase 8L additively
- protected Phase 2G/2H/2I, 6B/6C/6E, 7B, 7D wrapper, and
  8B/8C/8D/8E/8G/8H runtime files remain unchanged
- no backend/API/database file is added by Phase 8L

## Focused verification commands

```text
source .venv/bin/activate
python -m pytest -q tests/test_phase8l_local_detached_signature_prototype.py
python -m pytest -q tests/test_phase8k_key_management_design.py
python -m pytest -q tests/test_phase8j_detached_signature_verifier_design.py
python -m pytest -q tests/test_phase8i_detached_signature_design_finalization.py
python -m pytest -q tests/test_phase8h_export_integrity_verifier_hardening.py
python -m pytest -q tests/test_phase8g_export_integrity_verifier.py
python -m py_compile scripts/dev/build_phase8l_detached_signature.py
bash -n scripts/dev/run_phase8l_detached_signature.sh
```

## Major-phase checkpoint policy

Phase 8L is part of `feature/phase8-signature-governance-completion`.
Phase 8L should create a checkpoint commit only; no PR should be opened
after Phase 8L alone. Because Phase 8L adds runtime code, focused tests
plus Phase 8G-8K regressions and `py_compile`/`bash -n` are required
before moving on. The full suite is deferred to major Phase 8 completion
unless focused tests fail or protected runtime changes occur.

## Known limitations

Phase 8L is a local prototype only. Its signature is HMAC-SHA256
prototype only, not production signing. No signature verifier runtime, no
key management runtime, and no governed key custody exist. No encryption,
no authenticated operator identity, and no non-repudiation exist. No
backend/API/database and no production deployment exist.

## Final status target

phase8l_status: success
