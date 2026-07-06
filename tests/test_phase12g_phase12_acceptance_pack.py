from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/093-phase12g-phase12-acceptance-pack.md"
DOC = REPO_ROOT / "docs/PHASE12G_PHASE12_ACCEPTANCE_PACK.md"
THIS_TEST = Path(__file__)

def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(_text(path).lower().replace("`", "").split())


def _assert_all_tokens(text: str, tokens: tuple[str, ...] | list[str], *, label: str) -> None:
    for token in tokens:
        assert token in text, f"missing {label}: {token}"


def _assert_phase12g_docs_present() -> None:
    for path in (TASK_FILE, DOC):
        assert path.is_file(), f"missing Phase 12G file: {path}"


def _rel_matches(pattern: str, *roots: Path) -> list[str]:
    matches: list[str] = []
    for root in roots:
        if not root.exists():
            continue
        matches.extend(
            str(path.relative_to(REPO_ROOT))
            for path in root.rglob(pattern)
            if path.is_file() and "__pycache__" not in path.relative_to(REPO_ROOT).parts
        )
    return sorted(set(matches))


def test_phase12g_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 12G file: {path}"


def test_phase12g_only_introduces_expected_phase_files() -> None:
    matches = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("*phase12g*")
        if path.is_file()
        and ".git" not in path.relative_to(REPO_ROOT).parts
        and "__pycache__" not in path.relative_to(REPO_ROOT).parts
    )
    assert matches == [
        "codex/tasks/093-phase12g-phase12-acceptance-pack.md",
        "tests/test_phase12g_phase12_acceptance_pack.py",
    ]


def test_phase12g_only_introduces_expected_planning_doc() -> None:
    matches = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("*PHASE12G*")
        if path.is_file()
        and "__pycache__" not in path.relative_to(REPO_ROOT).parts
    )
    assert matches == [
        "docs/PHASE12G_PHASE12_ACCEPTANCE_PACK.md",
    ]


def test_phase12g_required_canonical_wording_exists() -> None:
    _assert_phase12g_docs_present()
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "Phase 12G is the Phase 12 acceptance/readiness pack.",
            "Phase 12G does not implement production runtime.",
            "Phase 12G does not approve production promotion.",
            "Phase 12G does not grant implementation approval.",
            "Phase 12G does not bypass the Phase 7D selected-gate manual boundary.",
            "Phase 12G does not select or invent an approved runtime implementation target.",
            "Phase 12G verifies the Phase 12A through Phase 12F chain.",
            "Phase 12F defines controlled runtime implementation readiness.",
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


def test_phase12g_task_file_preserves_core_boundary_wording() -> None:
    _assert_phase12g_docs_present()
    text = _text(TASK_FILE)
    _assert_all_tokens(
        text,
        (
            "phase12g_status: success",
            "Phase 12G is the Phase 12 acceptance/readiness pack.",
            "Phase 12G does not implement production runtime.",
            "Phase 12G does not approve production promotion.",
            "Phase 12G does not grant implementation approval.",
            "Phase 12G does not bypass the Phase 7D selected-gate manual boundary.",
            "Phase 12G does not select or invent an approved runtime implementation target.",
            "Phase 12G verifies the Phase 12A through Phase 12F chain.",
            "Approval remains the Phase 7D selected-gate manual boundary.",
        ),
        label="task token",
    )


