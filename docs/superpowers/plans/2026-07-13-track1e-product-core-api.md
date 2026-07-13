# Track 1E Product Core API Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the first usable local Product and AffiliateOffer API flow on top of the Track 1C server surface and the Track 1D SQLite local-first storage/runtime foundation.

**Architecture:** Keep the Track 1C API module as HTTP routing only, extend the Track 1D storage module with deterministic local schema evolution, extend the Track 1D repository narrowly for Product/AffiliateOffer operations, and add one Track 1E helper/service module for validation, repository calls, and response shaping. Preserve local-only runtime status and all deferred boundaries.

**Tech Stack:** Python standard library, `sqlite3`, `http.server`, pytest, Markdown, bash

## Global Constraints

- Track 1E implements the Product Core API for the first usable local product slice.
- Track 1E continues Implementation Track 1 — Backend/API/Database Usable Product Slice.
- Track 1E builds on the Track 1C local backend/API skeleton.
- Track 1E builds on the Track 1D SQLite local-first storage runtime.
- Track 1E implements local Product and AffiliateOffer API endpoints.
- Track 1E uses SQLite local-first MVP storage through the Track 1D repository/data access boundary.
- Track 1E evolves the Track 1D SQLite local-first schema only within the local product-slice runtime boundary.
- Track 1E schema evolution does not approve production database runtime.
- Track 1E schema evolution does not approve PostgreSQL or Aurora runtime.
- Track 1E schema evolution remains limited to SQLite local-first MVP storage.
- Track 1E continues to use the Track 1D repository/data access boundary.
- Track 1E does not implement production authentication.
- Track 1E does not implement RBAC enforcement.
- Track 1E does not implement production signing.
- Track 1E does not implement verifier runtime.
- Track 1E does not implement key custody runtime.
- Track 1E does not implement insight generation.
- Track 1E does not implement recommendation runtime.
- Track 1E does not approve production promotion.
- Track 1E does not approve production deployment.
- Track 1E preserves the Phase 7D selected-gate manual boundary.
- Track 1F is the first approved point for Minimal Usable UI/operator flow implementation, if Track 1E is accepted.
- Remain local-only, deterministic, dependency-free where practical, and use no external infrastructure, no secrets, no production database, no cloud database, and no deployment config.
- Do not add Source API endpoints unless absolutely required for tests; prefer seed/repository setup.
- Do not add CollectionRun workflow API, payment/billing, multi-tenant security, PostgreSQL/Aurora support, or production DB abstractions.

---

### Task 1: Write the Track 1E docs, task record, and focused failing test file

**Files:**
- Create: `codex/tasks/100-track1e-product-core-api.md`
- Create: `docs/TRACK1E_PRODUCT_CORE_API.md`
- Create: `tests/test_track1e_product_core_api.py`
- Modify: `docs/ROADMAP.md`
- Modify: `docs/PROJECT_STATE.md`
- Modify: `docs/TRACK1D_DATABASE_STORAGE_RUNTIME.md`

**Interfaces:**
- Consumes: Track 1C/1D runtime contracts and the approved Track 1E API/design
- Produces: Track 1E canonical wording, document sections/matrices, state pointers, and failing tests for runtime/API behavior

- [ ] **Step 1: Write the failing doc/file existence tests**

Create focused tests like:

```python
def test_track1e_required_files_exist() -> None:
    for path in (
        TASK_FILE,
        DOC,
        THIS_TEST,
        TRACK1E_HELPER_MODULE,
    ):
        assert path.is_file(), f"missing Track 1E file: {path}"
```

- [ ] **Step 2: Run the focused Track 1E test to verify RED**

Run: `./.venv/bin/python -m pytest tests/test_track1e_product_core_api.py::test_track1e_required_files_exist -q`
Expected: FAIL because the Track 1E files do not exist yet.

- [ ] **Step 3: Write the Track 1E docs and pointer updates**

Create the task/doc files and allowed pointer updates with the approved phrases:

```md
Track 1E implements the Product Core API for the first usable local product slice.
Track 1E evolves the Track 1D SQLite local-first schema only within the local product-slice runtime boundary.
Track 1E schema evolution does not approve production database runtime.
Track 1E schema evolution does not approve PostgreSQL or Aurora runtime.
Track 1E schema evolution remains limited to SQLite local-first MVP storage.
Track 1E continues to use the Track 1D repository/data access boundary.
Track 1E does not implement insight generation.
Track 1E does not implement recommendation runtime.
Track 1E does not approve production promotion.
Track 1E does not approve production deployment.
Track 1E preserves the Phase 7D selected-gate manual boundary.
```

- [ ] **Step 4: Re-run the focused Track 1E test**

Run: `./.venv/bin/python -m pytest tests/test_track1e_product_core_api.py::test_track1e_required_files_exist -q`
Expected: PASS

### Task 2: Write failing Track 1E API and schema-evolution tests

**Files:**
- Modify: `tests/test_track1e_product_core_api.py`

