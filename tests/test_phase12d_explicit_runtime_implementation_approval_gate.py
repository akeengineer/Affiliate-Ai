from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/090-phase12d-explicit-runtime-implementation-approval-gate.md"
DOC = REPO_ROOT / "docs/PHASE12D_EXPLICIT_RUNTIME_IMPLEMENTATION_APPROVAL_GATE.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE12C_DOC = REPO_ROOT / "docs/PHASE12C_IMPLEMENTATION_APPROVAL_EVIDENCE_PACKAGE.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(_text(path).lower().replace("`", "").split())


def _assert_all_tokens(text: str, tokens: tuple[str, ...] | list[str], *, label: str) -> None:
    for token in tokens:
        assert token in text, f"missing {label}: {token}"


def test_phase12d_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 12D file: {path}"


def test_phase12d_only_introduces_expected_phase_files() -> None:
    matches = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("*phase12d*")
        if path.is_file()
        and ".git" not in path.relative_to(REPO_ROOT).parts
        and "__pycache__" not in path.relative_to(REPO_ROOT).parts
    )
    assert matches == [
        "codex/tasks/090-phase12d-explicit-runtime-implementation-approval-gate.md",
        "tests/test_phase12d_explicit_runtime_implementation_approval_gate.py",
    ]


def test_phase12d_only_introduces_expected_planning_doc() -> None:
    matches = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("*PHASE12D*")
        if path.is_file()
        and "__pycache__" not in path.relative_to(REPO_ROOT).parts
    )
    assert matches == [
        "docs/PHASE12D_EXPLICIT_RUNTIME_IMPLEMENTATION_APPROVAL_GATE.md",
    ]


def test_phase12d_required_canonical_wording_exists() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "Phase 12D defines the explicit runtime implementation approval gate.",
            "Phase 12D does not implement production runtime.",
            "Phase 12D does not approve production promotion.",
            "Phase 12D does not bypass the Phase 7D selected-gate manual boundary.",
            "Phase 12D does not implement authentication runtime.",
            "Phase 12D does not implement RBAC enforcement.",
            "Phase 12D does not implement key custody runtime.",
            "Phase 12D does not implement backend/API/database.",
            "Phase 12D does not implement production signing.",
            "Phase 12D does not implement verifier runtime.",
            "Phase 12D does not implement production policy engine.",
            "Phase 12D does not implement deployment runtime.",
            "Phase 12D does not implement production promotion automation.",
            "Phase 12C defines implementation approval evidence package requirements.",
            "Phase 12B defines runtime boundary approval and implementation scope.",
            "Phase 12A defines governed production candidate implementation planning.",
            "Phase 11 acceptance remains readiness, not approval.",
            "Phase 10 acceptance remains readiness, not approval.",
            "Local-only prototypes remain local-only until governed promotion is explicitly approved.",
            "RBAC advisory context remains not enforcement.",
            "Approval remains the Phase 7D selected-gate manual boundary.",
            "Production authentication, RBAC enforcement, key custody, backend/API/database, production signing, verifier runtime, and production policy engine remain out of scope unless explicitly approved.",
        ),
        label="canonical wording",
    )


def test_phase12d_task_file_preserves_core_boundary_wording() -> None:
    text = _text(TASK_FILE)
    _assert_all_tokens(
        text,
        (
            "phase12d_status: success",
            "Phase 12D defines the explicit runtime implementation approval gate.",
            "Phase 12D does not implement production runtime.",
            "Phase 12D does not approve production promotion.",
            "Phase 12D does not bypass the Phase 7D selected-gate manual boundary.",
            "Approval remains the Phase 7D selected-gate manual boundary.",
        ),
        label="task token",
    )


def test_phase12d_required_sections_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 12d purpose",
            "relationship to phase 12a, phase 12b, and phase 12c",
            "explicit runtime implementation approval gate scope",
            "gate decision model",
            "approval eligibility criteria",
            "approval request intake requirements",
            "evidence package review requirements",
            "reviewer role requirements",
            "operator approval requirements",
            "runtime domain approval outcomes",
            "approved-for-implementation outcome",
            "denied outcome",
            "deferred outcome",
            "conditional approval exclusion",
            "production promotion exclusion",
            "manual approval boundary preservation",
            "local-only prototype protection",
            "runtime domain decision matrix",
            "evidence-to-decision mapping",
            "reviewer-to-attestation mapping",
            "blocking condition matrix",
            "implementation authorization record requirements",
            "audit evidence requirements",
            "traceability requirements",
            "fail-closed gate behavior",
            "runtime domain sequencing requirements",
            "dependency and sequencing risks",
            "residual risk handling",
            "non-goals and forbidden implementations",
            "acceptance criteria",
            "safe demo scenarios",
            "operator checklist",
            "recommended next step",
            "recommended next major subphase",
        ),
        label="section",
    )


def test_phase12d_references_prior_phase_readiness_and_manual_boundary_language() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 12c defines implementation approval evidence package requirements",
            "phase 12b defines runtime boundary approval and implementation scope",
            "phase 12a defines governed production candidate implementation planning",
            "phase 11 acceptance remains readiness, not approval",
            "phase 10 acceptance remains readiness, not approval",
            "approval remains the phase 7d selected-gate manual boundary",
            "local-only prototypes remain local-only until governed promotion is explicitly approved",
            "rbac advisory context remains not enforcement",
        ),
        label="readiness reference token",
    )


