from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
WRAPPER = REPO_ROOT / "scripts/dev/run_phase4e_demo_bundle.sh"
TASK_FILE = REPO_ROOT / "codex/tasks/024-phase4e-demo-bundle-command.md"
GITIGNORE = REPO_ROOT / ".gitignore"

OUT_DIR = REPO_ROOT / "tmp/phase4e-demo-bundle"
SUMMARY = OUT_DIR / "demo-bundle-summary.json"
DEMO_MD = OUT_DIR / "DEMO_BUNDLE.md"

VAULT_PRODUCTS_DIR = REPO_ROOT / "vault/products"
VAULT_DECISIONS_DIR = REPO_ROOT / "vault/decisions"

WEEK = "2026-W26"
EXPECTED_FILES = {"demo-bundle-summary.json", "DEMO_BUNDLE.md"}

PRIVATE_VAULT_PATHS = (
    "vault/products",
    "vault/decisions",
    "vault/trends",
    "vault/marketplace-signals",
    "vault/commissions",
    "vault/meetings",
    "vault/contents",
    "vault/compliance",
    "vault/reports",
    "vault/.obsidian",
)
AFFILIATE_URL_PATTERNS = ("aff=", "affiliate=", "tag=", "partner=", "sp_atk=", "bit.ly", "amzn.to", "shopee.link")
CONTENT_MARKERS = ("content_draft", "campaign_copy", "tiktok_script", "hook_text", "blog_post")


def _run(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(WRAPPER), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )


def _vault_snapshot() -> tuple[list[str], list[str]]:
    products = sorted(p.name for p in VAULT_PRODUCTS_DIR.iterdir()) if VAULT_PRODUCTS_DIR.is_dir() else []
    decisions = sorted(p.name for p in VAULT_DECISIONS_DIR.iterdir()) if VAULT_DECISIONS_DIR.is_dir() else []
    return products, decisions


def _out_files() -> set[str]:
    return {p.name for p in OUT_DIR.iterdir() if p.is_file()} if OUT_DIR.is_dir() else set()


# ── 1-4. existence + syntax ───────────────────────────────────────────────────

def test_task_file_exists() -> None:
    assert TASK_FILE.is_file()


def test_wrapper_exists_and_executable() -> None:
    assert WRAPPER.is_file()
    assert os.access(WRAPPER, os.X_OK)


def test_gitignore_includes_phase4e() -> None:
    assert "tmp/phase4e-demo-bundle/" in GITIGNORE.read_text(encoding="utf-8")


