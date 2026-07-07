from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/096-track1a-backend-api-database-runtime-selection-record.md"
DOC = REPO_ROOT / "docs/TRACK1A_BACKEND_API_DATABASE_RUNTIME_SELECTION_RECORD.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE14_DOC = REPO_ROOT / "docs/PHASE14_SELECTED_RUNTIME_DOMAIN_IMPLEMENTATION_PLAN_BLOCKED.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(_text(path).lower().replace("`", "").split())


def _assert_all_tokens(text: str, tokens: tuple[str, ...] | list[str], *, label: str) -> None:
    for token in tokens:
        assert token in text, f"missing {label}: {token}"


def test_track1a_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Track 1A file: {path}"


def test_track1a_required_canonical_wording_exists() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "Track 1A selects backend/API/database runtime as the first runtime domain for a usable product slice.",
            "Track 1A exits the governance-only loop and starts Implementation Track 1.",
            "Track 1A does not implement runtime code.",
            "Track 1A does not approve production promotion.",
            "Track 1A does not approve production deployment.",
            "Track 1A preserves the Phase 7D selected-gate manual boundary.",
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
            "Phase 14 documents the blocked selected runtime domain implementation planning state.",
            "Phase 13 defines the explicit implementation approval record and runtime domain selection process.",
            "Phase 12G is the Phase 12 acceptance/readiness pack.",
        ),
        label="canonical wording",
    )


def test_track1a_task_file_preserves_core_boundary_wording() -> None:
    text = _text(TASK_FILE)
    _assert_all_tokens(
        text,
        (
            "track1a_status: success",
            "Track 1A selects backend/API/database runtime as the first runtime domain for a usable product slice.",
            "Track 1A exits the governance-only loop and starts Implementation Track 1.",
            "Track 1A does not implement runtime code.",
            "Track 1A does not approve production promotion.",
            "Track 1A does not approve production deployment.",
            "Track 1A preserves the Phase 7D selected-gate manual boundary.",
        ),
        label="task token",
    )


def test_track1a_required_sections_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "track 1a purpose",
            "runtime domain selection decision",
            "why backend/api/database runtime first",
            "relationship to phase 14",
            "relationship to phase 13",
            "relationship to phase 12g",
            "implementation track 1 scope",
            "local product slice boundary",
            "deferred security and hardening scope",
            "production promotion exclusion",
            "production deployment exclusion",
            "phase 7d manual boundary preservation",
            "selected runtime domain matrix",
            "deferred runtime domain matrix",
            "product slice roadmap",
            "implementation guardrails",
            "non-goals and forbidden implementations",
            "acceptance criteria",
            "safe demo scenarios",
            "operator checklist",
            "recommended next step",
            "recommended next major subphase",
        ),
        label="section",
    )


def test_track1a_selection_transition_and_boundary_language_exists() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "track 1a selects backend/api/database runtime as the first runtime domain for a usable product slice",
            "track 1a exits the governance-only loop and starts implementation track 1",
            "track 1a does not implement runtime code",
            "track 1a does not approve production promotion",
            "track 1a does not approve production deployment",
            "track 1a preserves the phase 7d selected-gate manual boundary",
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
        label="selection and boundary token",
    )


def test_track1a_phase_relationships_are_documented() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 14 documents the blocked selected runtime domain implementation planning state",
            "phase 13 defines the explicit implementation approval record and runtime domain selection process",
            "phase 12g is the phase 12 acceptance/readiness pack",
        ),
        label="phase relationship token",
    )


def test_track1a_required_matrices_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "| Runtime Domain | Selection Status | Product Reason | Implementation Track | Production Promotion Status | Boundary Status |",
            "| Deferred Domain | Deferred Reason | Current Status | Required Future Approval | Production Promotion Status | Boundary Status |",
            "| Track | Purpose | Runtime Status | Expected Output | Blocking Condition | Acceptance Signal |",
            "| backend/API/database runtime | selected |",
            "| authentication runtime |",
            "| RBAC enforcement runtime |",
            "| production signing runtime |",
            "| verifier runtime |",
            "| key custody runtime |",
            "| production policy engine runtime |",
            "| deployment runtime |",
            "| CI/CD runtime |",
            "| observability runtime |",
            "| audit storage runtime |",
            "| backup/restore runtime |",
            "| Track 1A | Runtime domain selection record |",
            "| Track 1B | Backend/API/database product slice plan |",
            "| Track 1C | Local backend/API skeleton |",
            "| Track 1D | Database/storage runtime |",
            "| Track 1E | Product core API |",
            "| Track 1F | Minimal usable UI/operator flow |",
            "| Track 1G | End-to-end demo pack |",
            "| Track 1H | MVP acceptance pack |",
        ),
        label="matrix token",
    )


