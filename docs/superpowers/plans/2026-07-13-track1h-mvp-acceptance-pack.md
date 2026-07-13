# Track 1H MVP Acceptance Pack Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the docs/tests-only MVP Acceptance Pack that closes Implementation Track 1 for local/demo operation only.

**Architecture:** Add a canonical Track 1H acceptance document and documentation-focused tests. Update only approved docs/state pointers, with no runtime code, endpoint, UI, deployment, auth, RBAC, signing, verifier, or key-custody changes.

**Tech Stack:** Markdown, pytest, Python standard library path/file checks

## Global Constraints

- Track 1H creates the MVP Acceptance Pack for the first usable local product slice.
- Track 1H closes Implementation Track 1 — Backend/API/Database Usable Product Slice.
- Track 1H accepts the local product slice as usable for local/demo operation only.
- Track 1H does not implement runtime code.
- Track 1H does not add new API endpoints.
- Track 1H does not add UI features.
- Track 1H does not approve production promotion.
- Track 1H does not approve production deployment.
- Track 1H preserves the Phase 7D selected-gate manual boundary.

---

### Task 1: Track 1H task, acceptance doc, and pointer updates

**Files:**
- Create: `codex/tasks/103-track1h-mvp-acceptance-pack.md`
- Create: `docs/TRACK1H_MVP_ACCEPTANCE_PACK.md`
- Modify: `docs/ROADMAP.md`
- Modify: `docs/PROJECT_STATE.md`
- Modify: `docs/TRACK1G_END_TO_END_DEMO_PACK.md`

**Interfaces:**
- Consumes: Track 1A through Track 1G docs and runtime status language.
- Produces: the canonical Track 1H MVP acceptance record.

- [ ] Create the Track 1H task file with canonical boundary language.
- [ ] Create the Track 1H acceptance document with the required sections and matrices.
- [ ] Update docs/state pointers to reference Track 1H as accepted for local/demo operation only.
- [ ] Do not modify `scripts/dev/` or any runtime implementation file.

### Task 2: Documentation-focused tests

**Files:**
- Create: `tests/test_track1h_mvp_acceptance_pack.py`

**Interfaces:**
- Consumes: Track 1H task/doc/pointer files.
- Produces: test coverage proving wording, sections, matrices, pointer updates, and forbidden implementation boundaries.

- [ ] Add tests for required files.
- [ ] Add tests for canonical wording.
- [ ] Add tests for required sections and matrices.
- [ ] Add tests for Track 1A through Track 1G references and evidence sections.
- [ ] Add tests that no Track 1H runtime, endpoint, deployment/cloud, production auth, RBAC, signing, verifier, or key-custody files were introduced.

### Task 3: Verification

**Files:**
- All touched Track 1H files.

- [ ] Run `./.venv/bin/python -m pytest tests/test_track1h_mvp_acceptance_pack.py -q`.
- [ ] Run `./.venv/bin/python -m pytest tests/test_track1a_backend_api_database_runtime_selection_record.py tests/test_track1b_backend_api_database_product_slice_plan.py tests/test_track1c_local_backend_api_skeleton.py tests/test_track1d_database_storage_runtime.py tests/test_track1e_product_core_api.py tests/test_track1f_minimal_usable_ui_operator_flow.py tests/test_track1g_end_to_end_demo_pack.py tests/test_track1h_mvp_acceptance_pack.py -q`.
- [ ] Run `./.venv/bin/python -m pytest -q`.
- [ ] Run `git diff --check`.
- [ ] Run `git status --short`.
