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

TASK_FILE = REPO_ROOT / "codex/tasks/077-phase10d-derived-actor-attributed-audit-report-prototype.md"
DOC = REPO_ROOT / "docs/PHASE10D_DERIVED_ACTOR_ATTRIBUTED_AUDIT_REPORT_PROTOTYPE.md"
SCRIPT = REPO_ROOT / "scripts/dev/build_phase10d_actor_attributed_audit_report.py"
RUNNER = REPO_ROOT / "scripts/dev/run_phase10d_actor_attributed_audit_report.sh"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE10C_DOC = REPO_ROOT / "docs/PHASE10C_LOCAL_EVIDENCE_BUNDLE_ACTOR_RBAC_CONTEXT.md"
PHASE10B_DOC = REPO_ROOT / "docs/PHASE10B_ACTOR_ATTRIBUTION_AUDIT_STORE_INTEGRATION_PLAN.md"
PHASE10A_DOC = REPO_ROOT / "docs/PHASE10A_GOVERNED_RUNTIME_INTEGRATION_READINESS_DESIGN.md"
PHASE9D_DOC = REPO_ROOT / "docs/PHASE9D_ACTOR_ATTRIBUTION_IN_AUDIT_REPORTS.md"
PHASE9F_DOC = REPO_ROOT / "docs/PHASE9F_LOCAL_RBAC_POLICY_PROTOTYPE.md"
PHASE8C_DOC = REPO_ROOT / "docs/PHASE8C_AUDIT_STORE_VERIFIER_REPORTING.md"
PHASE8D_DOC = REPO_ROOT / "docs/PHASE8D_AUDIT_STORE_QUERY_CLI.md"
PHASE8E_DOC = REPO_ROOT / "docs/PHASE8E_AUDIT_EXPORT_PACK.md"
PHASE8O_DOC = REPO_ROOT / "docs/PHASE8O_FINAL_ACCEPTANCE_PACK.md"
GITIGNORE = REPO_ROOT / ".gitignore"

OUTPUT_ROOT = REPO_ROOT / "tmp/phase10d-actor-attributed-audit-report"
TEST_INPUT_ROOT = REPO_ROOT / "tmp/phase10d-test-input"

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
    REPO_ROOT / "scripts/dev/run_phase7d_single_gate_wrapper.sh": "372aef7a133950a24a1de859a1ba0c01486fd2c84bf46ded783105acc4e47b7d",
    REPO_ROOT / "scripts/dev/execute_single_gate_approval.py": "1b1d00817b1ae89c2840f18c9fe3b73f091abec9c900bf0bff83ad6820e9cebb",
}

FORBIDDEN_EXTENSIONS = (".pem", ".key", ".crt", ".p12", ".pfx", ".sql", ".sqlite", ".db", ".rego")
STATIC_STATUS_TOKENS = (
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
    return json.loads((output_dir / "actor-attributed-audit-report.json").read_text(encoding="utf-8"))


def _sample_manifest(
    *,
    evidence_path: str,
    extra: dict | None = None,
    evidence_extra: dict | None = None,
) -> dict:
    manifest = {
        "report_schema_version": "phase10d.actor_attributed_audit_report.v1",
        "report_id": "report-phase10d-sample",
        "report_purpose": "Derived actor-attributed audit report for local review.",
        "approval_boundary_statement": (
            "derived actor-attributed audit report is not approval; "
            "approval remains Phase 7D selected-gate manual boundary"
        ),
        "audit_evidence_references": [
            {
                "evidence_id": "ev-audit-query",
                "evidence_type": "audit_query_result",
                "evidence_phase": "phase8d",
                "evidence_path": evidence_path,
                "evidence_purpose": "Local audit query evidence.",
                "evidence_boundary_statement": (
                    "evidence reference is not approval; "
                    "audit actor attribution is not approval; "
                    "approval remains Phase 7D selected-gate manual boundary"
                ),
            }
        ],
    }
    if evidence_extra:
        manifest["audit_evidence_references"][0].update(evidence_extra)
    if extra:
        manifest.update(extra)
    return manifest


@pytest.fixture()
def phase10d_workspace() -> Path:
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


def _make_valid_manifest(phase10d_workspace: Path) -> tuple[Path, Path, Path]:
    evidence = phase10d_workspace / "evidence" / "audit-query-result.json"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text('{"query":"phase8d"}\n', encoding="utf-8")
    manifest = phase10d_workspace / "manifest.json"
    _write_json(manifest, _sample_manifest(evidence_path=str(evidence.relative_to(REPO_ROOT))))
    output_dir = OUTPUT_ROOT / f"pytest-{phase10d_workspace.name}"
    return manifest, evidence, output_dir


def _report_hash_without_self(report: dict) -> str:
    clone = json.loads(json.dumps(report))
    clone.pop("report_hash", None)
    return hashlib.sha256(_canonical_json(clone).encode("utf-8")).hexdigest()


# A. File existence and status


def test_phase10d_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, SCRIPT, RUNNER, THIS_TEST):
        assert path.is_file(), f"missing Phase 10D file: {path}"


