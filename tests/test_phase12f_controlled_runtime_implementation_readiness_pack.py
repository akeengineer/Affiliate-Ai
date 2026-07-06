from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/092-phase12f-controlled-runtime-implementation-readiness-pack.md"
DOC = REPO_ROOT / "docs/PHASE12F_CONTROLLED_RUNTIME_IMPLEMENTATION_READINESS_PACK.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE12E_DOC = REPO_ROOT / "docs/PHASE12E_APPROVED_RUNTIME_DOMAIN_IMPLEMENTATION_PREPARATION.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(_text(path).lower().replace("`", "").split())


def _assert_all_tokens(text: str, tokens: tuple[str, ...] | list[str], *, label: str) -> None:
    for token in tokens:
        assert token in text, f"missing {label}: {token}"


def test_phase12f_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 12F file: {path}"


def test_phase12f_only_introduces_expected_phase_files() -> None:
    matches = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("*phase12f*")
        if path.is_file()
        and ".git" not in path.relative_to(REPO_ROOT).parts
        and "__pycache__" not in path.relative_to(REPO_ROOT).parts
    )
    assert matches == [
        "codex/tasks/092-phase12f-controlled-runtime-implementation-readiness-pack.md",
        "tests/test_phase12f_controlled_runtime_implementation_readiness_pack.py",
    ]


def test_phase12f_only_introduces_expected_planning_doc() -> None:
    matches = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("*PHASE12F*")
        if path.is_file()
        and "__pycache__" not in path.relative_to(REPO_ROOT).parts
    )
    assert matches == [
        "docs/PHASE12F_CONTROLLED_RUNTIME_IMPLEMENTATION_READINESS_PACK.md",
    ]


def test_phase12f_required_canonical_wording_exists() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "Phase 12F defines controlled runtime implementation readiness.",
            "Phase 12F does not implement production runtime.",
            "Phase 12F does not approve production promotion.",
            "Phase 12F does not bypass the Phase 7D selected-gate manual boundary.",
            "Phase 12F does not implement authentication runtime.",
            "Phase 12F does not implement RBAC enforcement.",
            "Phase 12F does not implement key custody runtime.",
            "Phase 12F does not implement backend/API/database.",
            "Phase 12F does not implement production signing.",
            "Phase 12F does not implement verifier runtime.",
            "Phase 12F does not implement production policy engine.",
            "Phase 12F does not implement deployment runtime.",
            "Phase 12F does not implement production promotion automation.",
            "Phase 12E defines approved runtime domain implementation preparation.",
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


def test_phase12f_task_file_preserves_core_boundary_wording() -> None:
    text = _text(TASK_FILE)
    _assert_all_tokens(
        text,
        (
            "phase12f_status: success",
            "Phase 12F defines controlled runtime implementation readiness.",
            "Phase 12F does not implement production runtime.",
            "Phase 12F does not approve production promotion.",
            "Phase 12F does not bypass the Phase 7D selected-gate manual boundary.",
            "Approval remains the Phase 7D selected-gate manual boundary.",
        ),
        label="task token",
    )


def test_phase12f_required_sections_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 12f purpose",
            "relationship to phase 12a, phase 12b, phase 12c, phase 12d, and phase 12e",
            "controlled runtime implementation readiness scope",
            "approved runtime domain status",
            "runtime implementation readiness boundary",
            "runtime domain selection constraints",
            "implementation scope verification",
            "required control verification",
            "security control readiness",
            "ci test strategy readiness",
            "observability readiness",
            "audit evidence readiness",
            "secrets and key custody readiness",
            "backup and recovery readiness",
            "rollback readiness",
            "deployment readiness exclusion",
            "production promotion exclusion",
            "operator approval checkpoints",
            "implementation readiness blockers",
            "runtime readiness matrix",
            "control readiness matrix",
            "test strategy readiness matrix",
            "evidence readiness matrix",
            "rollback readiness matrix",
            "operator checkpoint matrix",
            "failure handling and escalation",
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


def test_phase12f_references_prior_phases_and_manual_boundary_language() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 12e defines approved runtime domain implementation preparation",
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


def test_phase12f_status_scope_verification_and_selection_constraints_are_documented() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "approved runtime domain: pending explicit phase 12d approval",
            "if the status is not preparation-ready for future implementation phase, the document must state that phase 12f remains a generic readiness pack and does not select a runtime implementation target",
            "controlled runtime implementation readiness scope",
            "runtime implementation readiness boundary",
            "runtime domain selection constraints",
            "implementation scope statement",
            "runtime boundary constraints",
            "explicit non-goals",
            "required control checklist",
            "security test strategy",
            "ci test strategy",
            "observability expectations",
            "audit evidence expectations",
            "secrets/key custody dependencies",
            "backup/recovery dependencies",
            "rollback expectations",
            "operator approval checkpoints",
            "production promotion exclusion statement",
        ),
        label="readiness scope token",
    )


