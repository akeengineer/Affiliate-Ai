from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK_FILE = REPO_ROOT / "codex/tasks/050-phase7g-operator-acceptance-demo-pack.md"
DOC_FILE = REPO_ROOT / "docs/PHASE7G_OPERATOR_ACCEPTANCE_DEMO_PACK.md"
RUNNER = REPO_ROOT / "scripts/dev/run_phase7g_safe_demo_pack.sh"
BUILDER = REPO_ROOT / "scripts/dev/build_phase7g_operator_acceptance_summary.py"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
LIVE_SNAPSHOT = REPO_ROOT / "docs/RELEASE_SNAPSHOT_PHASE7_RUNTIME_LIVE.md"
GITIGNORE = REPO_ROOT / ".gitignore"
OUT_DIR = REPO_ROOT / "tmp/phase7g-operator-acceptance"

PROTECTED_HASHES = {
    REPO_ROOT / "scripts/dev/run_phase7d_single_gate_wrapper.sh": "372aef7a133950a24a1de859a1ba0c01486fd2c84bf46ded783105acc4e47b7d",
    REPO_ROOT / "scripts/dev/execute_single_gate_approval.py": "1b1d00817b1ae89c2840f18c9fe3b73f091abec9c900bf0bff83ad6820e9cebb",
    REPO_ROOT / "scripts/dev/run_phase7b_audit_verifier.sh": "2eed4c68f12dff5306fc244c1a42a843d87b3af6150105fa9681593cd678bfa5",
    REPO_ROOT / "scripts/dev/verify_manual_approval_audit.py": "6c959019f458bd4e79ddf23a9e58055f5fbc16e99660496c4451c13783329c3e",
}

NEW_PHASE7G_FILES = (TASK_FILE, DOC_FILE, RUNNER, BUILDER)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _vault_snapshot() -> dict[str, str]:
    vault = REPO_ROOT / "vault"
    if not vault.exists():
        return {}
    return {
        str(path.relative_to(vault)): _sha256(path)
        for path in sorted(vault.rglob("*"))
        if path.is_file()
    }


def _safe_env() -> dict[str, str]:
    env = os.environ.copy()
    for key in (
        "APPROVE_PROMOTE",
        "APPROVE_DECISION",
        "APPROVE_FINALIZE",
        "APPROVE_ALL",
        "GLOBAL_APPROVAL",
        "APPROVE_GLOBAL",
        "ENABLE_GLOBAL_APPROVAL",
        "AFFILIATE_PHASE7D_EMERGENCY_STOP",
    ):
        env.pop(key, None)
    return env


def _run_demo(cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(RUNNER)],
        cwd=cwd,
        capture_output=True,
        text=True,
        env=_safe_env(),
        timeout=60,
    )


def test_required_files_exist_and_status_tokens() -> None:
    for path in (*NEW_PHASE7G_FILES, Path(__file__)):
        assert path.is_file(), f"missing Phase 7G file: {path}"
    assert "phase7g_status: success" in _text(TASK_FILE)
    assert "phase7g_status: success" in _text(DOC_FILE)
    assert "phase7d_runtime_readiness: implemented_manual_gate" in _text(DOC_FILE)
    assert "phase7d_runtime_readiness: implemented_manual_gate" in _text(TASK_FILE)


def test_phase7d_and_phase7b_runtime_files_are_unchanged() -> None:
    for path, expected_hash in PROTECTED_HASHES.items():
        assert _sha256(path) == expected_hash, f"protected runtime changed: {path}"


def test_runner_and_builder_static_runtime_safety() -> None:
    runner = _text(RUNNER)
    builder = _text(BUILDER)
    assert "--execute" not in runner
    for assignment in (
        "APPROVE_PROMOTE=true",
        "APPROVE_DECISION=true",
        "APPROVE_FINALIZE=true",
        "APPROVE_PROMOTE=1",
        "APPROVE_DECISION=1",
        "APPROVE_FINALIZE=1",
    ):
        assert assignment not in runner
    for primitive_form in (
        "python scripts/dev/promote_product_candidates.py",
        "python scripts/dev/create_decision.py",
        "python scripts/dev/finalize_decision.py",
        "bash scripts/dev/run_phase2g",
        "bash scripts/dev/run_phase2h",
        "bash scripts/dev/run_phase2i",
    ):
        assert primitive_form not in runner
        assert primitive_form not in builder
    for token in ("vault/", "urllib", "requests.", "http.client", "socket.", "sqlite3"):
        assert token not in builder


def test_safe_scenario_documentation_and_checklists() -> None:
    low = _text(DOC_FILE).lower()
    for token in (
        "### purpose",
        "### scope",
        "### safe demo scenarios",
        "no-execute / dry-run prevented path",
        "emergency stop prevented path",
        "missing evidence prevented/blocked path",
        "wrong approval flag rejection",
        "approve-all rejection",
        "chain/next-gate rejection",
        "invalid gate rejection",
        "audit artifact presence",
        "### phase 7b verifier handoff",
        "### operator checklist before real execution",
        "### manual review checklist after failure",
        "### what remains out of scope",
    ):
        assert token in low, f"missing Phase 7G documentation token: {token}"

    for token in (
        "confirm selected gate",
        "confirm product_id",
        "confirm report_week",
        "confirm phase 6b packet exists",
        "confirm phase 6c verifier ready",
        "confirm phase 6e plan exists",
        "confirm selected gate plan_ready",
        "confirm emergency stop inactive",
        "confirm operator identity",
        "confirm reason",
        "confirm intent",
        "confirm exact confirmation string",
        "confirm only matching approval flag is truthy",
        "confirm no global approval",
        "confirm no approve-all",
        "confirm no chain or next-gate request",
        "confirm non-production sample first",
        "inspect result audit",
        "inspect intent audit",
        "inspect wrapper exit code",
        "confirm whether primitive was invoked",
        "confirm whether partial completion occurred",
        "do not rerun automatically",
        "do not run next gate",
        "do not rollback automatically",
        "require operator review before retry",
    ):
        assert token in low, f"missing checklist token: {token}"