def test_phase10d_status_tokens() -> None:
    assert "phase10d_status: success" in _text(TASK_FILE)
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "phase10d_status: success",
            "phase10c_status: success",
            "phase10b_status: success",
            "phase10a_status: success",
            "phase7d_runtime_readiness: implemented_manual_gate",
            "durable_audit_store_status: phase8_final_acceptance_pack",
            "audit_actor_attribution_integration_status: derived_report_prototype",
            "governed_runtime_integration_status: local_evidence_bundle_and_actor_report_prototypes",
            "integration_runtime_status: local_derived_report_prototype",
            "local_evidence_bundle_status: prototype_local_only",
            "actor_attributed_audit_report_status: prototype_local_only",
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


def test_phase10d_runner_is_executable_mode_755() -> None:
    mode = RUNNER.stat().st_mode & 0o777
    assert mode == 0o755, f"expected 0755, got {oct(mode)}"


# B. Scope safety


def test_phase10d_scope_safety_tokens() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "local-only derived actor-attributed audit report prototype",
            "no source mutation",
            "no audit record rewrite",
            "no hash-chain rewrite",
            "no authentication runtime",
            "no rbac enforcement",
            "no backend/api/database",
            "no key management runtime",
            "no wrapper behavior change",
            "no primitive execution",
            "no vault read/write",
            "no phase 8 runtime behavior change",
            "no phase 9 runtime behavior change",
            "no phase 10c runtime behavior change",
        ),
        label="scope safety token",
    )


# C. Runtime static safety


def test_phase10d_script_no_forbidden_imports() -> None:
    text = _text(SCRIPT)
    low = text.lower()
    for forbidden in (
        "import subprocess",
        "from subprocess",
        "import sqlite3",
        "import boto3",
        "import requests",
        "import httpx",
        "import urllib",
    ):
        assert forbidden not in text, f"runtime must not contain: {forbidden}"
    for forbidden in ("fastapi",):
        assert forbidden not in low, f"runtime must not reference {forbidden}"


def test_phase10d_script_no_forbidden_runtime_calls() -> None:
    text = _text(SCRIPT)
    for forbidden in (
        "run_phase7d_single_gate_wrapper",
        "execute_single_gate_approval",
        "promote_product_candidates.py",
        "create_decision.py",
        "finalize_decision.py",
        "ingest_phase8b_audit_record",
        "verify_phase8c_audit_store",
        "query_phase8d_audit_store",
        "build_phase8e_audit_export_pack",
        "verify_phase8g_export_integrity",
        "build_phase8l_detached_signature",
        "verify_phase8m_detached_signature",
        "manage_phase9c_local_operator_registry",
        "build_phase9d_actor_attribution_report",
        "evaluate_phase9f_local_rbac_policy",
        "build_phase10c_local_evidence_bundle",
        "os.system(",
        "subprocess.",
    ):
        assert forbidden not in text, f"runtime must not contain: {forbidden}"


def test_phase10d_runner_static_safety() -> None:
    text = _text(RUNNER)
    for forbidden in (
        "--execute",
        "approve_all",
        "run_phase7d_single_gate_wrapper",
        "execute_single_gate_approval",
        "promote_product_candidates.py",
        "create_decision.py",
        "finalize_decision.py",
        "ingest_phase8b_audit_record.py",
        "verify_phase8c_audit_store.py",
        "query_phase8d_audit_store.py",
        "build_phase10c_local_evidence_bundle.py",
        "vault/",
        "curl ",
        "wget ",
    ):
        assert forbidden not in text, f"runner must not contain: {forbidden}"


