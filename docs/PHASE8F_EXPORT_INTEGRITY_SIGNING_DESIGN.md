# Phase 8F — Export Integrity / Signing Design

```text
phase8f_status: success
phase7d_runtime_readiness: implemented_manual_gate
durable_audit_store_status: export_integrity_signing_design
signing_implementation_status: design_only
```

### Purpose

Phase 8F designs export integrity and signing governance for Phase 8E
export packs. Phase 8F does not implement signing. It proposes a manifest
hash model, an evidence file hash model, a bundle hash model, a detached
signature model, a signing key ownership policy, key storage options, a
verification ceremony, a reviewer trust model, a signature failure model,
and a tamper-evidence model, all as design only.

### Scope

- docs/tests design-only
- no signing implementation
- no key generation
- no private key handling
- no encryption implementation
- no KMS/Secrets Manager implementation
- no backend/API/database
- no runtime script
- no wrapper behavior change
- no primitive execution
- no vault read/write
- no new mutation path
- no next-gate automation
- no chain execution

### Current export trust limitation

- Phase 8E creates local export packs
- Phase 8E records source hashes
- Phase 8E does not sign exports
- Phase 8E does not encrypt exports
- Phase 8E does not authenticate operator identity
- Phase 8E does not provide non-repudiation
- an export pack is evidence packaging, not a trusted approval artifact
- durable audit remains a local/tmp workflow

### Design objectives

Export integrity/signing governance must eventually support:

- manifest hash
- evidence file hashes
- bundle hash
- detached signature
- public verification metadata
- signer identity field
- signing timestamp
- key identifier
- signing policy version
- reviewer verification result
- tamper-evidence failure state
- manual review status
- no approval trigger
- no next-gate trigger
- no chain execution trigger

### Manifest hash model

- the canonical manifest JSON uses sorted keys and stable separators
  (`sort_keys=True`, `separators=(",", ":")`, `ensure_ascii=False`), matching
  the canonical JSON convention already used by Phase 8B/8C/8D
- volatile fields such as `generated_at` are excluded from the canonicalized
  content used to compute `manifest_hash`, so the hash reflects evidence
  content rather than wall-clock generation time
- `manifest_hash = sha256(canonical_manifest)`
- the manifest hash covers source evidence metadata and hashes (labels,
  paths, sha256 values, sizes, record/warning counts, and summaries)
- the manifest hash does not include private key material
- the manifest hash is a tamper-evidence value only; a matching manifest
  hash is not approval

### Evidence file hash model

- sha256 per evidence file, computed the same way Phase 8E already computes
  `source_evidence[].sha256`
- file size in bytes
- relative path inside the export pack (or the original repository-relative
  source path when no copy was made)
- the evidence label (`audit_records_jsonl`, `verification_json`,
  `verification_md`, `query_json`, `query_md`)
- copy byte identity: an evidence copy must be byte-identical to its source,
  exactly as Phase 8E already guarantees by construction
- missing evidence entries: recorded with a null hash and `exists: false`,
  matching Phase 8E's existing `missing_evidence` handling
- invalid evidence entries: a file that fails to parse (invalid JSON, wrong
  shape) is still hashed as raw bytes; parse failure is a separate,
  independently reported condition from hash computation
- evidence hash mismatch behavior: if a future verifier recomputes a file's
  sha256 and it differs from the recorded value, that evidence is untrusted
  and requires manual review; it is never silently accepted

### Bundle hash model

- a deterministic bundle descriptor lists, in a fixed and documented order,
  every evidence label paired with its `sha256` (or null if missing), plus
  the `manifest_hash` itself
- the ordered list of evidence file hashes and the ordered list of metadata
  hashes (currently just `manifest_hash`) are concatenated into one
  canonical bundle descriptor using the same canonical JSON convention
- `bundle_hash` is computed from the canonical bundle descriptor
- the bundle hash exists for tamper evidence only: it lets a reviewer detect
  that any evidence file, or the manifest itself, changed after export
- the bundle hash is not approval

### Detached signature model

A future detached signature would be:

