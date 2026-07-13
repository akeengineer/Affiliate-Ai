# Track 1E — Product Core API

track1e_status: success

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
implementation_approval_status: track1e_product_core_api_implemented
implementation_track_status: implementation_track_1_started
runtime_mode: local-only
storage_runtime: SQLite local-first MVP
product_core_api_status: implemented_in_track1e
production_promotion_status: not_approved
production_deployment_status: not_approved
production_authentication_status: deferred
rbac_enforcement_status: deferred
production_signing_status: deferred
verifier_runtime_status: deferred
key_custody_runtime_status: deferred
phase7d_boundary_status: preserved

## 1. Track 1E Purpose

Track 1E implements the Product Core API for the first usable local product slice.

Track 1E continues Implementation Track 1 — Backend/API/Database Usable Product Slice.

Track 1E builds on the Track 1C local backend/API skeleton.

Track 1E builds on the Track 1D SQLite local-first storage runtime.

Track 1E implements local Product and AffiliateOffer API endpoints.

Track 1E uses SQLite local-first MVP storage through the Track 1D repository/data access boundary.

Track 1E evolves the Track 1D SQLite local-first schema only within the local product-slice runtime boundary.

Track 1E schema evolution does not approve production database runtime.

Track 1E schema evolution does not approve PostgreSQL or Aurora runtime.

Track 1E schema evolution remains limited to SQLite local-first MVP storage.

Track 1E continues to use the Track 1D repository/data access boundary.

Track 1E does not implement production authentication.

Track 1E does not implement RBAC enforcement.

Track 1E does not implement production signing.

Track 1E does not implement verifier runtime.

Track 1E does not implement key custody runtime.

Track 1E does not implement insight generation.

Track 1E does not implement recommendation runtime.

Track 1E does not approve production promotion.

Track 1E does not approve production deployment.

Track 1E preserves the Phase 7D selected-gate manual boundary.

## 2. Relationship to Track 1A

Track 1A selects backend/API/database runtime as the first runtime domain for a
usable product slice.

Track 1E is the first approved point for the usable Product Core API layer
inside that selected runtime domain.

Track 1E does not reinterpret Track 1A as production approval of database,
promotion, or deployment scope.

## 3. Relationship to Track 1B

Track 1B defines the Product and AffiliateOffer API surface and the
repository-first local runtime plan.

Track 1E implements the smallest approved portion of that planned API surface:

- `POST /products`
- `GET /products`
- `GET /products/{id}`
- `PATCH /products/{id}`
- `POST /affiliate-offers`
- `GET /affiliate-offers`

## 4. Relationship to Track 1C

Track 1C provides the local backend/API skeleton and the service entrypoint.

Track 1E preserves:

- `GET /health`
- `GET /version`
- `GET /runtime/status`

Track 1E adds only the approved Product/AffiliateOffer routes to that Track 1C
surface.

## 5. Relationship to Track 1D

Track 1D provides the local SQLite storage/runtime foundation and the initial
repository/data access boundary.

Track 1E evolves the Track 1D SQLite local-first schema only within the local product-slice runtime boundary.

Track 1E schema evolution does not approve production database runtime.

Track 1E schema evolution does not approve PostgreSQL or Aurora runtime.

Track 1E schema evolution remains limited to SQLite local-first MVP storage.

Track 1E continues to use the Track 1D repository/data access boundary.

## 6. Local Product Core API Scope

Selected Runtime Domain: backend/API/database runtime

Implementation Track: Implementation Track 1 — Backend/API/Database Usable Product Slice

Product Goal: first usable local product slice

Runtime Mode: local-only

Storage Runtime: SQLite local-first MVP

Product Core API Status: implemented in Track 1E

Production Promotion Status: not approved

Production Deployment Status: not approved

Production Authentication Status: deferred

RBAC Enforcement Status: deferred

Production Signing Status: deferred

Verifier Runtime Status: deferred

Key Custody Runtime Status: deferred

Phase 7D Boundary Status: preserved

## 7. Product Endpoint Contract

Track 1E Product endpoints:

- `POST /products`
- `GET /products`
- `GET /products/{id}`
- `PATCH /products/{id}`

