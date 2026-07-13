from __future__ import annotations

import importlib.util
import json
import socket
import threading
import urllib.error
import urllib.request
from pathlib import Path
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/098-track1c-local-backend-api-skeleton.md"
DOC = REPO_ROOT / "docs/TRACK1C_LOCAL_BACKEND_API_SKELETON.md"
THIS_TEST = Path(__file__)

CONFIG_MODULE = REPO_ROOT / "scripts/dev/track1c_local_backend_config.py"
API_MODULE = REPO_ROOT / "scripts/dev/track1c_local_backend_api.py"
RUNNER_SCRIPT = REPO_ROOT / "scripts/dev/run_track1c_local_backend.py"
RUNNER_WRAPPER = REPO_ROOT / "scripts/dev/run_track1c_local_backend.sh"

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
TRACK1B_DOC = REPO_ROOT / "docs/TRACK1B_BACKEND_API_DATABASE_PRODUCT_SLICE_PLAN.md"


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


def _start_local_backend() -> tuple[object, threading.Thread, str]:
    config_module = _load_module("track1c_config", CONFIG_MODULE)
    api_module = _load_module("track1c_api", API_MODULE)

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
    return server, thread, f"http://127.0.0.1:{port}"


def test_track1c_required_files_exist() -> None:
    for path in (
        TASK_FILE,
        DOC,
        THIS_TEST,
        CONFIG_MODULE,
        API_MODULE,
        RUNNER_SCRIPT,
        RUNNER_WRAPPER,
    ):
        assert path.is_file(), f"missing Track 1C file: {path}"


def test_track1c_required_canonical_wording_exists() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "Track 1C implements the local backend/API skeleton for the first usable local product slice.",
            "Track 1C is the first runtime implementation step in Implementation Track 1.",
            "Track 1C implements local service startup, local configuration loading, GET /health, GET /version, and GET /runtime/status.",
            "Track 1C does not implement database/storage runtime.",
            "Track 1C does not implement Product or AffiliateOffer CRUD.",
            "Track 1C does not implement insight generation.",
            "Track 1C does not approve production promotion.",
            "Track 1C does not approve production deployment.",
            "Track 1C preserves the Phase 7D selected-gate manual boundary.",
            "Selected Runtime Domain: backend/API/database runtime",
            "Implementation Track: Implementation Track 1 — Backend/API/Database Usable Product Slice",
            "Product Goal: first usable local product slice",
            "Runtime Mode: local-only",
            "Production Promotion Status: not approved",
            "Production Deployment Status: not approved",
            "Production Authentication Status: deferred",
            "RBAC Enforcement Status: deferred",
            "Production Signing Status: deferred",
            "Verifier Runtime Status: deferred",
            "Key Custody Runtime Status: deferred",
            "Phase 7D Boundary Status: preserved",
            "Track 1D is the first approved point for database/storage runtime implementation, if Track 1C is accepted.",
        ),
        label="canonical wording",
    )


def test_track1c_task_file_preserves_core_boundary_wording() -> None:
    text = _text(TASK_FILE)
    _assert_all_tokens(
        text,
        (
            "Track 1C implements the local backend/API skeleton for the first usable local product slice.",
            "Track 1C is the first runtime implementation step in Implementation Track 1.",
            "Track 1C implements local service startup, local configuration loading, GET /health, GET /version, and GET /runtime/status.",
            "Track 1C does not implement database/storage runtime.",
            "Track 1C does not implement Product or AffiliateOffer CRUD.",
            "Track 1C does not implement insight generation.",
            "Track 1C does not approve production promotion.",
            "Track 1C does not approve production deployment.",
            "Track 1C preserves the Phase 7D selected-gate manual boundary.",
        ),
        label="task token",
    )


def test_track1c_required_sections_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "track 1c purpose",
            "relationship to track 1a",
            "relationship to track 1b",
            "local runtime implementation scope",
            "backend/api skeleton implementation",
            "endpoint contract",
            "local configuration boundary",
            "runtime status boundary",
            "deferred database/storage runtime",
            "deferred product crud scope",
            "deferred insight generation scope",
            "deferred security and hardening scope",
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


def test_track1c_required_matrices_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "| Endpoint | Method | Runtime Purpose | Required Response Fields | Boundary Signal | Track Introduced |",
            "| Runtime Area | Track 1C Status | Allowed Behavior | Forbidden Behavior | Next Eligible Track |",
            "| Deferred Area | Current Status | Deferred Reason | First Eligible Track | Required Future Approval |",
            "| GET /health | GET |",
            "| GET /version | GET |",
            "| GET /runtime/status | GET |",
            "| service startup |",
            "| local configuration loading |",
            "| backend/API skeleton |",
            "| database/storage runtime |",
            "| Product CRUD |",
            "| AffiliateOffer CRUD |",
            "| CollectionRun runtime |",
            "| Insight generation |",
            "| Recommendation runtime |",
            "| production authentication |",
            "| RBAC enforcement |",
            "| production signing |",
            "| verifier runtime |",
            "| key custody runtime |",
            "| production deployment |",
            "| cloud infrastructure |",
            "| CI/CD deployment |",
        ),
        label="matrix token",
    )


