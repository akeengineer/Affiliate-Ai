from __future__ import annotations

import hashlib
import hmac
import json
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/064-phase8m-detached-signature-verifier-prototype.md"
DOC = REPO_ROOT / "docs/PHASE8M_DETACHED_SIGNATURE_VERIFIER_PROTOTYPE.md"
RUNTIME_SCRIPT = REPO_ROOT / "scripts/dev/verify_phase8m_detached_signature.py"
SHELL_RUNNER = REPO_ROOT / "scripts/dev/run_phase8m_detached_signature_verifier.sh"
PHASE8L_BUILDER = REPO_ROOT / "scripts/dev/build_phase8l_detached_signature.py"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE8L_DOC = REPO_ROOT / "docs/PHASE8L_LOCAL_DETACHED_SIGNATURE_PROTOTYPE.md"
PHASE8K_DOC = REPO_ROOT / "docs/PHASE8K_KEY_MANAGEMENT_DESIGN.md"
PHASE8J_DOC = REPO_ROOT / "docs/PHASE8J_DETACHED_SIGNATURE_VERIFIER_DESIGN.md"

NEW_PHASE8M_FILES = (TASK_FILE, DOC, RUNTIME_SCRIPT, SHELL_RUNNER)

OUTPUT_ROOT = REPO_ROOT / "tmp/phase8m-detached-signature-verifier"
INPUT_ROOT = REPO_ROOT / "tmp/phase8m-test-input"
PHASE8L_OUTPUT_ROOT = REPO_ROOT / "tmp/phase8l-detached-signature"

PROTOTYPE_KEY_ENV = "AFFILIATE_PHASE8L_PROTOTYPE_KEY"
TEST_KEY_VALUE_A = "phase8m-unit-test-secret-a"
TEST_KEY_VALUE_B = "phase8m-unit-test-secret-b"

PROTECTED_HASHES = {
    REPO_ROOT / "scripts/dev/build_phase8l_detached_signature.py": "6a7fddfbb3077c18816b81c57738bd79471db5a3f578d35292fde8e8f318de09",
    REPO_ROOT / "scripts/dev/run_phase8l_detached_signature.sh": "ecd3d6846702948f5a9b77addcd6254ea3a7295dcb01765ebcad91ced1a196cb",
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


def _run_8l(args: list[str], env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(PHASE8L_BUILDER), *args],
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


def _unique_phase8l_dir(name: str) -> Path:
    unique = f"{name}-{uuid.uuid4().hex[:12]}"
    return PHASE8L_OUTPUT_ROOT / unique


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


def _write_manifest(input_dir: Path, manifest: dict = VALID_MANIFEST) -> Path:
    path = input_dir / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _produce_pair(name: str, key: str | None) -> tuple[Path, Path, Path, Path]:
    """Build a real Phase 8L descriptor/envelope pair via the 8L builder.

    Returns (input_dir, phase8l_dir, descriptor_path, envelope_path). The
    caller is responsible for removing both input_dir and phase8l_dir.
    Note: the 8L builder's own --output-dir guard only accepts paths under
    tmp/phase8l-detached-signature/, so the produced descriptor/envelope
    live there (not under tmp/phase8m-test-input/); the manifest fixture
    input lives under tmp/phase8m-test-input/.
    """
    input_dir = _unique_input_dir(name)
    phase8l_dir = _unique_phase8l_dir(name)
    manifest_path = _write_manifest(input_dir)
    env = os.environ.copy()
    env.pop(PROTOTYPE_KEY_ENV, None)
    if key:
        env[PROTOTYPE_KEY_ENV] = key
    result = _run_8l(
        ["--manifest-path", _rel(manifest_path), "--output-dir", _rel(phase8l_dir)],
        env=env,
    )
    assert result.returncode == 0, result.stderr
    descriptor_path = phase8l_dir / "signed-payload-descriptor.json"
    envelope_path = phase8l_dir / "detached-signature-envelope.json"
    assert descriptor_path.is_file() and envelope_path.is_file()
    return input_dir, phase8l_dir, descriptor_path, envelope_path


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
)

