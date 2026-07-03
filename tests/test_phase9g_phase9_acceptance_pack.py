from __future__ import annotations

import hashlib
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/073-phase9g-phase9-acceptance-pack.md"
DOC = REPO_ROOT / "docs/PHASE9G_PHASE9_ACCEPTANCE_PACK.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE9F_DOC = REPO_ROOT / "docs/PHASE9F_LOCAL_RBAC_POLICY_PROTOTYPE.md"
PHASE9E_DOC = REPO_ROOT / "docs/PHASE9E_RBAC_DESIGN.md"
PHASE9D_DOC = REPO_ROOT / "docs/PHASE9D_ACTOR_ATTRIBUTION_IN_AUDIT_REPORTS.md"
PHASE9C_DOC = REPO_ROOT / "docs/PHASE9C_LOCAL_OPERATOR_REGISTRY_PROTOTYPE.md"
PHASE9B_DOC = REPO_ROOT / "docs/PHASE9B_ACTOR_METADATA_SCHEMA_DESIGN.md"
PHASE9A_DOC = REPO_ROOT / "docs/PHASE9A_OPERATOR_IDENTITY_BOUNDARY_DESIGN.md"
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
    REPO_ROOT / "scripts/dev/run_phase7d_single_gate_wrapper.sh": "372aef7a133950a24a1de859a1ba0c01486fd2c84bf46ded783105acc4e47b7d",
    REPO_ROOT / "scripts/dev/execute_single_gate_approval.py": "1b1d00817b1ae89c2840f18c9fe3b73f091abec9c900bf0bff83ad6820e9cebb",
}

EXCLUDED_PARTS = {".git", ".venv", "tmp", "vault", "node_modules", "vendor"}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(_text(path).lower().replace("`", "").split())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# A. File existence and status
# ---------------------------------------------------------------------------


def test_phase9g_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 9G file: {path}"


def test_phase9g_no_runtime_script_or_runner() -> None:
    dev = REPO_ROOT / "scripts/dev"
    for pattern in ("*phase9g*.py", "*phase9g*.sh"):
        matches = sorted(p.name for p in dev.glob(pattern))
        assert matches == [], f"unexpected Phase 9G runtime file: {matches}"


def test_phase9g_task_status_token() -> None:
    assert "phase9g_status: success" in _text(TASK_FILE)


def test_phase9g_doc_status_tokens() -> None:
    text = _text(DOC)
    for token in (
        "phase9g_status: success",
        "phase9a_status: success",
        "phase9b_status: success",
        "phase9c_status: success",
        "phase9d_status: success",
        "phase9e_status: success",
        "phase9f_status: success",
        "rbac_policy_status: local_advisory_prototype",
        "rbac_runtime_status: local_advisory_prototype",
        "rbac_enforcement_status: not_implemented",
        "authentication_runtime_status: not_implemented",
        "key_management_runtime_status: not_implemented",
        "phase9_branch_workflow: enabled",
    ):
        assert token in text, f"missing status token: {token}"


# ---------------------------------------------------------------------------
# B. Scope safety
# ---------------------------------------------------------------------------


def test_phase9g_scope_safety_tokens() -> None:
    low = _flat(DOC)
    for token in (
        "docs/tests acceptance pack",
        "no new runtime scripts",
        "no shell runner",
        "no auth runtime",
        "no rbac enforcement",
        "no backend/api/database",
        "no key/cert files",
        "no wrapper behavior change",
        "no primitive execution",
        "no vault read/write",
        "no production deployment",
    ):
        assert token in low, f"missing scope safety token: {token}"


# ---------------------------------------------------------------------------
# C. Required sections
# ---------------------------------------------------------------------------


def test_phase9g_required_sections() -> None:
    text = _text(DOC)
    for token in (
        "### Purpose",
        "### Scope",
        "### Current trust boundary after Phase 9F",
        "### Phase 9 component summary",
        "### Safe demo scenarios",
        "### Acceptance criteria",
        "### Full-suite readiness checklist",
        "### PR readiness checklist",
        "### Merge readiness checklist",
        "### Runtime safety checklist",
        "### Identity boundary checklist",
        "### Actor metadata checklist",
        "### Registry checklist",
        "### Attribution checklist",
        "### RBAC advisory checklist",
        "### Approval boundary checklist",
        "### Protected runtime compatibility checklist",
        "### Artifact safety checklist",
        "### Known limitations",
        "### Recommended next major phase",
    ):
        assert token in text, f"missing section: {token}"


# ---------------------------------------------------------------------------
# D. Component summary assertions
# ---------------------------------------------------------------------------


def test_phase9g_component_summary_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "9a operator identity boundary design",
        "9b actor metadata schema design",
        "9c local operator registry prototype",
        "9d actor attribution in audit/reports",
        "9e rbac design",
        "9f local rbac policy prototype",
        "9g phase 9 acceptance pack",
        "artifact category",
        "runtime status",
        "safety boundary",
        "approval boundary",
    ):
        assert token in low, f"missing component summary token: {token}"


# ---------------------------------------------------------------------------
# E. Safe demo scenario assertions
# ---------------------------------------------------------------------------


