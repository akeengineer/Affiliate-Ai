from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = (
    REPO_ROOT
    / "codex/tasks/095-phase14-selected-runtime-domain-implementation-plan-blocked.md"
)
DOC = REPO_ROOT / "docs/PHASE14_SELECTED_RUNTIME_DOMAIN_IMPLEMENTATION_PLAN_BLOCKED.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE13_DOC = (
    REPO_ROOT
    / "docs/PHASE13_EXPLICIT_IMPLEMENTATION_APPROVAL_RECORD_AND_RUNTIME_DOMAIN_SELECTION.md"
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(_text(path).lower().replace("`", "").split())


def _assert_all_tokens(text: str, tokens: tuple[str, ...] | list[str], *, label: str) -> None:
    for token in tokens:
        assert token in text, f"missing {label}: {token}"


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


def test_phase14_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 14 file: {path}"


def test_phase14_only_introduces_expected_phase_files() -> None:
    matches = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("*phase14*")
        if path.is_file()
        and ".git" not in path.relative_to(REPO_ROOT).parts
        and "__pycache__" not in path.relative_to(REPO_ROOT).parts
    )
    assert matches == [
        "codex/tasks/095-phase14-selected-runtime-domain-implementation-plan-blocked.md",
        "tests/test_phase14_selected_runtime_domain_implementation_plan_blocked.py",
    ]


def test_phase14_only_introduces_expected_doc() -> None:
    matches = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("*PHASE14*")
        if path.is_file() and "__pycache__" not in path.relative_to(REPO_ROOT).parts
    )
    assert matches == [
        "docs/PHASE14_SELECTED_RUNTIME_DOMAIN_IMPLEMENTATION_PLAN_BLOCKED.md",
    ]


def test_phase14_required_canonical_wording_exists() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "Phase 14 documents the blocked selected runtime domain implementation planning state.",
            "Phase 14 is blocked because Phase 13 did not record explicit operator approval for exactly one runtime domain.",
            "Phase 14 does not select or infer a runtime domain.",
            "Phase 14 does not auto-select a runtime domain.",
            "Phase 14 does not grant implementation approval.",
            "Phase 14 does not implement production runtime.",
            "Phase 14 does not approve production promotion.",
            "Phase 14 does not bypass the Phase 7D selected-gate manual boundary.",
            "Phase 14 treats missing or ambiguous runtime domain approval as fail-closed.",
            "Runtime Domain Selection Status: not selected",
            "Implementation Approval Status: not granted",
            "Production Promotion Status: not approved",
            "Approval Record Status: pending explicit operator approval",
            "Phase 13 defines the explicit implementation approval record and runtime domain selection process.",
            "Phase 13 does not implement production runtime by default.",
            "Phase 13 does not approve production promotion.",
            "Phase 13 does not auto-select a runtime domain.",
            "Phase 13 does not infer implementation approval from Phase 12 acceptance.",
            "Phase 12G is the Phase 12 acceptance/readiness pack.",
            "Phase 12G does not grant implementation approval.",
            "Phase 12G does not approve production promotion.",
            "Phase 12 acceptance does not equal implementation approval.",
            "Phase 12 acceptance does not equal production promotion approval.",
            "Approved Runtime Domain remains pending explicit Phase 12D approval.",
            "Approval remains the Phase 7D selected-gate manual boundary.",
            "Production authentication, RBAC enforcement, key custody, backend/API/database, production signing, verifier runtime, and production policy engine remain out of scope unless explicitly approved.",
        ),
        label="canonical wording",
    )


def test_phase14_task_file_preserves_core_boundary_wording() -> None:
    text = _text(TASK_FILE)
    _assert_all_tokens(
        text,
        (
            "phase14_status: blocked_planning_only",
            "Phase 14 documents the blocked selected runtime domain implementation planning state.",
            "Phase 14 is blocked because Phase 13 did not record explicit operator approval for exactly one runtime domain.",
            "Phase 14 does not select or infer a runtime domain.",
            "Phase 14 does not auto-select a runtime domain.",
            "Phase 14 does not grant implementation approval.",
            "Phase 14 does not implement production runtime.",
            "Phase 14 does not approve production promotion.",
            "Phase 14 does not bypass the Phase 7D selected-gate manual boundary.",
            "Phase 14 treats missing or ambiguous runtime domain approval as fail-closed.",
            "Phase 14 Status: blocked / planning-only",
            "Approval remains the Phase 7D selected-gate manual boundary.",
        ),
        label="task token",
    )