def test_phase10d_runner_bash_syntax_ok() -> None:
    result = subprocess.run(["bash", "-n", str(RUNNER)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_phase10d_script_py_compile_ok() -> None:
    result = subprocess.run([sys.executable, "-m", "py_compile", str(SCRIPT)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


# D. Valid report behavior


def test_phase10d_valid_report_builds(phase10d_workspace: Path) -> None:
    manifest, evidence, output_dir = _make_valid_manifest(phase10d_workspace)

    actor = phase10d_workspace / "context" / "actor.json"
    rbac = phase10d_workspace / "context" / "rbac.json"
    bundle = phase10d_workspace / "context" / "bundle.json"
    signature = phase10d_workspace / "context" / "signature.json"
    final_acceptance = phase10d_workspace / "context" / "final-acceptance.json"
    boundary = phase10d_workspace / "context" / "boundary.json"
    actor.parent.mkdir(parents=True, exist_ok=True)

    _write_json(
        actor,
        {
            "actor_id": "actor_operator_one",
            "actor_type": "human_operator",
            "actor_identity_assurance": "operator_declared",
            "actor_identity_source": "environment_operator_label",
            "actor_role_labels": ["operator", "reviewer"],
            "actor_attribution_status": "local_report_prototype",
            "approval_boundary_statement": "audit actor attribution is not approval",
        },
    )
    _write_json(
        rbac,
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
        bundle,
        {
            "bundle_id": "bundle-10c",
            "bundle_status": "built",
            "bundle_hash": "abc123",
            "evidence_reference_count": 1,
            "present_evidence_count": 1,
            "missing_evidence_count": 0,
            "approval_boundary_statement": "evidence bundle validity is not approval",
        },
    )
    _write_json(
        signature,
        {
            "reference_type": "signature_context_reference",
            "note": "signature verification remains not approval",
            "approval_boundary_statement": "signature verification remains not approval",
        },
    )
    _write_json(
        final_acceptance,
        {
            "reference_type": "final_acceptance_context_reference",
            "note": "final acceptance remains not approval",
            "approval_boundary_statement": "final acceptance remains not approval",
        },
    )
    _write_json(
        boundary,
        {
            "reference_type": "approval_boundary_reference",
            "note": "approval remains Phase 7D selected-gate manual boundary",
            "approval_boundary_statement": "approval remains Phase 7D selected-gate manual boundary",
        },
    )

    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["actor_attribution_context"] = {
        "reference_type": "actor_attribution_context",
        "reference_path": str(actor.relative_to(REPO_ROOT)),
        "reference_boundary_statement": "audit actor attribution is not approval",
    }
    payload["rbac_advisory_context"] = {
        "reference_type": "rbac_advisory_context",
        "reference_path": str(rbac.relative_to(REPO_ROOT)),
        "reference_boundary_statement": "RBAC advisory context is not enforcement",
    }
    payload["evidence_bundle_context"] = {
        "reference_type": "evidence_bundle_context",
        "reference_path": str(bundle.relative_to(REPO_ROOT)),
        "reference_boundary_statement": "evidence bundle validity is not approval",
    }
    payload["signature_context_reference"] = {
        "reference_type": "signature_context_reference",
        "reference_path": str(signature.relative_to(REPO_ROOT)),
        "reference_boundary_statement": "signature verification remains not approval",
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
    assert report["report_status"] == "built"
    assert report["reviewer_action"] == "no_action_required"
    assert report["reviewer_action_required"] is False
    assert report["incident_classification"] == "none"
    assert report["audit_evidence_reference_count"] == 1
    assert report["present_evidence_count"] == 1
    assert report["missing_evidence_count"] == 0
    assert report["invalid_evidence_count"] == 0
    assert report["optional_context_count"] == 6
    assert report["report_hash"]

    ref = report["audit_evidence_references"][0]
    assert ref["evidence_status"] == "present"
    assert ref["relative_path"] == str(evidence.relative_to(REPO_ROOT))
    assert ref["size_bytes"] == evidence.stat().st_size
    assert ref["sha256"] == _sha256(evidence)

    assert report["actor_context_summary"]["actor_id"] == "actor_operator_one"
    assert report["rbac_advisory_context_summary"]["advisory_decision"] == "allow"
    assert report["evidence_bundle_context_summary"]["bundle_id"] == "bundle-10c"
    assert report["evidence_bundle_context_summary"]["bundle_hash"] == "abc123"

    markdown = _text(output_dir / "actor-attributed-audit-report.md").lower()
    for token in (
        "derived actor-attributed audit report is not approval",
        "audit actor attribution is not authentication",
        "audit actor attribution is not approval",
        "rbac advisory context is not enforcement",
        "rbac allow decision is not approval",
        "approval remains phase 7d selected-gate manual boundary",
    ):
        assert token in markdown, f"missing markdown token: {token}"


# E. Missing evidence warning behavior


def test_phase10d_missing_evidence_is_warning(phase10d_workspace: Path) -> None:
    manifest = phase10d_workspace / "manifest.json"
    missing = phase10d_workspace / "evidence" / "missing.json"
    _write_json(manifest, _sample_manifest(evidence_path=str(missing.relative_to(REPO_ROOT))))
    output_dir = OUTPUT_ROOT / f"pytest-{phase10d_workspace.name}-missing"
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode == 0, result.stderr

    report = _load_report(output_dir)
    assert report["report_status"] == "built_with_warnings"
    assert report["reviewer_action"] == "manual_review_required"
    assert report["missing_evidence_count"] == 1
    assert any(issue["issue_type"] == "evidence_file_missing" for issue in report["issues"])


# F. Optional context behavior


def test_phase10d_missing_optional_context_is_warning(phase10d_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10d_workspace)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["actor_attribution_context"] = {
        "reference_type": "actor_attribution_context",
        "reference_path": str((phase10d_workspace / "context" / "missing-actor.json").relative_to(REPO_ROOT)),
        "reference_boundary_statement": "audit actor attribution is not approval",
    }
    _write_json(manifest, payload)

    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode == 0, result.stderr
    report = _load_report(output_dir)
    assert report["report_status"] == "built_with_warnings"
    assert report["actor_context_summary"]["reference_status"] == "missing"


def test_phase10d_unsafe_optional_path_is_critical(phase10d_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10d_workspace)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["rbac_advisory_context"] = {
        "reference_type": "rbac_advisory_context",
        "reference_path": "docs/PHASE9F_LOCAL_RBAC_POLICY_PROTOTYPE.md",
        "reference_boundary_statement": "RBAC advisory context is not enforcement",
    }
    _write_json(manifest, payload)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0
    report = _load_report(output_dir)
    assert report["report_status"] == "not_built"


# G. Optional JSON parse behavior


def test_phase10d_invalid_actor_context_json_keeps_hash_and_warns(phase10d_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10d_workspace)
    actor = phase10d_workspace / "context" / "bad-actor.json"
    actor.parent.mkdir(parents=True, exist_ok=True)
    actor.write_text("{not-json}\n", encoding="utf-8")
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["actor_attribution_context"] = {
        "reference_type": "actor_attribution_context",
        "reference_path": str(actor.relative_to(REPO_ROOT)),
        "reference_boundary_statement": "audit actor attribution is not approval",
    }
    _write_json(manifest, payload)

    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode == 0, result.stderr
    report = _load_report(output_dir)
    assert report["report_status"] == "built_with_warnings"
    assert report["actor_context_summary"]["sha256"] == _sha256(actor)
    assert any(issue["issue_type"] == "optional_context_json_invalid" for issue in report["issues"])


def test_phase10d_missing_actor_summary_field_warns(phase10d_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10d_workspace)
    actor = phase10d_workspace / "context" / "actor-min.json"
    actor.parent.mkdir(parents=True, exist_ok=True)
    _write_json(actor, {"actor_id": "actor_only"})
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["actor_attribution_context"] = {
        "reference_type": "actor_attribution_context",
        "reference_path": str(actor.relative_to(REPO_ROOT)),
        "reference_boundary_statement": "audit actor attribution is not approval",
    }
    _write_json(manifest, payload)

    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode == 0, result.stderr
    report = _load_report(output_dir)
    assert any(issue["issue_type"] == "actor_context_summary_missing" for issue in report["issues"])


# H. Invalid manifest behavior


def test_phase10d_missing_manifest_path_exits_nonzero(phase10d_workspace: Path) -> None:
    output_dir = OUTPUT_ROOT / f"pytest-{phase10d_workspace.name}-invalid"
    result = _run_builder("--manifest", str(phase10d_workspace / "missing.json"), "--output-dir", str(output_dir))
    assert result.returncode != 0


def test_phase10d_invalid_manifest_json_exits_nonzero(phase10d_workspace: Path) -> None:
    manifest = phase10d_workspace / "manifest.json"
    manifest.write_text("{broken}\n", encoding="utf-8")
    output_dir = OUTPUT_ROOT / f"pytest-{phase10d_workspace.name}-invalid"
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0


def test_phase10d_missing_required_manifest_field_exits_nonzero(phase10d_workspace: Path) -> None:
    manifest = phase10d_workspace / "manifest.json"
    _write_json(
        manifest,
        {
            "report_schema_version": "phase10d.actor_attributed_audit_report.v1",
            "report_id": "report-phase10d-sample",
            "report_purpose": "bad",
            "approval_boundary_statement": "derived actor-attributed audit report is not approval",
        },
    )
    output_dir = OUTPUT_ROOT / f"pytest-{phase10d_workspace.name}-invalid"
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0
    report = _load_report(output_dir)
    assert report["report_status"] == "not_built"


def test_phase10d_invalid_schema_version_exits_nonzero(phase10d_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10d_workspace)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["report_schema_version"] = "wrong"
    _write_json(manifest, payload)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0


# I. Audit evidence reference validation


def test_phase10d_unknown_evidence_type_exits_nonzero(phase10d_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10d_workspace)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["audit_evidence_references"][0]["evidence_type"] = "unknown"
    _write_json(manifest, payload)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0


def test_phase10d_unknown_evidence_phase_exits_nonzero(phase10d_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10d_workspace)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["audit_evidence_references"][0]["evidence_phase"] = "phase11"
    _write_json(manifest, payload)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0


def test_phase10d_evidence_boundary_missing_required_phrase_exits_nonzero(phase10d_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10d_workspace)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["audit_evidence_references"][0]["evidence_boundary_statement"] = "review only"
    _write_json(manifest, payload)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0


# J. Privacy/secret validation


@pytest.mark.parametrize(
    "field_name,value",
    (
        ("report_id", "report-owner@example.com"),
        ("report_purpose", "API_KEY=secret"),
        ("report_purpose", "BEGIN PRIVATE KEY"),
    ),
)
def test_phase10d_secret_like_manifest_strings_are_rejected(
    phase10d_workspace: Path, field_name: str, value: str
) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10d_workspace)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload[field_name] = value
    _write_json(manifest, payload)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0
    report = _load_report(output_dir)
    assert report["incident_classification"] == "privacy_review_required"


def test_phase10d_secret_like_actor_context_is_rejected(phase10d_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10d_workspace)
    actor = phase10d_workspace / "context" / "actor.json"
    actor.parent.mkdir(parents=True, exist_ok=True)
    _write_json(actor, {"actor_id": "person@example.com"})
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["actor_attribution_context"] = {
        "reference_type": "actor_attribution_context",
        "reference_path": str(actor.relative_to(REPO_ROOT)),
        "reference_boundary_statement": "audit actor attribution is not approval",
    }
    _write_json(manifest, payload)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0
    report = _load_report(output_dir)
    assert report["incident_classification"] == "privacy_review_required"


# K. Approval boundary validation


def test_phase10d_manifest_requires_not_approval_statement(phase10d_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10d_workspace)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["approval_boundary_statement"] = "review only"
    _write_json(manifest, payload)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0
    report = _load_report(output_dir)
    assert report["incident_classification"] == "approval_boundary_review_required"


def test_phase10d_truthy_approval_flag_is_rejected(phase10d_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10d_workspace)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["approved"] = True
    _write_json(manifest, payload)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0


@pytest.mark.parametrize("field_name", ("next_gate", "execute", "enforcement_enabled"))
def test_phase10d_execution_intent_is_rejected(phase10d_workspace: Path, field_name: str) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10d_workspace)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload[field_name] = True
    _write_json(manifest, payload)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0


# L. Path safety


def test_phase10d_unsafe_docs_evidence_path_is_rejected(phase10d_workspace: Path) -> None:
    manifest = phase10d_workspace / "manifest.json"
    _write_json(
        manifest,
        _sample_manifest(evidence_path="docs/PHASE8D_AUDIT_STORE_QUERY_CLI.md"),
    )
    output_dir = OUTPUT_ROOT / f"pytest-{phase10d_workspace.name}-invalid"
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0
    report = _load_report(output_dir)
    assert report["incident_classification"] == "runtime_scope_violation"


def test_phase10d_output_dir_outside_allowed_root_is_rejected(phase10d_workspace: Path) -> None:
    manifest, _, _ = _make_valid_manifest(phase10d_workspace)
    bad_output = REPO_ROOT / "tmp" / ".." / "phase10d-bad"
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(bad_output))
    assert result.returncode != 0


def test_phase10d_symlink_evidence_is_rejected(phase10d_workspace: Path) -> None:
    target = phase10d_workspace / "evidence" / "real.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('{"x":1}\n', encoding="utf-8")
    link = phase10d_workspace / "evidence" / "symlink.json"
    link.symlink_to(target)
    manifest = phase10d_workspace / "manifest.json"
    _write_json(manifest, _sample_manifest(evidence_path=str(link.relative_to(REPO_ROOT))))
    output_dir = OUTPUT_ROOT / f"pytest-{phase10d_workspace.name}-invalid"
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0
    report = _load_report(output_dir)
    assert report["report_status"] == "not_built"


# M. Deterministic output/hash behavior


def test_phase10d_report_hash_is_deterministic_and_excludes_itself(phase10d_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10d_workspace)
    result_one = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result_one.returncode == 0, result_one.stderr
    report_one = _load_report(output_dir)
    hash_one = report_one["report_hash"]

    second_output = OUTPUT_ROOT / f"pytest-{phase10d_workspace.name}-second"
    result_two = _run_builder("--manifest", str(manifest), "--output-dir", str(second_output))
    assert result_two.returncode == 0, result_two.stderr
    report_two = _load_report(second_output)

    assert report_two["report_hash"] == hash_one
    assert _report_hash_without_self(report_one) == hash_one
    assert _report_hash_without_self(report_two) == hash_one


# N. Report schema behavior


def test_phase10d_report_schema_fields_present(phase10d_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10d_workspace)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode == 0, result.stderr
    report = _load_report(output_dir)

    for key in STATIC_STATUS_TOKENS:
        assert key in report, f"missing status field: {key}"

    for key in (
        "report_schema_version",
        "report_id",
        "report_purpose",
        "report_status",
        "audit_evidence_reference_count",
        "present_evidence_count",
        "missing_evidence_count",
        "invalid_evidence_count",
        "optional_context_count",
        "report_hash",
        "reviewer_action",
        "reviewer_action_required",
        "incident_classification",
        "severity_counts",
        "approval_boundary_statement",
        "safety_statement",
        "limitations",
        "issues",
        "audit_evidence_references",
        "actor_context_summary",
        "rbac_advisory_context_summary",
        "evidence_bundle_context_summary",
        "signature_context_reference",
        "final_acceptance_context_reference",
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
            "evidence_id",
            "reference_type",
            "message",
        ):
            assert key in issue, f"missing issue field: {key}"


# O. Source immutability behavior


def test_phase10d_source_files_are_unchanged(phase10d_workspace: Path) -> None:
    manifest, evidence, output_dir = _make_valid_manifest(phase10d_workspace)
    actor = phase10d_workspace / "context" / "actor.json"
    actor.parent.mkdir(parents=True, exist_ok=True)
    _write_json(actor, {"actor_id": "actor_operator_one"})
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["actor_attribution_context"] = {
        "reference_type": "actor_attribution_context",
        "reference_path": str(actor.relative_to(REPO_ROOT)),
        "reference_boundary_statement": "audit actor attribution is not approval",
    }
    _write_json(manifest, payload)

    manifest_before = manifest.read_bytes()
    evidence_before = evidence.read_bytes()
    actor_before = actor.read_bytes()

    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode == 0, result.stderr

    assert manifest.read_bytes() == manifest_before
    assert evidence.read_bytes() == evidence_before
    assert actor.read_bytes() == actor_before


# P. Documentation regression


def test_phase10d_required_sections_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "### Purpose",
            "### Scope",
            "### Runtime command",
            "### Manifest model",
            "### Audit evidence reference model",
            "### Actor context summary",
            "### RBAC advisory context summary",
            "### Evidence bundle context summary",
            "### Source immutability",
            "### Path safety",
            "### Non-authentication boundary",
            "### Non-RBAC-enforcement boundary",
            "### Non-approval boundary",
            "### Compatibility with Phase 10C",
            "### Compatibility with Phase 10B",
            "### Compatibility with Phase 10A",
            "### Compatibility with Phase 9G/9F/9D/9C",
            "### Compatibility with Phase 8O/8M/8G/8E/8D/8C/8B",
            "### Compatibility with Phase 7D",
            "### Failure taxonomy",
            "### Reviewer action mapping",
            "### Known limitations",
        ),
        label="section",
    )


