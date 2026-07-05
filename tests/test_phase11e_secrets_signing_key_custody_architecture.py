from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/084-phase11e-secrets-signing-key-custody-architecture.md"
DOC = REPO_ROOT / "docs/PHASE11E_SECRETS_SIGNING_AND_KEY_CUSTODY_ARCHITECTURE.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE11D_DOC = REPO_ROOT / "docs/PHASE11D_OBSERVABILITY_AND_AUDIT_RETENTION_READINESS.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(_text(path).lower().replace("`", "").split())


def _assert_all_tokens(text: str, tokens: tuple[str, ...] | list[str], *, label: str) -> None:
    for token in tokens:
        assert token in text, f"missing {label}: {token}"


def test_phase11e_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 11E file: {path}"


def test_phase11e_only_introduces_expected_phase_files() -> None:
    matches = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("*phase11e*")
        if path.is_file()
        and ".git" not in path.relative_to(REPO_ROOT).parts
        and "__pycache__" not in path.relative_to(REPO_ROOT).parts
    )
    assert matches == [
        "codex/tasks/084-phase11e-secrets-signing-key-custody-architecture.md",
        "tests/test_phase11e_secrets_signing_key_custody_architecture.py",
    ]


def test_phase11e_only_introduces_expected_architecture_doc() -> None:
    matches = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("*PHASE11E*")
        if path.is_file()
        and "__pycache__" not in path.relative_to(REPO_ROOT).parts
    )
    assert matches == [
        "docs/PHASE11E_SECRETS_SIGNING_AND_KEY_CUSTODY_ARCHITECTURE.md",
    ]


def test_phase11e_required_canonical_wording_exists() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "Phase 11E defines secrets, signing, and key custody architecture readiness.",
            "Phase 11E does not implement secrets runtime.",
            "Phase 11E does not implement signing runtime.",
            "Phase 11E does not implement verifier runtime.",
            "Phase 11E does not add key material.",
            "Phase 11E does not implement production runtime.",
            "Phase 11E does not approve production promotion.",
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


def test_phase11e_task_file_preserves_core_boundary_wording() -> None:
    text = _text(TASK_FILE)
    _assert_all_tokens(
        text,
        (
            "phase11e_status: success",
            "Phase 11E defines secrets, signing, and key custody architecture readiness.",
            "Phase 11E does not implement secrets runtime.",
            "Phase 11E does not implement signing runtime.",
            "Phase 11E does not implement verifier runtime.",
            "Phase 11E does not add key material.",
            "Phase 11E does not implement production runtime.",
            "Phase 11E does not approve production promotion.",
            "Approval remains the Phase 7D selected-gate manual boundary.",
        ),
        label="task token",
    )


def test_phase11e_required_sections_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 11e purpose",
            "relationship to phase 11a, phase 11b, phase 11c, and phase 11d",
            "secrets architecture readiness scope",
            "signing architecture readiness scope",
            "verifier architecture readiness scope",
            "key custody readiness scope",
            "secret classification model",
            "key classification model",
            "signing boundary model",
            "verifier separation model",
            "custody and separation of duties",
            "rotation readiness requirements",
            "revocation readiness requirements",
            "emergency key response model",
            "break-glass boundary",
            "secret redaction and exposure prevention",
            "test fixture safety requirements",
            "audit evidence requirements",
            "observability requirements for key events",
            "ci gate requirements for secrets and keys",
            "threat-to-key-control mapping",
            "signing-to-evidence mapping",
            "custody-to-approval mapping",
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


def test_phase11e_documents_secret_classification_model() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "production secret",
            "development secret",
            "test fixture token",
            "placeholder value",
            "signing private key",
            "verification public key",
            "rotation token",
            "revocation marker",
            "break-glass credential",
            "audit export credential",
            "ci secret",
            "local-only prototype placeholder",
            "no real secrets or key material may be committed",
        ),
        label="secret classification token",
    )


def test_phase11e_documents_key_classification_and_custody_requirements() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "signer/verifier separation",
            "private key custody",
            "public verifier distribution",
            "key ownership",
            "custodian role",
            "operator approval",
            "dual-control placeholder",
            "rotation schedule placeholder",
            "emergency revocation",
            "key compromise response",
            "audit evidence for key events",
            "no key material in repository",
            "no vault write before explicit approval",
        ),
        label="key custody token",
    )


def test_phase11e_documents_signing_boundary_model() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "signing request boundary",
            "signing approval boundary",
            "signing execution boundary",
            "verifier trust boundary",
            "artifact hash binding",
            "signature metadata requirements",
            "signer identity requirements",
            "verifier identity requirements",
            "rejection criteria",
            "re-signing prohibition unless explicitly approved",
            "export mutation prohibition",
            "production signing deferred to later approved phase",
        ),
        label="signing boundary token",
    )


