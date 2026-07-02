from __future__ import annotations

import hashlib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/051-phase7h-operator-runbook-hardening.md"
RUNBOOK = REPO_ROOT / "docs/PHASE7H_OPERATOR_RUNBOOK.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE7G_DOC = REPO_ROOT / "docs/PHASE7G_OPERATOR_ACCEPTANCE_DEMO_PACK.md"
LIVE_SNAPSHOT = REPO_ROOT / "docs/RELEASE_SNAPSHOT_PHASE7_RUNTIME_LIVE.md"

PROTECTED_HASHES = {
    REPO_ROOT / "scripts/dev/run_phase7d_single_gate_wrapper.sh": "372aef7a133950a24a1de859a1ba0c01486fd2c84bf46ded783105acc4e47b7d",
    REPO_ROOT / "scripts/dev/execute_single_gate_approval.py": "1b1d00817b1ae89c2840f18c9fe3b73f091abec9c900bf0bff83ad6820e9cebb",
    REPO_ROOT / "scripts/dev/run_phase7b_audit_verifier.sh": "2eed4c68f12dff5306fc244c1a42a843d87b3af6150105fa9681593cd678bfa5",
    REPO_ROOT / "scripts/dev/verify_manual_approval_audit.py": "6c959019f458bd4e79ddf23a9e58055f5fbc16e99660496c4451c13783329c3e",
    REPO_ROOT / "scripts/dev/run_phase7g_safe_demo_pack.sh": "be5f5410d4f4e66b61bda8ba0d4c9861b51f2afb8cb8c099b5c1c60ac6630abb",
    REPO_ROOT / "scripts/dev/build_phase7g_operator_acceptance_summary.py": "9dc7b38a355d8c9d9a5e57c43524308567c0ccf8130449b1a895c5281fc042cf",
}

NEW_PHASE7H_FILES = (TASK_FILE, RUNBOOK)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_phase7h_required_files_and_status_tokens_exist() -> None:
    for path in (*NEW_PHASE7H_FILES, Path(__file__)):
        assert path.is_file(), f"missing Phase 7H file: {path}"

    task_text = _text(TASK_FILE)
    runbook_text = _text(RUNBOOK)
    assert "phase7h_status: success" in task_text
    assert "phase7h_status: success" in runbook_text
    assert "phase7d_runtime_readiness: implemented_manual_gate" in task_text
    assert "phase7d_runtime_readiness: implemented_manual_gate" in runbook_text


def test_phase7h_runbook_scope_and_runtime_safety_tokens() -> None:
    low = _text(RUNBOOK).lower()
    for token in (
        "docs/tests/task-only",
        "operator runbook only",
        "no runtime wrapper behavior change",
        "no approval logic change",
        "no primitive execution",
        "no vault read/write",
        "no new mutation path",
        "no backend/api/database/network",
    ):
        assert token in low, f"missing scope token: {token}"


def test_phase7h_runbook_current_runtime_state_tokens() -> None:
    low = _text(RUNBOOK).lower()
    for token in (
        "phase 7d wrapper exists",
        "phase 7g safe demo pack exists",
        "phase7d_runtime_readiness is implemented_manual_gate",
        "runtime is selected-gate-only",
        "runtime is manual-gated",
        "runtime is not approve-all",
        "runtime is not automatic",
        "no next-gate automation",
        "no chain execution",
    ):
        assert token in low, f"missing runtime-state token: {token}"


def test_phase7h_runbook_has_required_checklist_sections() -> None:
    low = _text(RUNBOOK).lower()
    for token in (
        "### pre-execution checklist",
        "### safe execution ceremony",
        "### evidence verification checklist",
        "### approval flag handling policy",
        "### emergency stop procedure",
        "### audit verification procedure",
        "### failure/manual-review procedure",
        "### retry policy",
        "### partial-completion handling",
        "### incident response and escalation",
        "### post-execution recordkeeping",
        "### hard never-do list",
    ):
        assert token in low, f"missing required section: {token}"


def test_phase7h_runbook_specific_safety_assertions() -> None:
    low = _text(RUNBOOK).lower()
    for token in (
        "selected gate is exactly one of promote, decision, finalization",
        "phase 6c verifier output is ready",
        "selected gate plan_ready",
        "emergency stop is inactive",
        "only the matching approval flag is truthy",
        "no unrelated approval flag is truthy",
        "no global approval",
        "no approve-all",
        "no chain or next-gate request",
        "operator must clear approval flags after execution",
        "verifier valid is not approval",
        "do not auto-rerun",
        "do not rollback automatically",
        "do not retry silently",
    ):
        assert token in low, f"missing safety assertion: {token}"