def test_phase14_required_sections_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 14 purpose",
            "phase 14 blocked position",
            "relationship to phase 13",
            "relationship to phase 12g",
            "blocked runtime domain selection state",
            "default approval state",
            "no runtime domain selection",
            "no implementation approval",
            "no production promotion approval",
            "manual approval boundary preservation",
            "fail-closed blocking model",
            "required operator approval to unblock",
            "single-domain approval requirement",
            "explicit approval wording requirement",
            "blocked implementation planning scope",
            "runtime domain candidate status",
            "runtime domain selection blocker matrix",
            "phase 13 state carry-forward matrix",
            "approval requirement matrix",
            "runtime capability exclusion matrix",
            "unblock criteria matrix",
            "blocking condition matrix",
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


def test_phase14_required_blocked_state_and_unblock_wording_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "Phase 14 Status: blocked / planning-only",
            "I explicitly approve selecting `<runtime domain>` as the one runtime domain for future implementation planning only. This does not approve production promotion. This does not approve production runtime deployment. This does not bypass the Phase 7D selected-gate manual boundary.",
            "If this explicit wording is absent, Phase 14 remains blocked.",
        ),
        label="blocked state token",
    )


def test_phase14_required_matrices_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "## 17. Runtime Domain Selection Blocker Matrix",
            "| Runtime Domain Candidate | Phase 13 Selection Status | Phase 14 Planning Status | Blocking Condition | Required Operator Approval | Production Promotion Status |",
            "## 18. Phase 13 State Carry-Forward Matrix",
            "| Phase 13 Field | Phase 13 Value | Phase 14 Interpretation | Planning Impact | Required Resolution | Fail-Closed Behavior |",
            "## 19. Approval Requirement Matrix",
            "| Requirement | Required Evidence | Required Operator Wording | Blocking Condition | Phase 14 Status | Production Promotion Impact |",
            "## 20. Runtime Capability Exclusion Matrix",
            "| Runtime Capability | Phase 14 Position | Required Future Approval | Current Status | Blocking Condition |",
            "## 21. Unblock Criteria Matrix",
            "| Unblock Criterion | Required Source | Required Evidence | Required Operator Approval | Blocking Condition | Phase 14 Outcome |",
            "## 22. Blocking Condition Matrix",
            "| Blocking Condition | Affected Planning Area | Required Resolution | Required Reviewer | Gate Outcome | Production Promotion Impact |",
        ),
        label="matrix token",
    )


def test_phase14_runtime_domain_candidate_status_is_documented() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "authentication runtime",
            "rbac enforcement runtime",
            "backend/api/database runtime",
            "production signing runtime",
            "verifier runtime",
            "key custody runtime",
            "production policy engine runtime",
            "observability runtime",
            "audit storage runtime",
            "backup/restore runtime",
            "deployment runtime",
            "ci/cd runtime",
            "not selected / blocked by default",
            "ci/cd runtime remains out of scope / deferred by default unless explicitly approved in a later phase",
        ),
        label="runtime domain token",
    )


def test_phase14_fail_closed_model_is_documented() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "fail-closed if phase 13 approval record is pending",
            "fail-closed if runtime domain selection is not selected",
            "fail-closed if implementation approval is not granted",
            "fail-closed if operator approval is missing",
            "fail-closed if operator approval is ambiguous",
            "fail-closed if multiple runtime domains are selected",
            "fail-closed if selected runtime domain is inferred",
            "fail-closed if production promotion is inferred from planning",
            "fail-closed if phase 7d selected-gate manual boundary is bypassed",
            "fail-closed if ci/cd runtime is treated as selected by default",
            "no silent runtime domain selection",
            "no silent implementation approval",
            "no warning-only bypass for blocked planning",
            "explicit operator approval required to unblock",
            "blocked planning does not equal runtime implementation",
            "blocked planning does not equal production promotion approval",
            "production promotion approval remains deferred unless explicitly approved in a later phase",
        ),
        label="fail-closed token",
    )


