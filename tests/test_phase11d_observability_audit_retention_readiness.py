from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/083-phase11d-observability-audit-retention-readiness.md"
DOC = REPO_ROOT / "docs/PHASE11D_OBSERVABILITY_AND_AUDIT_RETENTION_READINESS.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE11C_DOC = REPO_ROOT / "docs/PHASE11C_CI_GATE_PROTECTED_BOUNDARY_ENFORCEMENT_DESIGN.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(_text(path).lower().replace("`", "").split())


def _assert_all_tokens(text: str, tokens: tuple[str, ...] | list[str], *, label: str) -> None:
    for token in tokens:
        assert token in text, f"missing {label}: {token}"


def test_phase11d_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 11D file: {path}"


def test_phase11d_only_introduces_expected_phase_files() -> None:
    matches = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("*phase11d*")
        if path.is_file()
        and ".git" not in path.relative_to(REPO_ROOT).parts
        and "__pycache__" not in path.relative_to(REPO_ROOT).parts
    )
    assert matches == [
        "codex/tasks/083-phase11d-observability-audit-retention-readiness.md",
        "tests/test_phase11d_observability_audit_retention_readiness.py",
    ]


def test_phase11d_only_introduces_expected_observability_files() -> None:
    matches = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("*PHASE11D*")
        if path.is_file()
        and "__pycache__" not in path.relative_to(REPO_ROOT).parts
    )
    assert matches == [
        "docs/PHASE11D_OBSERVABILITY_AND_AUDIT_RETENTION_READINESS.md",
    ]


def test_phase11d_required_canonical_wording_exists() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "Phase 11D defines observability and audit retention readiness.",
            "Phase 11D does not implement observability runtime.",
            "Phase 11D does not implement audit storage runtime.",
            "Phase 11D does not implement production runtime.",
            "Phase 11D does not approve production promotion.",
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


def test_phase11d_task_file_preserves_core_boundary_wording() -> None:
    text = _text(TASK_FILE)
    _assert_all_tokens(
        text,
        (
            "phase11d_status: success",
            "Phase 11D defines observability and audit retention readiness.",
            "Phase 11D does not implement observability runtime.",
            "Phase 11D does not implement audit storage runtime.",
            "Phase 11D does not implement production runtime.",
            "Phase 11D does not approve production promotion.",
            "Approval remains the Phase 7D selected-gate manual boundary.",
        ),
        label="task token",
    )


def test_phase11d_required_sections_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 11d purpose",
            "relationship to phase 11a, phase 11b, and phase 11c",
            "observability readiness scope",
            "audit retention readiness scope",
            "telemetry categories",
            "required future log events",
            "required future metrics",
            "required future traceability signals",
            "actor attribution observability",
            "approval event observability",
            "policy decision observability",
            "artifact integrity observability",
            "export and signing observability",
            "failure and rejection observability",
            "audit evidence lifecycle",
            "audit retention model",
            "evidence immutability requirements",
            "incident traceability model",
            "operational health signals",
            "privacy and secret redaction requirements",
            "observability-to-threat mapping",
            "observability-to-ci-gate mapping",
            "retention-to-control mapping",
            "failure handling and escalation",
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


def test_phase11d_documents_telemetry_categories() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "operator action",
            "manual approval event",
            "selected-gate decision",
            "actor attribution",
            "rbac advisory context",
            "policy decision",
            "artifact creation",
            "artifact hash verification",
            "export generation",
            "signing decision",
            "verification decision",
            "rejection event",
            "failure event",
            "boundary violation attempt",
            "secret scan result",
            "ci gate result",
            "protected boundary check result",
            "promotion-readiness evidence result",
            "backup/recovery readiness signal",
            "incident investigation signal",
        ),
        label="telemetry category",
    )


def test_phase11d_documents_required_future_log_events() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "approval selected",
            "approval rejected",
            "actor attribution captured",
            "rbac advisory context evaluated",
            "policy decision requested",
            "policy decision denied",
            "artifact hash calculated",
            "artifact hash mismatch",
            "export generated",
            "export rejected",
            "signing requested",
            "signing blocked",
            "verification requested",
            "verification failed",
            "primitive execution blocked",
            "protected boundary gate failed",
            "local-only prototype promotion blocked",
            "secret redaction applied",
            "retention policy applied",
            "incident evidence package created",
        ),
        label="future log event",
    )


