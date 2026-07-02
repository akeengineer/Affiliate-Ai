# Task 057 — Phase 8F Export Integrity / Signing Design

phase8f_status: success

phase7d_runtime_readiness: implemented_manual_gate

durable_audit_store_status: export_integrity_signing_design

## Purpose

Design export integrity and signing governance for Phase 8E export packs.
Phase 8F is docs/tests design-only: it proposes a manifest hash model, an
evidence file hash model, a bundle hash model, a detached signature model, a
signing key ownership policy, key storage options, a verification ceremony,
a reviewer trust model, a signature failure model, and a tamper-evidence
model. Phase 8F implements no signing, no verifier, and no key management.

## Scope

Phase 8F is docs/tests design-only. It adds a design document and a
docs-contract test, adds no runtime script, changes no Phase 8E export
behavior, changes no Phase 7D wrapper behavior, changes no approval logic,
executes no primitive, performs no vault read/write, adds no new mutation
path, and adds no backend/API/database/network behavior. It generates no
keys and handles no private key material.

## Files

- `codex/tasks/057-phase8f-export-integrity-signing-design.md`
- `docs/PHASE8F_EXPORT_INTEGRITY_SIGNING_DESIGN.md`
- `tests/test_phase8f_export_integrity_signing_design.py`
- additive updates to `docs/ROADMAP.md`
- additive updates to `docs/PROJECT_STATE.md`
- additive updates to `docs/PHASE8E_AUDIT_EXPORT_PACK.md`
- additive updates to `docs/PHASE8D_AUDIT_STORE_QUERY_CLI.md`

## Status model

- `success`: the export integrity/signing design exists, additive
  documentation pointers exist, `phase7d_runtime_readiness` remains
  `implemented_manual_gate`, `signing_implementation_status` is
  `design_only`, no runtime script/key/certificate file is added, and
  protected runtime files stay unchanged.
- `failed`: required design coverage is missing, additive docs regress, a
  runtime script or key material is added, or a protected runtime surface
  changes.

## Export integrity objective

Provide a deterministic design for verifying that a Phase 8E export pack has
not been tampered with, and for a future detached signature that a reviewer
can check, without implementing any signing, verification, or key
management code in this phase.

## Current export trust limitation

- Phase 8E creates local export packs
- Phase 8E records source hashes
- Phase 8E does not sign exports
- Phase 8E does not encrypt exports
- Phase 8E does not authenticate operator identity
- Phase 8E does not provide non-repudiation
- an export pack is evidence packaging, not a trusted approval artifact
- durable audit remains a local/tmp workflow

## Manifest hash model

Proposed: canonical manifest JSON (sorted keys, stable separators, volatile
fields such as `generated_at` excluded); `manifest_hash = sha256(canonical
manifest)`; the manifest hash covers source evidence metadata and hashes;
the manifest hash excludes private key material; the manifest hash is
tamper-evidence only, not approval.

## Evidence file hash model

Proposed: sha256 per evidence file; file size; relative path inside the
export pack; evidence label; copy byte identity (a copy must be
byte-identical to its source); missing evidence entries recorded with a null
hash; invalid evidence entries still hashed as raw bytes, with parse failure
reported separately; a future evidence hash mismatch marks that evidence
untrusted and requires manual review.

## Bundle hash model

Proposed: a deterministic bundle descriptor listing every evidence label
paired with its hash (or null) plus `manifest_hash`, in a fixed order,
canonicalized the same way; `bundle_hash` computed from that canonical
descriptor; the bundle hash exists for tamper evidence only and is not
approval.

## Detached signature model

Proposed (design only, no implementation): a future signature computed over
`bundle_hash`; stored in a signature file separate from the export manifest;
carrying signer identity metadata, key id, signing timestamp, algorithm, and
policy version; never containing private key material; never mutating
source evidence; never triggering approval or the next gate. No
implementation code or command examples for signing are included.

## Signing key ownership policy

Roles: operator, reviewer, system owner, security owner. Policy: explicit
key ownership; private keys never committed, never written into docs, never
placed in a tmp export pack; a key rotation policy and a revocation policy
are both required before any signing implementation; signer identity is not
strong identity until an authenticated operator identity system exists.

## Key storage options considered

Compared conceptually, with no implementation in Phase 8F: local offline key
file, OS keychain, hardware security key, cloud KMS, enterprise secrets
manager. Each is compared on strengths, weaknesses, operational fit, and
recommended future phase. Phase 8F implements none of these options.

## Verification ceremony

Proposed reviewer ceremony: receive the export pack; verify source file
hashes; verify the manifest hash; verify the bundle hash; verify the
detached signature if present in a future phase; verify signer/key
metadata; compare the result to the expected policy version and key set;
record the reviewer's decision; require manual review on any failure; never
treat verification success alone as approval of any Phase 7D gate.

