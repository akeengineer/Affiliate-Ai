from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
WRAPPER = REPO_ROOT / "scripts/dev/run_phase6b_approval_review_packet.sh"
BUILDER = REPO_ROOT / "scripts/dev/build_approval_review_packet.py"
TASK_FILE = REPO_ROOT / "codex/tasks/035-phase6b-dry-run-approval-review-packet.md"
BOUNDARY = REPO_ROOT / "docs/MANUAL_APPROVED_WORKFLOW_BOUNDARY.md"
GITIGNORE = REPO_ROOT / ".gitignore"

PHASE5D_WRAPPER = REPO_ROOT / "scripts/dev/run_phase5d_ui_shell_demo.sh"

PRODUCT_ID = "prod-laptop-stand"
WEEK = "2026-W26"
OUT_DIR = REPO_ROOT / "tmp/phase6b-approval-review"
JSON_OUT = OUT_DIR / f"review-{PRODUCT_ID}-{WEEK}.json"
MD_OUT = OUT_DIR / f"review-{PRODUCT_ID}-{WEEK}.md"

VAULT_PRODUCTS_DIR = REPO_ROOT / "vault/products"
VAULT_DECISIONS_DIR = REPO_ROOT / "vault/decisions"
PHASE2F_SUMMARY = REPO_ROOT / f"tmp/phase2f-hermes/operational-summary-{WEEK}.md"

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
    "AWS_SECRET_ACCESS_KEY",
    "BEGIN PRIVATE KEY",
    "OPENAI_API_KEY",
)


def _base_env(**overrides: str) -> dict[str, str]:
    env = os.environ.copy()
    env.pop("AFFILIATE_REQUIRE_OPERATOR_RUNTIME", None)
    env.update(overrides)
    return env


def _run(*args: str, env: dict[str, str] | None = None, cwd: Path | None = None):
    return subprocess.run(
        ["bash", str(WRAPPER), *args],
        cwd=cwd or REPO_ROOT,
        capture_output=True,
        text=True,
        env=env or _base_env(),
    )


def _build_chain() -> None:
    res = subprocess.run(
        ["bash", str(PHASE5D_WRAPPER), WEEK], cwd=REPO_ROOT, capture_output=True, text=True, env=_base_env()
    )
    assert res.returncode == 0, res.stderr


def _vault_lists() -> tuple[list[str], list[str]]:
    p = sorted(x.name for x in VAULT_PRODUCTS_DIR.iterdir()) if VAULT_PRODUCTS_DIR.is_dir() else []
    d = sorted(x.name for x in VAULT_DECISIONS_DIR.iterdir()) if VAULT_DECISIONS_DIR.is_dir() else []
    return p, d


# ── 1-5. existence / syntax / gitignore ───────────────────────────────────────

def test_artifacts_exist() -> None:
    assert TASK_FILE.is_file()
    assert BOUNDARY.is_file()
    assert BUILDER.is_file()
    assert WRAPPER.is_file()


def test_wrapper_executable() -> None:
    assert os.access(WRAPPER, os.X_OK)


def test_wrapper_syntax_ok() -> None:
    res = subprocess.run(["bash", "-n", str(WRAPPER)], capture_output=True, text=True)
    assert res.returncode == 0, res.stderr


def test_builder_compiles() -> None:
    res = subprocess.run(["python", "-m", "py_compile", str(BUILDER)], capture_output=True, text=True)
    assert res.returncode == 0, res.stderr


def test_gitignore_includes_phase6b() -> None:
    assert "tmp/phase6b-approval-review/" in GITIGNORE.read_text(encoding="utf-8")


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


# ── 10-11. end-to-end + JSON content ──────────────────────────────────────────

def test_end_to_end() -> None:
    _build_chain()
    res = _run(PRODUCT_ID, WEEK)
    assert res.returncode == 0, res.stderr
    for token in ("review_packet_json:", "review_packet_md:", "phase6b_status: success"):
        assert token in res.stdout, f"missing line: {token}"
    assert JSON_OUT.is_file()
    assert MD_OUT.is_file()


def test_json_content() -> None:
    _build_chain()
    assert _run(PRODUCT_ID, WEEK).returncode == 0
    d = json.loads(JSON_OUT.read_text(encoding="utf-8"))
    assert d["type"] == "phase6b_approval_review"
    assert d["dry_run"] is True
    assert d["product_id"] == PRODUCT_ID
    assert d["report_week"] == WEEK
    assert "score_decision" in d["score"]
    assert "product_opportunity_score" in d["score"]
    assert set(d["gates"]) == {"promote_gate_ready", "decision_gate_ready", "finalization_gate_ready"}
    assert all(isinstance(v, bool) for v in d["gates"].values())
    for s in d["sources"]:
        assert {"name", "path", "present", "bytes", "sha256"} <= set(s)
    for word in ("approve", "promote", "decide", "finalize", "vault"):
        assert word in d["statement"].lower()


