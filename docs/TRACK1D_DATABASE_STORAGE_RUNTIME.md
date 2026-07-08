# Track 1D — Database/Storage Runtime

track1d_status: success

track1c_status: success
track1b_status: success
track1a_status: success
phase14_status: blocked_planning_only
phase13_status: success
phase12g_status: success
phase12f_status: success
phase12e_status: success
phase12d_status: success
phase12c_status: success
phase12b_status: success
phase12a_status: success
phase7d_runtime_readiness: implemented_manual_gate

selected_runtime_domain: backend/API/database runtime
runtime_domain_selection_status: selected
implementation_approval_status: track1d_local_storage_implemented
implementation_track_status: implementation_track_1_started
runtime_mode: local-only
storage_runtime: SQLite local-first MVP
database_storage_runtime_status: implemented_in_track1d
product_crud_status: not_implemented
insight_generation_status: not_implemented
recommendation_runtime_status: not_implemented
production_promotion_status: not_approved
production_deployment_status: not_approved
production_authentication_status: deferred
rbac_enforcement_status: deferred
production_signing_status: deferred
verifier_runtime_status: deferred
key_custody_runtime_status: deferred
phase7d_boundary_status: preserved

## 1. Track 1D Purpose

Track 1D implements the local database/storage runtime for the first usable
local product slice.

Track 1D uses SQLite for local-first MVP storage.

Track 1D continues Implementation Track 1 — Backend/API/Database Usable Product Slice.

Track 1D is an explicit local product-slice runtime exception to the earlier Phase 1 Obsidian-only/no-database constraint.

The Track 1D exception is limited to SQLite local-first MVP storage for Implementation Track 1.

The Track 1D exception does not approve production database runtime.

The Track 1D exception does not approve production promotion.

The Track 1D exception does not approve production deployment.

Track 1D does not implement Product or AffiliateOffer full CRUD API.

Track 1D does not implement insight generation.

Track 1D does not implement recommendation runtime.

Track 1D preserves the Phase 7D selected-gate manual boundary.

## 2. Relationship to Track 1A

Track 1A selects backend/API/database runtime as the first runtime domain for
the first usable local product slice.

Track 1D is the first approved storage-runtime implementation inside that
selected runtime domain.

Track 1D is a post-Track-1A approved local runtime exception only. It does not
reinterpret Track 1A as production database approval, production promotion
approval, or production deployment approval.

## 3. Relationship to Track 1B

Track 1B defines SQLite as the default storage choice for the first local
product slice at planning level only.

Track 1D implements that Track 1B SQLite plan in the smallest repo-consistent
runtime form using local-only `sqlite3`.

Track 1D does not widen Track 1B into Track 1E Product Core API scope.

## 4. Relationship to Track 1C

Track 1C implements the local backend/API skeleton and intentionally leaves
database/storage runtime deferred.

Track 1D follows Track 1C by adding the first approved local database/storage
runtime and the consistent `GET /runtime/status` storage fields.

Track 1D does not add Product/AffiliateOffer full CRUD API endpoints to the
Track 1C surface.

## 5. Local Database/Storage Runtime Scope

Selected Runtime Domain: backend/API/database runtime

Implementation Track: Implementation Track 1 — Backend/API/Database Usable Product Slice

Product Goal: first usable local product slice

Runtime Mode: local-only

Storage Runtime: SQLite local-first MVP

Production Promotion Status: not approved

Production Deployment Status: not approved

Production Authentication Status: deferred

RBAC Enforcement Status: deferred

Production Signing Status: deferred

Verifier Runtime Status: deferred

Key Custody Runtime Status: deferred

Phase 7D Boundary Status: preserved

Track 1D scope is limited to local SQLite configuration, deterministic schema
initialization, reset/dev seed behavior, repository/data access foundation,
schema tests, and consistent storage status integration.

## 6. SQLite Local-First Storage Decision

SQLite is the chosen Track 1D storage runtime because it requires no external
infrastructure, no secrets, and no cloud service. It keeps the first usable
local product slice deterministic and easy to reset for tests and demos.

The decision remains local-first MVP only. Track 1D does not approve
PostgreSQL/Aurora runtime or any production database runtime.

## 7. Database Schema Contract

