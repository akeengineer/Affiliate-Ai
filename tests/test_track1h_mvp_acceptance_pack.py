from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/103-track1h-mvp-acceptance-pack.md"
DOC = REPO_ROOT / "docs/TRACK1H_MVP_ACCEPTANCE_PACK.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
TRACK1G_DOC = REPO_ROOT / "docs/TRACK1G_END_TO_END_DEMO_PACK.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(_text(path).lower().replace("`", "").split())


def _assert_all_tokens(text: str, tokens: tuple[str, ...] | list[str], *, label: str) -> None:
    for token in tokens:
        assert token in text, f"missing {label}: {token}"


def test_track1h_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Track 1H file: {path}"


def test_track1h_required_canonical_wording_exists() -> None:
    for path in (DOC, TASK_FILE):
        text = _text(path)
        _assert_all_tokens(
            text,
            (
                "Track 1H creates the MVP Acceptance Pack for the first usable local product slice.",
                "Track 1H closes Implementation Track 1 — Backend/API/Database Usable Product Slice.",
                "Track 1H accepts the local product slice as usable for local/demo operation only.",
                "Track 1H does not implement runtime code.",
                "Track 1H does not add new API endpoints.",
                "Track 1H does not add UI features.",
                "Track 1H does not approve production promotion.",
                "Track 1H does not approve production deployment.",
                "Track 1H preserves the Phase 7D selected-gate manual boundary.",
                "Selected Runtime Domain: backend/API/database runtime",
                "Implementation Track: Implementation Track 1 — Backend/API/Database Usable Product Slice",
                "Product Goal: first usable local product slice",
                "Runtime Mode: local-only",
                "Storage Runtime: SQLite local-first MVP",
                "Product Core API Status: implemented in Track 1E",
                "Minimal Operator Flow Status: implemented in Track 1F",
                "End-to-End Demo Pack Status: implemented in Track 1G",
                "MVP Acceptance Status: accepted for local/demo operation only",
                "Production Promotion Status: not approved",
                "Production Deployment Status: not approved",
                "Production Authentication Status: deferred",
                "RBAC Enforcement Status: deferred",
                "Production Signing Status: deferred",
                "Verifier Runtime Status: deferred",
                "Key Custody Runtime Status: deferred",
                "Phase 7D Boundary Status: preserved",
            ),
            label=f"canonical wording in {path}",
        )


def test_track1h_required_sections_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "track 1h purpose",
            "relationship to track 1a",
            "relationship to track 1b",
            "relationship to track 1c",
            "relationship to track 1d",
            "relationship to track 1e",
            "relationship to track 1f",
            "relationship to track 1g",
            "mvp acceptance decision",
            "accepted local product slice scope",
            "what works",
            "what does not work yet",
            "local demo evidence",
            "operator flow evidence",
            "api evidence",
            "storage evidence",
            "test evidence",
            "deferred security and hardening scope",
            "deferred production deployment scope",
            "known limitations",
            "production promotion exclusion",
            "production deployment exclusion",
            "phase 7d manual boundary preservation",
            "mvp acceptance matrix",
            "implemented capability matrix",
            "deferred capability matrix",
            "risk and limitation matrix",
            "recommended next step",
            "recommended next major track",
            "acceptance criteria",
        ),
        label="section",
    )


def test_track1h_required_matrices_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "| Acceptance Area | Accepted Status | Evidence | Boundary Signal | Track Source |",
            "| Capability | Implemented Status | Local Surface | Evidence | Track Introduced |",
            "| Deferred Capability | Current Status | Deferred Reason | First Eligible Future Track | Required Approval |",
            "| Risk/Limitation | Current Impact | Mitigation | Required Future Work | Production Boundary |",
            "| local backend/API skeleton |",
            "| SQLite local-first storage |",
            "| Product Core API |",
            "| Product API endpoints |",
            "| AffiliateOffer API endpoints |",
            "| minimal operator page |",
            "| end-to-end demo runner |",
            "| deterministic demo summary |",
            "| Source UI/API |",
            "| CollectionRun workflow API |",
            "| insight generation |",
            "| recommendation runtime |",
            "| production database runtime |",
            "| PostgreSQL/Aurora runtime |",
            "| production authentication |",
            "| RBAC enforcement |",
            "| production signing |",
            "| verifier runtime |",
            "| key custody runtime |",
            "| production frontend deployment |",
            "| production backend deployment |",
            "| cloud infrastructure |",
            "| CI/CD deployment pipeline |",
            "| payment/billing |",
            "| multi-tenant security |",
            "| customer production use |",
        ),
        label="matrix",
    )


def test_track1h_acceptance_decision_and_boundaries_are_documented() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "Track 1H creates the MVP Acceptance Pack",
            "Track 1H closes Implementation Track 1",
            "usable for local/demo operation only",
            "Track 1H does not implement runtime code",
            "Track 1H does not add new API endpoints",
            "Track 1H does not add UI features",
            "Track 1H does not approve production promotion",
            "Track 1H does not approve production deployment",
            "Track 1H preserves the Phase 7D selected-gate manual boundary",
        ),
        label="acceptance boundary",
    )


def test_track1h_references_track1a_through_track1g() -> None:
    text = _text(DOC)
    for track in ("Track 1A", "Track 1B", "Track 1C", "Track 1D", "Track 1E", "Track 1F", "Track 1G"):
        assert track in text, f"missing {track} reference"


def test_track1h_evidence_and_limitations_are_documented() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "what works",
            "what does not work yet",
            "local demo evidence",
            "operator flow evidence",
            "api evidence",
            "storage evidence",
            "test evidence",
            "deferred security and hardening scope",
            "deferred production deployment scope",
            "known limitations",
        ),
        label="evidence and limitation",
    )


def test_track1h_recommended_next_step_and_next_major_track_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "## Recommended Next Step",
            "Complete Track 1H PR readiness",
            "run focused checks",
            "run Track 1A through Track 1H focused chain",
            "run full suite",
            "confirm clean worktree",
            "push feature/track1h-mvp-acceptance-pack",
            "open one PR for Track 1H",
            "wait for CI green",
            "squash merge",
            "sync main",
            "delete feature branch",
            "## Recommended Next Major Track",
            "Implementation Track 2 — Local Product Intelligence Expansion",
            "Implementation Track 2 should expand the accepted local product slice only after Track 1H is merged.",
        ),
        label="recommended next step",
    )


def test_track1h_docs_and_state_pointers_reference_track1h() -> None:
    for path in (ROADMAP, PROJECT_STATE, TRACK1G_DOC):
        text = _text(path)
        assert "Track 1H" in text, f"missing Track 1H reference in {path}"
        assert "MVP Acceptance Pack" in text, f"missing MVP Acceptance Pack reference in {path}"


def test_track1h_no_runtime_files_are_introduced() -> None:
    forbidden = (
        REPO_ROOT / "scripts/dev/track1h_mvp_acceptance_pack.py",
        REPO_ROOT / "scripts/dev/run_track1h_mvp_acceptance_pack.sh",
        REPO_ROOT / "scripts/dev/track1h_runtime_status.py",
        REPO_ROOT / "scripts/dev/track1h_product_api.py",
        REPO_ROOT / "scripts/dev/track1h_operator_page.py",
    )
    for path in forbidden:
        assert not path.exists(), f"unexpected Track 1H runtime file: {path}"


def test_track1h_no_new_api_endpoint_or_ui_files_are_introduced() -> None:
    forbidden = (
        REPO_ROOT / "scripts/dev/track1h_local_backend_api.py",
        REPO_ROOT / "scripts/dev/track1h_endpoints.py",
        REPO_ROOT / "scripts/dev/track1h_api_routes.py",
        REPO_ROOT / "scripts/dev/track1h_ui.py",
        REPO_ROOT / "scripts/dev/track1h_operator_ui.py",
        REPO_ROOT / "docs/TRACK1H_API_ENDPOINTS.md",
    )
    for path in forbidden:
        assert not path.exists(), f"unexpected Track 1H endpoint/UI file: {path}"


def test_track1h_no_deployment_cloud_or_production_security_files_are_introduced() -> None:
    forbidden = (
        REPO_ROOT / "vercel.json",
        REPO_ROOT / "netlify.toml",
        REPO_ROOT / "Dockerfile.track1h",
        REPO_ROOT / "docker-compose.track1h.yml",
        REPO_ROOT / "terraform/track1h.tf",
        REPO_ROOT / "kubernetes/track1h.yaml",
        REPO_ROOT / ".github/workflows/deploy-track1h.yml",
        REPO_ROOT / "scripts/dev/track1h_production_auth.py",
        REPO_ROOT / "scripts/dev/track1h_rbac.py",
        REPO_ROOT / "scripts/dev/track1h_signing.py",
        REPO_ROOT / "scripts/dev/track1h_verifier.py",
        REPO_ROOT / "scripts/dev/track1h_key_custody.py",
    )
    for path in forbidden:
        assert not path.exists(), f"unexpected Track 1H forbidden file: {path}"
