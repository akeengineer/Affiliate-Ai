from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/089-phase12c-implementation-approval-evidence-package.md"
DOC = REPO_ROOT / "docs/PHASE12C_IMPLEMENTATION_APPROVAL_EVIDENCE_PACKAGE.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE12B_DOC = REPO_ROOT / "docs/PHASE12B_RUNTIME_BOUNDARY_APPROVAL_AND_IMPLEMENTATION_SCOPE.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(_text(path).lower().replace("`", "").split())


def _assert_all_tokens(text: str, tokens: tuple[str, ...] | list[str], *, label: str) -> None:
    for token in tokens:
        assert token in text, f"missing {label}: {token}"


def test_phase12c_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 12C file: {path}"


def test_phase12c_only_introduces_expected_phase_files() -> None:
    matches = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("*phase12c*")
        if path.is_file()
        and ".git" not in path.relative_to(REPO_ROOT).parts
        and "__pycache__" not in path.relative_to(REPO_ROOT).parts
    )
    assert matches == [
        "codex/tasks/089-phase12c-implementation-approval-evidence-package.md",
        "tests/test_phase12c_implementation_approval_evidence_package.py",
    ]


def test_phase12c_only_introduces_expected_planning_doc() -> None:
    matches = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("*PHASE12C*")
        if path.is_file()
        and "__pycache__" not in path.relative_to(REPO_ROOT).parts
    )
    assert matches == [
        "docs/PHASE12C_IMPLEMENTATION_APPROVAL_EVIDENCE_PACKAGE.md",
    ]


def test_phase12c_required_canonical_wording_exists() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "Phase 12C defines implementation approval evidence package requirements.",
            "Phase 12C does not implement production runtime.",
            "Phase 12C does not approve production promotion.",
            "Phase 12C does not grant implementation approval.",
            "Phase 12C does not implement authentication runtime.",
            "Phase 12C does not implement RBAC enforcement.",
            "Phase 12C does not implement key custody runtime.",
            "Phase 12C does not implement backend/API/database.",
            "Phase 12C does not implement production signing.",
            "Phase 12C does not implement verifier runtime.",
            "Phase 12C does not implement production policy engine.",
            "Phase 12C does not implement deployment runtime.",
            "Phase 12C does not implement production promotion automation.",
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


def test_phase12c_task_file_preserves_core_boundary_wording() -> None:
    text = _text(TASK_FILE)
    _assert_all_tokens(
        text,
        (
            "phase12c_status: success",
            "Phase 12C defines implementation approval evidence package requirements.",
            "Phase 12C does not implement production runtime.",
            "Phase 12C does not approve production promotion.",
            "Phase 12C does not grant implementation approval.",
            "Approval remains the Phase 7D selected-gate manual boundary.",
        ),
        label="task token",
    )


def test_phase12c_required_sections_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 12c purpose",
            "relationship to phase 12a and phase 12b",
            "implementation approval evidence scope",
            "evidence package definition",
            "runtime domain evidence requirements",
            "approval request contents",
            "reviewer and operator expectations",
            "blocking conditions",
            "traceability requirements",
            "readiness attestation model",
            "evidence classification model",
            "evidence completeness criteria",
            "evidence integrity requirements",
            "evidence freshness requirements",
            "evidence ownership requirements",
            "evidence review workflow",
            "runtime domain approval evidence matrix",
            "evidence-to-approval gate mapping",
            "blocking condition matrix",
            "reviewer responsibility matrix",
            "security evidence requirements",
            "ci evidence requirements",
            "observability evidence requirements",
            "secrets and key custody evidence requirements",
            "backup and recovery evidence requirements",
            "rollback evidence requirements",
            "deployment evidence requirements",
            "production promotion exclusion",
            "manual approval boundary preservation",
            "local-only prototype protection",
            "failure handling and escalation",
            "dependency and sequencing risks",
            "non-goals and forbidden implementations",
            "acceptance criteria",
            "safe demo scenarios",
            "operator checklist",
            "recommended next step",
            "recommended next major subphase",
        ),
        label="section",
    )


def test_phase12c_references_prior_phase_readiness_and_manual_boundary_language() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
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


def test_phase12c_evidence_classification_model_is_documented() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 11 acceptance evidence",
            "phase 12a planning evidence",
            "phase 12b runtime boundary evidence",
            "security control evidence",
            "ci gate evidence",
            "protected boundary evidence",
            "observability evidence",
            "audit retention evidence",
            "secrets/key custody evidence",
            "signing/verifier evidence",
            "backup/recovery evidence",
            "rollback evidence",
            "deployment readiness evidence",
            "reviewer attestation",
            "operator approval request",
            "blocking condition evidence",
            "no evidence class may be treated as implementation approval by itself",
        ),
        label="evidence classification token",
    )


def test_phase12c_runtime_domain_evidence_requirements_are_documented() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "authentication runtime",
            "authorization/rbac runtime",
            "policy engine runtime",
            "backend/api runtime",
            "database/storage runtime",
            "secrets/key custody runtime",
            "signing runtime",
            "verifier runtime",
            "observability runtime",
            "audit storage runtime",
            "backup/restore runtime",
            "deployment runtime",
            "ci/cd runtime",
            "rollback automation",
            "production promotion automation",
            "proposed for future approval",
            "deferred pending explicit approval",
            "out of scope for phase 12c",
        ),
        label="runtime domain evidence token",
    )