def test_wrapper_syntax_ok() -> None:
    result = subprocess.run(["bash", "-n", str(WRAPPER)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


# ── 5-10. validation + guardrails ─────────────────────────────────────────────

def test_invalid_week() -> None:
    result = _run("2026-W2")
    assert result.returncode != 0
    assert "week must match" in result.stderr


def test_wrong_arg_count() -> None:
    assert _run().returncode != 0
    assert _run(WEEK, "extra").returncode != 0


@pytest.mark.parametrize(
    "flag",
    ["ENABLE_AUTOPUBLISH", "ENABLE_OPENAI_API_DIRECT", "APPROVE_PROMOTE", "APPROVE_DECISION", "APPROVE_FINALIZE"],
)
def test_guardrail_flags(flag: str) -> None:
    env = {**os.environ, flag: "true"}
    result = _run(WEEK, env=env)
    assert result.returncode != 0
    assert flag in result.stderr


# ── 11-19. end-to-end happy path ──────────────────────────────────────────────

def test_end_to_end() -> None:
    result = _run(WEEK)
    assert result.returncode == 0, result.stderr
    for line in (
        "demo_step: acceptance -> PASS",
        "demo_step: snapshot -> PASS",
        "demo_step: catalog -> PASS",
        "demo_step: verifier -> PASS",
        "demo_bundle_path: tmp/phase4e-demo-bundle",
        "demo_bundle_file: demo-bundle-summary.json",
        "demo_bundle_file: DEMO_BUNDLE.md",
        "demo_bundle_status: ready",
        "phase4e_status: success",
    ):
        assert line in result.stdout, f"missing stdout line: {line}"


def test_exact_output_files() -> None:
    assert _run(WEEK).returncode == 0
    assert _out_files() == EXPECTED_FILES


def test_summary_valid_and_typed() -> None:
    assert _run(WEEK).returncode == 0
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert summary["type"] == "phase4e_demo_bundle"
    assert summary["status"] == "ready"
    assert summary["report_week"] == WEEK


def test_summary_steps_all_pass() -> None:
    assert _run(WEEK).returncode == 0
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert summary["steps"] == {
        "acceptance": "PASS",
        "snapshot": "PASS",
        "catalog": "PASS",
        "verifier": "PASS",
    }


def test_summary_artifact_references() -> None:
    assert _run(WEEK).returncode == 0
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    artifacts = summary["artifacts"]
    assert artifacts["phase4b_snapshot"] == "tmp/phase4b-ui-snapshot"
    assert artifacts["phase4c_catalog"] == "tmp/phase4c-snapshot-catalog"
    assert artifacts["phase4d_verification"] == "tmp/phase4d-demo-verifier"


def test_demo_md_content() -> None:
    assert _run(WEEK).returncode == 0
    text = DEMO_MD.read_text(encoding="utf-8")
    for token in (
        "Phase 4E Demo Bundle",
        "Status: ready",
        WEEK,
        "run_phase3d_acceptance.sh",
        "## Demo outputs",
        "## Verification",
        "## Guardrails",
        "## Known limitations",
    ):
        assert token in text, f"DEMO_BUNDLE.md missing: {token}"


# ── 20-24. safety + idempotency ───────────────────────────────────────────────

def test_no_vault_write() -> None:
    before = _vault_snapshot()
    assert _run(WEEK).returncode == 0
    after = _vault_snapshot()
    assert before == after


def test_output_files_clean() -> None:
    assert _run(WEEK).returncode == 0
    for path in (SUMMARY, DEMO_MD):
        text = path.read_text(encoding="utf-8")
        assert "http://" not in text
        assert "https://" not in text
        for vp in PRIVATE_VAULT_PATHS:
            assert vp not in text, f"{path.name} leaked vault path {vp}"
        for ap in AFFILIATE_URL_PATTERNS:
            assert ap not in text, f"{path.name} affiliate pattern {ap}"
        for marker in CONTENT_MARKERS:
            assert marker not in text, f"{path.name} content marker {marker}"
        assert not re.search(r"sk-[A-Za-z0-9]{20,}", text)
        assert not re.search(r"AKIA[A-Z0-9]{16}", text)
        assert not re.search(r"Bearer [A-Za-z0-9]{20,}", text)


def test_idempotent() -> None:
    assert _run(WEEK).returncode == 0
    assert _run(WEEK).returncode == 0
    assert _out_files() == EXPECTED_FILES


# ── 25-28. static safety ──────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "forbidden",
    [
        "run_phase2g",
        "run_phase2h",
        "run_phase2i",
        "promote_product_candidates.py",
        "create_decision.py",
        "finalize_decision.py",
    ],
)
def test_static_no_approved_references(forbidden: str) -> None:
    assert forbidden not in WRAPPER.read_text(encoding="utf-8")


def test_static_no_network_tools() -> None:
    text = WRAPPER.read_text(encoding="utf-8")
    assert "http://" not in text
    assert "https://" not in text
    for tool in (r"\bcurl\b", r"\bwget\b", r"\bnc\b"):
        assert not re.search(tool, text), f"wrapper references network tool: {tool}"


def test_static_calls_expected_wrappers() -> None:
    text = WRAPPER.read_text(encoding="utf-8")
    for expected in (
        "run_phase3d_acceptance.sh",
        "run_phase4b_ui_snapshot.sh",
        "run_phase4c_snapshot_catalog.sh",
        "run_phase4d_demo_verifier.sh",
    ):
        assert expected in text, f"wrapper does not call expected: {expected}"
