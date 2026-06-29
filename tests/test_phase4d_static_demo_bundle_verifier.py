from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
VERIFY_SCRIPT = REPO_ROOT / "scripts/dev/verify_demo_bundle.py"
WRAPPER = REPO_ROOT / "scripts/dev/run_phase4d_demo_verifier.sh"
TASK_FILE = REPO_ROOT / "codex/tasks/023-phase4d-static-demo-bundle-verifier.md"
GITIGNORE = REPO_ROOT / ".gitignore"

OUT_DIR = REPO_ROOT / "tmp/phase4d-demo-verifier"
REPORT = OUT_DIR / "verification-report.md"
SUMMARY = OUT_DIR / "verification-summary.json"

VAULT_PRODUCTS_DIR = REPO_ROOT / "vault/products"
VAULT_DECISIONS_DIR = REPO_ROOT / "vault/decisions"

EXPECTED_OUT_FILES = {"verification-report.md", "verification-summary.json"}

SNAP_INDEX = (
    "<!doctype html>\n<html lang=\"en\">\n<head><meta charset=\"utf-8\">"
    "<title>UI Mock</title><style>body{color:#111}</style></head>\n"
    "<body><h1>Affiliate Product Intelligence OS</h1><div>READ-ONLY MOCK</div></body>\n</html>\n"
)
CAT_INDEX = (
    "<!doctype html>\n<html lang=\"en\">\n<head><meta charset=\"utf-8\">"
    "<title>Snapshot Catalog</title><style>body{color:#111}</style></head>\n"
    "<body><h1>Snapshot Catalog</h1>"
    '<a href="../phase4b-ui-snapshot/index.html">open</a></body>\n</html>\n'
)
GUARDRAILS_TEXT = "# Guardrails\n\n- no autopublish\n- no vault writes\n- read-only only\n"
README_TEXT = "# Doc\n\nread-only static bundle. no backend, no server.\n"
INVENTORY_TEXT = "# Inventory\n\nno vault files included\nvault_included: false\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_valid_bundle(base: Path) -> tuple[Path, Path]:
    snap = base / "phase4b-ui-snapshot"
    cat = base / "phase4c-snapshot-catalog"
    snap.mkdir(parents=True, exist_ok=True)
    cat.mkdir(parents=True, exist_ok=True)

    snap_payloads = {
        "index.html": SNAP_INDEX,
        "README.md": README_TEXT,
        "INVENTORY.md": INVENTORY_TEXT,
        "GUARDRAILS.md": GUARDRAILS_TEXT,
    }
    files_meta = []
    total = 0
    for name, text in snap_payloads.items():
        data = text.encode("utf-8")
        (snap / name).write_text(text, encoding="utf-8")
        files_meta.append({"name": name, "sha256": _sha(data), "bytes": len(data)})
        total += len(data)
    manifest = {
        "type": "phase4b_ui_snapshot",
        "report_week": "2026-W26",
        "generated_at": "2099-01-01T00:00:00Z",
        "files": files_meta,
        "source_summary": {
            "portfolio_artifact": "present",
            "product_dashboards": 1,
            "score_files": 1,
            "vault_included": False,
        },
    }
    (snap / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    index_sha = _sha(SNAP_INDEX.encode("utf-8"))
    catalog = {
        "type": "phase4c_snapshot_catalog",
        "generated_at": "2099-01-01T00:00:00Z",
        "snapshot_count": 1,
        "skipped_count": 0,
        "snapshots": [
            {
                "source_dir": "tmp/phase4b-ui-snapshot",
                "report_week": "2026-W26",
                "generated_at": "2099-01-01T00:00:00Z",
                "file_count": 5,
                "total_bytes": total,
                "index_sha256": index_sha,
                "source_summary": {
                    "portfolio_artifact": "present",
                    "product_dashboards": 1,
                    "score_files": 1,
                    "vault_included": False,
                },
            }
        ],
    }
    (cat / "index.html").write_text(CAT_INDEX, encoding="utf-8")
    (cat / "README.md").write_text(README_TEXT, encoding="utf-8")
    (cat / "GUARDRAILS.md").write_text(GUARDRAILS_TEXT, encoding="utf-8")
    (cat / "catalog.json").write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    return snap, cat


def _clean_out() -> None:
    for name in EXPECTED_OUT_FILES:
        (OUT_DIR / name).unlink(missing_ok=True)


@pytest.fixture(autouse=True)
def _clean():
    _clean_out()
    yield
    _clean_out()


def _run(snap: Path, cat: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VERIFY_SCRIPT), "--snapshot-dir", str(snap), "--catalog-dir", str(cat)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )


def _run_wrapper(env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(WRAPPER)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )


def _summary() -> dict:
    return json.loads(SUMMARY.read_text(encoding="utf-8"))


def _vault_snapshot() -> tuple[list[str], list[str]]:
    products = sorted(p.name for p in VAULT_PRODUCTS_DIR.iterdir()) if VAULT_PRODUCTS_DIR.is_dir() else []
    decisions = sorted(p.name for p in VAULT_DECISIONS_DIR.iterdir()) if VAULT_DECISIONS_DIR.is_dir() else []
    return products, decisions


# ── 1-5. existence + syntax ───────────────────────────────────────────────────

def test_task_file_exists() -> None:
    assert TASK_FILE.is_file()


def test_verify_script_exists() -> None:
    assert VERIFY_SCRIPT.is_file()


def test_wrapper_exists_and_executable() -> None:
    assert WRAPPER.is_file()
    assert os.access(WRAPPER, os.X_OK)


def test_gitignore_includes_phase4d() -> None:
    assert "tmp/phase4d-demo-verifier/" in GITIGNORE.read_text(encoding="utf-8")


def test_wrapper_syntax_ok() -> None:
    result = subprocess.run(["bash", "-n", str(WRAPPER)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


# ── 6-16. happy path ──────────────────────────────────────────────────────────

def test_creates_output(tmp_path) -> None:
    snap, cat = build_valid_bundle(tmp_path)
    result = _run(snap, cat)
    assert result.returncode == 0, result.stderr
    assert OUT_DIR.is_dir()
    assert "phase4d_status: success" in result.stdout


def test_exact_output_files(tmp_path) -> None:
    snap, cat = build_valid_bundle(tmp_path)
    _run(snap, cat)
    assert {p.name for p in OUT_DIR.iterdir() if p.is_file()} == EXPECTED_OUT_FILES


def test_summary_valid_typed_success(tmp_path) -> None:
    snap, cat = build_valid_bundle(tmp_path)
    _run(snap, cat)
    summary = _summary()
    assert summary["type"] == "phase4d_demo_bundle_verification"
    assert summary["status"] == "success"


def test_summary_checked_paths(tmp_path) -> None:
    snap, cat = build_valid_bundle(tmp_path)
    _run(snap, cat)
    summary = _summary()
    assert summary["checked_paths"] == ["tmp/phase4b-ui-snapshot", "tmp/phase4c-snapshot-catalog"]


def test_manifest_hashes_match(tmp_path) -> None:
    snap, cat = build_valid_bundle(tmp_path)
    _run(snap, cat)
    assert _summary()["phase4b"]["manifest_hashes_match"] is True


def test_catalog_references_and_link(tmp_path) -> None:
    snap, cat = build_valid_bundle(tmp_path)
    _run(snap, cat)
    summary = _summary()
    assert summary["phase4c"]["references_phase4b"] is True
    assert summary["phase4c"]["relative_link_resolves"] is True


def test_report_has_table(tmp_path) -> None:
    snap, cat = build_valid_bundle(tmp_path)
    _run(snap, cat)
    text = REPORT.read_text(encoding="utf-8")
    assert "Phase 4D Demo Bundle Verification Report" in text
    assert "Status: success" in text
    assert "| check | result |" in text


# ── 17-23. failure paths ──────────────────────────────────────────────────────

def test_fail_on_hash_mismatch(tmp_path) -> None:
    snap, cat = build_valid_bundle(tmp_path)
    (snap / "index.html").write_text(SNAP_INDEX + "<!-- tampered -->\n", encoding="utf-8")
    result = _run(snap, cat)
    assert result.returncode != 0
    assert _summary()["phase4b"]["manifest_hashes_match"] is False


def test_fail_on_missing_reference(tmp_path) -> None:
    snap, cat = build_valid_bundle(tmp_path)
    catalog = json.loads((cat / "catalog.json").read_text(encoding="utf-8"))
    catalog["snapshots"][0]["source_dir"] = "tmp/other-dir"
    (cat / "catalog.json").write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    result = _run(snap, cat)
    assert result.returncode != 0
    assert _summary()["phase4c"]["references_phase4b"] is False


def test_fail_on_external_url(tmp_path) -> None:
    snap, cat = build_valid_bundle(tmp_path)
    manifest = json.loads((snap / "manifest.json").read_text(encoding="utf-8"))
    manifest["note"] = "https://example.test/path"
    (snap / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    result = _run(snap, cat)
    assert result.returncode != 0
    assert _summary()["safety"]["no_external_urls"] is False


def test_fail_on_vault_path(tmp_path) -> None:
    snap, cat = build_valid_bundle(tmp_path)
    manifest = json.loads((snap / "manifest.json").read_text(encoding="utf-8"))
    manifest["note"] = "see vault/products/secret.md"
    (snap / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    result = _run(snap, cat)
    assert result.returncode != 0
    assert _summary()["safety"]["no_vault_paths"] is False


def test_fail_on_raw_artifact(tmp_path) -> None:
    snap, cat = build_valid_bundle(tmp_path)
    (cat / "portfolio-2026-W26.md").write_text("raw\n", encoding="utf-8")
    result = _run(snap, cat)
    assert result.returncode != 0
    assert _summary()["safety"]["no_raw_artifacts"] is False


def test_fail_on_vault_included_true(tmp_path) -> None:
    snap, cat = build_valid_bundle(tmp_path)
    manifest = json.loads((snap / "manifest.json").read_text(encoding="utf-8"))
    manifest["source_summary"]["vault_included"] = True
    (snap / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    result = _run(snap, cat)
    assert result.returncode != 0
    assert _summary()["phase4b"]["vault_included"] is True


def test_fail_on_missing_input(tmp_path) -> None:
    snap, cat = build_valid_bundle(tmp_path)
    (snap / "README.md").unlink()
    result = _run(snap, cat)
    assert result.returncode != 0


# ── 24-25. wrapper guardrails ─────────────────────────────────────────────────

@pytest.mark.parametrize("flag", ["ENABLE_AUTOPUBLISH", "ENABLE_OPENAI_API_DIRECT"])
def test_wrapper_unsafe_flag(flag: str) -> None:
    env = {**os.environ, flag: "true"}
    result = _run_wrapper(env=env)
    assert result.returncode != 0
    assert flag in result.stderr


# ── 26-27. no vault write + idempotent ────────────────────────────────────────

def test_no_vault_write(tmp_path) -> None:
    snap, cat = build_valid_bundle(tmp_path)
    before = _vault_snapshot()
    _run(snap, cat)
    after = _vault_snapshot()
    assert before == after


def test_idempotent(tmp_path) -> None:
    snap, cat = build_valid_bundle(tmp_path)
    assert _run(snap, cat).returncode == 0
    assert _run(snap, cat).returncode == 0
    assert {p.name for p in OUT_DIR.iterdir() if p.is_file()} == EXPECTED_OUT_FILES


# ── 28-29. output content + safety ────────────────────────────────────────────

def test_report_contains_success_and_table(tmp_path) -> None:
    snap, cat = build_valid_bundle(tmp_path)
    _run(snap, cat)
    text = REPORT.read_text(encoding="utf-8")
    assert "Status: success" in text
    assert "No external URLs" in text
    assert "No raw artifact export" in text


def test_output_files_are_safe(tmp_path) -> None:
    snap, cat = build_valid_bundle(tmp_path)
    _run(snap, cat)
    for path in (REPORT, SUMMARY):
        text = path.read_text(encoding="utf-8")
        assert "http://" not in text
        assert "https://" not in text
        for vp in ("vault/products", "vault/decisions", "vault/.obsidian"):
            assert vp not in text
        for marker in ("content_draft", "campaign_copy", "tiktok_script", "hook_text", "blog_post"):
            assert marker not in text
        assert not re.search(r"sk-[A-Za-z0-9]{20,}", text)


# ── 30-33. static safety ──────────────────────────────────────────────────────

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
    verify_text = VERIFY_SCRIPT.read_text(encoding="utf-8")
    wrapper_text = WRAPPER.read_text(encoding="utf-8")
    assert forbidden not in verify_text
    assert forbidden not in wrapper_text


def test_static_no_vault_paths() -> None:
    text = VERIFY_SCRIPT.read_text(encoding="utf-8")
    assert 'REPO_ROOT / "vault"' not in text
    assert "vault/products" not in text
    assert "vault/decisions" not in text


def test_static_no_raw_artifact_reads() -> None:
    text = VERIFY_SCRIPT.read_text(encoding="utf-8")
    for forbidden in ("phase3a-dashboard", "phase3b-portfolio", "phase2e-import"):
        assert forbidden not in text