**Interfaces:**
- Consumes: `scripts/dev/track1d_local_storage.py`, `scripts/dev/track1d_repository.py`, `scripts/dev/track1c_local_backend_api.py`
- Produces: failing tests for schema evolution, Product/AffiliateOffer endpoints, runtime status, and deterministic errors

- [ ] **Step 1: Write failing schema-evolution tests**

Add tests for both fresh and Track 1D-shaped DBs:

```python
def test_track1e_schema_evolution_supports_existing_track1d_database(tmp_path: Path) -> None:
    ...
    assert "category" in product_columns
    assert "metadata" in product_columns
    assert "source_id" in affiliate_offer_columns
```

- [ ] **Step 2: Write failing endpoint tests**

Add real HTTP tests:

```python
def test_post_products_creates_valid_product(tmp_path: Path) -> None:
    status, payload = _request_json(
        f"{base_url}/products",
        method="POST",
        data={"name": "Desk Lamp", "category": "lighting"},
    )
    assert status == 200
    assert payload["name"] == "Desk Lamp"
```

- [ ] **Step 3: Write failing deterministic error tests**

Add focused negative cases:

```python
def test_malformed_json_returns_deterministic_validation_error(tmp_path: Path) -> None:
    ...
    assert payload == {
        "error": "validation_error",
        "message": "Request body must be valid JSON.",
        "status_code": 400,
    }
```

- [ ] **Step 4: Run the full Track 1E test file to verify RED**

Run: `./.venv/bin/python -m pytest tests/test_track1e_product_core_api.py -q`
Expected: FAIL on missing helper module, missing schema evolution, and missing routes, not on test syntax.

### Task 3: Implement deterministic Track 1E schema evolution and seed refresh

**Files:**
- Modify: `scripts/dev/track1d_local_storage.py`

**Interfaces:**
- Consumes: existing Track 1D local SQLite file
- Produces:
  - deterministic ensure Track 1E schema path for fresh and existing DBs
  - refreshed Track 1E seed rows using `category` and reusable demo `source_id`

- [ ] **Step 1: Add an explicit Track 1E schema target**

Define Track 1E table columns in code:

```python
PRODUCT_COLUMNS = (
    "id", "name", "category", "description", "status", "metadata", "created_at", "updated_at"
)
AFFILIATE_OFFER_COLUMNS = (
    "id", "product_id", "source_id", "title", "offer_url", "price", "currency",
    "commission_rate", "status", "metadata", "created_at", "updated_at"
)
```

- [ ] **Step 2: Implement deterministic local schema evolution**

Use a narrow rebuild/copy path for conflicting Track 1D tables only:

```python
def ensure_track1e_schema(config: LocalStorageConfig) -> dict[str, object]:
    ...
```

Requirements:
- support fresh DB
- support existing Track 1D DB
- no shadow tables retained
- no generic migration framework

- [ ] **Step 3: Refresh deterministic seed data**

Update demo rows:

```python
"products": (
    ("demo-product-track1e", "Track 1E Demo Product", "productivity", "", "active", "{}", ...),
)
```

- [ ] **Step 4: Run the Track 1E schema-focused tests**

Run: `./.venv/bin/python -m pytest tests/test_track1e_product_core_api.py -q`
Expected: schema tests move to PASS; route tests still FAIL.

### Task 4: Extend the Track 1D repository boundary narrowly for Track 1E

**Files:**
- Modify: `scripts/dev/track1d_repository.py`

**Interfaces:**
- Consumes: Track 1E schema from the storage layer
- Produces:
  - `create_product(data: dict[str, object]) -> dict[str, object]`
  - `list_products() -> list[dict[str, object]]`
  - `get_product(product_id: str) -> dict[str, object] | None`
  - `update_product(product_id: str, fields: dict[str, object]) -> dict[str, object] | None`
  - `product_exists(product_id: str) -> bool`
  - `source_exists(source_id: str) -> bool`
  - `create_affiliate_offer(data: dict[str, object]) -> dict[str, object]`
  - `list_affiliate_offers() -> list[dict[str, object]]`

- [ ] **Step 1: Add mapping helpers for Track 1E rows**

Create row serializers with stable types:

```python
def _row_to_product(row: sqlite3.Row) -> dict[str, object]:
    ...
```

- [ ] **Step 2: Implement Product operations**

Add narrow SQL methods only:

```python
def create_product(self, data: dict[str, object]) -> dict[str, object]:
    ...
```

- [ ] **Step 3: Implement AffiliateOffer operations and existence checks**

Add only the required methods:

```python
def source_exists(self, source_id: str) -> bool:
    ...
```

- [ ] **Step 4: Run the Track 1E test file again**

Run: `./.venv/bin/python -m pytest tests/test_track1e_product_core_api.py -q`
Expected: repository-level failures clear; HTTP routing still FAIL.

### Task 5: Implement the Track 1E helper/service module

**Files:**
- Create: `scripts/dev/track1e_product_core_api.py`

