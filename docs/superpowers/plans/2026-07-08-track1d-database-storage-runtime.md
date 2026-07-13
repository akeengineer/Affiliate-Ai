# Track 1D Database/Storage Runtime Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the Track 1D SQLite local-first storage runtime, repository foundation, runtime status integration, and required docs/tests without widening scope into Track 1E or any production runtime.

**Architecture:** Keep Track 1D inside the existing `scripts/dev/` local runtime structure from Track 1C. Use one storage module for config/schema/init/reset/seed/status, one repository module for small table-level operations, one runner pair for local commands, one focused Track 1D test file, and allowed docs/task updates that explicitly preserve the narrow exception boundary.

**Tech Stack:** Python standard library, `sqlite3`, `http.server`, pytest, Markdown, bash

## Global Constraints

- Track 1D implements the local database/storage runtime for the first usable local product slice.
- Track 1D uses SQLite for local-first MVP storage.
- Track 1D continues Implementation Track 1 — Backend/API/Database Usable Product Slice.
- Track 1D is an explicit local product-slice runtime exception to the earlier Phase 1 Obsidian-only/no-database constraint.
- The Track 1D exception is limited to SQLite local-first MVP storage for Implementation Track 1.
- The Track 1D exception does not approve production database runtime.
- The Track 1D exception does not approve production promotion.
- The Track 1D exception does not approve production deployment.
- Track 1D does not implement Product or AffiliateOffer full CRUD API.
- Track 1D does not implement insight generation.
- Track 1D does not implement recommendation runtime.
- Track 1D preserves the Phase 7D selected-gate manual boundary.
- Track 1E is the first approved point for Product Core API implementation, if Track 1D is accepted.
- Use Python standard library only if practical.
- Use `sqlite3` from the Python standard library.
- Require no external infrastructure, no secrets, no production database, and no cloud database.
- Keep runtime local-only and deterministic.
- Do not add Product/AffiliateOffer full CRUD API, CollectionRun workflow API, production authentication, RBAC enforcement, production signing, verifier runtime, key custody runtime, deployment files, cloud infrastructure, or CI/CD deployment pipeline.

---

### Task 1: Write the Track 1D spec, task record, and pointer docs

**Files:**
- Create: `codex/tasks/099-track1d-database-storage-runtime.md`
- Create: `docs/TRACK1D_DATABASE_STORAGE_RUNTIME.md`
- Modify: `docs/TRACK1C_LOCAL_BACKEND_API_SKELETON.md`
- Modify: `docs/ROADMAP.md`
- Modify: `docs/PROJECT_STATE.md`

**Interfaces:**
- Consumes: Track 1A/1B/1C wording and the approved exception boundary
- Produces: canonical Track 1D docs/tests wording and pointer updates used by the Track 1D test file

- [ ] **Step 1: Write the failing documentation expectations**

Add tests that assert these files and phrases exist before writing the docs:

```python
def test_track1d_required_files_exist() -> None:
    assert (REPO_ROOT / "codex/tasks/099-track1d-database-storage-runtime.md").is_file()
    assert (REPO_ROOT / "docs/TRACK1D_DATABASE_STORAGE_RUNTIME.md").is_file()
```

- [ ] **Step 2: Run the focused test to verify it fails**

Run: `./.venv/bin/python -m pytest tests/test_track1d_database_storage_runtime.py::test_track1d_required_files_exist -q`
Expected: FAIL because the Track 1D files do not exist yet.

- [ ] **Step 3: Write the Track 1D task/doc files and pointer updates**

Create the new task/doc files and update the allowed pointer docs so they include:

```md
Track 1D implements the local database/storage runtime for the first usable local product slice.
Track 1D uses SQLite for local-first MVP storage.
Track 1D continues Implementation Track 1 — Backend/API/Database Usable Product Slice.
Track 1D is an explicit local product-slice runtime exception to the earlier Phase 1 Obsidian-only/no-database constraint.
The Track 1D exception is limited to SQLite local-first MVP storage for Implementation Track 1.
The Track 1D exception does not approve production database runtime.
The Track 1D exception does not approve production promotion.
The Track 1D exception does not approve production deployment.
Track 1D does not implement Product or AffiliateOffer full CRUD API.
Track 1D does not implement insight generation.
Track 1D does not implement recommendation runtime.
Track 1D preserves the Phase 7D selected-gate manual boundary.
Track 1E is the first approved point for Product Core API implementation, if Track 1D is accepted.
```