def test_phase12d_gate_decision_model_is_documented() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "requested runtime domain",
            "phase 12b boundary classification",
            "phase 12c evidence package completeness",
            "evidence freshness",
            "evidence integrity",
            "reviewer attestation",
            "operator approval request",
            "blocking conditions",
            "implementation sequencing risk",
            "rollback expectation",
            "observability expectation",
            "security control expectation",
            "secrets/key custody expectation where applicable",
            "production promotion exclusion",
        ),
        label="gate decision model token",
    )


def test_phase12d_eligibility_intake_reviewer_operator_and_outcome_models_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "approval eligibility criteria",
            "approval request intake requirements",
            "evidence package review requirements",
            "reviewer role requirements",
            "operator approval requirements",
            "runtime domain approval outcomes",
            "approved for future implementation phase",
            "denied",
            "deferred pending evidence",
            "deferred pending reviewer assignment",
            "deferred pending boundary clarification",
            "deferred pending security control evidence",
            "deferred pending rollback evidence",
            "deferred pending observability evidence",
            "deferred pending secrets/key custody evidence",
            "deferred pending backup/recovery evidence",
            "approved-for-implementation outcome",
            "denied outcome",
            "deferred outcome",
            "conditional approval exclusion",
            "production promotion exclusion",
        ),
        label="outcome model token",
    )


def test_phase12d_required_mapping_tables_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "## Runtime Domain Decision Matrix",
            "| Runtime Domain | Required Evidence Package | Required Reviewer | Gate Decision | Implementation Authorization Status | Production Promotion Status |",
            "## Evidence-to-Decision Mapping",
            "| Evidence Type | Related Runtime Domain | Decision Dependency | Freshness Requirement | Integrity Requirement | Blocking Condition |",
            "## Reviewer-to-Attestation Mapping",
            "| Reviewer Role | Required Attestation | Related Runtime Domain | Conflict Check | Escalation Path | Approval Boundary |",
            "## Blocking Condition Matrix",
            "| Blocking Condition | Affected Runtime Domain | Required Resolution | Required Reviewer | Gate Outcome | Production Promotion Impact |",
        ),
        label="mapping table token",
    )


def test_phase12d_authorization_audit_traceability_and_fail_closed_models_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "implementation authorization record requirements",
            "audit evidence requirements",
            "traceability requirements",
            "fail-closed gate behavior",
            "runtime domain sequencing requirements",
            "dependency and sequencing risks",
            "residual risk handling",
        ),
        label="gate support model token",
    )


def test_phase12d_failure_handling_model_is_documented() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "fail-closed missing evidence package",
            "fail-closed incomplete evidence",
            "fail-closed stale evidence",
            "fail-closed ambiguous runtime domain",
            "fail-closed missing reviewer attestation",
            "fail-closed missing operator approval request",
            "fail-closed unresolved blocking condition",
            "fail-closed production promotion ambiguity",
            "no silent implementation approval",
            "no warning-only bypass for approval gates",
            "explicit operator review requirement",
            "implementation approval does not equal production promotion approval",
            "production promotion approval remains deferred unless explicitly approved in a later phase",
        ),
        label="failure handling token",
    )


def test_phase12d_non_goals_and_runtime_exclusions_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 12d does not implement production runtime",
            "phase 12d does not approve production promotion",
            "phase 12d does not bypass the phase 7d selected-gate manual boundary",
            "phase 12d does not implement authentication runtime",
            "phase 12d does not implement rbac enforcement",
            "phase 12d does not implement key custody runtime",
            "phase 12d does not implement backend/api/database",
            "phase 12d does not implement production signing",
            "phase 12d does not implement verifier runtime",
            "phase 12d does not implement production policy engine",
            "phase 12d does not implement deployment runtime",
            "phase 12d does not implement production promotion automation",
            "github actions workflow",
            "ci/cd deployment pipeline",
            "vault client runtime",
            "runtime implementation",
        ),
        label="non-goal token",
    )


def test_phase12d_pointer_docs_reference_phase12d() -> None:
    for path in (ROADMAP, PROJECT_STATE, PHASE12C_DOC):
        low = _flat(path)
        _assert_all_tokens(
            low,
            (
                "phase 12d",
                "explicit runtime implementation approval gate",
            ),
            label=f"pointer token in {path.name}",
        )


def test_phase12d_forbidden_runtime_artifacts_are_absent() -> None:
    forbidden = [
        REPO_ROOT / "scripts/dev/run_phase12d_explicit_runtime_implementation_approval_gate.sh",
        REPO_ROOT / "scripts/dev/phase12d_explicit_runtime_implementation_approval_gate.py",
        REPO_ROOT / "scripts/dev/phase12d_authentication_runtime.py",
        REPO_ROOT / "scripts/dev/phase12d_signing_runtime.py",
        REPO_ROOT / ".github/workflows/phase12d-explicit-runtime-implementation-approval-gate.yml",
        REPO_ROOT / "deploy/phase12d-explicit-runtime-implementation-approval-gate.yaml",
        REPO_ROOT / "deploy/phase12d-explicit-runtime-implementation-approval-gate.yml",
        REPO_ROOT / "infra/phase12d-explicit-runtime-implementation-approval-gate.tf",
        REPO_ROOT / "keys/phase12d-production-signing.key",
        REPO_ROOT / "certs/phase12d-production-signing.crt",
    ]
    for path in forbidden:
        assert not path.exists(), f"unexpected Phase 12D runtime artifact: {path}"
