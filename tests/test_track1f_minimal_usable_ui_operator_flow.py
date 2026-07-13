from __future__ import annotations

import importlib.util
import json
import os
import socket
import threading
import urllib.error
import urllib.request
from pathlib import Path
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/101-track1f-minimal-usable-ui-operator-flow.md"
DOC = REPO_ROOT / "docs/TRACK1F_MINIMAL_USABLE_UI_OPERATOR_FLOW.md"
THIS_TEST = Path(__file__)

TRACK1F_HELPER_MODULE = REPO_ROOT / "scripts/dev/track1f_operator_page.py"
TRACK1D_STORAGE_MODULE = REPO_ROOT / "scripts/dev/track1d_local_storage.py"
TRACK1C_API_MODULE = REPO_ROOT / "scripts/dev/track1c_local_backend_api.py"
TRACK1C_CONFIG_MODULE = REPO_ROOT / "scripts/dev/track1c_local_backend_config.py"

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
TRACK1E_DOC = REPO_ROOT / "docs/TRACK1E_PRODUCT_CORE_API.md"


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


def _request_json(
    url: str,
    *,
    method: str = "GET",
    data: dict[str, object] | None = None,
    raw_body: bytes | None = None,
) -> tuple[int, dict[str, object]]:
    body = raw_body
    headers = {"Content-Type": "application/json; charset=utf-8"}
    if data is not None:
        body = json.dumps(data, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return response.status, payload
    except urllib.error.HTTPError as exc:
        payload = json.loads(exc.read().decode("utf-8"))
        return exc.code, payload


def _request_html(url: str) -> tuple[int, str, str]:
    request = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(request, timeout=5) as response:
        body = response.read().decode("utf-8")
        return response.status, response.headers.get("Content-Type", ""), body


def _start_local_backend(storage_path: Path) -> tuple[object, threading.Thread, str]:
    previous_storage_path = os.environ.get("AFFILIATE_STORAGE_PATH")
    os.environ["AFFILIATE_STORAGE_PATH"] = str(storage_path)
    config_module = _load_module("track1c_config_track1f", TRACK1C_CONFIG_MODULE)
    api_module = _load_module("track1c_api_track1f", TRACK1C_API_MODULE)

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

    server._track1f_restore_env = _restore_env  # type: ignore[attr-defined]
    return server, thread, f"http://127.0.0.1:{port}"


def _shutdown_local_backend(server: object, thread: threading.Thread) -> None:
    restore_env = getattr(server, "_track1f_restore_env", None)
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)
    if callable(restore_env):
        restore_env()


def test_track1f_required_files_exist() -> None:
    for path in (
        TASK_FILE,
        DOC,
        THIS_TEST,
        TRACK1F_HELPER_MODULE,
    ):
        assert path.is_file(), f"missing Track 1F file: {path}"


def test_track1f_required_canonical_wording_exists_in_doc() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "Track 1F implements the minimal usable UI/operator flow for the first usable local product slice.",
            "Track 1F continues Implementation Track 1 — Backend/API/Database Usable Product Slice.",
            "Track 1F builds on the Track 1C local backend/API skeleton.",
            "Track 1F builds on the Track 1D SQLite local-first storage runtime.",
            "Track 1F builds on the Track 1E Product Core API.",
            "Track 1F provides a local-only operator flow for Product and AffiliateOffer usage.",
            "Track 1F does not implement production frontend deployment.",
            "Track 1F does not implement production authentication.",
            "Track 1F does not implement RBAC enforcement.",
            "Track 1F does not implement production signing.",
            "Track 1F does not implement verifier runtime.",
            "Track 1F does not implement key custody runtime.",
            "Track 1F does not approve production promotion.",
            "Track 1F does not approve production deployment.",
            "Track 1F preserves the Phase 7D selected-gate manual boundary.",
            "Selected Runtime Domain: backend/API/database runtime",
            "Implementation Track: Implementation Track 1 — Backend/API/Database Usable Product Slice",
            "Product Goal: first usable local product slice",
            "Runtime Mode: local-only",
            "Storage Runtime: SQLite local-first MVP",
            "Product Core API Status: implemented in Track 1E",
            "Minimal Operator Flow Status: implemented in Track 1F",
            "Production Promotion Status: not approved",
            "Production Deployment Status: not approved",
            "Production Authentication Status: deferred",
            "RBAC Enforcement Status: deferred",
            "Production Signing Status: deferred",
            "Verifier Runtime Status: deferred",
            "Key Custody Runtime Status: deferred",
            "Phase 7D Boundary Status: preserved",
            "Track 1G is the first approved point for End-to-End Demo Pack implementation, if Track 1F is accepted.",
        ),
        label="canonical wording",
    )