def test_phase7h_task_contract_has_required_sections() -> None:
    low = _text(TASK_FILE).lower()
    headings = (
        "purpose",
        "scope",
        "files",
        "status model",
        "operator runbook objective",
        "pre-execution checklist",
        "safe execution ceremony",
        "evidence verification checklist",
        "approval flag handling policy",
        "emergency stop procedure",
        "audit verification procedure",
        "failure/manual-review procedure",
        "retry policy",
        "partial-completion handling",
        "incident response and escalation",
        "post-execution recordkeeping",
        "hard never-do list",
        "documentation update scope",
        "no-execution/static-safety rules",
        "test strategy",
        "acceptance criteria",
        "verification commands",
        "known limitations",
        "final status target",
    )
    for heading in headings:
        assert f"## {heading}" in low, f"missing task section: {heading}"


def test_phase7h_documentation_regression_tokens() -> None:
    roadmap = _text(ROADMAP)
    project_state = _text(PROJECT_STATE)
    phase7g_doc = _text(PHASE7G_DOC)
    live_snapshot = _text(LIVE_SNAPSHOT)

    assert "Phase 7H" in roadmap
    assert "Operator Runbook Hardening" in roadmap
    assert "Phase 8A Durable Audit Store Design" in roadmap
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in roadmap

    assert "docs/PHASE7H_OPERATOR_RUNBOOK.md" in project_state
    for token in (
        "Current architecture",
        "no database",
        "no FastAPI",
        "no UI",
        "no external APIs",
        "no autopublish",
    ):
        assert token.lower() in project_state.lower(), f"missing project-state token: {token}"
    for token in (
        "operator runbook exists",
        "no new mutation path",
        "phase 7d wrapper behavior unchanged",
    ):
        assert token in project_state.lower(), f"missing project-state Phase 7H token: {token}"

    assert "Phase 7H" in phase7g_doc
    assert "runbook" in phase7g_doc.lower()
    assert "no runtime behavior change" in phase7g_doc.lower()

    assert "Phase 7H" in live_snapshot
    assert "docs/PHASE7H_OPERATOR_RUNBOOK.md" in live_snapshot
    assert "runbook does not change runtime behavior" in live_snapshot.lower()
    assert "no primitive execution is introduced by Phase 7H" in live_snapshot


def test_phase7h_protected_runtime_files_are_unchanged_and_no_new_runtime_script_exists() -> None:
    for path, expected_hash in PROTECTED_HASHES.items():
        assert path.is_file(), f"missing protected file: {path}"
        assert _sha256(path) == expected_hash, f"protected runtime changed: {path}"

    scripts_dir = REPO_ROOT / "scripts/dev"
    assert not any(scripts_dir.glob("*phase7h*")), "Phase 7H must not add runtime scripts"


def test_phase7h_no_new_mutation_command_is_added() -> None:
    low = (_text(TASK_FILE) + "\n" + _text(RUNBOOK)).lower()
    for token in (
        "new runtime command",
        "new mutation path",
        "no primitive execution",
    ):
        assert token in low, f"missing no-mutation token: {token}"


def test_new_phase7h_files_static_safety() -> None:
    banned = (
        "APPROVE_PROMOTE=true",
        "APPROVE_DECISION=true",
        "APPROVE_FINALIZE=true",
        "APPROVE_PROMOTE=1",
        "APPROVE_DECISION=1",
        "APPROVE_FINALIZE=1",
        "export APPROVE_PROMOTE=",
        "export APPROVE_DECISION=",
        "export APPROVE_FINALIZE=",
        "python scripts/dev/promote_product_candidates.py",
        "python scripts/dev/create_decision.py",
        "python scripts/dev/finalize_decision.py",
        "bash scripts/dev/run_phase2g",
        "bash scripts/dev/run_phase2h",
        "bash scripts/dev/run_phase2i",
        "http://",
        "https://",
        "/home/ubuntu/Affiliate-Ai",
        "AWS_SECRET_ACCESS_KEY",
        "BEGIN PRIVATE KEY",
        "OPENAI_API_KEY",
        "curl ",
        "wget ",
        "uvicorn ",
        "fastapi(",
        "sqlite3.connect",
        "requests.",
        "socket.",
    )
    for path in NEW_PHASE7H_FILES:
        text = _text(path)
        for token in banned:
            assert token not in text, f"{path.name} contains forbidden token: {token}"
