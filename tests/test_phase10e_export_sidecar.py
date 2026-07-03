from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/078-phase10e-export-sidecar-design-prototype.md"
DOC = REPO_ROOT / "docs/PHASE10E_EXPORT_SIDECAR_DESIGN_PROTOTYPE.md"
SCRIPT = REPO_ROOT / "scripts/dev/build_phase10e_export_sidecar.py"
RUNNER = REPO_ROOT / "scripts/dev/run_phase10e_export_sidecar.sh"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE10D_DOC = REPO_ROOT / "docs/PHASE10D_DERIVED_ACTOR_ATTRIBUTED_AUDIT_REPORT_PROTOTYPE.md"
PHASE10C_DOC = REPO_ROOT / "docs/PHASE10C_LOCAL_EVIDENCE_BUNDLE_ACTOR_RBAC_CONTEXT.md"
PHASE10B_DOC = REPO_ROOT / "docs/PHASE10B_ACTOR_ATTRIBUTION_AUDIT_STORE_INTEGRATION_PLAN.md"
PHASE10A_DOC = REPO_ROOT / "docs/PHASE10A_GOVERNED_RUNTIME_INTEGRATION_READINESS_DESIGN.md"
PHASE9D_DOC = REPO_ROOT / "docs/PHASE9D_ACTOR_ATTRIBUTION_IN_AUDIT_REPORTS.md"
PHASE9F_DOC = REPO_ROOT / "docs/PHASE9F_LOCAL_RBAC_POLICY_PROTOTYPE.md"
PHASE8E_DOC = REPO_ROOT / "docs/PHASE8E_AUDIT_EXPORT_PACK.md"
PHASE8G_DOC = REPO_ROOT / "docs/PHASE8G_EXPORT_INTEGRITY_VERIFIER.md"
PHASE8H_DOC = REPO_ROOT / "docs/PHASE8H_EXPORT_INTEGRITY_VERIFIER_HARDENING.md"
PHASE8L_DOC = REPO_ROOT / "docs/PHASE8L_LOCAL_DETACHED_SIGNATURE_PROTOTYPE.md"
PHASE8M_DOC = REPO_ROOT / "docs/PHASE8M_DETACHED_SIGNATURE_VERIFIER_PROTOTYPE.md"
PHASE8O_DOC = REPO_ROOT / "docs/PHASE8O_FINAL_ACCEPTANCE_PACK.md"
GITIGNORE = REPO_ROOT / ".gitignore"

OUTPUT_ROOT = REPO_ROOT / "tmp/phase10e-export-sidecar"
TEST_INPUT_ROOT = REPO_ROOT / "tmp/phase10e-test-input"

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
    REPO_ROOT / "scripts/dev/build_phase8l_detached_signature.py": "6a7fddfbb3077c18816b81c57738bd79471db5a3f578d35292fde8e8f318de09",
    REPO_ROOT / "scripts/dev/run_phase8l_detached_signature.sh": "ecd3d6846702948f5a9b77addcd6254ea3a7295dcb01765ebcad91ced1a196cb",
    REPO_ROOT / "scripts/dev/verify_phase8m_detached_signature.py": "ef26e4f11f5ecb73e31f01261b56adb35df223f514edc0986e32f9d00d441aca",
    REPO_ROOT / "scripts/dev/run_phase8m_detached_signature_verifier.sh": "de6cd990e794d5893d31f682a9c7073a350af30c701665c43729d0d889095ff0",
    REPO_ROOT / "scripts/dev/manage_phase9c_local_operator_registry.py": "19d8f8eea523c1b7014463fb351764842429dcb30076e4469a959bd7c326fb6e",
    REPO_ROOT / "scripts/dev/run_phase9c_local_operator_registry.sh": "6526dbeb53cbeeecf1485e73747ebee7f26e62c12f04295616c77b0f869bb21a",
    REPO_ROOT / "scripts/dev/build_phase9d_actor_attribution_report.py": "46b20935f235fc48a60737ed167a3f612b95afacdd978c326f110b61bf9af473",
    REPO_ROOT / "scripts/dev/run_phase9d_actor_attribution_report.sh": "900513d415be02280437752e4aefb9af6fbff3ab55c684f2943c20e43dc2fc43",
    REPO_ROOT / "scripts/dev/evaluate_phase9f_local_rbac_policy.py": "bea1e09dd14124f4d07439dfbb905a23e4ecfb71269fff8ff469a1ca8d461b64",
    REPO_ROOT / "scripts/dev/run_phase9f_local_rbac_policy.sh": "e43b58a44287d0bdf87c89e599781afcf1d0cd9aa600d457978a3121e9f24951",
    REPO_ROOT / "scripts/dev/build_phase10c_local_evidence_bundle.py": "7fc1b5aee0438871fae5112f602d2b1adb1f12bafa75b4994bfccc9dd8356a22",
    REPO_ROOT / "scripts/dev/run_phase10c_local_evidence_bundle.sh": "12c605905c6ee7bcdfc93c8f14968831963ecbb1692ba3f12bbb33e7fb0d04cf",
    REPO_ROOT / "scripts/dev/build_phase10d_actor_attributed_audit_report.py": "b2ab24a69651a4abc13455e31f7c9d9cdfcb09f6d42d8ecd54b59853a1d91dcf",
    REPO_ROOT / "scripts/dev/run_phase10d_actor_attributed_audit_report.sh": "ad6b4d4390d2e6df28154673b01c224fd7457c30ec32a75c8c5c66526ecaa793",
    REPO_ROOT / "scripts/dev/run_phase7d_single_gate_wrapper.sh": "372aef7a133950a24a1de859a1ba0c01486fd2c84bf46ded783105acc4e47b7d",
    REPO_ROOT / "scripts/dev/execute_single_gate_approval.py": "1b1d00817b1ae89c2840f18c9fe3b73f091abec9c900bf0bff83ad6820e9cebb",
}

