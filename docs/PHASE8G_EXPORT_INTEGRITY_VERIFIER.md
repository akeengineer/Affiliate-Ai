# Phase 8G — Export Integrity Verifier Prototype

```text
phase8g_status: success
phase7d_runtime_readiness: implemented_manual_gate
durable_audit_store_status: export_integrity_verifier
signing_implementation_status: not_implemented
```

### Purpose

Phase 8G implements a local hash-only export integrity verifier for Phase
8E export packs. It recomputes sha256 hashes for source evidence and copied
evidence files, recomputes a canonical bundle hash, and best-effort
recomputes a manifest hash if the manifest already carries one, following
the design in
[`PHASE8F_EXPORT_INTEGRITY_SIGNING_DESIGN.md`](PHASE8F_EXPORT_INTEGRITY_SIGNING_DESIGN.md).

### Scope

- local hash-only verifier
- no signing implementation
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

The wrapper never accepts an approval flag and never accepts `--execute`.

### Input export manifest

- default manifest: `tmp/phase8e-audit-export/audit-export-manifest.json`
- a missing manifest produces an empty report (`verification_status: empty`),
  not a failure
- invalid JSON, or a JSON body that is not an object, produces
  `verification_status: invalid` and a non-zero exit
- no `vault/`, `docs/`, `scripts/`, `tests/`, or `codex/` input paths
- no symlink input path
- no path traversal
- the export pack and all source evidence are opened read-only; nothing is
  ever mutated

### Hash-only verification model

- evidence sha256 verification: each `source_evidence` entry with
  `exists: true` and `allowed: true` is re-hashed from disk and compared to
  the manifest's recorded `sha256`
- evidence size verification: `size_bytes` is compared the same way
- copied evidence byte/hash check: each `copied_files` entry is re-hashed
  and compared against the corresponding source evidence's `sha256` when
  available
- a manifest hash is recomputed only if the manifest already carries a
  `manifest_hash` field
- a bundle descriptor and bundle hash are always computed
- overall status is `valid` (no issues), `warning` (issues found but the
  manifest itself was readable), `empty` (manifest missing), or `invalid`
  (a critical path/manifest/report-dir failure)

### Bundle descriptor model

The bundle descriptor is a canonical JSON object (`sort_keys=True`,
`separators=(",", ":")`, `ensure_ascii=False`) built from:

- `source_evidence` reduced to `label`, `path`, `sha256`, `size_bytes`,
  sorted by `label`
- `copied_files` reduced to `path` (the copy's destination) and `sha256`,
  sorted by `path`
- `record_count`, `verification_status`, `query_status`, `phase8e_status`,
  and `durable_audit_store_status`, taken directly from the manifest

`computed_bundle_hash` is the sha256 of this canonical descriptor.

### Output layout

- `tmp/phase8g-export-integrity/export-integrity-verification.json`
- `tmp/phase8g-export-integrity/export-integrity-verification.md`

### Safety boundary

- the verifier does not approve anything
- verified export is not approval
- a hash-valid export is not approval
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

### Phase 8F signing boundary

- Phase 8G is hash-only.
- Phase 8G does not implement detached signatures.
- Phase 8G does not handle private keys.
- Phase 8G does not implement encryption.
- Phase 8G prepares evidence integrity checks before any future signing
  implementation.
- the Phase 8F design remains the signing governance source of truth; this
  phase only implements the hash-only prerequisite it recommended.

### Operator/reviewer use

- use Phase 8E to generate the export pack.
- use Phase 8G to verify hash integrity.
- use Phase 8C for JSONL store-level verification.
- use Phase 8D for query/filtering.
- a Phase 8G verification result is evidence integrity only, not approval.
- a `warning` or `invalid` status requires manual review.

### Phase 8H hardening

Phase 8H hardens this verifier in place in
[`PHASE8H_EXPORT_INTEGRITY_VERIFIER_HARDENING.md`](PHASE8H_EXPORT_INTEGRITY_VERIFIER_HARDENING.md).
Phase 8H preserves this verifier's CLI shape and output paths exactly, and
adds a stable report schema, an issue taxonomy, severity, incident
classification, a reviewer action mapping, and a Phase 8E manifest
compatibility matrix. A verified export remains not approval.

### Phase 8I detached signature design

Phase 8I finalizes the detached signature design for future signing over
this verifier's output in
[`PHASE8I_DETACHED_SIGNATURE_DESIGN_FINALIZATION.md`](PHASE8I_DETACHED_SIGNATURE_DESIGN_FINALIZATION.md).
Phase 8I does not modify this verifier's behavior. Phase 8J's future
verifier design now exists in
[`PHASE8J_DETACHED_SIGNATURE_VERIFIER_DESIGN.md`](PHASE8J_DETACHED_SIGNATURE_VERIFIER_DESIGN.md)
and does not modify this verifier's behavior.

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
- a hardened schema/taxonomy/reviewer-action layer now exists in Phase 8H
- a finalized detached signature design now exists in Phase 8I

### Phase 10E export sidecar design/prototype

Phase 10E export sidecar design/prototype now exists at
`docs/PHASE10E_EXPORT_SIDECAR_DESIGN_PROTOTYPE.md`. Phase 10E may reference
export integrity reports as evidence context only. Verified export remains not
approval and Phase 10E does not modify Phase 8G runtime.
