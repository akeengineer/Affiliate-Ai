from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/076-phase10c-local-evidence-bundle-actor-rbac-context.md"
DOC = REPO_ROOT / "docs/PHASE10C_LOCAL_EVIDENCE_BUNDLE_ACTOR_RBAC_CONTEXT.md"
SCRIPT = REPO_ROOT / "scripts/dev/build_phase10c_local_evidence_bundle.py"
RUNNER = REPO_ROOT / "scripts/dev/run_phase10c_local_evidence_bundle.sh"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE10B_DOC = REPO_ROOT / "docs/PHASE10B_ACTOR_ATTRIBUTION_AUDIT_STORE_INTEGRATION_PLAN.md"
PHASE10A_DOC = REPO_ROOT / "docs/PHASE10A_GOVERNED_RUNTIME_INTEGRATION_READINESS_DESIGN.md"
PHASE9G_DOC = REPO_ROOT / "docs/PHASE9G_PHASE9_ACCEPTANCE_PACK.md"
PHASE9F_DOC = REPO_ROOT / "docs/PHASE9F_LOCAL_RBAC_POLICY_PROTOTYPE.md"
PHASE9D_DOC = REPO_ROOT / "docs/PHASE9D_ACTOR_ATTRIBUTION_IN_AUDIT_REPORTS.md"
PHASE8O_DOC = REPO_ROOT / "docs/PHASE8O_FINAL_ACCEPTANCE_PACK.md"
PHASE8B_DOC = REPO_ROOT / "docs/PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE.md"
GITIGNORE = REPO_ROOT / ".gitignore"

OUTPUT_ROOT = REPO_ROOT / "tmp/phase10c-local-evidence-bundle"
TEST_INPUT_ROOT = REPO_ROOT / "tmp/phase10c-test-input"

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
    REPO_ROOT / "scripts/dev/run_phase7d_single_gate_wrapper.sh": "372aef7a133950a24a1de859a1ba0c01486fd2c84bf46ded783105acc4e47b7d",
    REPO_ROOT / "scripts/dev/execute_single_gate_approval.py": "1b1d00817b1ae89c2840f18c9fe3b73f091abec9c900bf0bff83ad6820e9cebb",
    REPO_ROOT / "scripts/dev/promote_product_candidates.py": "496055979f5492389237662d756c4a51a6428da60c804e4ccba72efff0f1ff6e",
    REPO_ROOT / "scripts/dev/create_decision.py": "ac27e4300d617f60e45799980fead1f7e3a09f5f1f083ef5d42c1d327ded4613",
    REPO_ROOT / "scripts/dev/finalize_decision.py": "1c829e797b49ca8a3cff875a1609a06f093ca104873fa20597784a8adac3d177",
}

EXCLUDED_PARTS = {".git", ".venv", "tmp", "vault", "node_modules", "vendor", "__pycache__"}
FORBIDDEN_EXTENSIONS = (".pem", ".key", ".crt", ".p12", ".pfx", ".sql", ".sqlite", ".db", ".rego")

