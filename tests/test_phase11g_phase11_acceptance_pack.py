from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/086-phase11g-phase11-acceptance-pack.md"
DOC = REPO_ROOT / "docs/PHASE11G_PHASE11_ACCEPTANCE_PACK.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE11F_DOC = REPO_ROOT / "docs/PHASE11F_BACKUP_RECOVERY_AND_PROMOTION_RUNBOOK.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(_text(path).lower().replace("`", "").split())


def _assert_all_tokens(text: str, tokens: tuple[str, ...] | list[str], *, label: str) -> None:
    for token in tokens:
        assert token in text, f"missing {label}: {token}"


def test_phase11g_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 11G file: {path}"


def test_phase11g_only_introduces_expected_phase_files() -> None:
    matches = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("*phase11g*")
        if path.is_file()
        and ".git" not in path.relative_to(REPO_ROOT).parts
        and "__pycache__" not in path.relative_to(REPO_ROOT).parts
    )
    assert matches == [
        "codex/tasks/086-phase11g-phase11-acceptance-pack.md",
        "tests/test_phase11g_phase11_acceptance_pack.py",
    ]


def test_phase11g_only_introduces_expected_acceptance_doc() -> None:
    matches = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("*PHASE11G*")
        if path.is_file()
        and "__pycache__" not in path.relative_to(REPO_ROOT).parts
    )
    assert matches == [
        "docs/PHASE11G_PHASE11_ACCEPTANCE_PACK.md",
    ]


def test_phase11g_required_canonical_wording_exists() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "Phase 11G is the Phase 11 acceptance pack.",
            "Phase 11G does not implement production runtime.",
            "Phase 11G does not approve production promotion.",
            "Phase 11A defines production boundary and hardening readiness.",
            "Phase 11B defines threat model and security control mapping.",
            "Phase 11C defines CI gate and protected boundary enforcement design.",
            "Phase 11D defines observability and audit retention readiness.",
            "Phase 11E defines secrets, signing, and key custody architecture readiness.",
            "Phase 11F defines backup, recovery, and promotion runbook readiness.",
            "Local-only prototypes remain local-only until governed promotion is explicitly approved.",
            "RBAC advisory context remains not enforcement.",
            "Approval remains the Phase 7D selected-gate manual boundary.",
            "Phase 10 acceptance remains readiness, not approval.",
            "Phase 11 acceptance remains readiness, not approval.",
            "Production authentication, RBAC enforcement, key custody, backend/API/database, production signing, verifier runtime, and production policy engine remain out of scope unless explicitly approved.",
        ),
        label="canonical wording",
    )


def test_phase11g_task_file_preserves_core_boundary_wording() -> None:
    text = _text(TASK_FILE)
    _assert_all_tokens(
        text,
        (
            "phase11g_status: success",
            "Phase 11G is the Phase 11 acceptance pack.",
            "Phase 11G does not implement production runtime.",
            "Phase 11G does not approve production promotion.",
            "Phase 11 acceptance remains readiness, not approval.",
            "Approval remains the Phase 7D selected-gate manual boundary.",
        ),
        label="task token",
    )


def test_phase11g_required_sections_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 11g purpose",
            "phase 11 acceptance scope",
            "relationship to phase 10",
            "phase 11a acceptance summary",
            "phase 11b acceptance summary",
            "phase 11c acceptance summary",
            "phase 11d acceptance summary",
            "phase 11e acceptance summary",
            "phase 11f acceptance summary",
            "cross-phase boundary confirmation",
            "cross-phase non-goals",
            "production runtime exclusion",
            "production promotion exclusion",
            "manual approval boundary preservation",
            "local-only prototype protection",
            "required evidence summary",
            "ci gate readiness summary",
            "observability and audit readiness summary",
            "secrets, signing, and key custody readiness summary",
            "backup, recovery, and promotion runbook readiness summary",
            "safe demo scenarios",
            "full acceptance checklist",
            "pr readiness checklist",
            "merge readiness checklist",
            "known limitations",
            "recommended immediate next step",
            "recommended next major phase",
        ),
        label="section",
    )