def test_track1f_required_canonical_wording_exists_in_task_file() -> None:
    text = _text(TASK_FILE)
    _assert_all_tokens(
        text,
        (
            "Track 1F implements the minimal usable UI/operator flow for the first usable local product slice.",
            "Track 1F continues Implementation Track 1 — Backend/API/Database Usable Product Slice.",
            "Track 1F builds on the Track 1C local backend/API skeleton.",
            "Track 1F builds on the Track 1D SQLite local-first storage runtime.",
            "Track 1F builds on the Track 1E Product Core API.",
            "Track 1F provides a local-only operator flow for Product and AffiliateOffer usage.",
            "Track 1F does not implement production frontend deployment.",
            "Track 1F does not implement production authentication.",
            "Track 1F does not implement RBAC enforcement.",
            "Track 1F does not implement production signing.",
            "Track 1F does not implement verifier runtime.",
            "Track 1F does not implement key custody runtime.",
            "Track 1F does not approve production promotion.",
            "Track 1F does not approve production deployment.",
            "Track 1F preserves the Phase 7D selected-gate manual boundary.",
            "Track 1G is the first approved point for End-to-End Demo Pack implementation, if Track 1F is accepted.",
        ),
        label="task token",
    )


def test_track1f_required_sections_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "track 1f purpose",
            "relationship to track 1a",
            "relationship to track 1b",
            "relationship to track 1c",
            "relationship to track 1d",
            "relationship to track 1e",
            "minimal usable operator flow scope",
            "operator surface contract",
            "product operator action contract",
            "affiliateoffer operator action contract",
            "runtime status operator contract",
            "local-only ui boundary",
            "existing api integration",
            "validation and error handling preservation",
            "deferred source ui scope",
            "deferred collectionrun workflow scope",
            "deferred insight generation scope",
            "deferred recommendation runtime scope",
            "deferred security and hardening scope",
            "production frontend deployment exclusion",
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


def test_track1f_required_matrices_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "| Operator Action | Local Surface | Backing API/Service | Expected Output | Boundary Signal | Track Introduced |",
            "| Surface Area | Local Implementation | Purpose | Allowed Behavior | Forbidden Behavior | Track Introduced |",
            "| Existing API | Track Introduced | Operator Use | Expected Behavior | Preservation Requirement | Track 1F Change |",
            "| Status Field | Required Value | Purpose | Boundary Signal | Track Introduced |",
            "| Deferred Area | Current Status | Deferred Reason | First Eligible Track | Required Future Approval |",
            "| View runtime status |",
            "| Add product |",
            "| View product list |",
            "| Add affiliate offer |",
            "| View affiliate offer list |",
            "| `GET /operator` |",
            "| `GET /runtime/status` |",
            "| `POST /products` |",
            "| `GET /products` |",
            "| `POST /affiliate-offers` |",
            "| `GET /affiliate-offers` |",
            "| Source UI/API |",
            "| CollectionRun workflow UI/API |",
            "| insight generation |",
            "| recommendation runtime |",
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
        label="matrix token",
    )