REPORT_REQUIRED_FIELDS = (
    "phase8m_status",
    "durable_audit_store_status",
    "phase7d_runtime_readiness",
    "signing_implementation_status",
    "signature_runtime_status",
    "signature_verifier_runtime_status",
    "key_management_runtime_status",
    "major_phase_branch_workflow",
    "signature_verification_status",
    "signature_status",
    "verification_status",
    "signature_schema_version",
    "signed_payload_sha256",
    "computed_signed_payload_sha256",
    "signed_payload_hash_status",
    "signature_algorithm",
    "signature_encoding",
    "key_id",
    "key_version",
    "key_status",
    "revocation_status",
    "rotation_status",
    "signer_id",
    "signer_role",
    "signer_identity_assurance",
    "failure_count",
    "severity_counts",
    "incident_classification",
    "reviewer_action",
    "reviewer_action_required",
    "descriptor_path",
    "envelope_path",
    "summary_path",
    "output_dir",
    "issues",
    "safety_statement",
    "approval_boundary_statement",
    "limitations",
)


# ── A. File existence & status ──────────────────────────────────────────────

def test_phase8m_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, RUNTIME_SCRIPT, SHELL_RUNNER, THIS_TEST):
        assert path.is_file(), f"missing Phase 8M file: {path}"


def test_phase8m_task_status_token() -> None:
    assert "phase8m_status: success" in _text(TASK_FILE)


def test_phase8m_doc_status_tokens() -> None:
    text = _text(DOC)
    for token in (
        "phase8m_status: success",
        "phase7d_runtime_readiness: implemented_manual_gate",
        "durable_audit_store_status: detached_signature_verifier_prototype",
        "signing_implementation_status: prototype_local_only",
        "signature_runtime_status: local_prototype",
        "signature_verifier_runtime_status: local_prototype",
        "key_management_runtime_status: not_implemented",
        "major_phase_branch_workflow: enabled",
    ):
        assert token in text, f"missing status token: {token}"


# ── B. Scope safety ──────────────────────────────────────────────────────────

def test_phase8m_doc_scope_tokens() -> None:
    low = _text(DOC).lower()
    for token in (
        "local-only detached signature verifier prototype",
        "hmac-sha256 prototype signature verification only",
        "no signing",
        "no committed private keys",
        "no key generation",
        "no kms/secrets manager",
        "no backend/api/database",
        "no key management runtime",
        "no wrapper behavior change",
        "no primitive execution",
        "no vault read/write",
        "no new mutation path",
        "no next-gate automation",
        "no chain execution",
    ):
        assert token in low, f"missing scope token: {token}"


# ── C. Runtime static safety ─────────────────────────────────────────────────

def test_phase8m_runtime_script_no_forbidden_imports_or_primitives() -> None:
    text = _text(RUNTIME_SCRIPT)
    for forbidden in (
        "import subprocess",
        "import sqlite3",
        "import boto3",
        "import requests",
        "import httpx",
        "import urllib",
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
    # The verifier only verifies; it must not sign or call the 8L builder.
    assert "build_phase8l_detached_signature" not in text
    assert ".sig" not in text


def test_phase8m_shell_runner_static_safety() -> None:
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
        "build_phase8l_detached_signature",
    ):
        assert forbidden not in text, f"shell runner must not invoke: {forbidden}"


def test_phase8m_shell_runner_executable_mode() -> None:
    mode = SHELL_RUNNER.stat().st_mode & 0o777
    assert oct(mode) == "0o755", f"expected 0o755, got {oct(mode)}"


def test_phase8m_shell_runner_bash_syntax_ok() -> None:
    result = subprocess.run(["bash", "-n", str(SHELL_RUNNER)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_phase8m_runtime_script_py_compile_ok() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(RUNTIME_SCRIPT)], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr


# ── D. Missing input behavior ────────────────────────────────────────────────

def test_phase8m_missing_input_behavior() -> None:
    input_dir = _unique_input_dir("d-missing-inputs")
    output_dir = _unique_output_dir("d-missing-inputs")
    try:
        absent_descriptor = input_dir / "absent-descriptor.json"
        absent_envelope = input_dir / "absent-envelope.json"
        result = _run(
            [
                "--descriptor-path", _rel(absent_descriptor),
                "--envelope-path", _rel(absent_envelope),
                "--output-dir", _rel(output_dir),
            ]
        )
        assert result.returncode == 0, result.stderr

        report_json = output_dir / "detached-signature-verification.json"
        report_md = output_dir / "detached-signature-verification.md"
        assert report_json.is_file()
        assert report_md.is_file()

        report = json.loads(report_json.read_text(encoding="utf-8"))
        assert report["signature_verification_status"] == "skipped_missing_signature_inputs"
        assert report["verification_status"] == "empty"
        assert report["signature_status"] == "not_present"

        assert "verified signature is not approval" in report_md.read_text(encoding="utf-8").lower()
    finally:
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)


