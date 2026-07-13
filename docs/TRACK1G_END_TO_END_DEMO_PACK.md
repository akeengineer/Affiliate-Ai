# Track 1G — End-to-End Demo Pack

track1g_status: success

track1f_status: success
track1e_status: success
track1d_status: success
track1c_status: success
track1b_status: success
track1a_status: success
phase7d_runtime_readiness: implemented_manual_gate

selected_runtime_domain: backend/API/database runtime
runtime_mode: local-only
storage_runtime: SQLite local-first MVP
product_core_api_status: implemented_in_track1e
minimal_operator_flow_status: implemented_in_track1f
end_to_end_demo_pack_status: implemented_in_track1g
production_demo_deployment_status: not_approved
production_promotion_status: not_approved
production_deployment_status: not_approved
production_authentication_status: deferred
rbac_enforcement_status: deferred
production_signing_status: deferred
verifier_runtime_status: deferred
key_custody_runtime_status: deferred
phase7d_boundary_status: preserved

## 1. Track 1G Purpose

Track 1G implements the end-to-end demo pack for the first usable local product slice.

Track 1G continues Implementation Track 1 — Backend/API/Database Usable Product Slice.

Track 1G builds on the Track 1C local backend/API skeleton.

Track 1G builds on the Track 1D SQLite local-first storage runtime.

Track 1G builds on the Track 1E Product Core API.

Track 1G builds on the Track 1F minimal usable UI/operator flow.

Track 1G provides a deterministic local demo workflow.

Track 1G does not implement production deployment.

Track 1G does not implement production authentication.

Track 1G does not implement RBAC enforcement.

Track 1G does not implement production signing.

Track 1G does not implement verifier runtime.

Track 1G does not implement key custody runtime.

Track 1G does not approve production promotion.

Track 1G does not approve production deployment.

Track 1G preserves the Phase 7D selected-gate manual boundary.

## 2. Relationship to Track 1A

Track 1A selects backend/API/database runtime as the first runtime domain for a usable product slice.

Track 1G does not widen that selection into production runtime, promotion, or deployment approval.

## 3. Relationship to Track 1B

Track 1B defines the backend/API/database product slice plan.

Track 1G packages the first local end-to-end demonstration of that slice.

## 4. Relationship to Track 1C

Track 1C provides the local backend/API skeleton, `GET /health`, `GET /version`, and `GET /runtime/status`.

Track 1G verifies those runtime boundaries remain available.

## 5. Relationship to Track 1D

Track 1D provides SQLite local-first MVP storage.

Track 1G resets, initializes, and seeds only local demo SQLite storage.

## 6. Relationship to Track 1E

Track 1E provides Product and AffiliateOffer behavior.

Track 1G creates and lists demo Product/AffiliateOffer records through Track 1E behavior.

## 7. Relationship to Track 1F

Track 1F provides the minimal usable UI/operator flow.

Track 1G verifies the operator surface remains available.

## 8. End-to-End Demo Pack Scope

Selected Runtime Domain: backend/API/database runtime

Implementation Track: Implementation Track 1 — Backend/API/Database Usable Product Slice

Product Goal: first usable local product slice

Runtime Mode: local-only

Storage Runtime: SQLite local-first MVP

Product Core API Status: implemented in Track 1E

Minimal Operator Flow Status: implemented in Track 1F

End-to-End Demo Pack Status: implemented in Track 1G

Production Promotion Status: not approved

Production Deployment Status: not approved

Production Authentication Status: deferred

RBAC Enforcement Status: deferred

Production Signing Status: deferred

Verifier Runtime Status: deferred

Key Custody Runtime Status: deferred

Phase 7D Boundary Status: preserved

## 9. Demo Workflow Contract

### Demo Workflow Matrix

| Demo Step | Local Mechanism | Expected Output | Backing Track | Boundary Signal | Track Introduced |
| --- | --- | --- | --- | --- | --- |
| Reset/init local demo storage | Track 1D storage reset/init | empty initialized SQLite schema | Track 1D | local SQLite only | Track 1G |
| Seed deterministic demo source | Track 1D seed data | reusable `demo-source-track1d` | Track 1D | no Source API added | Track 1G |
| Verify runtime status | Track 1C status payload | local runtime status fields | Track 1C | no production runtime | Track 1G |
| Verify operator surface availability | Track 1F operator renderer | operator page available | Track 1F | local operator surface only | Track 1G |
| Create deterministic demo product | Track 1E Product helper | created product JSON | Track 1E | no direct SQLite edits | Track 1G |
| List products | Track 1E Product helper | product list JSON | Track 1E | no direct SQLite reads by operator | Track 1G |
| Create deterministic demo affiliate offer | Track 1E AffiliateOffer helper | created offer JSON | Track 1E | source validation preserved | Track 1G |
| List affiliate offers | Track 1E AffiliateOffer helper | affiliate offer list JSON | Track 1E | no recommendation runtime | Track 1G |
| Produce deterministic demo summary | Track 1G runner | JSON summary with `demo_status: ok` | Track 1G | local report only | Track 1G |

