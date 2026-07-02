# Phase 8D — Audit Store Query CLI over JSONL

```text
phase8d_status: success
phase7d_runtime_readiness: implemented_manual_gate
durable_audit_store_status: jsonl_query_cli
```

### Purpose

Phase 8D implements a read-only query CLI over the Phase 8B local
append-only JSONL audit store. It filters, sorts, and limits records from
`audit-records.jsonl` and writes a read-only query result. Phase 8D never
appends to or otherwise mutates the source JSONL store.

### Scope

- read-only JSONL query CLI
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
bash scripts/dev/run_phase8d_audit_query.sh [query options]
```

The wrapper never accepts an approval flag and never accepts `--execute`.

### Supported filters

All provided filters combine with AND semantics:

- `--product-id`
- `--report-week`
- `--selected-gate` (`promote`, `decision`, or `finalization`)
- `--operator`
- `--primitive-outcome`
- `--manual-review-status`
- `--incident-id`
- `--hash-status` (`valid`, `invalid`, or `unknown`)

`hash_status` is computed best-effort per record: `valid` if `record_hash`
recomputes and matches, `invalid` if `record_hash` is present but does not
match, and `unknown` if the record has no `record_hash` to verify against.

### Sorting and limit

- sort by `phase8b_ingested_at` (default) or `created_at`
- ascending by default; `--descending` reverses the order
- a record missing the sort field sorts as an empty string
- `--limit` defaults to 100 and must be an integer between 1 and 1000
  inclusive; an out-of-range or non-integer limit is rejected with a
  non-zero exit
- an invalid `--sort-by` value is likewise rejected with a non-zero exit

### Output layout

- `tmp/phase8d-audit-query/audit-query-result.json`
- `tmp/phase8d-audit-query/audit-query-result.md`

### Safety boundary

- the query CLI does not approve anything
- the query CLI does not execute a primitive
- the query CLI does not call the Phase 7D wrapper
- the query CLI does not call the Phase 7B verifier
- the query CLI does not call the Phase 8B ingest writer
- the query CLI does not call the Phase 8C verifier automatically
- the query CLI does not trigger the next gate
- the query CLI does not chain execution
- the query CLI does not append to the JSONL store
- the query CLI does not write the vault
- the query CLI writes only query artifacts under `tmp/phase8d-audit-query`

### Phase 8B and 8C compatibility

- Phase 8D reads the Phase 8B JSONL output.
- Phase 8D does not modify Phase 8B ingest behavior.
- Phase 8D does not replace Phase 8C verifier/reporting.
- Phase 8C should still be used for hash-chain verification of the whole
  store.
- Phase 8D can compute a best-effort per-record hash status for filtering,
  but this is not a substitute for a full Phase 8C hash-chain verification
  pass.

### Operator use

- use Phase 8B to ingest existing audit artifacts.
- use Phase 8C to verify/report store integrity.
- use Phase 8D to query records by product/week/gate/operator/outcome/
  review/incident/hash status.
- Phase 8D query results are evidence lookup, not approval.
- a Phase 8D `warning` result requires manual review.

### Known limitations

- local tmp query report only
- no SQLite index
- no S3/DynamoDB
- no backend/API
- no authenticated identity
- no production deployment
- no retention enforcement
- no full-text search
- no pagination cursor
- no automatic remediation