STATIC_STATUS_TOKENS = (
    "phase10c_status",
    "phase10b_status",
    "phase10a_status",
    "phase7d_runtime_readiness",
    "durable_audit_store_status",
    "audit_actor_attribution_integration_status",
    "governed_runtime_integration_status",
    "integration_runtime_status",
    "local_evidence_bundle_status",
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


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _run_builder(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def _load_bundle(output_dir: Path) -> dict:
    return json.loads((output_dir / "local-evidence-bundle.json").read_text(encoding="utf-8"))


def _sample_manifest(
    manifest_dir: Path,
    *,
    evidence_path: str,
    extra: dict | None = None,
    evidence_extra: dict | None = None,
) -> dict:
    manifest = {
        "bundle_schema_version": "phase10c.local_evidence_bundle.v1",
        "bundle_id": "bundle-phase10c-sample",
        "bundle_purpose": "Derived local evidence bundle for review.",
        "approval_boundary_statement": (
            "local evidence bundle is not approval; "
            "approval remains Phase 7D selected-gate manual boundary"
        ),
        "evidence_references": [
            {
                "evidence_id": "ev-audit-export",
                "evidence_type": "audit_export_pack",
                "evidence_phase": "phase8e",
                "evidence_path": evidence_path,
                "evidence_purpose": "Local reviewable export evidence.",
                "evidence_boundary_statement": (
                    "evidence reference is not approval; "
                    "approval remains Phase 7D selected-gate manual boundary"
                ),
            }
        ],
    }
    if evidence_extra:
        manifest["evidence_references"][0].update(evidence_extra)
    if extra:
        manifest.update(extra)
    return manifest


@pytest.fixture()
def phase10c_workspace() -> Path:
    unique = uuid.uuid4().hex[:12]
    root = TEST_INPUT_ROOT / f"pytest-{unique}"
    output_root = OUTPUT_ROOT / f"pytest-{root.name}"
    output_root_second = OUTPUT_ROOT / f"pytest-{root.name}-second"
    root.mkdir(parents=True, exist_ok=True)
    try:
        yield root
    finally:
        shutil.rmtree(root, ignore_errors=True)
        shutil.rmtree(output_root, ignore_errors=True)
        shutil.rmtree(output_root_second, ignore_errors=True)


def _make_valid_manifest(phase10c_workspace: Path) -> tuple[Path, Path, Path]:
    evidence_dir = phase10c_workspace / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence = evidence_dir / "audit-export-manifest.json"
    evidence.write_text('{"artifact":"phase8e"}\n', encoding="utf-8")
    manifest = phase10c_workspace / "manifest.json"
    _write_json(
        manifest,
        _sample_manifest(
            phase10c_workspace,
            evidence_path=str(evidence.relative_to(REPO_ROOT)),
        ),
    )
    output_dir = OUTPUT_ROOT / f"pytest-{phase10c_workspace.name}"
    return manifest, evidence, output_dir


def _bundle_hash_without_self(bundle: dict) -> str:
    clone = json.loads(json.dumps(bundle))
    clone.pop("bundle_hash", None)
    return hashlib.sha256(_canonical_json(clone).encode("utf-8")).hexdigest()


# A. File existence and status


def test_phase10c_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, SCRIPT, RUNNER, THIS_TEST):
        assert path.is_file(), f"missing Phase 10C file: {path}"


def test_phase10c_status_tokens() -> None:
    assert "phase10c_status: success" in _text(TASK_FILE)
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "phase10c_status: success",
            "phase10b_status: success",
            "phase10a_status: success",
            "phase7d_runtime_readiness: implemented_manual_gate",
            "durable_audit_store_status: phase8_final_acceptance_pack",
            "audit_actor_attribution_integration_status: design_only",
            "governed_runtime_integration_status: local_evidence_bundle_prototype",
            "integration_runtime_status: local_evidence_bundle_prototype",
            "local_evidence_bundle_status: prototype_local_only",
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


# B. Scope safety tokens


def test_phase10c_scope_safety_tokens() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "local-only derived evidence bundle runtime prototype",
            "standard library only",
            "read one local manifest",
            "validate safe evidence/context references",
            "hash present files",
            "safe missing files",
            "built_with_warnings",
            "reject unsafe paths",
            "reject secrets",
            "reject approval flags",
            "reject execution intent",
            "emit deterministic json + markdown",
            "no audit store mutation",
            "no integration enforcement",
            "no authentication runtime",
            "no rbac enforcement",
            "no backend/api/database",
            "no wrapper behavior change",
            "no primitive execution",
            "no vault read/write",
        ),
        label="scope safety token",
    )


# C. Runtime static safety


def test_phase10c_script_no_forbidden_imports() -> None:
    text = _text(SCRIPT)
    for forbidden in (
        "import subprocess",
        "from subprocess",
        "import sqlite3",
        "import boto3",
        "import requests",
        "import httpx",
        "import urllib",
    ):
        assert forbidden not in text, f"builder must not: {forbidden}"
    for bad in ("fastapi", "sqlalchemy", "flask", "django"):
        assert bad not in text.lower(), f"builder must not reference {bad}"


def test_phase10c_script_no_forbidden_runtime_calls() -> None:
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
        "os.system(",
        "subprocess.",
    ):
        assert forbidden not in text, f"builder must not contain: {forbidden}"