# ── E. Missing prototype key ─────────────────────────────────────────────────

def test_phase8m_missing_prototype_key_behavior() -> None:
    input_dir, phase8l_dir, descriptor_path, envelope_path = _produce_pair(
        "e-missing-key", TEST_KEY_VALUE_A
    )
    output_dir = _unique_output_dir("e-missing-key")
    try:
        result = _run(
            [
                "--descriptor-path", _rel(descriptor_path),
                "--envelope-path", _rel(envelope_path),
                "--output-dir", _rel(output_dir),
            ],
            env=_clean_env(),
        )
        assert result.returncode == 0, result.stderr

        report_json = output_dir / "detached-signature-verification.json"
        report_md = output_dir / "detached-signature-verification.md"
        report = json.loads(report_json.read_text(encoding="utf-8"))
        assert report["signature_verification_status"] == "skipped_missing_prototype_key"
        assert report["verification_status"] == "warning"
        assert report["signature_status"] == "present"
        assert report["reviewer_action"] == "manual_review_required"

        for p in (report_json, report_md):
            assert TEST_KEY_VALUE_A not in p.read_text(encoding="utf-8")

        assert "verified signature is not approval" in report_md.read_text(encoding="utf-8").lower()
    finally:
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(phase8l_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)


# ── F. Signature not ready ───────────────────────────────────────────────────

def test_phase8m_signature_not_ready_behavior() -> None:
    input_dir, phase8l_dir, descriptor_path, envelope_path = _produce_pair(
        "f-not-ready", None
    )
    output_dir = _unique_output_dir("f-not-ready")
    try:
        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
        assert envelope["signature_status"] == "not_ready"
        assert envelope["signing_status"] == "skipped_missing_prototype_key"

        result = _run(
            [
                "--descriptor-path", _rel(descriptor_path),
                "--envelope-path", _rel(envelope_path),
                "--output-dir", _rel(output_dir),
            ],
            env=_clean_env(),
        )
        assert result.returncode == 0, result.stderr

        report = json.loads(
            (output_dir / "detached-signature-verification.json").read_text(encoding="utf-8")
        )
        assert report["signature_verification_status"] == "skipped_signature_not_ready"
        assert report["verification_status"] == "warning"
        assert report["signature_status"] == "not_ready"
        assert report["reviewer_action"] == "manual_review_required"
    finally:
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(phase8l_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)


# ── G. Successful verification ───────────────────────────────────────────────

