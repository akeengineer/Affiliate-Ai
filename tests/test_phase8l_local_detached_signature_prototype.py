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

TASK_FILE = REPO_ROOT / "codex/tasks/063-phase8l-local-detached-signature-prototype.md"
DOC = REPO_ROOT / "docs/PHASE8L_LOCAL_DETACHED_SIGNATURE_PROTOTYPE.md"
RUNTIME_SCRIPT = REPO_ROOT / "scripts/dev/build_phase8l_detached_signature.py"
SHELL_RUNNER = REPO_ROOT / "scripts/dev/run_phase8l_detached_signature.sh"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE8K_DOC = REPO_ROOT / "docs/PHASE8K_KEY_MANAGEMENT_DESIGN.md"
PHASE8J_DOC = REPO_ROOT / "docs/PHASE8J_DETACHED_SIGNATURE_VERIFIER_DESIGN.md"
PHASE8I_DOC = REPO_ROOT / "docs/PHASE8I_DETACHED_SIGNATURE_DESIGN_FINALIZATION.md"

NEW_PHASE8L_FILES = (TASK_FILE, DOC, RUNTIME_SCRIPT, SHELL_RUNNER)

OUTPUT_ROOT = REPO_ROOT / "tmp/phase8l-detached-signature"
INPUT_ROOT = REPO_ROOT / "tmp/phase8l-test-input"

PROTOTYPE_KEY_ENV = "AFFILIATE_PHASE8L_PROTOTYPE_KEY"
TEST_KEY_VALUE = "phase8l-unit-test-secret"

