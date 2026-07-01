from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/049-phase7f-runtime-wrapper-live-snapshot.md"
LIVE_SNAPSHOT = REPO_ROOT / "docs/RELEASE_SNAPSHOT_PHASE7_RUNTIME_LIVE.md"
PHASE7_SNAPSHOT = REPO_ROOT / "docs/RELEASE_SNAPSHOT_PHASE7.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
BLUEPRINT = REPO_ROOT / "docs/PHASE7D_RUNTIME_WRAPPER_IMPLEMENTATION_BLUEPRINT.md"

NEW_FILES = (TASK_FILE, LIVE_SNAPSHOT)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase7f_task_and_live_snapshot_exist() -> None:
    assert TASK_FILE.is_file()
    assert LIVE_SNAPSHOT.is_file()


def test_phase7f_task_status_tokens() -> None:
    text = _text(TASK_FILE)
    assert "phase7f_status: success" in text
    assert "phase7d_runtime_readiness: implemented_manual_gate" in text


def test_live_snapshot_status_tokens() -> None:
    text = _text(LIVE_SNAPSHOT)
    assert "phase7f_status: success" in text
    assert "phase7d_runtime_readiness: implemented_manual_gate" in text


def test_live_snapshot_scope_tokens() -> None:
    low = _text(LIVE_SNAPSHOT).lower()
    for token in (
        "release snapshot only",
        "docs/tests/task-only",
        "no runtime behavior change",
        "no wrapper logic change",
        "no approval logic change",
        "no primitive execution",
        "no vault reads/writes",
        "no backend/api/database/network",
    ):
        assert token in low, f"missing scope token: {token}"


def test_live_snapshot_phase7_completion_matrix() -> None:
    text = _text(LIVE_SNAPSHOT)
    for token in (
        "Phase 7A: Manual Approval Audit Verifier Implementation Plan — complete",
        "Phase 7B: Read-only Audit Verifier Runtime — complete",
        "Phase 7C: Single-gate Manual Approval Wrapper Implementation Plan — complete",
        "Phase 7D-R: High-risk Implementation Readiness Review — complete",
        "Phase 7D-P: Runtime Wrapper Implementation Blueprint — complete",
        "Phase 7E: Runtime Blocked Release Snapshot — complete",
        "Phase 7D: Single-gate Runtime Wrapper — complete",
        "Phase 7F: Runtime Wrapper Live State Report — complete",
    ):
        assert token in text, f"missing completion token: {token}"


def test_live_snapshot_runtime_readiness_state() -> None:
    low = _text(LIVE_SNAPSHOT).lower()
    for token in (
        "runtime readiness state",
        "wrapper exists",
        "runtime is not approve-all",
        "runtime is not automatic",
        "every mutation still requires selected gate",
        "every mutation still requires matching approval flag semantics",
        "every mutation still requires operator confirmation",
        "evidence preconditions must pass",
        "emergency stop must be inactive",
        "audit must be generated",
        "no next-gate automation exists",
        "no chain execution exists",
    ):
        assert token in low, f"missing readiness token: {token}"


def test_live_snapshot_runtime_command_inventory() -> None:
    text = _text(LIVE_SNAPSHOT)
    for token in (
        "scripts/dev/run_phase7d_single_gate_wrapper.sh",
        "scripts/dev/execute_single_gate_approval.py",
        "scripts/dev/run_phase7b_audit_verifier.sh",
        "scripts/dev/verify_manual_approval_audit.py",
    ):
        assert token in text, f"missing inventory token: {token}"


def test_live_snapshot_current_capabilities() -> None:
    low = _text(LIVE_SNAPSHOT).lower()
    for token in (
        "what the system can do now",
        "build phase 6b approval review packets",
        "verify phase 6c approval review packets",
        "build phase 6e dry-run approval execution plans",
        "validate phase 7b audit artifacts",
        "execute a single selected gate only when all phase 7d wrapper checks pass",
        "write phase 7d wrapper audit artifacts under tmp",
        "keep phase 7b verifier read-only",
        "prevent approve-all, global approval, multi-gate execution, next-gate automation, and chain execution",
    ):
        assert token in low, f"missing capability token: {token}"


def test_live_snapshot_safety_guarantees() -> None:
    low = _text(LIVE_SNAPSHOT).lower()
    for token in (
        "phase 7d safety guarantees",
        "selected-gate-only",
        "explicit primitive allowlist",
        "no dynamic primitive command construction",
        "no shell eval",
        "matching approval flag semantics",
        "operator confirmation",
        "emergency stop",
        "evidence-derived decision gate",
        "safe vault-read supplements only",
        "no direct vault write by wrapper",
        "vault mutation only through selected primitive after all checks pass",
        "audit before/after behavior",
        "phase 7b-compatible audit artifacts",
        "no auto-run phase 7b as approval",
        "no next-gate automation",
        "no chain execution",
    ):
        assert token in low, f"missing safety token: {token}"


def test_live_snapshot_safe_demo_posture_and_out_of_scope() -> None:
    low = _text(LIVE_SNAPSHOT).lower()
    for token in (
        "safe demo posture",
        "use no-execute/dry-run/prevented paths first",
        "verify audit artifacts with phase 7b separately",
        "never demo approve-all",
        "never demo chain execution",
        "never use production vault data",
        "use tmp fixtures or sample data",
        "emergency stop should be tested before any live mutation demo",
        "what remains out of scope",
        "no backend/api/database",
        "no marketplace connector",
        "no autopublish",
        "no campaign launch",
        "no production deployment",
        "no durable audit store",
        "no operator authentication implementation",
        "no scheduled approval automation",
        "no multi-gate workflow",
        "no automatic finalization",
        "no external api integration",
        "phase 7g: operator acceptance / safe demo pack",
    ):
        assert token in low, f"missing token: {token}"


def test_phase7_snapshot_and_supporting_docs_reference_phase7f() -> None:
    snapshot = _text(PHASE7_SNAPSHOT)
    roadmap = _text(ROADMAP)
    project_state = _text(PROJECT_STATE)
    blueprint = _text(BLUEPRINT)

    assert "Phase 7F" in snapshot
    assert "RELEASE_SNAPSHOT_PHASE7_RUNTIME_LIVE.md" in snapshot
    assert "Phase 7F" in roadmap
    assert "RELEASE_SNAPSHOT_PHASE7_RUNTIME_LIVE.md" in roadmap
    assert "Phase 7F" in project_state
    assert "RELEASE_SNAPSHOT_PHASE7_RUNTIME_LIVE.md" in project_state
    assert "Phase 7F" in blueprint
    assert "RELEASE_SNAPSHOT_PHASE7_RUNTIME_LIVE.md" in blueprint


def test_new_phase7f_files_no_execution_forms() -> None:
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


def test_new_phase7f_files_static_safety() -> None:
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
