from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
WRAPPER = REPO_ROOT / "scripts/dev/run_phase6c_approval_review_verifier.sh"
VERIFIER = REPO_ROOT / "scripts/dev/verify_approval_review_packet.py"
TASK_FILE = REPO_ROOT / "codex/tasks/036-phase6c-approval-review-packet-verifier.md"
BOUNDARY = REPO_ROOT / "docs/MANUAL_APPROVED_WORKFLOW_BOUNDARY.md"
GITIGNORE = REPO_ROOT / ".gitignore"

PHASE5D_WRAPPER = REPO_ROOT / "scripts/dev/run_phase5d_ui_shell_demo.sh"
PHASE6B_WRAPPER = REPO_ROOT / "scripts/dev/run_phase6b_approval_review_packet.sh"

PRODUCT_ID = "prod-laptop-stand"
WEEK = "2026-W26"
PACKET_JSON = REPO_ROOT / f"tmp/phase6b-approval-review/review-{PRODUCT_ID}-{WEEK}.json"
PACKET_MD = REPO_ROOT / f"tmp/phase6b-approval-review/review-{PRODUCT_ID}-{WEEK}.md"
OUT_JSON = REPO_ROOT / f"tmp/phase6c-approval-review-verifier/verification-review-{PRODUCT_ID}-{WEEK}.json"
OUT_MD = REPO_ROOT / f"tmp/phase6c-approval-review-verifier/verification-review-{PRODUCT_ID}-{WEEK}.md"
PHASE2F_SOURCE = REPO_ROOT / f"tmp/phase2f-hermes/operational-summary-{WEEK}.md"

VAULT_PRODUCTS_DIR = REPO_ROOT / "vault/products"
VAULT_DECISIONS_DIR = REPO_ROOT / "vault/decisions"

GUARDRAIL_FLAGS = ["ENABLE_AUTOPUBLISH", "ENABLE_OPENAI_API_DIRECT", "APPROVE_PROMOTE", "APPROVE_DECISION", "APPROVE_FINALIZE"]

LEAK_TOKENS = (
    "/home/ubuntu/Affiliate-Ai",
    "vault/",
    "input_path",
    "note_refs",
    "next_allowed_action",
    "APPROVE_PROMOTE=true",
    "APPROVE_DECISION=true",
    "APPROVE_FINALIZE=true",
    "http://",
    "https://",
    "tag=",
    "affiliate=",
)


def _base_env(**overrides: str) -> dict[str, str]:
    env = os.environ.copy()
    env.pop("AFFILIATE_REQUIRE_OPERATOR_RUNTIME", None)
    env.update(overrides)
    return env


def _run(*args: str, env: dict[str, str] | None = None, cwd: Path | None = None):
    return subprocess.run(
        ["bash", str(WRAPPER), *args], cwd=cwd or REPO_ROOT, capture_output=True, text=True, env=env or _base_env()
    )


def _build_packet() -> None:
    for wrapper, args in ((PHASE5D_WRAPPER, [WEEK]), (PHASE6B_WRAPPER, [PRODUCT_ID, WEEK])):
        res = subprocess.run(["bash", str(wrapper), *args], cwd=REPO_ROOT, capture_output=True, text=True, env=_base_env())
        assert res.returncode == 0, res.stderr


def _vault_lists() -> tuple[list[str], list[str]]:
    p = sorted(x.name for x in VAULT_PRODUCTS_DIR.iterdir()) if VAULT_PRODUCTS_DIR.is_dir() else []
    d = sorted(x.name for x in VAULT_DECISIONS_DIR.iterdir()) if VAULT_DECISIONS_DIR.is_dir() else []
    return p, d


# ── 1-5. existence / syntax / gitignore ───────────────────────────────────────

def test_artifacts_exist() -> None:
    assert TASK_FILE.is_file()
    assert BOUNDARY.is_file()
    assert VERIFIER.is_file()
    assert WRAPPER.is_file()


def test_wrapper_executable() -> None:
    assert os.access(WRAPPER, os.X_OK)


def test_wrapper_syntax_ok() -> None:
    res = subprocess.run(["bash", "-n", str(WRAPPER)], capture_output=True, text=True)
    assert res.returncode == 0, res.stderr


def test_verifier_compiles() -> None:
    res = subprocess.run(["python", "-m", "py_compile", str(VERIFIER)], capture_output=True, text=True)
    assert res.returncode == 0, res.stderr


def test_gitignore_includes_phase6c() -> None:
    assert "tmp/phase6c-approval-review-verifier/" in GITIGNORE.read_text(encoding="utf-8")


# ── 6-9. argument + guardrail validation ──────────────────────────────────────

def test_invalid_product_id_fails() -> None:
    assert _run("Bad_ID", WEEK).returncode != 0


def test_invalid_week_fails() -> None:
    assert _run(PRODUCT_ID, "2026W26").returncode != 0


def test_wrong_arg_count_fails() -> None:
    assert _run(PRODUCT_ID).returncode != 0
    assert _run(PRODUCT_ID, WEEK, "extra").returncode != 0


@pytest.mark.parametrize("flag", GUARDRAIL_FLAGS)
def test_guardrail_flags_fail(flag: str) -> None:
    assert _run(PRODUCT_ID, WEEK, env=_base_env(**{flag: "true"})).returncode != 0


# ── 10-11. end-to-end ready + content ─────────────────────────────────────────

