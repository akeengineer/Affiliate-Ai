# Track 1C — Local Backend/API Skeleton

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
implementation_approval_status: track1c_local_runtime_started
implementation_track_status: implementation_track_1_started
runtime_mode: local-only
backend_api_skeleton_status: implemented
production_promotion_status: not_approved
production_deployment_status: not_approved
production_authentication_status: deferred
rbac_enforcement_status: deferred
production_signing_status: deferred
verifier_runtime_status: deferred
key_custody_runtime_status: deferred
phase7d_boundary_status: preserved

## 1. Track 1C Purpose

Track 1C implements the local backend/API skeleton for the first usable local product slice.

Track 1C is the first runtime implementation step in Implementation Track 1.

Track 1C implements local service startup, local configuration loading, GET /health, GET /version, and GET /runtime/status.

Track 1C does not implement database/storage runtime.

Track 1C does not implement Product or AffiliateOffer CRUD.

Track 1C does not implement insight generation.

Track 1C does not approve production promotion.

Track 1C does not approve production deployment.

Track 1C preserves the Phase 7D selected-gate manual boundary.

## 2. Relationship to Track 1A

Track 1A selects backend/API/database runtime as the first runtime domain for a usable product slice.

Track 1C follows that runtime-domain selection by adding the first approved
local runtime implementation for the selected domain.

Track 1C does not reinterpret Track 1A as production promotion approval or
production deployment approval.

## 3. Relationship to Track 1B

Track 1B defines the backend/API/database product slice implementation plan for the first usable local product slice.

Track 1C implements only the smallest approved subset of that plan: local
service startup, local configuration loading, GET /health, GET /version, and
GET /runtime/status.

Track 1C does not widen the Track 1B scope into storage runtime, CRUD runtime,
or insight generation runtime.

## 4. Local Runtime Implementation Scope

Selected Runtime Domain: backend/API/database runtime

Implementation Track: Implementation Track 1 — Backend/API/Database Usable Product Slice

Product Goal: first usable local product slice

Runtime Mode: local-only

Production Promotion Status: not approved

Production Deployment Status: not approved

Production Authentication Status: deferred

RBAC Enforcement Status: deferred

Production Signing Status: deferred

Verifier Runtime Status: deferred

Key Custody Runtime Status: deferred

Phase 7D Boundary Status: preserved

Track 1C is intentionally limited to a local-only HTTP skeleton with
deterministic JSON responses and no external infrastructure.

## 5. Backend/API Skeleton Implementation

Track 1C uses the smallest repo-consistent runtime layout under `scripts/dev/`:

- `scripts/dev/track1c_local_backend_config.py` for local configuration loading
- `scripts/dev/track1c_local_backend_api.py` for routing and deterministic JSON responses
- `scripts/dev/run_track1c_local_backend.py` for local service startup
- `scripts/dev/run_track1c_local_backend.sh` for repo-consistent shell entry

The backend skeleton uses Python standard library `http.server` only. It does
not add FastAPI, Flask, Django, or any new dependency.

The service is local-only and validates that the bind host stays within the
local boundary (`127.0.0.1` or `localhost`).

## 6. Endpoint Contract

### Endpoint Contract Matrix

| Endpoint | Method | Runtime Purpose | Required Response Fields | Boundary Signal | Track Introduced |
| --- | --- | --- | --- | --- | --- |
| GET /health | GET | confirm local process liveliness | `status`, `service`, `runtime_mode` | local-only health surface only | Track 1C |
| GET /version | GET | expose local skeleton version identity | `service`, `version`, `implementation_track`, `track` | Track 1C identity only | Track 1C |
| GET /runtime/status | GET | expose local runtime boundary and deferred statuses | selected runtime domain, runtime mode, promotion/deployment/security statuses, deferred implementation statuses | explicit local-only boundary declaration | Track 1C |

Track 1C endpoint payloads are deterministic JSON objects with stable field
values and no dependency on database state, operator identity, or external
services.

## 7. Local Configuration Boundary

Track 1C loads local configuration from deterministic defaults and optional
local overrides only:

- `AFFILIATE_BACKEND_HOST`
- `AFFILIATE_BACKEND_PORT`
- `--host`
- `--port`