Track 1D creates exactly these planning-aligned foundation tables:

- `products`
- `affiliate_offers`
- `sources`
- `collection_runs`
- `insights`
- `recommendations`

Each table uses a small deterministic schema with text primary keys, required
timestamp columns, and product relationships where needed. The schema exists to
prove the storage foundation works, not to finalize a full Track 1E API model.

### Schema Table Matrix

| Table | Purpose | Required Columns | Relationship | Seed Behavior | Track Introduced |
| --- | --- | --- | --- | --- | --- |
| products | core local product record | `id`, `name`, `marketplace`, `status`, `created_at`, `updated_at` | parent table for all product-slice rows | one deterministic demo product row | Track 1D |
| affiliate_offers | one local affiliate offer record | `id`, `product_id`, `program_name`, `commission_model`, `created_at`, `updated_at` | belongs to `products` | one deterministic demo offer row | Track 1D |
| sources | one provenance/source record | `id`, `product_id`, `source_type`, `source_ref`, `created_at` | belongs to `products` | one deterministic demo source row | Track 1D |
| collection_runs | one local collection execution record | `id`, `product_id`, `status`, `started_at`, `created_at` | belongs to `products` | one deterministic demo collection run row | Track 1D |
| insights | one stored deterministic insight artifact | `id`, `product_id`, `insight_type`, `summary`, `created_at` | belongs to `products` | one deterministic demo insight row | Track 1D |
| recommendations | one stored deterministic recommendation artifact | `id`, `product_id`, `recommendation_type`, `reason`, `created_at` | belongs to `products` | one deterministic demo recommendation row | Track 1D |

## 8. Migration/Init Plan

Track 1D uses deterministic `CREATE TABLE IF NOT EXISTS` schema creation with
standard-library `sqlite3`.

Initialization lives under `scripts/dev/track1d_local_storage.py` and is
invoked through `scripts/dev/run_track1d_local_storage.py` or the shell wrapper.

Track 1D does not introduce an external migration service, cloud migration
toolchain, or production DDL workflow.

## 9. Reset and Dev Seed Plan

Track 1D reset behavior removes the local SQLite file and reinitializes the
schema. This keeps the environment safe and repeatable for local demos and
tests.

Track 1D seed behavior inserts one deterministic row into each required table.
It is intentionally small and stable so schema proof stays clear and local-only.

## 10. Repository/Data Access Plan

Track 1D adds a repository/data access foundation in
`scripts/dev/track1d_repository.py`.

The repository boundary owns small SQL read/write helpers, table inspection,
and row-count queries. It does not implement application services or full CRUD
API behavior.

### Repository Contract Matrix

| Repository Area | Required Behavior | Allowed Operations | Forbidden Operations | Track Introduced |
| --- | --- | --- | --- | --- |
| schema inspection | list Track 1D tables deterministically | read sqlite schema metadata | schema migration planning beyond Track 1D | Track 1D |
| product repository | read one seeded product and count rows | get by id, count rows | full Product CRUD API service | Track 1D |
| affiliate offer repository | read seeded offers by product | list offers by `product_id`, count rows | full AffiliateOffer CRUD API service | Track 1D |
| shared repository helpers | expose connection and simple local row inspection | connect, close, count rows | workflow orchestration or HTTP routing | Track 1D |

## 11. Storage Status Contract

Track 1D storage status is exposed through the local storage module and, when
consistent, through Track 1C `GET /runtime/status`.

Required runtime status values:

- `database_storage_runtime_status: implemented in Track 1D as SQLite local-first MVP`
- `storage_runtime: SQLite local-first MVP`
- `product_crud_status: not implemented in Track 1D`
- `insight_generation_status: not implemented in Track 1D`

### Runtime Status Matrix

| Status Field | Required Value | Purpose | Boundary Signal | Track Introduced |
| --- | --- | --- | --- | --- |
| `database_storage_runtime_status` | `implemented in Track 1D as SQLite local-first MVP` | declare Track 1D storage runtime availability | local-only SQLite status only | Track 1D |
| `storage_runtime` | `SQLite local-first MVP` | name the approved storage runtime | no production database implied | Track 1D |
| `product_crud_status` | `not implemented in Track 1D` | declare Track 1E boundary remains closed | no Product Core API in Track 1D | Track 1D |
| `insight_generation_status` | `not implemented in Track 1D` | declare Track 1F logic boundary remains closed | no insight generation in Track 1D | Track 1D |
| `runtime_mode` | `local-only` | preserve local-only runtime boundary | no production runtime implied | Track 1D |