- computed over `bundle_hash` (or an equivalent signed payload descriptor
  derived from it), not over the raw evidence bytes directly
- stored in a signature file separate from the export manifest, so the
  manifest and its signature can be distributed, retained, or rotated
  independently
- accompanied by signer identity metadata, a key identifier, a signing
  timestamp, the signing algorithm, and the signing policy version
- free of any private key material in its own content
- non-mutating: producing or checking a signature never alters the source
  evidence, the manifest, or the export pack's existing files
- non-triggering: producing or checking a signature never triggers approval
  or the next gate

Phase 8F does not include implementation code or command examples for
signing; the above is a description of a future signature's required shape
and properties only.

### Signing key ownership policy

Roles:

- operator: runs Phase 8B/8C/8D/8E; does not own a signing key by default
- reviewer: verifies an export pack's integrity and signature in a future
  phase; does not own a signing key by default
- system owner: owns the infrastructure a future signing key would live on
- security owner: owns signing key issuance, rotation, and revocation
  policy

Policy:

- signing key ownership must be explicit; no implicit or shared ownership
- a private key must never be committed to the repository
- a private key must never be written into audit/export documentation
- a private key must never be placed inside a tmp export pack
- a key rotation policy is required before any signing implementation
- a revocation policy is required before any signing implementation
- signer identity must not be treated as strong identity until an
  authenticated operator identity system exists; until then, a signer
  identity field is metadata, not proof

### Key storage options considered

Compared conceptually, with no implementation in Phase 8F:

- **local offline key file**
  - strengths: simplest to reason about, no external dependency, fully
    local-first, consistent with the project's current architecture
  - weaknesses: weakest protection against key theft/loss, no built-in
    rotation, manual custody burden on the security owner
  - operational fit: reasonable for a first prototype phase, given the
    project's local-first posture
  - recommended phase: Phase 8G/8H prototype only, never production
- **OS keychain**
  - strengths: better at-rest protection than a bare file, native OS
    integration, no server dependency
  - weaknesses: platform-specific behavior, harder to script consistently
    across operator machines, still single-machine custody
  - operational fit: a reasonable step up from a local file for a
    single-operator local workflow
  - recommended phase: an alternative to Phase 8G/8H, still design-first
- **hardware security key**
  - strengths: strong protection against key exfiltration, well-understood
    signing ceremony, good non-repudiation properties
  - weaknesses: hardware dependency, operational friction, recovery/backup
    complexity, cost
  - operational fit: appropriate once signing moves beyond prototype and
    real reviewer trust is at stake
  - recommended phase: Phase 8I key management design, still design-first
- **cloud KMS**
  - strengths: managed rotation/revocation, strong access control,
    auditable key usage, no local key material at rest
  - weaknesses: introduces a network dependency and an external service,
    directly conflicts with the current local-first, no-external-API
    posture until an explicitly approved phase revisits that boundary
  - operational fit: only appropriate for a team/production posture, not
    the current local-first phase
  - recommended phase: Phase 8K, explicitly gated behind a future
    production-readiness decision
- **enterprise secrets manager**
  - strengths: centralized secret lifecycle management, integrates with
    broader organizational security tooling, strong audit trails
  - weaknesses: heaviest-weight option, requires organizational
    infrastructure the project does not currently have, network dependency
  - operational fit: only appropriate once the project has a team/
    production deployment target
  - recommended phase: Phase 8K, alongside or instead of cloud KMS

Phase 8F implements none of these options; it records the comparison only.

### Verification ceremony

A future reviewer verification ceremony:

1. receive the export pack
2. verify each source file's sha256 against `source_evidence[].sha256`
3. verify the manifest hash by recomputing it from the canonical manifest
4. verify the bundle hash by recomputing it from the canonical bundle
   descriptor
5. verify the detached signature, if present, in a future phase
6. verify signer identity and key metadata (key id, algorithm, policy
   version) against the expected signing policy
7. compare the verification result to the expected policy version and key
   set
8. record the reviewer's decision (accepted / rejected / needs-review)
9. require manual review on any failure at any step above
10. never treat verification success, by itself, as approval of any Phase
    7D gate