# ── 12. leakage guard ─────────────────────────────────────────────────────────

def test_leakage_guard() -> None:
    _build_chain()
    assert _run(PRODUCT_ID, WEEK).returncode == 0
    blob = JSON_OUT.read_text(encoding="utf-8") + MD_OUT.read_text(encoding="utf-8")
    for token in LEAK_TOKENS:
        assert token not in blob, f"packet leaked forbidden token: {token}"
    assert not any(rx.search(blob) for rx in (re.compile(r"sk-[A-Za-z0-9]{20,}"), re.compile(r"AKIA[A-Z0-9]{16}")))


# ── 13-14. no vault write / no vault read ─────────────────────────────────────

def test_no_vault_write() -> None:
    before = _vault_lists()
    _build_chain()
    assert _run(PRODUCT_ID, WEEK).returncode == 0
    assert before == _vault_lists()


def test_no_vault_read() -> None:
    _build_chain()
    assert _run(PRODUCT_ID, WEEK).returncode == 0
    d = json.loads(JSON_OUT.read_text(encoding="utf-8"))
    for s in d["sources"]:
        assert s["path"].startswith("tmp/"), f"non-tmp source path: {s['path']}"
    src = BUILDER.read_text(encoding="utf-8")
    assert 'REPO_ROOT / "vault"' not in src
    assert "read_vault" not in src


# ── 15. gate logic ────────────────────────────────────────────────────────────

def test_gate_logic() -> None:
    _build_chain()
    assert _run(PRODUCT_ID, WEEK).returncode == 0
    d = json.loads(JSON_OUT.read_text(encoding="utf-8"))
    assert d["gates"]["promote_gate_ready"] is True
    if d["compliance_status"] != "approved":
        assert d["gates"]["finalization_gate_ready"] is False


# ── 16. missing source degrades gracefully ────────────────────────────────────

def test_missing_source_degrades() -> None:
    _build_chain()
    backup = PHASE2F_SUMMARY.with_suffix(PHASE2F_SUMMARY.suffix + ".bak")
    moved = False
    try:
        if PHASE2F_SUMMARY.is_file():
            PHASE2F_SUMMARY.rename(backup)
            moved = True
        res = _run(PRODUCT_ID, WEEK)
        assert res.returncode == 0, res.stderr
        d = json.loads(JSON_OUT.read_text(encoding="utf-8"))
        f2 = next(s for s in d["sources"] if s["name"] == "phase2f_summary")
        assert f2["present"] is False
    finally:
        if moved:
            backup.rename(PHASE2F_SUMMARY)


# ── 17. cross-CWD ─────────────────────────────────────────────────────────────

def test_cross_cwd(tmp_path: Path) -> None:
    _build_chain()
    res = subprocess.run(
        ["bash", str(WRAPPER), PRODUCT_ID, WEEK], cwd=tmp_path, capture_output=True, text=True, env=_base_env()
    )
    assert res.returncode == 0, res.stderr
    assert "phase6b_status: success" in res.stdout


# ── 18. CI-C alignment ────────────────────────────────────────────────────────

def test_ci_c_alignment() -> None:
    text = WRAPPER.read_text(encoding="utf-8")
    assert "/home/ubuntu/Affiliate-Ai" not in text
    assert 'SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"' in text
    for pattern in (r"\bcurl\b", r"\bwget\b", r"\bnc\b", r"\bnetcat\b", r"https?://"):
        assert not re.search(pattern, text), f"network token in wrapper: {pattern}"


# ── 19. static boundary ───────────────────────────────────────────────────────

def test_wrapper_no_approved_workflow_refs() -> None:
    text = WRAPPER.read_text(encoding="utf-8")
    for ref in ("run_phase2g", "run_phase2h", "run_phase2i",
                "promote_product_candidates.py", "create_decision.py", "finalize_decision.py"):
        assert ref not in text, f"wrapper references approved workflow: {ref}"


# ── 20. documentation update ──────────────────────────────────────────────────

def test_boundary_doc_updated() -> None:
    text = BOUNDARY.read_text(encoding="utf-8")
    assert "Phase 6B dry-run review packet" in text
    assert "run_phase6b_approval_review_packet.sh" in text
    for banned in ("APPROVE_PROMOTE=true", "APPROVE_DECISION=true", "APPROVE_FINALIZE=true"):
        assert banned not in text, f"boundary doc contains execution example: {banned}"
