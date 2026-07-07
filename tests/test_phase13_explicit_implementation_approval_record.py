from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/094-phase13-explicit-implementation-approval-record.md"
DOC = (
    REPO_ROOT
    / "docs/PHASE13_EXPLICIT_IMPLEMENTATION_APPROVAL_RECORD_AND_RUNTIME_DOMAIN_SELECTION.md"
)
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE12G_DOC = REPO_ROOT / "docs/PHASE12G_PHASE12_ACCEPTANCE_PACK.md"


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


def test_phase13_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 13 file: {path}"


def test_phase13_only_introduces_expected_phase_files() -> None:
    matches = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("*phase13*")
        if path.is_file()
        and ".git" not in path.relative_to(REPO_ROOT).parts
        and "__pycache__" not in path.relative_to(REPO_ROOT).parts
    )
    assert matches == [
        "codex/tasks/094-phase13-explicit-implementation-approval-record.md",
        "tests/test_phase13_explicit_implementation_approval_record.py",
    ]


def test_phase13_only_introduces_expected_doc() -> None:
    matches = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("*PHASE13*")
        if path.is_file() and "__pycache__" not in path.relative_to(REPO_ROOT).parts
    )
    assert matches == [
        "docs/PHASE13_EXPLICIT_IMPLEMENTATION_APPROVAL_RECORD_AND_RUNTIME_DOMAIN_SELECTION.md",
    ]


def test_phase13_required_canonical_wording_exists() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "Phase 13 defines the explicit implementation approval record and runtime domain selection process.",
            "Phase 13 does not implement production runtime by default.",
            "Phase 13 does not approve production promotion.",
            "Phase 13 does not bypass the Phase 7D selected-gate manual boundary.",
            "Phase 13 does not auto-select a runtime domain.",
            "Phase 13 does not infer implementation approval from Phase 12 acceptance.",
            "Phase 13 does not infer production promotion approval from implementation approval.",
            "Phase 13 treats missing or ambiguous approval as fail-closed.",
            "Runtime Domain Selection Status: not selected",
            "Implementation Approval Status: not granted",
            "Production Promotion Status: not approved",
            "Approval Record Status: pending explicit operator approval",
            "Phase 12G is the Phase 12 acceptance/readiness pack.",
            "Phase 12G does not grant implementation approval.",
            "Phase 12G does not approve production promotion.",
            "Phase 12G does not select or invent an approved runtime implementation target.",
            "Phase 12 acceptance does not equal implementation approval.",
            "Phase 12 acceptance does not equal production promotion approval.",
            "Approved Runtime Domain remains pending explicit Phase 12D approval.",
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


def test_phase13_task_file_preserves_core_boundary_wording() -> None:
    text = _text(TASK_FILE)
    _assert_all_tokens(
        text,
        (
            "phase13_status: success",
            "Phase 13 defines the explicit implementation approval record and runtime domain selection process.",
            "Phase 13 does not implement production runtime by default.",
            "Phase 13 does not approve production promotion.",
            "Phase 13 does not bypass the Phase 7D selected-gate manual boundary.",
            "Phase 13 does not auto-select a runtime domain.",
            "Phase 13 does not infer implementation approval from Phase 12 acceptance.",
            "Phase 13 does not infer production promotion approval from implementation approval.",
            "Phase 13 treats missing or ambiguous approval as fail-closed.",
            "Approval remains the Phase 7D selected-gate manual boundary.",
        ),
        label="task token",
    )


def test_phase13_required_sections_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 13 purpose",
            "phase 13 approval position",
            "relationship to phase 12g",
            "relationship to phase 12a through phase 12f",
            "explicit implementation approval record scope",
            "runtime domain selection scope",
            "default approval state",
            "operator approval requirement",
            "runtime domain selection requirement",
            "single-domain selection constraint",
            "no auto-selection rule",
            "phase 12 acceptance non-equivalence",
            "production promotion exclusion",
            "manual approval boundary preservation",
            "fail-closed approval model",
            "approved runtime domain status",
            "implementation approval record template",
            "runtime domain candidate matrix",
            "runtime domain selection matrix",
            "approval evidence matrix",
            "operator attestation matrix",
            "approval boundary matrix",
            "blocking condition matrix",
            "runtime capability exclusion matrix",
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


