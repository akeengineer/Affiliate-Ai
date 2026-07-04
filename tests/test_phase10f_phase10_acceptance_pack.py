from __future__ import annotations

import hashlib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/079-phase10f-phase10-acceptance-pack.md"
DOC = REPO_ROOT / "docs/PHASE10F_PHASE10_ACCEPTANCE_PACK.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE10E_DOC = REPO_ROOT / "docs/PHASE10E_EXPORT_SIDECAR_DESIGN_PROTOTYPE.md"
PHASE10D_DOC = REPO_ROOT / "docs/PHASE10D_DERIVED_ACTOR_ATTRIBUTED_AUDIT_REPORT_PROTOTYPE.md"
PHASE10C_DOC = REPO_ROOT / "docs/PHASE10C_LOCAL_EVIDENCE_BUNDLE_ACTOR_RBAC_CONTEXT.md"
PHASE10B_DOC = REPO_ROOT / "docs/PHASE10B_ACTOR_ATTRIBUTION_AUDIT_STORE_INTEGRATION_PLAN.md"
PHASE10A_DOC = REPO_ROOT / "docs/PHASE10A_GOVERNED_RUNTIME_INTEGRATION_READINESS_DESIGN.md"
PHASE9G_DOC = REPO_ROOT / "docs/PHASE9G_PHASE9_ACCEPTANCE_PACK.md"
PHASE8O_DOC = REPO_ROOT / "docs/PHASE8O_FINAL_ACCEPTANCE_PACK.md"

PHASE10F_RUNTIME = REPO_ROOT / "scripts/dev/build_phase10f_phase10_acceptance_pack.py"
PHASE10F_RUNNER = REPO_ROOT / "scripts/dev/run_phase10f_phase10_acceptance_pack.sh"

PROTECTED_HASHES = {
    REPO_ROOT / "scripts/dev/build_phase10e_export_sidecar.py": "d5670eb340eeb21b0263577d7703c7749b70090740420d92e0e06c1a59fd5026",
    REPO_ROOT / "scripts/dev/run_phase10e_export_sidecar.sh": "3c9a3bcdaaa4c9607488e91d8b74e3f0d93f3d2c400bd0cb1ce24b17196f3acc",
    REPO_ROOT / "scripts/dev/build_phase10d_actor_attributed_audit_report.py": "b2ab24a69651a4abc13455e31f7c9d9cdfcb09f6d42d8ecd54b59853a1d91dcf",
    REPO_ROOT / "scripts/dev/run_phase10d_actor_attributed_audit_report.sh": "ad6b4d4390d2e6df28154673b01c224fd7457c30ec32a75c8c5c66526ecaa793",
    REPO_ROOT / "scripts/dev/build_phase10c_local_evidence_bundle.py": "7fc1b5aee0438871fae5112f602d2b1adb1f12bafa75b4994bfccc9dd8356a22",
    REPO_ROOT / "scripts/dev/run_phase10c_local_evidence_bundle.sh": "12c605905c6ee7bcdfc93c8f14968831963ecbb1692ba3f12bbb33e7fb0d04cf",
    REPO_ROOT / "scripts/dev/evaluate_phase9f_local_rbac_policy.py": "bea1e09dd14124f4d07439dfbb905a23e4ecfb71269fff8ff469a1ca8d461b64",
    REPO_ROOT / "scripts/dev/run_phase9f_local_rbac_policy.sh": "e43b58a44287d0bdf87c89e599781afcf1d0cd9aa600d457978a3121e9f24951",
    REPO_ROOT / "scripts/dev/build_phase9d_actor_attribution_report.py": "46b20935f235fc48a60737ed167a3f612b95afacdd978c326f110b61bf9af473",
    REPO_ROOT / "scripts/dev/run_phase9d_actor_attribution_report.sh": "900513d415be02280437752e4aefb9af6fbff3ab55c684f2943c20e43dc2fc43",
    REPO_ROOT / "scripts/dev/manage_phase9c_local_operator_registry.py": "19d8f8eea523c1b7014463fb351764842429dcb30076e4469a959bd7c326fb6e",
    REPO_ROOT / "scripts/dev/run_phase9c_local_operator_registry.sh": "6526dbeb53cbeeecf1485e73747ebee7f26e62c12f04295616c77b0f869bb21a",
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
    REPO_ROOT / "scripts/dev/build_phase8l_detached_signature.py": "6a7fddfbb3077c18816b81c57738bd79471db5a3f578d35292fde8e8f318de09",
    REPO_ROOT / "scripts/dev/run_phase8l_detached_signature.sh": "ecd3d6846702948f5a9b77addcd6254ea3a7295dcb01765ebcad91ced1a196cb",
    REPO_ROOT / "scripts/dev/verify_phase8m_detached_signature.py": "ef26e4f11f5ecb73e31f01261b56adb35df223f514edc0986e32f9d00d441aca",
    REPO_ROOT / "scripts/dev/run_phase8m_detached_signature_verifier.sh": "de6cd990e794d5893d31f682a9c7073a350af30c701665c43729d0d889095ff0",
    REPO_ROOT / "scripts/dev/run_phase7d_single_gate_wrapper.sh": "372aef7a133950a24a1de859a1ba0c01486fd2c84bf46ded783105acc4e47b7d",
    REPO_ROOT / "scripts/dev/execute_single_gate_approval.py": "1b1d00817b1ae89c2840f18c9fe3b73f091abec9c900bf0bff83ad6820e9cebb",
}

