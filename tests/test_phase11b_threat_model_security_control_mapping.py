from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/081-phase11b-threat-model-security-control-mapping.md"
DOC = REPO_ROOT / "docs/PHASE11B_THREAT_MODEL_SECURITY_CONTROL_MAPPING.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE11A_DOC = REPO_ROOT / "docs/PHASE11A_PRODUCTION_BOUNDARY_AND_HARDENING_READINESS.md"

PHASE11B_RUNTIME = REPO_ROOT / "scripts/dev/build_phase11b_threat_model_security_control_mapping.py"
PHASE11B_RUNNER = REPO_ROOT / "scripts/dev/run_phase11b_threat_model_security_control_mapping.sh"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(_text(path).lower().replace("`", "").split())


def _assert_all_tokens(text: str, tokens: tuple[str, ...] | list[str], *, label: str) -> None:
    for token in tokens:
        assert token in text, f"missing {label}: {token}"


def test_phase11b_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 11B file: {path}"


def test_phase11b_no_runtime_script_or_runner() -> None:
    assert not PHASE11B_RUNTIME.exists(), "Phase 11B must not add runtime script"
    assert not PHASE11B_RUNNER.exists(), "Phase 11B must not add shell runner"
    dev = REPO_ROOT / "scripts/dev"
    for pattern in ("*phase11b*.py", "*phase11b*.sh"):
        matches = sorted(str(path.relative_to(REPO_ROOT)) for path in dev.glob(pattern))
        assert matches == [], f"unexpected Phase 11B runtime file: {matches}"


def test_phase11b_status_tokens() -> None:
    assert "phase11b_status: success" in _text(TASK_FILE)
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "phase11b_status: success",
            "phase11a_status: success",
            "phase10f_status: success",
            "phase7d_runtime_readiness: implemented_manual_gate",
            "production_boundary_status: design_only",
            "hardening_readiness_status: design_only",
            "threat_model_status: design_only",
            "security_control_mapping_status: design_only",
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


def test_phase11b_required_canonical_wording_exists() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "Phase 11B defines threat model and security control mapping.",
            "Phase 11B does not implement production runtime.",
            "Phase 11B does not approve production promotion.",
            "Phase 11A defines production boundary and hardening readiness.",
            "Local-only prototypes remain local-only until governed promotion is explicitly approved.",
            "RBAC advisory context remains not enforcement.",
            "Approval remains the Phase 7D selected-gate manual boundary.",
            "Phase 10 acceptance remains readiness, not approval.",
            "Production authentication, RBAC enforcement, key custody, backend/API/database, production signing, verifier runtime, and production policy engine remain out of scope unless explicitly approved.",
        ),
        label="canonical wording",
    )


def test_phase11b_required_sections_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "### Phase 11B Purpose",
            "### Relationship to Phase 11A",
            "### Threat Modeling Scope",
            "### Assets and Security Objectives",
            "### Trust Boundaries",
            "### Threat Actors",
            "### Abuse Cases",
            "### Threat Categories",
            "### Security Control Objectives",
            "### Control Mapping Matrix",
            "### Approval Boundary Controls",
            "### Artifact Integrity Controls",
            "### Authentication and Authorization Control Requirements",
            "### Secrets and Key Custody Control Requirements",
            "### Policy Decision Control Requirements",
            "### Audit and Evidence Control Requirements",
            "### Export and Signing Control Requirements",
            "### Observability and Incident Detection Controls",
            "### Backup and Recovery Control Requirements",
            "### Residual Risks",
            "### Explicit Non-Goals",
            "### Acceptance Criteria",
            "### Safe Demo Scenarios",
            "### Operator Checklist",
            "### Recommended Next Step",
            "### Recommended Next Major Subphase",
        ),
        label="section",
    )


def test_phase11b_documents_required_threat_categories() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "unauthorized operator action",
            "forged approval event",
            "rbac advisory context misread as enforcement",
            "artifact tampering",
            "unsigned or incorrectly trusted export",
            "primitive execution outside selected-gate boundary",
            "secret leakage",
            "key misuse",
            "policy bypass",
            "audit evidence mutation",
            "path traversal",
            "hardcoded environment assumptions",
            "dependency or supply-chain compromise",
            "ci guardrail bypass",
            "observability blind spot",
            "backup/recovery gap",
            "local-only prototype promoted without approval",
        ),
        label="threat category",
    )


def test_phase11b_documents_control_mapping_matrix() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "| Threat | Impact | Existing Boundary | Required Future Control | Required Evidence | Approval Requirement | Phase Ownership |",
            "already covered by Phase 7D manual approval boundary",
            "covered by Phase 10 local advisory prototype boundary",
            "defined by Phase 11A production boundary readiness",
            "defined by Phase 11B threat/control mapping",
            "deferred to a later explicitly approved production phase",
        ),
        label="control mapping token",
    )


def test_phase11b_documents_residual_risks() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "residual risks",
            "manual approval remains a human boundary",
            "local-only artifacts are still not production-authorized",
            "advisory metadata can still be misunderstood if treated as enforcement",
            "future production controls remain unimplemented until explicitly approved",
        ),
        label="residual risk token",
    )


def test_phase11b_non_goals_are_explicit() -> None:
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


def test_phase11b_approval_boundary_has_no_drift() -> None:
    low = _flat(DOC)
    for token in (
        "approval remains the phase 7d selected-gate manual boundary",
        "phase 10 acceptance remains readiness, not approval",
        "phase 11a defines production boundary and hardening readiness",
        "phase 11b does not approve production promotion",
        "phase 11b does not implement production runtime",
        "rbac advisory context remains not enforcement",
    ):
        assert token in low, f"missing approval-boundary token: {token}"


def test_phase11b_acceptance_and_demo_sections_are_doc_only() -> None:
    low = _flat(DOC)
    for token in (
        "phase 11b acceptance doc exists",
        "phase 11b tests pass",
        "no phase 11b runtime file is introduced",
        "no phase 11b runner is introduced",
        "documentation-focused",
        "safe demo scenarios",
        "non-executing",
        "do not implement production runtime",
    ):
        assert token in low, f"missing doc-only token: {token}"


def test_phase11b_pointer_docs_reference_phase11b() -> None:
    roadmap = _flat(ROADMAP)
    project_state = _flat(PROJECT_STATE)
    phase11a = _flat(PHASE11A_DOC)

    for text, label in (
        (roadmap, "roadmap"),
        (project_state, "project state"),
        (phase11a, "phase11a"),
    ):
        for token in (
            "phase 11b",
            "threat model and security control mapping",
        ):
            assert token in text, f"missing {label} token: {token}"
