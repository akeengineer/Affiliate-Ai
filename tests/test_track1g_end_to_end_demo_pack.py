from __future__ import annotations

import importlib.util
import json
import os
import socket
import subprocess
import threading
import urllib.error
import urllib.request
from pathlib import Path
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/102-track1g-end-to-end-demo-pack.md"
DOC = REPO_ROOT / "docs/TRACK1G_END_TO_END_DEMO_PACK.md"
THIS_TEST = Path(__file__)

TRACK1G_RUNNER = REPO_ROOT / "scripts/dev/track1g_end_to_end_demo_pack.py"
TRACK1G_WRAPPER = REPO_ROOT / "scripts/dev/run_track1g_end_to_end_demo_pack.sh"
TRACK1D_STORAGE_MODULE = REPO_ROOT / "scripts/dev/track1d_local_storage.py"
TRACK1C_API_MODULE = REPO_ROOT / "scripts/dev/track1c_local_backend_api.py"
TRACK1C_CONFIG_MODULE = REPO_ROOT / "scripts/dev/track1c_local_backend_config.py"

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
TRACK1F_DOC = REPO_ROOT / "docs/TRACK1F_MINIMAL_USABLE_UI_OPERATOR_FLOW.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(_text(path).lower().replace("`", "").split())


def _assert_all_tokens(text: str, tokens: tuple[str, ...] | list[str], *, label: str) -> None:
    for token in tokens:
        assert token in text, f"missing {label}: {token}"


def _load_module(name: str, path: Path) -> ModuleType:
    assert path.is_file(), f"missing module file: {path}"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader, f"unable to load module spec for {path}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _request_json(url: str) -> tuple[int, dict[str, object]]:
    request = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(request, timeout=5) as response:
        payload = json.loads(response.read().decode("utf-8"))
        return response.status, payload


def _request_html(url: str) -> tuple[int, str, str]:
    request = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(request, timeout=5) as response:
        return response.status, response.headers.get("Content-Type", ""), response.read().decode("utf-8")


def _start_local_backend(storage_path: Path) -> tuple[object, threading.Thread, str]:
    previous_storage_path = os.environ.get("AFFILIATE_STORAGE_PATH")
    os.environ["AFFILIATE_STORAGE_PATH"] = str(storage_path)
    config_module = _load_module("track1c_config_track1g", TRACK1C_CONFIG_MODULE)
    api_module = _load_module("track1c_api_track1g", TRACK1C_API_MODULE)

    port = _find_free_port()
    config = config_module.load_local_backend_config(
        {
            "AFFILIATE_BACKEND_HOST": "127.0.0.1",
            "AFFILIATE_BACKEND_PORT": str(port),
        }
    )
    server = api_module.create_server(config)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    def _restore_env() -> None:
        if previous_storage_path is None:
            os.environ.pop("AFFILIATE_STORAGE_PATH", None)
        else:
            os.environ["AFFILIATE_STORAGE_PATH"] = previous_storage_path

    server._track1g_restore_env = _restore_env  # type: ignore[attr-defined]
    return server, thread, f"http://127.0.0.1:{port}"


def _shutdown_local_backend(server: object, thread: threading.Thread) -> None:
    restore_env = getattr(server, "_track1g_restore_env", None)
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)
    if callable(restore_env):
        restore_env()


def test_track1g_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, THIS_TEST, TRACK1G_RUNNER, TRACK1G_WRAPPER):
        assert path.is_file(), f"missing Track 1G file: {path}"


def test_track1g_required_canonical_wording_exists() -> None:
    for path in (DOC, TASK_FILE):
        text = _text(path)
        _assert_all_tokens(
            text,
            (
                "Track 1G implements the end-to-end demo pack for the first usable local product slice.",
                "Track 1G continues Implementation Track 1 — Backend/API/Database Usable Product Slice.",
                "Track 1G builds on the Track 1C local backend/API skeleton.",
                "Track 1G builds on the Track 1D SQLite local-first storage runtime.",
                "Track 1G builds on the Track 1E Product Core API.",
                "Track 1G builds on the Track 1F minimal usable UI/operator flow.",
                "Track 1G provides a deterministic local demo workflow.",
                "Track 1G does not implement production deployment.",
                "Track 1G does not implement production authentication.",
                "Track 1G does not implement RBAC enforcement.",
                "Track 1G does not implement production signing.",
                "Track 1G does not implement verifier runtime.",
                "Track 1G does not implement key custody runtime.",
                "Track 1G does not approve production promotion.",
                "Track 1G does not approve production deployment.",
                "Track 1G preserves the Phase 7D selected-gate manual boundary.",
                "Selected Runtime Domain: backend/API/database runtime",
                "Implementation Track: Implementation Track 1 — Backend/API/Database Usable Product Slice",
                "Product Goal: first usable local product slice",
                "Runtime Mode: local-only",
                "Storage Runtime: SQLite local-first MVP",
                "Product Core API Status: implemented in Track 1E",
                "Minimal Operator Flow Status: implemented in Track 1F",
                "End-to-End Demo Pack Status: implemented in Track 1G",
                "Production Promotion Status: not approved",
                "Production Deployment Status: not approved",
                "Production Authentication Status: deferred",
                "RBAC Enforcement Status: deferred",
                "Production Signing Status: deferred",
                "Verifier Runtime Status: deferred",
                "Key Custody Runtime Status: deferred",
                "Phase 7D Boundary Status: preserved",
                "Track 1H is the first approved point for MVP Acceptance Pack implementation, if Track 1G is accepted.",
            ),
            label=f"canonical wording in {path}",
        )


def test_track1g_required_sections_and_matrices_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "track 1g purpose",
            "relationship to track 1a",
            "relationship to track 1b",
            "relationship to track 1c",
            "relationship to track 1d",
            "relationship to track 1e",
            "relationship to track 1f",
            "end-to-end demo pack scope",
            "demo workflow contract",
            "demo runner contract",
            "demo output contract",
            "runtime status demo contract",
            "operator surface verification",
            "product demo flow",
            "affiliateoffer demo flow",
            "existing api integration",
            "local-only demo boundary",
            "deferred insight generation scope",
            "deferred recommendation runtime scope",
            "deferred security and hardening scope",
            "production demo deployment exclusion",
            "production promotion exclusion",
            "production deployment exclusion",
            "phase 7d manual boundary preservation",
            "test coverage",
            "local run instructions",
            "implementation guardrails",
            "non-goals and forbidden implementations",
            "acceptance criteria",
            "recommended next step",
            "recommended next major subphase",
        ),
        label="section",
    )
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "| Demo Step | Local Mechanism | Expected Output | Backing Track | Boundary Signal | Track Introduced |",
            "| Output Field | Required Value | Purpose | Deterministic Source | Track Introduced |",
            "| Existing Runtime Area | Track Introduced | Demo Use | Preservation Requirement | Track 1G Change |",
            "| Status Field | Required Value | Purpose | Boundary Signal | Track Introduced |",
            "| Deferred Area | Current Status | Deferred Reason | First Eligible Track | Required Future Approval |",
            "| Reset/init local demo storage |",
            "| Seed deterministic demo source |",
            "| Verify runtime status |",
            "| Verify operator surface availability |",
            "| Create deterministic demo product |",
            "| List products |",
            "| Create deterministic demo affiliate offer |",
            "| List affiliate offers |",
            "| Produce deterministic demo summary |",
            "| insight generation |",
            "| recommendation runtime |",
            "| production demo deployment |",
            "| production frontend deployment |",
            "| production authentication |",
            "| RBAC enforcement |",
            "| production signing |",
            "| verifier runtime |",
            "| key custody runtime |",
            "| production deployment |",
            "| cloud infrastructure |",
            "| CI/CD deployment |",
            "| payment/billing |",
            "| multi-tenant security |",
            "| customer production use |",
        ),
        label="matrix",
    )


def test_track1g_demo_runner_produces_deterministic_summary(tmp_path: Path) -> None:
    runner_module = _load_module("track1g_runner_summary", TRACK1G_RUNNER)
    database_path = tmp_path / "track1g-demo.sqlite3"
    output_path = tmp_path / "summary.json"

    summary = runner_module.run_demo(database_path=str(database_path), output_path=str(output_path))

    assert summary["demo_status"] == "ok"
    assert summary["runtime_mode"] == "local-only"
    assert summary["storage_runtime"] == "SQLite local-first MVP"
    assert summary["product_core_api_status"] == "implemented in Track 1E"
    assert summary["minimal_operator_flow_status"] == "implemented in Track 1F"
    assert summary["demo_product_count"] == 2
    assert summary["demo_affiliate_offer_count"] == 2
    assert summary["operator_surface_status"] == "available"
    assert output_path.is_file()
    assert json.loads(output_path.read_text(encoding="utf-8")) == summary


def test_track1g_demo_runner_wrapper_outputs_json(tmp_path: Path) -> None:
    database_path = tmp_path / "track1g-wrapper.sqlite3"
    output_path = tmp_path / "wrapper-summary.json"

    result = subprocess.run(
        [
            "bash",
            str(TRACK1G_WRAPPER),
            "--database-path",
            str(database_path),
            "--output-path",
            str(output_path),
        ],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout)
    assert payload["demo_status"] == "ok"
    assert payload["demo_product_count"] == 2
    assert payload["demo_affiliate_offer_count"] == 2
    assert output_path.is_file()


def test_track1g_runtime_status_reports_demo_pack_fields(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1g_runtime", TRACK1D_STORAGE_MODULE)
    database_path = tmp_path / "track1g-runtime.sqlite3"
    config = storage_module.load_local_storage_config({"AFFILIATE_STORAGE_PATH": str(database_path)})
    storage_module.ensure_track1e_schema(config)

    server, thread, base_url = _start_local_backend(database_path)
    try:
        status, payload = _request_json(f"{base_url}/runtime/status")
    finally:
        _shutdown_local_backend(server, thread)

    assert status == 200
    assert payload["runtime_mode"] == "local-only"
    assert payload["storage_runtime"] == "SQLite local-first MVP"
    assert payload["product_core_api_status"] == "implemented in Track 1E"
    assert payload["minimal_operator_flow_status"] == "implemented in Track 1F"
    assert payload["end_to_end_demo_pack_status"] == "implemented in Track 1G"
    assert payload["demo_workflow_status"] == "implemented in Track 1G"
    assert payload["production_demo_deployment_status"] == "not approved"
    assert payload["insight_generation_status"] == "not implemented in Track 1G"
    assert payload["recommendation_runtime_status"] == "not implemented in Track 1G"


def test_track1g_health_version_and_operator_still_work(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1g_existing", TRACK1D_STORAGE_MODULE)
    database_path = tmp_path / "track1g-existing.sqlite3"
    config = storage_module.load_local_storage_config({"AFFILIATE_STORAGE_PATH": str(database_path)})
    storage_module.seed_demo_data(config)

    server, thread, base_url = _start_local_backend(database_path)
    try:
        health_status, health_payload = _request_json(f"{base_url}/health")
        version_status, version_payload = _request_json(f"{base_url}/version")
        operator_status, content_type, operator_body = _request_html(f"{base_url}/operator")
    finally:
        _shutdown_local_backend(server, thread)

    assert health_status == 200
    assert health_payload["status"] == "ok"
    assert version_status == 200
    assert version_payload["track"] == "Track 1C"
    assert operator_status == 200
    assert content_type.startswith("text/html")
    assert "Track 1F provides a local-only operator flow" in operator_body


def test_track1g_existing_product_and_affiliate_offer_api_still_work(tmp_path: Path) -> None:
    runner_module = _load_module("track1g_runner_api", TRACK1G_RUNNER)
    summary = runner_module.run_demo(database_path=str(tmp_path / "track1g-api.sqlite3"))
    assert summary["created_product_id"] == "product-0002"
    assert summary["created_affiliate_offer_id"] == "affiliate-offer-0002"
    assert summary["demo_product_count"] == 2
    assert summary["demo_affiliate_offer_count"] == 2


def test_track1g_deferred_boundaries_are_preserved() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "Track 1G does not implement insight generation.",
            "Track 1G does not implement recommendation runtime.",
            "Track 1G does not approve production promotion.",
            "Track 1G does not approve production deployment.",
            "Track 1G does not implement production authentication.",
            "Track 1G does not implement RBAC enforcement.",
            "Track 1G does not implement production signing.",
            "Track 1G does not implement verifier runtime.",
            "Track 1G does not implement key custody runtime.",
        ),
        label="deferred boundary",
    )


def test_track1g_docs_and_state_pointers_reference_track1g() -> None:
    for path in (ROADMAP, PROJECT_STATE, TRACK1F_DOC):
        assert "Track 1G" in _text(path), f"missing Track 1G reference in {path}"


def test_track1g_no_production_demo_deployment_or_cloud_files_are_introduced() -> None:
    forbidden = (
        REPO_ROOT / "vercel.json",
        REPO_ROOT / "netlify.toml",
        REPO_ROOT / "Dockerfile.track1g",
        REPO_ROOT / "docker-compose.track1g.yml",
        REPO_ROOT / "terraform/track1g.tf",
        REPO_ROOT / "kubernetes/track1g-demo.yaml",
        REPO_ROOT / ".github/workflows/deploy-track1g-demo.yml",
        REPO_ROOT / "scripts/dev/track1g_production_deployment.py",
        REPO_ROOT / "scripts/dev/track1g_insight_generation.py",
        REPO_ROOT / "scripts/dev/track1g_recommendation_runtime.py",
    )
    for path in forbidden:
        assert not path.exists(), f"unexpected Track 1G forbidden file: {path}"
