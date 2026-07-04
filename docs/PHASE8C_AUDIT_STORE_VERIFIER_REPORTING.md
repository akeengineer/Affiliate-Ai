# Phase 8C — Audit Store Verifier / Reporting over JSONL

```text
phase8c_status: success
phase7d_runtime_readiness: implemented_manual_gate
durable_audit_store_status: jsonl_verifier_reporting
```

### Purpose

Phase 8C implements read-only verifier/reporting over the Phase 8B local
append-only JSONL audit store. It reads `audit-records.jsonl`, recomputes
each record's hash and validates hash-chain continuity, detects duplicates
and malformed lines, and writes a read-only verification/reporting summary.
Phase 8C never appends to or otherwise mutates the source JSONL store.

### Scope

- read-only JSONL verifier/reporting
- no append
- no source store mutation
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
bash scripts/dev/run_phase8c_audit_report.sh [store_path]
```

The wrapper never accepts an approval flag and never accepts `--execute`.

### Input store policy

- default input: `tmp/phase8b-audit-store/audit-records.jsonl`
- a missing store produces an empty report (`verification_status: empty`),
  not a failure
- no `vault/`, `docs/`, `scripts/`, `tests/`, or `codex/` input paths
- no symlink input path
- no path traversal
- the source store is never mutated; it is opened read-only

### Verification model

- line-by-line JSONL parsing; blank lines are ignored
- required field checks against the reporting field list: `audit_record_id`,
  `audit_schema_version`, `source_phase`, `product_id`, `report_week`,
  `selected_gate`, `operator`, `primitive_outcome`, `artifact_hash`,
  `previous_record_hash`, `record_hash`, `manual_review_status`,
  `created_at`, `phase8b_ingested_at`
- `record_hash` recomputation over canonical JSON
  (`sort_keys=True`, `separators=(",", ":")`, `ensure_ascii=False`) of the
  record with `record_hash` and `audit_record_id` both excluded, matching the
  Phase 8B hash-chain model
- `previous_record_hash` chain continuity: the first record must have
  `previous_record_hash` null, and each following record's
  `previous_record_hash` must equal the immediately prior record's stored
  `record_hash`
- duplicate `audit_record_id` detection
- duplicate `artifact_hash` detection
- duplicate `record_hash` detection
- overall status is `valid` (no issues), `warning` (parsed records exist but
  issues were found), `empty` (store missing or has zero non-blank lines), or
  `invalid` (a critical path/store failure prevented verification)

### Reporting model

Reporting summaries group parsed records by:

- `by_product_id`
- `by_report_week`
- `by_selected_gate`
- `by_operator`
- `by_primitive_outcome`
- `by_manual_review_status`

### Output layout

- `tmp/phase8c-audit-report/audit-store-verification.json`
- `tmp/phase8c-audit-report/audit-store-verification.md`

### Safety boundary

- the verifier does not approve anything
- the verifier does not execute a primitive
- the verifier does not call the Phase 7D wrapper
- the verifier does not call the Phase 7B verifier automatically
- the verifier does not trigger the next gate
- the verifier does not chain execution
- the verifier does not append to the JSONL store
- the verifier does not write the vault
- the verifier writes only report artifacts under `tmp/phase8c-audit-report`

### Phase 8B compatibility

- Phase 8C reads the Phase 8B JSONL output.
- Phase 8C does not modify Phase 8B ingest behavior.
- Phase 8C does not replace the Phase 8B writer.
- Phase 8C can detect corruption introduced outside the writer (for example a
  manually edited or truncated JSONL line).

### Operator use

- use Phase 8B to ingest existing audit artifacts.
- use Phase 8C to verify/report the JSONL store.
- keep the Phase 7B verifier as artifact-level verification.
- Phase 8C verifies store-level integrity.
- Phase 8C valid is not approval.
- Phase 8C warning/invalid requires manual review.

### Phase 8D query CLI

Phase 8D adds a read-only query CLI over this JSONL store in
[`PHASE8D_AUDIT_STORE_QUERY_CLI.md`](PHASE8D_AUDIT_STORE_QUERY_CLI.md). Phase
8D queries the JSONL store read-only; it does not replace Phase 8C
verifier/reporting and should be paired with Phase 8C for hash-chain
verification of the whole store.

### Phase 8E export pack

Phase 8E adds a read-only export pack that packages this verification report
alongside Phase 8B/8D evidence in
[`PHASE8E_AUDIT_EXPORT_PACK.md`](PHASE8E_AUDIT_EXPORT_PACK.md). Phase 8E
packages the verification report and evidence read-only; it does not modify
Phase 8C verifier behavior.

### Phase 10B actor attribution audit store integration plan

Phase 10B actor attribution audit store integration plan now exists at
`docs/PHASE10B_ACTOR_ATTRIBUTION_AUDIT_STORE_INTEGRATION_PLAN.md`. Phase 10B
plans future actor-attributed audit reports but does not modify Phase 8C
runtime.

### Phase 10D derived actor-attributed audit report prototype

Phase 10D derived actor-attributed audit report prototype now exists at
`docs/PHASE10D_DERIVED_ACTOR_ATTRIBUTED_AUDIT_REPORT_PROTOTYPE.md`. Phase 10D
may reference audit store verifier reports as evidence context only and does not
modify Phase 8C runtime.

### Known limitations

- local tmp report only
- no SQLite index
- no S3/DynamoDB
- no backend/API
- no authenticated identity
- no production deployment
- no retention enforcement
- a query CLI now exists in Phase 8D
- an export pack now exists in Phase 8E
- no automatic remediation