FORBIDDEN_EXTENSIONS = (".pem", ".key", ".crt", ".p12", ".pfx", ".sql", ".sqlite", ".db", ".rego")
EXCLUDED_PARTS = {".git", ".venv", "tmp", "vault", "node_modules", "vendor", "__pycache__"}
ALLOWED_PHASE10F_DOCS = {
    DOC,
    ROADMAP,
    PROJECT_STATE,
    PHASE10E_DOC,
    PHASE10D_DOC,
    PHASE10C_DOC,
    PHASE10B_DOC,
    PHASE10A_DOC,
    PHASE9G_DOC,
    PHASE8O_DOC,
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(_text(path).lower().replace("`", "").split())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _assert_all_tokens(text: str, tokens: tuple[str, ...] | list[str], *, label: str) -> None:
    for token in tokens:
        assert token in text, f"missing {label}: {token}"


def _repo_files():
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        yield path


def test_phase10f_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 10F file: {path}"


def test_phase10f_no_runtime_script_or_runner() -> None:
    assert not PHASE10F_RUNTIME.exists(), "Phase 10F must not add runtime script"
    assert not PHASE10F_RUNNER.exists(), "Phase 10F must not add shell runner"
    dev = REPO_ROOT / "scripts/dev"
    for pattern in ("*phase10f*.py", "*phase10f*.sh"):
        matches = sorted(str(path.relative_to(REPO_ROOT)) for path in dev.glob(pattern))
        assert matches == [], f"unexpected Phase 10F runtime file: {matches}"


def test_phase10f_status_tokens() -> None:
    assert "phase10f_status: success" in _text(TASK_FILE)
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "phase10f_status: success",
            "phase10e_status: success",
            "phase10d_status: success",
            "phase10c_status: success",
            "phase10b_status: success",
            "phase10a_status: success",
            "phase7d_runtime_readiness: implemented_manual_gate",
            "durable_audit_store_status: phase8_final_acceptance_pack",
            "audit_actor_attribution_integration_status: derived_report_prototype",
            "governed_runtime_integration_status: local_evidence_bundle_actor_report_and_export_sidecar_prototypes",
            "integration_runtime_status: local_export_sidecar_prototype",
            "local_evidence_bundle_status: prototype_local_only",
            "actor_attributed_audit_report_status: prototype_local_only",
            "export_sidecar_status: prototype_local_only",
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


def test_phase10f_scope_safety_tokens() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "docs/tests acceptance pack",
            "no new runtime scripts",
            "no shell runner",
            "no auth runtime",
            "no rbac enforcement",
            "no backend/api/database",
            "no key/cert files",
            "no export mutation",
            "no re-signing",
            "no wrapper behavior change",
            "no primitive execution",
            "no vault read/write",
            "no production deployment",
            "phase 10f closes phase 10",
            "phase 10f adds acceptance evidence only",
            "phase 10f does not add capability",
            "phase 10f does not add runtime",
        ),
        label="scope safety token",
    )


