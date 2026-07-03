from __future__ import annotations

import hashlib
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/074-phase10a-governed-runtime-integration-readiness-design.md"
DOC = REPO_ROOT / "docs/PHASE10A_GOVERNED_RUNTIME_INTEGRATION_READINESS_DESIGN.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE9G_DOC = REPO_ROOT / "docs/PHASE9G_PHASE9_ACCEPTANCE_PACK.md"
PHASE9F_DOC = REPO_ROOT / "docs/PHASE9F_LOCAL_RBAC_POLICY_PROTOTYPE.md"
PHASE9D_DOC = REPO_ROOT / "docs/PHASE9D_ACTOR_ATTRIBUTION_IN_AUDIT_REPORTS.md"
PHASE9C_DOC = REPO_ROOT / "docs/PHASE9C_LOCAL_OPERATOR_REGISTRY_PROTOTYPE.md"
PHASE8O_DOC = REPO_ROOT / "docs/PHASE8O_FINAL_ACCEPTANCE_PACK.md"

PROTECTED_HASHES = {
    REPO_ROOT / "scripts/dev/evaluate_phase9f_local_rbac_policy.py": "bea1e09dd14124f4d07439dfbb905a23e4ecfb71269fff8ff469a1ca8d461b64",
    REPO_ROOT / "scripts/dev/run_phase9f_local_rbac_policy.sh": "e43b58a44287d0bdf87c89e599781afcf1d0cd9aa600d457978a3121e9f24951",
    REPO_ROOT / "scripts/dev/build_phase9d_actor_attribution_report.py": "46b20935f235fc48a60737ed167a3f612b95afacdd978c326f110b61bf9af473",
    REPO_ROOT / "scripts/dev/run_phase9d_actor_attribution_report.sh": "900513d415be02280437752e4aefb9af6fbff3ab55c684f2943c20e43dc2fc43",
    REPO_ROOT / "scripts/dev/manage_phase9c_local_operator_registry.py": "19d8f8eea523c1b7014463fb351764842429dcb30076e4469a959bd7c326fb6e",
    REPO_ROOT / "scripts/dev/run_phase9c_local_operator_registry.sh": "6526dbeb53cbeeecf1485e73747ebee7f26e62c12f04295616c77b0f869bb21a",
    REPO_ROOT / "scripts/dev/verify_phase8m_detached_signature.py": "ef26e4f11f5ecb73e31f01261b56adb35df223f514edc0986e32f9d00d441aca",
    REPO_ROOT / "scripts/dev/run_phase8m_detached_signature_verifier.sh": "de6cd990e794d5893d31f682a9c7073a350af30c701665c43729d0d889095ff0",
    REPO_ROOT / "scripts/dev/build_phase8l_detached_signature.py": "6a7fddfbb3077c18816b81c57738bd79471db5a3f578d35292fde8e8f318de09",
    REPO_ROOT / "scripts/dev/run_phase8l_detached_signature.sh": "ecd3d6846702948f5a9b77addcd6254ea3a7295dcb01765ebcad91ced1a196cb",
    REPO_ROOT / "scripts/dev/verify_phase8g_export_integrity.py": "1711d387f813b2d8e046704ed7063f1ad7c050413c0b999b7358e0ad6939dc1c",
    REPO_ROOT / "scripts/dev/run_phase8g_export_integrity.sh": "486258b28e74f9034681e5cc7d3827efddbc19ed6e5f0a6266097d6679560c9d",
    REPO_ROOT / "scripts/dev/build_phase8e_audit_export_pack.py": "c656cb49c645f056be4069e78aa5fdf63cc77d3a6676d2ae5bd96fde2a0d8b31",
    REPO_ROOT / "scripts/dev/run_phase8e_audit_export.sh": "9441dc0e5a3fa692fb532c1f1475f89f871b4ed4289bb0d567cf26e6a1305cca",
    REPO_ROOT / "scripts/dev/run_phase7d_single_gate_wrapper.sh": "372aef7a133950a24a1de859a1ba0c01486fd2c84bf46ded783105acc4e47b7d",
    REPO_ROOT / "scripts/dev/execute_single_gate_approval.py": "1b1d00817b1ae89c2840f18c9fe3b73f091abec9c900bf0bff83ad6820e9cebb",
}

