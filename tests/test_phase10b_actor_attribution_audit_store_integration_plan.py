from __future__ import annotations

import hashlib
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/075-phase10b-actor-attribution-audit-store-integration-plan.md"
DOC = REPO_ROOT / "docs/PHASE10B_ACTOR_ATTRIBUTION_AUDIT_STORE_INTEGRATION_PLAN.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE10A_DOC = REPO_ROOT / "docs/PHASE10A_GOVERNED_RUNTIME_INTEGRATION_READINESS_DESIGN.md"
PHASE9G_DOC = REPO_ROOT / "docs/PHASE9G_PHASE9_ACCEPTANCE_PACK.md"
PHASE9D_DOC = REPO_ROOT / "docs/PHASE9D_ACTOR_ATTRIBUTION_IN_AUDIT_REPORTS.md"
PHASE9C_DOC = REPO_ROOT / "docs/PHASE9C_LOCAL_OPERATOR_REGISTRY_PROTOTYPE.md"
PHASE8O_DOC = REPO_ROOT / "docs/PHASE8O_FINAL_ACCEPTANCE_PACK.md"
PHASE8E_DOC = REPO_ROOT / "docs/PHASE8E_AUDIT_EXPORT_PACK.md"
PHASE8C_DOC = REPO_ROOT / "docs/PHASE8C_AUDIT_STORE_VERIFIER_REPORTING.md"
PHASE8B_COMPAT_DOC = REPO_ROOT / "docs/PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE_PROTOTYPE.md"

