from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/045-phase7d-r-high-risk-readiness-review.md"
REVIEW = REPO_ROOT / "docs/HIGH_RISK_SINGLE_GATE_WRAPPER_READINESS_REVIEW.md"
PLAN = REPO_ROOT / "docs/SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_IMPLEMENTATION_PLAN.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
RELEASE_SNAPSHOT = REPO_ROOT / "docs/RELEASE_SNAPSHOT_PHASE6.md"

NEW_FILES = (REVIEW, TASK_FILE)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ── 1-5. existence / status / scope / no wrapper ──────────────────────────────

def test_task_and_review_exist() -> None:
    assert TASK_FILE.is_file()
    assert REVIEW.is_file()


def test_task_final_status() -> None:
    assert "phase7d_r_status: success" in _text(TASK_FILE)


def test_review_runtime_readiness_blocked() -> None:
    assert "phase7d_runtime_readiness: blocked" in _text(REVIEW)


def test_review_scope_docs_only() -> None:
    low = _text(REVIEW).lower()
    assert "docs/tests/task-only" in low or "readiness review only" in low


def test_phase7d_wrapper_scripts_now_exist_but_review_remains_historical() -> None:
    assert (REPO_ROOT / "scripts/dev/run_phase7d_single_gate_wrapper.sh").is_file()
    assert not (REPO_ROOT / "scripts/dev/run_manual_approval_wrapper.sh").exists()
    assert (REPO_ROOT / "scripts/dev/execute_single_gate_approval.py").is_file()


# ── 6-7. readiness status model ───────────────────────────────────────────────

def test_review_status_model() -> None:
    text = _text(REVIEW)
    for token in ("ready_for_implementation", "blocked", "rejected"):
        assert token in text, f"missing status value: {token}"


def test_review_runtime_blocked_until_approval() -> None:
    low = _text(REVIEW).lower()
    assert "remains blocked until the user explicitly approves" in low


# ── 8-10. primitive invocation policy ─────────────────────────────────────────

def test_review_primitive_invocation_policy() -> None:
    low = _text(REVIEW).lower()
    assert "primitive invocation policy" in low
    assert "execute at most one primitive per invocation" in low


def test_review_explicit_allowlist() -> None:
    assert "explicit allowlist mapping" in _text(REVIEW).lower()


def test_review_no_untrusted_dynamic_invocation() -> None:
    low = _text(REVIEW).lower()
    assert "untrusted gate string" in low or "untrusted dynamic string" in low


# ── 11-16. selected-gate-only enforcement ─────────────────────────────────────

def test_review_selected_gate_only() -> None:
    assert "selected-gate-only enforcement" in _text(REVIEW).lower()


def test_review_allowed_gates() -> None:
    text = _text(REVIEW)
    for gate in ("promote", "decision", "finalization"):
        assert gate in text, f"missing gate: {gate}"


def test_review_requires_per_gate_plan() -> None:
    assert "per_gate_plan" in _text(REVIEW)


def test_review_requires_plan_ready() -> None:
    assert "plan_ready" in _text(REVIEW)


def test_review_blocked_overall_nuance() -> None:
    low = _text(REVIEW).lower()
    assert "overall `blocked` may be acceptable only if the selected gate itself" in low


def test_review_overall_failed_rejected() -> None:
    low = _text(REVIEW).lower()
    assert "overall `failed` is always rejected" in low


# ── 17. approval flag semantics ───────────────────────────────────────────────

def test_review_approval_flag_semantics() -> None:
    text = _text(REVIEW)
    for flag in ("APPROVE_PROMOTE", "APPROVE_DECISION", "APPROVE_FINALIZE"):
        assert flag in text, f"missing flag: {flag}"
    low = text.lower()
    for token in (
        "exactly one matching",
        "unrelated truthy approval flag",
        "multiple truthy approval flags",
        "global approval",
        "approve-all",
    ):
        assert token in low, f"missing approval flag token: {token}"


# ── 18. precondition evidence contract ────────────────────────────────────────

def test_review_precondition_evidence_contract() -> None:
    low = _text(REVIEW).lower()
    for token in (
        "phase 6b packet exists",
        "phase 6b packet `dry_run` is true",
        "phase 6c verdict is `ready`",
        "phase 6e execution plan exists",
        "phase 6e `dry_run` is true",
        "phase 6e overall verdict is not `failed`",
        "`product_id` matches across operator input",
        "`report_week` matches across operator input",
        "operator identity is non-empty",
        "approval reason is non-empty",
        "gate-specific approval intent is present",
    ):
        assert token in low, f"missing precondition token: {token}"


# ── 19-20. audit behavior + Phase 7B fields ───────────────────────────────────

def test_review_audit_outcomes() -> None:
    text = _text(REVIEW)
    for outcome in ("`success`", "`failure`", "`blocked`", "`prevented`"):
        assert outcome in text, f"missing outcome: {outcome}"


