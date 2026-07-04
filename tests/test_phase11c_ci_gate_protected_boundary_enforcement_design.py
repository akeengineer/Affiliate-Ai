"""Phase 11C CI Gate and Protected Boundary Enforcement Design — docs-contract tests."""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

TASK = REPO_ROOT / "codex/tasks/082-phase11c-ci-gate-protected-boundary-enforcement-design.md"
DOC = REPO_ROOT / "docs/PHASE11C_CI_GATE_PROTECTED_BOUNDARY_ENFORCEMENT_DESIGN.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE11B = REPO_ROOT / "docs/PHASE11B_THREAT_MODEL_SECURITY_CONTROL_MAPPING.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _low(path: Path) -> str:
    return _text(path).lower()


# ── 1. Files exist ────────────────────────────────────────────────────────────

def test_task_file_exists() -> None:
    assert TASK.is_file()


def test_design_doc_exists() -> None:
    assert DOC.is_file()


def test_test_file_exists() -> None:
    assert Path(__file__).is_file()


# ── 2. Required canonical wording ─────────────────────────────────────────────

CANONICAL = (
    "phase 11c defines ci gate and protected boundary enforcement design",
    "phase 11c does not implement ci/cd runtime",
    "phase 11c does not implement production runtime",
    "phase 11c does not approve production promotion",
    "phase 11b defines threat model and security control mapping",
    "phase 11a defines production boundary and hardening readiness",
    "local-only prototypes remain local-only until governed promotion is explicitly approved",
    "rbac advisory context remains not enforcement",
    "approval remains the phase 7d selected-gate manual boundary",
    "phase 10 acceptance remains readiness, not approval",
)


def test_canonical_wording_in_doc() -> None:
    low = _low(DOC)
    for phrase in CANONICAL:
        assert phrase in low, f"missing canonical phrase: {phrase}"


def test_canonical_wording_in_task() -> None:
    low = _low(TASK)
    for phrase in (
        "phase 11c defines ci gate and protected boundary enforcement design",
        "phase 11c does not implement ci/cd runtime",
        "phase 11c does not implement production runtime",
        "phase 11c does not approve production promotion",
        "approval remains the phase 7d selected-gate manual boundary",
    ):
        assert phrase in low, f"missing in task: {phrase}"


# ── 3. Required sections ──────────────────────────────────────────────────────

REQUIRED_SECTIONS = (
    "phase 11c purpose",
    "relationship to phase 11a and phase 11b",
    "ci gate design scope",
    "protected boundary design scope",
    "gate categories",
    "required gate evidence",
    "boundary enforcement design",
    "promotion-blocking criteria",
    "failure handling model",
    "required future ci gates",
    "required future protected boundary checks",
    "gate-to-threat mapping",
    "gate-to-control mapping",
    "manual approval boundary preservation",
    "local-only prototype protection",
    "production candidate readiness criteria",
    "non-goals and forbidden implementations",
    "acceptance criteria",
    "safe demo scenarios",
    "operator checklist",
    "recommended next step",
    "recommended next major subphase",
)


def test_required_sections_exist() -> None:
    low = _low(DOC)
    for section in REQUIRED_SECTIONS:
        assert section in low, f"missing section: {section}"


# ── 4. Gate categories documented ─────────────────────────────────────────────

GATE_CATEGORIES = (
    "full test suite gate",
    "focused regression gate",
    "secret scanning gate",
    "protected-hash gate",
    "permission/index gate",
    "hardcoded path gate",
    "docs/state pointer consistency gate",
    "boundary wording gate",
    "no-runtime-added gate",
    "no-production-capability-added gate",
    "dependency/supply-chain gate",
    "artifact integrity gate",
    "approval-boundary drift gate",
    "local-only prototype containment gate",
    "promotion-readiness evidence gate",
)


def test_gate_categories_documented() -> None:
    low = _low(DOC)
    for cat in GATE_CATEGORIES:
        assert cat in low, f"missing gate category: {cat}"


# ── 5. Protected boundary checks documented ───────────────────────────────────

PROTECTED_CHECKS = (
    "phase 7d manual approval boundary preservation",
    "phase 10 local advisory prototype boundary preservation",
    "phase 11a production boundary readiness preservation",
    "phase 11b threat/control mapping preservation",
    "no auth runtime introduced without approval",
    "no rbac enforcement introduced without approval",
    "no production policy engine introduced without approval",
    "no backend/api/database introduced without approval",
    "no key/cert/secrets committed",
    "no signing/verifier runtime introduced without approval",
    "no vault write introduced without approval",
    "no primitive execution introduced outside selected-gate boundary",
    "no export mutation or re-signing",
    "no production deployment path introduced",
    "no ci/cd deployment pipeline introduced",
)