def test_phase10f_required_sections_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "### Purpose",
            "### Scope",
            "### Current trust boundary after Phase 10E",
            "### Phase 10 component summary",
            "### Phase 10A acceptance summary",
            "### Phase 10B acceptance summary",
            "### Phase 10C acceptance summary",
            "### Phase 10D acceptance summary",
            "### Phase 10E acceptance summary",
            "### Phase 10F acceptance summary",
            "### Safe demo scenarios",
            "### Acceptance criteria",
            "### Full-suite readiness checklist",
            "### PR readiness checklist",
            "### Merge readiness checklist",
            "### Runtime safety checklist",
            "### Governed integration checklist",
            "### Local evidence bundle checklist",
            "### Actor-attributed audit report checklist",
            "### Export sidecar checklist",
            "### Actor/RBAC context checklist",
            "### Signature/export integrity checklist",
            "### Approval boundary checklist",
            "### Protected runtime compatibility checklist",
            "### Artifact safety checklist",
            "### Known limitations",
            "### Recommended immediate next step",
            "### Recommended next major phase",
        ),
        label="section",
    )


def test_phase10f_phase10a_to_10e_summaries_exist() -> None:
    low = _flat(DOC)
    for token in (
        "10a governed runtime integration readiness design",
        "10b actor attribution integration plan for audit store",
        "10c local evidence bundle with actor/rbac context",
        "10d derived actor-attributed audit report prototype",
        "10e export sidecar design/prototype",
        "10f phase 10 acceptance pack",
        "artifact category",
        "runtime status",
        "mutation boundary",
        "safety boundary",
        "approval boundary",
    ):
        assert token in low, f"missing component summary token: {token}"


def test_phase10f_safe_demo_scenarios_are_local_only_and_non_executing() -> None:
    low = _flat(DOC)
    for token in (
        "build local evidence bundle with all evidence present",
        "build local evidence bundle with safe missing evidence warning",
        "reject unsafe evidence bundle manifest path",
        "build actor-attributed audit report with actor/rbac/evidence-bundle context",
        "actor-attributed audit report with safe missing context warning",
        "reject actor-attributed audit report with approval flag",
        "build export sidecar with export/evidence/actor/rbac/signature context",
        "export sidecar with safe missing export warning",
        "reject export sidecar with secret-like metadata",
        "verify export sidecar does not mutate export manifest",
        "verify derived outputs remain not approval",
        "local-only",
        "non-executing",
    ):
        assert token in low, f"missing safe demo token: {token}"
    for forbidden in (
        "--execute",
        "run_phase7d_single_gate_wrapper.sh",
        "execute_single_gate_approval.py",
        "curl ",
        "wget ",
        "http://",
        "https://",
        "sqlite3 ",
        "boto3",
        "aws ",
        "openssl ",
        "gpg ",
        "kubectl ",
        "docker ",
    ):
        assert forbidden not in low, f"forbidden demo command token present: {forbidden}"


def test_phase10f_focused_and_full_suite_checks_are_documented() -> None:
    low = _flat(DOC)
    for token in (
        "python -m pytest -q tests/test_phase10f_phase10_acceptance_pack.py",
        "python -m pytest -q tests/test_phase10e_export_sidecar.py",
        "python -m pytest -q tests/test_phase10d_actor_attributed_audit_report.py",
        "python -m pytest -q tests/test_phase10c_local_evidence_bundle.py",
        "python -m pytest -q tests/test_phase10b_actor_attribution_audit_store_integration_plan.py",
        "python -m pytest -q tests/test_phase10a_governed_runtime_integration_readiness_design.py",
        "python -m pytest -q tests/test_phase9f_local_rbac_policy_prototype.py",
        "python -m pytest -q tests/test_phase9d_actor_attribution_report_prototype.py",
        "python -m pytest -q tests/test_phase9c_local_operator_registry_prototype.py",
        "python -m pytest -q tests/test_phase8o_final_acceptance_pack.py",
        "python -m pytest -q tests/test_phase8m_detached_signature_verifier_prototype.py",
        "python -m pytest -q tests/test_phase8l_local_detached_signature_prototype.py",
        "python -m pytest -q tests/test_phase8h_export_integrity_verifier_hardening.py",
        "python -m pytest -q tests/test_phase8g_export_integrity_verifier.py",
        "python -m pytest -q tests/test_phase8e_audit_export_pack.py",
        "python -m pytest -q tests/test_phase7d_single_gate_wrapper.py",
        "env -u affiliate_require_operator_runtime python -m pytest -q",
        "git diff --check",
        "hardcoded path grep over scripts",
    ):
        assert token in low, f"missing verification token: {token}"