def test_phase8m_successful_verification_behavior() -> None:
    input_dir, phase8l_dir, descriptor_path, envelope_path = _produce_pair(
        "g-verified", TEST_KEY_VALUE_A
    )
    output_dir = _unique_output_dir("g-verified")
    try:
        descriptor_bytes_before = descriptor_path.read_bytes()
        envelope_bytes_before = envelope_path.read_bytes()

        env = os.environ.copy()
        env.pop(PROTOTYPE_KEY_ENV, None)
        env[PROTOTYPE_KEY_ENV] = TEST_KEY_VALUE_A

        result = _run(
            [
                "--descriptor-path", _rel(descriptor_path),
                "--envelope-path", _rel(envelope_path),
                "--output-dir", _rel(output_dir),
            ],
            env=env,
        )
        assert result.returncode == 0, result.stderr

        report_json = output_dir / "detached-signature-verification.json"
        report_md = output_dir / "detached-signature-verification.md"
        report = json.loads(report_json.read_text(encoding="utf-8"))

        assert report["signature_verification_status"] == "verified_local_prototype"
        assert report["verification_status"] == "valid"
        assert report["signature_status"] == "verification_passed"
        assert report["signed_payload_hash_status"] == "match"

        descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
        recomputed_descriptor_hash = _sha256_bytes(_canonical_json(descriptor).encode("utf-8"))
        assert report["computed_signed_payload_sha256"] == recomputed_descriptor_hash

        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
        expected_hmac = hmac.new(
            TEST_KEY_VALUE_A.encode("utf-8"),
            envelope["signed_payload_sha256"].encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        assert expected_hmac == envelope["detached_signature_value"]

        # Raw key must never leak into any 8M output file.
        for p in (report_json, report_md):
            assert TEST_KEY_VALUE_A not in p.read_text(encoding="utf-8"), f"raw key leaked into {p}"

        # Every file 8M wrote lives directly under the chosen output-dir.
        written = list(output_dir.iterdir())
        assert written, "8M wrote no files"
        for p in written:
            assert p.parent.resolve() == output_dir.resolve()
            assert OUTPUT_ROOT in p.resolve().parents

        # 8M must not mutate the Phase 8L outputs it reads.
        assert descriptor_path.read_bytes() == descriptor_bytes_before
        assert envelope_path.read_bytes() == envelope_bytes_before

        md_low = report_md.read_text(encoding="utf-8").lower()
        assert "verified signature is not approval" in md_low
        assert "verification passed is not approval" in md_low
    finally:
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(phase8l_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)


# ── H. Signature mismatch ────────────────────────────────────────────────────

def test_phase8m_signature_mismatch_behavior() -> None:
    input_dir, phase8l_dir, descriptor_path, envelope_path = _produce_pair(
        "h-mismatch", TEST_KEY_VALUE_A
    )
    output_dir = _unique_output_dir("h-mismatch")
    try:
        env = os.environ.copy()
        env.pop(PROTOTYPE_KEY_ENV, None)
        env[PROTOTYPE_KEY_ENV] = TEST_KEY_VALUE_B

        result = _run(
            [
                "--descriptor-path", _rel(descriptor_path),
                "--envelope-path", _rel(envelope_path),
                "--output-dir", _rel(output_dir),
            ],
            env=env,
        )
        assert result.returncode != 0

        report_json = output_dir / "detached-signature-verification.json"
        report_md = output_dir / "detached-signature-verification.md"
        report = json.loads(report_json.read_text(encoding="utf-8"))
        assert report["signature_verification_status"] == "failed_signature_mismatch"
        assert report["verification_status"] == "invalid"
        assert report["signature_status"] == "verification_failed"
        assert report["incident_classification"] == "signature_integrity_failure"
        assert report["reviewer_action"] == "reject_signature_until_resolved"

        for p in (report_json, report_md):
            text = p.read_text(encoding="utf-8")
            assert TEST_KEY_VALUE_A not in text
            assert TEST_KEY_VALUE_B not in text
    finally:
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(phase8l_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)


# ── I. Signed payload hash mismatch ──────────────────────────────────────────

def test_phase8m_signed_payload_hash_mismatch_behavior() -> None:
    input_dir, phase8l_dir, descriptor_path, envelope_path = _produce_pair(
        "i-hash-mismatch", TEST_KEY_VALUE_A
    )
    tamper_dir = _unique_input_dir("i-hash-mismatch-tamper")
    output_dir = _unique_output_dir("i-hash-mismatch")
    try:
        descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
        descriptor["signer_role"] = "tampered-role"
        tampered_descriptor_path = tamper_dir / "signed-payload-descriptor.json"
        tampered_descriptor_path.write_text(
            json.dumps(descriptor, indent=2, sort_keys=True), encoding="utf-8"
        )

        env = os.environ.copy()
        env.pop(PROTOTYPE_KEY_ENV, None)
        env[PROTOTYPE_KEY_ENV] = TEST_KEY_VALUE_A

        result = _run(
            [
                "--descriptor-path", _rel(tampered_descriptor_path),
                "--envelope-path", _rel(envelope_path),
                "--output-dir", _rel(output_dir),
            ],
            env=env,
        )
        assert result.returncode != 0

        report = json.loads(
            (output_dir / "detached-signature-verification.json").read_text(encoding="utf-8")
        )
        assert report["signed_payload_hash_status"] == "mismatch"
        assert report["signature_verification_status"] == "failed_signed_payload_hash_mismatch"
        assert report["verification_status"] == "invalid"
        assert report["signature_status"] == "verification_failed"
        assert report["incident_classification"] == "signature_integrity_failure"
        assert report["reviewer_action"] == "reject_signature_until_resolved"
    finally:
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(phase8l_dir, ignore_errors=True)
        shutil.rmtree(tamper_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)


# ── J. Descriptor/envelope schema ────────────────────────────────────────────

def test_phase8m_schema_missing_descriptor_field() -> None:
    input_dir, phase8l_dir, descriptor_path, envelope_path = _produce_pair(
        "j-missing-descriptor-field", TEST_KEY_VALUE_A
    )
    tamper_dir = _unique_input_dir("j-missing-descriptor-field-tamper")
    output_dir = _unique_output_dir("j-missing-descriptor-field")
    try:
        descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
        del descriptor["signer_role"]
        tampered_path = tamper_dir / "signed-payload-descriptor.json"
        tampered_path.write_text(json.dumps(descriptor, indent=2, sort_keys=True), encoding="utf-8")

        result = _run(
            [
                "--descriptor-path", _rel(tampered_path),
                "--envelope-path", _rel(envelope_path),
                "--output-dir", _rel(output_dir),
            ]
        )
        assert result.returncode != 0

        report = json.loads(
            (output_dir / "detached-signature-verification.json").read_text(encoding="utf-8")
        )
        issue_types = {issue["issue_type"] for issue in report["issues"]}
        assert "missing_descriptor_field" in issue_types
        assert report["signature_verification_status"] == "failed_schema_validation"
        assert report["verification_status"] == "invalid"
    finally:
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(phase8l_dir, ignore_errors=True)
        shutil.rmtree(tamper_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)


def test_phase8m_schema_missing_envelope_field() -> None:
    input_dir, phase8l_dir, descriptor_path, envelope_path = _produce_pair(
        "j-missing-envelope-field", TEST_KEY_VALUE_A
    )
    tamper_dir = _unique_input_dir("j-missing-envelope-field-tamper")
    output_dir = _unique_output_dir("j-missing-envelope-field")
    try:
        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
        del envelope["signer_role"]
        tampered_path = tamper_dir / "detached-signature-envelope.json"
        tampered_path.write_text(json.dumps(envelope, indent=2, sort_keys=True), encoding="utf-8")

        result = _run(
            [
                "--descriptor-path", _rel(descriptor_path),
                "--envelope-path", _rel(tampered_path),
                "--output-dir", _rel(output_dir),
            ]
        )
        assert result.returncode != 0

        report = json.loads(
            (output_dir / "detached-signature-verification.json").read_text(encoding="utf-8")
        )
        issue_types = {issue["issue_type"] for issue in report["issues"]}
        assert "missing_envelope_field" in issue_types
        assert report["signature_verification_status"] == "failed_schema_validation"
        assert report["verification_status"] == "invalid"
    finally:
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(phase8l_dir, ignore_errors=True)
        shutil.rmtree(tamper_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)


def test_phase8m_schema_invalid_json_descriptor() -> None:
    input_dir = _unique_input_dir("j-invalid-json")
    output_dir = _unique_output_dir("j-invalid-json")
    try:
        bad_descriptor = input_dir / "bad-descriptor.json"
        bad_descriptor.write_text("not json {{{", encoding="utf-8")
        envelope_placeholder = input_dir / "envelope-placeholder.json"
        envelope_placeholder.write_text(json.dumps({"a": 1}), encoding="utf-8")

        result = _run(
            [
                "--descriptor-path", _rel(bad_descriptor),
                "--envelope-path", _rel(envelope_placeholder),
                "--output-dir", _rel(output_dir),
            ]
        )
        assert result.returncode != 0
    finally:
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)