def test_phase12c_approval_request_contents_are_documented() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "requested runtime domain",
            "implementation scope",
            "explicit non-goals",
            "phase 11 readiness references",
            "phase 12a planning references",
            "phase 12b boundary references",
            "required evidence package",
            "reviewer assignment",
            "blocking conditions",
            "rollback expectation",
            "observability expectation",
            "security control expectation",
            "secrets/key custody expectation where applicable",
            "production promotion exclusion statement",
        ),
        label="approval request token",
    )


def test_phase12c_reviewer_operator_blocking_traceability_and_attestation_models_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "reviewer and operator expectations",
            "blocking conditions",
            "traceability requirements",
            "readiness attestation model",
            "evidence completeness criteria",
            "evidence integrity requirements",
            "evidence freshness requirements",
            "evidence ownership requirements",
            "evidence review workflow",
        ),
        label="process model token",
    )


def test_phase12c_required_mapping_tables_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "## Runtime Domain Approval Evidence Matrix",
            "| Runtime Domain | Required Evidence | Required Reviewer | Required Approval Gate | Blocking Condition | Implementation Status |",
            "## Evidence-to-Approval Gate Mapping",
            "| Evidence Type | Related Runtime Domain | Required Approval Gate | Reviewer Requirement | Freshness Requirement | Blocking Condition |",
            "## Blocking Condition Matrix",
            "| Blocking Condition | Affected Runtime Domain | Required Evidence | Required Operator Action | Escalation Requirement | Promotion Impact |",
            "## Reviewer Responsibility Matrix",
            "| Reviewer Role | Evidence Responsibility | Approval Boundary | Required Attestation | Conflict of Interest Check | Escalation Path |",
        ),
        label="mapping table token",
    )


def test_phase12c_domain_specific_evidence_sections_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "security evidence requirements",
            "ci evidence requirements",
            "observability evidence requirements",
            "secrets and key custody evidence requirements",
            "backup and recovery evidence requirements",
            "rollback evidence requirements",
            "deployment evidence requirements",
        ),
        label="domain evidence section token",
    )


def test_phase12c_failure_handling_model_is_documented() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "fail-closed missing evidence package",
            "fail-closed incomplete evidence",
            "fail-closed stale evidence",
            "fail-closed ambiguous runtime domain",
            "fail-closed missing reviewer attestation",
            "fail-closed missing blocking condition review",
            "no silent implementation approval",
            "no warning-only bypass for evidence gaps",
            "explicit operator review requirement",
            "implementation approval does not equal production promotion approval",
            "production promotion approval remains deferred unless explicitly approved in a later phase",
        ),
        label="failure handling token",
    )


def test_phase12c_non_goals_and_runtime_exclusions_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 12c does not implement production runtime",
            "phase 12c does not approve production promotion",
            "phase 12c does not grant implementation approval",
            "phase 12c does not implement authentication runtime",
            "phase 12c does not implement rbac enforcement",
            "phase 12c does not implement key custody runtime",
            "phase 12c does not implement backend/api/database",
            "phase 12c does not implement production signing",
            "phase 12c does not implement verifier runtime",
            "phase 12c does not implement production policy engine",
            "phase 12c does not implement deployment runtime",
            "phase 12c does not implement production promotion automation",
            "github actions workflow",
            "ci/cd deployment pipeline",
            "vault client runtime",
            "implementation approval",
        ),
        label="non-goal token",
    )


def test_phase12c_pointer_docs_reference_phase12c() -> None:
    for path in (ROADMAP, PROJECT_STATE, PHASE12B_DOC):
        low = _flat(path)
        _assert_all_tokens(
            low,
            (
                "phase 12c",
                "implementation approval evidence package",
            ),
            label=f"pointer token in {path.name}",
        )


def test_phase12c_forbidden_runtime_artifacts_are_absent() -> None:
    forbidden = [
        REPO_ROOT / "scripts/dev/run_phase12c_implementation_approval_evidence_package.sh",
        REPO_ROOT / "scripts/dev/phase12c_implementation_approval_evidence_package.py",
        REPO_ROOT / "scripts/dev/phase12c_authentication_runtime.py",
        REPO_ROOT / "scripts/dev/phase12c_signing_runtime.py",
        REPO_ROOT / ".github/workflows/phase12c-implementation-approval-evidence-package.yml",
        REPO_ROOT / "deploy/phase12c-implementation-approval-evidence-package.yaml",
        REPO_ROOT / "deploy/phase12c-implementation-approval-evidence-package.yml",
        REPO_ROOT / "infra/phase12c-implementation-approval-evidence-package.tf",
        REPO_ROOT / "keys/phase12c-production-signing.key",
        REPO_ROOT / "certs/phase12c-production-signing.crt",
    ]
    for path in forbidden:
        assert not path.exists(), f"unexpected Phase 12C runtime artifact: {path}"
