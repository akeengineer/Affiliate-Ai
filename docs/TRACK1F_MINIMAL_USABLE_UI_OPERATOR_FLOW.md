# Track 1F — Minimal Usable UI / Operator Flow

track1f_status: success

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
implementation_approval_status: track1f_minimal_operator_flow_implemented
implementation_track_status: implementation_track_1_started
runtime_mode: local-only
storage_runtime: SQLite local-first MVP
product_core_api_status: implemented_in_track1e
minimal_operator_flow_status: implemented_in_track1f
operator_surface_status: implemented_in_track1f
production_frontend_deployment_status: not_approved
production_promotion_status: not_approved
production_deployment_status: not_approved
production_authentication_status: deferred
rbac_enforcement_status: deferred
production_signing_status: deferred
verifier_runtime_status: deferred
key_custody_runtime_status: deferred
phase7d_boundary_status: preserved

## 1. Track 1F Purpose

Track 1F implements the minimal usable UI/operator flow for the first usable local product slice.

Track 1F continues Implementation Track 1 — Backend/API/Database Usable Product Slice.

Track 1F builds on the Track 1C local backend/API skeleton.

Track 1F builds on the Track 1D SQLite local-first storage runtime.

Track 1F builds on the Track 1E Product Core API.

Track 1F provides a local-only operator flow for Product and AffiliateOffer usage.

Track 1F does not implement production frontend deployment.

Track 1F does not implement production authentication.

Track 1F does not implement RBAC enforcement.

Track 1F does not implement production signing.

Track 1F does not implement verifier runtime.

Track 1F does not implement key custody runtime.

Track 1F does not approve production promotion.

Track 1F does not approve production deployment.

Track 1F preserves the Phase 7D selected-gate manual boundary.

## 2. Relationship to Track 1A

Track 1A selects backend/API/database runtime as the first runtime domain for a
usable product slice.

Track 1F adds the first approved minimal operator-facing flow inside that
selected runtime domain.

Track 1F does not reinterpret Track 1A as approval for production frontend,
promotion, deployment, or cloud runtime scope.

## 3. Relationship to Track 1B

Track 1B defines the backend/API/database usable product slice plan and the
sequence of runtime steps.

Track 1F implements the first operator-facing local surface after the Track 1E
Product Core API exists.

## 4. Relationship to Track 1C

Track 1C provides the local backend/API skeleton and the HTTP routing boundary.

Track 1F preserves:

- `GET /health`
- `GET /version`
- `GET /runtime/status`

Track 1F adds only one local operator route:

- `GET /operator`

## 5. Relationship to Track 1D

Track 1D provides the SQLite local-first storage/runtime foundation.

Track 1F continues to use SQLite local-first MVP storage and does not widen the
Track 1D storage boundary into production database runtime.

## 6. Relationship to Track 1E

Track 1E provides the Product Core API and repository/data access boundary.

Track 1F reuses the existing Track 1E API endpoints and does not add a separate
operator mutation API.

## 7. Minimal Usable Operator Flow Scope

Selected Runtime Domain: backend/API/database runtime

Implementation Track: Implementation Track 1 — Backend/API/Database Usable Product Slice

Product Goal: first usable local product slice

Runtime Mode: local-only

Storage Runtime: SQLite local-first MVP

Product Core API Status: implemented in Track 1E

Minimal Operator Flow Status: implemented in Track 1F

Production Promotion Status: not approved

Production Deployment Status: not approved

Production Authentication Status: deferred

RBAC Enforcement Status: deferred

Production Signing Status: deferred

Verifier Runtime Status: deferred

Key Custody Runtime Status: deferred

Phase 7D Boundary Status: preserved

## 8. Operator Surface Contract

Track 1F serves one local-only operator page at `GET /operator`.

The page is rendered by the existing Python local backend and uses only
dependency-free HTML, CSS, and inline JavaScript.

### Operator Surface Matrix

| Surface Area | Local Implementation | Purpose | Allowed Behavior | Forbidden Behavior | Track Introduced |
| --- | --- | --- | --- | --- | --- |
| `GET /operator` | static HTML served by existing Python backend | expose the first usable local operator surface | render forms, panels, and inline fetch calls to approved Track 1E APIs | separate frontend app, build step, production deployment path | Track 1F |
| runtime status panel | HTML section + `fetch("/runtime/status")` | show boundary/runtime state | display deterministic JSON runtime status | mutate backend state | Track 1F |
| add product form | HTML form + `fetch("/products")` | create a local product | POST one product through Track 1E API | bypass Track 1E validation or repository boundary | Track 1F |
| product list panel | HTML section + `fetch("/products")` | list local products | display deterministic Track 1E product list response | query SQLite directly from browser | Track 1F |
| add affiliate offer form | HTML form + `fetch("/affiliate-offers")` | create a local affiliate offer | POST one offer through Track 1E API | add Source UI/API or bypass source validation | Track 1F |
| affiliate offer list panel | HTML section + `fetch("/affiliate-offers")` | list local offers | display deterministic Track 1E offer list response | query SQLite directly from browser | Track 1F |