PROTECTED_HASHES = {
    REPO_ROOT / "scripts/dev/verify_phase8g_export_integrity.py": "1711d387f813b2d8e046704ed7063f1ad7c050413c0b999b7358e0ad6939dc1c",
    REPO_ROOT / "scripts/dev/run_phase8g_export_integrity.sh": "486258b28e74f9034681e5cc7d3827efddbc19ed6e5f0a6266097d6679560c9d",
    REPO_ROOT / "scripts/dev/build_phase8e_audit_export_pack.py": "c656cb49c645f056be4069e78aa5fdf63cc77d3a6676d2ae5bd96fde2a0d8b31",
    REPO_ROOT / "scripts/dev/run_phase8e_audit_export.sh": "9441dc0e5a3fa692fb532c1f1475f89f871b4ed4289bb0d567cf26e6a1305cca",
    REPO_ROOT / "scripts/dev/query_phase8d_audit_store.py": "3ffab49a1cd16a744a8fe04e788601e567b2191a94a3fbcda55d8da864e5bf82",
    REPO_ROOT / "scripts/dev/run_phase8d_audit_query.sh": "2ad91d7551d5c027203772ab6109aebaf08eb21766fbe64fde07208205179649",
    REPO_ROOT / "scripts/dev/verify_phase8c_audit_store.py": "87edb8355f3f5868782a16060950d53bb80e09ac3f27d99e16377261fc763787",
    REPO_ROOT / "scripts/dev/run_phase8c_audit_report.sh": "72755c4576de3485a4827a4ce908c4dc64e53cb36cf907e335ff622c52ade7f1",
    REPO_ROOT / "scripts/dev/ingest_phase8b_audit_record.py": "d4af3b87e058a5ff93bf4b9ce57471dca4782a432098206df5dbb4275b7ff8a0",
    REPO_ROOT / "scripts/dev/run_phase8b_audit_ingest.sh": "9eeeb71d72fd6183caddf97a9dfa7406f985fcac06af5f16f67c2d7f9d2ca343",
    REPO_ROOT / "scripts/dev/run_phase7d_single_gate_wrapper.sh": "372aef7a133950a24a1de859a1ba0c01486fd2c84bf46ded783105acc4e47b7d",
    REPO_ROOT / "scripts/dev/execute_single_gate_approval.py": "1b1d00817b1ae89c2840f18c9fe3b73f091abec9c900bf0bff83ad6820e9cebb",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").lower().split())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _clean_env() -> dict:
    env = os.environ.copy()
    env.pop(PROTOTYPE_KEY_ENV, None)
    return env


def _run(args: list[str], env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(RUNTIME_SCRIPT), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env if env is not None else _clean_env(),
    )


def _unique_output_dir(name: str) -> Path:
    unique = f"{name}-{uuid.uuid4().hex[:12]}"
    return OUTPUT_ROOT / unique


def _unique_input_dir(name: str) -> Path:
    unique = f"{name}-{uuid.uuid4().hex[:12]}"
    path = INPUT_ROOT / unique
    path.mkdir(parents=True, exist_ok=True)
    return path


def _rel(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


VALID_MANIFEST = {
    "phase8e_status": "success",
    "durable_audit_store_status": "export_pack",
    "export_dir": "tmp/phase8e-audit-export",
    "record_count": 3,
    "generated_at": "2026-07-03T00:00:00Z",
    "bundle_hash": "abc123",
}

VALID_INTEGRITY = {
    "report_schema_version": "phase8g.integrity_report.v2",
    "verification_status": "valid",
    "compatibility_result": "compatible",
    "incident_classification": "none",
    "reviewer_action": "no_action_required",
    "reviewer_action_required": False,
    "computed_bundle_hash": "deadbeef",
    "computed_manifest_hash": "cafef00d",
    "verifier_hardening_status": "enabled",
    "issue_taxonomy_version": "phase8h.issue_taxonomy.v1",
    "compatibility_matrix_version": "phase8h.compatibility_matrix.v1",
}


@pytest.fixture(autouse=True)
def _cleanup_tmp_roots():
    yield
    # Tidy per-test unique dirs; both roots are gitignored anyway.


def _write_manifest(input_dir: Path, manifest: dict = VALID_MANIFEST) -> Path:
    path = input_dir / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _write_integrity(input_dir: Path, integrity: dict = VALID_INTEGRITY) -> Path:
    path = input_dir / "integrity.json"
    path.write_text(json.dumps(integrity, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


DESCRIPTOR_REQUIRED_FIELDS = (
    "payload_schema_version",
    "export_manifest_path",
    "export_manifest_sha256",
    "bundle_hash",
    "computed_manifest_hash",
    "report_schema_version",
    "issue_taxonomy_version",
    "compatibility_matrix_version",
    "verifier_hardening_status",
    "verification_status",
    "compatibility_result",
    "incident_classification",
    "reviewer_action",
    "reviewer_action_required",
    "generated_from_phase",
    "generated_by_tool",
    "created_at_utc",
    "signing_policy_version",
    "signer_id",
    "signer_role",
    "signer_identity_assurance",
    "key_id",
    "key_version",
    "approval_boundary_statement",
)

ENVELOPE_REQUIRED_FIELDS = (
    "signature_schema_version",
    "signed_payload_sha256",
    "signed_payload_descriptor_path",
    "detached_signature_path",
    "signature_algorithm",
    "signature_encoding",
    "key_id",
    "key_version",
    "signer_id",
    "signer_role",
    "signer_identity_assurance",
    "signing_policy_version",
    "signing_timestamp_utc",
    "signature_status",
    "signing_status",
    "verification_status",
    "revocation_status",
    "rotation_epoch",
    "approval_boundary_statement",
    "signature_runtime_status",
    "signing_implementation_status",
    "detached_signature_value",
)


# ── A. File existence & status ──────────────────────────────────────────────

def test_phase8l_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, RUNTIME_SCRIPT, SHELL_RUNNER, THIS_TEST):
        assert path.is_file(), f"missing Phase 8L file: {path}"


def test_phase8l_task_status_token() -> None:
    assert "phase8l_status: success" in _text(TASK_FILE)


def test_phase8l_doc_status_tokens() -> None:
    text = _text(DOC)
    for token in (
        "phase8l_status: success",
        "phase7d_runtime_readiness: implemented_manual_gate",
        "durable_audit_store_status: local_detached_signature_prototype",
        "signing_implementation_status: prototype_local_only",
        "signature_runtime_status: local_prototype",
        "signature_verifier_runtime_status: not_implemented",
        "key_management_runtime_status: not_implemented",
        "major_phase_branch_workflow: enabled",
    ):
        assert token in text, f"missing status token: {token}"


# ── B. Scope safety ──────────────────────────────────────────────────────────

def test_phase8l_doc_scope_tokens() -> None:
    low = _text(DOC).lower()
    for token in (
        "local-only detached signature prototype",
        "signed payload descriptor generation",
        "detached signature envelope generation",
        "hmac-sha256 prototype signature only",
        "no committed private keys",
        "no key generation",
        "no kms/secrets manager",
        "no backend/api/database",
        "no signature verifier implementation",
        "no wrapper behavior change",
        "no primitive execution",
        "no vault read/write",
        "no new mutation path",
        "no next-gate automation",
        "no chain execution",
    ):
        assert token in low, f"missing scope token: {token}"


# ── C. Runtime static safety ─────────────────────────────────────────────────

def test_phase8l_runtime_script_no_forbidden_imports_or_primitives() -> None:
    text = _text(RUNTIME_SCRIPT)
    for forbidden in (
        "import subprocess",
        "import sqlite3",
        "import boto3",
        "import requests",
        "import httpx",
        "import urllib",
        "fastapi",
        "FastAPI",
        "sqlite3.connect",
        "boto3.",
        "CREATE TABLE",
        "ssh-keygen",
        "openssl",
        "gpg ",
        "promote_product_candidates.py",
        "create_decision.py",
        "finalize_decision.py",
        "run_phase7d",
    ):
        assert forbidden not in text, f"runtime script must not contain: {forbidden}"


def test_phase8l_shell_runner_static_safety() -> None:
    text = _text(SHELL_RUNNER)
    assert "--execute" not in text
    for name in ("APPROVE_PROMOTE", "APPROVE_DECISION", "APPROVE_FINALIZE"):
        assert f"{name}=true" not in text, f"shell runner must not truthy-assign {name}"
    for forbidden in (
        "run_phase7d_single_gate_wrapper.sh",
        "execute_single_gate_approval.py",
        "ingest_phase8b",
        "verify_phase8c",
        "query_phase8d",
        "build_phase8e",
        "verify_phase8g_export_integrity",
    ):
        assert forbidden not in text, f"shell runner must not invoke: {forbidden}"


def test_phase8l_shell_runner_executable_mode() -> None:
    mode = SHELL_RUNNER.stat().st_mode & 0o777
    assert oct(mode) == "0o755", f"expected 0o755, got {oct(mode)}"


def test_phase8l_shell_runner_bash_syntax_ok() -> None:
    result = subprocess.run(["bash", "-n", str(SHELL_RUNNER)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_phase8l_runtime_script_py_compile_ok() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(RUNTIME_SCRIPT)], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr


# ── D. Missing manifest behavior ─────────────────────────────────────────────

def test_phase8l_missing_manifest_behavior() -> None:
    input_dir = _unique_input_dir("d-missing-manifest")
    output_dir = _unique_output_dir("d-missing-manifest")
    try:
        absent = input_dir / "absent.json"
        result = _run(
            ["--manifest-path", _rel(absent), "--output-dir", _rel(output_dir)]
        )
        assert result.returncode == 0, result.stderr

        summary_json = output_dir / "detached-signature-summary.json"
        summary_md = output_dir / "detached-signature-summary.md"
        assert summary_json.is_file()
        assert summary_md.is_file()
        assert not (output_dir / "signed-payload-descriptor.json").exists()
        assert not (output_dir / "detached-signature-envelope.json").exists()

        summary = json.loads(summary_json.read_text(encoding="utf-8"))
        assert summary["signing_status"] == "skipped_missing_manifest"
        assert summary["signature_status"] == "not_present"

        md_low = summary_md.read_text(encoding="utf-8").lower()
        assert "signature is not approval" in md_low
    finally:
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)


# ── E. Missing prototype key ─────────────────────────────────────────────────

def test_phase8l_missing_prototype_key_behavior() -> None:
    input_dir = _unique_input_dir("e-missing-key")
    output_dir = _unique_output_dir("e-missing-key")
    try:
        manifest_path = _write_manifest(input_dir)
        result = _run(
            ["--manifest-path", _rel(manifest_path), "--output-dir", _rel(output_dir)]
        )
        assert result.returncode == 0, result.stderr

        descriptor_path = output_dir / "signed-payload-descriptor.json"
        envelope_path = output_dir / "detached-signature-envelope.json"
        summary_json = output_dir / "detached-signature-summary.json"
        summary_md = output_dir / "detached-signature-summary.md"
        for p in (descriptor_path, envelope_path, summary_json, summary_md):
            assert p.is_file(), f"expected output missing: {p}"
        assert not (output_dir / "detached-signature.sig").exists()

        summary = json.loads(summary_json.read_text(encoding="utf-8"))
        assert summary["signing_status"] == "skipped_missing_prototype_key"
        assert summary["signature_status"] == "not_ready"
        assert isinstance(summary["signed_payload_sha256"], str) and summary["signed_payload_sha256"]

        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
        assert envelope["detached_signature_value"] is None

        for p in (descriptor_path, envelope_path, summary_json, summary_md):
            assert TEST_KEY_VALUE not in p.read_text(encoding="utf-8")

        assert "signature is not approval" in summary_md.read_text(encoding="utf-8").lower()
    finally:
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)


# ── F. Successful signing ────────────────────────────────────────────────────

def test_phase8l_successful_signing_behavior() -> None:
    input_dir = _unique_input_dir("f-signed")
    output_dir = _unique_output_dir("f-signed")
    try:
        manifest_path = _write_manifest(input_dir)
        integrity_path = _write_integrity(input_dir)
        manifest_bytes_before = manifest_path.read_bytes()
        integrity_bytes_before = integrity_path.read_bytes()

        env = os.environ.copy()
        env.pop(PROTOTYPE_KEY_ENV, None)
        env[PROTOTYPE_KEY_ENV] = TEST_KEY_VALUE

        result = _run(
            [
                "--manifest-path", _rel(manifest_path),
                "--integrity-report-path", _rel(integrity_path),
                "--output-dir", _rel(output_dir),
            ],
            env=env,
        )
        assert result.returncode == 0, result.stderr

        descriptor_path = output_dir / "signed-payload-descriptor.json"
        envelope_path = output_dir / "detached-signature-envelope.json"
        summary_json = output_dir / "detached-signature-summary.json"
        summary_md = output_dir / "detached-signature-summary.md"
        sig_path = output_dir / "detached-signature.sig"
        for p in (descriptor_path, envelope_path, summary_json, summary_md, sig_path):
            assert p.is_file(), f"expected output missing: {p}"

        summary = json.loads(summary_json.read_text(encoding="utf-8"))
        assert summary["signing_status"] == "signed_local_prototype"
        assert summary["signature_status"] == "present"
        assert summary["prototype_signature_algorithm"] == "hmac-sha256-prototype"

        descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
        recomputed_hash = _sha256_bytes(_canonical_json(descriptor).encode("utf-8"))
        assert recomputed_hash == summary["signed_payload_sha256"]

        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
        assert recomputed_hash == envelope["signed_payload_sha256"]

        import hmac

        expected_sig = hmac.new(
            TEST_KEY_VALUE.encode("utf-8"), recomputed_hash.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        assert envelope["detached_signature_value"] == expected_sig

        # Raw key must never leak into any output file.
        for p in (descriptor_path, envelope_path, summary_json, summary_md, sig_path):
            assert TEST_KEY_VALUE not in p.read_text(encoding="utf-8"), f"raw key leaked into {p}"

        # All written files must live under the chosen output-dir.
        written_files = [descriptor_path, envelope_path, summary_json, summary_md, sig_path]
        for p in written_files:
            assert OUTPUT_ROOT in p.resolve().parents
            assert output_dir.resolve() in p.resolve().parents or p.resolve().parent == output_dir.resolve()

        # Inputs must not be mutated.
        assert manifest_path.read_bytes() == manifest_bytes_before
        assert integrity_path.read_bytes() == integrity_bytes_before
    finally:
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)


# ── G. Descriptor schema ─────────────────────────────────────────────────────

def test_phase8l_descriptor_schema() -> None:
    input_dir = _unique_input_dir("g-descriptor")
    output_dir = _unique_output_dir("g-descriptor")
    try:
        manifest_path = _write_manifest(input_dir)
        integrity_path = _write_integrity(input_dir)
        env = os.environ.copy()
        env.pop(PROTOTYPE_KEY_ENV, None)
        env[PROTOTYPE_KEY_ENV] = TEST_KEY_VALUE
        result = _run(
            [
                "--manifest-path", _rel(manifest_path),
                "--integrity-report-path", _rel(integrity_path),
                "--output-dir", _rel(output_dir),
            ],
            env=env,
        )
        assert result.returncode == 0, result.stderr

        descriptor_path = output_dir / "signed-payload-descriptor.json"
        descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
        for field in DESCRIPTOR_REQUIRED_FIELDS:
            assert field in descriptor, f"missing descriptor field: {field}"

        assert "approval_boundary_statement" in descriptor
        assert TEST_KEY_VALUE not in descriptor_path.read_text(encoding="utf-8")

        assert descriptor["generated_by_tool"] == "build_phase8l_detached_signature.py"
        assert descriptor["payload_schema_version"] == "phase8l.signed_payload_descriptor.v1"
    finally:
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)


# ── H. Envelope schema ───────────────────────────────────────────────────────

def test_phase8l_envelope_schema() -> None:
    input_dir = _unique_input_dir("h-envelope")
    output_dir = _unique_output_dir("h-envelope")
    try:
        manifest_path = _write_manifest(input_dir)
        env = os.environ.copy()
        env.pop(PROTOTYPE_KEY_ENV, None)
        env[PROTOTYPE_KEY_ENV] = TEST_KEY_VALUE
        result = _run(
            ["--manifest-path", _rel(manifest_path), "--output-dir", _rel(output_dir)],
            env=env,
        )
        assert result.returncode == 0, result.stderr

        envelope_path = output_dir / "detached-signature-envelope.json"
        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
        for field in ENVELOPE_REQUIRED_FIELDS:
            assert field in envelope, f"missing envelope field: {field}"

        assert envelope["signature_algorithm"] == "hmac-sha256-prototype"
        assert envelope["signature_encoding"] == "hex"
        assert envelope["verification_status"] == "not_verified"
        assert envelope["revocation_status"] == "not_checked"
        assert envelope["rotation_epoch"] == "prototype"
        assert envelope["signature_schema_version"] == "phase8l.detached_signature_envelope.v1"

        assert TEST_KEY_VALUE not in envelope_path.read_text(encoding="utf-8")
    finally:
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)