def test_phase8m_schema_json_array_descriptor() -> None:
    input_dir = _unique_input_dir("j-json-array")
    output_dir = _unique_output_dir("j-json-array")
    try:
        arr_descriptor = input_dir / "array-descriptor.json"
        arr_descriptor.write_text("[1,2,3]", encoding="utf-8")
        envelope_placeholder = input_dir / "envelope-placeholder.json"
        envelope_placeholder.write_text(json.dumps({"a": 1}), encoding="utf-8")

        result = _run(
            [
                "--descriptor-path", _rel(arr_descriptor),
                "--envelope-path", _rel(envelope_placeholder),
                "--output-dir", _rel(output_dir),
            ]
        )
        assert result.returncode != 0
    finally:
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)


def test_phase8m_schema_unsupported_algorithm() -> None:
    input_dir, phase8l_dir, descriptor_path, envelope_path = _produce_pair(
        "j-bad-algorithm", TEST_KEY_VALUE_A
    )
    tamper_dir = _unique_input_dir("j-bad-algorithm-tamper")
    output_dir = _unique_output_dir("j-bad-algorithm")
    try:
        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
        envelope["signature_algorithm"] = "rsa-sha256-not-supported"
        tampered_path = tamper_dir / "detached-signature-envelope.json"
        tampered_path.write_text(json.dumps(envelope, indent=2, sort_keys=True), encoding="utf-8")

        env = os.environ.copy()
        env.pop(PROTOTYPE_KEY_ENV, None)
        env[PROTOTYPE_KEY_ENV] = TEST_KEY_VALUE_A

        result = _run(
            [
                "--descriptor-path", _rel(descriptor_path),
                "--envelope-path", _rel(tampered_path),
                "--output-dir", _rel(output_dir),
            ],
            env=env,
        )
        assert result.returncode != 0
        report = json.loads(
            (output_dir / "detached-signature-verification.json").read_text(encoding="utf-8")
        )
        assert report["verification_status"] == "invalid"
        assert report["signature_verification_status"] == "failed_unsupported_algorithm"
    finally:
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(phase8l_dir, ignore_errors=True)
        shutil.rmtree(tamper_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)