def test_protected_boundary_checks_documented() -> None:
    low = _low(DOC)
    for check in PROTECTED_CHECKS:
        assert check in low, f"missing protected check: {check}"


# ── 6. Gate-to-threat mapping exists ──────────────────────────────────────────

def test_gate_to_threat_mapping_exists() -> None:
    text = _text(DOC)
    assert "Gate-to-Threat Mapping" in text
    # Table should have key threats from Phase 11B
    low = text.lower()
    for threat in (
        "unauthorized operator action",
        "forged approval event",
        "artifact tampering",
        "secret leakage",
        "key misuse",
        "policy bypass",
        "path traversal",
        "local-only prototype promoted without approval",
    ):
        assert threat in low, f"missing threat in mapping: {threat}"


# ── 7. Gate-to-control mapping exists ─────────────────────────────────────────

def test_gate_to_control_mapping_exists() -> None:
    text = _text(DOC)
    assert "Gate-to-Control Mapping" in text
    low = text.lower()
    assert "failed protected boundary gates must block production promotion readiness" in low


# ── 8. Failure handling model documented ──────────────────────────────────────

FAILURE_MODEL = (
    "fail-closed gate behavior",
    "no silent pass",
    "no warning-only bypass for protected boundaries",
    "explicit operator review requirement",
    "evidence capture requirement",
    "known-failure classification",
    "retry criteria",
    "escalation criteria",
)


def test_failure_handling_model_documented() -> None:
    low = _low(DOC)
    for item in FAILURE_MODEL:
        assert item in low, f"missing failure model item: {item}"


# ── 9. Promotion-blocking criteria documented ─────────────────────────────────

def test_promotion_blocking_criteria_documented() -> None:
    low = _low(DOC)
    assert "promotion-blocking criteria" in low
    assert "block" in low
    assert "missing" in low or "fail" in low


# ── 10. Non-goals documented ──────────────────────────────────────────────────

NON_GOALS = (
    "github actions workflow",
    "ci/cd deployment pipeline",
    "deployment manifest",
    "authentication runtime",
    "rbac enforcement",
    "production policy engine",
    "backend/api/database",
    "vault write",
    "primitive execution",
)


def test_non_goals_documented() -> None:
    low = _low(DOC)
    for ng in NON_GOALS:
        assert ng in low, f"missing non-goal: {ng}"


# ── 11. Approval language preserved ──────────────────────────────────────────

def test_approval_boundary_preserved() -> None:
    low = _low(DOC)
    assert "approval remains the phase 7d selected-gate manual boundary" in low
    assert "phase 10 acceptance remains readiness, not approval" in low


def test_phase11a_remains_boundary_not_runtime() -> None:
    low = _low(DOC)
    assert "phase 11a defines production boundary and hardening readiness" in low


def test_phase11b_remains_mapping_not_runtime() -> None:
    low = _low(DOC)
    assert "phase 11b defines threat model and security control mapping" in low


def test_phase11c_does_not_implement_runtime() -> None:
    low = _low(DOC)
    assert "phase 11c does not implement ci/cd runtime" in low
    assert "phase 11c does not implement production runtime" in low


# ── 12. Docs/state pointers reference Phase 11C ───────────────────────────────

def test_roadmap_references_phase11c() -> None:
    assert "phase 11c" in _low(ROADMAP) or "11c" in _low(ROADMAP)


def test_project_state_references_phase11c() -> None:
    assert "phase 11c" in _low(PROJECT_STATE) or "11c" in _low(PROJECT_STATE)


def test_phase11b_points_to_phase11c() -> None:
    assert "phase 11c" in _low(PHASE11B) or "11c" in _low(PHASE11B)


# ── 13. No runtime files introduced ──────────────────────────────────────────

def test_no_phase11c_runner_introduced() -> None:
    scripts = REPO_ROOT / "scripts/dev"
    assert not any(scripts.glob("*phase11c*")), "Phase 11C must not add runtime scripts"
    assert not any(scripts.glob("*run_phase11c*")), "Phase 11C must not add a runner"


def test_no_github_actions_workflow_introduced() -> None:
    workflows = REPO_ROOT / ".github/workflows"
    for wf in workflows.glob("*.yml"):
        assert "phase11c" not in wf.name.lower(), f"Phase 11C workflow found: {wf.name}"


def test_no_deployment_manifest_introduced() -> None:
    for name in ("Dockerfile", "docker-compose.yml", "k8s", "terraform", "cdk.json"):
        assert not (REPO_ROOT / name).exists(), f"deployment manifest found: {name}"
