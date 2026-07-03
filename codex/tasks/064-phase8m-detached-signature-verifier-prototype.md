# Task 064 — Phase 8M Detached Signature Verifier Prototype

phase8m_status: success

phase7d_runtime_readiness: implemented_manual_gate

durable_audit_store_status: detached_signature_verifier_prototype

signing_implementation_status: prototype_local_only

signature_runtime_status: local_prototype

signature_verifier_runtime_status: local_prototype

key_management_runtime_status: not_implemented

major_phase_branch_workflow: enabled

## Purpose

Phase 8M implements a local-only detached signature verifier prototype
over Phase 8L outputs: it reads a Phase 8L signed payload descriptor and
detached signature envelope (and optionally the Phase 8L summary),
recomputes the signed payload hash, validates descriptor/envelope schema,
and — only when the in-memory prototype key is present — verifies the
HMAC-SHA256 prototype signature. Phase 8M does not implement production
signing, production verification, or key management runtime.

## Scope

- local-only detached signature verifier prototype
- signed payload descriptor hash verification
- HMAC-SHA256 prototype signature verification only
- descriptor/envelope schema checks
- deterministic verification report
- no signing
- no committed private keys
- no key generation
- no KMS/Secrets Manager
- no backend/API/database
- no key management runtime
- no wrapper behavior change
- no primitive execution
- no vault read/write
- no new mutation path
- no next-gate automation
- no chain execution

## Files

- `scripts/dev/verify_phase8m_detached_signature.py`
- `scripts/dev/run_phase8m_detached_signature_verifier.sh`
- `tests/test_phase8m_detached_signature_verifier_prototype.py`
- `codex/tasks/064-phase8m-detached-signature-verifier-prototype.md`
- `docs/PHASE8M_DETACHED_SIGNATURE_VERIFIER_PROTOTYPE.md`
- additive updates to `docs/ROADMAP.md`
- additive updates to `docs/PROJECT_STATE.md`
- additive updates to `docs/PHASE8L_LOCAL_DETACHED_SIGNATURE_PROTOTYPE.md`
- additive updates to `docs/PHASE8K_KEY_MANAGEMENT_DESIGN.md`
- additive updates to `docs/PHASE8J_DETACHED_SIGNATURE_VERIFIER_DESIGN.md`
- additive updates to `.gitignore`

Note: the Phase 8I/8J/8K regression tests also received a compatibility
whitelist update for the sanctioned Phase 8M runtime filenames; that
whitelist update is mentioned here only and is not part of this
documentation-only task.

## Status model

- `phase8m_status: success` — the local detached signature verifier
  prototype exists, additive documentation pointers exist, and protected
  runtime files stay unchanged.
- `phase7d_runtime_readiness: implemented_manual_gate` — the Phase 7D
  single-gate manual approval wrapper remains the only implemented
  approval runtime; Phase 8M does not change it.
- `durable_audit_store_status: detached_signature_verifier_prototype` —
  the durable audit store status token advances to reflect that a local
  detached signature verifier prototype now exists.
- `signing_implementation_status: prototype_local_only` — signing remains
  a local, non-production HMAC-SHA256 prototype; Phase 8M does not sign
  anything.
- `signature_runtime_status: local_prototype` — the Phase 8L signing
  runtime remains a local prototype; Phase 8M does not change it.
- `signature_verifier_runtime_status: local_prototype` — a local-only
  detached signature verifier runtime now exists.
- `key_management_runtime_status: not_implemented` — no key management
  runtime exists.
- `major_phase_branch_workflow: enabled` — Phase 8M follows the
  major-phase checkpoint-commit-only workflow; no PR is opened for this
  sub-phase alone.

## Local detached signature verifier prototype objective

Provide a working, local-only reference implementation of the Phase 8J
verifier-side interpretation over the Phase 8L descriptor/envelope
outputs: recomputing the signed payload hash, validating descriptor and
envelope schema, and verifying the HMAC-SHA256 prototype signature using
the same in-memory environment-variable prototype key model as Phase 8L,
so future phases can build governed key management and enterprise
verification against a concrete, tested verifier output shape.

## Current trust boundary