def test_track1c_health_endpoint_returns_required_local_only_contract() -> None:
    server, thread, base_url = _start_local_backend()
    try:
        status, payload = _request_json(f"{base_url}/health")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert status == 200
    assert payload == {
        "status": "ok",
        "service": "affiliate-ai-backend",
        "runtime_mode": "local-only",
    }


def test_track1c_version_endpoint_returns_required_track_contract() -> None:
    server, thread, base_url = _start_local_backend()
    try:
        status, payload = _request_json(f"{base_url}/version")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert status == 200
    assert payload == {
        "service": "affiliate-ai-backend",
        "version": "local-dev",
        "implementation_track": "Implementation Track 1 — Backend/API/Database Usable Product Slice",
        "track": "Track 1C",
    }


def test_track1c_runtime_status_endpoint_returns_required_boundary_contract() -> None:
    server, thread, base_url = _start_local_backend()
    try:
        status, payload = _request_json(f"{base_url}/runtime/status")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert status == 200
    assert payload == {
        "selected_runtime_domain": "backend/API/database runtime",
        "runtime_mode": "local-only",
        "production_frontend_deployment_status": "not approved",
        "production_promotion_status": "not approved",
        "production_deployment_status": "not approved",
        "production_authentication_status": "deferred",
        "rbac_enforcement_status": "deferred",
        "production_signing_status": "deferred",
        "verifier_runtime_status": "deferred",
        "key_custody_runtime_status": "deferred",
        "phase_7d_boundary_status": "preserved",
        "database_storage_runtime_status": "implemented in Track 1D as SQLite local-first MVP",
        "storage_runtime": "SQLite local-first MVP",
        "product_crud_status": "implemented in Track 1E",
        "product_core_api_status": "implemented in Track 1E",
        "product_endpoint_status": "implemented in Track 1E",
        "affiliate_offer_endpoint_status": "implemented in Track 1E",
        "minimal_operator_flow_status": "implemented in Track 1F",
        "operator_surface_status": "implemented in Track 1F",
        "end_to_end_demo_pack_status": "implemented in Track 1G",
        "demo_workflow_status": "implemented in Track 1G",
        "production_demo_deployment_status": "not approved",
        "insight_generation_status": "not implemented in Track 1G",
        "recommendation_runtime_status": "not implemented in Track 1G",
    }


def test_track1c_state_pointer_docs_reference_track1c() -> None:
    roadmap = _text(ROADMAP)
    project_state = _text(PROJECT_STATE)
    track1b = _text(TRACK1B_DOC)

    _assert_all_tokens(
        roadmap,
        (
            "Track 1C — Local Backend/API Skeleton",
            "docs/TRACK1C_LOCAL_BACKEND_API_SKELETON.md",
            "Track 1C implements the local backend/API skeleton for the first usable local product slice.",
        ),
        label="roadmap Track 1C pointer",
    )
    _assert_all_tokens(
        project_state,
        (
            "Track 1C adds the local backend/API skeleton documented in",
            "`docs/TRACK1C_LOCAL_BACKEND_API_SKELETON.md`.",
            "`track1c_status` is `success`.",
            "`runtime_mode` is `local-only`.",
            "`implementation_track_status` remains `implementation_track_1_started`.",
        ),
        label="project state Track 1C pointer",
    )
    _assert_all_tokens(
        track1b,
        (
            "Track 1C implements the local backend/API skeleton for the first usable local product slice.",
            "Track 1C is the first runtime implementation step in Implementation Track 1.",
            "Track 1C implements local service startup, local configuration loading, GET /health, GET /version, and GET /runtime/status.",
            "Track 1C does not implement database/storage runtime.",
            "Track 1C does not implement Product or AffiliateOffer CRUD.",
            "Track 1C does not implement insight generation.",
            "Track 1C does not approve production promotion.",
            "Track 1C does not approve production deployment.",
            "Track 1C preserves the Phase 7D selected-gate manual boundary.",
            "Track 1D is the first approved point for database/storage runtime implementation, if Track 1C is accepted.",
        ),
        label="track1b Track 1C pointer",
    )


def test_track1c_no_database_or_deployment_or_production_runtime_files_are_introduced() -> None:
    forbidden_files = [
        REPO_ROOT / "migrations" / "track1c.sql",
        REPO_ROOT / "schema" / "track1c.sql",
        REPO_ROOT / "docker-compose.track1c.yml",
        REPO_ROOT / ".github" / "workflows" / "track1c.yml",
        REPO_ROOT / "scripts/dev/track1c_database_runtime.py",
        REPO_ROOT / "scripts/dev/track1c_product_crud.py",
        REPO_ROOT / "scripts/dev/track1c_affiliate_offer_crud.py",
        REPO_ROOT / "scripts/dev/track1c_insight_generation.py",
        REPO_ROOT / "scripts/dev/track1c_authentication_runtime.py",
        REPO_ROOT / "scripts/dev/track1c_rbac_runtime.py",
        REPO_ROOT / "scripts/dev/track1c_signing_runtime.py",
        REPO_ROOT / "scripts/dev/track1c_verifier_runtime.py",
        REPO_ROOT / "scripts/dev/track1c_key_custody_runtime.py",
    ]
    for path in forbidden_files:
        assert not path.exists(), f"unexpected Track 1C forbidden runtime file: {path}"
