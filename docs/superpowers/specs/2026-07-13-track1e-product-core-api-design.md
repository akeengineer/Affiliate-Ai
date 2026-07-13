# Track 1E Product Core API Design

## Goal

Implement Track 1E as the Product Core API step for Implementation Track 1 —
Backend/API/Database Usable Product Slice.

Track 1E implements the Product Core API for the first usable local product
slice.

Track 1E continues Implementation Track 1 — Backend/API/Database Usable
Product Slice.

Track 1E builds on the Track 1C local backend/API skeleton.

Track 1E builds on the Track 1D SQLite local-first storage runtime.

Track 1E implements local Product and AffiliateOffer API endpoints.

Track 1E uses SQLite local-first MVP storage through the Track 1D
repository/data access boundary.

Track 1E evolves the Track 1D SQLite local-first schema only within the local
product-slice runtime boundary.

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

Track 1F is the first approved point for Minimal Usable UI/operator flow
implementation, if Track 1E is accepted.

## Scope Decision

Track 1E adds the first usable local Product and AffiliateOffer API flow on top
of the existing Track 1C HTTP skeleton and the Track 1D SQLite local-first
storage/runtime foundation.

The implementation remains local-only, dependency-free where practical, and
limited to:

- Product endpoints
- AffiliateOffer endpoints
- deterministic validation and error responses
- deterministic local schema evolution for `products` and
  `affiliate_offers`
- narrow Track 1D repository extensions
- runtime status updates

Track 1E does not widen into Source APIs, CollectionRun workflow APIs, insight
generation, recommendation runtime, production runtime, or deployment scope.

## File-Level Design

### New files

- `scripts/dev/track1e_product_core_api.py`
  - Track 1E helper/service module
  - owns JSON parsing, validation, repository calls, and response shaping
- `codex/tasks/100-track1e-product-core-api.md`
- `docs/TRACK1E_PRODUCT_CORE_API.md`
- `tests/test_track1e_product_core_api.py`

### Modified files

- `scripts/dev/track1c_local_backend_api.py`
  - HTTP routing only
  - preserves existing Track 1C routes
  - adds Track 1E Product/AffiliateOffer routes and deterministic error wiring
- `scripts/dev/track1d_local_storage.py`
  - deterministic Track 1E schema evolution path
  - Track 1E seed shape
- `scripts/dev/track1d_repository.py`
  - Product/AffiliateOffer repository operations required by Track 1E
- `docs/ROADMAP.md`
- `docs/PROJECT_STATE.md`
- `docs/TRACK1D_DATABASE_STORAGE_RUNTIME.md`

## Exact Schema Delta: Track 1D -> Track 1E

### `products`

Track 1D foundation schema:

- `id`
- `name`
- `marketplace`
- `status`
- `created_at`
- `updated_at`

Track 1E schema:

- preserve: `id`, `name`, `status`, `created_at`, `updated_at`
- add: `category`, `description`, `metadata`
- replace/deprecate for API purposes: `marketplace -> category`

Design decision:

- new Track 1E API behavior reads/writes `category`
- `marketplace` is not part of the Track 1E API contract
- local schema evolution may rebuild the local table deterministically to land
  the approved Track 1E shape cleanly

### `affiliate_offers`

Track 1D foundation schema:

- `id`
- `product_id`
- `program_name`
- `commission_model`
- `created_at`
- `updated_at`

Track 1E schema:

- preserve: `id`, `product_id`, `created_at`, `updated_at`
- add: `source_id`, `title`, `offer_url`, `price`, `currency`,
  `commission_rate`, `status`, `metadata`
- replace/deprecate for API purposes: `program_name`, `commission_model`

Design decision:

- new Track 1E API behavior reads/writes the Track 1E fields only
- old foundation-only fields are not part of the Track 1E API contract

### `sources`

- preserve existing schema
- reuse deterministic Track 1D demo source for `source_id` validation and seed

### `collection_runs`, `insights`, `recommendations`

- preserve existing schema
- preserve storage-only role
- do not add workflow/generation/runtime behavior in Track 1E