def test_end_to_end_ready() -> None:
    _build_packet()
    res = _run(PRODUCT_ID, WEEK)
    assert res.returncode == 0, res.stderr
    for token in ("verification_review_json:", "verification_review_md:", "verdict: ready", "phase6c_status: success"):
        assert token in res.stdout, f"missing line: {token}"
    assert OUT_JSON.is_file()
    assert OUT_MD.is_file()


def test_json_content() -> None:
    _build_packet()
    assert _run(PRODUCT_ID, WEEK).returncode == 0
    d = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert d["type"] == "phase6c_approval_review_verification"
    assert d["product_id"] == PRODUCT_ID
    assert d["report_week"] == WEEK
    assert d["verdict"] == "ready"
    assert d["checks"]
    assert "source_integrity" in d


# ── 12. output self-safety ────────────────────────────────────────────────────

def test_output_safety() -> None:
    _build_packet()
    assert _run(PRODUCT_ID, WEEK).returncode == 0
    blob = OUT_JSON.read_text(encoding="utf-8") + OUT_MD.read_text(encoding="utf-8")
    for token in LEAK_TOKENS:
        assert token not in blob, f"verifier output leaked token: {token}"


# ── 13. failed path (tampered packet) ─────────────────────────────────────────

def test_failed_path_tampered_packet() -> None:
    _build_packet()
    try:
        d = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        d["dry_run"] = False
        PACKET_JSON.write_text(json.dumps(d, indent=2), encoding="utf-8")
        res = _run(PRODUCT_ID, WEEK)
        assert res.returncode != 0
        assert "verdict: failed" in res.stdout
    finally:
        _build_packet()


# ── 14. warning path (changed source) ─────────────────────────────────────────

def test_warning_path_changed_source() -> None:
    _build_packet()
    try:
        with PHASE2F_SOURCE.open("a", encoding="utf-8") as fh:
            fh.write("\n<!-- changed -->\n")
        res = _run(PRODUCT_ID, WEEK)
        assert res.returncode == 0, res.stderr
        assert "verdict: warning" in res.stdout
        assert json.loads(OUT_JSON.read_text(encoding="utf-8"))["verdict"] == "warning"
    finally:
        _build_packet()


# ── 15. missing packet ────────────────────────────────────────────────────────

def test_missing_packet_fails() -> None:
    _build_packet()
    backup = PACKET_JSON.with_suffix(".json.bak")
    try:
        PACKET_JSON.rename(backup)
        res = _run(PRODUCT_ID, WEEK)
        assert res.returncode != 0
        assert "verdict: failed" in res.stdout
    finally:
        if backup.is_file():
            backup.rename(PACKET_JSON)


# ── 16. finalization consistency ──────────────────────────────────────────────

def test_finalization_consistency_fails() -> None:
    _build_packet()
    try:
        d = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        d["gates"]["finalization_gate_ready"] = True
        d["compliance_status"] = "not_evaluated"
        PACKET_JSON.write_text(json.dumps(d, indent=2), encoding="utf-8")
        res = _run(PRODUCT_ID, WEEK)
        assert res.returncode != 0
        assert "verdict: failed" in res.stdout
    finally:
        _build_packet()


# ── 17. sources tmp-only ──────────────────────────────────────────────────────

def test_sources_tmp_only_fails() -> None:
    _build_packet()
    try:
        d = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        d["sources"][0]["path"] = "vault/products/secret.md"
        PACKET_JSON.write_text(json.dumps(d, indent=2), encoding="utf-8")
        res = _run(PRODUCT_ID, WEEK)
        assert res.returncode != 0
        assert "verdict: failed" in res.stdout
    finally:
        _build_packet()


# ── 18. cross-CWD ─────────────────────────────────────────────────────────────

def test_cross_cwd(tmp_path: Path) -> None:
    _build_packet()
    res = subprocess.run(
        ["bash", str(WRAPPER), PRODUCT_ID, WEEK], cwd=tmp_path, capture_output=True, text=True, env=_base_env()
    )
    assert res.returncode == 0, res.stderr
    assert "phase6c_status: success" in res.stdout


# ── 19. CI-C alignment ────────────────────────────────────────────────────────

def test_ci_c_alignment() -> None:
    text = WRAPPER.read_text(encoding="utf-8")
    assert "/home/ubuntu/Affiliate-Ai" not in text
    assert 'SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"' in text
    for pattern in (r"\bcurl\b", r"\bwget\b", r"\bnc\b", r"\bnetcat\b", r"https?://"):
        assert not re.search(pattern, text), f"network token in wrapper: {pattern}"


# ── 20. static boundary ───────────────────────────────────────────────────────

def test_wrapper_no_approved_workflow_refs() -> None:
    text = WRAPPER.read_text(encoding="utf-8")
    for ref in ("run_phase2g", "run_phase2h", "run_phase2i",
                "promote_product_candidates.py", "create_decision.py", "finalize_decision.py"):
        assert ref not in text, f"wrapper references approved workflow: {ref}"


# ── 21. no vault write ────────────────────────────────────────────────────────

def test_no_vault_write() -> None:
    before = _vault_lists()
    _build_packet()
    assert _run(PRODUCT_ID, WEEK).returncode == 0
    assert before == _vault_lists()


# ── 22. no forbidden body ingestion ───────────────────────────────────────────

def test_no_forbidden_body_ingestion() -> None:
    src = VERIFIER.read_text(encoding="utf-8")
    assert "read_bytes" in src  # sources are hashed, not parsed
    assert 'REPO_ROOT / "vault"' not in src
    _build_packet()
    assert _run(PRODUCT_ID, WEEK).returncode == 0
    d = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert d["packet_path"].startswith("tmp/")
