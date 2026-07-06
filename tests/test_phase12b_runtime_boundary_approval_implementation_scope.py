from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/088-phase12b-runtime-boundary-approval-implementation-scope.md"
DOC = REPO_ROOT / "docs/PHASE12B_RUNTIME_BOUNDARY_APPROVAL_AND_IMPLEMENTATION_SCOPE.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE12A_DOC = REPO_ROOT / "docs/PHASE12A_GOVERNED_PRODUCTION_CANDIDATE_IMPLEMENTATION_PLAN.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(_text(path).lower().replace("`", "").split())


def _assert_all_tokens(text: str, tokens: tuple[str, ...] | list[str], *, label: str) -> None:
    for token in tokens:
        assert token in text, f"missing {label}: {token}"


def test_phase12b_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 12B file: {path}"


def test_phase12b_only_introduces_expected_phase_files() -> None:
    matches = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("*phase12b*")
        if path.is_file()
        and ".git" not in path.relative_to(REPO_ROOT).parts
        and "__pycache__" not in path.relative_to(REPO_ROOT).parts
    )
    assert matches == [
        "codex/tasks/088-phase12b-runtime-boundary-approval-implementation-scope.md",
        "tests/test_phase12b_runtime_boundary_approval_implementation_scope.py",
    ]


def test_phase12b_only_introduces_expected_planning_doc() -> None:
    matches = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("*PHASE12B*")
        if path.is_file()
        and "__pycache__" not in path.relative_to(REPO_ROOT).parts
    )
    assert matches == [
        "docs/PHASE12B_RUNTIME_BOUNDARY_APPROVAL_AND_IMPLEMENTATION_SCOPE.md",
    ]


def test_phase12b_required_canonical_wording_exists() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "Phase 12B defines runtime boundary approval and implementation scope.",
            "Phase 12B does not implement production runtime.",
            "Phase 12B does not approve production promotion.",
            "Phase 12B does not grant implementation approval.",
            "Phase 12B does not implement authentication runtime.",
            "Phase 12B does not implement RBAC enforcement.",
            "Phase 12B does not implement key custody runtime.",
            "Phase 12B does not implement backend/API/database.",
            "Phase 12B does not implement production signing.",
            "Phase 12B does not implement verifier runtime.",
            "Phase 12B does not implement production policy engine.",
            "Phase 12B does not implement deployment runtime.",
            "Phase 12B does not implement production promotion automation.",
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


def test_phase12b_task_file_preserves_core_boundary_wording() -> None:
    text = _text(TASK_FILE)
    _assert_all_tokens(
        text,
        (
            "phase12b_status: success",
            "Phase 12B defines runtime boundary approval and implementation scope.",
            "Phase 12B does not implement production runtime.",
            "Phase 12B does not approve production promotion.",
            "Phase 12B does not grant implementation approval.",
            "Approval remains the Phase 7D selected-gate manual boundary.",
        ),
        label="task token",
    )


def test_phase12b_required_sections_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 12b purpose",
            "relationship to phase 12a",
            "runtime boundary approval scope",
            "implementation scope definition",
            "proposed runtime domain inventory",
            "deferred runtime domain inventory",
            "approval evidence requirements",
            "implementation approval gate model",
            "runtime boundary classification model",
            "candidate domain approval matrix",
            "deferred domain rationale matrix",
            "evidence-to-approval mapping",
            "implementation readiness checklist",
            "production promotion exclusion",
            "manual approval boundary preservation",
            "local-only prototype protection",
            "authentication runtime scope",
            "authorization and rbac runtime scope",
            "policy engine runtime scope",
            "backend/api/database runtime scope",
            "secrets and key custody runtime scope",
            "signing and verifier runtime scope",
            "observability and audit runtime scope",
            "backup and recovery runtime scope",
            "deployment runtime scope",
            "ci/cd runtime scope",
            "production promotion automation scope",
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


def test_phase12b_references_prior_phase_readiness_and_manual_boundary_language() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 12a defines governed production candidate implementation planning",
            "phase 11 acceptance remains readiness, not approval",
            "phase 10 acceptance remains readiness, not approval",
            "approval remains the phase 7d selected-gate manual boundary",
            "local-only prototypes remain local-only until governed promotion is explicitly approved",
            "rbac advisory context remains not enforcement",
        ),
        label="readiness reference token",
    )


def test_phase12b_proposed_runtime_domain_inventory_is_documented() -> None:
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
            "out of scope for phase 12b",
        ),
        label="proposed runtime domain token",
    )