def test_review_audit_phase7b_fields() -> None:
    text = _text(REVIEW)
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


# ── 21. crash-window mitigation ───────────────────────────────────────────────

def test_review_crash_window_mitigation() -> None:
    low = _text(REVIEW).lower()
    assert "intent / pre-execution audit record" in low
    assert "result / post-execution audit record" in low
    assert "partial completion" in low
    assert "manual review" in low


# ── 22. vault write boundary ──────────────────────────────────────────────────

def test_review_vault_write_boundary() -> None:
    low = _text(REVIEW).lower()
    assert "no vault write on a failed precondition" in low
    assert "except an audit under `tmp/`" in low
    assert "only inside the selected primitive" in low
    assert "no durable audit in the vault in phase 7d unless separately approved" in low


# ── 23. failure / rollback posture ────────────────────────────────────────────

def test_review_failure_rollback_posture() -> None:
    low = _text(REVIEW).lower()
    assert "fail closed on a failed precondition" in low
    assert "never retry silently" in low
    assert "never rollback automatically" in low
    assert "never run a compensating primitive automatically" in low
    assert "require manual review after a primitive failure" in low


# ── 24. emergency stop / dry-run decision ─────────────────────────────────────

def test_review_emergency_stop_dry_run() -> None:
    low = _text(REVIEW).lower()
    assert "default to dry-run or prevented mode" in low
    assert "matching gate\n  approval flag" in low or "matching gate approval flag" in low
    assert "operator confirmation" in low
    assert "remains blocked until this policy is explicitly accepted" in low


# ── 25. Phase 7B verifier integration ─────────────────────────────────────────

def test_review_phase7b_integration() -> None:
    low = _text(REVIEW).lower()
    assert "compatible with phase 7b" in low
    assert "keep the verifier read-only" in low
    assert "never let the phase 7b verifier trigger the next gate" in low
    assert "never treat a verifier `valid` result as approval" in low


# ── 26. forbidden-under-all-conditions ────────────────────────────────────────

def test_review_forbidden_list() -> None:
    low = _text(REVIEW).lower()
    for token in (
        "execute more than one gate",
        "execute a primitive from an untrusted dynamic string",
        "execute a primitive without matching gate approval",
        "run the next gate automatically",
        "retry silently",
        "rollback automatically",
        "accept global approval",
        "accept approve-all",
        "accept a multi-gate request",
        "use backend/api/database/network",
        "autopublish",
        "campaign launch",
        "marketplace submit",
        "generate affiliate links",
    ):
        assert token in low, f"missing forbidden token: {token}"


# ── 27. Phase 7D implementation checklist ─────────────────────────────────────

def test_review_phase7d_checklist() -> None:
    low = _text(REVIEW).lower()
    assert "future phase 7d implementation checklist" in low
    assert "wrapper accepts exactly one gate" in low
    assert "the audit passes the phase 7b verifier" in low
    assert "full suite passes" in low


# ── 28-31. additive pointers ──────────────────────────────────────────────────

def test_roadmap_references_7dr_and_7d() -> None:
    text = _text(ROADMAP)
    assert "Phase 7D-R" in text
    assert "Phase 7D " in text or "Phase 7D —" in text
    assert "HIGH_RISK_SINGLE_GATE_WRAPPER_READINESS_REVIEW.md" in text


def test_project_state_points_to_review() -> None:
    assert "docs/HIGH_RISK_SINGLE_GATE_WRAPPER_READINESS_REVIEW.md" in _text(PROJECT_STATE)


def test_plan_points_to_review() -> None:
    assert "HIGH_RISK_SINGLE_GATE_WRAPPER_READINESS_REVIEW.md" in _text(PLAN)


def test_release_snapshot_points_to_7dr() -> None:
    text = _text(RELEASE_SNAPSHOT)
    assert "Phase 7D-R" in text
    assert "HIGH_RISK_SINGLE_GATE_WRAPPER_READINESS_REVIEW.md" in text


# ── 32-33. token regression ───────────────────────────────────────────────────

def test_roadmap_tokens_preserved() -> None:
    text = _text(ROADMAP)
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in text, f"ROADMAP dropped token: {token}"


def test_project_state_tokens_preserved() -> None:
    text = _text(PROJECT_STATE)
    for token in ("Current architecture", "no database", "no FastAPI", "no UI", "no external APIs", "no autopublish"):
        assert token in text, f"PROJECT_STATE dropped token: {token}"


# ── 34. no-execution guard (new files only) ───────────────────────────────────

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


# ── 35. static safety (new files only) ────────────────────────────────────────

def test_new_files_static_safety() -> None:
    for path in NEW_FILES:
        text = _text(path)
        for token in ("http://", "https://", "/home/ubuntu/Affiliate-Ai",
                      "AWS_SECRET_ACCESS_KEY", "BEGIN PRIVATE KEY", "OPENAI_API_KEY"):
            assert token not in text, f"{path.name} contains forbidden token: {token}"
