from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/085-phase11f-backup-recovery-promotion-runbook.md"
DOC = REPO_ROOT / "docs/PHASE11F_BACKUP_RECOVERY_AND_PROMOTION_RUNBOOK.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE11E_DOC = REPO_ROOT / "docs/PHASE11E_SECRETS_SIGNING_AND_KEY_CUSTODY_ARCHITECTURE.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(_text(path).lower().replace("`", "").split())


def _assert_all_tokens(text: str, tokens: tuple[str, ...] | list[str], *, label: str) -> None:
    for token in tokens:
        assert token in text, f"missing {label}: {token}"


def test_phase11f_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 11F file: {path}"


def test_phase11f_only_introduces_expected_phase_files() -> None:
    matches = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("*phase11f*")
        if path.is_file()
        and ".git" not in path.relative_to(REPO_ROOT).parts
        and "__pycache__" not in path.relative_to(REPO_ROOT).parts
    )
    assert matches == [
        "codex/tasks/085-phase11f-backup-recovery-promotion-runbook.md",
        "tests/test_phase11f_backup_recovery_promotion_runbook.py",
    ]


def test_phase11f_only_introduces_expected_runbook_doc() -> None:
    matches = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("*PHASE11F*")
        if path.is_file()
        and "__pycache__" not in path.relative_to(REPO_ROOT).parts
    )
    assert matches == [
        "docs/PHASE11F_BACKUP_RECOVERY_AND_PROMOTION_RUNBOOK.md",
    ]


def test_phase11f_required_canonical_wording_exists() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "Phase 11F defines backup, recovery, and promotion runbook readiness.",
            "Phase 11F does not implement backup runtime.",
            "Phase 11F does not implement restore runtime.",
            "Phase 11F does not implement deployment runtime.",
            "Phase 11F does not implement production promotion automation.",
            "Phase 11F does not implement production runtime.",
            "Phase 11F does not approve production promotion.",
            "Phase 11E defines secrets, signing, and key custody architecture readiness.",
            "Phase 11D defines observability and audit retention readiness.",
            "Phase 11C defines CI gate and protected boundary enforcement design.",
            "Phase 11B defines threat model and security control mapping.",
            "Phase 11A defines production boundary and hardening readiness.",
            "Local-only prototypes remain local-only until governed promotion is explicitly approved.",
            "RBAC advisory context remains not enforcement.",
            "Approval remains the Phase 7D selected-gate manual boundary.",
            "Phase 10 acceptance remains readiness, not approval.",
            "Production authentication, RBAC enforcement, key custody, backend/API/database, production signing, verifier runtime, and production policy engine remain out of scope unless explicitly approved.",
        ),
        label="canonical wording",
    )


def test_phase11f_task_file_preserves_core_boundary_wording() -> None:
    text = _text(TASK_FILE)
    _assert_all_tokens(
        text,
        (
            "phase11f_status: success",
            "Phase 11F defines backup, recovery, and promotion runbook readiness.",
            "Phase 11F does not implement backup runtime.",
            "Phase 11F does not implement restore runtime.",
            "Phase 11F does not implement deployment runtime.",
            "Phase 11F does not implement production promotion automation.",
            "Phase 11F does not implement production runtime.",
            "Phase 11F does not approve production promotion.",
            "Approval remains the Phase 7D selected-gate manual boundary.",
        ),
        label="task token",
    )


def test_phase11f_required_sections_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 11f purpose",
            "relationship to phase 11a, phase 11b, phase 11c, phase 11d, and phase 11e",
            "backup readiness scope",
            "recovery readiness scope",
            "promotion runbook scope",
            "backup object classification",
            "recovery object classification",
            "rpo and rto placeholder model",
            "backup evidence requirements",
            "restore validation requirements",
            "rollback criteria",
            "disaster recovery boundary",
            "promotion readiness preconditions",
            "controlled promotion runbook",
            "promotion evidence package",
            "operator approval checkpoints",
            "failure and rollback handling",
            "backup-to-control mapping",
            "recovery-to-evidence mapping",
            "promotion-to-approval mapping",
            "observability requirements for backup and recovery events",
            "ci gate requirements for promotion readiness",
            "secrets and key custody dependency checks",
            "audit retention dependency checks",
            "manual approval boundary preservation",
            "local-only prototype protection",
            "production candidate readiness criteria",
            "non-goals and forbidden implementations",
            "acceptance criteria",
            "safe demo scenarios",
            "operator checklist",
            "recommended next step",
            "recommended next major subphase",
        ),
        label="section",
    )


def test_phase11f_documents_backup_object_classification() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "documentation artifact",
            "acceptance pack",
            "evidence bundle",
            "audit report",
            "export sidecar artifact",
            "signed export metadata placeholder",
            "configuration snapshot",
            "ci evidence package",
            "approval event evidence",
            "observability evidence package",
            "secret/key custody evidence package",
            "promotion readiness package",
            "rollback evidence package",
            "incident evidence package",
            "do not implement storage, backup, restore, or retention runtime",
        ),
        label="backup object classification token",
    )