def test_track1f_operator_route_returns_html_surface(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1f_operator", TRACK1D_STORAGE_MODULE)
    database_path = tmp_path / "track1f-operator.sqlite3"
    config = storage_module.load_local_storage_config({"AFFILIATE_STORAGE_PATH": str(database_path)})
    storage_module.seed_demo_data(config)

    server, thread, base_url = _start_local_backend(database_path)
    try:
        status, content_type, body = _request_html(f"{base_url}/operator")
    finally:
        _shutdown_local_backend(server, thread)

    assert status == 200
    assert content_type.startswith("text/html")
    _assert_all_tokens(
        body,
        (
            "ตัวจัดการ Affiliate Product",
            "โหมด Local เท่านั้น",
            "สถานะระบบ",
            "เพิ่มสินค้า",
            "รายการสินค้า",
            "เพิ่ม Affiliate Offer",
            "รายการ Affiliate Offer",
            "ผลลัพธ์ล่าสุด",
            "ข้อผิดพลาดล่าสุด",
        ),
        label="operator page content",
    )


def test_track1f_operator_page_references_existing_track1e_endpoints(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1f_page_endpoints", TRACK1D_STORAGE_MODULE)
    database_path = tmp_path / "track1f-page-endpoints.sqlite3"
    config = storage_module.load_local_storage_config({"AFFILIATE_STORAGE_PATH": str(database_path)})
    storage_module.seed_demo_data(config)

    server, thread, base_url = _start_local_backend(database_path)
    try:
        _, _, body = _request_html(f"{base_url}/operator")
    finally:
        _shutdown_local_backend(server, thread)

    _assert_all_tokens(
        body,
        (
            "/runtime/status",
            "/products",
            "/affiliate-offers",
            "fetch(",
            "demo-source-track1d",
        ),
        label="endpoint reference",
    )
    assert "/sources" not in body
    assert "/collection-runs" not in body


def test_track1f_health_endpoint_still_works(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1f_health", TRACK1D_STORAGE_MODULE)
    database_path = tmp_path / "track1f-health.sqlite3"
    config = storage_module.load_local_storage_config({"AFFILIATE_STORAGE_PATH": str(database_path)})
    storage_module.ensure_track1e_schema(config)

    server, thread, base_url = _start_local_backend(database_path)
    try:
        status, payload = _request_json(f"{base_url}/health")
    finally:
        _shutdown_local_backend(server, thread)

    assert status == 200
    assert payload == {
        "status": "ok",
        "service": "affiliate-ai-backend",
        "runtime_mode": "local-only",
    }


def test_track1f_version_endpoint_still_works(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1f_version", TRACK1D_STORAGE_MODULE)
    database_path = tmp_path / "track1f-version.sqlite3"
    config = storage_module.load_local_storage_config({"AFFILIATE_STORAGE_PATH": str(database_path)})
    storage_module.ensure_track1e_schema(config)

    server, thread, base_url = _start_local_backend(database_path)
    try:
        status, payload = _request_json(f"{base_url}/version")
    finally:
        _shutdown_local_backend(server, thread)

    assert status == 200
    assert payload == {
        "service": "affiliate-ai-backend",
        "version": "local-dev",
        "implementation_track": "Implementation Track 1 — Backend/API/Database Usable Product Slice",
        "track": "Track 1C",
    }


def test_track1f_runtime_status_reports_operator_fields(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1f_runtime", TRACK1D_STORAGE_MODULE)
    database_path = tmp_path / "track1f-runtime.sqlite3"
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
    assert payload["operator_surface_status"] == "implemented in Track 1F"
    assert payload["production_frontend_deployment_status"] == "not approved"
    assert payload["end_to_end_demo_pack_status"] == "implemented in Track 1G"
    assert payload["demo_workflow_status"] == "implemented in Track 1G"
    assert payload["production_demo_deployment_status"] == "not approved"
    assert payload["insight_generation_status"] == "not implemented in Track 1G"
    assert payload["recommendation_runtime_status"] == "not implemented in Track 1G"


def test_track1f_existing_product_api_still_works(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1f_product_api", TRACK1D_STORAGE_MODULE)
    database_path = tmp_path / "track1f-product-api.sqlite3"
    config = storage_module.load_local_storage_config({"AFFILIATE_STORAGE_PATH": str(database_path)})
    storage_module.ensure_track1e_schema(config)

    server, thread, base_url = _start_local_backend(database_path)
    try:
        status, payload = _request_json(
            f"{base_url}/products",
            method="POST",
            data={
                "name": "Track 1F Desk Shelf",
                "category": "desk",
                "description": "Operator flow demo product.",
            },
        )
        list_status, list_payload = _request_json(f"{base_url}/products")
    finally:
        _shutdown_local_backend(server, thread)

    assert status == 200
    assert payload["name"] == "Track 1F Desk Shelf"
    assert payload["category"] == "desk"
    assert list_status == 200
    assert list_payload["count"] >= 1


def test_track1f_existing_affiliate_offer_api_still_works(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1f_offer_api", TRACK1D_STORAGE_MODULE)
    database_path = tmp_path / "track1f-offer-api.sqlite3"
    config = storage_module.load_local_storage_config({"AFFILIATE_STORAGE_PATH": str(database_path)})
    storage_module.seed_demo_data(config)

    server, thread, base_url = _start_local_backend(database_path)
    try:
        status, payload = _request_json(
            f"{base_url}/affiliate-offers",
            method="POST",
            data={
                "product_id": "demo-product-track1e",
                "source_id": "demo-source-track1d",
                "offer_url": "https://example.com/track1f-offer",
                "title": "Track 1F Offer",
            },
        )
        list_status, list_payload = _request_json(f"{base_url}/affiliate-offers")
    finally:
        _shutdown_local_backend(server, thread)

    assert status == 200
    assert payload["product_id"] == "demo-product-track1e"
    assert payload["source_id"] == "demo-source-track1d"
    assert list_status == 200
    assert list_payload["count"] >= 1


def test_track1f_validation_error_contract_is_preserved(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1f_error_contract", TRACK1D_STORAGE_MODULE)
    database_path = tmp_path / "track1f-error-contract.sqlite3"
    config = storage_module.load_local_storage_config({"AFFILIATE_STORAGE_PATH": str(database_path)})
    storage_module.ensure_track1e_schema(config)

    server, thread, base_url = _start_local_backend(database_path)
    try:
        status, payload = _request_json(
            f"{base_url}/products",
            method="POST",
            raw_body=b'{"name":"Broken","category":',
        )
    finally:
        _shutdown_local_backend(server, thread)

    assert status == 400
    assert payload == {
        "error": "validation_error",
        "message": "Request body must be valid JSON.",
        "status_code": 400,
    }


def test_track1f_no_frontend_framework_dependencies_are_introduced() -> None:
    forbidden = (
        REPO_ROOT / "package.json",
        REPO_ROOT / "package-lock.json",
        REPO_ROOT / "pnpm-lock.yaml",
        REPO_ROOT / "yarn.lock",
        REPO_ROOT / "next.config.js",
        REPO_ROOT / "vite.config.ts",
        REPO_ROOT / "tailwind.config.js",
        REPO_ROOT / "frontend/package.json",
        REPO_ROOT / "apps/operator/package.json",
    )
    for path in forbidden:
        assert not path.exists(), f"unexpected frontend dependency file introduced: {path}"


def test_track1f_no_production_deployment_or_cloud_infrastructure_files_are_introduced() -> None:
    forbidden = (
        REPO_ROOT / "vercel.json",
        REPO_ROOT / "netlify.toml",
        REPO_ROOT / "Dockerfile.operator",
        REPO_ROOT / "docker-compose.operator.yml",
        REPO_ROOT / "terraform/main.tf",
        REPO_ROOT / "kubernetes/operator-deployment.yaml",
        REPO_ROOT / ".github/workflows/deploy-operator.yml",
    )
    for path in forbidden:
        assert not path.exists(), f"unexpected deployment or infrastructure file introduced: {path}"


def test_track1f_no_source_or_collectionrun_ui_is_introduced() -> None:
    text = _text(DOC)
    assert "Track 1F does not implement Source UI/API." in text
    assert "Track 1F does not implement CollectionRun workflow UI/API." in text


def test_track1f_insight_and_recommendation_runtime_are_not_implemented() -> None:
    text = _text(DOC)
    assert "Track 1F does not implement insight generation." in text
    assert "Track 1F does not implement recommendation runtime." in text


def test_track1f_promotion_and_deployment_are_not_approved() -> None:
    text = _text(DOC)
    assert "Track 1F does not approve production promotion." in text
    assert "Track 1F does not approve production deployment." in text


def test_track1f_auth_rbac_signing_verifier_and_key_custody_remain_deferred() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "Track 1F does not implement production authentication.",
            "Track 1F does not implement RBAC enforcement.",
            "Track 1F does not implement production signing.",
            "Track 1F does not implement verifier runtime.",
            "Track 1F does not implement key custody runtime.",
        ),
        label="security boundary wording",
    )


def test_track1f_docs_and_state_pointers_reference_track1f() -> None:
    for path in (ROADMAP, PROJECT_STATE, TRACK1E_DOC):
        assert "Track 1F" in _text(path), f"missing Track 1F reference in {path}"