PROTECTED_HASHES = {
    REPO_ROOT / "scripts/dev/ingest_phase8b_audit_record.py": "d4af3b87e058a5ff93bf4b9ce57471dca4782a432098206df5dbb4275b7ff8a0",
    REPO_ROOT / "scripts/dev/run_phase8b_audit_ingest.sh": "9eeeb71d72fd6183caddf97a9dfa7406f985fcac06af5f16f67c2d7f9d2ca343",
    REPO_ROOT / "scripts/dev/verify_phase8c_audit_store.py": "87edb8355f3f5868782a16060950d53bb80e09ac3f27d99e16377261fc763787",
    REPO_ROOT / "scripts/dev/run_phase8c_audit_report.sh": "72755c4576de3485a4827a4ce908c4dc64e53cb36cf907e335ff622c52ade7f1",
    REPO_ROOT / "scripts/dev/query_phase8d_audit_store.py": "3ffab49a1cd16a744a8fe04e788601e567b2191a94a3fbcda55d8da864e5bf82",
    REPO_ROOT / "scripts/dev/run_phase8d_audit_query.sh": "2ad91d7551d5c027203772ab6109aebaf08eb21766fbe64fde07208205179649",
    REPO_ROOT / "scripts/dev/build_phase8e_audit_export_pack.py": "c656cb49c645f056be4069e78aa5fdf63cc77d3a6676d2ae5bd96fde2a0d8b31",
    REPO_ROOT / "scripts/dev/run_phase8e_audit_export.sh": "9441dc0e5a3fa692fb532c1f1475f89f871b4ed4289bb0d567cf26e6a1305cca",
    REPO_ROOT / "scripts/dev/verify_phase8g_export_integrity.py": "1711d387f813b2d8e046704ed7063f1ad7c050413c0b999b7358e0ad6939dc1c",
    REPO_ROOT / "scripts/dev/run_phase8g_export_integrity.sh": "486258b28e74f9034681e5cc7d3827efddbc19ed6e5f0a6266097d6679560c9d",
    REPO_ROOT / "scripts/dev/verify_phase8m_detached_signature.py": "ef26e4f11f5ecb73e31f01261b56adb35df223f514edc0986e32f9d00d441aca",
    REPO_ROOT / "scripts/dev/run_phase8m_detached_signature_verifier.sh": "de6cd990e794d5893d31f682a9c7073a350af30c701665c43729d0d889095ff0",
    REPO_ROOT / "scripts/dev/manage_phase9c_local_operator_registry.py": "19d8f8eea523c1b7014463fb351764842429dcb30076e4469a959bd7c326fb6e",
    REPO_ROOT / "scripts/dev/run_phase9c_local_operator_registry.sh": "6526dbeb53cbeeecf1485e73747ebee7f26e62c12f04295616c77b0f869bb21a",
    REPO_ROOT / "scripts/dev/build_phase9d_actor_attribution_report.py": "46b20935f235fc48a60737ed167a3f612b95afacdd978c326f110b61bf9af473",
    REPO_ROOT / "scripts/dev/run_phase9d_actor_attribution_report.sh": "900513d415be02280437752e4aefb9af6fbff3ab55c684f2943c20e43dc2fc43",
    REPO_ROOT / "scripts/dev/evaluate_phase9f_local_rbac_policy.py": "bea1e09dd14124f4d07439dfbb905a23e4ecfb71269fff8ff469a1ca8d461b64",
    REPO_ROOT / "scripts/dev/run_phase9f_local_rbac_policy.sh": "e43b58a44287d0bdf87c89e599781afcf1d0cd9aa600d457978a3121e9f24951",
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


def test_phase10b_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 10B file: {path}"


def test_phase10b_no_runtime_script_or_runner() -> None:
    dev = REPO_ROOT / "scripts/dev"
    for pattern in ("*phase10b*.py", "*phase10b*.sh", "*phase10*.py", "*phase10*.sh"):
        matches = sorted(str(path.relative_to(REPO_ROOT)) for path in dev.glob(pattern))
        assert matches == [], f"unexpected Phase 10 runtime file: {matches}"


def test_phase10b_status_tokens() -> None:
    assert "phase10b_status: success" in _text(TASK_FILE)
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "phase10b_status: success",
            "phase10a_status: success",
            "phase7d_runtime_readiness: implemented_manual_gate",
            "durable_audit_store_status: phase8_final_acceptance_pack",
            "audit_actor_attribution_integration_status: design_only",
            "governed_runtime_integration_status: design_only",
            "integration_runtime_status: not_implemented",
            "identity_boundary_status: design_only",
            "actor_metadata_schema_status: design_only",
            "actor_metadata_runtime_status: local_registry_prototype",
            "local_operator_registry_status: prototype_local_only",
            "actor_attribution_status: local_report_prototype",
            "rbac_policy_status: local_advisory_prototype",
            "rbac_runtime_status: local_advisory_prototype",
            "rbac_enforcement_status: not_implemented",
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


def test_phase10b_scope_safety_tokens() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "docs/tests design-only",
            "no runtime scripts",
            "no shell runner",
            "no audit store runtime changes",
            "no audit query runtime changes",
            "no audit export runtime changes",
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


def test_phase10b_required_sections() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "### Purpose",
            "### Scope",
            "### Current trust boundary after Phase 10A",
            "### Audit store actor attribution concept model",
            "### Existing Phase 8 audit artifact model",
            "### Existing Phase 9 actor/RBAC context model",
            "### Future audit actor field model",
            "### Actor attribution source binding model",
            "### RBAC advisory source binding model",
            "### Signature/evidence source binding model",
            "### Append-only compatibility model",
            "### Hash-chain compatibility model",
            "### Query/report compatibility model",
            "### Export pack compatibility model",
            "### Final acceptance compatibility model",
            "### Future integration package compatibility",
            "### Future audit record input contract",
            "### Future audit report output contract",
            "### Future audit export output contract",
            "### Migration and backward compatibility plan",
            "### Privacy and PII minimization model",
            "### Secret handling model",
            "### Approval boundary preservation model",
            "### Runtime safety model",
            "### Non-authentication boundary",
            "### Non-RBAC-enforcement boundary",
            "### Non-approval boundary",
            "### Future Phase 10C boundary",
            "### Compatibility with Phase 10A",
            "### Compatibility with Phase 9G/9D/9C/9F",
            "### Compatibility with Phase 8B/8C/8D/8E/8G/8M/8O",
            "### Compatibility with Phase 7D",
            "### Failure taxonomy",
            "### Reviewer action mapping",
            "### Non-goals",
            "### Known limitations",
        ),
        label="section",
    )