No secret, token, cloud endpoint, or external service configuration is loaded
in Track 1C.

The configuration boundary remains local-only and fail-closed for non-local
host values.

## 8. Runtime Status Boundary

`GET /runtime/status` is the explicit boundary endpoint for Track 1C.

It confirms:

- selected runtime domain is backend/API/database runtime
- runtime mode is local-only
- production promotion is not approved
- production deployment is not approved
- production authentication/RBAC/signing/verifier/key custody remain deferred
- database/storage runtime is not implemented in Track 1C
- Product/AffiliateOffer CRUD is not implemented in Track 1C
- insight generation is not implemented in Track 1C

### Runtime Boundary Matrix

| Runtime Area | Track 1C Status | Allowed Behavior | Forbidden Behavior | Next Eligible Track |
| --- | --- | --- | --- | --- |
| service startup | implemented | start one local-only HTTP process | deployment runtime, daemon supervisor, cloud bootstrapping | Track 1C |
| local configuration loading | implemented | load deterministic local host/port config | secret loading, cloud config loading, remote service config | Track 1C |
| backend/API skeleton | implemented | serve GET /health, GET /version, GET /runtime/status | CRUD routes, storage access, remote integrations | Track 1C |
| database/storage runtime | deferred | report not implemented in Track 1C | schema, migrations, SQLite runtime, external DB | Track 1D |
| Product CRUD | deferred | report not implemented in Track 1C | create/list/get/patch Product runtime | Track 1E |
| AffiliateOffer CRUD | deferred | report not implemented in Track 1C | create/list/get AffiliateOffer runtime | Track 1E |
| insight generation | deferred | report not implemented in Track 1C | deterministic insight runtime | Track 1F |

## 9. Deferred Database/Storage Runtime

Track 1C does not implement database/storage runtime.

Storage initialization, schema creation, migrations, and local database
operations remain deferred.

Track 1D is the first approved point for database/storage runtime implementation, if Track 1C is accepted.

## 10. Deferred Product CRUD Scope

Track 1C does not implement Product or AffiliateOffer CRUD.

No product create/list/get/update path is added in this track. No
AffiliateOffer create/list path is added in this track.

CollectionRun runtime and Recommendation runtime are also deferred because
their first useful behavior depends on later storage and product-slice runtime
work.

## 11. Deferred Insight Generation Scope

Track 1C does not implement insight generation.

No insight generation request handling, recommendation runtime, scoring bridge,
or derived product-slice analysis runtime is added in this track.

## 12. Deferred Security and Hardening Scope

Production Authentication Status: deferred

RBAC Enforcement Status: deferred

Production Signing Status: deferred

Verifier Runtime Status: deferred

Key Custody Runtime Status: deferred

### Deferred Implementation Matrix

| Deferred Area | Current Status | Deferred Reason | First Eligible Track | Required Future Approval |
| --- | --- | --- | --- | --- |
| database/storage runtime | deferred | Track 1C is skeleton-only and storage-free | Track 1D | explicit later-track approval |
| Product CRUD | deferred | Track 1C exposes status-only runtime | Track 1E | explicit later-track approval |
| AffiliateOffer CRUD | deferred | Track 1C exposes status-only runtime | Track 1E | explicit later-track approval |
| CollectionRun runtime | deferred | collection runtime depends on later storage/application layers | Track 1E | explicit later-track approval |
| Insight generation | deferred | insight logic is outside skeleton scope | Track 1F | explicit later-track approval |
| Recommendation runtime | deferred | recommendation logic is outside skeleton scope | Track 1F | explicit later-track approval |
| production authentication | deferred | local-only skeleton does not require production identity runtime | explicit later track | explicit later-track approval |
| RBAC enforcement | deferred | local-only skeleton does not require production authorization runtime | explicit later track | explicit later-track approval |
| production signing | deferred | signing is outside Track 1C runtime scope | explicit later track | explicit later-track approval |
| verifier runtime | deferred | verifier runtime is outside Track 1C runtime scope | explicit later track | explicit later-track approval |
| key custody runtime | deferred | key custody is outside Track 1C runtime scope | explicit later track | explicit later-track approval |
| production deployment | not approved | Track 1C is local-only | explicit later track | explicit later-track approval |
| cloud infrastructure | deferred | no cloud runtime is approved in Track 1C | explicit later track | explicit later-track approval |
| CI/CD deployment | deferred | Track 1C adds no deployment path | explicit later track | explicit later-track approval |