- Phase 8I finalized the detached signature design
- Phase 8J designed detached signature verifier interpretation
- Phase 8K designed key management governance
- Phase 8L implemented a local prototype signing runtime
- a local prototype verifier runtime now exists
- no key management runtime exists
- no authenticated operator identity exists
- no governed key custody exists
- no enterprise non-repudiation exists
- a verified prototype signature is evidence only, not approval
- durable audit remains a local/tmp workflow

## Runtime input contract

`scripts/dev/verify_phase8m_detached_signature.py` accepts
`--descriptor-path`, `--envelope-path`, `--summary-path`, and
`--output-dir`. Defaults: descriptor-path
`tmp/phase8l-detached-signature/signed-payload-descriptor.json`;
envelope-path
`tmp/phase8l-detached-signature/detached-signature-envelope.json`;
summary-path
`tmp/phase8l-detached-signature/detached-signature-summary.json`;
output-dir `tmp/phase8m-detached-signature-verifier`.
`scripts/dev/run_phase8m_detached_signature_verifier.sh` forwards all CLI
arguments unchanged to the verifier script. The prototype key is read
only from the `AFFILIATE_PHASE8L_PROTOTYPE_KEY` environment variable.

## Descriptor validation model

The descriptor must be a JSON object containing all 24 required fields:
`payload_schema_version`, `export_manifest_path`, `export_manifest_sha256`,
`bundle_hash`, `computed_manifest_hash`, `report_schema_version`,
`issue_taxonomy_version`, `compatibility_matrix_version`,
`verifier_hardening_status`, `verification_status`, `compatibility_result`,
`incident_classification`, `reviewer_action`, `reviewer_action_required`,
`generated_from_phase`, `generated_by_tool`, `created_at_utc`,
`signing_policy_version`, `signer_id`, `signer_role`,
`signer_identity_assurance`, `key_id`, `key_version`,
`approval_boundary_statement`. Each missing field raises a
`missing_descriptor_field` issue.

## Envelope validation model

The envelope must be a JSON object containing all 21 required fields:
`signature_schema_version`, `signed_payload_sha256`,
`signed_payload_descriptor_path`, `detached_signature_path`,
`signature_algorithm`, `signature_encoding`, `key_id`, `key_version`,
`signer_id`, `signer_role`, `signer_identity_assurance`,
`signing_policy_version`, `signing_timestamp_utc`, `signature_status`,
`signing_status`, `verification_status`, `revocation_status`,
`rotation_epoch`, `approval_boundary_statement`,
`signature_runtime_status`, `signing_implementation_status`. Each missing
field raises a `missing_envelope_field` issue.

## Signed payload hash verification model

`computed_signed_payload_sha256` is the SHA-256 hex digest of the
canonical JSON serialization of the descriptor (`sort_keys=True`,
`separators=(",", ":")`, `ensure_ascii=False`). It is compared against
the envelope's `signed_payload_sha256`. A match sets
`signed_payload_hash_status: match`; a mismatch sets
`signed_payload_hash_status: mismatch` and fails verification with
`incident_classification: signature_integrity_failure`. A hash match is
necessary but is not approval.

## Prototype HMAC verification model

The expected signature is computed as
`hmac.new(raw_key, envelope["signed_payload_sha256"], hashlib.sha256).hexdigest()`
and compared to `detached_signature_value` using `hmac.compare_digest`.
Only `signature_algorithm: hmac-sha256-prototype` and
`signature_encoding: hex` are supported. Verification only proceeds when
the envelope's signed payload hash matches and the algorithm/encoding are
supported.

## Missing input behavior

When the descriptor path or the envelope path resolves safely but does
not exist, the tool writes a report with
`signature_verification_status: skipped_missing_signature_inputs`,
`signature_status: not_present`, `verification_status: empty`, and
`reviewer_action: no_action_required`, and exits 0.

## Missing prototype key behavior