def test_phase10f_immediate_next_step_and_phase11_wording() -> None:
    for path in (TASK_FILE, DOC):
        low = _flat(path)
        _assert_all_tokens(
            low,
            (
                "recommended immediate next step",
                "complete phase 10 pr readiness",
                "run focused checks",
                "run full suite",
                "confirm clean worktree",
                "push feature/phase10-governed-runtime-integration",
                "open one pr for phase 10",
                "wait for ci green",
                "squash merge",
                "sync main",
                "delete feature branch",
                "pr readiness is not approval",
                "merge readiness is not approval",
                "ci green is not approval",
                "acceptance evidence is not approval",
                "approval remains phase 7d selected-gate manual boundary",
                "recommended next major phase",
                "phase 11 — production boundary and hardening readiness",
                "phase 11 should not immediately implement production authentication, rbac enforcement, key custody, backend/api/database, production signing, or production policy engine unless explicitly approved",
                "phase 11 should first define the production boundary, hardening requirements, ci gates, observability model, secrets/key custody design, backup/recovery posture, and controlled promotion path from local-only prototypes to governed production candidates",
                "phase 10 ends with acceptance evidence and pr readiness",
                "phase 11 begins with production-boundary design, not premature production runtime",
            ),
            label=f"readiness wording in {path.name}",
        )


def test_phase10f_acceptance_criteria_and_boundary_assertions_exist() -> None:
    low = _flat(DOC)
    for token in (
        "phase 10a–10e checkpoints exist",
        "phase 10f acceptance doc exists",
        "phase 10f tests pass",
        "phase 10a/10b/10c/10d/10e focused regressions pass",
        "phase 9f/9d/9c focused regressions pass",
        "phase 8o/8m/8l/8h/8g/8e focused regressions pass",
        "phase 7d focused regression passes",
        "full suite passes before pr",
        "no new runtime in 10f",
        "no auth runtime",
        "no rbac enforcement",
        "no production policy engine",
        "no backend/api/database",
        "no key/cert files",
        "no export mutation",
        "no re-signing",
        "no primitive execution",
        "no vault write",
        "no wrapper behavior change",
        "no phase 10e/10d/10c runtime behavior change",
        "no phase 9 runtime behavior change",
        "no phase 8 runtime behavior change",
        "approval boundary statements preserved",
        "phase 10 acceptance pack is not approval",
        "governed runtime integration readiness is not approval",
        "export sidecar is not approval",
        "verified export is not approval",
        "signed export is not approval",
        "rbac advisory context is not enforcement",
    ):
        assert token in low, f"missing acceptance/boundary token: {token}"


def test_phase10f_protected_runtime_hashes_unchanged() -> None:
    for path, expected in PROTECTED_HASHES.items():
        assert path.is_file(), f"missing protected file: {path}"
        assert _sha256(path) == expected, f"protected runtime changed unexpectedly: {path}"


def test_phase10f_no_risky_artifacts_added() -> None:
    package_json = REPO_ROOT / "package.json"
    assert not package_json.exists(), "package.json must not be added"
    for path in _repo_files():
        suffix = path.suffix.lower()
        assert suffix not in FORBIDDEN_EXTENSIONS, f"forbidden artifact added: {path.relative_to(REPO_ROOT)}"
        assert path.name != "workflow.yml", f"unexpected workflow file added: {path.relative_to(REPO_ROOT)}"


def test_phase10f_cross_phase_pointers_exist_only_in_allowed_docs() -> None:
    matched = set()
    for path in (REPO_ROOT / "docs").glob("*.md"):
        text = _text(path)
        if "Phase 10F" in text or "PHASE10F_PHASE10_ACCEPTANCE_PACK.md" in text:
            matched.add(path)
    assert matched == ALLOWED_PHASE10F_DOCS, (
        "Phase 10F pointers drifted outside allowed docs: "
        f"{sorted(str(path.relative_to(REPO_ROOT)) for path in matched)}"
    )


def test_phase10f_docs_and_state_references_present() -> None:
    assert "Phase 10F" in _text(ROADMAP)
    assert "Phase 10F" in _text(PROJECT_STATE)
    assert "docs/PHASE10F_PHASE10_ACCEPTANCE_PACK.md" in _text(PROJECT_STATE)
    assert "Phase 5" in _text(ROADMAP)
    assert "read-only" in _text(ROADMAP)
    assert "manual-approved" in _text(ROADMAP)
    state = _text(PROJECT_STATE)
    for token in ("Current architecture", "no database", "no FastAPI", "no UI", "no external APIs", "no autopublish"):
        assert token in state, f"missing PROJECT_STATE token: {token}"