## 9. Product Operator Action Contract

Track 1F Product operator actions:

- view runtime status
- add product
- view product list

The operator page uses only Track 1E Product API behavior and preserves the
Track 1E validation and error contract.

## 10. AffiliateOffer Operator Action Contract

Track 1F AffiliateOffer operator actions:

- add affiliate offer
- view affiliate offer list

Track 1F does not implement Source UI/API. The operator flow reuses the
existing deterministic local source validation model and may document the demo
source `demo-source-track1d` for local setup/demo purposes.

## 11. Runtime Status Operator Contract

Track 1F extends `GET /runtime/status` with operator-surface fields only.

### Runtime Status Matrix

| Status Field | Required Value | Purpose | Boundary Signal | Track Introduced |
| --- | --- | --- | --- | --- |
| `product_core_api_status` | `implemented in Track 1E` | preserve Product Core API availability | Product Core API came from Track 1E, not Track 1F | Track 1F |
| `minimal_operator_flow_status` | `implemented in Track 1F` | declare operator flow availability | local-only operator flow only | Track 1F |
| `operator_surface_status` | `implemented in Track 1F` | declare operator surface availability | `GET /operator` exists locally only | Track 1F |
| `production_frontend_deployment_status` | `not approved` | preserve deployment boundary | no production frontend deployment | Track 1F |
| `insight_generation_status` | `not implemented in Track 1F` | preserve later-track boundary | no insight generation runtime | Track 1F |
| `recommendation_runtime_status` | `not implemented in Track 1F` | preserve later-track boundary | no recommendation runtime | Track 1F |

## 12. Local-Only UI Boundary

Track 1F remains local-only.

The operator surface is served from the existing local backend and is not a
production UI, hosted frontend, or deployable customer-facing application.

## 13. Existing API Integration

Track 1F uses existing Track 1E APIs only.

### Existing API Integration Matrix

| Existing API | Track Introduced | Operator Use | Expected Behavior | Preservation Requirement | Track 1F Change |
| --- | --- | --- | --- | --- | --- |
| `GET /runtime/status` | Track 1C | show runtime status panel | return deterministic runtime boundary JSON | preserve existing status fields and extend only with Track 1F operator fields | add operator status fields |
| `POST /products` | Track 1E | add product | create one validated product | preserve Track 1E validation/error contract | no payload contract change |
| `GET /products` | Track 1E | list products | return deterministic product list JSON | preserve response shape | no response contract change |
| `POST /affiliate-offers` | Track 1E | add affiliate offer | create one validated offer | preserve Track 1E validation/error contract | no payload contract change |
| `GET /affiliate-offers` | Track 1E | list affiliate offers | return deterministic offer list JSON | preserve response shape | no response contract change |

### Operator Flow Matrix

| Operator Action | Local Surface | Backing API/Service | Expected Output | Boundary Signal | Track Introduced |
| --- | --- | --- | --- | --- | --- |
| View runtime status | `/operator` runtime panel | `GET /runtime/status` | deterministic runtime JSON shown in the page | local-only boundary remains explicit | Track 1F |
| Add product | `/operator` add product form | `POST /products` | created product JSON or deterministic validation error | uses Track 1E Product API unchanged | Track 1F |
| View product list | `/operator` product list panel | `GET /products` | deterministic product list JSON | no direct SQLite editing | Track 1F |
| Add affiliate offer | `/operator` add affiliate offer form | `POST /affiliate-offers` | created offer JSON or deterministic validation error | uses Track 1E AffiliateOffer API unchanged | Track 1F |
| View affiliate offer list | `/operator` affiliate offer list panel | `GET /affiliate-offers` | deterministic offer list JSON | no direct SQLite editing | Track 1F |

## 14. Validation and Error Handling Preservation

Track 1F preserves the Track 1E validation and error handling contract.

The operator page displays returned JSON error objects but does not redefine:

- `400 malformed JSON`
- `404 not_found`
- `405 method_not_allowed`
- `422 validation_error`

## 15. Deferred Source UI Scope

Track 1F does not implement Source UI/API.

## 16. Deferred CollectionRun Workflow Scope

Track 1F does not implement CollectionRun workflow UI/API.

## 17. Deferred Insight Generation Scope

Track 1F does not implement insight generation.

## 18. Deferred Recommendation Runtime Scope

Track 1F does not implement recommendation runtime.

## 19. Deferred Security and Hardening Scope

Track 1F does not implement production authentication.

Track 1F does not implement RBAC enforcement.

Track 1F does not implement production signing.

Track 1F does not implement verifier runtime.

Track 1F does not implement key custody runtime.

### Deferred Implementation Matrix

