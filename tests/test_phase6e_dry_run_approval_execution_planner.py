from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
WRAPPER = REPO_ROOT / "scripts/dev/run_phase6e_approval_execution_plan.sh"
PLANNER = REPO_ROOT / "scripts/dev/build_approval_execution_plan.py"
TASK_FILE = REPO_ROOT / "codex/tasks/038-phase6e-dry-run-approval-execution-planner.md"
BOUNDARY = REPO_ROOT / "docs/MANUAL_APPROVAL_EXECUTION_BOUNDARY.md"
GITIGNORE = REPO_ROOT / ".gitignore"

PHASE5D = REPO_ROOT / "scripts/dev/run_phase5d_ui_shell_demo.sh"
PHASE6B = REPO_ROOT / "scripts/dev/run_phase6b_approval_review_packet.sh"
PHASE6C = REPO_ROOT / "scripts/dev/run_phase6c_approval_review_verifier.sh"

PRODUCT_ID = "prod-laptop-stand"
WEEK = "2026-W26"
PACKET_JSON = REPO_ROOT / f"tmp/phase6b-approval-review/review-{PRODUCT_ID}-{WEEK}.json"
VERIFIER_JSON = REPO_ROOT / f"tmp/phase6c-approval-review-verifier/verification-review-{PRODUCT_ID}-{WEEK}.json"
OUT_JSON = REPO_ROOT / f"tmp/phase6e-approval-execution-plan/execution-plan-{PRODUCT_ID}-{WEEK}.json"
OUT_MD = REPO_ROOT / f"tmp/phase6e-approval-execution-plan/execution-plan-{PRODUCT_ID}-{WEEK}.md"

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
    "python scripts/dev/promote_product_candidates.py",
    "python scripts/dev/create_decision.py",
    "python scripts/dev/finalize_decision.py",
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


def _build_chain() -> None:
    for wrapper, args in ((PHASE5D, [WEEK]), (PHASE6B, [PRODUCT_ID, WEEK]), (PHASE6C, [PRODUCT_ID, WEEK])):
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
    assert PLANNER.is_file()
    assert WRAPPER.is_file()


def test_wrapper_executable() -> None:
    assert os.access(WRAPPER, os.X_OK)


def test_wrapper_syntax_ok() -> None:
    res = subprocess.run(["bash", "-n", str(WRAPPER)], capture_output=True, text=True)
    assert res.returncode == 0, res.stderr


def test_planner_compiles() -> None:
    res = subprocess.run(["python", "-m", "py_compile", str(PLANNER)], capture_output=True, text=True)
    assert res.returncode == 0, res.stderr


def test_gitignore_includes_phase6e() -> None:
    assert "tmp/phase6e-approval-execution-plan/" in GITIGNORE.read_text(encoding="utf-8")


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


# ── 10-11. end-to-end (normal blocked) + content ──────────────────────────────

def test_end_to_end_blocked() -> None:
    _build_chain()
    res = _run(PRODUCT_ID, WEEK)
    assert res.returncode == 0, res.stderr
    for token in ("execution_plan_json:", "execution_plan_md:", "verdict: blocked", "phase6e_status: success"):
        assert token in res.stdout, f"missing line: {token}"
    assert OUT_JSON.is_file()
    assert OUT_MD.is_file()


def test_json_content() -> None:
    _build_chain()
    assert _run(PRODUCT_ID, WEEK).returncode == 0
    d = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert d["type"] == "phase6e_approval_execution_plan"
    assert d["dry_run"] is True
    assert d["product_id"] == PRODUCT_ID and d["report_week"] == WEEK
    assert "verifier_verdict" in d
    assert "preconditions" in d
    assert d["proposed_gate_sequence"] == ["promote", "decision", "finalization"]
    assert set(d["per_gate_plan"]) == {"promote", "decision", "finalization"}
    assert d["required_future_operator_inputs"]
    for field in ("product_id", "report_week", "gate_name", "primitive_name", "operator",
                  "approval_reason", "timestamp", "source_packet_path", "verifier_path",
                  "precondition_summary", "result_summary"):
        assert field in d["audit_preview"], f"missing audit field: {field}"
    assert any("compliance" in b.lower() for b in d["blockers"])
    for word in ("approve", "promote", "decide", "finalize", "vault"):
        assert word in d["statement"].lower()


# ── 12. output self-safety ────────────────────────────────────────────────────