### Reviewer trust model

- the reviewer verifies evidence integrity, not approval
- the reviewer does not approve a mutation by verifying a signature
- the reviewer must check Phase 7B/8C/8D evidence context, not just the
  Phase 8E export pack in isolation
- the reviewer must check the Phase 7H operator runbook context for the
  underlying Phase 7D wrapper invocation
- the reviewer must not rely solely on a signature; signature verification
  is one input among several
- the reviewer must verify the signing policy version matches what is
  expected for the current phase
- the reviewer must escalate any mismatch or failure rather than resolve it
  unilaterally

### Signature failure behavior

- a missing signature in the current phase is expected, since Phase 8F
  implements no signing
- a future signature mismatch means a tamper-evidence failure
- a key id mismatch requires manual review
- an expired or revoked key requires manual review
- an unknown signer requires manual review
- a hash mismatch (manifest, evidence, or bundle) requires manual review
- a verification failure must not auto-delete evidence
- a verification failure must not retry execution
- a verification failure must not trigger rollback
- a verification failure must not trigger the next gate

### Tamper-evidence model

- a hash mismatch marks the affected evidence untrusted
- a broken bundle hash marks the whole export untrusted
- a signature mismatch marks the export untrusted
- an untrusted export requires manual review
- tamper-evidence status is separate from approval status; they are never
  conflated
- tamper-evidence status must not mutate the audit store

### Privacy and secret handling

- no private keys in the repository
- no private keys in the export pack
- no secrets in the manifest
- no approval flags in the manifest
- no API keys
- no affiliate secrets
- no raw terminal dump if it contains secrets
- reviewer logs/screenshots must be sanitized before sharing
- signing metadata must avoid sensitive personal data

### Non-goals

Phase 8F does not:

- implement signing
- implement a verification script
- generate keys
- handle private keys
- implement encryption
- implement KMS/Secrets Manager
- implement backend/API/database
- modify Phase 8E export behavior
- modify Phase 7D wrapper behavior
- execute primitives
- approve anything
- trigger the next gate
- add chain execution
- create a production deployment

### Phase 8E export boundary

- the Phase 8E export pack remains read-only packaging
- Phase 8F only designs a future integrity/signing layer
- Phase 8F does not change Phase 8E runtime behavior
- a future signing step should consume the export pack after generation,
  as a separate, additive step
- future signing must not alter source evidence

### Phase 7D approval boundary

- a signature is not approval
- a verified export is not approval
- reviewer verification is not primitive execution
- signing must not bypass the selected-gate manual approval boundary
- signing must not set approval flags
- signing must not trigger the Phase 7D wrapper
- signing must not trigger the next gate
- approval remains the Phase 7D selected-gate manual boundary, unchanged by
  this design

### Future implementation path

- Phase 8G: Export Integrity Verifier Prototype — local hash-only
  verification (manifest hash, evidence hashes, bundle hash), no private
  keys
- Phase 8H: Detached Signature Design Finalization or Prototype, still no
  backend
- Phase 8I: Key Management Design
- Phase 8J: Optional encrypted export design
- Phase 8K: Optional enterprise KMS integration design

None of the above are implemented in Phase 8F.

### Phase 8G verifier

Phase 8G implements the hash-only export integrity verifier this design
recommended, in
`docs/PHASE8G_EXPORT_INTEGRITY_VERIFIER.md`. Phase 8G implements no signing
or key management; it verifies evidence and bundle hashes only. A verified
export is not approval.

### Phase 8H verifier hardening

Phase 8H hardens the Phase 8G hash-only verifier before any detached
signature implementation, in
`docs/PHASE8H_EXPORT_INTEGRITY_VERIFIER_HARDENING.md`: a stable report
schema, an issue taxonomy, severity, incident classification, a reviewer
action mapping, and a compatibility matrix. Phase 8H implements no signing
and no keys.

### Known limitations

- design only
- no signing implementation
- no verifier implementation
- no key management
- no encryption
- no authenticated operator identity
- no non-repudiation
- no backend/API/database
- no production deployment
- a hash-only verifier now exists in Phase 8G
