from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/080-phase11a-production-boundary-and-hardening-readiness.md"
DOC = REPO_ROOT / "docs/PHASE11A_PRODUCTION_BOUNDARY_AND_HARDENING_READINESS.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE10F_DOC = REPO_ROOT / "docs/PHASE10F_PHASE10_ACCEPTANCE_PACK.md"

PHASE11A_RUNTIME = REPO_ROOT / "scripts/dev/build_phase11a_production_boundary_and_hardening_readiness.py"
PHASE11A_RUNNER = REPO_ROOT / "scripts/dev/run_phase11a_production_boundary_and_hardening_readiness.sh"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(_text(path).lower().replace("`", "").split())


def _assert_all_tokens(text: str, tokens: tuple[str, ...] | list[str], *, label: str) -> None:
    for token in tokens:
        assert token in text, f"missing {label}: {token}"


def test_phase11a_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 11A file: {path}"


def test_phase11a_no_runtime_script_or_runner() -> None:
    assert not PHASE11A_RUNTIME.exists(), "Phase 11A must not add runtime script"
    assert not PHASE11A_RUNNER.exists(), "Phase 11A must not add shell runner"
    dev = REPO_ROOT / "scripts/dev"
    for pattern in ("*phase11a*.py", "*phase11a*.sh"):
        matches = sorted(str(path.relative_to(REPO_ROOT)) for path in dev.glob(pattern))
        assert matches == [], f"unexpected Phase 11A runtime file: {matches}"


def test_phase11a_status_tokens() -> None:
    assert "phase11a_status: success" in _text(TASK_FILE)
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "phase11a_status: success",
            "phase10f_status: success",
            "phase7d_runtime_readiness: implemented_manual_gate",
            "production_boundary_status: design_only",
            "hardening_readiness_status: design_only",
            "governed_production_candidate_status: defined_not_approved",
            "production_runtime_status: out_of_scope",
            "observability_runtime_status: not_implemented",
            "secrets_key_custody_runtime_status: not_implemented",
            "backup_recovery_runtime_status: not_implemented",
            "authentication_runtime_status: not_implemented",
            "rbac_enforcement_status: not_implemented",
            "key_management_runtime_status: not_implemented",
            "backend_api_database_status: not_implemented",
            "phase11_branch_workflow: enabled",
        ),
        label="status token",
    )


def test_phase11a_required_canonical_wording_exists() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "Phase 11A defines production boundary and hardening readiness.",
            "Phase 11A does not implement production runtime.",
            "Phase 11A does not approve production promotion.",
            "Local-only prototypes remain local-only until governed promotion is explicitly approved.",
            "RBAC advisory context remains not enforcement.",
            "Approval remains the Phase 7D selected-gate manual boundary.",
            "Phase 10 acceptance remains readiness, not approval.",
            "Production authentication, RBAC enforcement, key custody, backend/API/database, production signing, verifier runtime, and production policy engine remain out of scope unless explicitly approved.",
        ),
        label="canonical wording",
    )


def test_phase11a_required_sections_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "### Phase 11A Purpose",
            "### Relationship to Phase 10",
            "### Production Boundary Definition",
            "### Local-Only Prototype Inventory",
            "### Governed Production Candidate Criteria",
            "### Hardening Requirements",
            "### CI Gate Model",
            "### Observability Model",
            "### Secrets and Key Custody Design",
            "### Backup and Recovery Posture",
            "### Controlled Promotion Path",
            "### Explicit Approval Requirements",
            "### Non-Goals and Forbidden Implementations",
            "### Acceptance Criteria",
            "### Safe Demo Scenarios",
            "### Operator Checklist",
            "### Recommended Next Step",
            "### Recommended Next Major Subphase",
        ),
        label="section",
    )


def test_phase11a_documents_production_boundary_model() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "local-only prototype",
            "governed production candidate",
            "production runtime",
            "not production-authorized",
            "production runtime is out of scope for phase 11a",
        ),
        label="production boundary token",
    )