def test_phase11g_references_phase11a_through_phase11f() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 11a acceptance summary",
            "phase 11b acceptance summary",
            "phase 11c acceptance summary",
            "phase 11d acceptance summary",
            "phase 11e acceptance summary",
            "phase 11f acceptance summary",
            "production boundary definition",
            "hardening requirements",
            "threat model and control mapping",
            "ci gate design",
            "protected boundary checks",
            "observability and audit retention readiness",
            "secrets/signing/key custody architecture readiness",
            "backup/recovery/promotion runbook readiness",
            "phase 11 does not provide production runtime implementation",
        ),
        label="phase 11 acceptance summary token",
    )


def test_phase11g_preserves_readiness_and_manual_boundary_language() -> None:
    low = _flat(DOC)
    for token in (
        "phase 11 acceptance remains readiness, not approval",
        "phase 10 acceptance remains readiness, not approval",
        "approval remains the phase 7d selected-gate manual boundary",
        "local-only prototypes remain local-only until governed promotion is explicitly approved",
        "rbac advisory context remains not enforcement",
    ):
        assert token in low, f"missing preserved-boundary token: {token}"


def test_phase11g_explicitly_excludes_production_runtime_and_promotion_approval() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 11g does not implement production runtime",
            "phase 11g does not approve production promotion",
            "production runtime exclusion",
            "production promotion exclusion",
            "production promotion approval",
        ),
        label="runtime exclusion token",
    )


def test_phase11g_required_readiness_summaries_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "required evidence summary",
            "ci gate readiness summary",
            "observability and audit readiness summary",
            "secrets, signing, and key custody readiness summary",
            "backup, recovery, and promotion runbook readiness summary",
        ),
        label="readiness summary token",
    )


def test_phase11g_safe_demo_and_checklists_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "safe demo scenarios",
            "full acceptance checklist",
            "pr readiness checklist",
            "merge readiness checklist",
            "known limitations",
        ),
        label="checklist token",
    )


def test_phase11g_recommended_immediate_next_step_exists() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "## Recommended Immediate Next Step",
            "Complete Phase 11 PR readiness",
            "- run focused checks",
            "- run full suite",
            "- confirm clean worktree",
            "- push feature/phase11g-phase11-acceptance-pack",
            "- open one PR for Phase 11",
            "- wait for CI green",
            "- squash merge",
            "- sync main",
            "- delete feature branch",
        ),
        label="immediate next step token",
    )


def test_phase11g_recommended_next_major_phase_exists() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "## Recommended Next Major Phase",
            "Phase 12 — Governed Production Candidate Implementation Planning",
            "Phase 12 should not immediately implement production authentication, RBAC enforcement, key custody, backend/API/database, production signing, verifier runtime, production policy engine, deployment runtime, or production promotion automation unless explicitly approved.",
            "Phase 12 should first translate the Phase 11 readiness outputs into an explicitly approved production candidate implementation plan, including scoped runtime boundaries, implementation sequence, security controls, CI enforcement candidates, observability implementation candidates, backup/recovery implementation candidates, secrets/key custody implementation candidates, rollback strategy, and approval gates.",
        ),
        label="next major phase token",
    )


def test_phase11g_pointer_docs_reference_phase11g() -> None:
    for path in (ROADMAP, PROJECT_STATE, PHASE11F_DOC):
        low = _flat(path)
        _assert_all_tokens(
            low,
            (
                "phase 11g",
                "phase 11 acceptance pack",
            ),
            label=f"pointer token in {path.name}",
        )


def test_phase11g_forbidden_runtime_artifacts_are_absent() -> None:
    forbidden = [
        REPO_ROOT / "scripts/dev/run_phase11g_phase11_acceptance_pack.sh",
        REPO_ROOT / "scripts/dev/phase11g_phase11_acceptance_pack.py",
        REPO_ROOT / "scripts/dev/phase11g_production_runtime.py",
        REPO_ROOT / "scripts/dev/phase11g_deployment_runtime.py",
        REPO_ROOT / ".github/workflows/phase11g-phase11-acceptance-pack.yml",
        REPO_ROOT / "deploy/phase11g-phase11-acceptance-pack.yaml",
    ]
    for path in forbidden:
        assert not path.exists(), f"unexpected Phase 11G runtime artifact: {path}"
