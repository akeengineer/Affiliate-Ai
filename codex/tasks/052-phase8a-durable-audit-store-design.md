# Task 052 — Phase 8A Durable Audit Store Design

phase8a_status: success

phase7d_runtime_readiness: implemented_manual_gate

## Purpose

Design a future durable audit store for Phase 7D single-gate wrapper and Phase
7B audit verifier artifacts. Phase 8A is docs/tests-task only: it proposes a
record schema, a storage abstraction, backend options, and a migration path
from tmp-local audit output. Phase 8A implements no storage and changes no
runtime behavior.

## Scope

Phase 8A is docs/tests-task only. It adds a design document and a docs-contract
test, changes no runtime wrapper behavior, changes no approval logic, executes
no primitive, performs no vault read/write, adds no new runtime command, adds
no new mutation path, and adds no backend/API/database/network behavior.

## Files

- `codex/tasks/052-phase8a-durable-audit-store-design.md`
- `docs/PHASE8A_DURABLE_AUDIT_STORE_DESIGN.md`
- `tests/test_phase8a_durable_audit_store_design.py`
- additive updates to `docs/ROADMAP.md`
- additive updates to `docs/PROJECT_STATE.md`
- additive updates to `docs/PHASE7H_OPERATOR_RUNBOOK.md`
- additive updates to `docs/RELEASE_SNAPSHOT_PHASE7_RUNTIME_LIVE.md`

## Status model

- `success`: the durable audit store design exists, additive documentation
  pointers exist, Phase 7D runtime readiness remains
  `implemented_manual_gate`, `durable_audit_store_status` is `design_only`, and
  protected runtime files stay unchanged.
- `failed`: required design coverage is missing, additive docs regress, or a
  protected runtime surface changes.

## Durable audit objective

Provide a deterministic, append-only, tamper-evident audit record design for
Phase 7D wrapper invocations and Phase 7B verifier results, without
implementing storage or changing the existing tmp-local audit write path.

## Current tmp-local limitation

- tmp-local audit is not durable
- audit artifacts are not queryable over time
- audit artifacts are not tamper-evident by default
- a durable audit store is not implemented

## Target durable audit capabilities

The design targets: append-only records, immutable record identity,
product_id/report_week/selected_gate linkage, wrapper intent audit capture,
wrapper result audit capture, primitive outcome reference, Phase 7B verifier
result reference, operator identity, reason and intent capture, emergency stop
state capture, precondition/result summaries, artifact hashing, schema
versioning, manual review status, incident reference, and retention metadata.

## Non-goals

- no storage implementation
- no durable audit writer
- no database
- no SQLite implementation
- no S3 implementation
- no DynamoDB implementation
- no backend/API
- no external APIs/URLs/network behavior
- no new runtime command or mutation path
- no primitive execution
- no vault read/write
- no Phase 7D wrapper behavior change
- no Phase 7B verifier behavior change
- no approve-all, chain execution, next-gate automation, autopublish,
  marketplace connector, or production deployment

## Audit record model

Proposed logical fields (design only, no implementation):

`audit_record_id`, `audit_schema_version`, `source_phase`, `product_id`,
`report_week`, `selected_gate`, `wrapper_version`, `operator`,
`approval_reason`, `approval_intent`, `execution_mode`,
`emergency_stop_state`, `mutation_attempted`, `primitive_name`,
`primitive_outcome`, `phase6b_packet_ref`, `phase6c_verifier_ref`,
`phase6e_plan_ref`, `phase7b_verifier_ref`, `intent_audit_ref`,
`result_audit_ref`, `precondition_summary`, `result_summary`,
`manual_review_status`, `incident_id`, `created_at`, `completed_at`,
`artifact_hash`, `previous_record_hash`, `retention_class`.

## Audit artifact lifecycle

Proposed lifecycle: Phase 7D wrapper writes tmp intent/result audit artifacts
as it does today; Phase 7B verifier validates them as it does today; a future
(not-built-in-8A) durable writer would read those tmp artifacts plus the Phase
7B verifier result, construct one durable record per invocation, compute
`artifact_hash`/`previous_record_hash`, and append it to durable storage,
referencing rather than duplicating the tmp artifact content.

## Storage abstraction design

Proposed abstraction: a write interface (append one immutable record), a read
interface (fetch by id or list by product_id/report_week/selected_gate/time
range), and a verification interface (recompute artifact hash and validate
chaining). Backend implementations plug in behind this abstraction without
changing the record schema or the Phase 7D/7B integration boundary. No
interface, writer, or reader is implemented in Phase 8A.

## Backend options considered

Compared conceptually: local append-only JSONL, local SQLite, S3 object
store, DynamoDB table, external SIEM/log archive. See the design document for
the full tradeoff comparison. None are implemented in Phase 8A.

## Recommended local-first implementation path