# ── I. Path safety ───────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "manifest_path",
    [
        "docs/PHASE8L_LOCAL_DETACHED_SIGNATURE_PROTOTYPE.md",
        "scripts/dev/build_phase8l_detached_signature.py",
        "tests/test_phase8l_local_detached_signature_prototype.py",
        "codex/tasks/063-phase8l-local-detached-signature-prototype.md",
        "vault/x.json",
    ],
)
def test_phase8l_reject_manifest_path_under_rejected_roots(manifest_path) -> None:
    output_dir = _unique_output_dir("i-rejected-root")
    try:
        result = _run(["--manifest-path", manifest_path, "--output-dir", _rel(output_dir)])
        assert result.returncode != 0
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_phase8l_reject_manifest_path_traversal() -> None:
    output_dir = _unique_output_dir("i-traversal")
    try:
        result = _run(
            ["--manifest-path", "tmp/phase8l-test-input/../../etc/passwd", "--output-dir", _rel(output_dir)]
        )
        assert result.returncode != 0
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_phase8l_reject_symlinked_manifest() -> None:
    input_dir = _unique_input_dir("i-symlink")
    output_dir = _unique_output_dir("i-symlink")
    try:
        real = _write_manifest(input_dir)
        link = input_dir / "link.json"
        try:
            link.symlink_to(real)
        except OSError:
            pytest.skip("symlinks not supported in this environment")
        # Use the unresolved relative path so the symlink itself is what the
        # runtime validates (calling _rel() here would resolve through it).
        link_rel = link.relative_to(REPO_ROOT).as_posix()
        result = _run(["--manifest-path", link_rel, "--output-dir", _rel(output_dir)])
        assert result.returncode != 0
    finally:
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)