def test_phase10b_concept_model_assertions() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "audit_actor_context",
            "audit_actor_binding",
            "audit_actor_source",
            "actor_attribution_reference",
            "rbac_advisory_reference",
            "signature_evidence_reference",
            "approval_boundary_reference",
            "backward_compatible_audit_record",
            "actor_attributed_audit_report",
            "actor_attributed_audit_export",
            "concept model is design-only",
            "no audit actor fields are emitted in phase 10b",
            "audit actor attribution is not authentication",
            "audit actor attribution is not approval",
        ),
        label="concept model token",
    )


def test_phase10b_phase8_artifact_assertions() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase8b_audit_record_jsonl",
            "phase8c_audit_store_verification_report",
            "phase8d_audit_query_result",
            "phase8e_audit_export_manifest",
            "phase8e_audit_export_summary",
            "phase8g_export_integrity_report",
            "phase8m_signature_verifier_report",
            "phase8o_final_acceptance_pack",
            "current purpose",
            "current mutation boundary",
            "current integrity boundary",
            "future actor attribution touchpoint",
            "approval boundary",
        ),
        label="phase 8 artifact token",
    )


def test_phase10b_phase9_context_assertions() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase9c_operator_registry",
            "phase9d_actor_attribution_report",
            "phase9f_rbac_advisory_report",
            "phase9g_acceptance_pack",
            "current purpose",
            "current trust boundary",
            "future audit integration role",
            "approval boundary",
        ),
        label="phase 9 context token",
    )


def test_phase10b_future_audit_actor_field_assertions() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "audit_actor_schema_version",
            "audit_actor_id",
            "audit_actor_type",
            "audit_actor_identity_assurance",
            "audit_actor_identity_source",
            "audit_actor_role_labels",
            "audit_actor_registry_reference",
            "audit_actor_attribution_reference",
            "audit_rbac_advisory_reference",
            "audit_signature_evidence_reference",
            "audit_approval_boundary_reference",
            "audit_actor_privacy_classification",
            "audit_actor_added_at_phase",
            "audit_actor_boundary_statement",
            "fields are optional for backward compatibility",
            "fields are attribution-only",
            "fields must not affect hash-chain validation unless a future phase explicitly defines versioned hash inclusion",
            "fields must not imply authentication",
            "fields must not imply approval",
        ),
        label="future audit actor field token",
    )


def test_phase10b_binding_model_assertions() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "actor_source_type",
            "actor_source_path",
            "actor_source_hash_reference",
            "actor_id",
            "actor_type",
            "actor_identity_assurance",
            "actor_identity_source",
            "actor_role_labels",
            "actor_binding_status",
            "actor_boundary_statement",
            "actor source binding is not authentication",
            "actor source binding is not approval",
            "rbac_source_type",
            "rbac_source_path",
            "rbac_source_hash_reference",
            "advisory_decision",
            "decision_reason",
            "obligations",
            "denial_reasons",
            "rbac_policy_status",
            "rbac_enforcement_status",
            "rbac_boundary_statement",
            "rbac advisory source binding is not enforcement",
            "allow is not approval",
            "deny is not incident by itself",
            "signature_source_type",
            "signature_source_path",
            "signature_source_hash_reference",
            "signature_verification_status",
            "signed_payload_hash_status",
            "export_integrity_status",
            "key_management_runtime_status",
            "verified signature is not approval",
            "export integrity passed is not approval",
            "local signature/verifier remains prototype only",
        ),
        label="binding model token",
    )


def test_phase10b_append_only_hash_chain_assertions() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 8b append-only jsonl must remain append-only",
            "future actor attribution should not rewrite existing audit records",
            "future attribution may be appended as separate actor attribution event records or emitted in derived reports",
            "existing audit record hashes must remain valid",
            "backfill must be report-only unless a later phase explicitly designs append-only backfill events",
            "existing hash-chain verification must remain valid",
            "actor attribution added after the fact must not invalidate old hash chains",
            "future hash inclusion must use explicit schema versioning",
            "derived actor-attributed reports must clearly separate source audit hash from derived actor context hash",
            "hash validity is not approval",
        ),
        label="append-only/hash-chain token",
    )