### Product Core API Matrix

| API Area | Endpoint | Method | Purpose | Required Validation | Track Introduced |
| --- | --- | --- | --- | --- | --- |
| Product | /products | POST | create one local product record | `name` and `category` required; status enum; metadata object | Track 1E |
| Product | /products | GET | list local products | deterministic response shape only | Track 1E |
| Product | /products/{id} | GET | get one local product | path id lookup | Track 1E |
| Product | /products/{id} | PATCH | patch allowed local product fields | non-empty patch; unknown fields rejected; field validation enforced | Track 1E |
| AffiliateOffer | /affiliate-offers | POST | create one local affiliate offer | `product_id`, `source_id`, `offer_url` required; references must exist | Track 1E |
| AffiliateOffer | /affiliate-offers | GET | list local affiliate offers | deterministic response shape only | Track 1E |

### Product Entity Field Matrix

| Field | Required | Type | Validation | Default | Storage Mapping |
| --- | --- | --- | --- | --- | --- |
| `id` | response only | string | generated locally | generated | `products.id` |
| `name` | yes | string | non-empty | none | `products.name` |
| `category` | yes | string | non-empty | none | `products.category` |
| `description` | no | string | string if present | empty string | `products.description` |
| `status` | no | string | `active`, `inactive`, `archived` | `active` | `products.status` |
| `metadata` | no | object | JSON object if present | `{}` | `products.metadata` |
| `created_at` | response only | string | ISO-8601 UTC | generated | `products.created_at` |
| `updated_at` | response only | string | ISO-8601 UTC | generated | `products.updated_at` |

## 8. AffiliateOffer Endpoint Contract

Track 1E AffiliateOffer endpoints:

- `POST /affiliate-offers`
- `GET /affiliate-offers`

### AffiliateOffer Entity Field Matrix

| Field | Required | Type | Validation | Default | Storage Mapping |
| --- | --- | --- | --- | --- | --- |
| `id` | response only | string | generated locally | generated | `affiliate_offers.id` |
| `product_id` | yes | string | must reference existing product | none | `affiliate_offers.product_id` |
| `source_id` | yes | string | must reference existing source | none | `affiliate_offers.source_id` |
| `title` | no | string | string if present | empty string | `affiliate_offers.title` |
| `offer_url` | yes | string | non-empty | none | `affiliate_offers.offer_url` |
| `price` | no | number | numeric if present | `null` | `affiliate_offers.price` |
| `currency` | no | string | string if present | empty string | `affiliate_offers.currency` |
| `commission_rate` | no | number | numeric if present | `null` | `affiliate_offers.commission_rate` |
| `status` | no | string | `active`, `inactive`, `archived` | `active` | `affiliate_offers.status` |
| `metadata` | no | object | JSON object if present | `{}` | `affiliate_offers.metadata` |
| `created_at` | response only | string | ISO-8601 UTC | generated | `affiliate_offers.created_at` |
| `updated_at` | response only | string | ISO-8601 UTC | generated | `affiliate_offers.updated_at` |

## 9. Validation and Error Handling Contract

Track 1E uses one stable deterministic JSON error serializer for all non-2xx
responses.

### Error Contract Matrix

| Error Case | HTTP Status | Error Code | Required Response Fields | Deterministic Behavior | Track Introduced |
| --- | --- | --- | --- | --- | --- |
| malformed JSON | 400 | `validation_error` | `error`, `message`, `status_code` | stable message and field set | Track 1E |
| missing product route target | 404 | `not_found` | `error`, `message`, `status_code` | stable missing-resource message | Track 1E |
| unsupported method on supported route | 405 | `method_not_allowed` | `error`, `message`, `status_code` | stable method/path message | Track 1E |
| semantic validation failure | 422 | `validation_error` | `error`, `message`, `status_code` | stable message, optional deterministic `field_errors` | Track 1E |

## 10. Repository/Data Access Integration

Track 1E extends the Track 1D repository/data access boundary narrowly.

### Repository Integration Matrix