def test_phase12f_readiness_and_blocker_areas_are_documented() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "required control verification",
            "security control readiness",
            "ci test strategy readiness",
            "observability readiness",
            "audit evidence readiness",
            "secrets and key custody readiness",
            "backup and recovery readiness",
            "rollback readiness",
            "deployment readiness exclusion",
            "production promotion exclusion",
            "operator approval checkpoints",
            "implementation readiness blockers",
            "authentication runtime",
            "authorization/rbac runtime",
            "policy engine runtime",
            "backend/api runtime",
            "database/storage runtime",
            "signing runtime",
            "verifier runtime",
            "secrets/key custody runtime",
            "observability runtime",
            "audit storage runtime",
            "backup/restore runtime",
            "deployment runtime",
            "ci/cd runtime",
            "rollback automation",
            "production promotion automation",
            "ci/cd runtime remains out of scope / deferred by default unless explicitly approved in a later phase",
        ),
        label="readiness blocker token",
    )


def test_phase12f_required_readiness_matrices_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "## Runtime Readiness Matrix",
            "| Runtime Domain | Phase 12E Preparation Status | Readiness Scope | Required Controls | Readiness Status | Production Promotion Status |",
            "## Control Readiness Matrix",
            "| Required Control | Related Runtime Domain | Readiness Evidence | Blocking Condition | Required Operator Action | Deferred Implementation Phase |",
            "## Test Strategy Readiness Matrix",
            "| Test Area | Required Test Strategy | Related Runtime Domain | Required Evidence | Blocking Condition | Deferred Implementation Phase |",
            "## Evidence Readiness Matrix",
            "| Evidence Type | Related Readiness Area | Required Reviewer | Freshness Requirement | Integrity Requirement | Blocking Condition |",
            "## Rollback Readiness Matrix",
            "| Rollback Requirement | Related Runtime Domain | Readiness Evidence | Validation Requirement | Operator Checkpoint | Production Promotion Impact |",
            "## Operator Checkpoint Matrix",
            "| Operator Checkpoint | Required Evidence | Related Runtime Domain | Blocking Condition | Approval Boundary | Escalation Path |",
        ),
        label="readiness matrix token",
    )


def test_phase12f_failure_handling_model_and_non_goals_are_documented() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "fail-closed missing phase 12d approval status",
            "fail-closed missing phase 12e preparation status",
            "fail-closed ambiguous runtime domain selection",
            "fail-closed missing implementation scope",
            "fail-closed missing required controls",
            "fail-closed missing test strategy",
            "fail-closed missing rollback readiness",
            "fail-closed missing observability readiness",
            "fail-closed missing operator checkpoint",
            "fail-closed production promotion ambiguity",
            "no silent runtime readiness pass",
            "no warning-only bypass for readiness gaps",
            "explicit operator review requirement",
            "implementation readiness does not equal runtime implementation",
            "implementation readiness does not equal production promotion approval",
            "production promotion approval remains deferred unless explicitly approved in a later phase",
            "non-goals and forbidden implementations",
            "runtime implementation",
            "ci/cd runtime",
        ),
        label="failure-handling token",
    )


def test_phase12f_next_step_and_next_major_subphase_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "## Recommended Next Step",
            "Complete Phase 12F PR readiness",
            "- run focused checks",
            "- run full suite",
            "- confirm clean worktree",
            "- push feature/phase12f-controlled-runtime-implementation-readiness-pack",
            "- open one PR for Phase 12F",
            "- wait for CI green",
            "- squash merge",
            "- sync main",
            "- delete feature branch",
            "## Recommended Next Major Subphase",
            "Phase 12G — Phase 12 Acceptance Pack",
            "Phase 12G should summarize and verify the full Phase 12 planning, approval-scope, evidence-package, approval-gate, implementation-preparation, and controlled-readiness chain. Phase 12G should remain an acceptance/readiness pack only. Phase 12G should not implement production runtime, approve production promotion, grant implementation approval, or bypass the Phase 7D selected-gate manual boundary unless explicitly approved in a later phase.",
        ),
        label="next step token",
    )


def test_phase12f_pointer_docs_reference_phase12f() -> None:
    _assert_all_tokens(
        _text(ROADMAP),
        (
            "Phase 12F — Controlled Runtime Implementation Readiness Pack",
            "docs/PHASE12F_CONTROLLED_RUNTIME_IMPLEMENTATION_READINESS_PACK.md",
        ),
        label="roadmap token",
    )
    _assert_all_tokens(
        _text(PROJECT_STATE),
        (
            "Phase 12F controlled runtime implementation readiness pack",
            "docs/PHASE12F_CONTROLLED_RUNTIME_IMPLEMENTATION_READINESS_PACK.md",
        ),
        label="project state token",
    )
    _assert_all_tokens(
        _text(PHASE12E_DOC),
        (
            "Phase 12F — Controlled Runtime Implementation Readiness Pack",
            "Phase 12F should convert the Phase 12E preparation artifacts into a controlled runtime implementation readiness pack for a later explicitly approved implementation phase.",
        ),
        label="phase12e pointer token",
    )


def test_phase12f_does_not_introduce_runner_runtime_or_forbidden_phase_files() -> None:
    assert not list((REPO_ROOT / "scripts").rglob("*phase12f*"))
    assert not list((REPO_ROOT / ".github").rglob("*phase12f*"))
    assert not list((REPO_ROOT / "services").rglob("*phase12f*"))
    assert not list((REPO_ROOT / "api").rglob("*phase12f*"))
    assert not list((REPO_ROOT / "database").rglob("*phase12f*"))
    assert not list((REPO_ROOT / "deploy").rglob("*phase12f*"))
