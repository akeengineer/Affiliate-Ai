# Track 1F Minimal Usable UI / Operator Flow Design

## Goal

Implement Track 1F as the minimal usable UI/operator flow step for
Implementation Track 1 — Backend/API/Database Usable Product Slice.

Track 1F must make the first local product slice usable by an operator.

## Design Decision

Track 1F uses a simple single-page `GET /operator` HTML view served directly by
the existing Python local backend.

This is the smallest repo-consistent operator surface because:

- Track 1C already owns the local HTTP routing boundary.
- Track 1E already exposes the required Product and AffiliateOffer APIs.
- The task explicitly prefers a local HTML/admin page when it can be done with
  Python standard library only.
- A separate frontend app or build step would widen scope and violate the
  dependency-free local-only boundary.

## Approved Surface

Track 1F adds one local-only operator page:

- `GET /operator`

The page will include:

- a local-only boundary notice
- a runtime status panel
- an add product form
- a product list panel
- an add affiliate offer form
- an affiliate offer list panel
- deterministic result and error panels
- tiny inline JavaScript `fetch` calls to existing Track 1E endpoints only

## Existing API Reuse

The operator page will call only these existing endpoints:

- `GET /runtime/status`
- `POST /products`
- `GET /products`
- `POST /affiliate-offers`
- `GET /affiliate-offers`

Track 1F will not add a new operator-specific mutation API and will not bypass
the Track 1E Product/AffiliateOffer behavior.

## Storage and Source Boundary

Track 1F does not add Source UI/API endpoints.

AffiliateOffer creation will continue to depend on an existing `source_id`
validated through the Track 1D repository/data access boundary. The operator
surface will document the deterministic demo source
`demo-source-track1d` rather than introducing Source CRUD.

## Runtime Status Delta

Track 1F extends `GET /runtime/status` with:

- `minimal_operator_flow_status: implemented in Track 1F`
- `operator_surface_status: implemented in Track 1F`
- `production_frontend_deployment_status: not approved`
- `insight_generation_status: not implemented in Track 1F`
- `recommendation_runtime_status: not implemented in Track 1F`

Track 1F preserves:

- `runtime_mode: local-only`
- `storage_runtime: SQLite local-first MVP`
- `product_core_api_status: implemented in Track 1E`
- `product_endpoint_status: implemented in Track 1E`
- `affiliate_offer_endpoint_status: implemented in Track 1E`
- existing deferred security and promotion/deployment boundary fields

## File Structure

The implementation will stay in the existing local-dev layout:

- Modify `scripts/dev/track1c_local_backend_api.py`
  Route `GET /operator`, return HTML, and extend runtime status fields.
- Create `scripts/dev/track1f_operator_page.py`
  One small helper that renders deterministic HTML and embeds tiny inline
  JavaScript for `fetch` calls.
- Create `codex/tasks/101-track1f-minimal-usable-ui-operator-flow.md`
- Create `docs/TRACK1F_MINIMAL_USABLE_UI_OPERATOR_FLOW.md`
- Create `tests/test_track1f_minimal_usable_ui_operator_flow.py`
- Update `docs/ROADMAP.md`
- Update `docs/PROJECT_STATE.md`
- Update `docs/TRACK1E_PRODUCT_CORE_API.md`

## Error Handling

Track 1F preserves the Track 1E validation and error contract exactly.

The operator page may display returned JSON errors, but it must not change:

- `400 validation_error`
- `404 not_found`
- `405 method_not_allowed`
- `422 validation_error`

## Testing Strategy

Focused Track 1F tests will verify:

- required files and canonical wording
- required sections and matrices
- `GET /operator` returns `200`
- `/operator` returns `text/html`
- the page contains the required operator panels and boundary language
- the page references the approved Track 1E endpoints
- `GET /runtime/status` reports Track 1F operator fields
- existing Product and AffiliateOffer APIs still work unchanged
- validation/error behavior is preserved
- no frontend framework dependencies are introduced
- no production deployment or cloud infrastructure files are introduced

## Non-Goals

Track 1F does not add:

- React, Next.js, Vite, Tailwind, npm packages, or a frontend build step
- Source UI/API
- CollectionRun workflow UI/API
- insight generation
- recommendation runtime
- production frontend deployment
- production authentication
- RBAC enforcement
- production signing
- verifier runtime
- key custody runtime
- cloud infrastructure
- CI/CD deployment pipeline
- production promotion
- production deployment