def test_phase11e_documents_verifier_separation_rotation_revocation_and_emergency_response() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "verifier separation model",
            "custody and separation of duties",
            "rotation readiness requirements",
            "revocation readiness requirements",
            "emergency key response model",
            "break-glass boundary",
            "secret redaction and exposure prevention",
            "test fixture safety requirements",
            "audit evidence requirements",
            "observability requirements for key events",
            "ci gate requirements for secrets and keys",
        ),
        label="readiness area token",
    )


def test_phase11e_documents_required_mapping_tables() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "| Threat | Required Key/Secret Control | Required Evidence | Approval Requirement | CI Gate Dependency | Deferred Implementation Phase |",
            "| Signing Event | Required Metadata | Required Evidence | Required Observability Signal | Rejection Condition | Production Promotion Impact |",
            "| Custody Event | Required Custodian | Required Approval | Required Evidence | Separation Requirement | Emergency Handling Requirement |",
        ),
        label="mapping header",
    )


def test_phase11e_documents_failure_handling_model() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "fail-closed missing key evidence",
            "fail-closed secret scan finding",
            "fail-closed signing ambiguity",
            "fail-closed verifier ambiguity",
            "no silent signing acceptance",
            "no warning-only bypass for key custody issues",
            "explicit operator review requirement",
            "incident evidence package requirement",
            "revocation escalation requirement",
            "manual approval does not override missing protected key evidence unless explicitly approved in a later production phase",
        ),
        label="failure handling token",
    )


def test_phase11e_non_goals_are_explicit() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "production secrets",
            "test secrets that resemble real credentials",
            "key files",
            "certificate files",
            "signing runtime",
            "verifier runtime",
            "vault write",
            "vault client runtime",
            "key custody runtime",
            "key rotation runtime",
            "revocation runtime",
            "authentication runtime",
            "login/session/user store",
            "rbac enforcement",
            "production policy engine",
            "backend/api/database files",
            "logging runtime",
            "metrics runtime",
            "tracing runtime",
            "siem integration",
            "network service",
            "deployment manifest",
            "github actions workflow",
            "ci/cd deployment pipeline",
            "primitive execution",
            "export mutation",
            "re-signing",
            "production authorization",
            "production promotion approval",
        ),
        label="non-goal token",
    )


def test_phase11e_no_approval_language_drift() -> None:
    low = _flat(DOC)
    for token in (
        "approval remains the phase 7d selected-gate manual boundary",
        "phase 10 acceptance remains readiness, not approval",
        "phase 11a defines production boundary and hardening readiness",
        "phase 11b defines threat model and security control mapping",
        "phase 11c defines ci gate and protected boundary enforcement design",
        "phase 11d defines observability and audit retention readiness",
        "phase 11e does not implement secrets runtime",
        "phase 11e does not implement signing runtime",
        "phase 11e does not implement verifier runtime",
        "phase 11e does not add key material",
        "phase 11e does not implement production runtime",
        "phase 11e does not approve production promotion",
        "rbac advisory context remains not enforcement",
    ):
        assert token in low, f"missing approval-boundary token: {token}"


def test_phase11e_pointer_docs_reference_phase11e() -> None:
    for path in (ROADMAP, PROJECT_STATE, PHASE11D_DOC):
        low = _flat(path)
        _assert_all_tokens(
            low,
            (
                "phase 11e",
                "secrets, signing, and key custody architecture",
            ),
            label=f"pointer token in {path.name}",
        )


def test_phase11e_forbidden_runtime_artifacts_are_absent() -> None:
    forbidden = [
        REPO_ROOT / "scripts/dev/run_phase11e_secrets_signing_key_custody_architecture.sh",
        REPO_ROOT / "scripts/dev/phase11e_secrets_signing_key_custody_architecture.py",
        REPO_ROOT / "scripts/dev/phase11e_signing_runtime.py",
        REPO_ROOT / "scripts/dev/phase11e_verifier_runtime.py",
        REPO_ROOT / "scripts/dev/phase11e_vault_client.py",
        REPO_ROOT / ".github/workflows/phase11e-secrets-signing-key-custody-architecture.yml",
        REPO_ROOT / "deploy/phase11e-secrets-signing-key-custody-architecture.yaml",
        REPO_ROOT / "certs/phase11e-cert.pem",
        REPO_ROOT / "keys/phase11e-private-key.pem",
    ]
    for path in forbidden:
        assert not path.exists(), f"unexpected Phase 11E runtime artifact: {path}"