- [ ] **Step 4: Run the docs-focused test to verify it passes**

Run: `./.venv/bin/python -m pytest tests/test_track1d_database_storage_runtime.py::test_track1d_required_files_exist -q`
Expected: PASS

### Task 2: Add Track 1D failing storage/runtime tests

**Files:**
- Create: `tests/test_track1d_database_storage_runtime.py`

**Interfaces:**
- Consumes: `scripts/dev/track1d_local_storage.py`, `scripts/dev/track1d_repository.py`, `scripts/dev/track1c_local_backend_api.py`
- Produces: failing tests for schema init/reset/seed/status and runtime status integration

- [ ] **Step 1: Write failing tests for the storage interfaces**

Define the expected interfaces:

```python
storage_module = _load_module("track1d_storage", STORAGE_MODULE)
repo_module = _load_module("track1d_repo", REPOSITORY_MODULE)

config = storage_module.load_local_storage_config({"AFFILIATE_STORAGE_PATH": str(db_path)})
storage_module.init_storage(config)
storage_module.seed_demo_data(config)
status = storage_module.get_storage_status(config)

repository = repo_module.Track1DRepository.connect(config.database_path)
```

- [ ] **Step 2: Run the focused test file to verify RED**

Run: `./.venv/bin/python -m pytest tests/test_track1d_database_storage_runtime.py -q`
Expected: FAIL because the Track 1D modules do not exist and runtime status has not been updated.

- [ ] **Step 3: Keep the tests focused on Track 1D boundaries**

Include explicit assertions such as:

```python
assert status["storage_runtime"] == "SQLite local-first MVP"
assert payload["product_crud_status"] == "not implemented in Track 1D"
assert payload["insight_generation_status"] == "not implemented in Track 1D"
assert "POST /products" not in _text(DOC)
```

- [ ] **Step 4: Re-run the focused test after edits to keep failures targeted**

Run: `./.venv/bin/python -m pytest tests/test_track1d_database_storage_runtime.py -q`
Expected: FAIL only on missing implementation, not on syntax or import errors.

### Task 3: Implement the Track 1D storage module and runner

**Files:**
- Create: `scripts/dev/track1d_local_storage.py`
- Create: `scripts/dev/run_track1d_local_storage.py`
- Create: `scripts/dev/run_track1d_local_storage.sh`

**Interfaces:**
- Consumes: local env overrides, stdlib `sqlite3`
- Produces:
  - `load_local_storage_config(env: Mapping[str, str] | None = None, *, database_path_override: str | None = None) -> LocalStorageConfig`
  - `init_storage(config: LocalStorageConfig) -> dict[str, object]`
  - `reset_storage(config: LocalStorageConfig) -> dict[str, object]`
  - `seed_demo_data(config: LocalStorageConfig) -> dict[str, object]`
  - `get_storage_status(config: LocalStorageConfig) -> dict[str, object]`

- [ ] **Step 1: Implement config and schema helpers**

Create a small config object and deterministic schema list:

```python
class LocalStorageConfig:
    __slots__ = ("database_path", "runtime_mode", "storage_runtime")

def schema_statements() -> tuple[str, ...]:
    return (
        "CREATE TABLE IF NOT EXISTS products (...)",
        "CREATE TABLE IF NOT EXISTS affiliate_offers (...)",
        "CREATE TABLE IF NOT EXISTS sources (...)",
        "CREATE TABLE IF NOT EXISTS collection_runs (...)",
        "CREATE TABLE IF NOT EXISTS insights (...)",
        "CREATE TABLE IF NOT EXISTS recommendations (...)",
    )
```

- [ ] **Step 2: Implement `init_storage`, `reset_storage`, `seed_demo_data`, and `get_storage_status`**

Keep behavior deterministic and local-only:

```python
def init_storage(config: LocalStorageConfig) -> dict[str, object]:
    ...

def reset_storage(config: LocalStorageConfig) -> dict[str, object]:
    ...

def seed_demo_data(config: LocalStorageConfig) -> dict[str, object]:
    ...

def get_storage_status(config: LocalStorageConfig) -> dict[str, object]:
    return {
        "database_storage_runtime_status": "implemented in Track 1D as SQLite local-first MVP",
        "storage_runtime": "SQLite local-first MVP",
        "database_path": str(config.database_path),
        "tables": [...],
    }
```

- [ ] **Step 3: Implement the local runner pair**

Support only the approved operations:

```python
parser.add_argument("command", choices=("init", "reset", "seed", "status"))
```

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
./.venv/bin/python scripts/dev/run_track1d_local_storage.py "$@"
```

- [ ] **Step 4: Run focused tests for the storage module**

Run: `./.venv/bin/python -m pytest tests/test_track1d_database_storage_runtime.py -q`
Expected: storage tests move to PASS or to the next missing repository/API integration failure.

### Task 4: Implement the Track 1D repository foundation

**Files:**
- Create: `scripts/dev/track1d_repository.py`

**Interfaces:**
- Consumes: `sqlite3.Connection`, Track 1D schema
- Produces:
  - `Track1DRepository.connect(database_path: str | Path) -> Track1DRepository`
  - `table_names(self) -> list[str]`
  - `insert_demo_records(self) -> dict[str, int]`
  - `count_rows(self, table_name: str) -> int`
  - `get_product(self, product_id: str) -> dict[str, str] | None`
  - `list_affiliate_offers(self, product_id: str) -> list[dict[str, str]]`

- [ ] **Step 1: Implement the repository wrapper**

Start with a minimal class:

```python
class Track1DRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
```

- [ ] **Step 2: Add smoke-level read/write methods only**

Implement inserts and simple reads, not full CRUD:

```python
def insert_demo_records(self) -> dict[str, int]:
    ...

def get_product(self, product_id: str) -> dict[str, str] | None:
    ...
```

- [ ] **Step 3: Ensure seed and repository use the same deterministic rows**

Keep one shared demo dataset shape:

```python
DEMO_PRODUCT_ID = "demo-product-track1d"
```

- [ ] **Step 4: Run focused tests again**

Run: `./.venv/bin/python -m pytest tests/test_track1d_database_storage_runtime.py -q`
Expected: repository smoke tests pass; any remaining failures should be in Track 1C runtime status or docs wording.

### Task 5: Integrate Track 1D storage status into Track 1C runtime status

**Files:**
- Modify: `scripts/dev/track1c_local_backend_api.py`

**Interfaces:**
- Consumes: `load_local_storage_config`, `get_storage_status`
- Produces: updated `GET /runtime/status` payload with Track 1D storage fields and unchanged local-only boundary behavior

- [ ] **Step 1: Add a failing API-status assertion if not already present**

Use a focused assertion:

```python
assert payload["database_storage_runtime_status"] == "implemented in Track 1D as SQLite local-first MVP"
assert payload["storage_runtime"] == "SQLite local-first MVP"
```

- [ ] **Step 2: Update the runtime status payload**

Load storage status lazily and merge only the allowed fields:

```python
storage_status = _storage_runtime_status()
return {
    "selected_runtime_domain": config.selected_runtime_domain,
    "runtime_mode": config.runtime_mode,
    ...
    "database_storage_runtime_status": storage_status["database_storage_runtime_status"],
    "storage_runtime": storage_status["storage_runtime"],
    "product_crud_status": "not implemented in Track 1D",
    "insight_generation_status": "not implemented in Track 1D",
}
```

- [ ] **Step 3: Keep failure behavior deterministic**

If storage is unavailable, preserve a safe local-only status:

```python
except Exception:
    return {
        "database_storage_runtime_status": "not implemented in Track 1C",
        "storage_runtime": "unavailable",
    }
```

- [ ] **Step 4: Run the focused Track 1D test file**

Run: `./.venv/bin/python -m pytest tests/test_track1d_database_storage_runtime.py -q`
Expected: PASS

### Task 6: Run required verification and inspect the final diff

**Files:**
- Verify only; no new files

**Interfaces:**
- Consumes: all Track 1D files and the allowed pointer updates
- Produces: fresh evidence that Track 1D passes required checks and stays within scope

- [ ] **Step 1: Run the Track 1D focused verification**

Run: `./.venv/bin/python -m pytest tests/test_track1d_database_storage_runtime.py -q`
Expected: PASS

- [ ] **Step 2: Run the Track 1A-1D chain verification**

Run: `./.venv/bin/python -m pytest tests/test_track1a_backend_api_database_runtime_selection_record.py tests/test_track1b_backend_api_database_product_slice_plan.py tests/test_track1c_local_backend_api_skeleton.py tests/test_track1d_database_storage_runtime.py -q`
Expected: PASS

- [ ] **Step 3: Run the full repo verification**

Run: `./.venv/bin/python -m pytest -q`
Expected: PASS

- [ ] **Step 4: Run whitespace/diff verification**

Run: `git diff --check`
Expected: no output
