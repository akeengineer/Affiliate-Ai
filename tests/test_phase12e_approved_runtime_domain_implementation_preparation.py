from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/091-phase12e-approved-runtime-domain-implementation-preparation.md"
DOC = REPO_ROOT / "docs/PHASE12E_APPROVED_RUNTIME_DOMAIN_IMPLEMENTATION_PREPARATION.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE12D_DOC = REPO_ROOT / "docs/PHASE12D_EXPLICIT_RUNTIME_IMPLEMENTATION_APPROVAL_GATE.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(_text(path).lower().replace("`", "").split())


def _assert_all_tokens(text: str, tokens: tuple[str, ...] | list[str], *, label: str) -> None:
    for token in tokens:
        assert token in text, f"missing {label}: {token}"


def test_phase12e_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 12E file: {path}"


def test_phase12e_only_introduces_expected_phase_files() -> None:
    matches = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("*phase12e*")
        if path.is_file()
        and ".git" not in path.relative_to(REPO_ROOT).parts
        and "__pycache__" not in path.relative_to(REPO_ROOT).parts
    )
    assert matches == [
        "codex/tasks/091-phase12e-approved-runtime-domain-implementation-preparation.md",
        "tests/test_phase12e_approved_runtime_domain_implementation_preparation.py",
    ]


def test_phase12e_only_introduces_expected_planning_doc() -> None:
    matches = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("*PHASE12E*")
        if path.is_file()
        and "__pycache__" not in path.relative_to(REPO_ROOT).parts
    )
    assert matches == [
        "docs/PHASE12E_APPROVED_RUNTIME_DOMAIN_IMPLEMENTATION_PREPARATION.md",
    ]


def test_phase12e_required_canonical_wording_exists() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "Phase 12E defines approved runtime domain implementation preparation.",
            "Phase 12E does not implement production runtime.",
            "Phase 12E does not approve production promotion.",
            "Phase 12E does not bypass the Phase 7D selected-gate manual boundary.",
            "Phase 12E does not implement authentication runtime.",
            "Phase 12E does not implement RBAC enforcement.",
            "Phase 12E does not implement key custody runtime.",
            "Phase 12E does not implement backend/API/database.",
            "Phase 12E does not implement production signing.",
            "Phase 12E does not implement verifier runtime.",
            "Phase 12E does not implement production policy engine.",
            "Phase 12E does not implement deployment runtime.",
            "Phase 12E does not implement production promotion automation.",
            "Phase 12D defines the explicit runtime implementation approval gate.",
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


def test_phase12e_task_file_preserves_core_boundary_wording() -> None:
    text = _text(TASK_FILE)
    _assert_all_tokens(
        text,
        (
            "phase12e_status: success",
            "Phase 12E defines approved runtime domain implementation preparation.",
            "Phase 12E does not implement production runtime.",
            "Phase 12E does not approve production promotion.",
            "Phase 12E does not bypass the Phase 7D selected-gate manual boundary.",
            "Approval remains the Phase 7D selected-gate manual boundary.",
        ),
        label="task token",
    )


def test_phase12e_required_sections_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 12e purpose",
            "relationship to phase 12a, phase 12b, phase 12c, and phase 12d",
            "approved runtime domain preparation scope",
            "approved runtime domain status",
            "implementation preparation boundary",
            "runtime domain selection constraints",
            "implementation preparation artifacts",
            "runtime boundary constraints",
            "required control preparation",
            "security control preparation",
            "ci test strategy preparation",
            "observability preparation",
            "audit evidence preparation",
            "secrets and key custody preparation",
            "backup and recovery preparation",
            "rollback preparation",
            "operator approval checkpoints",
            "implementation readiness criteria",
            "implementation non-goals",
            "runtime domain preparation matrix",
            "control-to-preparation mapping",
            "evidence-to-preparation mapping",
            "rollback-to-implementation mapping",
            "test strategy matrix",
            "failure handling and escalation",
            "dependency and sequencing risks",
            "residual risk handling",
            "manual approval boundary preservation",
            "local-only prototype protection",
            "production promotion exclusion",
            "non-goals and forbidden implementations",
            "acceptance criteria",
            "safe demo scenarios",
            "operator checklist",
            "recommended next step",
            "recommended next major subphase",
        ),
        label="section",
    )


def test_phase12e_references_prior_phases_and_manual_boundary_language() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 12d defines the explicit runtime implementation approval gate",
            "phase 12c defines implementation approval evidence package requirements",
            "phase 12b defines runtime boundary approval and implementation scope",
            "phase 12a defines governed production candidate implementation planning",
            "phase 11 acceptance remains readiness, not approval",
            "phase 10 acceptance remains readiness, not approval",
            "approval remains the phase 7d selected-gate manual boundary",
            "local-only prototypes remain local-only until governed promotion is explicitly approved",
            "rbac advisory context remains not enforcement",
        ),
        label="prior phase reference token",
    )


def test_phase12e_status_boundary_selection_and_artifacts_are_documented() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "approved runtime domain: pending explicit phase 12d approval",
            "if the status is not approved for future implementation phase, phase 12e remains a preparation template and does not select a runtime implementation target",
            "implementation preparation boundary",
            "runtime domain selection constraints",
            "implementation scope statement",
            "runtime boundary constraints",
            "explicit non-goals",
            "required control checklist",
            "security test plan",
            "ci test plan",
            "observability plan",
            "audit evidence plan",
            "secrets/key custody dependency note",
            "rollback plan",
            "operator checkpoint list",
            "implementation readiness attestation",
            "production promotion exclusion statement",
        ),
        label="preparation artifact token",
    )