EXCLUDED_PARTS = {".git", ".venv", "tmp", "vault", "node_modules", "vendor", "__pycache__"}
FORBIDDEN_EXTENSIONS = (".pem", ".key", ".crt", ".p12", ".pfx", ".sql", ".sqlite", ".db", ".rego")


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(_text(path).lower().replace("`", "").split())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _assert_all_tokens(text: str, tokens: tuple[str, ...], *, label: str) -> None:
    for token in tokens:
        assert token in text, f"missing {label}: {token}"


# ---------------------------------------------------------------------------
# A. File existence and status
# ---------------------------------------------------------------------------


def test_phase10a_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 10A file: {path}"


def test_phase10a_no_runtime_script_or_runner() -> None:
    dev = REPO_ROOT / "scripts/dev"
    for pattern in ("*phase10a*.py", "*phase10a*.sh"):
        matches = sorted(str(path.relative_to(REPO_ROOT)) for path in dev.glob(pattern))
        assert matches == [], f"unexpected Phase 10 runtime file: {matches}"


def test_phase10a_status_tokens() -> None:
    assert "phase10a_status: success" in _text(TASK_FILE)
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "phase10a_status: success",
            "phase7d_runtime_readiness: implemented_manual_gate",
            "durable_audit_store_status: phase8_final_acceptance_pack",
            "identity_boundary_status: design_only",
            "actor_metadata_schema_status: design_only",
            "actor_metadata_runtime_status: local_registry_prototype",
            "local_operator_registry_status: prototype_local_only",
            "actor_attribution_status: local_report_prototype",
            "rbac_design_status: design_only",
            "rbac_policy_status: local_advisory_prototype",
            "rbac_runtime_status: local_advisory_prototype",
            "rbac_enforcement_status: not_implemented",
            "governed_runtime_integration_status: design_only",
            "integration_runtime_status: not_implemented",
            "identity_runtime_status: not_implemented",
            "authentication_runtime_status: not_implemented",
            "operator_identity_assurance_status: unauthenticated_or_operator_declared",
            "signing_implementation_status: prototype_local_only",
            "signature_runtime_status: local_prototype",
            "signature_verifier_runtime_status: local_prototype",
            "key_management_runtime_status: not_implemented",
            "backend_api_database_status: not_implemented",
            "phase10_branch_workflow: enabled",
        ),
        label="status token",
    )


# ---------------------------------------------------------------------------
# B. Scope safety
# ---------------------------------------------------------------------------


def test_phase10a_scope_safety_tokens() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "docs/tests design-only",
            "no runtime scripts",
            "no shell runner",
            "no integration runtime",
            "no authentication runtime",
            "no rbac enforcement",
            "no production policy engine",
            "no backend/api/database",
            "no key management runtime",
            "no wrapper behavior change",
            "no primitive execution",
            "no vault read/write",
            "no new mutation path",
        ),
        label="scope safety token",
    )


# ---------------------------------------------------------------------------
# C. Required sections
# ---------------------------------------------------------------------------


def test_phase10a_required_sections() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "### Purpose",
            "### Scope",
            "### Current trust boundary after Phase 9",
            "### Governed integration concept model",
            "### Evidence source model",
            "### Actor context source model",
            "### Advisory RBAC context source model",
            "### Signature context source model",
            "### Approval boundary source model",
            "### Integration readiness package model",
            "### Future integration input contract",
            "### Future integration output contract",
            "### Evidence binding model",
            "### Actor binding model",
            "### RBAC advisory binding model",
            "### Signature binding model",
            "### Approval boundary preservation model",
            "### Runtime safety model",
            "### Non-authentication boundary",
            "### Non-RBAC-enforcement boundary",
            "### Non-approval boundary",
            "### Future Phase 10B boundary",
            "### Compatibility with Phase 9G",
            "### Compatibility with Phase 9F",
            "### Compatibility with Phase 9D",
            "### Compatibility with Phase 9C",
            "### Compatibility with Phase 8O/8M/8L/8E",
            "### Compatibility with Phase 7D",
            "### Failure taxonomy",
            "### Reviewer action mapping",
            "### Non-goals",
            "### Known limitations",
        ),
        label="section",
    )