## 10. Demo Runner Contract

The demo runner is `scripts/dev/track1g_end_to_end_demo_pack.py`.

The shell wrapper is `scripts/dev/run_track1g_end_to_end_demo_pack.sh`.

The runner accepts local path overrides and emits deterministic JSON.

## 11. Demo Output Contract

### Demo Output Matrix

| Output Field | Required Value | Purpose | Deterministic Source | Track Introduced |
| --- | --- | --- | --- | --- |
| `runtime_mode` | `local-only` | prove local runtime | storage/runtime status | Track 1G |
| `storage_runtime` | `SQLite local-first MVP` | prove SQLite local storage | Track 1D config | Track 1G |
| `product_core_api_status` | `implemented in Track 1E` | prove Product Core API availability | runtime status | Track 1G |
| `minimal_operator_flow_status` | `implemented in Track 1F` | prove operator flow availability | runtime status | Track 1G |
| `demo_product_count` | `2` | prove seed plus created product are listed | Product list response | Track 1G |
| `demo_affiliate_offer_count` | `2` | prove seed plus created offer are listed | AffiliateOffer list response | Track 1G |
| `demo_status` | `ok` | prove demo completed | Track 1G runner | Track 1G |

## 12. Runtime Status Demo Contract

### Runtime Status Matrix

| Status Field | Required Value | Purpose | Boundary Signal | Track Introduced |
| --- | --- | --- | --- | --- |
| `end_to_end_demo_pack_status` | `implemented in Track 1G` | declare demo pack availability | local demo only | Track 1G |
| `demo_workflow_status` | `implemented in Track 1G` | declare demo workflow availability | no production demo deployment | Track 1G |
| `production_demo_deployment_status` | `not approved` | preserve deployment boundary | no production demo deployment | Track 1G |
| `insight_generation_status` | `not implemented in Track 1G` | preserve insight boundary | no insight generation runtime | Track 1G |
| `recommendation_runtime_status` | `not implemented in Track 1G` | preserve recommendation boundary | no recommendation runtime | Track 1G |

## 13. Operator Surface Verification

Track 1G verifies the Track 1F operator surface by confirming rendered operator HTML contains the local operator flow boundary.

## 14. Product Demo Flow

Track 1G creates a deterministic demo product through Track 1E behavior and lists products.

## 15. AffiliateOffer Demo Flow

Track 1G creates a deterministic demo affiliate offer linked to the seeded product/source and lists affiliate offers.

## 16. Existing API Integration

### Existing Runtime Integration Matrix

| Existing Runtime Area | Track Introduced | Demo Use | Preservation Requirement | Track 1G Change |
| --- | --- | --- | --- | --- |
| local backend status | Track 1C | verify runtime boundary | preserve `GET /health`, `GET /version`, `GET /runtime/status` | add Track 1G status fields |
| SQLite local-first storage | Track 1D | reset/init/seed demo storage | preserve local SQLite only | no schema change |
| Product Core API | Track 1E | create/list demo Product and AffiliateOffer | preserve validation/error contracts | no API contract change |
| operator surface | Track 1F | verify `/operator` availability | preserve local-only HTML surface | no route contract change |

## 17. Local-Only Demo Boundary

Track 1G remains local-only and writes only deterministic local demo output.

## 18. Deferred Insight Generation Scope

Track 1G does not implement insight generation.

## 19. Deferred Recommendation Runtime Scope

Track 1G does not implement recommendation runtime.

## 20. Deferred Security and Hardening Scope

Track 1G does not implement production authentication.

Track 1G does not implement RBAC enforcement.

Track 1G does not implement production signing.

Track 1G does not implement verifier runtime.

Track 1G does not implement key custody runtime.

### Deferred Implementation Matrix

