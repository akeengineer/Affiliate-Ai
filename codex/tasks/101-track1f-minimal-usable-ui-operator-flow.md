# Task 101 — Track 1F Minimal Usable UI / Operator Flow

## Goal

Implement Track 1F as the minimal usable UI/operator flow step for Implementation Track 1 — Backend/API/Database Usable Product Slice.

Track 1F implements the minimal usable UI/operator flow for the first usable local product slice.

Track 1F continues Implementation Track 1 — Backend/API/Database Usable Product Slice.

Track 1F builds on the Track 1C local backend/API skeleton.

Track 1F builds on the Track 1D SQLite local-first storage runtime.

Track 1F builds on the Track 1E Product Core API.

Track 1F provides a local-only operator flow for Product and AffiliateOffer usage.

## Approved Operator Surface

Use a simple single-page `GET /operator` HTML view served by the existing
Python local backend.

The page includes:

- local-only boundary notice
- runtime status panel
- add product form
- product list panel
- add affiliate offer form
- affiliate offer list panel
- deterministic result/error panels
- tiny inline JavaScript `fetch` calls to the existing Track 1E APIs

## Required Boundary

- Track 1F does not implement production frontend deployment.
- Track 1F does not implement production authentication.
- Track 1F does not implement RBAC enforcement.
- Track 1F does not implement production signing.
- Track 1F does not implement verifier runtime.
- Track 1F does not implement key custody runtime.
- Track 1F does not approve production promotion.
- Track 1F does not approve production deployment.
- Track 1F preserves the Phase 7D selected-gate manual boundary.
- Selected Runtime Domain: backend/API/database runtime
- Implementation Track: Implementation Track 1 — Backend/API/Database Usable Product Slice
- Product Goal: first usable local product slice
- Runtime Mode: local-only
- Storage Runtime: SQLite local-first MVP
- Product Core API Status: implemented in Track 1E
- Minimal Operator Flow Status: implemented in Track 1F
- Production Promotion Status: not approved
- Production Deployment Status: not approved
- Production Authentication Status: deferred
- RBAC Enforcement Status: deferred
- Production Signing Status: deferred
- Verifier Runtime Status: deferred
- Key Custody Runtime Status: deferred
- Phase 7D Boundary Status: preserved
- Track 1G is the first approved point for End-to-End Demo Pack implementation, if Track 1F is accepted.

## Implementation Notes

- Keep HTTP routing in `scripts/dev/track1c_local_backend_api.py`.
- Add one small Track 1F helper/module under `scripts/dev/` for HTML rendering.
- Use existing Track 1E API endpoints only:
  - `GET /runtime/status`
  - `POST /products`
  - `GET /products`
  - `POST /affiliate-offers`
  - `GET /affiliate-offers`
- Preserve existing Track 1C/1D/1E contracts.
- Preserve the existing Track 1E validation/error contract.
- Do not add React, Next.js, Vite, Tailwind, npm packages, bundlers, or a production frontend deployment config.
- Do not add Source UI/API, CollectionRun workflow UI/API, insight generation, recommendation runtime, auth/RBAC/signing/verifier/key custody runtime, cloud infrastructure, CI/CD deployment pipeline, production promotion, or production deployment.