| Repository Operation | Purpose | Storage Table | Allowed Behavior | Forbidden Behavior | Track Introduced |
| --- | --- | --- | --- | --- | --- |
| `create_product` | insert one local product | `products` | one deterministic insert with defaults | generic CRUD framework | Track 1E |
| `list_products` | list local products | `products` | deterministic list ordering | pagination framework | Track 1E |
| `get_product` | fetch one local product | `products` | one record lookup | broad query abstraction | Track 1E |
| `update_product` | patch one local product | `products` | allowed-field update only | full generic patch engine | Track 1E |
| `product_exists` | validate product reference | `products` | boolean existence check | business workflow orchestration | Track 1E |
| `source_exists` | validate source reference | `sources` | boolean existence check | Source API layer | Track 1E |
| `create_affiliate_offer` | insert one local affiliate offer | `affiliate_offers` | one deterministic insert with defaults | generic CRUD framework | Track 1E |
| `list_affiliate_offers` | list local affiliate offers | `affiliate_offers` | deterministic list ordering | filtering framework outside scope | Track 1E |

## 11. SQLite Local-First Storage Boundary

Track 1E keeps storage limited to SQLite local-first MVP only.

The Track 1D storage module is evolved with deterministic local schema handling
that supports:

- fresh local database files
- existing Track 1D local database files
- no shadow tables retained after evolution
- no generic production migration framework

## 12. Runtime Status Contract

Track 1E preserves the Track 1C/1D runtime fields and adds the Product Core API
status fields.

### Runtime Status Matrix

| Status Field | Required Value | Purpose | Boundary Signal | Track Introduced |
| --- | --- | --- | --- | --- |
| `product_core_api_status` | `implemented in Track 1E` | declare Product Core API availability | local-only API status only | Track 1E |
| `product_endpoint_status` | `implemented in Track 1E` | declare Product endpoint availability | no Source/CollectionRun/Insight scope implied | Track 1E |
| `affiliate_offer_endpoint_status` | `implemented in Track 1E` | declare AffiliateOffer endpoint availability | local-only offer API only | Track 1E |
| `insight_generation_status` | `not implemented in Track 1E` | preserve later-track boundary | no insight generation runtime | Track 1E |
| `recommendation_runtime_status` | `not implemented in Track 1E` | preserve later-track boundary | no recommendation runtime | Track 1E |

## 13. Deferred Source API Scope

Track 1E does not implement Source API endpoints.

Source records are reused only for repository validation and deterministic seed
setup.

## 14. Deferred CollectionRun Workflow API Scope

Track 1E does not implement CollectionRun workflow API behavior.

CollectionRun storage remains present from Track 1D only as deferred foundation.

## 15. Deferred Insight Generation Scope

Track 1E does not implement insight generation.

## 16. Deferred Recommendation Runtime Scope

Track 1E does not implement recommendation runtime.

## 17. Deferred Security and Hardening Scope

Track 1E does not implement production authentication.

Track 1E does not implement RBAC enforcement.

Track 1E does not implement production signing.

Track 1E does not implement verifier runtime.

Track 1E does not implement key custody runtime.

### Deferred Implementation Matrix

| Deferred Area | Current Status | Deferred Reason | First Eligible Track | Required Future Approval |
| --- | --- | --- | --- | --- |
| Source API endpoints | deferred | Track 1E reuses source seed/repository validation only | explicit later track | explicit later-track approval |
| CollectionRun workflow API | deferred | Track 1E is Product Core API only | explicit later track | explicit later-track approval |
| insight generation | deferred | outside Track 1E scope | Track 1F+ | explicit later-track approval |
| recommendation runtime | deferred | outside Track 1E scope | Track 1F+ | explicit later-track approval |
| production database runtime | not approved | Track 1E remains local SQLite only | explicit later track | explicit later-track approval |
| PostgreSQL/Aurora runtime | deferred | SQLite local-first MVP remains the only approved runtime | explicit later track | explicit later-track approval |
| production authentication | deferred | local-only runtime boundary | explicit later track | explicit later-track approval |
| RBAC enforcement | deferred | local-only runtime boundary | explicit later track | explicit later-track approval |
| production signing | deferred | local-only runtime boundary | explicit later track | explicit later-track approval |
| verifier runtime | deferred | local-only runtime boundary | explicit later track | explicit later-track approval |
| key custody runtime | deferred | local-only runtime boundary | explicit later track | explicit later-track approval |
| production deployment | not approved | Track 1E remains local-only | explicit later track | explicit later-track approval |
| cloud infrastructure | deferred | no cloud runtime approved | explicit later track | explicit later-track approval |
| CI/CD deployment | deferred | no deployment pipeline approved | explicit later track | explicit later-track approval |
| payment/billing | deferred | outside Product Core API MVP scope | explicit later track | explicit later-track approval |
| multi-tenant security | deferred | outside local single-operator scope | explicit later track | explicit later-track approval |

