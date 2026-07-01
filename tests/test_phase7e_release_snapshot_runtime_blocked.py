from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/047-phase7e-release-snapshot-runtime-blocked.md"
SNAPSHOT = REPO_ROOT / "docs/RELEASE_SNAPSHOT_PHASE7.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
BLUEPRINT = REPO_ROOT / "docs/PHASE7D_RUNTIME_WRAPPER_IMPLEMENTATION_BLUEPRINT.md"
RELEASE_SNAPSHOT_PHASE6 = REPO_ROOT / "docs/RELEASE_SNAPSHOT_PHASE6.md"

NEW_FILES = (TASK_FILE, SNAPSHOT)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_task_and_snapshot_exist() -> None:
    assert TASK_FILE.is_file()
    assert SNAPSHOT.is_file()


def test_task_contains_success_status() -> None:
    assert "phase7e_status: success" in _text(TASK_FILE)


def test_snapshot_status_model() -> None:
    text = _text(SNAPSHOT)
    assert "phase7e_status: success" in text
    assert "phase7d_runtime_readiness: blocked" in text


def test_snapshot_scope_is_release_snapshot_only() -> None:
    low = _text(SNAPSHOT).lower()
    assert "docs/tests/task-only" in low or "release snapshot only" in low


def test_no_runtime_wrapper_scripts_added() -> None:
    assert not (REPO_ROOT / "scripts/dev/run_phase7d_single_gate_wrapper.sh").exists()
    assert not (REPO_ROOT / "scripts/dev/run_manual_approval_wrapper.sh").exists()
    assert not (REPO_ROOT / "scripts/dev/execute_single_gate_approval.py").exists()


def test_snapshot_includes_phase7_completion_matrix() -> None:
    text = _text(SNAPSHOT)
    for token in (
        "Phase 7A",
        "Phase 7B",
        "Phase 7C",
        "Phase 7D-R",
        "Phase 7D-P",
        "Phase 7E",
        "Phase 7D Runtime Implementation",
    ):
        assert token in text, f"missing phase token: {token}"


def test_snapshot_marks_all_completed_and_runtime_future_blocked() -> None:
    low = _text(SNAPSHOT).lower()
    for token in (
        "manual approval audit verifier implementation plan — complete",
        "read-only audit verifier runtime — complete",
        "single-gate manual approval wrapper implementation plan — complete",
        "high-risk implementation readiness review — complete",
        "runtime wrapper implementation blueprint — complete",
        "release snapshot / runtime blocked state report — complete",
    ):
        assert token in low, f"missing completion token: {token}"
    assert "blocked/future" in low


def test_snapshot_defines_current_capabilities() -> None:
    low = _text(SNAPSHOT).lower()
    for token in (
        "what the system can do now",
        "build approval review packets via phase 6b",
        "verify approval review packets via phase 6c",
        "build dry-run approval execution plans via phase 6e",
        "validate manual approval audit artifacts via phase 7b",
        "document and test the future single-gate wrapper boundary",
        "document and test the high-risk readiness review",
        "document and test the finalized implementation blueprint",
        "maintain runtime readiness as blocked",
    ):
        assert token in low, f"missing capability token: {token}"


def test_snapshot_defines_runtime_blocked_state() -> None:
    low = _text(SNAPSHOT).lower()
    for token in (
        "what remains blocked",
        "no runtime approval wrapper exists yet",
        "no phase 7d runtime command exists yet",
        "no approval mutation is introduced",
        "no primitive execution is introduced",
        "no vault write is introduced by phase 7 wrapper",
        "no durable audit store exists yet",
        "no operator authentication implementation exists yet",
        "no backend/api/database exists",
        "no marketplace connector exists",
        "no autopublish exists",
        "no production deployment exists",
    ):
        assert token in low, f"missing blocked-state token: {token}"


def test_snapshot_explains_why_runtime_remains_blocked() -> None:
    low = _text(SNAPSHOT).lower()
    for token in (
        "why phase 7d runtime remains blocked",
        "first future phase that may call approval primitives",
        "may mutate vault state",
        "unintended promotion, decision creation, or finalization",
        "runtime must remain blocked until explicit high-risk approval is given",
        "does not authorize runtime implementation",
    ):
        assert token in low, f"missing blocked rationale token: {token}"


def test_snapshot_defines_unlock_conditions() -> None:
    low = _text(SNAPSHOT).lower()
    for token in (
        "conditions before phase 7d can unlock",
        "user explicitly approves phase 7d runtime implementation",
        "approval phrase must be specific to phase 7d",
        "phase7d_runtime_readiness must be intentionally changed in a future pr",
        "runtime wrapper files must be added intentionally",
        "selected-gate-only enforcement must be implemented",
        "explicit primitive allowlist must be implemented",
        "approval flag semantics must be implemented",
        "emergency stop / dry-run / operator confirmation decision must be implemented",
        "audit-before/after behavior must be implemented",
        "phase 7b audit verifier compatibility must be tested",
        "no primitive execution on failed precondition must be tested",
        "no vault write on failed precondition must be tested",
        "no next-gate / no chain behavior must be tested",
        "full suite must pass",
    ):
        assert token in low, f"missing unlock condition token: {token}"