def test_phase8l_reject_output_dir_outside_guarded_root() -> None:
    outside = REPO_ROOT / "tmp/some-other-dir"
    try:
        result = _run(["--output-dir", "tmp/some-other-dir"])
        assert result.returncode != 0
    finally:
        shutil.rmtree(outside, ignore_errors=True)


def test_phase8l_invalid_json_manifest_exits_nonzero() -> None:
    input_dir = _unique_input_dir("i-invalid-json")
    output_dir = _unique_output_dir("i-invalid-json")
    try:
        bad = input_dir / "bad.json"
        bad.write_text("not json {{{", encoding="utf-8")
        result = _run(["--manifest-path", _rel(bad), "--output-dir", _rel(output_dir)])
        assert result.returncode != 0
    finally:
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)


def test_phase8l_json_array_manifest_exits_nonzero() -> None:
    input_dir = _unique_input_dir("i-json-array")
    output_dir = _unique_output_dir("i-json-array")
    try:
        arr = input_dir / "array.json"
        arr.write_text("[1,2,3]", encoding="utf-8")
        result = _run(["--manifest-path", _rel(arr), "--output-dir", _rel(output_dir)])
        assert result.returncode != 0
    finally:
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)


# ── J. Documentation regression ──────────────────────────────────────────────

def test_phase8l_roadmap_references() -> None:
    text = _text(ROADMAP)
    assert "Phase 8L" in text
    assert "PHASE8L_LOCAL_DETACHED_SIGNATURE_PROTOTYPE.md" in text
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in text, f"ROADMAP dropped token: {token}"