def test_phase11f_documents_recovery_object_classification_and_placeholder_model() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "single artifact recovery",
            "evidence bundle recovery",
            "acceptance pack recovery",
            "configuration snapshot recovery",
            "audit report recovery",
            "promotion readiness package recovery",
            "incident evidence package recovery",
            "rpo placeholder",
            "rto placeholder",
            "business criticality classification placeholder",
            "restore validation frequency placeholder",
            "recovery dependency placeholder",
            "operator review requirement",
            "explicit approval requirement before production values are finalized",
        ),
        label="recovery placeholder token",
    )


def test_phase11f_documents_restore_validation_and_rollback_expectations() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "backup evidence requirements",
            "restore validation requirements",
            "rollback criteria",
            "disaster recovery boundary",
            "restore validation evidence",
            "rollback trigger",
            "rollback evidence package",
            "promotion evidence gap",
            "restore validation failure",
            "rollback escalation requirement",
        ),
        label="restore and rollback token",
    )


def test_phase11f_documents_controlled_promotion_runbook_and_evidence_package() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "confirm local-only prototype status",
            "confirm phase 11a boundary readiness",
            "confirm phase 11b threat/control mapping",
            "confirm phase 11c ci gate readiness",
            "confirm phase 11d observability/audit retention readiness",
            "confirm phase 11e secrets/signing/key custody readiness",
            "confirm backup/recovery readiness",
            "confirm restore validation evidence",
            "confirm rollback criteria",
            "assemble promotion evidence package",
            "request explicit operator approval",
            "preserve phase 7d manual approval boundary",
            "classify as governed production candidate only after explicit approval",
            "defer production runtime implementation to a later approved phase",
            "operator approval checkpoints",
            "promotion evidence package",
        ),
        label="promotion runbook token",
    )


def test_phase11f_documents_required_mapping_tables() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "| Backup Object | Required Control | Required Evidence | Restore Requirement | Retention Dependency | Approval Requirement |",
            "| Recovery Scenario | Required Evidence | Restore Validation Requirement | Rollback Criteria | Operator Action | Production Promotion Impact |",
            "| Promotion Step | Required Evidence | Required Gate | Required Approval | Blocking Condition | Deferred Implementation Phase |",
        ),
        label="mapping header",
    )


def test_phase11f_documents_failure_handling_model() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "fail-closed missing backup evidence",
            "fail-closed missing restore validation",
            "fail-closed rollback ambiguity",
            "fail-closed promotion evidence gap",
            "no silent promotion readiness pass",
            "no warning-only bypass for protected promotion evidence",
            "explicit operator review requirement",
            "incident evidence package requirement",
            "rollback escalation requirement",
            "manual approval does not override missing protected backup/recovery evidence unless explicitly approved in a later production phase",
        ),
        label="failure handling token",
    )


def test_phase11f_non_goals_are_explicit() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "backup runtime",
            "restore runtime",
            "database/storage runtime",
            "backend/api/database files",
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
            "signing runtime",
            "verifier runtime",
            "authentication runtime",
            "login/session/user store",
            "rbac enforcement",
            "production policy engine",
            "logging runtime",
            "metrics runtime",
            "tracing runtime",
            "siem integration",
            "network service",
            "primitive execution",
            "export mutation",
            "re-signing",
            "production authorization",
            "production promotion approval",
        ),
        label="non-goal token",
    )


def test_phase11f_no_approval_language_drift() -> None:
    low = _flat(DOC)
    for token in (
        "approval remains the phase 7d selected-gate manual boundary",
        "phase 10 acceptance remains readiness, not approval",
        "phase 11a defines production boundary and hardening readiness",
        "phase 11b defines threat model and security control mapping",
        "phase 11c defines ci gate and protected boundary enforcement design",
        "phase 11d defines observability and audit retention readiness",
        "phase 11e defines secrets, signing, and key custody architecture readiness",
        "phase 11f does not implement backup runtime",
        "phase 11f does not implement restore runtime",
        "phase 11f does not implement deployment runtime",
        "phase 11f does not implement production promotion automation",
        "phase 11f does not implement production runtime",
        "phase 11f does not approve production promotion",
        "rbac advisory context remains not enforcement",
    ):
        assert token in low, f"missing approval-boundary token: {token}"


def test_phase11f_pointer_docs_reference_phase11f() -> None:
    for path in (ROADMAP, PROJECT_STATE, PHASE11E_DOC):
        low = _flat(path)
        _assert_all_tokens(
            low,
            (
                "phase 11f",
                "backup, recovery, and promotion runbook",
            ),
            label=f"pointer token in {path.name}",
        )


def test_phase11f_forbidden_runtime_artifacts_are_absent() -> None:
    forbidden = [
        REPO_ROOT / "scripts/dev/run_phase11f_backup_recovery_promotion_runbook.sh",
        REPO_ROOT / "scripts/dev/phase11f_backup_recovery_promotion_runbook.py",
        REPO_ROOT / "scripts/dev/phase11f_backup_runtime.py",
        REPO_ROOT / "scripts/dev/phase11f_restore_runtime.py",
        REPO_ROOT / "scripts/dev/phase11f_deployment_runtime.py",
        REPO_ROOT / ".github/workflows/phase11f-backup-recovery-promotion-runbook.yml",
        REPO_ROOT / "deploy/phase11f-backup-recovery-promotion-runbook.yaml",
        REPO_ROOT / "infra/phase11f-backup-recovery-promotion-runbook.tf",
    ]
    for path in forbidden:
        assert not path.exists(), f"unexpected Phase 11F runtime artifact: {path}"