def test_output_safety() -> None:
    _build_chain()
    assert _run(PRODUCT_ID, WEEK).returncode == 0
    blob = OUT_JSON.read_text(encoding="utf-8") + OUT_MD.read_text(encoding="utf-8")
    for token in LEAK_TOKENS:
        assert token not in blob, f"plan leaked token: {token}"
    assert not any(rx.search(blob) for rx in (re.compile(r"sk-[A-Za-z0-9]{20,}"), re.compile(r"AKIA[A-Z0-9]{16}")))


# ── 13. failed path ───────────────────────────────────────────────────────────

def test_failed_path_verifier_failed() -> None:
    _build_chain()
    try:
        d = json.loads(VERIFIER_JSON.read_text(encoding="utf-8"))
        d["verdict"] = "failed"
        VERIFIER_JSON.write_text(json.dumps(d, indent=2), encoding="utf-8")
        res = _run(PRODUCT_ID, WEEK)
        assert res.returncode != 0
        assert "verdict: failed" in res.stdout
    finally:
        _build_chain()


# ── 14. blocked warning path ──────────────────────────────────────────────────

def test_warning_path_blocked() -> None:
    _build_chain()
    try:
        d = json.loads(VERIFIER_JSON.read_text(encoding="utf-8"))
        d["verdict"] = "warning"
        VERIFIER_JSON.write_text(json.dumps(d, indent=2), encoding="utf-8")
        res = _run(PRODUCT_ID, WEEK)
        assert res.returncode == 0, res.stderr
        assert "verdict: blocked" in res.stdout
    finally:
        _build_chain()


# ── 15. finalization blocked normal rule ──────────────────────────────────────

def test_finalization_blocked() -> None:
    _build_chain()
    assert _run(PRODUCT_ID, WEEK).returncode == 0
    d = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    fin = d["per_gate_plan"]["finalization"]
    assert fin["plan_ready"] is False
    assert "compliance" in (fin["blocked_reason"] or "").lower()


# ── 16. gate order ────────────────────────────────────────────────────────────

def test_gate_order() -> None:
    _build_chain()
    assert _run(PRODUCT_ID, WEEK).returncode == 0
    d = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert d["proposed_gate_sequence"] == ["promote", "decision", "finalization"]


# ── 17. boundary doc hash ─────────────────────────────────────────────────────

def test_boundary_doc_hash_recorded() -> None:
    _build_chain()
    assert _run(PRODUCT_ID, WEEK).returncode == 0
    d = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    bd = d["boundary_doc"]
    assert bd["present"] is True
    assert isinstance(bd["bytes"], int) and bd["bytes"] > 0
    assert isinstance(bd["sha256"], str) and len(bd["sha256"]) == 64
    src = PLANNER.read_text(encoding="utf-8")
    # boundary doc is hashed, never parsed as text
    assert "MANUAL_APPROVAL_EXECUTION_BOUNDARY.md" in src


# ── 18. cross-CWD ─────────────────────────────────────────────────────────────

def test_cross_cwd(tmp_path: Path) -> None:
    _build_chain()
    res = subprocess.run(
        ["bash", str(WRAPPER), PRODUCT_ID, WEEK], cwd=tmp_path, capture_output=True, text=True, env=_base_env()
    )
    assert res.returncode == 0, res.stderr
    assert "phase6e_status: success" in res.stdout


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
    _build_chain()
    assert _run(PRODUCT_ID, WEEK).returncode == 0
    assert before == _vault_lists()


# ── 22. no forbidden body ingestion ───────────────────────────────────────────

def test_no_forbidden_body_ingestion() -> None:
    src = PLANNER.read_text(encoding="utf-8")
    assert "read_bytes" in src  # boundary doc hashed via bytes
    assert 'REPO_ROOT / "vault"' not in src
    _build_chain()
    assert _run(PRODUCT_ID, WEEK).returncode == 0
    d = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert d["packet_path"].startswith("tmp/")
    assert d["verifier_path"].startswith("tmp/")


# ── 23. documentation update ──────────────────────────────────────────────────

def test_boundary_doc_updated() -> None:
    text = BOUNDARY.read_text(encoding="utf-8")
    assert "Phase 6E dry-run execution planner" in text
    assert "run_phase6e_approval_execution_plan.sh" in text
    for banned in ("APPROVE_PROMOTE=true", "APPROVE_DECISION=true", "APPROVE_FINALIZE=true"):
        assert banned not in text, f"boundary doc contains execution example: {banned}"