When the descriptor and envelope validate, the hash matches, the
algorithm/encoding are supported, and the envelope signature is present
and ready, but `AFFILIATE_PHASE8L_PROTOTYPE_KEY` is unset, the tool writes
a report with `signature_verification_status:
skipped_missing_prototype_key`, `signature_status: present`,
`verification_status: warning`, and `reviewer_action:
manual_review_required`, and exits 0. When the envelope itself reports
`signature_status: not_ready` or `signing_status:
skipped_missing_prototype_key` (Phase 8L skipped signing), the tool
instead writes `signature_verification_status:
skipped_signature_not_ready` with the same exit 0 behavior. When the
envelope reports `signature_status: not_present`, the tool writes
`signature_verification_status: skipped_signature_not_present` with
`verification_status: empty` and exits 0.

## Invalid descriptor/envelope behavior

When the descriptor or envelope file exists but is not valid JSON, or the
parsed JSON is not an object, the tool writes a report with
`signature_verification_status: failed_invalid_input`,
`verification_status: invalid`, `reviewer_action:
reject_signature_until_resolved`, and exits nonzero. When either file
parses as a JSON object but is missing a required field, the tool writes
`signature_verification_status: failed_schema_validation` with the same
`invalid`/`reject_signature_until_resolved`/nonzero outcome. When the
prototype key is present but `detached_signature_value` is missing, the
tool writes `signature_verification_status:
failed_missing_signature_value` with the same outcome shape.

## Signature mismatch behavior

When the recomputed signed payload hash does not match the envelope
value, the tool writes `signature_verification_status:
failed_signed_payload_hash_mismatch`, `signed_payload_hash_status:
mismatch`, `incident_classification: signature_integrity_failure`, and
exits nonzero. When the prototype key is present and the recomputed HMAC
does not match `detached_signature_value`, the tool writes
`signature_verification_status: failed_signature_mismatch` with the same
`invalid`/`reject_signature_until_resolved`/`signature_integrity_failure`/
nonzero outcome shape. Unsupported `signature_algorithm` or
`signature_encoding` values fail as `failed_unsupported_algorithm` or
`failed_unsupported_encoding` respectively, both nonzero.

## Verification report model

The report JSON top-level fields are: `phase8m_status`,
`durable_audit_store_status`, `phase7d_runtime_readiness`,
`signing_implementation_status`, `signature_runtime_status`,
`signature_verifier_runtime_status`, `key_management_runtime_status`,
`major_phase_branch_workflow`, `signature_verification_status`,
`signature_status`, `verification_status`, `signature_schema_version`,
`signed_payload_sha256`, `computed_signed_payload_sha256`,
`signed_payload_hash_status`, `signature_algorithm`,
`signature_encoding`, `key_id`, `key_version`, `key_status`,
`revocation_status`, `rotation_status`, `signer_id`, `signer_role`,
`signer_identity_assurance`, `failure_count`, `severity_counts`,
`incident_classification`, `reviewer_action`,
`reviewer_action_required`, `descriptor_path`, `envelope_path`,
`summary_path`, `output_dir`, `issues`, `safety_statement`,
`approval_boundary_statement`, `limitations`. Each issue carries
`issue_type`, `severity` (`info`/`warning`/`critical`),
`incident_classification` (`none`/`signature_not_available`/
`signature_integrity_failure`/`key_lifecycle_review_required`/
`policy_review_required`/`signer_identity_review_required`/
`replay_review_required`), `reviewer_action`
(`no_action_required`/`manual_review_required`/
`reject_signature_until_resolved`), and `message`. A matching
`detached-signature-verification.md` renders the same status tokens,
signer/key metadata, issue summary, output paths, safety boundary, and
known limitations.

## Failure taxonomy mapping