| Deferred Area | Current Status | Deferred Reason | First Eligible Track | Required Future Approval |
| --- | --- | --- | --- | --- |
| insight generation | deferred | outside Track 1G scope | explicit later track | explicit later-track approval |
| recommendation runtime | deferred | outside Track 1G scope | explicit later track | explicit later-track approval |
| production demo deployment | not approved | Track 1G remains local-only | explicit later track | explicit later-track approval |
| production frontend deployment | not approved | Track 1F/1G remain local-only | explicit later track | explicit later-track approval |
| production authentication | deferred | local-only demo boundary | explicit later track | explicit later-track approval |
| RBAC enforcement | deferred | local-only demo boundary | explicit later track | explicit later-track approval |
| production signing | deferred | local-only demo boundary | explicit later track | explicit later-track approval |
| verifier runtime | deferred | local-only demo boundary | explicit later track | explicit later-track approval |
| key custody runtime | deferred | local-only demo boundary | explicit later track | explicit later-track approval |
| production deployment | not approved | no deployment approved | explicit later track | explicit later-track approval |
| cloud infrastructure | deferred | no cloud runtime approved | explicit later track | explicit later-track approval |
| CI/CD deployment | deferred | no deployment pipeline approved | explicit later track | explicit later-track approval |
| payment/billing | deferred | outside Track 1G scope | explicit later track | explicit later-track approval |
| multi-tenant security | deferred | outside local demo scope | explicit later track | explicit later-track approval |
| customer production use | deferred | Track 1G is local demo only | explicit later track | explicit later-track approval |

## 21. Production Demo Deployment Exclusion

Track 1G does not implement production demo deployment.

## 22. Production Promotion Exclusion

Track 1G does not approve production promotion.

Production Promotion Status: not approved

## 23. Production Deployment Exclusion

Track 1G does not approve production deployment.

Production Deployment Status: not approved

## 24. Phase 7D Manual Boundary Preservation

Track 1G preserves the Phase 7D selected-gate manual boundary.

Phase 7D Boundary Status: preserved

## 25. Test Coverage

Track 1G tests cover docs, task, runner, runtime status, operator availability, Product/AffiliateOffer demo behavior, deterministic summary, and forbidden production/deployment scope.

## 26. Local Run Instructions

Run:

- `bash scripts/dev/run_track1g_end_to_end_demo_pack.sh`

Optional local overrides:

- `bash scripts/dev/run_track1g_end_to_end_demo_pack.sh --database-path tmp/track1g-demo/demo.sqlite3 --output-path tmp/track1g-demo/summary.json`

## 27. Implementation Guardrails

- Track 1G implements the end-to-end demo pack for the first usable local product slice.
- Track 1G continues Implementation Track 1 — Backend/API/Database Usable Product Slice.
- Track 1G builds on the Track 1C local backend/API skeleton.
- Track 1G builds on the Track 1D SQLite local-first storage runtime.
- Track 1G builds on the Track 1E Product Core API.
- Track 1G builds on the Track 1F minimal usable UI/operator flow.
- Track 1G provides a deterministic local demo workflow.

## 28. Non-Goals and Forbidden Implementations

- production demo deployment
- production deployment
- production authentication
- RBAC enforcement
- production signing
- verifier runtime
- key custody runtime
- cloud infrastructure
- CI/CD deployment
- payment/billing
- multi-tenant security
- customer production use
- insight generation
- recommendation runtime

## 29. Acceptance Criteria

- end-to-end demo pack is implemented
- demo runner can reset/init local demo storage
- demo runner can verify runtime status
- demo runner can verify operator surface availability
- demo runner can create deterministic demo product
- demo runner can list products
- demo runner can create deterministic demo affiliate offer
- demo runner can list affiliate offers
- demo runner produces deterministic demo summary
- existing Track 1C/1D/1E/1F contracts remain preserved

## 30. Recommended Next Step

Track 1H — MVP Acceptance Pack

Track 1H is the first approved point for MVP Acceptance Pack implementation, if Track 1G is accepted.

Track 1H creates the MVP Acceptance Pack for the first usable local product slice.

Track 1H closes Implementation Track 1 — Backend/API/Database Usable Product Slice.

Track 1H accepts the local product slice as usable for local/demo operation only.

See `docs/TRACK1H_MVP_ACCEPTANCE_PACK.md`.

## 31. Recommended Next Major Subphase

Implementation Track 2 — Local Product Intelligence Expansion, after Track 1H is merged.