# ---------------------------------------------------------------------------
# D. Concept model assertions
# ---------------------------------------------------------------------------


def test_phase10a_concept_model_assertions() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "evidence_source",
            "actor_context",
            "rbac_advisory_context",
            "signature_context",
            "approval_boundary_context",
            "integration_readiness_package",
            "integration_binding",
            "compatibility_check",
            "safety_check",
            "reviewer_action",
            "acceptance_evidence",
            "the model is design-only",
            "no runtime evaluator exists in phase 10a",
            "no integration package is produced in phase 10a",
            "integration readiness is not approval",
        ),
        label="concept model token",
    )


# ---------------------------------------------------------------------------
# E. Evidence/source assertions
# ---------------------------------------------------------------------------


def test_phase10a_evidence_source_assertions() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase8e_audit_export_pack",
            "phase8g_export_integrity_report",
            "phase8m_signature_verifier_report",
            "phase8o_final_acceptance_pack",
            "phase9d_actor_attribution_report",
            "phase9f_local_rbac_advisory_report",
            "phase7d_selected_gate_evidence",
            "source purpose",
            "expected local path family",
            "trust level",
            "mutation boundary",
            "approval boundary",
        ),
        label="evidence/source token",
    )


# ---------------------------------------------------------------------------
# F. Actor / RBAC / signature context assertions
# ---------------------------------------------------------------------------


def test_phase10a_actor_rbac_signature_context_assertions() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase9c_local_operator_registry",
            "phase9d_actor_attribution_report",
            "future_actor_metadata_fields",
            "actor context is not authentication",
            "actor context is not approval",
            "phase9e_rbac_design",
            "phase9f_local_rbac_policy_report",
            "future_rbac_advisory_report",
            "rbac advisory context is not enforcement",
            "rbac allow decision is not approval",
            "phase8l_local_detached_signature",
            "phase8m_signature_verifier_report",
            "phase8n_signature_incident_runbook",
            "no production signing exists",
            "no key management runtime exists",
        ),
        label="context token",
    )


# ---------------------------------------------------------------------------
# G. Integration package / input / output assertions
# ---------------------------------------------------------------------------


def test_phase10a_package_input_output_assertions() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "package_schema_version",
            "evidence_sources",
            "actor_context",
            "rbac_advisory_context",
            "signature_context",
            "approval_boundary_context",
            "compatibility_checks",
            "safety_checks",
            "reviewer_action",
            "limitations",
            "audit_export_manifest",
            "export_integrity_report",
            "signature_verifier_report",
            "final_acceptance_pack",
            "local_operator_registry",
            "actor_attribution_report",
            "rbac_advisory_report",
            "selected_gate_boundary_reference",
            "governed_integration_readiness_report.json",
            "governed_integration_readiness_report.md",
            "integration_compatibility_matrix",
            "integration_safety_findings",
            "integration_limitations",
            "future package is evidence only",
            "package validity is not approval",
        ),
        label="package/input/output token",
    )


# ---------------------------------------------------------------------------
# H. Binding model assertions
# ---------------------------------------------------------------------------


def test_phase10a_binding_model_assertions() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "evidence_id",
            "evidence_type",
            "evidence_phase",
            "evidence_path",
            "evidence_hash_reference",
            "evidence_integrity_status",
            "evidence_signature_status",
            "actor_id",
            "actor_type",
            "actor_identity_assurance",
            "actor_identity_source",
            "actor_role_labels",
            "actor_registry_reference",
            "actor_attribution_reference",
            "advisory_decision",
            "decision_reason",
            "matched_permission_ids",
            "denied_permission_ids",
            "obligations",
            "denial_reasons",
            "rbac_policy_status",
            "rbac_enforcement_status",
            "signature_runtime_status",
            "signature_verifier_runtime_status",
            "signing_implementation_status",
            "signature_verification_status",
            "signed_payload_hash_status",
            "key_management_runtime_status",
        ),
        label="binding model token",
    )


