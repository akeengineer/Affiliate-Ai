from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/097-track1b-backend-api-database-product-slice-plan.md"
DOC = REPO_ROOT / "docs/TRACK1B_BACKEND_API_DATABASE_PRODUCT_SLICE_PLAN.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
TRACK1A_DOC = REPO_ROOT / "docs/TRACK1A_BACKEND_API_DATABASE_RUNTIME_SELECTION_RECORD.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(_text(path).lower().replace("`", "").split())


def _assert_all_tokens(text: str, tokens: tuple[str, ...] | list[str], *, label: str) -> None:
    for token in tokens:
        assert token in text, f"missing {label}: {token}"


def test_track1b_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Track 1B file: {path}"


def test_track1b_required_canonical_wording_exists() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "Track 1B defines the backend/API/database product slice implementation plan for the first usable local product slice.",
            "Track 1B continues Implementation Track 1 — Backend/API/Database Usable Product Slice.",
            "Track 1B does not implement runtime code.",
            "Track 1B does not add backend/API/database implementation files.",
            "Track 1B does not approve production promotion.",
            "Track 1B does not approve production deployment.",
            "Track 1B preserves the Phase 7D selected-gate manual boundary.",
            "Selected Runtime Domain: backend/API/database runtime",
            "Implementation Track: Implementation Track 1 — Backend/API/Database Usable Product Slice",
            "Product Goal: first usable local product slice",
            "Production Promotion Status: not approved",
            "Production Deployment Status: not approved",
            "Production Authentication Status: deferred",
            "RBAC Enforcement Status: deferred",
            "Production Signing Status: deferred",
            "Verifier Runtime Status: deferred",
            "Key Custody Runtime Status: deferred",
            "Phase 7D Boundary Status: preserved",
            "Track 1A selects backend/API/database runtime as the first runtime domain for a usable product slice.",
            "Track 1C is the first approved point for local backend/API skeleton implementation, if Track 1B is accepted.",
            "SQLite is the default storage choice for the first local product slice because it requires no external infrastructure, supports deterministic demo workflows, keeps reset and seed operations simple, and can be migrated to PostgreSQL or Aurora later after the product slice proves useful.",
        ),
        label="canonical wording",
    )


def test_track1b_task_file_preserves_core_boundary_wording() -> None:
    text = _text(TASK_FILE)
    _assert_all_tokens(
        text,
        (
            "Track 1B defines the backend/API/database product slice implementation plan for the first usable local product slice.",
            "Track 1B continues Implementation Track 1 — Backend/API/Database Usable Product Slice.",
            "Track 1B does not implement runtime code.",
            "Track 1B does not add backend/API/database implementation files.",
            "Track 1B does not approve production promotion.",
            "Track 1B does not approve production deployment.",
            "Track 1B preserves the Phase 7D selected-gate manual boundary.",
        ),
        label="task token",
    )


def test_track1b_required_sections_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "track 1b purpose",
            "relationship to track 1a",
            "product slice goal",
            "local-first runtime boundary",
            "backend service plan",
            "api surface plan",
            "database/storage plan",
            "product entity model",
            "repository/data access plan",
            "validation and error handling plan",
            "deterministic insight generation plan",
            "minimal ui or operator flow plan",
            "local run command plan",
            "seed and reset plan",
            "test plan",
            "demo acceptance flow",
            "rollback and cleanup plan",
            "deferred security and hardening scope",
            "production promotion exclusion",
            "production deployment exclusion",
            "phase 7d manual boundary preservation",
            "implementation guardrails",
            "non-goals and forbidden implementations",
            "acceptance criteria",
            "recommended next step",
            "recommended next major subphase",
        ),
        label="section",
    )


def test_track1b_track_relationships_and_boundary_language_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "track 1b defines the backend/api/database product slice implementation plan for the first usable local product slice",
            "track 1b continues implementation track 1 — backend/api/database usable product slice",
            "track 1b does not implement runtime code",
            "track 1b does not add backend/api/database implementation files",
            "track 1b does not approve production promotion",
            "track 1b does not approve production deployment",
            "track 1b preserves the phase 7d selected-gate manual boundary",
            "track 1a selects backend/api/database runtime as the first runtime domain for a usable product slice",
            "track 1c is the first approved point for local backend/api skeleton implementation, if track 1b is accepted",
            "selected runtime domain: backend/api/database runtime",
            "implementation track: implementation track 1 — backend/api/database usable product slice",
            "product goal: first usable local product slice",
            "production authentication status: deferred",
            "rbac enforcement status: deferred",
            "production signing status: deferred",
            "verifier runtime status: deferred",
            "key custody runtime status: deferred",
            "phase 7d boundary status: preserved",
        ),
        label="relationship and boundary token",
    )


def test_track1b_required_entities_endpoints_and_storage_decision_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "Product",
            "AffiliateOffer",
            "Source",
            "CollectionRun",
            "Insight",
            "Recommendation",
            "GET /health",
            "GET /version",
            "GET /runtime/status",
            "POST /products",
            "GET /products",
            "GET /products/{id}",
            "PATCH /products/{id}",
            "POST /affiliate-offers",
            "GET /affiliate-offers",
            "POST /collection-runs",
            "GET /collection-runs/{id}",
            "POST /insights/generate",
            "GET /insights",
            "SQLite is the default storage choice for the first local product slice because it requires no external infrastructure, supports deterministic demo workflows, keeps reset and seed operations simple, and can be migrated to PostgreSQL or Aurora later after the product slice proves useful.",
        ),
        label="entity, endpoint, or storage token",
    )


def test_track1b_required_matrices_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "| Entity | Purpose | Required Fields | Validation Rules | Relationship | Track Introduced |",
            "| Endpoint | Method | Purpose | Request Shape | Response Shape | Validation Boundary | Track Introduced |",
            "| Storage Component | Local Choice | Purpose | Migration/Init Need | Reset/Seed Need | Future Production Candidate |",
            "| Test Area | Required Coverage | Track Introduced | Acceptance Signal | Deferred Coverage |",
            "| Security Domain | Current Status | Deferred Reason | Required Future Approval | Not Allowed In Track 1B |",
            "| Product |",
            "| AffiliateOffer |",
            "| Source |",
            "| CollectionRun |",
            "| Insight |",
            "| Recommendation |",
            "| GET /health | GET |",
            "| GET /version | GET |",
            "| GET /runtime/status | GET |",
            "| POST /products | POST |",
            "| GET /products | GET |",
            "| GET /products/{id} | GET |",
            "| PATCH /products/{id} | PATCH |",
            "| POST /affiliate-offers | POST |",
            "| GET /affiliate-offers | GET |",
            "| POST /collection-runs | POST |",
            "| GET /collection-runs/{id} | GET |",
            "| POST /insights/generate | POST |",
            "| GET /insights | GET |",
            "| SQLite database file | SQLite for local-first MVP |",
            "| schema initialization | SQLite for local-first MVP |",
            "| local seed dataset | Markdown/JSON fixture set |",
            "| local reset procedure | SQLite file replacement |",
            "| service startup smoke |",
            "| product CRUD contract |",
            "| insight generation contract |",
            "| production authentication |",
            "| RBAC enforcement |",
            "| production signing |",
            "| verifier runtime |",
            "| key custody runtime |",
            "| production deployment |",
            "| CI/CD deployment |",
            "| multi-tenant enforcement |",
            "| payment/billing |",
            "| customer production use |",
        ),
        label="matrix token",
    )


def test_track1b_deferred_security_scope_is_documented() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "deferred security and hardening scope",
            "production authentication status: deferred",
            "rbac enforcement status: deferred",
            "production signing status: deferred",
            "verifier runtime status: deferred",
            "key custody runtime status: deferred",
            "track 1b does not approve production promotion",
            "track 1b does not approve production deployment",
        ),
        label="deferred security token",
    )


def test_track1b_recommended_next_step_and_subphase_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "## Recommended Next Step",
            "Complete Track 1B PR readiness",
            "- run focused checks",
            "- run full suite",
            "- confirm clean worktree",
            "- push feature/track1b-backend-api-database-product-slice-plan",
            "- open one PR for Track 1B",
            "- wait for CI green",
            "- squash merge",
            "- sync main",
            "- delete feature branch",
            "## Recommended Next Major Subphase",
            "Track 1C — Local Backend/API Skeleton",
            "Track 1C should implement the local backend/API skeleton for the first usable local product slice. Track 1C should add only local runtime code required for service startup, configuration loading, GET /health, GET /version, and GET /runtime/status. Track 1C should not implement production authentication, RBAC enforcement, production signing, verifier runtime, key custody runtime, production deployment, cloud infrastructure, or production promotion unless explicitly approved in a later track.",
        ),
        label="next-step token",
    )


def test_track1b_state_pointer_docs_reference_track1b() -> None:
    roadmap = _text(ROADMAP)
    project_state = _text(PROJECT_STATE)
    track1a = _text(TRACK1A_DOC)

    _assert_all_tokens(
        roadmap,
        (
            "Track 1B — Backend/API/Database Product Slice Plan",
            "docs/TRACK1B_BACKEND_API_DATABASE_PRODUCT_SLICE_PLAN.md",
            "Track 1B defines the backend/API/database product slice implementation plan for the first usable local product slice.",
        ),
        label="roadmap Track 1B pointer",
    )
    _assert_all_tokens(
        project_state,
        (
            "Track 1B adds the backend/API/database product slice plan documented in",
            "`docs/TRACK1B_BACKEND_API_DATABASE_PRODUCT_SLICE_PLAN.md`.",
            "`track1b_status` is `success`.",
            "`selected_runtime_domain` remains `backend/API/database runtime`.",
            "`implementation_track_status` remains `implementation_track_1_started`.",
            "`product_slice_planning_status` is `defined`.",
        ),
        label="project state Track 1B pointer",
    )
    _assert_all_tokens(
        track1a,
        (
            "Track 1B defines the backend/API/database product slice implementation plan for the first usable local product slice.",
            "Track 1B continues Implementation Track 1 — Backend/API/Database Usable Product Slice.",
            "Track 1B does not implement runtime code.",
            "Track 1B does not add backend/API/database implementation files.",
            "Track 1B does not approve production promotion.",
            "Track 1B does not approve production deployment.",
            "Track 1B preserves the Phase 7D selected-gate manual boundary.",
        ),
        label="track1a Track 1B pointer",
    )


def test_track1b_no_runtime_or_deployment_files_are_introduced() -> None:
    track_matches = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("*")
        if path.is_file()
        and "track1b" in path.name.lower()
        and ".git" not in path.relative_to(REPO_ROOT).parts
        and "__pycache__" not in path.relative_to(REPO_ROOT).parts
    )
    assert track_matches == [
        "codex/tasks/097-track1b-backend-api-database-product-slice-plan.md",
        "docs/TRACK1B_BACKEND_API_DATABASE_PRODUCT_SLICE_PLAN.md",
        "tests/test_track1b_backend_api_database_product_slice_plan.py",
    ]

    deployment_matches = (
        sorted(
            str(path.relative_to(REPO_ROOT))
            for path in (REPO_ROOT / ".github").rglob("*track1b*")
            if path.is_file()
        )
        if (REPO_ROOT / ".github").exists()
        else []
    )
    assert deployment_matches == [], f"unexpected Track 1B deployment files: {deployment_matches}"

    forbidden_files = [
        REPO_ROOT / "scripts/dev/run_track1b.sh",
        REPO_ROOT / "scripts/dev/track1b_backend_api_database.py",
        REPO_ROOT / "app/track1b_backend_api_database.py",
        REPO_ROOT / "src/track1b_backend_api_database.py",
    ]
    for path in forbidden_files:
        assert not path.exists(), f"unexpected Track 1B runtime file: {path}"


def test_track1b_no_auth_rbac_signing_verifier_or_key_custody_runtime_is_introduced() -> None:
    doc_text = _text(DOC)
    _assert_all_tokens(
        doc_text,
        (
            "Production Authentication Status: deferred",
            "RBAC Enforcement Status: deferred",
            "Production Signing Status: deferred",
            "Verifier Runtime Status: deferred",
            "Key Custody Runtime Status: deferred",
        ),
        label="deferred runtime status token",
    )
