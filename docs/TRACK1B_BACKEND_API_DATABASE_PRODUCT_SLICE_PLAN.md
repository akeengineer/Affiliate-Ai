# Track 1B — Backend/API/Database Product Slice Plan

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
implementation_approval_status: track1b_plan_defined
implementation_track_status: implementation_track_1_started
product_slice_planning_status: defined
production_promotion_status: not_approved
production_deployment_status: not_approved
production_authentication_status: deferred
rbac_enforcement_status: deferred
production_signing_status: deferred
verifier_runtime_status: deferred
key_custody_runtime_status: deferred
phase7d_boundary_status: preserved

## 1. Track 1B Purpose

Track 1B defines the backend/API/database product slice implementation plan for the first usable local product slice.

Track 1B continues Implementation Track 1 — Backend/API/Database Usable Product Slice.

Track 1B does not implement runtime code.

Track 1B does not add backend/API/database implementation files.

Track 1B does not approve production promotion.

Track 1B does not approve production deployment.

Track 1B preserves the Phase 7D selected-gate manual boundary.

Track 1B is backend/API/database product slice planning documentation only.

## 2. Relationship to Track 1A

Track 1A selects backend/API/database runtime as the first runtime domain for a usable product slice.

Track 1B follows Track 1A by defining the first implementation plan for that
selected runtime domain without introducing runtime code.

Track 1B keeps the same governance/readiness discipline as Track 1A while
moving the substance forward from selection to product-slice planning.

Track 1B does not reinterpret Track 1A as production promotion approval or
production deployment approval.

## 3. Product Slice Goal

Selected Runtime Domain: backend/API/database runtime

Implementation Track: Implementation Track 1 — Backend/API/Database Usable Product Slice

Product Goal: first usable local product slice

Production Promotion Status: not approved

Production Deployment Status: not approved

Production Authentication Status: deferred

RBAC Enforcement Status: deferred

Production Signing Status: deferred

Verifier Runtime Status: deferred

Key Custody Runtime Status: deferred

Phase 7D Boundary Status: preserved

The first usable local product slice is planned as a local-only operator flow
that can create, view, update, and inspect products and affiliate offers,
record collection runs, and generate deterministic insights without any cloud
deployment or production approval.

## 4. Local-First Runtime Boundary

Track 1B remains docs/tests-only.

The planned runtime boundary is local-first, single-operator, and deterministic.

The future runtime may read and write only local product-slice data required
for the approved Track 1 scope and must stay outside production deployment,
multi-tenant operation, and customer production use.

Track 1B does not implement runtime code.

Track 1B does not add backend/API/database implementation files.

Current Phase 1 artifacts remain the live implementation baseline until a later
track explicitly adds approved local runtime files.

## 5. Backend Service Plan

The planned backend service is a local-only operator service with five bounded
responsibilities:

- runtime status surface for health/version/runtime status
- product application service for create/list/read/update product workflows
- affiliate offer application service for create/list offer workflows
- collection run application service for local collection-run tracking
- deterministic insight application service for repeatable insight generation

The service plan remains framework-agnostic in Track 1B. Track 1C is the first approved point for local backend/API skeleton implementation, if Track 1B is accepted.

The planned process boundary is one local service process with explicit config
loading, local file/database initialization checks, and deterministic request
handling. No background workers, queues, webhooks, or cloud dependencies are
planned in Track 1B.

## 6. API Surface Plan

The planned API surface is a thin local HTTP contract over the product-slice
application services. The API exists to make the first usable local product
slice testable and operable, not to create a production-facing surface.

Planned endpoint families:

- runtime inspection endpoints
- product management endpoints
- affiliate offer endpoints
- collection run endpoints
- deterministic insight endpoints

### API Endpoint Matrix