- Phase 8B: local append-only JSONL prototype
- Phase 8C: verifier/reporting over JSONL
- Phase 8D: optional SQLite index
- Phase 8E: optional S3/DynamoDB design for team/production

Each remains a separate, explicitly approved future phase. Phase 8A implements
none of them.

## Integrity and tamper-evidence model

Proposed: every record carries `artifact_hash` and `previous_record_hash` for
hash-chaining; the store is append-only with no in-place edits; a verification
pass can recompute the chain and detect gaps or mismatches. No hashing or
chaining code is implemented in Phase 8A.

## Privacy and secret handling

A future durable record must never include raw secrets, tokens, credentials,
private-key material, approval flag truthy assignments, vault paths (absent a
future explicitly approved phase), or operator-local filesystem paths; it
carries only non-sensitive summary fields already used by Phase 7B artifacts.

## Operator identity model

The `operator` field remains free-text/non-authenticated, consistent with the
current Phase 7D/7H posture. Phase 8A proposes no authentication
implementation; it only reserves the field in the schema.

## Phase 7B verifier compatibility

The proposed durable record references the Phase 7B verifier result via
`phase7b_verifier_ref` and does not replace or re-implement Phase 7B
validation. The Phase 7B verifier remains read-only and evidence-only. A
future durable writer would run after Phase 7B verification, not instead of
it.

## Phase 7D wrapper integration boundary

This design does not change Phase 7D wrapper behavior. The wrapper continues
writing tmp intent/result audit artifacts exactly as it does today. A future
durable writer would be a separate, additive consumer of those tmp artifacts.
No new mutation path, runtime command, or dependency is added to the wrapper.
`phase7d_runtime_readiness` remains `implemented_manual_gate`.

## Failure and recovery model

Proposed: a failed durable-store append must not block or roll back the Phase
7D wrapper's primitive execution or tmp audit write; tmp remains the source of
truth until durable storage is proven; failures require manual review, not
automatic retry; a broken hash chain requires manual investigation, not
automatic repair. No failure-handling code is implemented in Phase 8A.

## Migration plan from tmp-local

Proposed: keep tmp-local artifacts as the source of truth through Phase 8B;
build the JSONL writer as an additive read-of-tmp process; backfill historical
tmp artifacts as a one-time, explicitly approved future operation; run both
tmp and durable output side by side until verified; only after explicit
approval would tmp-local output be deprecated. Phase 8A performs no migration.

## Retention and cleanup policy

Proposed: every record carries `retention_class`; cleanup is retention-driven
archival/rotation, never in-place edit or deletion of an active record;
incident-linked records default to the longest retention class. No retention
or cleanup code is implemented in Phase 8A.

## Query/reporting model

Proposed query surface: by product_id, report_week, selected_gate, time range,
manual_review_status, and incident_id, plus an aggregate reporting layer for
operator review. No query or reporting code is implemented in Phase 8A.

## Test strategy

Deterministic docs-contract tests: task and design doc exist; required status
tokens exist; scope/non-goal tokens exist; current-limitation coverage;
design-objective coverage; audit schema field coverage; backend options and
recommended path coverage; integrity/privacy/operator/verifier/integration
coverage; failure/recovery/retention/query coverage; ROADMAP/PROJECT_STATE/
PHASE7H_OPERATOR_RUNBOOK/RELEASE_SNAPSHOT_PHASE7_RUNTIME_LIVE pointers;
ROADMAP/PROJECT_STATE token regression; protected runtime file hash
regression; absence of new runtime/storage/database/backend/API files; and a
static-safety scan over only the two new Phase 8A files.

## Acceptance criteria

- task exists
- design doc exists
- design doc contains `phase8a_status: success`
- design doc contains `phase7d_runtime_readiness: implemented_manual_gate`
- design doc contains `durable_audit_store_status: design_only`
- design doc states docs/tests-task only and design only
- design doc states no storage/database/backend/API implementation
- design doc states no Phase 7D wrapper behavior change
- design doc states no primitive execution and no vault read/write
- design doc states no new mutation path
- ROADMAP, PROJECT_STATE, PHASE7H_OPERATOR_RUNBOOK, and the Phase 7 runtime
  live snapshot all reference Phase 8A additively
- protected Phase 6B/6C/6E/7B/7D/7G runtime files remain unchanged
- no new runtime, storage, database, backend, or API file is added by Phase 8A

## Verification commands

```text
source .venv/bin/activate

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

env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q

grep -RInE "/home/[^/]+/Affiliate-Ai" scripts/ || echo "scripts clean"
git diff --check
git status --short --branch
```

## Known limitations

Phase 8A is design only. No storage, writer, or reader exists. Durable audit
storage remains unimplemented; audit artifacts remain tmp-local until a future
phase implements Phase 8B. Operator identity remains unauthenticated. No
backend/API/database, S3/DynamoDB/SIEM integration, hash-chaining, retention,
or query code exists.

## Final status target

phase8a_status: success