def test_phase8m_schema_unsupported_encoding() -> None:
    input_dir, phase8l_dir, descriptor_path, envelope_path = _produce_pair(
        "j-bad-encoding", TEST_KEY_VALUE_A
    )
    tamper_dir = _unique_input_dir("j-bad-encoding-tamper")
    output_dir = _unique_output_dir("j-bad-encoding")
    try:
        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
        envelope["signature_encoding"] = "base64-not-supported"
        tampered_path = tamper_dir / "detached-signature-envelope.json"
        tampered_path.write_text(json.dumps(envelope, indent=2, sort_keys=True), encoding="utf-8")

        env = os.environ.copy()
        env.pop(PROTOTYPE_KEY_ENV, None)
        env[PROTOTYPE_KEY_ENV] = TEST_KEY_VALUE_A

        result = _run(
            [
                "--descriptor-path", _rel(descriptor_path),
                "--envelope-path", _rel(tampered_path),
                "--output-dir", _rel(output_dir),
            ],
            env=env,
        )
        assert result.returncode != 0
        report = json.loads(
            (output_dir / "detached-signature-verification.json").read_text(encoding="utf-8")
        )
        assert report["verification_status"] == "invalid"
        assert report["signature_verification_status"] == "failed_unsupported_encoding"
    finally:
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(phase8l_dir, ignore_errors=True)
        shutil.rmtree(tamper_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)


# ── K. Report schema ──────────────────────────────────────────────────────────

def test_phase8m_report_schema_fields() -> None:
    input_dir, phase8l_dir, descriptor_path, envelope_path = _produce_pair(
        "k-report-schema", TEST_KEY_VALUE_A
    )
    output_dir = _unique_output_dir("k-report-schema")
    try:
        env = os.environ.copy()
        env.pop(PROTOTYPE_KEY_ENV, None)
        env[PROTOTYPE_KEY_ENV] = TEST_KEY_VALUE_A
        result = _run(
            [
                "--descriptor-path", _rel(descriptor_path),
                "--envelope-path", _rel(envelope_path),
                "--output-dir", _rel(output_dir),
            ],
            env=env,
        )
        assert result.returncode == 0, result.stderr

        report_json = output_dir / "detached-signature-verification.json"
        report = json.loads(report_json.read_text(encoding="utf-8"))

        for field in REPORT_REQUIRED_FIELDS:
            assert field in report, f"missing report field: {field}"

        assert report["phase8m_status"] == "success"
        assert report["durable_audit_store_status"] == "detached_signature_verifier_prototype"
        assert report["phase7d_runtime_readiness"] == "implemented_manual_gate"
        assert report["signing_implementation_status"] == "prototype_local_only"
        assert report["signature_runtime_status"] == "local_prototype"
        assert report["signature_verifier_runtime_status"] == "local_prototype"
        assert report["key_management_runtime_status"] == "not_implemented"
        assert report["major_phase_branch_workflow"] == "enabled"

        report_text = report_json.read_text(encoding="utf-8")
        assert TEST_KEY_VALUE_A not in report_text

        for field_name, value in report.items():
            if "approve" in field_name.lower():
                assert value is not True, f"unexpected truthy approval flag field: {field_name}"
    finally:
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(phase8l_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)