FORBIDDEN_EXTENSIONS = (".pem", ".key", ".crt", ".p12", ".pfx", ".sql", ".sqlite", ".db", ".rego")
STATIC_STATUS_TOKENS = (
    "phase10e_status",
    "phase10d_status",
    "phase10c_status",
    "phase10b_status",
    "phase10a_status",
    "phase7d_runtime_readiness",
    "durable_audit_store_status",
    "audit_actor_attribution_integration_status",
    "governed_runtime_integration_status",
    "integration_runtime_status",
    "local_evidence_bundle_status",
    "actor_attributed_audit_report_status",
    "export_sidecar_status",
    "identity_boundary_status",
    "actor_metadata_schema_status",
    "actor_metadata_runtime_status",
    "local_operator_registry_status",
    "actor_attribution_status",
    "rbac_policy_status",
    "rbac_runtime_status",
    "rbac_enforcement_status",
    "identity_runtime_status",
    "authentication_runtime_status",
    "operator_identity_assurance_status",
    "signing_implementation_status",
    "signature_runtime_status",
    "signature_verifier_runtime_status",
    "key_management_runtime_status",
    "backend_api_database_status",
    "phase10_branch_workflow",
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(_text(path).lower().replace("`", "").split())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _assert_all_tokens(text: str, tokens: tuple[str, ...] | list[str], *, label: str) -> None:
    for token in tokens:
        assert token in text, f"missing {label}: {token}"


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _run_builder(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def _load_report(output_dir: Path) -> dict:
    return json.loads((output_dir / "export-sidecar.json").read_text(encoding="utf-8"))


def _sample_manifest(
    *,
    export_path: str,
    extra: dict | None = None,
    export_extra: dict | None = None,
) -> dict:
    manifest = {
        "sidecar_schema_version": "phase10e.export_sidecar.v1",
        "sidecar_id": "sidecar-phase10e-sample",
        "sidecar_purpose": "Derived export sidecar for local review.",
        "approval_boundary_statement": (
            "export sidecar is not approval; "
            "approval remains Phase 7D selected-gate manual boundary"
        ),
        "export_references": [
            {
                "export_id": "export-manifest-1",
                "export_type": "audit_export_manifest",
                "export_phase": "phase8e",
                "export_path": export_path,
                "export_purpose": "Primary export manifest fixture.",
                "export_boundary_statement": (
                    "export sidecar inclusion is not approval; "
                    "export manifest hash is not approval; "
                    "approval remains Phase 7D selected-gate manual boundary"
                ),
            }
        ],
    }
    if export_extra:
        manifest["export_references"][0].update(export_extra)
    if extra:
        manifest.update(extra)
    return manifest


@pytest.fixture()
def phase10e_workspace() -> Path:
    unique = uuid.uuid4().hex[:12]
    root = TEST_INPUT_ROOT / f"pytest-{unique}"
    root.mkdir(parents=True, exist_ok=True)
    try:
        yield root
    finally:
        shutil.rmtree(root, ignore_errors=True)
        shutil.rmtree(OUTPUT_ROOT / f"pytest-{root.name}", ignore_errors=True)
        shutil.rmtree(OUTPUT_ROOT / f"pytest-{root.name}-second", ignore_errors=True)
        shutil.rmtree(OUTPUT_ROOT / f"pytest-{root.name}-missing", ignore_errors=True)
        shutil.rmtree(OUTPUT_ROOT / f"pytest-{root.name}-invalid", ignore_errors=True)


def _make_valid_manifest(phase10e_workspace: Path) -> tuple[Path, Path, Path]:
    export_file = phase10e_workspace / "exports" / "audit-export-manifest.json"
    export_file.parent.mkdir(parents=True, exist_ok=True)
    export_file.write_text('{"export":"phase8e"}\n', encoding="utf-8")
    manifest = phase10e_workspace / "manifest.json"
    _write_json(manifest, _sample_manifest(export_path=str(export_file.relative_to(REPO_ROOT))))
    output_dir = OUTPUT_ROOT / f"pytest-{phase10e_workspace.name}"
    return manifest, export_file, output_dir


def _sidecar_hash_without_self(report: dict) -> str:
    clone = json.loads(json.dumps(report))
    clone.pop("sidecar_hash", None)
    return hashlib.sha256(_canonical_json(clone).encode("utf-8")).hexdigest()


# A. File existence and status


def test_phase10e_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, SCRIPT, RUNNER, THIS_TEST):
        assert path.is_file(), f"missing Phase 10E file: {path}"


def test_phase10e_status_tokens() -> None:
    assert "phase10e_status: success" in _text(TASK_FILE)
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
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


def test_phase10e_runner_is_executable_mode_755() -> None:
    mode = RUNNER.stat().st_mode & 0o777
    assert mode == 0o755, f"expected 0755, got {oct(mode)}"


# B. Scope safety


def test_phase10e_scope_safety_tokens() -> None:
    low = _flat(DOC)
    for token in (
        "local-only",
        "derived export sidecar",
        "standard library only",
        "no authentication",
        "no rbac enforcement",
        "no backend/api/database",
        "no wrapper behavior change",
        "no primitive execution",
        "no export mutation",
        "no re-signing",
    ):
        assert token in low, f"missing safety token: {token}"


def test_phase10e_script_no_forbidden_imports() -> None:
    text = _text(SCRIPT)
    for forbidden in (
        "import requests",
        "import httpx",
        "import urllib",
        "import sqlite3",
        "import boto3",
        "import subprocess",
        "from urllib",
        "from requests",
        "from httpx",
        "from boto3",
    ):
        assert forbidden not in text, f"forbidden import present: {forbidden}"


def test_phase10e_script_no_forbidden_runtime_calls() -> None:
    text = _flat(SCRIPT)
    for forbidden in (
        "run_phase7d_single_gate_wrapper",
        "execute_single_gate_approval",
        "build_phase8e_audit_export_pack",
        "verify_phase8g_export_integrity",
        "build_phase8l_detached_signature",
        "verify_phase8m_detached_signature",
        "build_phase10c_local_evidence_bundle",
        "build_phase10d_actor_attributed_audit_report",
        "subprocess.",
        " os.system(",
    ):
        assert forbidden not in text, f"script must not contain: {forbidden}"


def test_phase10e_runner_static_safety() -> None:
    text = _text(RUNNER)
    for forbidden in (
        "--execute",
        "run_phase7d_single_gate_wrapper.sh",
        "execute_single_gate_approval.py",
        "build_phase8e_audit_export_pack.py",
        "verify_phase8g_export_integrity.py",
        "build_phase8l_detached_signature.py",
        "verify_phase8m_detached_signature.py",
        "build_phase10c_local_evidence_bundle.py",
        "build_phase10d_actor_attributed_audit_report.py --execute",
        "vault/",
        "curl ",
        "wget ",
    ):
        assert forbidden not in text, f"runner must not contain: {forbidden}"


def test_phase10e_runner_bash_syntax_ok() -> None:
    result = subprocess.run(["bash", "-n", str(RUNNER)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_phase10e_script_py_compile_ok() -> None:
    result = subprocess.run([sys.executable, "-m", "py_compile", str(SCRIPT)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


# D. Valid sidecar behavior


def test_phase10e_valid_sidecar_builds(phase10e_workspace: Path) -> None:
    manifest, export_file, output_dir = _make_valid_manifest(phase10e_workspace)

    context_root = phase10e_workspace / "context"
    context_root.mkdir(parents=True, exist_ok=True)

    evidence_bundle = context_root / "evidence-bundle.json"
    actor_report = context_root / "actor-report.json"
    actor_context = context_root / "actor-context.json"
    rbac_context = context_root / "rbac-context.json"
    signature_context = context_root / "signature-context.json"
    integrity_context = context_root / "integrity-context.json"
    final_acceptance = context_root / "final-acceptance.json"
    boundary = context_root / "boundary.json"

    _write_json(
        evidence_bundle,
        {
            "bundle_id": "bundle-10c",
            "bundle_status": "built",
            "bundle_hash": "bundle-hash-10c",
            "evidence_reference_count": 1,
            "present_evidence_count": 1,
            "missing_evidence_count": 0,
            "approval_boundary_statement": "evidence bundle validity is not approval",
        },
    )
    _write_json(
        actor_report,
        {
            "report_id": "report-10d",
            "report_status": "built",
            "report_hash": "report-hash-10d",
            "audit_evidence_reference_count": 2,
            "present_evidence_count": 2,
            "missing_evidence_count": 0,
            "actor_context_summary": {"actor_id": "actor_operator_one"},
            "rbac_advisory_context_summary": {"advisory_decision": "allow"},
            "approval_boundary_statement": "actor-attributed audit report is not approval",
        },
    )
    _write_json(
        actor_context,
        {
            "actor_id": "actor_operator_one",
            "actor_type": "human_operator",
            "actor_identity_assurance": "operator_declared",
            "actor_identity_source": "environment_operator_label",
            "actor_role_labels": ["operator", "reviewer"],
            "actor_attribution_status": "local_report_prototype",
            "approval_boundary_statement": "actor context is not authentication",
        },
    )
    _write_json(
        rbac_context,
        {
            "advisory_decision": "allow",
            "decision_reason": "advisory only",
            "obligations": ["manual-review"],
            "denial_reasons": [],
            "rbac_policy_status": "local_advisory_prototype",
            "rbac_enforcement_status": "not_implemented",
            "approval_boundary_statement": "RBAC allow decision is not approval",
        },
    )
    _write_json(
        signature_context,
        {
            "signature_verification_status": "verified",
            "signed_payload_hash_status": "match",
            "verification_result": "success",
            "approval_boundary_statement": "verified signature remains not approval",
        },
    )
    _write_json(
        integrity_context,
        {
            "export_integrity_status": "verified",
            "compatibility_result": "compatible",
            "approval_boundary_statement": "verified export is not approval",
        },
    )
    _write_json(
        final_acceptance,
        {
            "phase8o_status": "success",
            "final_acceptance_status": "accepted",
            "reviewer_action": "manual_review_required",
            "approval_boundary_statement": "final acceptance remains not approval",
        },
    )
    _write_json(
        boundary,
        {
            "reference_type": "approval_boundary_reference",
            "approval_boundary_statement": "approval remains Phase 7D selected-gate manual boundary",
        },
    )

    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["evidence_bundle_reference"] = {
        "reference_type": "evidence_bundle_reference",
        "reference_path": str(evidence_bundle.relative_to(REPO_ROOT)),
        "reference_boundary_statement": "evidence bundle validity is not approval",
    }
    payload["actor_attributed_audit_report_reference"] = {
        "reference_type": "actor_attributed_audit_report_reference",
        "reference_path": str(actor_report.relative_to(REPO_ROOT)),
        "reference_boundary_statement": "actor-attributed audit report is not approval",
    }
    payload["actor_attribution_context_reference"] = {
        "reference_type": "actor_attribution_context_reference",
        "reference_path": str(actor_context.relative_to(REPO_ROOT)),
        "reference_boundary_statement": "actor context is not authentication",
    }
    payload["rbac_advisory_context_reference"] = {
        "reference_type": "rbac_advisory_context_reference",
        "reference_path": str(rbac_context.relative_to(REPO_ROOT)),
        "reference_boundary_statement": "RBAC advisory context is not enforcement",
    }
    payload["signature_context_reference"] = {
        "reference_type": "signature_context_reference",
        "reference_path": str(signature_context.relative_to(REPO_ROOT)),
        "reference_boundary_statement": "verified signature remains not approval",
    }
    payload["export_integrity_context_reference"] = {
        "reference_type": "export_integrity_context_reference",
        "reference_path": str(integrity_context.relative_to(REPO_ROOT)),
        "reference_boundary_statement": "verified export is not approval",
    }
    payload["final_acceptance_context_reference"] = {
        "reference_type": "final_acceptance_context_reference",
        "reference_path": str(final_acceptance.relative_to(REPO_ROOT)),
        "reference_boundary_statement": "final acceptance remains not approval",
    }
    payload["approval_boundary_reference"] = {
        "reference_type": "approval_boundary_reference",
        "reference_path": str(boundary.relative_to(REPO_ROOT)),
        "reference_boundary_statement": "approval remains Phase 7D selected-gate manual boundary",
    }
    _write_json(manifest, payload)

    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode == 0, result.stderr

    report = _load_report(output_dir)
    assert report["sidecar_status"] == "built"
    assert report["reviewer_action"] == "no_action_required"
    assert report["reviewer_action_required"] is False
    assert report["incident_classification"] == "none"
    assert report["export_reference_count"] == 1
    assert report["present_export_count"] == 1
    assert report["missing_export_count"] == 0
    assert report["invalid_export_count"] == 0
    assert report["optional_context_count"] == 8
    assert report["sidecar_hash"]

    export_ref = report["export_references"][0]
    assert export_ref["export_status"] == "present"
    assert export_ref["relative_path"] == str(export_file.relative_to(REPO_ROOT))
    assert export_ref["size_bytes"] == export_file.stat().st_size
    assert export_ref["sha256"] == _sha256(export_file)

    assert report["evidence_bundle_summary"]["bundle_id"] == "bundle-10c"
    assert report["evidence_bundle_summary"]["bundle_hash"] == "bundle-hash-10c"
    assert report["actor_attributed_audit_report_summary"]["report_id"] == "report-10d"
    assert report["actor_attribution_context_summary"]["actor_id"] == "actor_operator_one"
    assert report["rbac_advisory_context_summary"]["advisory_decision"] == "allow"
    assert report["signature_context_summary"]["verification_result"] == "success"
    assert report["export_integrity_context_summary"]["export_integrity_status"] == "verified"
    assert report["final_acceptance_context_summary"]["phase8o_status"] == "success"

    markdown = _text(output_dir / "export-sidecar.md").lower()
    for token in (
        "export sidecar is not approval",
        "export sidecar validity is not approval",
        "verified export is not approval",
        "signed export is not approval",
        "approval remains phase 7d selected-gate manual boundary",
    ):
        assert token in markdown, f"missing markdown token: {token}"


# E. Missing export warning behavior


def test_phase10e_missing_export_is_warning(phase10e_workspace: Path) -> None:
    manifest = phase10e_workspace / "manifest.json"
    missing = phase10e_workspace / "exports" / "missing.json"
    _write_json(manifest, _sample_manifest(export_path=str(missing.relative_to(REPO_ROOT))))
    output_dir = OUTPUT_ROOT / f"pytest-{phase10e_workspace.name}-missing"
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode == 0, result.stderr

    report = _load_report(output_dir)
    assert report["sidecar_status"] == "built_with_warnings"
    assert report["reviewer_action"] == "manual_review_required"
    assert report["missing_export_count"] == 1
    assert any(issue["issue_type"] == "export_file_missing" for issue in report["issues"])


# F. Optional context behavior


def test_phase10e_missing_optional_context_is_warning(phase10e_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10e_workspace)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["evidence_bundle_reference"] = {
        "reference_type": "evidence_bundle_reference",
        "reference_path": str((phase10e_workspace / "context" / "missing-bundle.json").relative_to(REPO_ROOT)),
        "reference_boundary_statement": "evidence bundle validity is not approval",
    }
    _write_json(manifest, payload)

    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode == 0, result.stderr
    report = _load_report(output_dir)
    assert report["sidecar_status"] == "built_with_warnings"
    assert report["evidence_bundle_summary"]["reference_status"] == "missing"


def test_phase10e_unsafe_optional_path_is_critical(phase10e_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10e_workspace)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["rbac_advisory_context_reference"] = {
        "reference_type": "rbac_advisory_context_reference",
        "reference_path": "docs/PHASE9F_LOCAL_RBAC_POLICY_PROTOTYPE.md",
        "reference_boundary_statement": "RBAC advisory context is not enforcement",
    }
    _write_json(manifest, payload)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0
    report = _load_report(output_dir)
    assert report["sidecar_status"] == "not_built"


# G. Optional JSON parse behavior


def test_phase10e_invalid_evidence_bundle_json_keeps_hash_and_warns(phase10e_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10e_workspace)
    bad_bundle = phase10e_workspace / "context" / "bad-bundle.json"
    bad_bundle.parent.mkdir(parents=True, exist_ok=True)
    bad_bundle.write_text("{not-json}\n", encoding="utf-8")
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["evidence_bundle_reference"] = {
        "reference_type": "evidence_bundle_reference",
        "reference_path": str(bad_bundle.relative_to(REPO_ROOT)),
        "reference_boundary_statement": "evidence bundle validity is not approval",
    }
    _write_json(manifest, payload)

    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode == 0, result.stderr
    report = _load_report(output_dir)
    assert report["sidecar_status"] == "built_with_warnings"
    assert report["evidence_bundle_summary"]["sha256"] == _sha256(bad_bundle)
    assert any(issue["issue_type"] == "optional_context_json_invalid" for issue in report["issues"])


def test_phase10e_missing_actor_report_summary_field_warns(phase10e_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10e_workspace)
    actor_report = phase10e_workspace / "context" / "actor-report-min.json"
    actor_report.parent.mkdir(parents=True, exist_ok=True)
    _write_json(actor_report, {"report_id": "report-only"})
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["actor_attributed_audit_report_reference"] = {
        "reference_type": "actor_attributed_audit_report_reference",
        "reference_path": str(actor_report.relative_to(REPO_ROOT)),
        "reference_boundary_statement": "actor-attributed audit report is not approval",
    }
    _write_json(manifest, payload)

    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode == 0, result.stderr
    report = _load_report(output_dir)
    assert any(issue["issue_type"] == "actor_report_summary_missing" for issue in report["issues"])


# H. Invalid manifest behavior


def test_phase10e_missing_manifest_path_exits_nonzero(phase10e_workspace: Path) -> None:
    output_dir = OUTPUT_ROOT / f"pytest-{phase10e_workspace.name}-invalid"
    result = _run_builder("--manifest", str(phase10e_workspace / "missing.json"), "--output-dir", str(output_dir))
    assert result.returncode != 0


def test_phase10e_invalid_manifest_json_exits_nonzero(phase10e_workspace: Path) -> None:
    manifest = phase10e_workspace / "manifest.json"
    manifest.write_text("{broken}\n", encoding="utf-8")
    output_dir = OUTPUT_ROOT / f"pytest-{phase10e_workspace.name}-invalid"
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0


def test_phase10e_manifest_scalar_exits_nonzero(phase10e_workspace: Path) -> None:
    manifest = phase10e_workspace / "manifest.json"
    manifest.write_text('"scalar"\n', encoding="utf-8")
    output_dir = OUTPUT_ROOT / f"pytest-{phase10e_workspace.name}-invalid"
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0


def test_phase10e_missing_required_manifest_field_exits_nonzero(phase10e_workspace: Path) -> None:
    manifest = phase10e_workspace / "manifest.json"
    _write_json(
        manifest,
        {
            "sidecar_schema_version": "phase10e.export_sidecar.v1",
            "sidecar_id": "sidecar-phase10e-sample",
            "sidecar_purpose": "bad",
            "approval_boundary_statement": "export sidecar is not approval",
        },
    )
    output_dir = OUTPUT_ROOT / f"pytest-{phase10e_workspace.name}-invalid"
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0
    report = _load_report(output_dir)
    assert report["sidecar_status"] == "not_built"


def test_phase10e_invalid_schema_version_exits_nonzero(phase10e_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10e_workspace)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["sidecar_schema_version"] = "wrong"
    _write_json(manifest, payload)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0


def test_phase10e_export_references_must_be_list(phase10e_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10e_workspace)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["export_references"] = {}
    _write_json(manifest, payload)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0


# I. Export reference validation


def test_phase10e_unknown_export_type_exits_nonzero(phase10e_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10e_workspace)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["export_references"][0]["export_type"] = "unknown"
    _write_json(manifest, payload)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0


def test_phase10e_unknown_export_phase_exits_nonzero(phase10e_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10e_workspace)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["export_references"][0]["export_phase"] = "phase11"
    _write_json(manifest, payload)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0


def test_phase10e_export_boundary_missing_required_phrase_exits_nonzero(phase10e_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10e_workspace)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["export_references"][0]["export_boundary_statement"] = "review only"
    _write_json(manifest, payload)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0


# J. Privacy/secret validation


@pytest.mark.parametrize(
    "field_name,value",
    (
        ("sidecar_id", "owner@example.com"),
        ("sidecar_purpose", "API_KEY=secret"),
        ("sidecar_purpose", "BEGIN PRIVATE KEY"),
        ("sidecar_purpose", "AWS_SECRET_ACCESS_KEY=example"),
    ),
)
def test_phase10e_secret_like_manifest_strings_are_rejected(
    phase10e_workspace: Path, field_name: str, value: str
) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10e_workspace)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload[field_name] = value
    _write_json(manifest, payload)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0
    report = _load_report(output_dir)
    assert report["incident_classification"] == "privacy_review_required"


def test_phase10e_secret_like_actor_context_is_rejected(phase10e_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10e_workspace)
    actor = phase10e_workspace / "context" / "actor.json"
    actor.parent.mkdir(parents=True, exist_ok=True)
    _write_json(actor, {"actor_id": "person@example.com"})
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["actor_attribution_context_reference"] = {
        "reference_type": "actor_attribution_context_reference",
        "reference_path": str(actor.relative_to(REPO_ROOT)),
        "reference_boundary_statement": "actor context is not authentication",
    }
    _write_json(manifest, payload)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0
    report = _load_report(output_dir)
    assert report["incident_classification"] == "privacy_review_required"


# K. Approval boundary validation


def test_phase10e_manifest_requires_not_approval_statement(phase10e_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10e_workspace)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["approval_boundary_statement"] = "review only"
    _write_json(manifest, payload)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0
    report = _load_report(output_dir)
    assert report["incident_classification"] == "approval_boundary_review_required"


def test_phase10e_truthy_approval_flag_is_rejected(phase10e_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10e_workspace)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["approved"] = True
    _write_json(manifest, payload)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0


@pytest.mark.parametrize(
    "field_name",
    ("next_gate", "execute", "enforcement_enabled", "execute_primitive", "primitive_execution_intent"),
)
def test_phase10e_execution_intent_is_rejected(phase10e_workspace: Path, field_name: str) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10e_workspace)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload[field_name] = True
    _write_json(manifest, payload)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0


# L. Path safety


def test_phase10e_unsafe_docs_export_path_is_rejected(phase10e_workspace: Path) -> None:
    manifest = phase10e_workspace / "manifest.json"
    _write_json(
        manifest,
        _sample_manifest(export_path="docs/PHASE8E_AUDIT_EXPORT_PACK.md"),
    )
    output_dir = OUTPUT_ROOT / f"pytest-{phase10e_workspace.name}-invalid"
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0
    report = _load_report(output_dir)
    assert report["incident_classification"] == "runtime_scope_violation"


def test_phase10e_output_dir_outside_allowed_root_is_rejected(phase10e_workspace: Path) -> None:
    manifest, _, _ = _make_valid_manifest(phase10e_workspace)
    bad_output = REPO_ROOT / "tmp" / ".." / "phase10e-bad"
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(bad_output))
    assert result.returncode != 0


def test_phase10e_symlink_export_is_rejected(phase10e_workspace: Path) -> None:
    target = phase10e_workspace / "exports" / "real.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('{"x":1}\n', encoding="utf-8")
    link = phase10e_workspace / "exports" / "symlink.json"
    link.symlink_to(target)
    manifest = phase10e_workspace / "manifest.json"
    _write_json(manifest, _sample_manifest(export_path=str(link.relative_to(REPO_ROOT))))
    output_dir = OUTPUT_ROOT / f"pytest-{phase10e_workspace.name}-invalid"
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0
    report = _load_report(output_dir)
    assert report["sidecar_status"] == "not_built"


# M. Deterministic output/hash behavior


def test_phase10e_sidecar_hash_is_deterministic_and_excludes_itself(phase10e_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10e_workspace)
    result_one = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result_one.returncode == 0, result_one.stderr
    report_one = _load_report(output_dir)
    hash_one = report_one["sidecar_hash"]

    second_output = OUTPUT_ROOT / f"pytest-{phase10e_workspace.name}-second"
    result_two = _run_builder("--manifest", str(manifest), "--output-dir", str(second_output))
    assert result_two.returncode == 0, result_two.stderr
    report_two = _load_report(second_output)

    assert report_two["sidecar_hash"] == hash_one
    assert _sidecar_hash_without_self(report_one) == hash_one
    assert _sidecar_hash_without_self(report_two) == hash_one


# N. Report schema behavior


def test_phase10e_report_schema_fields_present(phase10e_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10e_workspace)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode == 0, result.stderr
    report = _load_report(output_dir)

    for key in STATIC_STATUS_TOKENS:
        assert key in report, f"missing status field: {key}"

    for key in (
        "sidecar_schema_version",
        "sidecar_id",
        "sidecar_purpose",
        "sidecar_status",
        "export_reference_count",
        "present_export_count",
        "missing_export_count",
        "invalid_export_count",
        "optional_context_count",
        "sidecar_hash",
        "reviewer_action",
        "reviewer_action_required",
        "incident_classification",
        "severity_counts",
        "approval_boundary_statement",
        "safety_statement",
        "limitations",
        "issues",
        "export_references",
        "evidence_bundle_summary",
        "actor_attributed_audit_report_summary",
        "actor_attribution_context_summary",
        "rbac_advisory_context_summary",
        "signature_context_summary",
        "export_integrity_context_summary",
        "final_acceptance_context_summary",
        "approval_boundary_reference",
    ):
        assert key in report, f"missing report field: {key}"

    assert set(report["severity_counts"]).issuperset({"info", "warning", "critical"})
    for issue in report["issues"]:
        for key in (
            "issue_type",
            "severity",
            "incident_classification",
            "reviewer_action",
            "export_id",
            "reference_type",
            "message",
        ):
            assert key in issue, f"missing issue field: {key}"


# O. Source immutability behavior


def test_phase10e_source_files_are_unchanged(phase10e_workspace: Path) -> None:
    manifest, export_file, output_dir = _make_valid_manifest(phase10e_workspace)
    bundle = phase10e_workspace / "context" / "bundle.json"
    bundle.parent.mkdir(parents=True, exist_ok=True)
    _write_json(bundle, {"bundle_id": "bundle-only"})
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["evidence_bundle_reference"] = {
        "reference_type": "evidence_bundle_reference",
        "reference_path": str(bundle.relative_to(REPO_ROOT)),
        "reference_boundary_statement": "evidence bundle validity is not approval",
    }
    _write_json(manifest, payload)

    manifest_before = manifest.read_bytes()
    export_before = export_file.read_bytes()
    bundle_before = bundle.read_bytes()

    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode == 0, result.stderr

    assert manifest.read_bytes() == manifest_before
    assert export_file.read_bytes() == export_before
    assert bundle.read_bytes() == bundle_before


# P. Documentation regression


def test_phase10e_required_sections_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "### Purpose",
            "### Scope",
            "### Runtime command",
            "### Sidecar input manifest model",
            "### Export source reference model",
            "### Evidence bundle reference model",
            "### Actor-attributed audit report reference model",
            "### Actor/RBAC context reference model",
            "### Signature/export integrity context model",
            "### Final acceptance context model",
            "### Approval boundary reference model",
            "### Source immutability model",
            "### Export manifest preservation model",
            "### Export integrity preservation model",
            "### Signature preservation model",
            "### Sidecar hash model",
            "### Sidecar output model",
            "### Path safety model",
            "### Privacy and secret scan model",
            "### Non-authentication boundary",
            "### Non-RBAC-enforcement boundary",
            "### Non-approval boundary",
            "### Compatibility with Phase 10D",
            "### Compatibility with Phase 10C",
            "### Compatibility with Phase 10B",
            "### Compatibility with Phase 10A",
            "### Compatibility with Phase 9G/9F/9D/9C",
            "### Compatibility with Phase 8O/8M/8L/8H/8G/8E",
            "### Compatibility with Phase 7D",
            "### Failure taxonomy",
            "### Reviewer action mapping",
            "### Known limitations",
        ),
        label="section",
    )


