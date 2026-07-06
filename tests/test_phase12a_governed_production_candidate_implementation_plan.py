from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/087-phase12a-governed-production-candidate-implementation-plan.md"
DOC = REPO_ROOT / "docs/PHASE12A_GOVERNED_PRODUCTION_CANDIDATE_IMPLEMENTATION_PLAN.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE11G_DOC = REPO_ROOT / "docs/PHASE11G_PHASE11_ACCEPTANCE_PACK.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(_text(path).lower().replace("`", "").split())


def _assert_all_tokens(text: str, tokens: tuple[str, ...] | list[str], *, label: str) -> None:
    for token in tokens:
        assert token in text, f"missing {label}: {token}"


def test_phase12a_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 12A file: {path}"


def test_phase12a_only_introduces_expected_phase_files() -> None:
    matches = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("*phase12a*")
        if path.is_file()
        and ".git" not in path.relative_to(REPO_ROOT).parts
        and "__pycache__" not in path.relative_to(REPO_ROOT).parts
    )
    assert matches == [
        "codex/tasks/087-phase12a-governed-production-candidate-implementation-plan.md",
        "tests/test_phase12a_governed_production_candidate_implementation_plan.py",
    ]


def test_phase12a_only_introduces_expected_planning_doc() -> None:
    matches = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("*PHASE12A*")
        if path.is_file()
        and "__pycache__" not in path.relative_to(REPO_ROOT).parts
    )
    assert matches == [
        "docs/PHASE12A_GOVERNED_PRODUCTION_CANDIDATE_IMPLEMENTATION_PLAN.md",
    ]


def test_phase12a_required_canonical_wording_exists() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "Phase 12A defines governed production candidate implementation planning.",
            "Phase 12A does not implement production runtime.",
            "Phase 12A does not approve production promotion.",
            "Phase 12A does not implement authentication runtime.",
            "Phase 12A does not implement RBAC enforcement.",
            "Phase 12A does not implement key custody runtime.",
            "Phase 12A does not implement backend/API/database.",
            "Phase 12A does not implement production signing.",
            "Phase 12A does not implement verifier runtime.",
            "Phase 12A does not implement production policy engine.",
            "Phase 12A does not implement deployment runtime.",
            "Phase 12A does not implement production promotion automation.",
            "Phase 11 acceptance remains readiness, not approval.",
            "Phase 10 acceptance remains readiness, not approval.",
            "Local-only prototypes remain local-only until governed promotion is explicitly approved.",
            "RBAC advisory context remains not enforcement.",
            "Approval remains the Phase 7D selected-gate manual boundary.",
            "Production authentication, RBAC enforcement, key custody, backend/API/database, production signing, verifier runtime, and production policy engine remain out of scope unless explicitly approved.",
        ),
        label="canonical wording",
    )


def test_phase12a_task_file_preserves_core_boundary_wording() -> None:
    text = _text(TASK_FILE)
    _assert_all_tokens(
        text,
        (
            "phase12a_status: success",
            "Phase 12A defines governed production candidate implementation planning.",
            "Phase 12A does not implement production runtime.",
            "Phase 12A does not approve production promotion.",
            "Phase 11 acceptance remains readiness, not approval.",
            "Approval remains the Phase 7D selected-gate manual boundary.",
        ),
        label="task token",
    )


def test_phase12a_required_sections_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 12a purpose",
            "relationship to phase 11 acceptance",
            "production candidate planning scope",
            "implementation planning scope",
            "scoped runtime boundary model",
            "candidate runtime domains",
            "implementation sequence",
            "approval gate model",
            "production candidate acceptance criteria",
            "security control implementation candidates",
            "authentication candidate boundary",
            "authorization and rbac candidate boundary",
            "policy engine candidate boundary",
            "backend/api/database candidate boundary",
            "secrets and key custody candidate boundary",
            "signing and verifier candidate boundary",
            "observability candidate boundary",
            "audit storage candidate boundary",
            "backup and recovery candidate boundary",
            "ci enforcement candidate boundary",
            "deployment candidate boundary",
            "rollback strategy",
            "evidence requirements",
            "promotion constraints",
            "dependency and sequencing risks",
            "residual risk handling",
            "manual approval boundary preservation",
            "local-only prototype protection",
            "non-goals and forbidden implementations",
            "acceptance criteria",
            "safe demo scenarios",
            "operator checklist",
            "recommended next step",
            "recommended next major subphase",
        ),
        label="section",
    )


def test_phase12a_references_phase10_phase11_and_manual_boundary_language() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 11 acceptance remains readiness, not approval",
            "phase 10 acceptance remains readiness, not approval",
            "approval remains the phase 7d selected-gate manual boundary",
            "local-only prototypes remain local-only until governed promotion is explicitly approved",
            "rbac advisory context remains not enforcement",
            "phase 11g is the phase 11 acceptance pack",
            "phase 11a defines production boundary and hardening readiness",
            "phase 11b defines threat model and security control mapping",
            "phase 11c defines ci gate and protected boundary enforcement design",
            "phase 11d defines observability and audit retention readiness",
            "phase 11e defines secrets, signing, and key custody architecture readiness",
            "phase 11f defines backup, recovery, and promotion runbook readiness",
        ),
        label="readiness reference token",
    )