def test_phase8l_project_state_references() -> None:
    text = _text(PROJECT_STATE)
    assert "docs/PHASE8L_LOCAL_DETACHED_SIGNATURE_PROTOTYPE.md" in text
    for token in (
        "Current architecture",
        "no database",
        "no FastAPI",
        "no UI",
        "no external APIs",
        "no autopublish",
    ):
        assert token in text, f"PROJECT_STATE dropped token: {token}"


def test_phase8l_major_phase_branch_workflow_reference() -> None:
    roadmap = _text(ROADMAP)
    project_state = _text(PROJECT_STATE)
    assert "major_phase_branch_workflow" in roadmap or "major phase branch workflow" in roadmap.lower()
    assert "major_phase_branch_workflow" in project_state or "major phase branch workflow" in project_state.lower()


def test_phase8l_phase8k_doc_references() -> None:
    assert "Phase 8L" in _text(PHASE8K_DOC)


def test_phase8l_phase8j_doc_references() -> None:
    assert "Phase 8L" in _text(PHASE8J_DOC)


def test_phase8l_phase8i_doc_references() -> None:
    assert "Phase 8L" in _text(PHASE8I_DOC)


# ── K. Protected runtime files unchanged ─────────────────────────────────────

def test_phase8l_protected_runtime_files_unchanged() -> None:
    for path, expected_hash in PROTECTED_HASHES.items():
        assert path.is_file(), f"missing protected file: {path}"
        assert _sha256(path) == expected_hash, f"protected runtime changed: {path}"