## 12. Deferred Product CRUD Scope

Track 1D does not implement Product or AffiliateOffer full CRUD API.

Track 1D may create storage tables and repository primitives, but it does not
add create/list/get/patch endpoints, application services, or workflow handlers
for full Product Core API behavior.

Track 1E is the first approved point for Product Core API implementation, if Track 1D is accepted.

## 13. Deferred Insight Generation Scope

Track 1D does not implement insight generation.

Any deterministic insight request handling, orchestration, or derived analysis
runtime remains deferred to a later track.

## 14. Deferred Recommendation Runtime Scope

Track 1D does not implement recommendation runtime.

Stored `recommendations` rows exist only as schema/runtime foundation and demo
seed proof. They do not constitute a live recommendation engine.

## 15. Deferred Security and Hardening Scope

Production Authentication Status: deferred

RBAC Enforcement Status: deferred

Production Signing Status: deferred

Verifier Runtime Status: deferred

Key Custody Runtime Status: deferred

### Deferred Implementation Matrix

| Deferred Area | Current Status | Deferred Reason | First Eligible Track | Required Future Approval |
| --- | --- | --- | --- | --- |
| Product full CRUD API | deferred | Track 1D is storage-foundation only | Track 1E | explicit later-track approval |
| AffiliateOffer full CRUD API | deferred | Track 1D is storage-foundation only | Track 1E | explicit later-track approval |
| CollectionRun workflow API | deferred | Track 1D stores schema only, not workflow behavior | Track 1E | explicit later-track approval |
| Insight generation | deferred | Track 1D adds storage only, not generation logic | Track 1F | explicit later-track approval |
| Recommendation runtime | deferred | Track 1D adds storage only, not runtime recommendations | Track 1F | explicit later-track approval |
| production database runtime | not approved | Track 1D is local-only SQLite MVP | explicit later track | explicit later-track approval |
| PostgreSQL/Aurora runtime | deferred | local SQLite MVP is the only approved storage runtime | explicit later track | explicit later-track approval |
| production authentication | deferred | Track 1D does not add production identity runtime | explicit later track | explicit later-track approval |
| RBAC enforcement | deferred | Track 1D does not add production authorization runtime | explicit later track | explicit later-track approval |
| production signing | deferred | Track 1D does not add signing runtime | explicit later track | explicit later-track approval |
| verifier runtime | deferred | Track 1D does not add verifier runtime | explicit later track | explicit later-track approval |
| key custody runtime | deferred | Track 1D does not add key custody runtime | explicit later track | explicit later-track approval |
| production deployment | not approved | Track 1D remains local-only | explicit later track | explicit later-track approval |
| cloud infrastructure | deferred | Track 1D adds no cloud runtime | explicit later track | explicit later-track approval |
| CI/CD deployment | deferred | Track 1D adds no deployment pipeline | explicit later track | explicit later-track approval |

## 16. Production Database Exclusion

The Track 1D exception does not approve production database runtime.

Track 1D does not introduce a production database service, managed SQL
platform, or production data migration path.

## 17. Production Promotion Exclusion

The Track 1D exception does not approve production promotion.

Production Promotion Status: not approved

Track 1D implementation does not convert local SQLite runtime into production
promotion approval.

## 18. Production Deployment Exclusion

The Track 1D exception does not approve production deployment.

Production Deployment Status: not approved

Track 1D adds no deployment manifest, no cloud infrastructure, and no CI/CD
deployment pipeline.

## 19. Phase 7D Manual Boundary Preservation

Track 1D preserves the Phase 7D selected-gate manual boundary.

Phase 7D Boundary Status: preserved

Track 1D does not bypass, widen, automate, or replace the selected-gate manual
boundary.

## 20. Test Coverage

Track 1D tests cover:

- required files
- required canonical wording
- required sections and matrices
- SQLite schema initialization
- local reset behavior
- deterministic dev seed behavior
- required table existence
- repository/data access smoke behavior
- Track 1C runtime status integration
- absence of Product/AffiliateOffer full CRUD API
- absence of insight generation and recommendation runtime
- absence of production database, deployment, cloud, and security-runtime files

## 21. Local Run Instructions

Initialize storage:

- `bash scripts/dev/run_track1d_local_storage.sh init`

Seed deterministic demo data:

- `bash scripts/dev/run_track1d_local_storage.sh seed`

Inspect storage status:

- `bash scripts/dev/run_track1d_local_storage.sh status`

Reset local storage:

- `bash scripts/dev/run_track1d_local_storage.sh reset`

## 22. Implementation Guardrails

- Track 1D implements the local database/storage runtime for the first usable local product slice.
- Track 1D uses SQLite for local-first MVP storage.
- Track 1D continues Implementation Track 1 — Backend/API/Database Usable Product Slice.
- Track 1D is an explicit local product-slice runtime exception to the earlier Phase 1 Obsidian-only/no-database constraint.
- The Track 1D exception is limited to SQLite local-first MVP storage for Implementation Track 1.
- The Track 1D exception does not approve production database runtime.
- The Track 1D exception does not approve production promotion.
- The Track 1D exception does not approve production deployment.
- Track 1D does not implement Product or AffiliateOffer full CRUD API.
- Track 1D does not implement insight generation.
- Track 1D does not implement recommendation runtime.
- Track 1D preserves the Phase 7D selected-gate manual boundary.
- use Python standard library `sqlite3`
- keep runtime local-only
- require no external infrastructure
- require no secrets
- keep deterministic init/reset/seed behavior

### Storage Component Matrix

| Storage Component | Local Implementation | Purpose | Track Introduced | Production Status | Boundary Signal |
| --- | --- | --- | --- | --- | --- |
| SQLite database file | SQLite local-first MVP file under local-dev runtime | primary local persistence for the product slice foundation | Track 1D | not approved for production | local-only exception only |
| schema initialization | deterministic `sqlite3` DDL in `track1d_local_storage.py` | create required tables safely and repeatably | Track 1D | production database runtime not approved | no external migration service |
| reset storage | local file reset plus schema re-init | return the local slice to a clean deterministic state | Track 1D | production reset workflow not approved | local demo/test safety only |
| dev seed dataset | one deterministic row per required table | prove schema and repository behavior locally | Track 1D | production seed workflow not approved | demo data only |
| repository foundation | `track1d_repository.py` read/write smoke helpers | provide testable local storage access | Track 1D | production repository/runtime not approved | no Track 1E API scope |

## 23. Non-Goals and Forbidden Implementations

The following remain forbidden in Track 1D:

- Product/AffiliateOffer full CRUD API
- CollectionRun workflow API
- insight generation
- recommendation runtime
- production database runtime
- PostgreSQL/Aurora runtime
- production authentication
- RBAC enforcement
- production signing
- verifier runtime
- key custody runtime
- deployment files
- cloud infrastructure
- CI/CD deployment pipeline
- production promotion approval
- production deployment approval

## 24. Acceptance Criteria

- required files exist
- required canonical wording exists
- required sections and matrices exist
- Track 1D implements SQLite local-first storage
- Track 1D continues Implementation Track 1
- SQLite storage can initialize schema
- SQLite storage can reset local data safely
- SQLite storage can seed deterministic demo data
- required tables exist
- repository/data access smoke behavior works
- runtime/storage status reports SQLite local-first MVP
- Product/AffiliateOffer full CRUD API is not implemented in Track 1D
- insight generation is not implemented in Track 1D
- recommendation runtime is not implemented in Track 1D
- production promotion is not approved
- production deployment is not approved
- auth/RBAC/signing/verifier/key custody remain deferred
- docs/state pointers reference Track 1D
- no production database files are introduced
- no deployment/cloud infrastructure files are introduced
- no production auth/RBAC/signing/verifier/key custody runtime files are introduced

## 25. Recommended Next Step

Track 1E — Product Core API

Track 1E should build the first approved Product Core API behavior on top of
the Track 1D SQLite storage and repository foundation without widening into
production runtime scope.

## 26. Recommended Next Major Subphase

Track 1E — Product Core API
