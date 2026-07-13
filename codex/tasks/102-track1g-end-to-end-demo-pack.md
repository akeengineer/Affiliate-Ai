# Task 102 — Track 1G End-to-End Demo Pack

## Goal

Track 1G implements the end-to-end demo pack for the first usable local product slice.

Track 1G continues Implementation Track 1 — Backend/API/Database Usable Product Slice.

Track 1G builds on the Track 1C local backend/API skeleton.

Track 1G builds on the Track 1D SQLite local-first storage runtime.

Track 1G builds on the Track 1E Product Core API.

Track 1G builds on the Track 1F minimal usable UI/operator flow.

Track 1G provides a deterministic local demo workflow.

## Boundary

- Track 1G does not implement production deployment.
- Track 1G does not implement production authentication.
- Track 1G does not implement RBAC enforcement.
- Track 1G does not implement production signing.
- Track 1G does not implement verifier runtime.
- Track 1G does not implement key custody runtime.
- Track 1G does not approve production promotion.
- Track 1G does not approve production deployment.
- Track 1G preserves the Phase 7D selected-gate manual boundary.
- Selected Runtime Domain: backend/API/database runtime
- Implementation Track: Implementation Track 1 — Backend/API/Database Usable Product Slice
- Product Goal: first usable local product slice
- Runtime Mode: local-only
- Storage Runtime: SQLite local-first MVP
- Product Core API Status: implemented in Track 1E
- Minimal Operator Flow Status: implemented in Track 1F
- End-to-End Demo Pack Status: implemented in Track 1G
- Production Promotion Status: not approved
- Production Deployment Status: not approved
- Production Authentication Status: deferred
- RBAC Enforcement Status: deferred
- Production Signing Status: deferred
- Verifier Runtime Status: deferred
- Key Custody Runtime Status: deferred
- Phase 7D Boundary Status: preserved
- Track 1H is the first approved point for MVP Acceptance Pack implementation, if Track 1G is accepted.

## Required Demo Behavior

The Track 1G demo runner must:

- reset/init local demo storage
- seed deterministic demo data
- verify runtime status
- verify operator surface availability
- create deterministic demo product
- list products
- create deterministic demo affiliate offer linked to product/source
- list affiliate offers
- produce deterministic demo summary

The demo remains local-only, dependency-free, secret-free, and production-free.