def test_task_contract_has_all_required_sections() -> None:
    low = _text(TASK_FILE).lower()
    headings = (
        "purpose",
        "scope",
        "files",
        "status model",
        "operator acceptance objective",
        "safe demo scenarios",
        "demo runner behavior",
        "acceptance summary behavior",
        "phase 7d wrapper integration",
        "phase 7b verifier handoff",
        "no-mutation guarantee",
        "operator checklist",
        "failure/manual-review checklist",
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


def test_runner_syntax_compile_mode_and_gitignore() -> None:
    assert stat.S_IMODE(RUNNER.stat().st_mode) == 0o755
    shell_check = subprocess.run(["bash", "-n", str(RUNNER)], capture_output=True, text=True)
    assert shell_check.returncode == 0, shell_check.stderr
    pyc = subprocess.run(
        [sys.executable, "-m", "py_compile", str(BUILDER)],
        capture_output=True,
        text=True,
    )
    assert pyc.returncode == 0, pyc.stderr
    assert "tmp/phase7g-operator-acceptance/" in _text(GITIGNORE)


def test_demo_runs_cross_cwd_and_does_not_mutate_vault(tmp_path: Path) -> None:
    before = _vault_snapshot()
    result = _run_demo(tmp_path)
    after = _vault_snapshot()
    assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    assert before == after
    assert "phase7g_status: success" in result.stdout
    assert (OUT_DIR / "operator-acceptance-summary.json").is_file()
    assert (OUT_DIR / "operator-acceptance-summary.md").is_file()


def test_acceptance_summary_contains_safe_observations() -> None:
    if not (OUT_DIR / "operator-acceptance-summary.json").is_file():
        result = _run_demo(REPO_ROOT)
        assert result.returncode == 0, result.stderr

    summary = json.loads((OUT_DIR / "operator-acceptance-summary.json").read_text(encoding="utf-8"))
    assert summary["phase7g_status"] == "success"
    assert summary["phase7d_runtime_readiness"] == "implemented_manual_gate"
    assert summary["safety_statement"]
    assert summary["operator_checklist"]
    assert summary["manual_review_checklist"]
    assert summary["next_recommended_phase"]

    scenarios = summary["scenarios_executed"]
    assert len(scenarios) >= 9
    ids = {scenario["scenario_id"] for scenario in scenarios}
    assert {
        "no_execute_dry_run",
        "emergency_stop",
        "missing_evidence",
        "wrong_approval_flag",
        "approve_all_text",
        "chain_next_gate",
        "invalid_gate",
        "audit_artifact_generation",
        "phase7b_verifier_handoff",
    }.issubset(ids)
    for scenario in scenarios:
        assert "expected_result" in scenario
        assert isinstance(scenario["observed_exit_code"], int)
        assert scenario["passed"] is True
        assert scenario.get("primitive_success") is not True

    assert summary["audit_artifacts_found"]
    markdown = _text(OUT_DIR / "operator-acceptance-summary.md")
    for token in (
        "phase7g_status: success",
        "phase7d_runtime_readiness: implemented_manual_gate",
        "Safety statement",
        "Operator checklist",
        "Manual review checklist",
    ):
        assert token in markdown


def test_documentation_regression_tokens() -> None:
    roadmap = _text(ROADMAP)
    project_state = _text(PROJECT_STATE)
    live_snapshot = _text(LIVE_SNAPSHOT)
    assert "Phase 7G" in roadmap
    assert "Operator Acceptance / Safe Demo Pack" in roadmap
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in roadmap
    assert "docs/PHASE7G_OPERATOR_ACCEPTANCE_DEMO_PACK.md" in project_state
    for token in (
        "Current architecture",
        "no database",
        "No FastAPI",
        "No UI",
        "no external APIs",
        "no autopublish",
    ):
        assert token.lower() in project_state.lower()
    assert "Phase 7G" in live_snapshot
    assert "safe demo pack does not change runtime behavior" in live_snapshot.lower()
    assert "no primitive execution is introduced by Phase 7G" in live_snapshot


def test_new_phase7g_files_static_safety() -> None:
    banned = (
        "APPROVE_PROMOTE=true",
        "APPROVE_DECISION=true",
        "APPROVE_FINALIZE=true",
        "bash scripts/dev/run_phase2g",
        "bash scripts/dev/run_phase2h",
        "bash scripts/dev/run_phase2i",
        "python scripts/dev/promote_product_candidates.py",
        "python scripts/dev/create_decision.py",
        "python scripts/dev/finalize_decision.py",
        "http://",
        "https://",
        "/home/ubuntu/Affiliate-Ai",
        "AWS_SECRET_ACCESS_KEY",
        "BEGIN PRIVATE KEY",
        "OPENAI_API_KEY",
        "curl ",
        "wget ",
        "FastAPI(",
        "sqlite3.connect",
    )
    for path in NEW_PHASE7G_FILES:
        text = _text(path)
        for token in banned:
            assert token not in text, f"{path.name} contains forbidden token: {token}"
