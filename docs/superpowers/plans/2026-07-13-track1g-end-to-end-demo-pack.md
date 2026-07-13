# Track 1G End-to-End Demo Pack Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic local demo pack that proves the Track 1C/1D/1E/1F product slice works end to end.

**Architecture:** Add a small Python runner under `scripts/dev/` that resets/seeds SQLite local storage, verifies runtime/operator availability, creates/lists Product and AffiliateOffer records through Track 1E helpers, and emits a deterministic JSON summary. Keep runtime status integration in the existing Track 1C backend.

**Tech Stack:** Python standard library, SQLite via existing Track 1D module, existing Track 1E service helpers, pytest

## Global Constraints

- Track 1G implements the end-to-end demo pack for the first usable local product slice.
- Track 1G continues Implementation Track 1 — Backend/API/Database Usable Product Slice.
- Track 1G builds on the Track 1C local backend/API skeleton.
- Track 1G builds on the Track 1D SQLite local-first storage runtime.
- Track 1G builds on the Track 1E Product Core API.
- Track 1G builds on the Track 1F minimal usable UI/operator flow.
- Track 1G provides a deterministic local demo workflow.
- Track 1G does not implement production deployment.
- Track 1G does not implement production authentication.
- Track 1G does not implement RBAC enforcement.
- Track 1G does not implement production signing.
- Track 1G does not implement verifier runtime.
- Track 1G does not implement key custody runtime.
- Track 1G does not approve production promotion.
- Track 1G does not approve production deployment.
- Track 1G preserves the Phase 7D selected-gate manual boundary.

---

### Task 1: Track 1G documentation and failing tests

**Files:**
- Create: `codex/tasks/102-track1g-end-to-end-demo-pack.md`
- Create: `docs/TRACK1G_END_TO_END_DEMO_PACK.md`
- Create: `tests/test_track1g_end_to_end_demo_pack.py`
- Modify: `docs/ROADMAP.md`
- Modify: `docs/PROJECT_STATE.md`
- Modify: `docs/TRACK1F_MINIMAL_USABLE_UI_OPERATOR_FLOW.md`

**Interfaces:**
- Consumes: existing Track 1C/1D/1E/1F paths and contracts.
- Produces: focused test contract for Track 1G.

- [ ] Write docs/task/tests for Track 1G.
- [ ] Run `./.venv/bin/python -m pytest tests/test_track1g_end_to_end_demo_pack.py -q`.
Expected: FAIL because the runner and Track 1G runtime status fields are not implemented yet.

### Task 2: Demo runner and shell wrapper

**Files:**
- Create: `scripts/dev/track1g_end_to_end_demo_pack.py`
- Create: `scripts/dev/run_track1g_end_to_end_demo_pack.sh`
- Test: `tests/test_track1g_end_to_end_demo_pack.py`

**Interfaces:**
- Produces: `run_demo(database_path: str | None = None, output_path: str | None = None) -> dict[str, object]`

- [ ] Implement deterministic reset/init/seed, runtime/operator verification, Product create/list, AffiliateOffer create/list, and JSON summary emission.
- [ ] Run `./.venv/bin/python -m pytest tests/test_track1g_end_to_end_demo_pack.py -q`.
Expected: FAIL only on missing runtime status fields.

### Task 3: Runtime status integration

**Files:**
- Modify: `scripts/dev/track1c_local_backend_api.py`
- Modify: prior Track 1C/1D/1E/1F tests as needed

**Interfaces:**
- Consumes: existing `_runtime_status_payload(config: Any) -> dict[str, str]`
- Produces: Track 1G runtime fields.

- [ ] Add `end_to_end_demo_pack_status`, `demo_workflow_status`, `production_demo_deployment_status`, and Track 1G deferred insight/recommendation status values.
- [ ] Run focused and chain tests.

### Task 4: Verification

**Files:**
- All touched Track 1G files.

- [ ] Run `./.venv/bin/python -m pytest tests/test_track1g_end_to_end_demo_pack.py -q`.
- [ ] Run `./.venv/bin/python -m pytest tests/test_track1a_backend_api_database_runtime_selection_record.py tests/test_track1b_backend_api_database_product_slice_plan.py tests/test_track1c_local_backend_api_skeleton.py tests/test_track1d_database_storage_runtime.py tests/test_track1e_product_core_api.py tests/test_track1f_minimal_usable_ui_operator_flow.py tests/test_track1g_end_to_end_demo_pack.py -q`.
- [ ] Run `./.venv/bin/python -m pytest -q`.
- [ ] Run `git diff --check`.
- [ ] Run `git status --short`.