**Interfaces:**
- Consumes: `Track1DRepository`, `load_local_storage_config`, `ensure_track1e_schema`
- Produces:
  - `handle_product_create(body: bytes, *, database_path: str | None = None) -> tuple[int, dict[str, object]]`
  - `handle_product_list(*, database_path: str | None = None) -> tuple[int, dict[str, object]]`
  - `handle_product_get(product_id: str, *, database_path: str | None = None) -> tuple[int, dict[str, object]]`
  - `handle_product_patch(product_id: str, body: bytes, *, database_path: str | None = None) -> tuple[int, dict[str, object]]`
  - `handle_affiliate_offer_create(body: bytes, *, database_path: str | None = None) -> tuple[int, dict[str, object]]`
  - `handle_affiliate_offer_list(*, database_path: str | None = None) -> tuple[int, dict[str, object]]`
  - `error_response(status_code: int, error: str, message: str, field_errors: dict[str, str] | None = None) -> tuple[int, dict[str, object]]`

- [ ] **Step 1: Add deterministic JSON parsing and error helpers**

Implement:

```python
def parse_json_object(body: bytes) -> tuple[dict[str, object] | None, tuple[int, dict[str, object]] | None]:
    ...
```

- [ ] **Step 2: Add Product validation and handlers**

Implement exact Track 1E validation rules and response shaping.

- [ ] **Step 3: Add AffiliateOffer validation and handlers**

Implement exact Track 1E validation rules and response shaping.

- [ ] **Step 4: Run the focused Track 1E test file**

Run: `./.venv/bin/python -m pytest tests/test_track1e_product_core_api.py -q`
Expected: service/helper tests pass; Track 1C routing tests still FAIL if not wired yet.

### Task 6: Wire Track 1E routes into the Track 1C API module

**Files:**
- Modify: `scripts/dev/track1c_local_backend_api.py`

**Interfaces:**
- Consumes: Track 1E helper/service handlers
- Produces:
  - preserved `GET /health`, `GET /version`, `GET /runtime/status`
  - `POST /products`
  - `GET /products`
  - `GET /products/{id}`
  - `PATCH /products/{id}`
  - `POST /affiliate-offers`
  - `GET /affiliate-offers`
  - deterministic `404` and `405` responses
  - runtime status fields:
    - `product_core_api_status`
    - `product_endpoint_status`
    - `affiliate_offer_endpoint_status`
    - `insight_generation_status`
    - `recommendation_runtime_status`

- [ ] **Step 1: Add route parsing helpers**

Create small path dispatch helpers:

```python
def _product_id_from_path(path: str) -> str | None:
    ...
```

- [ ] **Step 2: Add `do_POST` and `do_PATCH` support with stable errors**

Implement method handlers with route-aware `405` behavior:

```python
def do_POST(self) -> None:
    ...
```

- [ ] **Step 3: Update runtime status payload**

Return:

```python
"product_core_api_status": "implemented in Track 1E",
"product_endpoint_status": "implemented in Track 1E",
"affiliate_offer_endpoint_status": "implemented in Track 1E",
"insight_generation_status": "not implemented in Track 1E",
"recommendation_runtime_status": "not implemented in Track 1E",
```

- [ ] **Step 4: Run the Track 1E test file and the Track 1A-1E chain**

Run: `./.venv/bin/python -m pytest tests/test_track1e_product_core_api.py -q`
Expected: PASS

Run: `./.venv/bin/python -m pytest tests/test_track1a_backend_api_database_runtime_selection_record.py tests/test_track1b_backend_api_database_product_slice_plan.py tests/test_track1c_local_backend_api_skeleton.py tests/test_track1d_database_storage_runtime.py tests/test_track1e_product_core_api.py -q`
Expected: PASS

### Task 7: Run full verification and inspect final repo state

**Files:**
- Verify only; no new files

**Interfaces:**
- Consumes: all Track 1E runtime/docs/tests changes
- Produces: fresh evidence that Track 1E passes focused checks, chain checks, full suite, and diff hygiene

- [ ] **Step 1: Run focused Track 1E verification**

Run: `./.venv/bin/python -m pytest tests/test_track1e_product_core_api.py -q`
Expected: PASS

- [ ] **Step 2: Run the Track 1A+1B+1C+1D+1E chain**

Run: `./.venv/bin/python -m pytest tests/test_track1a_backend_api_database_runtime_selection_record.py tests/test_track1b_backend_api_database_product_slice_plan.py tests/test_track1c_local_backend_api_skeleton.py tests/test_track1d_database_storage_runtime.py tests/test_track1e_product_core_api.py -q`
Expected: PASS

- [ ] **Step 3: Run the full suite**

Run: `./.venv/bin/python -m pytest -q`
Expected: PASS

- [ ] **Step 4: Run diff hygiene checks**

Run: `git diff --check`
Expected: no output

Run: `git status --short`
Expected: only intended Track 1E files before commit, clean after commit
