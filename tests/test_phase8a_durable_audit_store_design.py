from __future__ import annotations

import hashlib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/052-phase8a-durable-audit-store-design.md"
DESIGN_DOC = REPO_ROOT / "docs/PHASE8A_DURABLE_AUDIT_STORE_DESIGN.md"
THIS_TEST = Path(__file__)
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
RUNBOOK = REPO_ROOT / "docs/PHASE7H_OPERATOR_RUNBOOK.md"
LIVE_SNAPSHOT = REPO_ROOT / "docs/RELEASE_SNAPSHOT_PHASE7_RUNTIME_LIVE.md"

NEW_PHASE8A_FILES = (TASK_FILE, DESIGN_DOC)

PROTECTED_HASHES = {
    REPO_ROOT / "scripts/dev/run_phase7d_single_gate_wrapper.sh": "372aef7a133950a24a1de859a1ba0c01486fd2c84bf46ded783105acc4e47b7d",
    REPO_ROOT / "scripts/dev/execute_single_gate_approval.py": "1b1d00817b1ae89c2840f18c9fe3b73f091abec9c900bf0bff83ad6820e9cebb",
    REPO_ROOT / "scripts/dev/run_phase7b_audit_verifier.sh": "2eed4c68f12dff5306fc244c1a42a843d87b3af6150105fa9681593cd678bfa5",
    REPO_ROOT / "scripts/dev/verify_manual_approval_audit.py": "6c959019f458bd4e79ddf23a9e58055f5fbc16e99660496c4451c13783329c3e",
    REPO_ROOT / "scripts/dev/run_phase7g_safe_demo_pack.sh": "be5f5410d4f4e66b61bda8ba0d4c9861b51f2afb8cb8c099b5c1c60ac6630abb",
    REPO_ROOT / "scripts/dev/build_phase7g_operator_acceptance_summary.py": "9dc7b38a355d8c9d9a5e57c43524308567c0ccf8130449b1a895c5281fc042cf",
    REPO_ROOT / "scripts/dev/promote_product_candidates.py": "496055979f5492389237662d756c4a51a6428da60c804e4ccba72efff0f1ff6e",
    REPO_ROOT / "scripts/dev/create_decision.py": "ac27e4300d617f60e45799980fead1f7e3a09f5f1f083ef5d42c1d327ded4613",
    REPO_ROOT / "scripts/dev/finalize_decision.py": "1c829e797b49ca8a3cff875a1609a06f093ca104873fa20597784a8adac3d177",
    REPO_ROOT / "scripts/dev/run_phase6b_approval_review_packet.sh": "6a26deaec375cf75b51af9efe35c0edb74da71ef5c9809ed05881557c6008718",
    REPO_ROOT / "scripts/dev/build_approval_review_packet.py": "c9344582798d9b34f2f718ac53089d24ec9dba12a6a8b6b403732348f823d127",
    REPO_ROOT / "scripts/dev/run_phase6c_approval_review_verifier.sh": "7c46cb0ea3bc7e992196f0c4ebfabf0fbf14979e73c818cdef3e94913b033750",
    REPO_ROOT / "scripts/dev/verify_approval_review_packet.py": "70601a3c90b96096e08c9fdc5bb66ebbb711c3f2c8607f6cb98d11020c6698e7",
    REPO_ROOT / "scripts/dev/run_phase6e_approval_execution_plan.sh": "aca77b68eabfbb1f17fe9ca5060f7fd2100f21210866ff69ed33217781579d49",
    REPO_ROOT / "scripts/dev/build_approval_execution_plan.py": "d98ca9879b6d3d75c1790f4be54e2489cdc47e90583bd4fe95e4a6e424429c13",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").lower().split())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ── 1-3. existence ─────────────────────────────────────────────────────────

def test_phase8a_required_files_exist() -> None:
    for path in (TASK_FILE, DESIGN_DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 8A file: {path}"


# ── 4-7. required top-level status tokens ───────────────────────────────────

def test_phase8a_task_status_token() -> None:
    assert "phase8a_status: success" in _text(TASK_FILE)


def test_phase8a_design_doc_status_tokens() -> None:
    text = _text(DESIGN_DOC)
    assert "phase8a_status: success" in text
    assert "phase7d_runtime_readiness: implemented_manual_gate" in text
    assert "durable_audit_store_status: design_only" in text


def test_phase8a_task_runtime_readiness_token() -> None:
    assert "phase7d_runtime_readiness: implemented_manual_gate" in _text(TASK_FILE)


# ── 8-16. scope / non-goal tokens in design doc ─────────────────────────────

def test_phase8a_design_doc_scope_tokens() -> None:
    low = _text(DESIGN_DOC).lower()
    for token in (
        "docs/tests-task only",
        "design only",
        "no storage implementation",
        "no database",
        "no backend",
        "no fastapi",
        "no api routes",
        "no phase 7d wrapper behavior change",
        "no primitive execution",
        "no vault read",
        "no vault write",
        "no new mutation path",
    ):
        assert token in low, f"missing scope token: {token}"


def test_phase8a_design_doc_durable_status_repeated() -> None:
    assert _text(DESIGN_DOC).count("durable_audit_store_status: design_only") >= 1


# ── 17. current limitation coverage ─────────────────────────────────────────

def test_phase8a_design_doc_current_limitation_coverage() -> None:
    low = _text(DESIGN_DOC).lower()
    for token in (
        "tmp-local audit is not durable",
        "not queryable over time",
        "not tamper-evident by default",
        "durable audit store is not implemented",
    ):
        assert token in low, f"missing current-limitation token: {token}"


# ── 18. design objectives coverage ──────────────────────────────────────────

def test_phase8a_design_doc_design_objectives_coverage() -> None:
    low = _text(DESIGN_DOC).lower()
    for token in (
        "append-only",
        "immutable record identity",
        "product_id/report_week/selected_gate linkage",
        "wrapper intent audit capture",
        "wrapper result audit capture",
        "primitive outcome reference",
        "phase 7b verifier result reference",
        "operator identity field",
        "reason and intent fields",
        "emergency stop state",
        "precondition summary",
        "result summary",
        "artifact hash",
        "schema version",
        "manual review status",
        "incident reference",
        "retention metadata",
    ):
        assert token in low, f"missing design-objective token: {token}"


# ── 19. audit schema required fields ────────────────────────────────────────

AUDIT_RECORD_FIELDS = (
    "audit_record_id",
    "audit_schema_version",
    "source_phase",
    "product_id",
    "report_week",
    "selected_gate",
    "wrapper_version",
    "operator",
    "approval_reason",
    "approval_intent",
    "execution_mode",
    "emergency_stop_state",
    "mutation_attempted",
    "primitive_name",
    "primitive_outcome",
    "phase6b_packet_ref",
    "phase6c_verifier_ref",
    "phase6e_plan_ref",
    "phase7b_verifier_ref",
    "intent_audit_ref",
    "result_audit_ref",
    "precondition_summary",
    "result_summary",
    "manual_review_status",
    "incident_id",
    "created_at",
    "completed_at",
    "artifact_hash",
    "previous_record_hash",
    "retention_class",
)


def test_phase8a_design_doc_audit_record_fields() -> None:
    text = _text(DESIGN_DOC)
    for field in AUDIT_RECORD_FIELDS:
        assert field in text, f"missing audit record field: {field}"


def test_phase8a_task_audit_record_fields() -> None:
    text = _text(TASK_FILE)
    for field in AUDIT_RECORD_FIELDS:
        assert field in text, f"missing audit record field in task: {field}"


# ── 20. backend options and recommended path ────────────────────────────────

def test_phase8a_design_doc_backend_options() -> None:
    low = _text(DESIGN_DOC).lower()
    for token in (
        "local append-only jsonl",
        "local sqlite",
        "s3 object store",
        "dynamodb table",
        "external siem",
    ):
        assert token in low, f"missing backend option token: {token}"


def test_phase8a_design_doc_recommended_path() -> None:
    text = _text(DESIGN_DOC)
    for token in (
        "Phase 8B: local append-only JSONL prototype",
        "Phase 8C: verifier/reporting over JSONL",
        "Phase 8D: optional SQLite index",
        "Phase 8E: optional S3/DynamoDB design for team/production",
    ):
        assert token in text, f"missing recommended-path token: {token}"


# ── 21. integrity/privacy/operator/verifier/integration requirements ───────

def test_phase8a_design_doc_integrity_and_privacy() -> None:
    low = _text(DESIGN_DOC).lower()
    for token in (
        "tamper-evidence",
        "previous_record_hash",
        "append-only; no in-place edit",
        "never include raw secrets",
        "never include private-key material",
        "never include approval flag truthy assignments",
    ):
        assert token in low, f"missing integrity/privacy token: {token}"


def test_phase8a_design_doc_operator_and_verifier_and_integration() -> None:
    low = _text(DESIGN_DOC).lower()
    for token in (
        "operator identity remains a free-text/non-authenticated field",
        "phase 7b verifier remains read-only and evidence-only",
        "this design does not change phase 7d wrapper behavior",
        "phase7d_runtime_readiness` remains `implemented_manual_gate`",
    ):
        assert token in low, f"missing operator/verifier/integration token: {token}"


# ── 22. failure/recovery/retention/query requirements ───────────────────────

def test_phase8a_design_doc_failure_retention_query() -> None:
    flat = _flat(DESIGN_DOC)
    for token in (
        "must not block or roll back the phase 7d wrapper's primitive execution",
        "require manual review, not automatic retry",
        "manual investigation, not automatic repair",
        "retention_class",
        "query by `product_id`",
        "query by `report_week`",
        "query by `selected_gate`",
    ):
        assert token in flat, f"missing failure/retention/query token: {token}"


# ── 23-26. documentation regression / pointers ──────────────────────────────

def test_phase8a_roadmap_references() -> None:
    text = _text(ROADMAP)
    assert "Phase 8A" in text
    assert "Durable Audit Store Design" in text
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in text, f"ROADMAP dropped token: {token}"


def test_phase8a_project_state_references() -> None:
    text = _text(PROJECT_STATE)
    assert "docs/PHASE8A_DURABLE_AUDIT_STORE_DESIGN.md" in text
    low = text.lower()
    assert "design_only" in low
    for token in (
        "Current architecture",
        "no database",
        "no FastAPI",
        "no UI",
        "no external APIs",
        "no autopublish",
    ):
        assert token in text, f"PROJECT_STATE dropped token: {token}"


def test_phase8a_runbook_references() -> None:
    text = _text(RUNBOOK)
    assert "Phase 8A" in text
    low = text.lower()
    assert "durable audit store" in low
    assert "not implemented yet" in low or "not implemented" in low
    assert "design only" in low


def test_phase8a_live_snapshot_references() -> None:
    text = _text(LIVE_SNAPSHOT)
    assert "Phase 8A" in text
    assert "does not change phase 7 runtime behavior" in _flat(LIVE_SNAPSHOT)


# ── 29. protected runtime files exist and unchanged ─────────────────────────

def test_phase8a_protected_runtime_files_unchanged() -> None:
    for path, expected_hash in PROTECTED_HASHES.items():
        assert path.is_file(), f"missing protected file: {path}"
        assert _sha256(path) == expected_hash, f"protected runtime changed: {path}"


# ── 30-32. no new runtime/storage/database/backend/api files ───────────────

def test_phase8a_no_new_runtime_or_storage_script_exists() -> None:
    scripts_dir = REPO_ROOT / "scripts/dev"
    assert not any(scripts_dir.glob("*phase8a*")), "Phase 8A must not add runtime scripts"
    for pattern in ("*audit_store*", "*audit_writer*", "*durable*"):
        assert not any(scripts_dir.glob(pattern)), f"Phase 8A must not add storage scripts matching {pattern}"


def test_phase8a_no_database_backend_api_files_added() -> None:
    forbidden_suffixes = (".sql", ".sqlite", ".db")
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in {".git", "node_modules", ".venv", "tmp", "vault"} for part in path.parts):
            continue
        if path.suffix.lower() in forbidden_suffixes:
            raise AssertionError(f"unexpected database file found: {path}")
    assert not (REPO_ROOT / "requirements.txt").exists() or "fastapi" not in _text(REPO_ROOT / "requirements.txt").lower()
    assert not (REPO_ROOT / "package.json").exists()


# ── 33. static safety for only the two new Phase 8A files ──────────────────

def test_new_phase8a_files_static_safety() -> None:
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
        "boto3.client",
        "boto3.resource",
        "CREATE TABLE",
        "requests.",
        "socket.",
    )
    for path in NEW_PHASE8A_FILES:
        text = _text(path)
        for token in banned:
            assert token not in text, f"{path.name} contains forbidden token: {token}"