## 18. Production Database Exclusion

Track 1E schema evolution does not approve production database runtime.

Track 1E does not add a production database service, cloud database, or managed
runtime abstraction.

## 19. Production Promotion Exclusion

Track 1E does not approve production promotion.

Production Promotion Status: not approved

## 20. Production Deployment Exclusion

Track 1E does not approve production deployment.

Production Deployment Status: not approved

Track 1E adds no deployment files, cloud infrastructure, or CI/CD deployment
pipeline.

## 21. Phase 7D Manual Boundary Preservation

Track 1E preserves the Phase 7D selected-gate manual boundary.

Phase 7D Boundary Status: preserved

## 22. Test Coverage

Track 1E tests cover:

- required files
- required canonical wording
- required sections and matrices
- schema evolution for fresh and Track 1D-shaped local DBs
- preserved Track 1C endpoints
- Product API create/list/get/patch
- AffiliateOffer API create/list
- deterministic `400`, `404`, `405`, and `422` responses
- runtime status Product Core API fields
- deferred boundary preservation and forbidden runtime-file absence

## 23. Local Run Instructions

Run the local service:

- `bash scripts/dev/run_track1c_local_backend.sh`

Example local Product API call surface:

- `GET /health`
- `GET /version`
- `GET /runtime/status`
- `POST /products`
- `GET /products`
- `GET /products/{id}`
- `PATCH /products/{id}`
- `POST /affiliate-offers`
- `GET /affiliate-offers`

## 24. Implementation Guardrails

- Track 1E implements the Product Core API for the first usable local product slice.
- Track 1E evolves the Track 1D SQLite local-first schema only within the local product-slice runtime boundary.
- Track 1E schema evolution does not approve production database runtime.
- Track 1E schema evolution does not approve PostgreSQL or Aurora runtime.
- Track 1E schema evolution remains limited to SQLite local-first MVP storage.
- Track 1E continues to use the Track 1D repository/data access boundary.
- Track 1E does not implement insight generation.
- Track 1E does not implement recommendation runtime.
- Track 1E does not approve production promotion.
- Track 1E does not approve production deployment.
- Track 1E preserves the Phase 7D selected-gate manual boundary.
- no Source API endpoints unless absolutely required for tests
- no CollectionRun workflow API
- no deployment files
- no cloud infrastructure
- no CI/CD deployment pipeline

## 25. Non-Goals and Forbidden Implementations

The following remain forbidden in Track 1E:

- Source API endpoints beyond test/setup reuse
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
- payment/billing
- multi-tenant security
- production promotion approval
- production deployment approval

## 26. Acceptance Criteria

- Product Core API is implemented
- Product endpoints work locally
- AffiliateOffer endpoints work locally
- SQLite local-first storage is used through the Track 1D repository/data access boundary
- validation errors are deterministic
- not_found errors are deterministic
- method_not_allowed errors are deterministic
- unsupported route errors are deterministic
- runtime status reflects Product Core API implemented in Track 1E
- no insight generation is implemented
- no recommendation runtime is implemented
- no production database runtime is introduced
- no production promotion approval is introduced
- no production deployment approval is introduced

## 27. Recommended Next Step

Track 1F — Minimal Usable UI/operator flow

Track 1F is the first approved point for Minimal Usable UI/operator flow implementation, if Track 1E is accepted.

## 28. Recommended Next Major Subphase

Track 1F — Minimal Usable UI/operator flow