def test_phase9g_safe_demo_scenario_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "valid local operator registry build",
        "registry secret/privacy rejection",
        "actor attribution report build",
        "actor attribution actor-not-found rejection",
        "rbac advisory allow",
        "rbac explicit deny precedence",
        "rbac execute_primitive hard block",
        "require_phase7d_selected_gate",
        "final acceptance evidence attribution without approval inference",
    ):
        assert token in low, f"missing scenario token: {token}"
    assert "all scenario commands are local-only" in low
    for token in (
        "approval flags",
        "--execute",
        "wrapper calls",
        "primitive calls",
        "network calls",
        "backend/api/database calls",
        "key commands",
    ):
        assert token in low, f"missing scenario safety token: {token}"


# ---------------------------------------------------------------------------
# F. Acceptance criteria assertions
# ---------------------------------------------------------------------------


def test_phase9g_acceptance_criteria_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "phase 9a–9f checkpoints exist",
        "phase 9g acceptance doc exists",
        "phase 9g tests pass",
        "phase 9a/9b/9c/9d/9e/9f focused regressions pass",
        "phase 8o/8m/8l focused regressions pass",
        "phase 7d focused regression passes",
        "full suite passes before pr",
        "no new runtime in 9g",
        "no auth runtime",
        "no rbac enforcement",
        "no production policy engine",
        "no backend/api/database",
        "no key/cert files",
        "no primitive execution",
        "no vault write",
        "no wrapper behavior change",
        "no phase 8 runtime behavior change",
        "no phase 9c/9d/9f runtime behavior change",
        "approval boundary statements preserved",
    ):
        assert token in low, f"missing acceptance criteria token: {token}"


# ---------------------------------------------------------------------------
# G. Full-suite / PR / merge readiness assertions
# ---------------------------------------------------------------------------


def test_phase9g_readiness_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "env -u affiliate_require_operator_runtime python -m pytest -q",
        "git diff --check",
        "hardcoded path grep over scripts",
        "worktree clean",
        "branch is feature/phase9-identity-boundary",
        "base is main",
        "complete phase 9 identity and rbac governance workflow",
        "phase 9a–9g summary",
        "focused test results",
        "full-suite result",
        "local-only prototype status",
        "no authentication runtime",
        "no rbac enforcement",
        "no backend/api/database",
        "no key/cert files",
        "no wrapper/primitive/vault mutation",
        "approval remains phase 7d selected-gate manual boundary",
        "do not merge until ci is green",
        "squash merge recommended",
    ):
        assert token in low, f"missing readiness token: {token}"


# ---------------------------------------------------------------------------
# H. Runtime safety assertions
# ---------------------------------------------------------------------------


def test_phase9g_runtime_safety_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "phase 9g added no runtime scripts",
        "phase 9g added no shell runner",
        "phase 9f remains advisory-only",
        "phase 9d remains attribution-only",
        "phase 9c remains local registry metadata-only",
        "no auth runtime",
        "no rbac enforcement",
        "no policy engine",
        "no backend/api/database",
        "no package.json",
        "no workflow/deployment",
        "no key/cert files",
        "no external apis",
        "no network",
        "no primitive execution",
        "no vault write",
    ):
        assert token in low, f"missing runtime safety token: {token}"


# ---------------------------------------------------------------------------
# I. Identity / actor / registry / attribution assertions
# ---------------------------------------------------------------------------


def test_phase9g_identity_actor_registry_attribution_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "identity boundary is design-only",
        "operator identity remains unauthenticated or operator-declared",
        "authenticated identity is not approval",
        "operator identity is not approval",
        "reviewer identity is not approval",
        "signer identity is not approval",
        "actor metadata schema exists",
        "schema validity is not approval",
        "actor_id is not approval",
        "identity assurance is not approval",
        "identity source is not approval",
        "session reference is not approval",
        "local operator registry is prototype_local_only",
        "registry presence is not authentication",
        "registry presence is not approval",
        "registry report is evidence only",
        "actor attribution is local_report_prototype",
        "actor attribution is not authentication",
        "actor attribution is not approval",
        "actor-attributed report is evidence only",
    ):
        assert token in low, f"missing identity/actor/registry/attribution token: {token}"


# ---------------------------------------------------------------------------
# J. RBAC advisory assertions
# ---------------------------------------------------------------------------


def test_phase9g_rbac_advisory_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "rbac design is design_only",
        "rbac policy status is local_advisory_prototype",
        "rbac runtime status is local_advisory_prototype",
        "rbac enforcement status is not_implemented",
        "local rbac policy prototype is not enforcement",
        "rbac allow decision is not approval",
        "rbac eligibility is not approval",
        "rbac advisory report is evidence only",
        "explicit deny precedence is advisory only",
        "execute_primitive is hard-blocked",
        "approve_selected_gate advisory allow still requires",
        "phase 7d selected-gate manual boundary",
    ):
        assert token in low, f"missing RBAC advisory token: {token}"


# ---------------------------------------------------------------------------
# K. Approval boundary assertions
# ---------------------------------------------------------------------------