def test_phase11a_documents_required_hardening_areas() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "authentication boundary",
            "authorization/rbac boundary",
            "policy decision boundary",
            "artifact integrity boundary",
            "signing and verification boundary",
            "secrets/key custody boundary",
            "audit and evidence boundary",
            "export boundary",
            "failure-mode boundary",
            "operator approval boundary",
            "dependency and supply-chain boundary",
            "filesystem/path boundary",
            "ci/test boundary",
        ),
        label="hardening area",
    )


def test_phase11a_documents_required_ci_gates() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
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
        ),
        label="ci gate",
    )


def test_phase11a_documents_observability_model() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "structured logs",
            "correlation ids",
            "actor attribution",
            "decision traceability",
            "artifact hash tracking",
            "policy decision logging",
            "approval event logging",
            "failure and rejection logging",
            "metrics and health signals",
            "audit retention expectations",
            "do not implement logging runtime",
        ),
        label="observability token",
    )


def test_phase11a_documents_secrets_and_key_custody_design() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "no hardcoded secrets",
            "no test fixtures that trip secret scanners",
            "key material must not be committed",
            "production keys must require controlled custody",
            "signing keys and verification keys must be separated",
            "rotation must be designed before runtime use",
            "emergency revocation must be designed before runtime use",
        ),
        label="secrets token",
    )


def test_phase11a_documents_backup_and_recovery_posture() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "artifact backup",
            "audit store backup",
            "configuration backup",
            "restore testing",
            "recovery time objective placeholder",
            "recovery point objective placeholder",
            "rollback criteria",
            "disaster recovery boundary",
        ),
        label="backup token",
    )


def test_phase11a_documents_controlled_promotion_path() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "1. local-only prototype",
            "2. documented boundary review",
            "3. threat model review",
            "4. hardening checklist review",
            "5. ci gate readiness",
            "6. observability readiness",
            "7. secrets/key custody readiness",
            "8. backup/recovery readiness",
            "9. explicit approval",
            "10. governed production candidate",
            "11. production runtime implementation in a later approved phase",
        ),
        label="promotion path token",
    )


def test_phase11a_non_goals_are_explicit() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "authentication runtime",
            "login/session/user store",
            "rbac enforcement",
            "production policy engine",
            "backend/api/database files",
            "production signing runtime",
            "verifier runtime",
            "key/cert files",
            "key custody runtime",
            "vault write",
            "primitive execution",
            "export mutation",
            "re-signing",
            "network service",
            "deployment manifest",
            "cloud infrastructure",
            "production secrets",
            "ci/cd deployment pipeline",
        ),
        label="non-goal token",
    )


def test_phase11a_approval_boundary_has_no_drift() -> None:
    low = _flat(DOC)
    for token in (
        "approval remains the phase 7d selected-gate manual boundary",
        "phase 10 acceptance remains readiness, not approval",
        "phase 11a does not approve production promotion",
        "rbac advisory context remains not enforcement",
    ):
        assert token in low, f"missing approval-boundary token: {token}"


def test_phase11a_acceptance_and_demo_sections_are_doc_only() -> None:
    low = _flat(DOC)
    for token in (
        "phase 11a acceptance doc exists",
        "phase 11a tests pass",
        "no phase 11a runtime file is introduced",
        "no phase 11a runner is introduced",
        "documentation-focused",
        "safe demo scenarios",
        "non-executing",
        "do not implement production runtime",
    ):
        assert token in low, f"missing doc-only token: {token}"


def test_phase11a_pointer_docs_reference_phase11a() -> None:
    roadmap = _flat(ROADMAP)
    project_state = _flat(PROJECT_STATE)
    phase10f = _flat(PHASE10F_DOC)

    for text, label in (
        (roadmap, "roadmap"),
        (project_state, "project state"),
        (phase10f, "phase10f"),
    ):
        for token in (
            "phase 11a",
            "production boundary and hardening readiness",
        ):
            assert token in text, f"missing {label} pointer token: {token}"