# ── L. Path safety ────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def valid_pair():
    input_dir, phase8l_dir, descriptor_path, envelope_path = _produce_pair(
        "l-path-safety-fixture", TEST_KEY_VALUE_A
    )
    yield descriptor_path, envelope_path
    shutil.rmtree(input_dir, ignore_errors=True)
    shutil.rmtree(phase8l_dir, ignore_errors=True)


@pytest.mark.parametrize(
    "descriptor_path_arg",
    [
        "docs/PHASE8M_DETACHED_SIGNATURE_VERIFIER_PROTOTYPE.md",
        "tests/test_phase8m_detached_signature_verifier_prototype.py",
        "codex/tasks/064-phase8m-detached-signature-verifier-prototype.md",
        "vault/x.json",
    ],
)
def test_phase8m_reject_descriptor_path_under_rejected_roots(descriptor_path_arg, valid_pair) -> None:
    _, envelope_path = valid_pair
    output_dir = _unique_output_dir("l-rejected-root")
    try:
        result = _run(
            [
                "--descriptor-path", descriptor_path_arg,
                "--envelope-path", _rel(envelope_path),
                "--output-dir", _rel(output_dir),
            ]
        )
        assert result.returncode != 0
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_phase8m_reject_envelope_path_under_rejected_root_scripts(valid_pair) -> None:
    descriptor_path, _ = valid_pair
    output_dir = _unique_output_dir("l-rejected-root-envelope")
    try:
        result = _run(
            [
                "--descriptor-path", _rel(descriptor_path),
                "--envelope-path", "scripts/dev/verify_phase8m_detached_signature.py",
                "--output-dir", _rel(output_dir),
            ]
        )
        assert result.returncode != 0
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_phase8m_reject_descriptor_path_traversal(valid_pair) -> None:
    _, envelope_path = valid_pair
    output_dir = _unique_output_dir("l-traversal")
    try:
        result = _run(
            [
                "--descriptor-path", "tmp/phase8m-test-input/../../etc/passwd",
                "--envelope-path", _rel(envelope_path),
                "--output-dir", _rel(output_dir),
            ]
        )
        assert result.returncode != 0
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_phase8m_reject_symlinked_descriptor(valid_pair) -> None:
    descriptor_path, envelope_path = valid_pair
    input_dir = _unique_input_dir("l-symlink-descriptor")
    output_dir = _unique_output_dir("l-symlink-descriptor")
    try:
        link = input_dir / "descriptor-link.json"
        try:
            link.symlink_to(descriptor_path)
        except OSError:
            pytest.skip("symlinks not supported in this environment")
        # Pass the unresolved relative path so the symlink itself is what
        # the runtime validates (calling _rel() here would resolve through it).
        link_rel = link.relative_to(REPO_ROOT).as_posix()
        result = _run(
            [
                "--descriptor-path", link_rel,
                "--envelope-path", _rel(envelope_path),
                "--output-dir", _rel(output_dir),
            ]
        )
        assert result.returncode != 0
    finally:
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)


def test_phase8m_reject_symlinked_envelope(valid_pair) -> None:
    descriptor_path, envelope_path = valid_pair
    input_dir = _unique_input_dir("l-symlink-envelope")
    output_dir = _unique_output_dir("l-symlink-envelope")
    try:
        link = input_dir / "envelope-link.json"
        try:
            link.symlink_to(envelope_path)
        except OSError:
            pytest.skip("symlinks not supported in this environment")
        link_rel = link.relative_to(REPO_ROOT).as_posix()
        result = _run(
            [
                "--descriptor-path", _rel(descriptor_path),
                "--envelope-path", link_rel,
                "--output-dir", _rel(output_dir),
            ]
        )
        assert result.returncode != 0
    finally:
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)


def test_phase8m_reject_output_dir_outside_guarded_root(valid_pair) -> None:
    descriptor_path, envelope_path = valid_pair
    outside = REPO_ROOT / "tmp/other-dir"
    try:
        result = _run(
            [
                "--descriptor-path", _rel(descriptor_path),
                "--envelope-path", _rel(envelope_path),
                "--output-dir", "tmp/other-dir",
            ]
        )
        assert result.returncode != 0
    finally:
        shutil.rmtree(outside, ignore_errors=True)


# ── M. Documentation regression ──────────────────────────────────────────────