def test_phase13_default_state_and_approval_template_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "Approval Record ID",
            "Approval Record Status",
            "Runtime Domain Selection Status",
            "Selected Runtime Domain",
            "Implementation Approval Status",
            "Production Promotion Status",
            "Operator Approver",
            "Reviewer Attestations",
            "Phase 12G Reference",
            "Phase 12D Gate Reference",
            "Evidence Package Reference",
            "Required Controls",
            "Boundary Constraints",
            "Blocking Conditions",
            "Expiration or Review Date",
            "Rollback Expectation",
            "Observability Expectation",
            "Audit Evidence Expectation",
            "Production Promotion Exclusion",
            "Phase 7D Boundary Preservation Statement",
            "Approval Record Status: pending explicit operator approval",
            "Runtime Domain Selection Status: not selected",
            "Selected Runtime Domain: none",
            "Implementation Approval Status: not granted",
            "Production Promotion Status: not approved",
        ),
        label="template token",
    )


def test_phase13_required_matrices_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "## 18. Runtime Domain Candidate Matrix",
            "| Runtime Domain Candidate | Phase 12D Gate Status | Phase 12E Preparation Status | Phase 12F Readiness Status | Selection Eligibility | Blocking Condition | Production Promotion Status |",
            "## 19. Runtime Domain Selection Matrix",
            "| Selection Decision | Selected Runtime Domain | Required Operator Approval | Required Evidence | Implementation Approval Status | Production Promotion Status | Fail-Closed Behavior |",
            "## 20. Approval Evidence Matrix",
            "| Evidence Type | Required For | Source Phase | Freshness Requirement | Integrity Requirement | Blocking Condition | Approval Impact |",
            "## 21. Operator Attestation Matrix",
            "| Attestation | Required Operator | Required Evidence | Related Runtime Domain | Boundary Statement | Blocking Condition | Approval Impact |",
            "## 22. Approval Boundary Matrix",
            "| Boundary | Approval Record Position | Runtime Implementation Impact | Production Promotion Impact | Required Future Approval | Fail-Closed Condition |",
            "## 23. Blocking Condition Matrix",
            "| Blocking Condition | Affected Approval Area | Required Resolution | Required Reviewer | Gate Outcome | Production Promotion Impact |",
            "## 24. Runtime Capability Exclusion Matrix",
            "| Runtime Capability | Phase 13 Position | Required Future Approval | Current Status | Blocking Condition | Production Promotion Status |",
        ),
        label="matrix token",
    )


def test_phase13_runtime_domain_candidate_and_selection_rows_exist() -> None:
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
            "not eligible / pending explicit operator approval",
            "no selection",
            "approved single-domain selection",
            "denied selection",
            "deferred selection",
            "ambiguous selection",
            "multi-domain selection attempt",
            "multi-domain selection attempt must fail closed",
            "ambiguous selection must fail closed",
        ),
        label="runtime domain matrix token",
    )


def test_phase13_fail_closed_model_is_documented() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "fail-closed if operator approval is missing",
            "fail-closed if operator approval is ambiguous",
            "fail-closed if multiple runtime domains are selected",
            "fail-closed if selected runtime domain lacks phase 12d gate evidence",
            "fail-closed if selected runtime domain lacks phase 12c evidence package",
            "fail-closed if selected runtime domain lacks phase 12e preparation",
            "fail-closed if selected runtime domain lacks phase 12f readiness",
            "fail-closed if implementation approval is inferred from phase 12 acceptance",
            "fail-closed if production promotion is inferred from implementation approval",
            "fail-closed if phase 7d selected-gate manual boundary is bypassed",
            "fail-closed if production promotion is ambiguous",
            "no silent implementation approval",
            "no silent runtime domain selection",
            "no warning-only bypass for approval boundaries",
            "explicit operator review requirement",
            "implementation approval does not equal runtime implementation",
            "implementation approval does not equal production promotion approval",
            "production promotion approval remains deferred unless explicitly approved in a later phase",
        ),
        label="fail-closed token",
    )