def test_phase10c_runner_static_safety() -> None:
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
        "evaluate_phase9f_local_rbac_policy.py",
        "vault/",
        "curl ",
        "wget ",
    ):
        assert forbidden not in text, f"runner must not contain: {forbidden}"


def test_phase10c_runner_executable_mode() -> None:
    mode = RUNNER.stat().st_mode & 0o777
    assert mode == 0o755, f"expected 0755, got {oct(mode)}"


def test_phase10c_runner_bash_syntax_ok() -> None:
    result = subprocess.run(["bash", "-n", str(RUNNER)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_phase10c_script_py_compile_ok() -> None:
    result = subprocess.run([sys.executable, "-m", "py_compile", str(SCRIPT)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


# D. Valid bundle behavior


def test_phase10c_valid_bundle_builds(phase10c_workspace: Path) -> None:
    manifest, evidence, output_dir = _make_valid_manifest(phase10c_workspace)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode == 0, result.stderr

    bundle = _load_bundle(output_dir)
    assert bundle["bundle_status"] == "built"
    assert bundle["reviewer_action"] == "no_action_required"
    assert bundle["reviewer_action_required"] is False
    assert bundle["incident_classification"] == "none"
    assert bundle["present_evidence_count"] == 1
    assert bundle["missing_evidence_count"] == 0
    assert bundle["invalid_evidence_count"] == 0
    assert bundle["evidence_reference_count"] == 1
    assert bundle["optional_context_count"] == 0

    ref = bundle["evidence_references"][0]
    assert ref["evidence_status"] == "present"
    assert ref["relative_path"] == str(evidence.relative_to(REPO_ROOT))
    assert ref["size_bytes"] == evidence.stat().st_size
    assert ref["sha256"] == _sha256(evidence)


# E. Missing evidence warning behavior


def test_phase10c_missing_evidence_is_warning(phase10c_workspace: Path) -> None:
    manifest = phase10c_workspace / "manifest.json"
    missing = phase10c_workspace / "evidence" / "missing.json"
    _write_json(
        manifest,
        _sample_manifest(
            phase10c_workspace,
            evidence_path=str(missing.relative_to(REPO_ROOT)),
        ),
    )
    output_dir = OUTPUT_ROOT / f"pytest-{phase10c_workspace.name}-missing"
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode == 0, result.stderr

    bundle = _load_bundle(output_dir)
    assert bundle["bundle_status"] == "built_with_warnings"
    assert bundle["reviewer_action"] == "manual_review_required"
    assert bundle["reviewer_action_required"] is True
    assert bundle["incident_classification"] == "evidence_review_required"
    assert bundle["present_evidence_count"] == 0
    assert bundle["missing_evidence_count"] == 1
    assert bundle["invalid_evidence_count"] == 0
    assert bundle["severity_counts"]["warning"] >= 1
    assert any(issue["severity"] == "warning" for issue in bundle["issues"])
    assert bundle["evidence_references"][0]["evidence_status"] == "missing"


# F. Optional context behavior


def test_phase10c_optional_contexts_count_and_hash(phase10c_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10c_workspace)
    actor_ref = phase10c_workspace / "context" / "actor.json"
    actor_ref.parent.mkdir(parents=True, exist_ok=True)
    actor_ref.write_text('{"actor":"operator-a"}\n', encoding="utf-8")
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["actor_context_reference"] = {
        "reference_type": "actor_context_reference",
        "reference_path": str(actor_ref.relative_to(REPO_ROOT)),
        "reference_boundary_statement": "actor context is not authentication",
    }
    _write_json(manifest, payload)

    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode == 0, result.stderr
    bundle = _load_bundle(output_dir)
    assert bundle["optional_context_count"] == 1
    assert bundle["actor_context_reference"]["reference_status"] == "present"
    assert bundle["actor_context_reference"]["sha256"] == _sha256(actor_ref)


def test_phase10c_missing_optional_context_is_warning(phase10c_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10c_workspace)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["rbac_advisory_context_reference"] = {
        "reference_type": "rbac_advisory_context_reference",
        "reference_path": str((phase10c_workspace / "context" / "missing-rbac.json").relative_to(REPO_ROOT)),
        "reference_boundary_statement": "RBAC advisory context is not enforcement",
    }
    _write_json(manifest, payload)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode == 0, result.stderr

    bundle = _load_bundle(output_dir)
    assert bundle["bundle_status"] == "built_with_warnings"
    assert bundle["optional_context_count"] == 1
    assert bundle["rbac_advisory_context_reference"]["reference_status"] == "missing"


# G. Invalid manifest behavior


def test_phase10c_invalid_manifest_is_not_built(phase10c_workspace: Path) -> None:
    manifest = phase10c_workspace / "manifest.json"
    _write_json(
        manifest,
        {
            "bundle_schema_version": "wrong",
            "bundle_id": "bundle-phase10c-sample",
            "bundle_purpose": "bad",
            "approval_boundary_statement": "local evidence bundle is not approval",
            "evidence_references": [],
        },
    )
    output_dir = OUTPUT_ROOT / f"pytest-{phase10c_workspace.name}-invalid-manifest"
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0

    bundle = _load_bundle(output_dir)
    assert bundle["bundle_status"] == "not_built"
    assert bundle["reviewer_action"] in {
        "reject_evidence_bundle_until_resolved",
        "reject_runtime_scope_until_resolved",
    }
    assert bundle["invalid_evidence_count"] >= 1 or bundle["severity_counts"]["critical"] >= 1


# H. Evidence reference validation


def test_phase10c_invalid_evidence_type_is_rejected(phase10c_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10c_workspace)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["evidence_references"][0]["evidence_type"] = "invalid_type"
    _write_json(manifest, payload)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0
    bundle = _load_bundle(output_dir)
    assert bundle["bundle_status"] == "not_built"
    assert bundle["severity_counts"]["critical"] >= 1


def test_phase10c_invalid_evidence_phase_is_rejected(phase10c_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10c_workspace)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["evidence_references"][0]["evidence_phase"] = "phase11"
    _write_json(manifest, payload)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0
    bundle = _load_bundle(output_dir)
    assert bundle["bundle_status"] == "not_built"


# I. Privacy and secret validation


@pytest.mark.parametrize(
    "field_name,value",
    (
        ("bundle_id", "bundle-owner@example.com"),
        ("bundle_purpose", "API_KEY=secret"),
        ("bundle_purpose", "BEGIN PRIVATE KEY"),
    ),
)
def test_phase10c_secret_like_manifest_strings_are_rejected(
    phase10c_workspace: Path, field_name: str, value: str
) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10c_workspace)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload[field_name] = value
    _write_json(manifest, payload)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0
    bundle = _load_bundle(output_dir)
    assert bundle["bundle_status"] == "not_built"
    assert bundle["incident_classification"] == "privacy_review_required"


def test_phase10c_secret_like_evidence_metadata_is_rejected(phase10c_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10c_workspace)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["evidence_references"][0]["evidence_purpose"] = "TOKEN=secret"
    _write_json(manifest, payload)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0
    bundle = _load_bundle(output_dir)
    assert bundle["bundle_status"] == "not_built"
    assert bundle["incident_classification"] == "privacy_review_required"


# J. Approval boundary validation


def test_phase10c_manifest_requires_not_approval_statement(phase10c_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10c_workspace)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["approval_boundary_statement"] = "review only"
    _write_json(manifest, payload)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0
    bundle = _load_bundle(output_dir)
    assert bundle["incident_classification"] == "approval_boundary_review_required"


def test_phase10c_truthy_approval_flag_is_rejected(phase10c_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10c_workspace)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["approved"] = True
    _write_json(manifest, payload)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0
    bundle = _load_bundle(output_dir)
    assert bundle["bundle_status"] == "not_built"
    assert bundle["incident_classification"] == "approval_boundary_review_required"


@pytest.mark.parametrize("field_name", ("next_gate", "execute", "enforcement_enabled"))
def test_phase10c_execution_intent_is_rejected(phase10c_workspace: Path, field_name: str) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10c_workspace)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload[field_name] = True
    _write_json(manifest, payload)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0
    bundle = _load_bundle(output_dir)
    assert bundle["bundle_status"] == "not_built"
    assert bundle["incident_classification"] in {
        "approval_boundary_review_required",
        "runtime_scope_violation",
        "primitive_execution_blocked",
    }


# K. Path safety


def test_phase10c_unsafe_docs_path_is_rejected(phase10c_workspace: Path) -> None:
    manifest = phase10c_workspace / "manifest.json"
    _write_json(
        manifest,
        _sample_manifest(
            phase10c_workspace,
            evidence_path="docs/PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE.md",
        ),
    )
    output_dir = OUTPUT_ROOT / f"pytest-{phase10c_workspace.name}-unsafe-docs"
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0
    bundle = _load_bundle(output_dir)
    assert bundle["bundle_status"] == "not_built"
    assert bundle["incident_classification"] == "runtime_scope_violation"


def test_phase10c_traversal_output_dir_is_rejected(phase10c_workspace: Path) -> None:
    manifest, _, _ = _make_valid_manifest(phase10c_workspace)
    bad_output = REPO_ROOT / "tmp" / ".." / "phase10c-bad"
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(bad_output))
    assert result.returncode != 0


def test_phase10c_symlink_evidence_is_rejected(phase10c_workspace: Path) -> None:
    target = phase10c_workspace / "evidence" / "real.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('{"x":1}\n', encoding="utf-8")
    link = phase10c_workspace / "evidence" / "symlink.json"
    link.symlink_to(target)
    manifest = phase10c_workspace / "manifest.json"
    _write_json(
        manifest,
        _sample_manifest(
            phase10c_workspace,
            evidence_path=str(link.relative_to(REPO_ROOT)),
        ),
    )
    output_dir = OUTPUT_ROOT / f"pytest-{phase10c_workspace.name}-symlink"
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode != 0
    bundle = _load_bundle(output_dir)
    assert bundle["bundle_status"] == "not_built"


# L. Deterministic output/hash behavior


def test_phase10c_bundle_hash_is_deterministic_and_excludes_itself(phase10c_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10c_workspace)
    result_one = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result_one.returncode == 0, result_one.stderr
    bundle_one = _load_bundle(output_dir)
    hash_one = bundle_one["bundle_hash"]

    second_output = OUTPUT_ROOT / f"pytest-{phase10c_workspace.name}-second"
    result_two = _run_builder("--manifest", str(manifest), "--output-dir", str(second_output))
    assert result_two.returncode == 0, result_two.stderr
    bundle_two = _load_bundle(second_output)

    assert bundle_two["bundle_hash"] == hash_one
    assert _bundle_hash_without_self(bundle_one) == hash_one
    assert _bundle_hash_without_self(bundle_two) == hash_one


def test_phase10c_markdown_report_contains_boundaries(phase10c_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10c_workspace)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode == 0, result.stderr

    report = _text(output_dir / "local-evidence-bundle.md").lower()
    for token in (
        "local evidence bundle is not approval",
        "evidence bundle validity is not approval",
        "actor context is not authentication",
        "rbac advisory context is not enforcement",
        "rbac allow decision is not approval",
        "approval remains phase 7d selected-gate manual boundary",
    ):
        assert token in report, f"missing markdown boundary token: {token}"


# M. Report schema behavior


def test_phase10c_bundle_schema_fields_present(phase10c_workspace: Path) -> None:
    manifest, _, output_dir = _make_valid_manifest(phase10c_workspace)
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode == 0, result.stderr
    bundle = _load_bundle(output_dir)

    for key in STATIC_STATUS_TOKENS:
        assert key in bundle, f"missing status field: {key}"

    for key in (
        "bundle_schema_version",
        "bundle_id",
        "bundle_purpose",
        "bundle_status",
        "evidence_reference_count",
        "present_evidence_count",
        "missing_evidence_count",
        "invalid_evidence_count",
        "optional_context_count",
        "bundle_hash",
        "reviewer_action",
        "reviewer_action_required",
        "incident_classification",
        "severity_counts",
        "approval_boundary_statement",
        "safety_statement",
        "limitations",
        "issues",
        "evidence_references",
    ):
        assert key in bundle, f"missing bundle field: {key}"

    assert set(bundle["severity_counts"]).issuperset({"info", "warning", "critical"})
    for issue in bundle["issues"]:
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


# N. Source immutability behavior


def test_phase10c_source_evidence_is_unchanged(phase10c_workspace: Path) -> None:
    manifest, evidence, output_dir = _make_valid_manifest(phase10c_workspace)
    before = evidence.read_bytes()
    result = _run_builder("--manifest", str(manifest), "--output-dir", str(output_dir))
    assert result.returncode == 0, result.stderr
    after = evidence.read_bytes()
    assert after == before


# O. Documentation regression refs


def test_phase10c_doc_and_task_reference_canonical_phase8b_names() -> None:
    for path in (TASK_FILE, DOC):
        text = _text(path)
        assert "docs/PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE.md" in text
        assert "tests/test_phase8b_local_append_only_audit_store.py" in text
        if "PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE_PROTOTYPE.md" in text:
            assert "earlier task wording may refer" in text.lower()
            assert "canonical phase 8b document" in text.lower()


def test_phase10c_required_sections_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "### Purpose",
            "### Scope",
            "### Runtime command",
            "### Manifest model",
            "### Evidence reference model",
            "### Optional context references",
            "### Output layout",
            "### Source immutability",
            "### Path safety",
            "### Privacy and secret handling",
            "### Approval boundary",
            "### Non-authentication boundary",
            "### Non-RBAC-enforcement boundary",
            "### Non-approval boundary",
            "### Compatibility with Phase 10B",
            "### Compatibility with Phase 10A",
            "### Compatibility with Phase 9G/9F/9D/9C",
            "### Compatibility with Phase 8O/8M/8G/8E/8C/8B",
            "### Compatibility with Phase 7D",
            "### Failure taxonomy",
            "### Reviewer action mapping",
            "### Known limitations",
        ),
        label="section",
    )