| Endpoint | Method | Purpose | Request Shape | Response Shape | Validation Boundary | Track Introduced |
| --- | --- | --- | --- | --- | --- | --- |
| GET /health | GET | local process liveliness check | no body | `{ "status": "ok" }` | service availability only | Track 1B |
| GET /version | GET | expose local build/version metadata | no body | `{ "version": "...", "track": "1C+" }` | static response contract | Track 1B |
| GET /runtime/status | GET | expose local runtime mode and deferred statuses | no body | `{ "runtime_domain": "backend/API/database runtime", "promotion": "not approved", "deployment": "not approved" }` | status serialization boundary | Track 1B |
| POST /products | POST | create one local product record | product create payload | product resource payload | request schema and required-field validation | Track 1B |
| GET /products | GET | list products for operator review | optional local filters | list of product summaries | query parameter normalization | Track 1B |
| GET /products/{id} | GET | view one product record | path id only | full product resource | path parameter validation and existence lookup | Track 1B |
| PATCH /products/{id} | PATCH | patch editable product fields | partial product payload | updated product resource | partial-field validation and immutable-field guard | Track 1B |
| POST /affiliate-offers | POST | create one affiliate offer record | offer create payload | offer resource payload | request schema and product reference validation | Track 1B |
| GET /affiliate-offers | GET | list affiliate offers | optional product filter | list of offer summaries | query parameter normalization | Track 1B |
| POST /collection-runs | POST | start and record one local collection run | collection-run create payload | collection-run resource | request schema and source/product linkage validation | Track 1B |
| GET /collection-runs/{id} | GET | inspect one collection run | path id only | collection-run resource | path parameter validation and existence lookup | Track 1B |
| POST /insights/generate | POST | generate deterministic insights for one product slice | generation request payload | generated insight and recommendation payload | request schema and deterministic input validation | Track 1B |
| GET /insights | GET | list generated insights | optional product filter | list of insight summaries | query parameter normalization | Track 1B |

## 7. Database/Storage Plan

SQLite is the default storage choice for the first local product slice because it requires no external infrastructure, supports deterministic demo workflows, keeps reset and seed operations simple, and can be migrated to PostgreSQL or Aurora later after the product slice proves useful.

Track 1B records that storage decision at planning level only.

The planned storage boundary is one local SQLite database file plus a small
set of deterministic seed/reset fixtures used for local acceptance and repeatable
demo workflows.

This planning decision does not add a database to the current implementation in
Track 1B. It only defines the default local-first storage target for later
tracks inside Implementation Track 1.

### Storage Plan Matrix

| Storage Component | Local Choice | Purpose | Migration/Init Need | Reset/Seed Need | Future Production Candidate |
| --- | --- | --- | --- | --- | --- |
| SQLite database file | SQLite for local-first MVP | primary local persistence for the product slice | initialize schema in a later runtime track | reset by recreating the local file | PostgreSQL or Aurora |
| schema initialization | SQLite for local-first MVP | create deterministic local tables/indexes | one explicit init/migration command in Track 1D | rerunnable local init check | PostgreSQL or Aurora migration toolchain |
| local seed dataset | Markdown/JSON fixture set | populate deterministic demo records | load through a later seed command | re-seed after reset for demos/tests | sanitized production-like fixtures |
| local reset procedure | SQLite file replacement | return local environment to known-clean state | documented in a later runtime track | required before repeat demos | managed reset/migration workflow |

## 8. Product Entity Model

The product slice plan defines six planning-level entities:

- Product
- AffiliateOffer
- Source
- CollectionRun
- Insight
- Recommendation

The entity model is intentionally small so the first usable local product slice
can be demonstrated, reset, and tested deterministically.

### Product Entity Matrix