def test_phase11d_documents_required_future_metrics() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "approval decision count",
            "rejected approval count",
            "gate failure count",
            "protected boundary failure count",
            "artifact verification failure count",
            "export rejection count",
            "signing block count",
            "verification failure count",
            "policy denial count",
            "secret scan finding count",
            "evidence bundle creation count",
            "audit retention application count",
            "incident package creation count",
            "mean time to classify failure",
            "mean time to produce evidence package",
        ),
        label="future metric",
    )


def test_phase11d_documents_audit_retention_model_and_evidence_lifecycle() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "retention classes",
            "evidence lifecycle states",
            "retention trigger events",
            "retention duration placeholders",
            "legal/compliance hold placeholder",
            "deletion eligibility criteria",
            "tamper-evidence requirements",
            "restore validation requirement",
            "chain-of-custody expectation",
            "audit export expectation",
            "retention exception handling",
            "operator review requirement",
            "captured",
            "retained",
            "held",
            "eligible for expiration review",
        ),
        label="retention token",
    )


def test_phase11d_documents_privacy_secret_redaction_and_traceability() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "privacy and secret redaction requirements",
            "no secrets in telemetry payloads",
            "secret redaction applied",
            "minimum necessary actor attribution",
            "incident traceability model",
            "correlation identifier",
            "chain-of-custody",
            "evidence package",
        ),
        label="privacy/traceability token",
    )


def test_phase11d_documents_required_mapping_tables() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "| Threat | Required Signal | Required Evidence | Detection Purpose | Escalation Trigger | Deferred Implementation Phase |",
            "| CI Gate | Required Observability Signal | Required Evidence | Failure Indicator | Operator Action | Production Promotion Impact |",
            "| Evidence Type | Retention Class | Integrity Requirement | Access Requirement | Restore Requirement | Deletion/Expiration Requirement | Approval Requirement |",
        ),
        label="mapping header",
    )


def test_phase11d_documents_failure_handling_model() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "fail-closed observability gaps",
            "no silent telemetry loss for protected boundaries",
            "explicit operator review requirement",
            "evidence capture requirement",
            "known-observability-gap classification",
            "retry criteria",
            "escalation criteria",
            "incident package requirement",
            "manual approval does not override missing protected evidence unless explicitly approved in a later production phase",
        ),
        label="failure handling token",
    )


def test_phase11d_non_goals_are_explicit() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "logging runtime",
            "metrics runtime",
            "tracing runtime",
            "audit database",
            "backend/api/database files",
            "siem integration",
            "cloud monitoring integration",
            "opentelemetry runtime",
            "network service",
            "deployment manifest",
            "github actions workflow",
            "ci/cd deployment pipeline",
            "authentication runtime",
            "login/session/user store",
            "rbac enforcement",
            "production policy engine",
            "production signing runtime",
            "verifier runtime",
            "key/cert files",
            "key custody runtime",
            "vault write",
            "primitive execution",
            "export mutation",
            "re-signing",
            "production secrets",
            "production authorization",
            "production promotion approval",
        ),
        label="non-goal token",
    )


def test_phase11d_no_approval_language_drift() -> None:
    low = _flat(DOC)
    for token in (
        "approval remains the phase 7d selected-gate manual boundary",
        "phase 10 acceptance remains readiness, not approval",
        "phase 11a defines production boundary and hardening readiness",
        "phase 11b defines threat model and security control mapping",
        "phase 11c defines ci gate and protected boundary enforcement design",
        "phase 11d does not implement observability runtime",
        "phase 11d does not implement audit storage runtime",
        "phase 11d does not implement production runtime",
        "phase 11d does not approve production promotion",
        "rbac advisory context remains not enforcement",
    ):
        assert token in low, f"missing approval-boundary token: {token}"


def test_phase11d_pointer_docs_reference_phase11d() -> None:
    for path in (ROADMAP, PROJECT_STATE, PHASE11C_DOC):
        low = _flat(path)
        _assert_all_tokens(
            low,
            (
                "phase 11d",
                "observability and audit retention readiness",
            ),
            label=f"pointer token in {path.name}",
        )