| Deferred Area | Current Status | Deferred Reason | First Eligible Track | Required Future Approval |
| --- | --- | --- | --- | --- |
| Source UI/API | deferred | Track 1F reuses existing source validation only | explicit later track | explicit later-track approval |
| CollectionRun workflow UI/API | deferred | Track 1F is operator flow for Product and AffiliateOffer only | explicit later track | explicit later-track approval |
| insight generation | deferred | outside Track 1F scope | Track 1G+ | explicit later-track approval |
| recommendation runtime | deferred | outside Track 1F scope | Track 1G+ | explicit later-track approval |
| production frontend deployment | not approved | Track 1F remains local-only | explicit later track | explicit later-track approval |
| production authentication | deferred | local-only operator boundary | explicit later track | explicit later-track approval |
| RBAC enforcement | deferred | local-only operator boundary | explicit later track | explicit later-track approval |
| production signing | deferred | local-only operator boundary | explicit later track | explicit later-track approval |
| verifier runtime | deferred | local-only operator boundary | explicit later track | explicit later-track approval |
| key custody runtime | deferred | local-only operator boundary | explicit later track | explicit later-track approval |
| production deployment | not approved | Track 1F remains local-only | explicit later track | explicit later-track approval |
| cloud infrastructure | deferred | no cloud runtime approved | explicit later track | explicit later-track approval |
| CI/CD deployment | deferred | no deployment pipeline approved | explicit later track | explicit later-track approval |
| payment/billing | deferred | outside Track 1F scope | explicit later track | explicit later-track approval |
| multi-tenant security | deferred | outside local single-operator scope | explicit later track | explicit later-track approval |
| customer production use | deferred | Track 1F is local operator flow only | explicit later track | explicit later-track approval |

## 20. Production Frontend Deployment Exclusion

Track 1F does not implement production frontend deployment.

Track 1F adds no frontend framework dependency, hosting config, or production
frontend artifact pipeline.

## 21. Production Promotion Exclusion

Track 1F does not approve production promotion.

Production Promotion Status: not approved

## 22. Production Deployment Exclusion

Track 1F does not approve production deployment.

Production Deployment Status: not approved

## 23. Phase 7D Manual Boundary Preservation

Track 1F preserves the Phase 7D selected-gate manual boundary.

Phase 7D Boundary Status: preserved

## 24. Test Coverage

Track 1F tests cover:

- required files
- required canonical wording
- required sections and matrices
- `GET /operator` HTML surface
- runtime status Track 1F operator fields
- existing Product and AffiliateOffer APIs still working
- Track 1E validation/error behavior preservation
- frontend dependency exclusions
- deployment/cloud infrastructure exclusions
- docs/state pointer updates

## 25. Local Run Instructions

Run the local backend:

- `bash scripts/dev/run_track1c_local_backend.sh`

Then open:

- `http://127.0.0.1:8011/operator`

Use the page to:

- view runtime status
- add a product
- list products
- add an affiliate offer
- list affiliate offers

## 26. Implementation Guardrails

- Track 1F implements the minimal usable UI/operator flow for the first usable local product slice.
- Track 1F continues Implementation Track 1 — Backend/API/Database Usable Product Slice.
- Track 1F builds on the Track 1C local backend/API skeleton.
- Track 1F builds on the Track 1D SQLite local-first storage runtime.
- Track 1F builds on the Track 1E Product Core API.
- Track 1F provides a local-only operator flow for Product and AffiliateOffer usage.
- Track 1F does not implement production frontend deployment.
- Track 1F does not implement production authentication.
- Track 1F does not implement RBAC enforcement.
- Track 1F does not implement production signing.
- Track 1F does not implement verifier runtime.
- Track 1F does not implement key custody runtime.
- Track 1F does not approve production promotion.
- Track 1F does not approve production deployment.
- Track 1F preserves the Phase 7D selected-gate manual boundary.

## 27. Non-Goals and Forbidden Implementations

The following remain forbidden in Track 1F:

- React
- Next.js
- Vite
- Tailwind
- npm packages
- frontend build step
- production frontend deployment config
- Source UI/API
- CollectionRun workflow UI/API
- insight generation
- recommendation runtime
- production authentication
- RBAC enforcement
- production signing
- verifier runtime
- key custody runtime
- cloud infrastructure
- CI/CD deployment pipeline
- production promotion approval
- production deployment approval

## 28. Acceptance Criteria

- minimal usable UI/operator flow is implemented
- operator can view runtime status
- operator can add product
- operator can view product list
- operator can add affiliate offer
- operator can view affiliate offer list
- operator flow uses existing Track 1E Product/AffiliateOffer behavior
- existing Track 1C/1D/1E contracts remain preserved
- no production frontend deployment is introduced
- no frontend framework dependency is introduced
- no insight generation is implemented
- no recommendation runtime is implemented
- no production promotion approval is introduced
- no production deployment approval is introduced

## 29. Recommended Next Step

Track 1G — End-to-End Demo Pack

Track 1G is the first approved point for End-to-End Demo Pack implementation, if Track 1F is accepted.

## 30. Recommended Next Major Subphase

Track 1G — End-to-End Demo Pack
