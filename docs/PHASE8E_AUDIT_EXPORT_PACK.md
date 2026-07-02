# Phase 8E — Audit Export Pack

```text
phase8e_status: success
phase7d_runtime_readiness: implemented_manual_gate
durable_audit_store_status: export_pack
```

### Purpose

Phase 8E implements a read-only audit export pack over Phase 8B/8C/8D local
evidence. It bundles or summarizes the Phase 8B JSONL audit store, the
optional Phase 8C verification report, and the optional Phase 8D query
result into a single reviewable export manifest and Markdown summary. Phase
8E never appends to or otherwise mutates any source evidence file.

### Scope

- read-only export pack
- no append
- no source evidence mutation
- no wrapper behavior change
- no primitive execution
- no vault read/write
- no backend/API/database
- no SQLite/S3/DynamoDB
- no network behavior
- no new mutation path
- no next-gate automation
- no chain execution

### Runtime command

```text
bash scripts/dev/run_phase8e_audit_export.sh [export options]
```

The wrapper never accepts an approval flag and never accepts `--execute`.

### Input evidence

- the Phase 8B JSONL store (`tmp/phase8b-audit-store/audit-records.jsonl`)
- the Phase 8C verification JSON/Markdown report
  (`tmp/phase8c-audit-report/audit-store-verification.{json,md}`)
- the Phase 8D query JSON/Markdown result
  (`tmp/phase8d-audit-query/audit-query-result.{json,md}`)
- any of the four Phase 8C/8D evidence files may be missing; a missing
  optional file is recorded as missing evidence, not a failure
- a missing Phase 8B store produces an empty export pack, not a failure

### Export layout

- `tmp/phase8e-audit-export/audit-export-manifest.json`
- `tmp/phase8e-audit-export/audit-export-summary.md`
- with `--include-copies`, byte-identical evidence copies under
  `tmp/phase8e-audit-export/evidence/`:
  - `audit-records.jsonl`
  - `audit-store-verification.json`
  - `audit-store-verification.md`
  - `audit-query-result.json`
  - `audit-query-result.md`

### Manifest model

The export manifest carries: `phase8e_status`,
`durable_audit_store_status`, `phase7d_runtime_readiness`, `export_status`,
`export_dir`, `generated_at`, `include_copies`, `source_evidence`,
`missing_evidence`, `source_hashes`, `record_count`, `invalid_line_count`,
`warning_count`, `verification_status`, `query_status`, `summaries`,
`copied_files`, `safety_statement`, and `limitations`. Each `source_evidence`
entry carries `label`, `path`, `exists`, `allowed`, `sha256`, `size_bytes`,
and `copied_to`. Reporting summaries group all valid store records by
`product_id`, `report_week`, `selected_gate`, `operator`,
`primitive_outcome`, and `manual_review_status`.

### Source hash model

Every existing input's sha256 and byte size are recorded in
`source_evidence` and `source_hashes` before any copy is made. When
`--include-copies` is set, each copy is verified byte-identical to its
source by construction (the copy is a direct byte-for-byte write of the
bytes already hashed); source files are opened read-only throughout and are
never modified.

### Missing evidence behavior

- `empty`: the Phase 8B store is missing, or has zero valid records
- `success`: the export pack was generated with at least one valid record,
  no invalid lines/reports, and no missing optional evidence
- `warning`: the export pack was generated but missing optional evidence,
  invalid JSONL lines, or invalid optional report JSON was found
- `invalid` only applies to a critical path/export-dir validation failure,
  which aborts the run entirely (non-zero exit, no manifest written)

### Safety boundary

- the export pack does not approve anything
- the export pack does not execute a primitive
- the export pack does not call the Phase 7D wrapper
- the export pack does not call the Phase 7B verifier
- the export pack does not call the Phase 8B ingest writer
- the export pack does not call the Phase 8C verifier
- the export pack does not call the Phase 8D query CLI
- the export pack does not trigger the next gate
- the export pack does not chain execution
- the export pack does not append to the JSONL store
- the export pack does not write the vault
- the export pack writes only export artifacts under
  `tmp/phase8e-audit-export`

### Phase 8B/8C/8D compatibility

- Phase 8E consumes Phase 8B/8C/8D outputs as evidence.
- Phase 8E does not modify Phase 8B ingest, Phase 8C verifier, or Phase 8D
  query behavior.
- Phase 8C should still be used for store-level hash-chain verification.
- Phase 8D should still be used for query/filtering of individual records.
- Phase 8E is packaging/review support only, not a replacement for either.

### Operator/reviewer use

- use Phase 8B to ingest existing audit artifacts.
- use Phase 8C to verify/report store integrity.
- use Phase 8D to query relevant records.
- use Phase 8E to create a reviewable export pack summarizing all of the
  above.
- a Phase 8E export is evidence packaging, not approval.
- a Phase 8E `warning` result requires manual review.

### Phase 8F export integrity / signing design

Phase 8F designs the future signing/integrity governance layer for this
export pack in
[`PHASE8F_EXPORT_INTEGRITY_SIGNING_DESIGN.md`](PHASE8F_EXPORT_INTEGRITY_SIGNING_DESIGN.md).
Phase 8F does not modify Phase 8E export behavior; it is design only. A
signature, once implemented in a future phase, is not approval.

### Phase 8G export integrity verifier

Phase 8G implements a local hash-only verifier over this export pack's
manifest in
[`PHASE8G_EXPORT_INTEGRITY_VERIFIER.md`](PHASE8G_EXPORT_INTEGRITY_VERIFIER.md).
Phase 8G verifies export integrity read-only; it does not modify Phase 8E
export behavior. A verified export is not approval.

### Known limitations

- local tmp export only
- no archive signing
- no encryption
- no SQLite index
- no S3/DynamoDB
- no backend/API
- no authenticated identity
- no production deployment
- no retention enforcement
- no automated distribution
- an integrity/signing design now exists in Phase 8F
- no automatic remediation