def test_phase14_non_goals_and_forbidden_implementations_are_documented() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 14 is blocked selected-runtime-domain implementation planning documentation only",
            "production runtime",
            "authentication runtime",
            "login/session/user store",
            "rbac enforcement",
            "production policy engine",
            "backend/api/database",
            "database schema",
            "api server",
            "network service",
            "deployment manifest",
            "cloud infrastructure",
            "github actions workflow",
            "ci/cd deployment pipeline",
            "production promotion automation",
            "production rollback automation",
            "production disaster recovery runtime",
            "production secrets",
            "key files",
            "certificate files",
            "vault write",
            "vault client runtime",
            "key rotation runtime",
            "revocation runtime",
            "signing runtime",
            "logging runtime",
            "metrics runtime",
            "tracing runtime",
            "siem integration",
            "backup runtime",
            "restore runtime",
            "primitive execution",
            "export mutation",
            "re-signing",
            "production authorization",
            "implementation approval",
            "runtime implementation",
            "production promotion approval",
            "selected runtime implementation plan for a specific runtime domain",
        ),
        label="non-goal token",
    )


def test_phase14_pointer_docs_reference_phase14() -> None:
    for path in (ROADMAP, PROJECT_STATE, PHASE13_DOC):
        low = _flat(path)
        _assert_all_tokens(
            low,
            (
                "phase 14",
                "selected runtime domain implementation plan blocked",
            ),
            label=f"pointer token in {path.name}",
        )

    _assert_all_tokens(
        _flat(PHASE13_DOC),
        (
            "phase 14 should document the blocked selected runtime domain implementation planning state if phase 13 does not record explicit operator approval for exactly one runtime domain",
            "phase 14 should not select or infer a runtime domain",
            "phase 14 should remain blocked",
        ),
        label="phase13 forward pointer token",
    )


def test_phase14_recommended_next_step_and_next_major_subphase_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "## Recommended Next Step",
            "Complete Phase 14 PR readiness",
            "- run focused checks",
            "- run full suite",
            "- confirm clean worktree",
            "- push feature/phase14-selected-runtime-domain-implementation-plan-blocked",
            "- open one PR for Phase 14",
            "- wait for CI green",
            "- squash merge",
            "- sync main",
            "- delete feature branch",
            "## Recommended Next Major Subphase",
            "Phase 15 — Explicit Single Runtime Domain Approval",
            "Phase 15 should record explicit operator approval for exactly one runtime domain before any selected runtime domain implementation plan is created. Phase 15 should not implement production runtime by default, approve production promotion, or bypass the Phase 7D selected-gate manual boundary unless explicitly approved. If explicit operator approval is missing, ambiguous, or selects multiple runtime domains, Phase 15 must remain fail-closed.",
        ),
        label="next-step token",
    )


def test_phase14_forbidden_runtime_artifacts_are_absent() -> None:
    assert not _rel_matches("*phase14*", REPO_ROOT / "scripts")
    assert not _rel_matches("*phase14*", REPO_ROOT / "services")
    assert not _rel_matches("*phase14*", REPO_ROOT / "api")
    assert not _rel_matches("*phase14*", REPO_ROOT / "database")
    assert not _rel_matches("*phase14*", REPO_ROOT / ".github" / "workflows")
    assert not _rel_matches("*phase14*", REPO_ROOT / "deploy")
    assert not _rel_matches("*phase14*", REPO_ROOT / "infra")
    assert not _rel_matches("*phase14*", REPO_ROOT / "keys")
    assert not _rel_matches("*phase14*", REPO_ROOT / "certs")