def test_phase10d_task_uses_canonical_references() -> None:
    text = _text(TASK_FILE)
    assert "docs/PHASE8D_AUDIT_STORE_QUERY_CLI.md" in text
    assert "tests/test_phase8d_audit_store_query_cli.py" in text
    assert "tests/test_phase8b_local_append_only_audit_store.py" in text


def test_phase10d_docs_and_state_references_present() -> None:
    assert "Phase 10D" in _text(ROADMAP)
    assert "Phase 10D" in _text(PROJECT_STATE)
    assert "docs/PHASE10D_DERIVED_ACTOR_ATTRIBUTED_AUDIT_REPORT_PROTOTYPE.md" in _text(PROJECT_STATE)
    assert "Phase 5" in _text(ROADMAP)
    assert "read-only" in _text(ROADMAP)
    assert "manual-approved" in _text(ROADMAP)
    state = _text(PROJECT_STATE)
    for token in ("Current architecture", "no database", "no FastAPI", "no UI", "no external APIs", "no autopublish"):
        assert token in state, f"missing PROJECT_STATE token: {token}"


def test_phase10d_cross_phase_pointer_updates_present() -> None:
    for path in (
        PHASE10C_DOC,
        PHASE10B_DOC,
        PHASE10A_DOC,
        PHASE9D_DOC,
        PHASE9F_DOC,
        PHASE8C_DOC,
        PHASE8D_DOC,
        PHASE8E_DOC,
        PHASE8O_DOC,
    ):
        text = _text(path)
        assert "Phase 10D" in text, f"missing Phase 10D pointer in {path}"
        assert "PHASE10D_DERIVED_ACTOR_ATTRIBUTED_AUDIT_REPORT_PROTOTYPE.md" in text


# Q. Protected runtime files unchanged


def test_phase10d_protected_runtime_hashes_unchanged() -> None:
    for path, expected in PROTECTED_HASHES.items():
        assert path.is_file(), f"missing protected file: {path}"
        assert _sha256(path) == expected, f"protected runtime changed unexpectedly: {path}"


# R. Static safety for new Phase 10D files only


def test_phase10d_new_files_do_not_reference_forbidden_artifacts() -> None:
    for path in (TASK_FILE, DOC, SCRIPT, RUNNER):
        text = _flat(path)
        for forbidden in FORBIDDEN_EXTENSIONS:
            assert forbidden not in text, f"forbidden extension reference in {path}: {forbidden}"


# S. Repo-wide artifact safety


def test_phase10d_gitignore_entries_present() -> None:
    text = _text(GITIGNORE)
    assert "tmp/phase10d-actor-attributed-audit-report/" in text
    assert "tmp/phase10d-test-input/" in text
