from __future__ import annotations

import glob
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/042-phase7a-audit-verifier-implementation-plan.md"
PLAN = REPO_ROOT / "docs/MANUAL_APPROVAL_AUDIT_VERIFIER_IMPLEMENTATION_PLAN.md"
BOUNDARY = REPO_ROOT / "docs/MANUAL_APPROVAL_AUDIT_VERIFIER_BOUNDARY.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
RELEASE_SNAPSHOT = REPO_ROOT / "docs/RELEASE_SNAPSHOT_PHASE6.md"

NEW_FILES = (PLAN, TASK_FILE)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ── 1-2. existence + final status ─────────────────────────────────────────────

def test_task_and_plan_exist() -> None:
    assert TASK_FILE.is_file()
    assert PLAN.is_file()


def test_task_final_status() -> None:
    assert "phase7a_status: success" in _text(TASK_FILE)


# ── 3. scope is docs/tests/task-only ──────────────────────────────────────────

def test_plan_scope_is_docs_only() -> None:
    low = _text(PLAN).lower()
    assert "docs/tests/task-only" in low or "implementation plan only" in low


# ── 4-5. no runtime script / verifier / wrapper added ─────────────────────────

def test_no_phase7a_runtime_script() -> None:
    assert glob.glob(str(REPO_ROOT / "scripts/dev/*phase7a*")) == []


def test_runtime_verifier_and_wrapper_are_phase7b_scope() -> None:
    # Phase 7A is plan-only; the runtime verifier/wrapper are Phase 7B artifacts.
    # Before Phase 7B these did not exist; Phase 7B implements them. Either state
    # is consistent with Phase 7A remaining docs/tests/task-only.
    verifier = REPO_ROOT / "scripts/dev/verify_manual_approval_audit.py"
    wrapper = REPO_ROOT / "scripts/dev/run_phase7b_audit_verifier.sh"
    assert not glob.glob(str(REPO_ROOT / "scripts/dev/*phase7a*"))
    assert verifier.exists() == wrapper.exists()


# ── 6. no runtime command in Phase 7A ─────────────────────────────────────────

def test_plan_states_no_runtime_command() -> None:
    low = _text(PLAN).lower()
    assert "no runtime command exists in phase 7a" in low


# ── 7. future verifier objective ──────────────────────────────────────────────

def test_plan_defines_objective() -> None:
    low = _text(PLAN).lower()
    assert "implementation objective" in low
    assert "read one audit artifact" in low
    assert "return `valid`, `warning`, or `invalid`" in low


# ── 8-9. proposed command shape + one artifact path ───────────────────────────

def test_plan_command_shape_proposed_only() -> None:
    text = _text(PLAN)
    assert "run_phase7b_audit_verifier.sh" in text
    assert "verify_manual_approval_audit" in text
    assert "proposed future names only" in text.lower()


def test_plan_one_audit_artifact_path() -> None:
    assert "exactly one audit artifact path" in _text(PLAN).lower()


# ── 10-11. input contract + required fields ───────────────────────────────────

def test_plan_input_contract() -> None:
    low = _text(PLAN).lower()
    assert "one json audit artifact" in low
    assert "read-only input" in low
    assert "must not modify the input" in low


def test_plan_required_audit_fields() -> None:
    text = _text(PLAN)
    for field in (
        "product_id",
        "report_week",
        "selected_gate",
        "primitive_name",
        "operator",
        "approval_reason",
        "timestamp",
        "source_packet_path",
        "verifier_path",
        "execution_plan_path",
        "precondition_summary",
        "result_summary",
        "outcome",
        "mutation_attempted",
        "gate_specific_approval_intent",
        "approved_flag_name",
        "wrapper_version",
        "audit_schema_version",
    ):
        assert field in text, f"missing audit field: {field}"


# ── 12. validation rules ──────────────────────────────────────────────────────

def test_plan_validation_rules() -> None:
    text = _text(PLAN)
    for gate in ("`promote`", "`decision`", "`finalization`"):
        assert gate in text, f"missing gate value: {gate}"
    for prim in ("promote_product_candidates.py", "create_decision.py", "finalize_decision.py"):
        assert prim in text, f"missing primitive: {prim}"
    for flag in ("APPROVE_PROMOTE", "APPROVE_DECISION", "APPROVE_FINALIZE"):
        assert flag in text, f"missing flag: {flag}"
    low = text.lower()
    for token in (
        "only one gate is represented",
        "no multi-gate list",
        "no global approval",
        "no approve-all",
        "no automatic next-gate",
        "no chain execution",
        "no hidden promotion",
        "no ui-direct approval",
    ):
        assert token in low, f"missing validation token: {token}"


# ── 13. mutation consistency ──────────────────────────────────────────────────