## 13. Production Promotion Exclusion

Track 1C does not approve production promotion.

Production Promotion Status: not approved

Track 1C runtime implementation does not convert local startup into promotion
approval.

## 14. Production Deployment Exclusion

Track 1C does not approve production deployment.

Production Deployment Status: not approved

Track 1C does not add deployment files, deployment runtime, cloud
infrastructure, or CI/CD deployment changes.

## 15. Phase 7D Manual Boundary Preservation

Track 1C preserves the Phase 7D selected-gate manual boundary.

Phase 7D Boundary Status: preserved

Track 1C does not bypass, widen, automate, or replace the selected-gate manual
boundary.

## 16. Test Coverage

Track 1C tests cover:

- required files
- required canonical wording
- required document sections and matrices
- focused local service startup on ephemeral localhost port
- GET /health contract
- GET /version contract
- GET /runtime/status contract
- docs/state pointer references
- absence of forbidden storage/deployment/security runtime files

## 17. Local Run Instructions

Local startup command:

- `bash scripts/dev/run_track1c_local_backend.sh`

Optional overrides:

- `bash scripts/dev/run_track1c_local_backend.sh --host 127.0.0.1 --port 8001`

Expected local-only endpoints:

- `GET /health`
- `GET /version`
- `GET /runtime/status`

## 18. Implementation Guardrails

- Track 1C implements the local backend/API skeleton for the first usable local product slice.
- Track 1C is the first runtime implementation step in Implementation Track 1.
- Track 1C implements local service startup, local configuration loading, GET /health, GET /version, and GET /runtime/status.
- Track 1C does not implement database/storage runtime.
- Track 1C does not implement Product or AffiliateOffer CRUD.
- Track 1C does not implement insight generation.
- Track 1C does not approve production promotion.
- Track 1C does not approve production deployment.
- Track 1C preserves the Phase 7D selected-gate manual boundary.
- no new dependency
- no FastAPI/Flask/Django yet
- no deployment files
- no production auth/RBAC/signing/verifier/key custody runtime
- no cloud infrastructure
- no CI/CD deployment changes

## 19. Non-Goals and Forbidden Implementations

The following remain forbidden in Track 1C:

- database/storage runtime
- Product CRUD runtime
- AffiliateOffer CRUD runtime
- CollectionRun runtime
- insight generation runtime
- recommendation runtime
- deployment files
- production authentication runtime
- RBAC enforcement runtime
- production signing runtime
- verifier runtime
- key custody runtime
- cloud infrastructure
- CI/CD deployment changes
- production promotion approval
- production deployment approval

## 20. Acceptance Criteria

- local backend/API skeleton is implemented
- GET /health works
- GET /version works
- GET /runtime/status works
- runtime mode is local-only
- no database/storage runtime is implemented
- no Product/AffiliateOffer CRUD is implemented
- no insight generation is implemented
- no production promotion approval is introduced
- no production deployment approval is introduced
- focused Track 1C tests pass
- full suite passes or CI validates the full suite if local Phase 1 smoke remains slow
- git diff check passes
- worktree is clean after commit

## 21. Recommended Next Step

## Recommended Next Step

Complete Track 1C PR readiness

- run focused checks
- run full suite
- confirm clean worktree
- push feature/track1c-local-backend-api-skeleton
- open one PR for Track 1C
- wait for CI green
- squash merge
- sync main
- delete feature branch

## 22. Recommended Next Major Subphase

## Recommended Next Major Subphase

Track 1D — Database/Storage Runtime

Track 1D should implement the first approved database/storage runtime for the first usable local product slice. Track 1D should add only the local storage runtime needed to initialize and access local product-slice persistence. Track 1D should not implement production authentication, RBAC enforcement, production signing, verifier runtime, key custody runtime, production deployment, cloud infrastructure, or production promotion unless explicitly approved in a later track.

Track 1D is now documented separately in `docs/TRACK1D_DATABASE_STORAGE_RUNTIME.md`
as the narrow post-Track-1A SQLite local-first MVP storage exception for
Implementation Track 1.