def test_phase10b_query_export_final_acceptance_assertions() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "future query/report outputs may support actor filters",
            "actor_id",
            "actor_type",
            "identity_assurance",
            "role label",
            "advisory decision",
            "attribution source",
            "actor filters are search/report features only",
            "actor filters must not approve or execute anything",
            "future export packs may include actor attribution sidecar files",
            "actor attribution sidecars must preserve source manifest hashes",
            "export pack inclusion is not approval",
            "signed export remains not approval",
            "verified export remains not approval",
            "future final acceptance packs may reference actor-attributed audit reports",
            "final acceptance evidence remains not approval",
            "reviewer action remains guidance only",
        ),
        label="query/export/final acceptance token",
    )


def test_phase10b_future_contract_assertions() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "audit_event_type",
            "audit_event_id",
            "audit_event_timestamp_utc",
            "source_phase",
            "source_artifact_reference",
            "actor_context_reference",
            "rbac_advisory_reference",
            "signature_evidence_reference",
            "report_schema_version",
            "source_audit_records",
            "actor_context_summary",
            "rbac_advisory_summary",
            "signature_evidence_summary",
            "actor_attributed_records",
            "actor_filter_summary",
            "export_schema_version",
            "source_manifest_reference",
            "actor_attribution_sidecar_reference",
            "rbac_advisory_sidecar_reference",
            "compatibility_matrix",
            "phase 10b does not modify runtime input contracts",
            "phase 10b does not emit runtime reports",
            "phase 10b does not emit runtime exports",
        ),
        label="future contract token",
    )


def test_phase10b_migration_backward_compatibility_assertions() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 10b design-only",
            "phase 10c local evidence bundle design/prototype",
            "phase 10d derived actor-attributed audit report prototype",
            "phase 10e export sidecar design/prototype",
            "later schema versioning for audit actor fields",
            "existing phase 8 artifacts must remain readable",
            "existing hash chains must remain valid",
            "actor attribution must be additive/derived unless later explicitly versioned",
            "approval boundary must be preserved",
        ),
        label="migration/backward compatibility token",
    )


def test_phase10b_privacy_secret_assertions() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "prefer pseudonymous actor_id",
            "avoid raw email",
            "avoid full legal name",
            "store actor_display_label only when needed",
            "separate stable actor_id from display label",
            "never store secrets as actor attribution metadata",
            "minimize registry-derived fields",
            "support future redaction",
            "actor attribution integration must never store raw affiliate_phase8l_prototype_key",
            "must never store private keys",
            "must never store api keys",
            "must never store oauth/oidc/saml tokens",
            "must never store database passwords",
            "must never store affiliate credentials",
        ),
        label="privacy/secret token",
    )


def test_phase10b_approval_boundary_assertions() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "actor attribution integration plan is not runtime integration",
            "audit actor attribution is not authentication",
            "audit actor attribution is not approval",
            "audit actor field presence is not approval",
            "actor metadata validity is not approval",
            "registry presence is not authentication",
            "registry presence is not approval",
            "rbac advisory decision is not approval",
            "rbac allow decision is not approval",
            "signature verification remains not approval",
            "final acceptance remains not approval",
            "integrated audit evidence is not approval",
            "approval remains phase 7d selected-gate manual boundary",
            "integration plan must not trigger wrapper",
            "integration plan must not execute primitives",
            "integration plan must not trigger next gate",
            "integration plan must not set approval flags",
        ),
        label="approval boundary token",
    )


def test_phase10b_runtime_safety_assertions() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 10b adds no runtime",
            "future runtime must not rewrite existing audit records",
            "future runtime must not invalidate hash chains",
            "future runtime must not call phase 7d wrapper",
            "future runtime must not execute primitives",
            "future runtime must not write vault",
            "future runtime must not mutate phase 8 source outputs",
            "future runtime must not mutate phase 9 source outputs",
            "future runtime must write only to its own tmp output root",
            "future runtime must remain advisory/evidence only unless a later phase explicitly changes scope",
        ),
        label="runtime safety token",
    )