# ---------------------------------------------------------------------------
# I. Approval boundary assertions
# ---------------------------------------------------------------------------


def test_phase10a_approval_boundary_assertions() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "governed integration readiness is not runtime integration",
            "integration design is not approval",
            "evidence bundle is not approval",
            "evidence binding is not approval",
            "actor binding is not authentication",
            "actor binding is not approval",
            "rbac advisory binding is not enforcement",
            "rbac advisory decision is not approval",
            "advisory allow decision is not approval",
            "signature verification remains not approval",
            "final acceptance remains not approval",
            "approval remains phase 7d selected-gate manual boundary",
            "integration readiness must not trigger wrapper",
            "integration readiness must not execute primitives",
            "integration readiness must not trigger next gate",
            "integration readiness must not set approval flags",
        ),
        label="approval boundary token",
    )


# ---------------------------------------------------------------------------
# J. Runtime safety assertions
# ---------------------------------------------------------------------------


def test_phase10a_runtime_safety_assertions() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 10a adds no runtime",
            "future runtime must be local-only unless explicitly changed",
            "future runtime must not call phase 7d wrapper",
            "future runtime must not execute primitives",
            "future runtime must not write vault",
            "future runtime must not mutate phase 8 or phase 9 source outputs",
            "future runtime must write only to its own tmp output root",
            "future runtime must be advisory/evidence only unless a later phase explicitly changes scope",
        ),
        label="runtime safety token",
    )


# ---------------------------------------------------------------------------
# K. Compatibility assertions
# ---------------------------------------------------------------------------


def test_phase10a_compatibility_assertions() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 10a follows phase 9g acceptance boundaries",
            "phase 10a does not reopen phase 9 acceptance semantics",
            "phase 10a does not modify phase 9f runtime",
            "rbac advisory reports remain evidence only",
            "phase 10a does not modify phase 9d runtime",
            "actor attribution remains not approval",
            "phase 10a does not modify phase 9c runtime",
            "registry presence remains not authentication or approval",
            "phase 10a does not modify phase 8 runtime",
            "signature verification remains not approval",
            "final acceptance remains not approval",
            "phase 10a does not modify phase 7d",
            "integration readiness must not approve",
            "integration readiness must not execute primitives",
        ),
        label="compatibility token",
    )


# ---------------------------------------------------------------------------
# L. Failure taxonomy assertions
# ---------------------------------------------------------------------------


def test_phase10a_failure_taxonomy_assertions() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "evidence_source_missing",
            "evidence_source_untrusted",
            "actor_context_missing",
            "actor_context_untrusted",
            "rbac_advisory_context_missing",
            "rbac_advisory_context_untrusted",
            "signature_context_missing",
            "signature_context_untrusted",
            "approval_boundary_missing",
            "compatibility_check_failed",
            "safety_check_failed",
            "identity_assurance_insufficient",
            "rbac_enforcement_confusion",
            "approval_inference_detected",
            "primitive_execution_intent_detected",
            "vault_mutation_intent_detected",
            "backend_integration_out_of_scope",
            "authentication_runtime_out_of_scope",
            "key_management_runtime_out_of_scope",
            "integration_readiness_review_required",
            "evidence_review_required",
            "actor_context_review_required",
            "rbac_advisory_review_required",
            "signature_review_required",
            "approval_boundary_review_required",
            "runtime_scope_violation",
            "primitive_execution_blocked",
            "vault_mutation_blocked",
            "no_action_required",
            "manual_review_required",
            "reject_integration_until_resolved",
            "reject_runtime_scope_until_resolved",
        ),
        label="failure taxonomy token",
    )


# ---------------------------------------------------------------------------
# M. Documentation regression
# ---------------------------------------------------------------------------