def test_phase9g_approval_boundary_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "phase 9 acceptance pack is not approval",
        "acceptance pack evidence is not approval",
        "identity boundary is not approval",
        "actor metadata is not approval",
        "actor attribution is not approval",
        "local operator registry is not authentication",
        "registry presence is not approval",
        "local rbac policy prototype is not enforcement",
        "rbac allow decision is not approval",
        "rbac eligibility is not approval",
        "rbac advisory decision is not approval",
        "rbac advisory report is evidence only",
        "authenticated identity is not approval",
        "signature verification remains not approval",
        "final acceptance remains not approval",
        "approval remains phase 7d selected-gate manual boundary",
        "acceptance pack must not trigger wrapper",
        "acceptance pack must not execute primitives",
        "acceptance pack must not trigger next gate",
        "acceptance pack must not set approval flags",
    ):
        assert token in low, f"missing approval boundary token: {token}"


# ---------------------------------------------------------------------------
# L. Protected runtime compatibility assertions
# ---------------------------------------------------------------------------


def test_phase9g_protected_runtime_files_exist_and_unchanged() -> None:
    for path, digest in PROTECTED_HASHES.items():
        assert path.is_file(), f"missing protected runtime file: {path}"
        if digest is not None:
            assert _sha256(path) == digest, f"protected runtime changed: {path}"


def test_phase9g_no_implementation_files_added() -> None:
    dev = REPO_ROOT / "scripts/dev"
    for pattern in ("*phase9g*", "*policy*.rego", "*opa*"):
        matches = sorted(p.name for p in dev.glob(pattern))
        assert matches == [], f"unexpected Phase 9G implementation files ({pattern}): {matches}"
    assert not (REPO_ROOT / "package.json").exists()


# ---------------------------------------------------------------------------
# M. Artifact safety assertions
# ---------------------------------------------------------------------------


def test_phase9g_repo_wide_artifact_safety() -> None:
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        suffix = path.suffix.lower()
        assert suffix not in (".pem", ".key", ".crt", ".p12", ".pfx"), f"unexpected key/cert file: {path}"
        assert suffix not in (".sql", ".sqlite", ".db"), f"unexpected database file: {path}"
        assert suffix != ".rego", f"unexpected policy (.rego) file: {path}"
    assert not (REPO_ROOT / "package.json").exists()


def test_phase9g_artifact_safety_checklist_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "no .pem/.key/.crt/.p12/.pfx files",
        "no package.json",
        "no backend/api/database files",
        "no .sql/.sqlite/.db files",
        "no .rego files",
        "no opa policy files",
        "no production policy runtime files",
        "no oauth/oidc/saml config files",
        "no workflow/deployment files",
        "no key/cert material",
    ):
        assert token in low, f"missing artifact safety token: {token}"


# ---------------------------------------------------------------------------
# N. Documentation regression
# ---------------------------------------------------------------------------


def test_phase9g_documentation_regressions() -> None:
    roadmap = _text(ROADMAP)
    project_state = _text(PROJECT_STATE)
    assert "Phase 9G" in roadmap
    assert "docs/PHASE9G_PHASE9_ACCEPTANCE_PACK.md" in roadmap
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in roadmap, f"ROADMAP dropped token: {token}"

    assert "docs/PHASE9G_PHASE9_ACCEPTANCE_PACK.md" in project_state
    for token in ("Current architecture", "no database", "no FastAPI", "no UI",
                  "no external APIs", "no autopublish"):
        assert token in project_state, f"PROJECT_STATE dropped token: {token}"

    for doc in (PHASE9F_DOC, PHASE9E_DOC, PHASE9D_DOC, PHASE9C_DOC, PHASE9B_DOC, PHASE9A_DOC, PHASE8O_DOC):
        assert "Phase 9G" in _text(doc), f"missing Phase 9G reference in {doc.name}"


# ---------------------------------------------------------------------------
# O. Static safety for new Phase 9G docs/task only
# ---------------------------------------------------------------------------


def test_phase9g_static_safety_scan_new_files_only() -> None:
    banned = (
        "http://",
        "https://",
        "/home/ubuntu/Affiliate-Ai",
        "BEGIN RSA PRIVATE KEY",
        "BEGIN PRIVATE KEY",
        "BEGIN OPENSSH PRIVATE KEY",
        "AWS_SECRET_ACCESS_KEY",
        "OPENAI_API_KEY",
        "ssh-keygen",
        "openssl genrsa",
        "openssl req",
        "openssl enc",
        "gpg --gen-key",
        "curl ",
        "wget ",
        "uvicorn ",
        "fastapi",
        "sqlite3.connect",
        "sqlite3 ",
        "boto3.client",
        "boto3 ",
        "CREATE TABLE",
        "aws kms",
        "cryptography.hazmat",
        "python scripts/dev/execute_single_gate_approval.py",
        "bash scripts/dev/run_phase7d_single_gate_wrapper.sh",
        "opa eval",
    )
    for path in (TASK_FILE, DOC):
        text = _text(path)
        for token in banned:
            assert token not in text, f"{path.name} contains forbidden token: {token}"
        assert not re.search(r"approve_[a-z_]+\s*[:=]\s*true", text, flags=re.IGNORECASE)
