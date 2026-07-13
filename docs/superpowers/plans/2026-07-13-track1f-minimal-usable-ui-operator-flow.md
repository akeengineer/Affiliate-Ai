# Track 1F Minimal Usable UI / Operator Flow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local-only `/operator` HTML surface on top of the existing Track 1E APIs so an operator can view runtime status, add a product, list products, add an affiliate offer, and list affiliate offers without direct SQLite edits.

**Architecture:** Keep HTTP routing in the existing Track 1C backend, add one small Track 1F HTML helper module under `scripts/dev/`, and preserve Track 1E API handlers as the only mutation/listing boundary. Extend runtime status in place and verify the operator page through deterministic local tests.

**Tech Stack:** Python standard library `http.server`, inline HTML/CSS/JavaScript, sqlite3-backed Track 1D/1E local runtime, pytest

## Global Constraints

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
- Use existing Track 1E API endpoints only: `GET /runtime/status`, `POST /products`, `GET /products`, `POST /affiliate-offers`, `GET /affiliate-offers`.
- Do not add React, Next.js, Vite, Tailwind, npm packages, bundlers, or production frontend deployment config.

---

### Task 1: Write Track 1F docs, task record, and focused tests

**Files:**
- Create: `codex/tasks/101-track1f-minimal-usable-ui-operator-flow.md`
- Create: `docs/TRACK1F_MINIMAL_USABLE_UI_OPERATOR_FLOW.md`
- Create: `tests/test_track1f_minimal_usable_ui_operator_flow.py`
- Modify: `docs/ROADMAP.md`
- Modify: `docs/PROJECT_STATE.md`
- Modify: `docs/TRACK1E_PRODUCT_CORE_API.md`

**Interfaces:**
- Consumes: existing Track 1C/1D/1E file paths and runtime behavior
- Produces: Track 1F documentation/test contract and failing tests for `/operator` and runtime status

- [ ] Write the new Track 1F doc/task/tests and update Track 1F state pointers.
- [ ] Run: `./.venv/bin/python -m pytest tests/test_track1f_minimal_usable_ui_operator_flow.py -q`
Expected: FAIL because `/operator` and Track 1F runtime status are not implemented yet.

### Task 2: Add deterministic operator page helper

**Files:**
- Create: `scripts/dev/track1f_operator_page.py`
- Test: `tests/test_track1f_minimal_usable_ui_operator_flow.py`

**Interfaces:**
- Consumes: no new dependencies; static strings and approved endpoint paths
- Produces: `render_operator_page() -> str`

- [ ] Implement `render_operator_page()` with the local-only boundary notice, runtime/product/offer sections, result/error panels, and inline `fetch` calls to the approved Track 1E endpoints.
- [ ] Run: `./.venv/bin/python -m pytest tests/test_track1f_minimal_usable_ui_operator_flow.py -q`
Expected: still FAIL until the backend route is wired.

### Task 3: Wire `/operator` and Track 1F runtime status into the backend

**Files:**
- Modify: `scripts/dev/track1c_local_backend_api.py`
- Test: `tests/test_track1f_minimal_usable_ui_operator_flow.py`
- Test: `tests/test_track1c_local_backend_api_skeleton.py`
- Test: `tests/test_track1d_database_storage_runtime.py`
- Test: `tests/test_track1e_product_core_api.py`

**Interfaces:**
- Consumes: `render_operator_page() -> str`
- Produces: `GET /operator` HTML response and extended runtime status fields

- [ ] Add the `/operator` GET route, a text/html response path, and runtime status fields:
  - `minimal_operator_flow_status`
  - `operator_surface_status`
  - `production_frontend_deployment_status`
  - updated `insight_generation_status`
  - updated `recommendation_runtime_status`
- [ ] Run: `./.venv/bin/python -m pytest tests/test_track1f_minimal_usable_ui_operator_flow.py -q`
Expected: PASS

### Task 4: Update chain tests for Track 1F runtime status evolution

**Files:**
- Modify: `tests/test_track1c_local_backend_api_skeleton.py`
- Modify: `tests/test_track1d_database_storage_runtime.py`
- Modify: `tests/test_track1e_product_core_api.py`

**Interfaces:**
- Consumes: Track 1F runtime status payload
- Produces: chain tests that assert the current post-Track-1F contract

- [ ] Update older exact-payload assertions so they reflect Track 1F’s added runtime status fields while preserving prior boundaries.
- [ ] Run: `./.venv/bin/python -m pytest tests/test_track1a_backend_api_database_runtime_selection_record.py tests/test_track1b_backend_api_database_product_slice_plan.py tests/test_track1c_local_backend_api_skeleton.py tests/test_track1d_database_storage_runtime.py tests/test_track1e_product_core_api.py tests/test_track1f_minimal_usable_ui_operator_flow.py -q`
Expected: PASS

### Task 5: Full verification and repo hygiene

**Files:**
- Modify: any touched Track 1F files if needed from verification results

**Interfaces:**
- Consumes: complete Track 1F implementation
- Produces: verified clean worktree diff

- [ ] Run: `./.venv/bin/python -m pytest -q`
Expected: PASS
- [ ] Run: `git diff --check`
Expected: no output
- [ ] Run: `git status --short`
Expected: only intended Track 1F files remain modified before commit

## Self-Review

- Spec coverage: the plan covers docs/task/tests, operator helper rendering, backend route wiring, runtime status updates, chain test updates, and full verification.
- Placeholder scan: no TODO/TBD placeholders remain.
- Type consistency: the only new helper interface is `render_operator_page() -> str`, and runtime status field names match the approved Track 1F contract.