def test_phase10a_documentation_regression_references() -> None:
    _assert_all_tokens(_text(ROADMAP), ("Phase 10A", "Phase 5", "read-only", "manual-approved"), label="roadmap token")
    _assert_all_tokens(
        _text(PROJECT_STATE),
        (
            "docs/PHASE10A_GOVERNED_RUNTIME_INTEGRATION_READINESS_DESIGN.md",
            "Current architecture",
            "no database",
            "no FastAPI",
            "no UI",
            "no external APIs",
            "no autopublish",
        ),
        label="project state token",
    )
    for path in (PHASE9G_DOC, PHASE9F_DOC, PHASE9D_DOC, PHASE9C_DOC, PHASE8O_DOC):
        assert "Phase 10A" in _text(path), f"missing Phase 10A reference in {path}"


# ---------------------------------------------------------------------------
# N. Protected runtime files unchanged / no implementation files
# ---------------------------------------------------------------------------


def test_phase10a_protected_runtime_files_unchanged() -> None:
    for path, expected_hash in PROTECTED_HASHES.items():
        assert path.is_file(), f"missing protected runtime file: {path}"
        assert _sha256(path) == expected_hash, f"protected runtime file changed: {path}"


def test_phase10a_no_implementation_files_added() -> None:
    disallowed = (
        REPO_ROOT / "package.json",
        REPO_ROOT / "package-lock.json",
        REPO_ROOT / "pnpm-lock.yaml",
        REPO_ROOT / "yarn.lock",
    )
    for path in disallowed:
        assert not path.exists(), f"unexpected implementation artifact: {path}"

    scripts = REPO_ROOT / "scripts"
    forbidden_patterns = (
        "**/*phase10a*.py",
        "**/*phase10a*.sh",
        "**/*integration*runtime*",
        "**/*auth*.py",
        "**/*rbac*enforcement*",
        "**/*policy*engine*",
        "**/*backend*",
        "**/*api*",
        "**/*database*",
    )
    for pattern in forbidden_patterns:
        matches = [
            path for path in scripts.glob(pattern)
            if path.is_file() and "phase10" in path.name.lower()
        ]
        assert matches == [], f"unexpected implementation file(s): {matches}"


# ---------------------------------------------------------------------------
# O. Static safety for new Phase 10A docs/task only
# ---------------------------------------------------------------------------


def test_phase10a_static_safety_for_new_docs_only() -> None:
    combined = f"{_text(TASK_FILE)}\n{_text(DOC)}"
    forbidden_patterns = (
        r"APPROVE_[A-Z0-9_]+=true",
        r"--execute\b",
        r"\brun_phase7d_single_gate_wrapper\.sh\b",
        r"\bexecute_single_gate_approval\.py\b",
        r"\bpromote_product_candidates\.py\b",
        r"\bcreate_decision\.py\b",
        r"\bfinalize_decision\.py\b",
        r"https?://",
        r"/home/[^/\s]+/Affiliate-Ai",
        r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
        r"\bssh-keygen\b",
        r"\bopenssl\s+genrsa\b",
        r"\bgpg\s+--sign\b",
        r"\bage-keygen\b",
        r"\bsqlite3\.connect\b",
        r"\bboto3\.client\b",
        r"\bCREATE TABLE\b",
        r"\bFastAPI\(",
        r"\boauthlib\b",
        r"\boidc-provider\b",
        r"\bopa\s+eval\b",
        r"\brego\b.*\bpackage\b",
    )
    for pattern in forbidden_patterns:
        assert re.search(pattern, combined, flags=re.IGNORECASE | re.MULTILINE) is None, pattern


# ---------------------------------------------------------------------------
# P. Repo-wide artifact safety
# ---------------------------------------------------------------------------


def test_phase10a_repo_wide_artifact_safety() -> None:
    unexpected = []
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        name = path.name.lower()
        suffix = "".join(path.suffixes).lower()
        if name == "package.json" or suffix in FORBIDDEN_EXTENSIONS:
            unexpected.append(path.relative_to(REPO_ROOT).as_posix())
    assert unexpected == [], f"unexpected repo artifact(s): {unexpected}"