def test_plan_mutation_consistency() -> None:
    low = _text(PLAN).lower()
    assert "`blocked` or `prevented` means `mutation_attempted` is false" in low
    assert "`success` or `failure` means `mutation_attempted` must be explicit" in low


# ── 14. path rules ────────────────────────────────────────────────────────────

def test_plan_path_rules() -> None:
    low = _text(PLAN).lower()
    assert "relative `tmp/` path" in low
    assert "no absolute path" in low
    assert "no traversal" in low
    assert "no vault path" in low
    assert "no external url" in low
    assert "no operator-local path" in low


# ── 15. output contract ───────────────────────────────────────────────────────

def test_plan_output_contract() -> None:
    text = _text(PLAN)
    assert "tmp/phase7b-audit-verifier/" in text
    low = text.lower()
    assert "json verifier report" in low
    assert "markdown verifier report" in low
    for field in (
        "type",
        "generated_at",
        "source_audit_path",
        "source_audit_sha256",
        "source_audit_bytes",
        "required_fields",
        "gate_consistency",
        "path_safety",
        "mutation_consistency",
        "forbidden_content",
        "referenced_artifacts",
        "warnings",
        "failures",
        "verdict",
        "statement",
    ):
        assert f"`{field}`" in text, f"missing planned JSON field: {field}"


# ── 16. verdict policy + exit ─────────────────────────────────────────────────

def test_plan_verdict_policy() -> None:
    text = _text(PLAN)
    for verdict in ("`valid`", "`warning`", "`invalid`"):
        assert verdict in text, f"missing verdict: {verdict}"
    low = text.lower()
    assert "`valid` exits 0" in low
    assert "`warning` exits 0" in low
    assert "`invalid` exits non-zero" in low


# ── 17. fail-closed behavior ──────────────────────────────────────────────────

def test_plan_fail_closed() -> None:
    low = _text(PLAN).lower()
    for token in (
        "fail closed on missing input",
        "fail closed on invalid json",
        "fail closed on missing required field",
        "fail closed on unsafe path",
        "fail closed on command form",
        "fail closed on leakage",
    ):
        assert token in low, f"missing fail-closed token: {token}"


# ── 18. safety statements ─────────────────────────────────────────────────────

def test_plan_safety_statements() -> None:
    low = _text(PLAN).lower()
    for token in (
        "never execute primitives",
        "never mutate vault",
        "never rewrite audit artifact",
        "never trigger wrapper",
        "never infer approval",
        "always report evidence",
    ):
        assert token in low, f"missing safety token: {token}"


# ── 19. future Phase 7B test plan ─────────────────────────────────────────────

def test_plan_future_phase7b_tests() -> None:
    low = _text(PLAN).lower()
    assert "future phase 7b test plan" in low
    assert "valid promote audit -> `valid`" in low
    assert "missing required field -> `invalid`" in low
    assert "optional metadata warning path -> `warning`" in low
    assert "no primitive execution" in low


# ── 20-22. additive pointers ──────────────────────────────────────────────────

def test_roadmap_references_phase7a_and_7b() -> None:
    text = _text(ROADMAP)
    assert "Phase 7A" in text
    assert "Phase 7B" in text
    assert "MANUAL_APPROVAL_AUDIT_VERIFIER_IMPLEMENTATION_PLAN.md" in text


def test_project_state_points_to_plan() -> None:
    assert "docs/MANUAL_APPROVAL_AUDIT_VERIFIER_IMPLEMENTATION_PLAN.md" in _text(PROJECT_STATE)


def test_release_snapshot_points_to_phase7a() -> None:
    text = _text(RELEASE_SNAPSHOT)
    assert "Phase 7A" in text
    assert "MANUAL_APPROVAL_AUDIT_VERIFIER_IMPLEMENTATION_PLAN.md" in text


# ── 23-24. token regression ───────────────────────────────────────────────────

def test_roadmap_tokens_preserved() -> None:
    text = _text(ROADMAP)
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in text, f"ROADMAP dropped token: {token}"


def test_project_state_tokens_preserved() -> None:
    text = _text(PROJECT_STATE)
    for token in ("Current architecture", "no database", "no FastAPI", "no UI", "no external APIs", "no autopublish"):
        assert token in text, f"PROJECT_STATE dropped token: {token}"


# ── 25. no-execution guard (new files only) ───────────────────────────────────

def test_new_files_no_execution_forms() -> None:
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
        for form in banned:
            assert form not in text, f"{path.name} contains execution form: {form}"


# ── 26. static safety (new files only) ────────────────────────────────────────

def test_new_files_static_safety() -> None:
    for path in NEW_FILES:
        text = _text(path)
        for token in ("http://", "https://", "/home/ubuntu/Affiliate-Ai",
                      "AWS_SECRET_ACCESS_KEY", "BEGIN PRIVATE KEY", "OPENAI_API_KEY"):
            assert token not in text, f"{path.name} contains forbidden token: {token}"