def test_phase13_non_goals_and_forbidden_implementations_are_documented() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 13 is explicit implementation approval record and runtime domain selection documentation only",
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
            "production promotion approval",
            "runtime implementation",
        ),
        label="non-goal token",
    )


def test_phase13_required_relationships_and_boundary_language_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 12g is the phase 12 acceptance/readiness pack",
            "phase 12g does not grant implementation approval",
            "phase 12g does not approve production promotion",
            "phase 12g does not select or invent an approved runtime implementation target",
            "phase 12f defines controlled runtime implementation readiness",
            "phase 12e defines approved runtime domain implementation preparation",
            "phase 12d defines the explicit runtime implementation approval gate",
            "phase 12c defines implementation approval evidence package requirements",
            "phase 12b defines runtime boundary approval and implementation scope",
            "phase 12a defines governed production candidate implementation planning",
            "phase 12 acceptance does not equal implementation approval",
            "phase 12 acceptance does not equal production promotion approval",
            "approved runtime domain remains pending explicit phase 12d approval",
            "phase 11 acceptance remains readiness, not approval",
            "phase 10 acceptance remains readiness, not approval",
            "local-only prototypes remain local-only until governed promotion is explicitly approved",
            "rbac advisory context remains not enforcement",
            "approval remains the phase 7d selected-gate manual boundary",
        ),
        label="relationship token",
    )


def test_phase13_pointer_docs_reference_phase13() -> None:
    for path in (ROADMAP, PROJECT_STATE, PHASE12G_DOC):
        low = _flat(path)
        _assert_all_tokens(
            low,
            (
                "phase 13",
                "explicit implementation approval record",
            ),
            label=f"pointer token in {path.name}",
        )

    _assert_all_tokens(
        _flat(PHASE12G_DOC),
        (
            "phase 13 should not implement production runtime by default",
            "phase 13 should create an explicit implementation approval record",
        ),
        label="phase12g forward pointer token",
    )


def test_phase13_recommended_next_step_and_next_major_subphase_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "## Recommended Next Step",
            "Complete Phase 13 PR readiness",
            "- run focused checks",
            "- run full suite",
            "- confirm clean worktree",
            "- push feature/phase13-explicit-implementation-approval-record",
            "- open one PR for Phase 13",
            "- wait for CI green",
            "- squash merge",
            "- sync main",
            "- delete feature branch",
            "## Recommended Next Major Subphase",
            "Phase 14 — Selected Runtime Domain Implementation Plan Blocked State",
            "Phase 14 should document the blocked selected runtime domain implementation planning state if Phase 13 does not record explicit operator approval for exactly one runtime domain.",
            "Phase 14 should not select or infer a runtime domain.",
            "Phase 14 should remain blocked.",
        ),
        label="next-step token",
    )


def test_phase13_forbidden_runtime_artifacts_are_absent() -> None:
    assert not _rel_matches("*phase13*", REPO_ROOT / "scripts")
    assert not _rel_matches("*phase13*", REPO_ROOT / "services")
    assert not _rel_matches("*phase13*", REPO_ROOT / "api")
    assert not _rel_matches("*phase13*", REPO_ROOT / "database")
    assert not _rel_matches("*phase13*", REPO_ROOT / ".github" / "workflows")
    assert not _rel_matches("*phase13*", REPO_ROOT / "deploy")
    assert not _rel_matches("*phase13*", REPO_ROOT / "infra")
    assert not _rel_matches("*phase13*", REPO_ROOT / "keys")
    assert not _rel_matches("*phase13*", REPO_ROOT / "certs")