def test_phase12g_required_sections_exist() -> None:
    _assert_phase12g_docs_present()
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 12g purpose",
            "phase 12 acceptance position",
            "relationship to phase 12a, phase 12b, phase 12c, phase 12d, phase 12e, and phase 12f",
            "phase 12 chain summary",
            "phase 12a acceptance summary",
            "phase 12b acceptance summary",
            "phase 12c acceptance summary",
            "phase 12d acceptance summary",
            "phase 12e acceptance summary",
            "phase 12f acceptance summary",
            "full phase 12 boundary confirmation",
            "production runtime exclusion",
            "production promotion exclusion",
            "implementation approval exclusion",
            "approved runtime domain status",
            "phase 7d manual boundary preservation",
            "local-only prototype protection",
            "rbac advisory context confirmation",
            "runtime implementation target exclusion",
            "phase 12 acceptance matrix",
            "phase 12 boundary matrix",
            "phase 12 artifact matrix",
            "phase 12 risk and residual control matrix",
            "phase 12 verification matrix",
            "phase 12 non-goal matrix",
            "runtime capability exclusion matrix",
            "failure handling and escalation",
            "dependency and sequencing risks",
            "residual risk handling",
            "acceptance criteria",
            "safe demo scenarios",
            "operator checklist",
            "recommended next step",
            "recommended next major subphase",
        ),
        label="section",
    )


def test_phase12g_references_phase12a_through_phase12f_and_manual_boundary_language() -> None:
    _assert_phase12g_docs_present()
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 12a acceptance summary",
            "phase 12b acceptance summary",
            "phase 12c acceptance summary",
            "phase 12d acceptance summary",
            "phase 12e acceptance summary",
            "phase 12f acceptance summary",
            "governed production candidate implementation planning",
            "runtime boundary approval and implementation scope",
            "implementation approval evidence package requirements",
            "explicit runtime implementation approval gate",
            "approved runtime domain implementation preparation",
            "controlled runtime implementation readiness",
            "phase 12 acceptance remains readiness, not approval",
            "phase 11 acceptance remains readiness, not approval",
            "phase 10 acceptance remains readiness, not approval",
            "approval remains the phase 7d selected-gate manual boundary",
            "local-only prototypes remain local-only until governed promotion is explicitly approved",
            "rbac advisory context remains not enforcement",
        ),
        label="phase chain token",
    )


def test_phase12g_required_matrices_exist() -> None:
    _assert_phase12g_docs_present()
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "## 20. Phase 12 Acceptance Matrix",
            "| Phase | Purpose | Acceptance Status | Runtime Implementation Status | Production Promotion Status | Approval Boundary |",
            "## 21. Phase 12 Boundary Matrix",
            "| Boundary Area | Required Phase Reference | Preserved Constraint | Failure Condition | Required Operator Action |",
            "## 22. Phase 12 Artifact Matrix",
            "| Phase | Required Artifact | Required Status | Forbidden Artifact Type | Verification Method |",
            "## 23. Phase 12 Risk and Residual Control Matrix",
            "| Risk Area | Residual Constraint | Required Evidence | Failure Condition | Escalation Path |",
            "## 24. Phase 12 Verification Matrix",
            "| Verification Area | Required Check | Required Evidence | Fail-Closed Condition |",
            "## 25. Phase 12 Non-Goal Matrix",
            "| Non-Goal Area | Why It Remains Out of Scope | Required Preserved Wording |",
            "## 26. Runtime Capability Exclusion Matrix",
            "| Runtime Capability | Exclusion Status | Approval Requirement |",
        ),
        label="matrix token",
    )


def test_phase12g_failure_handling_tokens_exist() -> None:
    _assert_phase12g_docs_present()
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "fail-closed missing phase 12a through phase 12f chain evidence",
            "fail-closed missing phase boundary wording",
            "fail-closed missing acceptance matrix coverage",
            "fail-closed ambiguous runtime capability claim",
            "fail-closed ambiguous production promotion language",
            "fail-closed ambiguous implementation approval language",
            "fail-closed implicit runtime domain selection",
            "fail-closed missing manual boundary preservation",
            "no silent acceptance pass with missing chain evidence",
            "no warning-only bypass for readiness boundary gaps",
            "explicit operator review requirement",
            "acceptance/readiness does not equal runtime implementation",
            "acceptance/readiness does not equal implementation approval",
            "acceptance/readiness does not equal production promotion approval",
            "production promotion approval remains deferred unless explicitly approved in a later phase",
            "non-goals and forbidden implementations",
            "runtime implementation target selection",
            "implementation approval record",
        ),
        label="failure-handling token",
    )


