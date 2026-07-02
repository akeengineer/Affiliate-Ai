# Phase 8A — Durable Audit Store Design

```text
phase8a_status: success
phase7d_runtime_readiness: implemented_manual_gate
durable_audit_store_status: design_only
```

## Purpose

This document designs a future durable audit store for Phase 7D single-gate
wrapper and Phase 7B audit verifier artifacts. Phase 8A is design only: it
proposes an audit record schema, a storage abstraction, backend options, and a
migration path from the current tmp-local audit output. Phase 8A does not
implement storage, does not implement a durable writer, and does not change
Phase 7D wrapper behavior.

## Scope

- docs/tests-task only
- design only
- no storage implementation
- no database
- no SQLite implementation
- no S3 implementation
- no DynamoDB implementation
- no backend
- no FastAPI
- no API routes
- no external APIs
- no external URLs
- no network behavior
- no new runtime command
- no new mutation path
- no primitive execution
- no vault read
- no vault write
- no Phase 7D wrapper behavior change
- no Phase 7B verifier behavior change

`durable_audit_store_status: design_only` for the entire lifetime of Phase 8A.

## Current limitation

The current audit posture, inherited from Phase 7B/7D/7H, has these
limitations:

- tmp-local audit is not durable
- audit artifacts live under `tmp/phase7d-single-gate-wrapper/` and
  `tmp/phase7b-audit-verifier/`, which are gitignored and operator-machine-local
- audit artifacts are not queryable over time; there is no index, no cross-run
  aggregation, and no time-range query surface
- audit artifacts are not tamper-evident by default; nothing chains one record
  to the previous record or detects post-write modification
- a durable audit store is not implemented; every phase through 7H records
  audit artifacts as tmp-local JSON only, and Phase 7H explicitly notes that
  operators must "archive or record audit outputs manually until durable audit
  store exists"

## Design objectives

The durable audit store design targets the following properties for a future
implementation phase:

- append-only: records are written once and never mutated in place
- immutable record identity: every record has a stable `audit_record_id` that
  never changes after creation
- product_id/report_week/selected_gate linkage: every record is queryable by
  the same product_id, report_week, and selected_gate keys already used by
  Phase 6B/6C/6E/7D/7B
- wrapper intent audit capture: the record captures the Phase 7D wrapper's
  pre-execution intent audit (operator, reason, intent, selected gate)
- wrapper result audit capture: the record captures the Phase 7D wrapper's
  post-execution result audit (outcome, mutation_attempted, primitive result)
- primitive outcome reference: the record references the primitive outcome
  without re-executing or re-deriving it
- Phase 7B verifier result reference: the record references the Phase 7B
  verifier's validation result for the same audit artifact
- operator identity field: every record carries an `operator` field
- reason and intent fields: every record carries `approval_reason` and
  `approval_intent` fields
- emergency stop state: every record captures `emergency_stop_state` at
  execution time
- precondition summary: every record carries a `precondition_summary`
- result summary: every record carries a `result_summary`
- artifact hash: every record carries an `artifact_hash` of the underlying
  audit artifact content
- schema version: every record carries `audit_schema_version`
- manual review status: every record carries `manual_review_status`
- incident reference: every record carries an optional `incident_id`
- retention metadata: every record carries a `retention_class`

## Non-goals

- Phase 8A does not implement storage.
- Phase 8A is design only.
- Phase 8A adds no database, no backend, no API, and no storage
  implementation.
- Phase 8A makes no Phase 7D wrapper behavior changes.
- Phase 8A performs no primitive execution.
- Phase 8A performs no vault read/write.
- Phase 8A adds no new mutation path.
- Phase 8A does not add approve-all, global approval, multi-gate execution,
  next-gate automation, or chain execution.
- Phase 8A does not add autopublish, campaign launch, or a marketplace
  connector.
- Phase 8A does not change Phase 6B/6C/6E, Phase 7B verifier, Phase 7D wrapper,
  or Phase 7G safe demo behavior.

## Audit record model

The proposed logical audit record (a future schema, not implemented in Phase
8A) has these fields:

- `audit_record_id`
- `audit_schema_version`
- `source_phase`
- `product_id`
- `report_week`
- `selected_gate`
- `wrapper_version`
- `operator`
- `approval_reason`
- `approval_intent`
- `execution_mode`
- `emergency_stop_state`
- `mutation_attempted`
- `primitive_name`
- `primitive_outcome`
- `phase6b_packet_ref`
- `phase6c_verifier_ref`
- `phase6e_plan_ref`
- `phase7b_verifier_ref`
- `intent_audit_ref`
- `result_audit_ref`
- `precondition_summary`
- `result_summary`
- `manual_review_status`
- `incident_id`
- `created_at`
- `completed_at`
- `artifact_hash`
- `previous_record_hash`
- `retention_class`

`previous_record_hash` is the field that would give the store hash-chained
tamper-evidence in a future implementation; Phase 8A defines the field but
implements no chaining logic.

## Audit artifact lifecycle

Proposed logical lifecycle for a future durable audit record (design only):

1. Phase 7D wrapper writes an intent audit artifact under tmp before primitive
   execution, as it does today.
2. Phase 7D wrapper writes a result audit artifact under tmp after primitive
   execution or prevention, as it does today.
3. Phase 7B verifier validates the tmp audit artifact, as it does today.
4. A future durable audit writer (not built in Phase 8A) would read the
   existing tmp artifacts and the Phase 7B verifier result, construct one
   durable audit record per gate invocation, compute `artifact_hash` and
   `previous_record_hash`, and append the record to durable storage.
5. The durable record would reference, not duplicate, the tmp artifact
   content: `intent_audit_ref` and `result_audit_ref` point at the tmp
   artifact paths and their hashes.
6. Manual review, incident response, and retention transitions would update
   `manual_review_status`, `incident_id`, and `retention_class` only, never the
   append-only record body.

Phase 8A implements none of these steps; this section is a proposed design
only.

## Storage abstraction design

A future durable audit store should be designed behind a storage abstraction
so the record model and the Phase 7D/7B integration boundary stay stable
regardless of backend:

- a write interface: append one immutable audit record
- a read interface: fetch by `audit_record_id`, or list by
  `product_id`/`report_week`/`selected_gate`/time range
- a verification interface: recompute `artifact_hash` and validate
  `previous_record_hash` chaining
- backend implementations plug in behind this abstraction without changing the
  record schema, the Phase 7D wrapper, or the Phase 7B verifier

Phase 8A defines the shape of this abstraction conceptually; it implements no
interface, no writer, and no reader.

## Backend options considered

Options compared for a future durable audit store, conceptually only:

- **local append-only JSONL** — one line per record, append-only file
  semantics, simplest operational model, naturally durable-yet-local, easy to
  hash-chain, easy to `grep`/`jq` for ad hoc queries; weakest built-in query
  performance at large record counts.
- **local SQLite** — indexed local queries by product_id/report_week/gate/time
  range, still local-first and single-file, adds schema/migration overhead
  relative to JSONL; a reasonable index layer over an append-only log rather
  than a replacement for it.
- **S3 object store** — durable, versioned, off-machine storage suitable for a
  team setting; introduces network dependency, external credentials, and an
  external API surface that is explicitly out of scope for local-first Phase 1
  through Phase 7 operation.
- **DynamoDB table** — durable, queryable, scalable managed store; introduces
  a backend/database dependency, external credentials, and network calls, all
  explicitly out of scope for the current local-first posture.
- **external SIEM/log archive** — good for compliance-grade long-term
  retention and correlation with other security telemetry; introduces an
  external system dependency and is the heaviest-weight option, appropriate
  only after a local-first design is proven.

## Recommended local-first implementation path

Phase 8A recommends, but does not implement, this future sequence:

- Phase 8B: local append-only JSONL prototype
- Phase 8C: verifier/reporting over JSONL
- Phase 8D: optional SQLite index
- Phase 8E: optional S3/DynamoDB design for team/production

Each future phase remains separately scoped and separately approved before
implementation, matching the existing Phase 6/7 pattern of design-then-approve.

## Integrity and tamper-evidence model

Proposed integrity properties for a future implementation:

- every durable record carries `artifact_hash`, a content hash of the
  referenced tmp audit artifact
- every durable record carries `previous_record_hash`, chaining it to the
  prior record in the same store
- the store is append-only; no in-place edit of a written record is permitted
- a verification pass can recompute the hash chain and detect any gap or
  mismatch