# P. Protected runtime files unchanged


def test_phase10c_protected_runtime_hashes_unchanged() -> None:
    for path, expected in PROTECTED_HASHES.items():
        assert path.is_file(), f"missing protected file: {path}"
        assert _sha256(path) == expected, f"protected runtime changed unexpectedly: {path}"


# Q. Static safety for new Phase 10C files only


def test_phase10c_new_files_do_not_reference_forbidden_artifacts() -> None:
    for path in (TASK_FILE, DOC, SCRIPT, RUNNER):
        text = _flat(path)
        for forbidden in FORBIDDEN_EXTENSIONS:
            assert forbidden not in text, f"forbidden extension reference in {path}: {forbidden}"


# R. Repo-wide artifact safety


def test_phase10c_gitignore_entries_present() -> None:
    text = _text(GITIGNORE)
    assert "tmp/phase10c-local-evidence-bundle/" in text
    assert "tmp/phase10c-test-input/" in text


def test_phase10c_docs_and_state_references_present() -> None:
    assert "Phase 10C" in _text(ROADMAP)
    assert "Phase 10C" in _text(PROJECT_STATE)
    assert "docs/PHASE10C_LOCAL_EVIDENCE_BUNDLE_ACTOR_RBAC_CONTEXT.md" in _text(PROJECT_STATE)
    assert "local_evidence_bundle_prototype" in _text(ROADMAP)
    assert "local_evidence_bundle_prototype" in _text(PROJECT_STATE)
    assert "Phase 5" in _text(ROADMAP)
    assert "read-only" in _text(ROADMAP)
    assert "manual-approved" in _text(ROADMAP)


def test_phase10c_cross_phase_pointer_updates_present() -> None:
    for path in (
        PHASE10B_DOC,
        PHASE10A_DOC,
        PHASE9G_DOC,
        PHASE9F_DOC,
        PHASE9D_DOC,
        PHASE8O_DOC,
    ):
        text = _text(path)
        assert "Phase 10C" in text, f"missing Phase 10C pointer in {path}"
        assert "PHASE10C_LOCAL_EVIDENCE_BUNDLE_ACTOR_RBAC_CONTEXT.md" in text


def test_phase10c_task_uses_canonical_focused_verification_command() -> None:
    text = _text(TASK_FILE)
    assert "python -m pytest -q tests/test_phase8b_local_append_only_audit_store.py" in text
    assert "tests/test_phase8b_local_audit_store.py" not in text