def test_phase10e_task_uses_canonical_references() -> None:
    text = _text(TASK_FILE)
    assert "docs/PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE.md" in text
    assert "tests/test_phase8b_local_append_only_audit_store.py" in text
    assert "PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE_PROTOTYPE.md" in text


def test_phase10e_docs_and_state_references_present() -> None:
    assert "Phase 10E" in _text(ROADMAP)
    assert "Phase 10E" in _text(PROJECT_STATE)
    assert "docs/PHASE10E_EXPORT_SIDECAR_DESIGN_PROTOTYPE.md" in _text(PROJECT_STATE)
    assert "Phase 5" in _text(ROADMAP)
    assert "read-only" in _text(ROADMAP)
    assert "manual-approved" in _text(ROADMAP)
    state = _text(PROJECT_STATE)
    for token in ("Current architecture", "no database", "no FastAPI", "no UI", "no external APIs", "no autopublish"):
        assert token in state, f"missing PROJECT_STATE token: {token}"


def test_phase10e_cross_phase_pointer_updates_present() -> None:
    for path in (
        PHASE10D_DOC,
        PHASE10C_DOC,
        PHASE10B_DOC,
        PHASE10A_DOC,
        PHASE9D_DOC,
        PHASE9F_DOC,
        PHASE8E_DOC,
        PHASE8G_DOC,
        PHASE8H_DOC,
        PHASE8L_DOC,
        PHASE8M_DOC,
        PHASE8O_DOC,
    ):
        text = _text(path)
        assert "Phase 10E" in text, f"missing Phase 10E pointer in {path}"
        assert "PHASE10E_EXPORT_SIDECAR_DESIGN_PROTOTYPE.md" in text


# Q. Protected runtime files unchanged


def test_phase10e_protected_runtime_hashes_unchanged() -> None:
    for path, expected in PROTECTED_HASHES.items():
        assert path.is_file(), f"missing protected file: {path}"
        assert _sha256(path) == expected, f"protected runtime changed unexpectedly: {path}"


# R. Static safety for new Phase 10E files only


def test_phase10e_new_files_do_not_reference_forbidden_artifacts() -> None:
    for path in (TASK_FILE, DOC, SCRIPT, RUNNER):
        text = _flat(path)
        for forbidden in FORBIDDEN_EXTENSIONS:
            assert forbidden not in text, f"forbidden extension reference in {path}: {forbidden}"


# S. Repo-wide artifact safety


def test_phase10e_gitignore_entries_present() -> None:
    text = _text(GITIGNORE)
    assert "tmp/phase10e-export-sidecar/" in text
    assert "tmp/phase10e-test-input/" in text