def test_phase12b_deferred_runtime_domain_inventory_is_documented() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "production authentication",
            "rbac enforcement",
            "production policy engine",
            "backend/api/database",
            "production signing",
            "verifier runtime",
            "key custody runtime",
            "deployment runtime",
            "production promotion automation",
        ),
        label="deferred runtime domain token",
    )


def test_phase12b_approval_gate_model_is_documented() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "implementation scope approval",
            "runtime boundary approval",
            "authentication/rbac approval",
            "backend/api/database approval",
            "secrets/key custody approval",
            "signing/verifier approval",
            "policy engine approval",
            "observability/audit approval",
            "backup/recovery approval",
            "deployment approval",
            "production promotion approval",
            "phase 12b defines these approval gates but does not grant them",
        ),
        label="approval gate token",
    )


def test_phase12b_required_mapping_tables_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "## Candidate Domain Approval Matrix",
            "| Runtime Domain | Proposed Scope | Approval Gate | Required Evidence | Implementation Status | Blocking Condition |",
            "## Deferred Domain Rationale Matrix",
            "| Deferred Domain | Deferral Reason | Required Future Approval | Required Evidence | Risk if Implemented Early | Next Eligible Phase |",
            "## Evidence-to-Approval Mapping",
            "| Evidence Type | Related Runtime Domain | Required Approval Gate | Reviewer Requirement | Blocking Condition | Production Promotion Impact |",
        ),
        label="mapping table token",
    )


def test_phase12b_implementation_readiness_and_promotion_exclusion_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "implementation readiness checklist",
            "production promotion exclusion",
            "manual approval boundary preservation",
            "local-only prototype protection",
            "safe demo scenarios",
            "operator checklist",
        ),
        label="readiness token",
    )


def test_phase12b_failure_handling_model_is_documented() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "fail-closed missing implementation scope approval",
            "fail-closed missing runtime boundary approval",
            "fail-closed missing required evidence",
            "fail-closed ambiguous implementation status",
            "no silent implementation approval",
            "no warning-only bypass for runtime boundary approval",
            "explicit operator review requirement",
            "implementation approval does not equal production promotion approval",
            "production promotion approval remains deferred unless explicitly approved in a later phase",
        ),
        label="failure handling token",
    )


def test_phase12b_non_goals_and_runtime_exclusions_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 12b does not implement production runtime",
            "phase 12b does not approve production promotion",
            "phase 12b does not grant implementation approval",
            "phase 12b does not implement authentication runtime",
            "phase 12b does not implement rbac enforcement",
            "phase 12b does not implement key custody runtime",
            "phase 12b does not implement backend/api/database",
            "phase 12b does not implement production signing",
            "phase 12b does not implement verifier runtime",
            "phase 12b does not implement production policy engine",
            "phase 12b does not implement deployment runtime",
            "phase 12b does not implement production promotion automation",
            "github actions workflow",
            "ci/cd deployment pipeline",
            "vault client runtime",
            "audit storage runtime",
        ),
        label="non-goal token",
    )


def test_phase12b_pointer_docs_reference_phase12b() -> None:
    for path in (ROADMAP, PROJECT_STATE, PHASE12A_DOC):
        low = _flat(path)
        _assert_all_tokens(
            low,
            (
                "phase 12b",
                "runtime boundary approval and implementation scope",
            ),
            label=f"pointer token in {path.name}",
        )


def test_phase12b_forbidden_runtime_artifacts_are_absent() -> None:
    forbidden = [
        REPO_ROOT / "scripts/dev/run_phase12b_runtime_boundary_approval_and_implementation_scope.sh",
        REPO_ROOT / "scripts/dev/phase12b_runtime_boundary_approval_and_implementation_scope.py",
        REPO_ROOT / "scripts/dev/phase12b_authentication_runtime.py",
        REPO_ROOT / "scripts/dev/phase12b_policy_engine_runtime.py",
        REPO_ROOT / ".github/workflows/phase12b-runtime-boundary-approval-implementation-scope.yml",
        REPO_ROOT / "deploy/phase12b-runtime-boundary-approval-implementation-scope.yaml",
        REPO_ROOT / "deploy/phase12b-runtime-boundary-approval-implementation-scope.yml",
        REPO_ROOT / "infra/phase12b-runtime-boundary-approval-implementation-scope.tf",
        REPO_ROOT / "keys/phase12b-production-signing.key",
        REPO_ROOT / "certs/phase12b-production-signing.crt",
    ]
    for path in forbidden:
        assert not path.exists(), f"unexpected Phase 12B runtime artifact: {path}"