| outcome | signature_verification_status | verification_status | incident_classification | exit |
| --- | --- | --- | --- | --- |
| missing descriptor or envelope | `skipped_missing_signature_inputs` | `empty` | `signature_not_available` | 0 |
| invalid JSON / non-object | `failed_invalid_input` | `invalid` | `signature_integrity_failure` | nonzero |
| missing required field | `failed_schema_validation` | `invalid` | `policy_review_required` | nonzero |
| signed payload hash mismatch | `failed_signed_payload_hash_mismatch` | `invalid` | `signature_integrity_failure` | nonzero |
| unsupported algorithm | `failed_unsupported_algorithm` | `invalid` | `policy_review_required` | nonzero |
| unsupported encoding | `failed_unsupported_encoding` | `invalid` | `policy_review_required` | nonzero |
| envelope not_ready / signing skipped | `skipped_signature_not_ready` | `warning` | `signature_not_available` | 0 |
| envelope signature not present | `skipped_signature_not_present` | `empty` | `signature_not_available` | 0 |
| prototype key env var missing | `skipped_missing_prototype_key` | `warning` | `signature_not_available` | 0 |
| signature value missing | `failed_missing_signature_value` | `invalid` | `signature_integrity_failure` | nonzero |
| HMAC match | `verified_local_prototype` | `valid` | `none` | 0 |
| HMAC mismatch | `failed_signature_mismatch` | `invalid` | `signature_integrity_failure` | nonzero |

## Reviewer action mapping

- `no_action_required` — missing signature inputs (nothing to verify yet)
  or a verified prototype signature
- `manual_review_required` — a missing prototype key, a not-ready or
  not-present envelope signature
- `reject_signature_until_resolved` — invalid input, schema validation
  failure, signed payload hash mismatch, unsupported algorithm/encoding,
  missing signature value, or HMAC mismatch

Rules:

- reviewer action is guidance only
- reviewer action is not approval
- reviewer action must not execute a primitive
- reviewer action must not trigger the wrapper
- reviewer action must not trigger the next gate

## Path safety model

The descriptor path, envelope path, and summary path are each rejected if
empty, if they contain a `..` traversal segment, if they are symlinks, if
they resolve outside the repository, or if they resolve under a rejected
source root (`vault`, `docs`, `scripts`, `tests`, `codex`); a path that
resolves safely but does not exist is treated as "missing" rather than an
error (except the summary path, which is always optional). The output
directory is rejected if empty, if it contains a `..` traversal segment,
if it is a symlink, or if it does not resolve to
`tmp/phase8m-detached-signature-verifier` or a path beneath it. Any
rejected path causes a nonzero exit.

## Non-goals

Phase 8M does not implement production signing, does not implement a
production signature verifier, does not implement key management
runtime, does not generate or persist keys, does not implement
KMS/Secrets Manager, does not implement backend/API/database, does not
change Phase 7D wrapper behavior, does not change Phase 8B/8C/8D/8E/8G/8L
runtime behavior, does not execute primitives, does not read or write the
vault, does not trigger the next gate, and does not add chain execution.

## Phase 8L signing prototype boundary

Phase 8L remains the local prototype signing runtime that produces the
descriptor and envelope Phase 8M consumes. Phase 8M does not modify Phase
8L outputs and does not call the Phase 8L signing script automatically.

## Phase 8K key management boundary

Phase 8K remains design-only key management governance. Phase 8M does not
implement key management runtime. `key_management_runtime_status` remains
`not_implemented`.

## Phase 8J verifier design boundary

Phase 8J remains design-only detached signature verifier interpretation.
Phase 8M is the first local runtime implementation of a narrow subset of
that design. `signature_verifier_runtime_status` advances to
`local_prototype`; enterprise verification remains not implemented.

## Phase 8I verifier design boundary

Phase 8I remains the detached signature envelope/payload design source.
Phase 8M does not change the Phase 8I design document.

## Phase 8H verifier boundary

Phase 8H remains the hash-only export integrity verifier. Phase 8M does
not change Phase 8H runtime behavior.

## Phase 8E export boundary

Phase 8E remains the export pack builder. Phase 8M does not modify the
Phase 8E export pack and does not call Phase 8E export automatically.

## Phase 7D approval boundary

Approval remains the Phase 7D selected-gate manual boundary. Phase 8M
does not call the Phase 7D wrapper, does not call primitives, does not
write the vault, and does not trigger the next gate.

## Operator/reviewer use model

An operator runs the Phase 8M runner against an existing Phase 8L
descriptor and envelope to produce a local verification report. A
reviewer treats the resulting `signature_verification_status` and issues
as supplementary evidence only; a verified prototype signature does not
replace, bypass, or substitute for the Phase 7D selected-gate manual
approval boundary.

## Test strategy