## Routing Design

Track 1C remains the server surface and process entrypoint.

Preserved routes:

- `GET /health`
- `GET /version`
- `GET /runtime/status`

Added routes:

- `POST /products`
- `GET /products`
- `GET /products/{id}`
- `PATCH /products/{id}`
- `POST /affiliate-offers`
- `GET /affiliate-offers`

`track1c_local_backend_api.py` remains the HTTP-only routing module. Track 1E
application behavior lives in the Track 1E helper/service module.

## Endpoint Contract

### Products

`POST /products`

- required: `name`, `category`
- optional: `description`, `status`, `metadata`
- success returns full product record with timestamps and generated `id`

`GET /products`

- returns `{ "products": [...], "count": <int> }`

`GET /products/{id}`

- returns one product when found
- returns deterministic `404 not_found` when missing

`PATCH /products/{id}`

- allowed fields: `name`, `category`, `description`, `status`, `metadata`
- rejects empty patch bodies and unknown fields
- returns full updated product record

### Affiliate Offers

`POST /affiliate-offers`

- required: `product_id`, `source_id`, `offer_url`
- optional: `title`, `price`, `currency`, `commission_rate`, `status`,
  `metadata`
- validates referenced product and source existence
- returns full created offer record

`GET /affiliate-offers`

- returns `{ "affiliate_offers": [...], "count": <int> }`

## Error Contract

Track 1E uses one stable deterministic JSON error serializer for all non-2xx
responses.

Error shapes:

- malformed JSON -> `400`, `error: validation_error`
- missing route resource -> `404`, `error: not_found`
- unsupported method on supported route -> `405`, `error: method_not_allowed`
- semantic validation failure -> `422`, `error: validation_error`

Optional `field_errors` is allowed only if deterministic.

## Repository Boundary

Track 1E extends `Track1DRepository` only with:

- `create_product(data: dict[str, object]) -> dict[str, object]`
- `list_products() -> list[dict[str, object]]`
- `get_product(product_id: str) -> dict[str, object] | None`
- `update_product(product_id: str, fields: dict[str, object]) -> dict[str, object] | None`
- `product_exists(product_id: str) -> bool`
- `source_exists(source_id: str) -> bool`
- `create_affiliate_offer(data: dict[str, object]) -> dict[str, object]`
- `list_affiliate_offers() -> list[dict[str, object]]`

The repository remains the SQL/data access boundary and does not become a
generic CRUD framework.

## Runtime Status Design

Track 1E preserves the Track 1C/1D runtime status fields and adds:

- `product_core_api_status: implemented in Track 1E`
- `product_endpoint_status: implemented in Track 1E`
- `affiliate_offer_endpoint_status: implemented in Track 1E`
- `insight_generation_status: not implemented in Track 1E`
- `recommendation_runtime_status: not implemented in Track 1E`

## Test Strategy

`tests/test_track1e_product_core_api.py` will verify:

- required files, wording, sections, and matrices
- Track 1D -> Track 1E schema evolution for fresh DB and existing Track 1D DB
- preserved Track 1C endpoints
- Product API create/list/get/patch
- AffiliateOffer API create/list
- deterministic error responses for malformed JSON, missing resources,
  unsupported methods, unsupported routes, and validation failures
- runtime status Track 1E fields
- preservation of deferred boundaries and absence of production/runtime-expansion files

## Non-Goals

Track 1E does not implement:

- Source API endpoints except seed/repository support
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
- production promotion
- production deployment

## Verification Plan

Run exactly:

- `./.venv/bin/python -m pytest tests/test_track1e_product_core_api.py -q`
- `./.venv/bin/python -m pytest tests/test_track1a_backend_api_database_runtime_selection_record.py tests/test_track1b_backend_api_database_product_slice_plan.py tests/test_track1c_local_backend_api_skeleton.py tests/test_track1d_database_storage_runtime.py tests/test_track1e_product_core_api.py -q`
- `./.venv/bin/python -m pytest -q`
- `git diff --check`
- `git status --short`