def test_phase12g_does_not_introduce_forbidden_runtime_or_infra_artifacts() -> None:
    assert not _rel_matches("*phase12g*", REPO_ROOT / "scripts")
    assert not _rel_matches("*phase12g*", REPO_ROOT / "services")
    assert not _rel_matches("*phase12g*", REPO_ROOT / "api")
    assert not _rel_matches("*phase12g*", REPO_ROOT / "database")
    assert not _rel_matches("*phase12g*", REPO_ROOT / "deploy")
    assert not _rel_matches("*phase12g*", REPO_ROOT / ".github")
    assert not _rel_matches("*phase12g*", REPO_ROOT / "infra")
    assert not _rel_matches("*phase12g*", REPO_ROOT / "terraform")
    assert not _rel_matches("*phase12g*", REPO_ROOT / "helm")
    assert not _rel_matches("*phase12g*", REPO_ROOT / "k8s")


def test_phase12g_does_not_introduce_forbidden_keys_signing_or_approval_records() -> None:
    assert not _rel_matches("*phase12g*.pem", REPO_ROOT)
    assert not _rel_matches("*phase12g*.key", REPO_ROOT)
    assert not _rel_matches("*phase12g*.crt", REPO_ROOT)
    assert not _rel_matches("*phase12g*.cer", REPO_ROOT)
    assert not _rel_matches("*phase12g*.p12", REPO_ROOT)
    assert not _rel_matches("*phase12g*.pfx", REPO_ROOT)
    assert not _rel_matches("*phase12g*sign*", REPO_ROOT / "scripts", REPO_ROOT / "services", REPO_ROOT / "api")
    assert not _rel_matches("*phase12g*verif*", REPO_ROOT / "scripts", REPO_ROOT / "services", REPO_ROOT / "api")
    assert not _rel_matches("*phase12g*vault*", REPO_ROOT / "scripts", REPO_ROOT / "services", REPO_ROOT / "api")
    assert not _rel_matches("*phase12g*approval*", REPO_ROOT / "records", REPO_ROOT / "artifacts", REPO_ROOT / "approvals")


def test_phase12g_repository_guards_cover_shell_runtime_and_workflow_artifacts() -> None:
    assert not _rel_matches("*phase12g*.sh", REPO_ROOT)
    assert not _rel_matches("*phase12g*.bash", REPO_ROOT)
    assert not _rel_matches("*phase12g*runner*", REPO_ROOT)
    assert not _rel_matches("*phase12g*runtime*", REPO_ROOT / "scripts", REPO_ROOT / "services", REPO_ROOT / "api")
    assert not _rel_matches("*phase12g*workflow*", REPO_ROOT / ".github")


def test_phase12g_required_closing_sections_and_runtime_exclusions_exist() -> None:
    _assert_phase12g_docs_present()
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "## 27. Acceptance Criteria",
            "Phase 12G is the Phase 12 acceptance/readiness pack.",
            "Phase 12G verifies the Phase 12A through Phase 12F chain.",
            "Phase 12G remains acceptance/readiness only.",
            "## 28. Safe Demo Scenarios",
            "Review the Phase 12A through Phase 12G documents locally to confirm the chain remains docs/tests only.",
            "Run the focused Phase 12G docs-contract test and confirm boundary wording remains unchanged.",
            "## 29. Operator Checklist",
            "confirm the Phase 12A through Phase 12G document chain is present",
            "confirm no runtime implementation was introduced",
            "confirm no implementation approval record was introduced",
            "confirm no production promotion approval was introduced",
            "## Recommended Next Step",
            "Complete Phase 12G PR readiness",
            "## Recommended Next Major Subphase",
            "Phase 13",
            "production runtime",
            "backend/API/database",
            "GitHub Actions workflow",
            "implementation approval",
            "runtime implementation",
            "production promotion approval",
        ),
        label="closing token",
    )