# ── L. Static safety for new Phase 8L files only ─────────────────────────────

def test_new_phase8l_files_static_safety() -> None:
    banned = (
        "http://",
        "https://",
        "/home/ubuntu/Affiliate-Ai",
        "BEGIN RSA PRIVATE KEY",
        "BEGIN PRIVATE KEY",
        "BEGIN OPENSSH PRIVATE KEY",
        "AWS_SECRET_ACCESS_KEY",
        "OPENAI_API_KEY",
        "sqlite3.connect",
        "boto3.client",
        "boto3.resource",
        "CREATE TABLE",
        "ssh-keygen",
        "openssl genrsa",
        "openssl req",
        "gpg --gen-key",
        "aws kms",
        "cryptography.hazmat",
        "curl ",
        "wget ",
        "uvicorn ",
        "APPROVE_PROMOTE=true",
        "APPROVE_DECISION=true",
        "APPROVE_FINALIZE=true",
    )
    for path in NEW_PHASE8L_FILES:
        text = _text(path)
        for token in banned:
            assert token not in text, f"{path.name} contains forbidden token: {token}"


# ── M. Approval boundary ─────────────────────────────────────────────────────

def test_phase8l_doc_approval_boundary_tokens() -> None:
    low = _text(DOC).lower()
    for token in (
        "signature is not approval",
        "signed export is not approval",
        "local prototype signature is not approval",
        "active/prototype key is not approval",
        "signer metadata is not approval",
        "signature generation does not call wrapper",
        "signature generation does not trigger next gate",
        "signature generation does not set approval flags",
        "phase 7d selected-gate manual boundary",
    ):
        assert token in low, f"missing approval boundary token: {token}"


