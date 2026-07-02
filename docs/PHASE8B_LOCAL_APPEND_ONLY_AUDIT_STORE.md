# Phase 8B — Local Append-only Audit Store Prototype

```text
phase8b_status: success
phase7d_runtime_readiness: implemented_manual_gate
durable_audit_store_status: local_append_only_prototype
```

### Purpose

Phase 8B implements a local append-only JSONL audit store prototype for
ingesting existing audit artifacts. It follows the design in
[`PHASE8A_DURABLE_AUDIT_STORE_DESIGN.md`](PHASE8A_DURABLE_AUDIT_STORE_DESIGN.md)
and is the first runtime implementation of that design: Phase 8B reads one
existing audit artifact (normally a Phase 7D wrapper output) and appends one
normalized, hash-chained durable audit record to a local, gitignored JSONL
store. Phase 8B does not change Phase 7D wrapper behavior and executes no
approval primitive.

### Scope

- local-first runtime prototype
- ingest-only
- append-only JSONL
- hash-chain record integrity
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
bash scripts/dev/run_phase8b_audit_ingest.sh <audit_artifact_path> [operator_note]
```

The wrapper never accepts an approval flag and never accepts `--execute`.

### Store layout

- `tmp/phase8b-audit-store/audit-records.jsonl`
- `tmp/phase8b-audit-store/audit-ingest-summary.json`
- `tmp/phase8b-audit-store/audit-ingest-summary.md`

All three paths live under the gitignored `tmp/` tree and are never committed.

### Input artifact policy

- the audit artifact must be an existing JSON object
- normally under `tmp/`
- no `vault/`, `docs/`, `scripts/`, `tests/`, or `codex/` input paths
- no symlink input path
- no path traversal
- the source artifact is never mutated; it is opened read-only

### Record model

Every normalized record carries these fields:

`audit_record_id`, `audit_schema_version`, `source_phase`, `product_id`,
`report_week`, `selected_gate`, `wrapper_version`, `operator`,
`approval_reason`, `approval_intent`, `execution_mode`,
`emergency_stop_state`, `mutation_attempted`, `primitive_name`,
`primitive_outcome`, `phase6b_packet_ref`, `phase6c_verifier_ref`,
`phase6e_plan_ref`, `phase7b_verifier_ref`, `intent_audit_ref`,
`result_audit_ref`, `source_audit_artifact_ref`, `precondition_summary`,
`result_summary`, `manual_review_status`, `incident_id`, `created_at`,
`completed_at`, `artifact_hash`, `previous_record_hash`, `record_hash`,
`retention_class`, `phase8b_ingested_at`, `phase8b_store_version`.

Fields are extracted best-effort from the source artifact using flexible
aliases (for example `approval_intent` also accepts
`gate_specific_approval_intent`, and `primitive_outcome` also accepts
`outcome`). Absent fields are stored as `null`; ingest never fails because an
optional field is missing.

### Hash-chain model

- `artifact_hash` = sha256 of the source audit artifact's raw bytes.
- `previous_record_hash` = `record_hash` of the last valid line in
  `audit-records.jsonl`, or `null` for the first record in the store.
- `record_hash` = sha256 of the canonical JSON (`sort_keys=True`,
  `separators=(",", ":")`, `ensure_ascii=False`) of the normalized record
  with `record_hash` and `audit_record_id` both excluded. `audit_record_id`
  is derived from `record_hash`, so it cannot be part of its own hash input.
- `audit_record_id` = `"audit-"` followed by the first 16 hex characters of
  `record_hash`.
- Verification recomputes the canonical JSON of a stored record with
  `record_hash` and `audit_record_id` removed, hashes it, and compares the
  result to the stored `record_hash`.
- Records are appended one JSON line at a time; no previous line is ever
  edited.

### Duplicate handling

If a record with the same `artifact_hash` already exists in the store,
ingest does not append a duplicate. It exits `0` with `ingest_status:
duplicate_skipped`, `duplicate: true`, `appended: false`, and the existing
record's `audit_record_id` in the summary.

### Failure behavior

Ingest exits non-zero and appends nothing on:

- a missing, non-file, symlinked, or unsafe source path
- a source path outside the repository or under `vault/`, `docs/`,
  `scripts/`, `tests/`, or `codex/`
- invalid JSON, or a JSON body that is not an object
- a custom `--store-dir` outside `tmp/phase8b-audit-store`
- a corrupted or malformed line in the existing JSONL store (hash-chain read
  failure)

### Safety boundary

- the ingest writer does not approve anything
- the ingest writer does not execute a primitive
- the ingest writer does not call the Phase 7D wrapper
- the ingest writer does not call the Phase 7B verifier automatically
- the ingest writer does not trigger the next gate
- the ingest writer does not chain execution
- the ingest writer does not write the vault
- the ingest writer does not write outside `tmp/phase8b-audit-store`

### Phase 7B verifier compatibility

- Phase 7B remains read-only.
- Phase 7B valid is not approval.
- Phase 8B may ingest verifier references if present in the source artifact
  (via `phase7b_verifier_ref`).
- Phase 8B does not run the Phase 7B verifier automatically.
- invalid verifier output still requires manual review; Phase 8B does not
  infer approval or validity from ingestion alone.

### Operator use

1. run the Phase 7G safe demo pack first for acceptance.
2. run the Phase 7H checklist before any real use of the Phase 7D wrapper.
3. after wrapper execution and audit generation, run the Phase 7B verifier
   manually.
4. then ingest the existing audit artifact with Phase 8B.
5. record the ingest summary output manually until a query/reporting command
   exists.

### Phase 8C verifier / reporting

Phase 8C adds a read-only verifier/reporting command over this JSONL store in
[`PHASE8C_AUDIT_STORE_VERIFIER_REPORTING.md`](PHASE8C_AUDIT_STORE_VERIFIER_REPORTING.md).
Phase 8C verifies and reports the JSONL store read-only; it does not modify
Phase 8B ingest behavior and does not replace this writer.

### Known limitations

- local tmp prototype only
- JSONL only, no SQLite index
- no S3/DynamoDB backend
- no backend/API
- no authenticated operator identity
- no production deployment
- no automatic migration
- no retention enforcement
- a query/reporting command now exists in Phase 8C