def test_snapshot_requires_explicit_phase_specific_approval() -> None:
    text = _text(SNAPSHOT)
    low = text.lower()
    assert "explicit approval requirement" in low
    assert "must not start from a vague instruction" in low
    assert "approve phase 7d runtime implementation" in low
    assert "phase-specific" in low
    assert "not approve-all" in low


def test_snapshot_includes_runtime_safety_contract() -> None:
    low = _text(SNAPSHOT).lower()
    for token in (
        "runtime safety contract",
        "phase 7b remains read-only",
        "phase 7d runtime wrapper does not exist yet",
        "phase 7d runtime readiness remains blocked",
        "phase 2g/2h/2i primitives remain unchanged",
        "at most one primitive per invocation",
        "never infer approval",
        "never run next gate automatically",
        "never chain execution",
        "never use global approval or approve-all",
    ):
        assert token in low, f"missing runtime safety token: {token}"


def test_snapshot_includes_files_and_docs_inventory() -> None:
    text = _text(SNAPSHOT)
    for token in (
        "docs/MANUAL_APPROVAL_AUDIT_VERIFIER_IMPLEMENTATION_PLAN.md",
        "docs/MANUAL_APPROVAL_AUDIT_VERIFIER_BOUNDARY.md",
        "scripts/dev/verify_manual_approval_audit.py",
        "scripts/dev/run_phase7b_audit_verifier.sh",
        "docs/SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_IMPLEMENTATION_PLAN.md",
        "docs/HIGH_RISK_SINGLE_GATE_WRAPPER_READINESS_REVIEW.md",
        "docs/PHASE7D_RUNTIME_WRAPPER_IMPLEMENTATION_BLUEPRINT.md",
        "docs/RELEASE_SNAPSHOT_PHASE7.md",
    ):
        assert token in text, f"missing inventory token: {token}"


def test_snapshot_known_limitations() -> None:
    low = _text(SNAPSHOT).lower()
    for token in (
        "known limitations",
        "no runtime wrapper yet",
        "no approval mutation yet",
        "no phase 7d command yet",
        "no durable audit store yet",
        "no auth/operator identity implementation",
        "no backend/api/database",
        "no marketplace connector",
        "no autopublish",
        "no production deployment",
        "phase 7d runtime readiness remains blocked",
    ):
        assert token in low, f"missing limitation token: {token}"


def test_docs_updates_reference_phase7e() -> None:
    roadmap = _text(ROADMAP)
    project_state = _text(PROJECT_STATE)
    blueprint = _text(BLUEPRINT)
    release6 = _text(RELEASE_SNAPSHOT_PHASE6)

    assert "Phase 7E" in roadmap
    assert "blocked" in roadmap.lower()
    assert "docs/RELEASE_SNAPSHOT_PHASE7.md" in project_state
    assert "Phase 7E" in blueprint
    assert "RELEASE_SNAPSHOT_PHASE7.md" in blueprint
    assert "Phase 7E" in release6
    assert "RELEASE_SNAPSHOT_PHASE7.md" in release6


def test_roadmap_regression_tokens_preserved() -> None:
    text = _text(ROADMAP)
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in text, f"ROADMAP dropped token: {token}"


def test_project_state_regression_tokens_preserved() -> None:
    text = _text(PROJECT_STATE)
    for token in (
        "Current architecture",
        "no database",
        "no FastAPI",
        "no UI",
        "no external APIs",
        "no autopublish",
    ):
        assert token in text, f"PROJECT_STATE dropped token: {token}"


def test_new_phase7e_files_no_execution_forms() -> None:
    banned = [
        "APPROVE_PROMOTE=true",
        "APPROVE_DECISION=true",
        "APPROVE_FINALIZE=true",
        "bash scripts/dev/run_phase2g",
        "bash scripts/dev/run_phase2h",
        "bash scripts/dev/run_phase2i",
        "python scripts/dev/promote_product_candidates.py",
        "python scripts/dev/create_decision.py",
        "python scripts/dev/finalize_decision.py",
    ]
    for path in NEW_FILES:
        text = _text(path)
        for token in banned:
            assert token not in text, f"{path.name} contains execution form: {token}"


def test_new_phase7e_files_static_safety() -> None:
    banned = (
        "http://",
        "https://",
        "/home/ubuntu/Affiliate-Ai",
        "AWS_SECRET_ACCESS_KEY",
        "BEGIN PRIVATE KEY",
        "OPENAI_API_KEY",
    )
    for path in NEW_FILES:
        text = _text(path)
        for token in banned:
            assert token not in text, f"{path.name} contains forbidden token: {token}"