def test_phase8l_runtime_summary_md_approval_boundary() -> None:
    input_dir = _unique_input_dir("m-approval-md")
    output_dir = _unique_output_dir("m-approval-md")
    try:
        manifest_path = _write_manifest(input_dir)
        result = _run(["--manifest-path", _rel(manifest_path), "--output-dir", _rel(output_dir)])
        assert result.returncode == 0, result.stderr
        md_low = (output_dir / "detached-signature-summary.md").read_text(encoding="utf-8").lower()
        for token in (
            "signature is not approval",
            "signed export is not approval",
            "local prototype signature is not approval",
        ):
            assert token in md_low, f"missing summary md approval token: {token}"
    finally:
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)


# ── N. Repo-wide artifact safety ─────────────────────────────────────────────

EXCLUDED_PARTS = {".git", ".venv", "tmp", "vault", "node_modules"}


def test_phase8l_no_key_cert_files_repo_wide() -> None:
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        assert path.suffix.lower() not in (".pem", ".key", ".crt", ".p12", ".pfx"), f"unexpected key/cert file: {path}"


def test_phase8l_no_package_json_at_repo_root() -> None:
    assert not (REPO_ROOT / "package.json").exists()


def test_phase8l_no_database_files_repo_wide() -> None:
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        assert path.suffix.lower() not in (".sql", ".sqlite", ".db"), f"unexpected database file: {path}"


def test_phase8l_exactly_one_shell_runner() -> None:
    scripts_dir = REPO_ROOT / "scripts/dev"
    matches = sorted(p.name for p in scripts_dir.glob("*phase8l*.sh"))
    assert matches == ["run_phase8l_detached_signature.sh"], f"unexpected phase8l shell runners: {matches}"