def test_track1a_deferred_security_scope_is_documented() -> None:
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
            "track 1a does not approve production promotion",
            "track 1a does not approve production deployment",
        ),
        label="deferred security token",
    )


def test_track1a_recommended_next_step_and_subphase_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "## Recommended Next Step",
            "Complete Track 1A PR readiness",
            "- run focused checks",
            "- run full suite",
            "- confirm clean worktree",
            "- push feature/track1a-backend-api-database-runtime-selection-record",
            "- open one PR for Track 1A",
            "- wait for CI green",
            "- squash merge",
            "- sync main",
            "- delete feature branch",
            "## Recommended Next Major Subphase",
            "Track 1B — Backend/API/Database Product Slice Plan",
            "Track 1B should define the backend/API/database product slice implementation plan for the first usable local product slice. Track 1B should identify the local backend service, database/storage approach, product entities, API endpoints, validation rules, tests, local run commands, and demo acceptance flow. Track 1B should not implement production authentication, RBAC enforcement, production signing, verifier runtime, key custody runtime, production deployment, or production promotion unless explicitly approved in a later track.",
        ),
        label="next-step token",
    )


def test_track1a_state_pointer_docs_reference_track1a() -> None:
    roadmap = _text(ROADMAP)
    project_state = _text(PROJECT_STATE)
    phase14 = _text(PHASE14_DOC)

    _assert_all_tokens(
        roadmap,
        (
            "Track 1A — Backend/API/Database Runtime Selection Record",
            "docs/TRACK1A_BACKEND_API_DATABASE_RUNTIME_SELECTION_RECORD.md",
            "Track 1A exits the governance-only loop and starts Implementation Track 1.",
        ),
        label="roadmap Track 1A pointer",
    )
    _assert_all_tokens(
        project_state,
        (
            "Track 1A adds the backend/API/database runtime selection record documented in",
            "`docs/TRACK1A_BACKEND_API_DATABASE_RUNTIME_SELECTION_RECORD.md`.",
            "`track1a_status` is `success`.",
            "`selected_runtime_domain` is `backend/API/database runtime`.",
            "`implementation_track_status` is `implementation_track_1_started`.",
        ),
        label="project state Track 1A pointer",
    )
    _assert_all_tokens(
        phase14,
        (
            "Track 1A selects backend/API/database runtime as the first runtime domain for a usable product slice.",
            "Track 1A exits the governance-only loop and starts Implementation Track 1.",
            "Track 1A does not implement runtime code.",
            "Track 1A does not approve production promotion.",
            "Track 1A does not approve production deployment.",
            "Track 1A preserves the Phase 7D selected-gate manual boundary.",
        ),
        label="phase14 Track 1A pointer",
    )


def test_track1a_no_runtime_or_deployment_files_are_introduced() -> None:
    runtime_matches = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("*track1a*")
        if path.is_file()
        and ".git" not in path.relative_to(REPO_ROOT).parts
        and "__pycache__" not in path.relative_to(REPO_ROOT).parts
    )
    assert runtime_matches == [
        "codex/tasks/096-track1a-backend-api-database-runtime-selection-record.md",
        "tests/test_track1a_backend_api_database_runtime_selection_record.py",
    ]

    deployment_matches = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in (REPO_ROOT / ".github").rglob("*track1a*")
        if path.is_file()
    ) if (REPO_ROOT / ".github").exists() else []
    assert deployment_matches == [], f"unexpected Track 1A deployment files: {deployment_matches}"

    forbidden_files = [
        REPO_ROOT / "scripts/dev/run_track1a.sh",
        REPO_ROOT / "scripts/dev/track1a_backend_api_database.py",
        REPO_ROOT / "app/track1a_backend_api_database.py",
        REPO_ROOT / "src/track1a_backend_api_database.py",
    ]
    for path in forbidden_files:
        assert not path.exists(), f"unexpected Track 1A runtime file: {path}"


def test_track1a_no_auth_rbac_signing_verifier_or_key_custody_runtime_is_introduced() -> None:
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