def test_phase12e_runtime_boundary_and_control_preparation_are_documented() -> None:
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
            "ci/cd boundary",
            "rollback boundary",
            "production promotion boundary",
            "required control preparation",
            "security control preparation",
            "ci test strategy preparation",
            "observability preparation",
            "audit evidence preparation",
            "secrets and key custody preparation",
            "backup and recovery preparation",
            "rollback preparation",
            "operator approval checkpoints",
            "implementation readiness criteria",
        ),
        label="boundary preparation token",
    )


def test_phase12e_required_mapping_tables_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "## Runtime Domain Preparation Matrix",
            "| Runtime Domain | Phase 12D Gate Status | Preparation Scope | Required Controls | Implementation Readiness Status | Production Promotion Status |",
            "## Control-to-Preparation Mapping",
            "| Required Control | Related Runtime Domain | Preparation Artifact | Required Evidence | Blocking Condition | Deferred Implementation Phase |",
            "## Evidence-to-Preparation Mapping",
            "| Evidence Type | Related Preparation Artifact | Required Reviewer | Freshness Requirement | Integrity Requirement | Blocking Condition |",
            "## Rollback-to-Implementation Mapping",
            "| Rollback Requirement | Related Runtime Domain | Required Preparation Artifact | Validation Requirement | Operator Checkpoint | Production Promotion Impact |",
            "## Test Strategy Matrix",
            "| Test Area | Required Test Strategy | Related Runtime Domain | Required Evidence | Blocking Condition | Deferred Implementation Phase |",
        ),
        label="mapping table token",
    )


def test_phase12e_failure_handling_model_and_non_goals_are_documented() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "fail-closed missing phase 12d approval status",
            "fail-closed ambiguous runtime domain selection",
            "fail-closed missing preparation artifact",
            "fail-closed missing required controls",
            "fail-closed missing rollback preparation",
            "fail-closed missing test strategy",
            "fail-closed missing observability preparation",
            "fail-closed missing operator checkpoint",
            "no silent runtime implementation preparation pass",
            "no warning-only bypass for preparation gaps",
            "explicit operator review requirement",
            "implementation preparation does not equal runtime implementation",
            "implementation preparation does not equal production promotion approval",
            "production promotion approval remains deferred unless explicitly approved in a later phase",
            "implementation non-goals",
            "production promotion exclusion",
            "non-goals and forbidden implementations",
            "ci/cd runtime",
            "runtime implementation",
        ),
        label="failure-handling token",
    )


def test_phase12e_next_step_and_next_major_subphase_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "## Recommended Next Step",
            "Complete Phase 12E PR readiness",
            "- run focused checks",
            "- run full suite",
            "- confirm clean worktree",
            "- push feature/phase12e-approved-runtime-domain-implementation-preparation",
            "- open one PR for Phase 12E",
            "- wait for CI green",
            "- squash merge",
            "- sync main",
            "- delete feature branch",
            "## Recommended Next Major Subphase",
            "Phase 12F — Controlled Runtime Implementation Readiness Pack",
            "Phase 12F should convert the Phase 12E preparation artifacts into a controlled runtime implementation readiness pack for a later explicitly approved implementation phase. Phase 12F should not implement production runtime, approve production promotion, or bypass the Phase 7D selected-gate manual boundary unless explicitly approved. Phase 12F should verify implementation scope, required controls, test strategy, rollback expectations, observability requirements, evidence requirements, and operator approval checkpoints before any runtime code is introduced.",
        ),
        label="next step token",
    )


def test_phase12e_pointer_docs_reference_phase12e() -> None:
    _assert_all_tokens(
        _text(ROADMAP),
        (
            "Phase 12E — Approved Runtime Domain Implementation Preparation",
            "docs/PHASE12E_APPROVED_RUNTIME_DOMAIN_IMPLEMENTATION_PREPARATION.md",
        ),
        label="roadmap token",
    )
    _assert_all_tokens(
        _text(PROJECT_STATE),
        (
            "Phase 12E approved runtime domain implementation preparation",
            "docs/PHASE12E_APPROVED_RUNTIME_DOMAIN_IMPLEMENTATION_PREPARATION.md",
        ),
        label="project state token",
    )
    _assert_all_tokens(
        _text(PHASE12D_DOC),
        (
            "Phase 12E — Approved Runtime Domain Implementation Preparation",
            "Phase 12E should prepare the first explicitly approved runtime domain for implementation in a later controlled phase.",
        ),
        label="phase12d pointer token",
    )


def test_phase12e_does_not_introduce_runner_runtime_or_forbidden_phase_files() -> None:
    assert not list((REPO_ROOT / "scripts").rglob("*phase12e*"))
    assert not list((REPO_ROOT / ".github").rglob("*phase12e*"))
    assert not list((REPO_ROOT / "services").rglob("*phase12e*"))
    assert not list((REPO_ROOT / "api").rglob("*phase12e*"))
    assert not list((REPO_ROOT / "database").rglob("*phase12e*"))
    assert not list((REPO_ROOT / "deploy").rglob("*phase12e*"))