| Entity | Purpose | Required Fields | Validation Rules | Relationship | Track Introduced |
| --- | --- | --- | --- | --- | --- |
| Product | core operator record for one candidate product | `id`, `name`, `marketplace`, `status`, `created_at`, `updated_at` | id required, name non-empty, marketplace non-empty, timestamps required | one Product has many AffiliateOffer, CollectionRun, Insight, Recommendation | Track 1B |
| AffiliateOffer | local representation of one affiliate program/offer | `id`, `product_id`, `program_name`, `commission_model`, `created_at`, `updated_at` | product reference required, program name non-empty, commission model non-empty | many AffiliateOffer belong to one Product | Track 1B |
| Source | provenance record for one marketplace, trend, or operator input source | `id`, `product_id`, `source_type`, `source_ref`, `created_at` | source type required, source ref non-empty | many Source records can support one Product or CollectionRun | Track 1B |
| CollectionRun | one deterministic local collection execution record | `id`, `product_id`, `started_at`, `status`, `created_at` | product reference required, status enum required | many CollectionRun records belong to one Product and may reference Source records | Track 1B |
| Insight | one generated deterministic analysis output | `id`, `product_id`, `insight_type`, `summary`, `created_at` | product reference required, summary non-empty | many Insight records belong to one Product and can derive from CollectionRun | Track 1B |
| Recommendation | one action-oriented decision output for the operator | `id`, `product_id`, `recommendation_type`, `reason`, `created_at` | product reference required, reason non-empty | many Recommendation records belong to one Product and may cite Insight | Track 1B |

## 9. Repository/Data Access Plan

The planned data access layer is repository-first and local-only.

One repository boundary is planned per entity family:

- product repository
- affiliate offer repository
- source repository
- collection run repository
- insight repository
- recommendation repository

The repository layer should own SQL statements, transaction boundaries, record
mapping, and not-found handling so application services remain deterministic
and easy to test with a clean local database reset.

Track 1B does not choose an ORM. The plan favors the smallest deterministic
data-access approach that preserves readability and explicit SQL behavior.

## 10. Validation and Error Handling Plan

Validation is planned at three boundaries:

- request boundary validation for path/query/body shape
- application boundary validation for business rules and allowed state changes
- repository boundary validation for referential existence and duplicate guards

The planned error handling contract is:

- `400` for malformed request shape
- `404` for missing entity ids
- `409` for conflicting local state changes
- `422` for semantically invalid but well-formed input
- `500` for unexpected local runtime failures

All validation and error responses must remain deterministic and should return
stable machine-readable error codes in later runtime tracks.

## 11. Deterministic Insight Generation Plan

The planned insight generator must be deterministic across repeated runs over
the same local inputs.

The future runtime should derive Insight and Recommendation records only from
persisted local product-slice data, explicit operator inputs, and deterministic
rules. No external API call, background fetch, or non-deterministic generation
step is approved inside Track 1B.

The planned minimum deterministic outputs are:

- product summary insight
- affiliate-offer fit insight
- collection-run completeness insight
- recommendation summary for operator next action

The scoring and recommendation path should remain explainable so local demos
can show why a recommendation was produced from the stored inputs.

## 12. Minimal UI or Operator Flow Plan

The first usable operator flow is planned as a local operator sequence:

1. inspect runtime readiness with `GET /health`, `GET /version`, and `GET /runtime/status`
2. create a product with `POST /products`
3. review products with `GET /products` and `GET /products/{id}`
4. add one or more affiliate offers with `POST /affiliate-offers`
5. record one collection run with `POST /collection-runs`
6. generate one deterministic insight result with `POST /insights/generate`
7. inspect generated insights with `GET /insights`

Track 1B does not add a UI. The minimal operator surface for the first product
slice is planned as local API interaction first, with a minimal UI or operator
wrapper deferred to later Track 1 work.

## 13. Local Run Command Plan

The planned local run commands are documentation targets for later tracks only:

- `./scripts/dev/run_track1c_local_backend.sh` for local service startup
- `./scripts/dev/run_track1d_local_storage_init.sh` for local storage initialization
- `./scripts/dev/run_track1d_local_storage_seed.sh` for deterministic local seed loading
- `./scripts/dev/run_track1g_local_product_slice_demo.sh` for the end-to-end local demo flow

Track 1B records these command targets so later implementation tracks can keep
the local operator workflow simple and script-driven without introducing those
files yet.

## 14. Seed and Reset Plan

The seed/reset plan is local-only and deterministic.

The planned seed path should load a small sanitized dataset that exercises all
required entities and endpoints for the demo acceptance flow.

The planned reset path should remove or replace the local SQLite file, reload
the same deterministic fixtures, and return the environment to a known-clean
state for repeat tests and repeat demos.