Deterministic tests in
`tests/test_phase8m_detached_signature_verifier_prototype.py` exercise:
missing descriptor/envelope inputs, invalid (non-JSON or non-object)
descriptor/envelope, a descriptor or envelope missing a required field,
a signed payload hash mismatch, an unsupported algorithm/encoding, an
envelope with `signature_status: not_ready` or `not_present`, a missing
prototype key, a missing `detached_signature_value`, a matching HMAC
signature, a mismatched HMAC signature, unsafe descriptor/envelope/
summary/output-dir paths, canonical hash determinism, output-file
placement under `tmp/phase8m-detached-signature-verifier/` only, doc
cross-reference regression across
ROADMAP/PROJECT_STATE/PHASE8L/PHASE8K/PHASE8J, protected-runtime-file
non-modification, and a static safety scan of the new files rejecting
secrets, private-key material, and unrelated executable command examples.

## Acceptance criteria

- task exists
- design doc exists
- runtime script exists and is importable/compilable
- shell runner exists and passes `bash -n`
- design doc contains `phase8m_status: success`
- design doc contains `phase7d_runtime_readiness: implemented_manual_gate`
- design doc contains `durable_audit_store_status:
  detached_signature_verifier_prototype`
- design doc contains `signing_implementation_status: prototype_local_only`
- design doc contains `signature_runtime_status: local_prototype`
- design doc contains `signature_verifier_runtime_status: local_prototype`
- design doc contains `key_management_runtime_status: not_implemented`
- design doc contains `major_phase_branch_workflow: enabled`
- missing descriptor or envelope produces `skipped_missing_signature_inputs`
  and exit 0
- unset prototype key with a ready envelope produces
  `skipped_missing_prototype_key` and exit 0
- set prototype key with a matching signature produces
  `verified_local_prototype` and exit 0
- set prototype key with a mismatched signature produces
  `failed_signature_mismatch` and a nonzero exit
- invalid descriptor or envelope produces `failed_invalid_input` and a
  nonzero exit
- a signed payload hash mismatch produces
  `failed_signed_payload_hash_mismatch` and a nonzero exit
- unsafe paths produce a nonzero exit
- outputs are written only under `tmp/phase8m-detached-signature-verifier/`
- ROADMAP, PROJECT_STATE, PHASE8L, PHASE8K, and PHASE8J all reference
  Phase 8M additively
- protected Phase 2G/2H/2I, 6B/6C/6E, 7B, 7D wrapper, and
  8B/8C/8D/8E/8G/8H/8L runtime files remain unchanged
- no backend/API/database file is added by Phase 8M

## Focused verification commands

```text
source .venv/bin/activate
python -m pytest -q tests/test_phase8m_detached_signature_verifier_prototype.py
python -m pytest -q tests/test_phase8l_local_detached_signature_prototype.py
python -m pytest -q tests/test_phase8k_key_management_design.py
python -m pytest -q tests/test_phase8j_detached_signature_verifier_design.py
python -m pytest -q tests/test_phase8i_detached_signature_design_finalization.py
python -m pytest -q tests/test_phase8h_export_integrity_verifier_hardening.py
python -m pytest -q tests/test_phase8g_export_integrity_verifier.py
python -m py_compile scripts/dev/verify_phase8m_detached_signature.py
bash -n scripts/dev/run_phase8m_detached_signature_verifier.sh
```

## Major-phase checkpoint policy

Phase 8M is part of `feature/phase8-signature-governance-completion`.
Phase 8M should create a checkpoint commit only; no PR should be opened
after Phase 8M alone. Because Phase 8M adds runtime code, focused tests
plus Phase 8G-8L regressions and `py_compile`/`bash -n` are required
before moving on. The full suite is deferred to major Phase 8 completion
unless focused tests fail or protected runtime changes occur.

## Known limitations

Phase 8M is a local prototype only. Its verification is HMAC-SHA256
prototype only, not a production signature verifier. No production
signing, no key management runtime, and no governed key custody exist.
No encryption, no authenticated operator identity, and no non-repudiation
exist. No backend/API/database and no production deployment exist.

## Final status target

phase8m_status: success