def test_phase12a_candidate_runtime_domains_are_documented() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "authentication boundary",
            "authorization/rbac boundary",
            "policy decision boundary",
            "backend/api boundary",
            "database/storage boundary",
            "signing boundary",
            "verifier boundary",
            "secrets/key custody boundary",
            "observability boundary",
            "audit storage boundary",
            "backup/recovery boundary",
            "deployment boundary",
            "ci enforcement boundary",
            "rollback boundary",
            "production promotion boundary",
            "candidate only",
            "requires explicit approval",
        ),
        label="candidate runtime domain token",
    )


def test_phase12a_implementation_sequence_is_documented() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "confirm phase 11 acceptance baseline",
            "confirm local-only prototype status",
            "confirm explicit approval requirement",
            "define runtime boundary candidates",
            "define implementation dependency order",
            "define security controls per candidate domain",
            "define ci enforcement candidates",
            "define observability implementation candidates",
            "define secrets/key custody implementation candidates",
            "define backup/recovery implementation candidates",
            "define rollback strategy",
            "define production candidate acceptance criteria",
            "request explicit implementation approval",
            "defer runtime implementation to later approved phase 12 subphases",
        ),
        label="implementation sequence token",
    )


def test_phase12a_approval_gate_model_and_evidence_mapping_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "planning approval",
            "runtime boundary approval",
            "security control approval",
            "authentication/rbac approval",
            "backend/api/database approval",
            "secrets/key custody approval",
            "signing/verifier approval",
            "observability/audit approval",
            "backup/recovery approval",
            "deployment approval",
            "production promotion approval",
            "phase 12a does not grant any of these approvals",
            "approval gate to evidence mapping",
            "required reviewer",
            "promotion impact",
        ),
        label="approval gate token",
    )


def test_phase12a_required_mapping_tables_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "## Phase 11 Output to Phase 12 Candidate Mapping",
            "| Phase 11 Output | Candidate Implementation Domain | Required Approval Gate | Required Evidence | Deferred Implementation Phase | Blocking Condition |",
            "## Runtime Boundary Candidate Mapping",
            "| Runtime Domain | Candidate Boundary | Required Control | Required Evidence | Approval Requirement | Implementation Status |",
            "## Approval Gate to Evidence Mapping",
            "| Approval Gate | Required Evidence | Required Reviewer | Blocking Condition | Promotion Impact | Deferred Implementation Phase |",
        ),
        label="mapping table token",
    )


def test_phase12a_acceptance_rollback_evidence_and_promotion_constraints_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "production candidate acceptance criteria",
            "rollback strategy",
            "evidence requirements",
            "promotion constraints",
            "residual risk handling",
            "operator checklist",
            "safe demo scenarios",
        ),
        label="acceptance and rollback token",
    )


def test_phase12a_failure_handling_model_is_documented() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "fail-closed missing implementation approval",
            "fail-closed missing runtime boundary evidence",
            "fail-closed missing security control evidence",
            "fail-closed missing rollback strategy",
            "fail-closed missing production candidate acceptance criteria",
            "no silent promotion readiness pass",
            "no warning-only bypass for protected approval gates",
            "explicit operator review requirement",
            "implementation approval does not equal production promotion approval",
            "production promotion approval remains deferred unless explicitly approved in a later phase",
        ),
        label="failure handling token",
    )


def test_phase12a_non_goals_and_runtime_exclusions_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 12a does not implement production runtime",
            "phase 12a does not approve production promotion",
            "phase 12a does not implement authentication runtime",
            "phase 12a does not implement rbac enforcement",
            "phase 12a does not implement key custody runtime",
            "phase 12a does not implement backend/api/database",
            "phase 12a does not implement production signing",
            "phase 12a does not implement verifier runtime",
            "phase 12a does not implement production policy engine",
            "phase 12a does not implement deployment runtime",
            "phase 12a does not implement production promotion automation",
            "production runtime",
            "github actions workflow",
            "ci/cd deployment pipeline",
            "vault client runtime",
        ),
        label="non-goal token",
    )


def test_phase12a_pointer_docs_reference_phase12a() -> None:
    for path in (ROADMAP, PROJECT_STATE, PHASE11G_DOC):
        low = _flat(path)
        _assert_all_tokens(
            low,
            (
                "phase 12a",
                "governed production candidate implementation plan",
            ),
            label=f"pointer token in {path.name}",
        )


def test_phase12a_forbidden_runtime_artifacts_are_absent() -> None:
    forbidden = [
        REPO_ROOT / "scripts/dev/run_phase12a_governed_production_candidate_implementation_plan.sh",
        REPO_ROOT / "scripts/dev/phase12a_governed_production_candidate_implementation_plan.py",
        REPO_ROOT / "scripts/dev/phase12a_authentication_runtime.py",
        REPO_ROOT / "scripts/dev/phase12a_signing_runtime.py",
        REPO_ROOT / ".github/workflows/phase12a-governed-production-candidate-implementation-plan.yml",
        REPO_ROOT / "deploy/phase12a-governed-production-candidate-implementation-plan.yaml",
        REPO_ROOT / "deploy/phase12a-governed-production-candidate-implementation-plan.yml",
        REPO_ROOT / "infra/phase12a-governed-production-candidate-implementation-plan.tf",
        REPO_ROOT / "keys/phase12a-production-signing.key",
        REPO_ROOT / "certs/phase12a-production-signing.crt",
    ]
    for path in forbidden:
        assert not path.exists(), f"unexpected Phase 12A runtime artifact: {path}"