## 15. Test Plan

Track 1B adds only documentation-focused tests in this track.

Later runtime tracks should add focused unit, contract, and local integration
tests per endpoint and service boundary before any implementation area is
considered complete.

### Test Plan Matrix

| Test Area | Required Coverage | Track Introduced | Acceptance Signal | Deferred Coverage |
| --- | --- | --- | --- | --- |
| service startup smoke | verify local startup, config load, and health endpoints | Track 1B | planned smoke checks documented before Track 1C work | framework-specific boot behavior |
| product CRUD contract | create/list/get/patch product path and validation outcomes | Track 1B | endpoint contract remains explicit and deterministic | pagination, bulk operations |
| affiliate offer contract | create/list offer path and product linkage validation | Track 1B | offer lifecycle scope is bounded | offer sync/import automation |
| collection run contract | create/get collection run path and state reporting | Track 1B | collection run lifecycle is documented | background collection execution |
| insight generation contract | deterministic insight/recommendation output over same inputs | Track 1B | repeat runs produce same result shape | advanced ranking heuristics |
| seed/reset determinism | reset returns clean state and seed reproduces same records | Track 1B | local demo can repeat reliably | migration edge cases |
| phase boundary guards | verify no production auth/RBAC/signing/verifier/key custody/deployment runtime is added in Track 1B | Track 1B | docs/tests-only boundary remains enforced | future production hardening tests |

## 16. Demo Acceptance Flow

The planned demo acceptance flow for the first usable local product slice is:

1. start the future local backend skeleton
2. confirm `GET /health`, `GET /version`, and `GET /runtime/status`
3. seed the local dataset
4. create or view a Product
5. create one AffiliateOffer for that Product
6. create one CollectionRun
7. generate one deterministic Insight and Recommendation
8. list the resulting insights
9. reset the local environment

The acceptance flow is local-only and operator-driven. It is not production
promotion and not production deployment.

## 17. Rollback and Cleanup Plan

The rollback plan for the first usable local product slice is intentionally
simple:

- stop the local service process
- archive or discard the local SQLite file
- restore the last known-good seed/reset fixture set
- rerun local init and seed
- rerun focused health and contract checks

Cleanup should remove temporary local runtime artifacts and return the repo to
the same docs/tests-controlled baseline when the demo or test cycle is done.

## 18. Deferred Security and Hardening Scope

Production Authentication Status: deferred

RBAC Enforcement Status: deferred

Production Signing Status: deferred

Verifier Runtime Status: deferred

Key Custody Runtime Status: deferred

Authentication runtime, RBAC enforcement runtime, production signing runtime,
verifier runtime, key custody runtime, production deployment, CI/CD
deployment, multi-tenant enforcement, payment/billing, and customer production
use remain deferred outside Track 1B.

### Deferred Security Matrix

| Security Domain | Current Status | Deferred Reason | Required Future Approval | Not Allowed In Track 1B |
| --- | --- | --- | --- | --- |
| production authentication | deferred | local product slice planning does not require production identity runtime | explicit later-track approval | yes |
| RBAC enforcement | deferred | single-operator local-first slice does not require production authorization runtime | explicit later-track approval | yes |
| production signing | deferred | signing is outside the first usable local slice plan | explicit later-track approval | yes |
| verifier runtime | deferred | verifier runtime is outside the first usable local slice plan | explicit later-track approval | yes |
| key custody runtime | deferred | key custody is outside the first usable local slice plan | explicit later-track approval | yes |
| production deployment | not approved | Track 1B is planning-only and local-first | explicit later-track approval | yes |
| CI/CD deployment | deferred | deployment automation is outside Track 1B scope | explicit later-track approval | yes |
| multi-tenant enforcement | deferred | first slice is local-only and single-operator | explicit later-track approval | yes |
| payment/billing | deferred | billing is unrelated to the first usable local slice | explicit later-track approval | yes |
| customer production use | deferred | Track 1B is not a production approval path | explicit later-track approval | yes |

## 19. Production Promotion Exclusion

Track 1B does not approve production promotion.