## Reviewer trust model

The reviewer verifies evidence integrity, not approval; must check Phase
7B/8C/8D evidence context and the Phase 7H operator runbook context; must
not rely solely on a signature; must verify the signing policy version; must
escalate any mismatch or failure.

## Signature failure behavior

A missing signature in the current phase is expected. A future signature
mismatch means a tamper-evidence failure. A key id mismatch, an expired or
revoked key, an unknown signer, or a hash mismatch all require manual
review. A verification failure must not auto-delete evidence, must not
retry execution, must not trigger rollback, and must not trigger the next
gate.

## Tamper-evidence model

A hash mismatch marks the affected evidence untrusted. A broken bundle hash
or a signature mismatch marks the whole export untrusted. An untrusted
export requires manual review. Tamper-evidence status is separate from
approval status and must not mutate the audit store.

## Privacy and secret handling

No private keys in the repository or export pack; no secrets or approval
flags in the manifest; no API keys or affiliate secrets; no raw terminal
dump containing secrets; reviewer logs/screenshots must be sanitized;
signing metadata must avoid sensitive personal data.

## Non-goals

Phase 8F does not implement signing, a verification script, key generation,
private key handling, encryption, KMS/Secrets Manager, or backend/API/
database. It does not modify Phase 8E export behavior, Phase 7D wrapper
behavior, execute primitives, approve anything, trigger the next gate, add
chain execution, or create a production deployment.

## Phase 8E export boundary

The Phase 8E export pack remains read-only packaging. Phase 8F only designs
a future integrity/signing layer and does not change Phase 8E runtime
behavior. A future signing step should consume the export pack after
generation, as a separate, additive step, and must not alter source
evidence.

## Phase 7D approval boundary

A signature is not approval; a verified export is not approval; reviewer
verification is not primitive execution. Signing must not bypass the
selected-gate manual approval boundary, must not set approval flags, must
not trigger the Phase 7D wrapper, and must not trigger the next gate.
Approval remains the Phase 7D selected-gate manual boundary, unchanged by
this design.

## Future implementation path

- Phase 8G: Export Integrity Verifier Prototype (local hash-only
  verification, no private keys)
- Phase 8H: Detached Signature Design Finalization or Prototype (still no
  backend)
- Phase 8I: Key Management Design
- Phase 8J: Optional encrypted export design
- Phase 8K: Optional enterprise KMS integration design

None of the above are implemented in Phase 8F.

## Test strategy

Deterministic docs-contract tests: task and design doc exist; required
status tokens exist; scope/non-goal tokens exist; current-limitation
coverage; design-objective coverage; all required design sections exist;
key-storage-option coverage; "signature is not approval" assertion
coverage; signature-failure-behavior assertion coverage;
ROADMAP/PROJECT_STATE/PHASE8E/PHASE8D pointers; ROADMAP/PROJECT_STATE token
regression; protected runtime file hash regression; absence of any Phase 8F
runtime/signing/key/certificate/database/backend/API file; and a
static-safety scan over only the two new Phase 8F files.

## Acceptance criteria

- task exists
- design doc exists
- design doc contains `phase8f_status: success`
- design doc contains `phase7d_runtime_readiness: implemented_manual_gate`
- design doc contains
  `durable_audit_store_status: export_integrity_signing_design`
- design doc contains `signing_implementation_status: design_only`
- design doc states docs/tests design-only
- design doc states no signing/key-generation/private-key-handling/
  encryption/KMS/Secrets-Manager implementation
- design doc states no Phase 8E export behavior change
- design doc states no Phase 7D wrapper behavior change
- design doc states no primitive execution and no vault read/write
- design doc states no new mutation path
- ROADMAP, PROJECT_STATE, PHASE8E_AUDIT_EXPORT_PACK, and
  PHASE8D_AUDIT_STORE_QUERY_CLI all reference Phase 8F additively
- protected Phase 6B/6C/6E/7B/7D/7G/8B/8C/8D/8E runtime files remain
  unchanged
- no new runtime, signing, key, certificate, database, backend, or API file
  is added by Phase 8F

## Verification commands

```text
source .venv/bin/activate
umask 022

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

find scripts/dev -type f -name "*.sh" -exec chmod 755 {} \;

env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q

grep -RInE "/home/[^/]+/Affiliate-Ai" scripts/ || echo "scripts clean"
git diff --check
git status --short --branch
```

## Known limitations

Phase 8F is design only. No signing, verifier, or key-management
implementation exists. No encryption, no authenticated operator identity, no
non-repudiation, no backend/API/database, and no production deployment
exist.

## Final status target

phase8f_status: success