- Phase 8A defines this model conceptually; it implements no hashing, no
  chaining, and no verification code

## Privacy and secret handling

A future durable audit record must:

- never include raw secrets, tokens, or credentials
- never include private-key material
- never include approval flag truthy assignments
- never include vault paths unless a future explicitly approved phase revisits
  that boundary
- never include operator-local filesystem paths
- carry only the same non-sensitive summary fields the Phase 7B audit
  artifacts already carry today (precondition/result summaries, not raw
  command output)

## Operator identity model

A future durable audit record captures an `operator` field consistent with the
Phase 7D wrapper's current operator identity input:

- operator identity remains a free-text/non-authenticated field, matching the
  current Phase 7D/7H posture ("operator identity is not authenticated")
- Phase 8A proposes no authentication implementation
- a future phase may explicitly revisit authenticated operator identity; Phase
  8A only reserves the `operator` field in the record schema

## Phase 7B verifier compatibility

- the proposed durable record references the Phase 7B verifier result via
  `phase7b_verifier_ref`; it does not replace or re-implement Phase 7B
  validation
- Phase 7B verifier remains read-only and evidence-only under this design
- a future durable audit writer would run after Phase 7B verification, not
  instead of it
- the Phase 7B verifier's existing tmp-artifact input contract is unchanged by
  this design

## Phase 7D wrapper integration boundary

- this design does not change Phase 7D wrapper behavior
- the Phase 7D wrapper continues to write intent/result audit artifacts under
  tmp exactly as it does today
- a future durable audit writer would be a separate, additive consumer of
  those tmp artifacts, not a modification to the wrapper's write path
- the wrapper does not gain a new mutation path, a new runtime command, or a
  new dependency from this design
- `phase7d_runtime_readiness` remains `implemented_manual_gate` and is
  unaffected by Phase 8A

## Failure and recovery model

Proposed failure/recovery properties for a future implementation:

- a failed durable-store append must not block or roll back the Phase 7D
  wrapper's primitive execution or its tmp audit write; tmp remains the source
  of truth until durable storage is proven
- a failed durable-store append must be visible (not silently dropped) so an
  operator can manually record the gap
- durable-store read/verification failures require manual review, not
  automatic retry
- recovery from a broken hash chain requires manual investigation, not
  automatic repair
- Phase 8A defines these properties conceptually only; no failure-handling
  code is implemented

## Migration plan from tmp-local

Proposed migration plan for a future phase (not executed in Phase 8A):

1. keep tmp-local audit artifacts as the source of truth during and after
   Phase 8B
2. build the append-only JSONL writer as an additive, read-of-tmp process
3. backfill historical tmp audit artifacts into the JSONL store as a one-time,
   explicitly approved operation in a future phase
4. keep both tmp and durable output side by side until the durable store is
   verified against a sample of historical records
5. only after explicit approval would tmp-local output be deprecated as the
   sole record; Phase 8A does not deprecate or remove tmp-local output

## Retention and cleanup policy

Proposed retention properties for a future implementation:

- every record carries a `retention_class` so different record types (routine
  vs. incident-linked) can have different retention windows
- append-only storage means "cleanup" is a retention-driven archival/rotation
  operation, never an in-place edit or deletion of an active record
- incident-linked records (`incident_id` set) should default to the longest
  retention class
- Phase 8A proposes this policy shape only; no retention or cleanup code is
  implemented

## Query/reporting model

Proposed query/reporting surface for a future implementation:

- query by `product_id`
- query by `report_week`
- query by `selected_gate`
- query by time range (`created_at`/`completed_at`)
- query by `manual_review_status`
- query by `incident_id`
- a reporting layer could aggregate counts per gate/operator/week for operator
  review, without introducing a backend/API
- Phase 8A proposes this surface conceptually; no query or reporting code is
  implemented

## Recommended next phase

- Phase 8B: local append-only JSONL prototype, as the first durable-audit
  implementation phase, separately scoped and separately approved

## Known limitations

- Phase 8A is design only; no storage, writer, or reader exists.
- Durable audit storage remains unimplemented after Phase 8A.
- Audit artifacts remain tmp-local until a future phase implements Phase 8B.
- Operator identity remains unauthenticated.
- No backend/API/database exists.
- No S3/DynamoDB/SIEM integration exists.
- No hash-chaining, retention, or query code exists.