def test_phase10b_compatibility_assertions() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "phase 10b follows phase 10a governed readiness model",
            "phase 10b narrows readiness design toward audit store actor attribution",
            "phase 10b does not implement the readiness package runtime",
            "phase 10b follows phase 9g acceptance boundaries",
            "phase 10b may reference phase 9d actor attribution conceptually",
            "phase 10b may reference phase 9c registry conceptually",
            "phase 10b may reference phase 9f advisory rbac conceptually",
            "phase 10b does not modify phase 9 runtime",
            "actor attribution remains evidence only",
            "registry presence remains not authentication",
            "rbac advisory report remains evidence only",
            "phase 10b may reference phase 8 audit/export/signature/final acceptance artifacts conceptually",
            "phase 10b does not modify phase 8 runtime",
            "phase 8b append-only behavior remains unchanged",
            "phase 8c verification behavior remains unchanged",
            "phase 8d query behavior remains unchanged",
            "phase 8e export behavior remains unchanged",
            "phase 8g/8m verification behavior remains unchanged",
            "signature verification remains not approval",
            "final acceptance remains not approval",
            "phase 7d remains selected-gate manual approval runtime",
            "phase 10b does not modify phase 7d",
        ),
        label="compatibility token",
    )


def test_phase10b_failure_taxonomy_assertions() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "audit_actor_context_missing",
            "audit_actor_context_untrusted",
            "audit_actor_schema_missing",
            "audit_actor_schema_incompatible",
            "source_audit_record_missing",
            "source_hash_chain_unavailable",
            "source_hash_chain_invalid",
            "actor_source_binding_missing",
            "actor_source_binding_untrusted",
            "rbac_advisory_binding_missing",
            "rbac_advisory_binding_untrusted",
            "signature_evidence_binding_missing",
            "signature_evidence_binding_untrusted",
            "export_sidecar_missing",
            "export_sidecar_incompatible",
            "backward_compatibility_risk",
            "privacy_review_required",
            "secret_metadata_detected",
            "approval_inference_detected",
            "primitive_execution_intent_detected",
            "vault_mutation_intent_detected",
            "runtime_scope_violation",
            "audit_actor_integration_review_required",
            "evidence_review_required",
            "actor_context_review_required",
            "rbac_advisory_review_required",
            "signature_review_required",
            "approval_boundary_review_required",
            "primitive_execution_blocked",
            "vault_mutation_blocked",
            "no_action_required",
            "manual_review_required",
            "reject_audit_actor_integration_until_resolved",
            "reject_runtime_scope_until_resolved",
        ),
        label="failure taxonomy token",
    )


def test_phase10b_documentation_regression_references() -> None:
    _assert_all_tokens(_text(ROADMAP), ("Phase 10B", "Phase 5", "read-only", "manual-approved"), label="roadmap token")
    _assert_all_tokens(
        _text(PROJECT_STATE),
        (
            "docs/PHASE10B_ACTOR_ATTRIBUTION_AUDIT_STORE_INTEGRATION_PLAN.md",
            "Current architecture",
            "no database",
            "no FastAPI",
            "no UI",
            "no external APIs",
            "no autopublish",
        ),
        label="project state token",
    )
    for path in (
        PHASE10A_DOC,
        PHASE9G_DOC,
        PHASE9D_DOC,
        PHASE9C_DOC,
        PHASE8O_DOC,
        PHASE8E_DOC,
        PHASE8C_DOC,
        PHASE8B_COMPAT_DOC,
    ):
        assert "Phase 10B" in _text(path), f"missing Phase 10B reference in {path}"


def test_phase10b_protected_runtime_files_unchanged() -> None:
    for path, expected_hash in PROTECTED_HASHES.items():
        assert path.is_file(), f"missing protected runtime file: {path}"
        assert _sha256(path) == expected_hash, f"protected runtime file changed: {path}"


def test_phase10b_no_implementation_files_added() -> None:
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
        "**/*phase10b*.py",
        "**/*phase10b*.sh",
        "**/*audit*store*runtime*",
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
            if path.is_file() and ("phase10b" in path.name.lower() or "runtime" in path.name.lower())
        ]
        assert matches == [], f"unexpected implementation file(s): {matches}"


def test_phase10b_static_safety_for_new_docs_only() -> None:
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


def test_phase10b_repo_wide_artifact_safety() -> None:
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