def test_phase8m_roadmap_references() -> None:
    text = _text(ROADMAP)
    assert "Phase 8M" in text
    assert "PHASE8M_DETACHED_SIGNATURE_VERIFIER_PROTOTYPE.md" in text
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in text, f"ROADMAP dropped token: {token}"


def test_phase8m_project_state_references() -> None:
    text = _text(PROJECT_STATE)
    assert "docs/PHASE8M_DETACHED_SIGNATURE_VERIFIER_PROTOTYPE.md" in text
    for token in (
        "Current architecture",
        "no database",
        "no FastAPI",
        "no UI",
        "no external APIs",
        "no autopublish",
    ):
        assert token in text, f"PROJECT_STATE dropped token: {token}"


def test_phase8m_major_phase_branch_workflow_reference() -> None:
    roadmap = _text(ROADMAP)
    project_state = _text(PROJECT_STATE)
    assert "major_phase_branch_workflow" in roadmap or "major phase branch workflow" in roadmap.lower()
    assert "major_phase_branch_workflow" in project_state or "major phase branch workflow" in project_state.lower()


def test_phase8m_phase8l_doc_references() -> None:
    assert "Phase 8M" in _text(PHASE8L_DOC)


def test_phase8m_phase8k_doc_references() -> None:
    assert "Phase 8M" in _text(PHASE8K_DOC)


def test_phase8m_phase8j_doc_references() -> None:
    assert "Phase 8M" in _text(PHASE8J_DOC)


# ── N. Protected runtime files unchanged ─────────────────────────────────────

def test_phase8m_protected_runtime_files_unchanged() -> None:
    for path, expected_hash in PROTECTED_HASHES.items():
        assert path.is_file(), f"missing protected file: {path}"
        assert _sha256(path) == expected_hash, f"protected runtime changed: {path}"


# ── O. Static safety for new Phase 8M files only ─────────────────────────────

def test_new_phase8m_files_static_safety() -> None:
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
    for path in NEW_PHASE8M_FILES:
        text = _text(path)
        for token in banned:
            assert token not in text, f"{path.name} contains forbidden token: {token}"


# ── P. Approval boundary ─────────────────────────────────────────────────────

def test_phase8m_doc_approval_boundary_tokens() -> None:
    low = _text(DOC).lower()
    for token in (
        "verified signature is not approval",
        "verification passed is not approval",
        "signature verifier result is not approval",
        "valid verification_status is not approval",
        "signer metadata is not approval",
        "key metadata is not approval",
        "does not call wrapper",
        "does not trigger next gate",
        "does not set approval flags",
        "phase 7d selected-gate manual boundary",
    ):
        assert token in low, f"missing approval boundary token: {token}"


def test_phase8m_runtime_verification_md_approval_boundary() -> None:
    input_dir, phase8l_dir, descriptor_path, envelope_path = _produce_pair(
        "p-approval-md", TEST_KEY_VALUE_A
    )
    output_dir = _unique_output_dir("p-approval-md")
    try:
        env = os.environ.copy()
        env.pop(PROTOTYPE_KEY_ENV, None)
        env[PROTOTYPE_KEY_ENV] = TEST_KEY_VALUE_A
        result = _run(
            [
                "--descriptor-path", _rel(descriptor_path),
                "--envelope-path", _rel(envelope_path),
                "--output-dir", _rel(output_dir),
            ],
            env=env,
        )
        assert result.returncode == 0, result.stderr
        md_low = (output_dir / "detached-signature-verification.md").read_text(encoding="utf-8").lower()
        assert "verified signature is not approval" in md_low
        assert "verification passed is not approval" in md_low
    finally:
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(phase8l_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)


# ── Q. Repo-wide artifact safety ─────────────────────────────────────────────

EXCLUDED_PARTS = {".git", ".venv", "tmp", "vault", "node_modules"}


def test_phase8m_no_key_cert_files_repo_wide() -> None:
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        assert path.suffix.lower() not in (".pem", ".key", ".crt", ".p12", ".pfx"), f"unexpected key/cert file: {path}"


def test_phase8m_no_package_json_at_repo_root() -> None:
    assert not (REPO_ROOT / "package.json").exists()


def test_phase8m_no_database_files_repo_wide() -> None:
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        assert path.suffix.lower() not in (".sql", ".sqlite", ".db"), f"unexpected database file: {path}"
