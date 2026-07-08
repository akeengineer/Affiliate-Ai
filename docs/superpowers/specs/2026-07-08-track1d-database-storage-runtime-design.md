# Track 1D Database/Storage Runtime Design

## Goal

Implement Track 1D as the local database/storage runtime step for
Implementation Track 1 — Backend/API/Database Usable Product Slice.

Track 1D implements the local database/storage runtime for the first usable
local product slice.

Track 1D uses SQLite for local-first MVP storage.

Track 1D continues Implementation Track 1 — Backend/API/Database Usable
Product Slice.

Track 1D is an explicit local product-slice runtime exception to the earlier
Phase 1 Obsidian-only/no-database constraint.

The Track 1D exception is limited to SQLite local-first MVP storage for
Implementation Track 1.

The Track 1D exception does not approve production database runtime.

The Track 1D exception does not approve production promotion.

The Track 1D exception does not approve production deployment.

Track 1D does not implement Product or AffiliateOffer full CRUD API.

Track 1D does not implement insight generation.

Track 1D does not implement recommendation runtime.

Track 1D preserves the Phase 7D selected-gate manual boundary.

Track 1E is the first approved point for Product Core API implementation, if
Track 1D is accepted.

## Scope Decision

Track 1D adds a narrow local SQLite runtime under the existing `scripts/dev/`
structure introduced by Track 1C. The new runtime remains local-only,
dependency-free where practical, and uses Python standard library `sqlite3`
for deterministic schema initialization, reset, seed, and repository smoke
behavior.

This track does not widen the exception beyond the first usable local product
slice. Obsidian remains the project memory system for the broader Phase 1
workflow. The Track 1D exception exists only because Track 1A selected
`backend/API/database runtime`, Track 1B planned SQLite local-first storage,
and Track 1C introduced the local backend/API skeleton.

## File-Level Design

### New runtime files

- `scripts/dev/track1d_local_storage.py`
  - resolve a local SQLite path
  - define the deterministic schema contract
  - implement `init_storage`, `reset_storage`, `seed_demo_data`, and
    `get_storage_status`
  - use only standard library modules
- `scripts/dev/track1d_repository.py`
  - provide repository/data access foundation over the Track 1D schema
  - expose small read/write helpers for smoke coverage, not full CRUD services
- `scripts/dev/run_track1d_local_storage.py`
  - command-line entrypoint for `init`, `reset`, `seed`, and `status`
- `scripts/dev/run_track1d_local_storage.sh`
  - repo-consistent shell wrapper matching existing `scripts/dev/` patterns

### Modified runtime file

- `scripts/dev/track1c_local_backend_api.py`
  - update `GET /runtime/status` to report Track 1D storage status when the
    storage layer can be queried consistently

### Required docs/tests/task files

- `codex/tasks/099-track1d-database-storage-runtime.md`
- `docs/TRACK1D_DATABASE_STORAGE_RUNTIME.md`
- `tests/test_track1d_database_storage_runtime.py`

### Allowed pointer updates

- `docs/ROADMAP.md`
- `docs/PROJECT_STATE.md`
- `docs/TRACK1C_LOCAL_BACKEND_API_SKELETON.md`

## Schema Design

Track 1D will create these local SQLite tables:

- `products`
- `affiliate_offers`
- `sources`
- `collection_runs`
- `insights`
- `recommendations`

Each table will use a small deterministic schema aligned with Track 1B:

- stable text primary keys
- required timestamps stored as ISO-8601 UTC text
- required status/type fields as text
- foreign-key references from child tables back to `products`
- optional references kept minimal to avoid premature API design

The schema will be created with rerunnable `CREATE TABLE IF NOT EXISTS`
statements and foreign-key enforcement enabled per connection.

## Repository Boundary

Track 1D adds repository primitives, not application services and not full
CRUD API behavior.

The repository layer will expose:

- table existence inspection
- insert helpers for deterministic demo rows
- list/count helpers for smoke assertions
- product lookup and related child lookup helpers

The repository layer will not expose:

- HTTP handlers
- validation-heavy Product/AffiliateOffer CRUD services
- collection workflow orchestration
- insight generation
- recommendation runtime

## Runtime Status Integration

Track 1D will update Track 1C `GET /runtime/status` to include:

- `database_storage_runtime_status: implemented in Track 1D as SQLite local-first MVP`
- `storage_runtime: SQLite local-first MVP`
- `product_crud_status: not implemented in Track 1D`
- `insight_generation_status: not implemented in Track 1D`

The status payload remains deterministic and local-only. No endpoint beyond
the existing Track 1C surface is added in this track.

## Deterministic Seed Strategy

Track 1D seed behavior will create a small, fixed demo dataset:

- one product
- one affiliate offer
- one source
- one collection run
- one insight
- one recommendation

Seed behavior must be idempotent after reset and deterministic across runs.
The goal is schema proof and repository smoke coverage, not sample data depth.

## Test Strategy

`tests/test_track1d_database_storage_runtime.py` will cover:

- required files and canonical wording
- required document sections and matrices
- schema initialization
- reset behavior
- deterministic seed behavior
- required tables existence
- repository read/write smoke behavior
- runtime status payload updates through the Track 1C API module
- absence of Track 1E+ scope such as full CRUD API, insight generation, and
  recommendation runtime
- absence of production database, deployment, cloud, and security-runtime
  expansions

## Non-Goals

Track 1D does not implement:

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
- production promotion
- production deployment

## Verification Plan

Run exactly:

- `./.venv/bin/python -m pytest tests/test_track1d_database_storage_runtime.py -q`
- `./.venv/bin/python -m pytest tests/test_track1a_backend_api_database_runtime_selection_record.py tests/test_track1b_backend_api_database_product_slice_plan.py tests/test_track1c_local_backend_api_skeleton.py tests/test_track1d_database_storage_runtime.py -q`
- `./.venv/bin/python -m pytest -q`
- `git diff --check`