Production Promotion Status: not approved

Track 1B does not convert planning approval into promotion approval.

## 20. Production Deployment Exclusion

Track 1B does not approve production deployment.

Production Deployment Status: not approved

Track 1B does not create a deployment runtime, deployment manifest, cloud
infrastructure path, or CI/CD deployment path.

## 21. Phase 7D Manual Boundary Preservation

Track 1B preserves the Phase 7D selected-gate manual boundary.

Phase 7D Boundary Status: preserved

Approval remains the Phase 7D selected-gate manual boundary.

Track 1B does not bypass, widen, automate, or replace the selected-gate manual
boundary.

## 22. Implementation Guardrails

- Track 1B defines the backend/API/database product slice implementation plan for the first usable local product slice.
- Track 1B continues Implementation Track 1 — Backend/API/Database Usable Product Slice.
- Track 1B does not implement runtime code.
- Track 1B does not add backend/API/database implementation files.
- Track 1B does not approve production promotion.
- Track 1B does not approve production deployment.
- Track 1B preserves the Phase 7D selected-gate manual boundary.
- no deployment files
- no auth/RBAC/signing/verifier/key custody runtime
- no production runtime files
- no production promotion
- no production deployment

## 23. Non-Goals and Forbidden Implementations

The following remain forbidden in Track 1B:

- runtime implementation code
- backend/API/database implementation files
- deployment files
- production authentication runtime
- RBAC enforcement runtime
- production signing runtime
- verifier runtime
- key custody runtime
- production policy engine runtime
- CI/CD deployment runtime
- cloud infrastructure
- multi-tenant runtime
- payment/billing runtime
- customer production use
- production promotion approval
- production deployment approval

## 24. Acceptance Criteria

- required files exist
- required canonical wording exists
- required sections exist
- Track 1B continues Implementation Track 1
- Track 1B defines the backend/API/database product slice implementation plan
- Track 1B does not implement runtime code
- Track 1B does not add backend/API/database implementation files
- Track 1B does not approve production promotion
- Track 1B does not approve production deployment
- Phase 7D boundary is preserved
- Track 1A is referenced
- Track 1C is identified as the first backend/API skeleton implementation point
- required product entities are documented
- required API endpoint plan is documented
- SQLite local-first storage decision is documented
- product entity matrix exists
- API endpoint matrix exists
- storage plan matrix exists
- test plan matrix exists
- deferred security matrix exists
- deferred security/hardening scope is documented
- docs/state pointers reference Track 1B
- no Track 1B backend/API/database implementation files are introduced
- no Track 1B deployment files are introduced
- no Track 1B auth/RBAC/signing/verifier/key custody runtime is introduced

## 25. Recommended Next Step

## Recommended Next Step

Complete Track 1B PR readiness

- run focused checks
- run full suite
- confirm clean worktree
- push feature/track1b-backend-api-database-product-slice-plan
- open one PR for Track 1B
- wait for CI green
- squash merge
- sync main
- delete feature branch

## 26. Recommended Next Major Subphase

## Recommended Next Major Subphase

Track 1C — Local Backend/API Skeleton

Track 1C should implement the local backend/API skeleton for the first usable local product slice. Track 1C should add only local runtime code required for service startup, configuration loading, GET /health, GET /version, and GET /runtime/status. Track 1C should not implement production authentication, RBAC enforcement, production signing, verifier runtime, key custody runtime, production deployment, cloud infrastructure, or production promotion unless explicitly approved in a later track.

Track 1C implements the local backend/API skeleton for the first usable local product slice.

Track 1C is the first runtime implementation step in Implementation Track 1.

Track 1C implements local service startup, local configuration loading, GET /health, GET /version, and GET /runtime/status.

Track 1C does not implement database/storage runtime.

Track 1C does not implement Product or AffiliateOffer CRUD.

Track 1C does not implement insight generation.

Track 1C does not approve production promotion.

Track 1C does not approve production deployment.

Track 1C preserves the Phase 7D selected-gate manual boundary.

Track 1D is the first approved point for database/storage runtime implementation, if Track 1C is accepted.
