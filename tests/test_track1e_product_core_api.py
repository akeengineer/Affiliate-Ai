from __future__ import annotations

import importlib.util
import json
import os
import socket
import sqlite3
import threading
import urllib.error
import urllib.request
from pathlib import Path
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/100-track1e-product-core-api.md"
DOC = REPO_ROOT / "docs/TRACK1E_PRODUCT_CORE_API.md"
THIS_TEST = Path(__file__)

TRACK1E_HELPER_MODULE = REPO_ROOT / "scripts/dev/track1e_product_core_api.py"
TRACK1D_STORAGE_MODULE = REPO_ROOT / "scripts/dev/track1d_local_storage.py"
TRACK1D_REPOSITORY_MODULE = REPO_ROOT / "scripts/dev/track1d_repository.py"
TRACK1C_API_MODULE = REPO_ROOT / "scripts/dev/track1c_local_backend_api.py"
TRACK1C_CONFIG_MODULE = REPO_ROOT / "scripts/dev/track1c_local_backend_config.py"

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
TRACK1D_DOC = REPO_ROOT / "docs/TRACK1D_DATABASE_STORAGE_RUNTIME.md"

REQUIRED_TRACK1E_TABLES = (
    "products",
    "affiliate_offers",
    "sources",
    "collection_runs",
    "insights",
    "recommendations",
)


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


def _start_local_backend(storage_path: Path) -> tuple[object, threading.Thread, str]:
    previous_storage_path = os.environ.get("AFFILIATE_STORAGE_PATH")
    os.environ["AFFILIATE_STORAGE_PATH"] = str(storage_path)
    config_module = _load_module("track1c_config_track1e", TRACK1C_CONFIG_MODULE)
    api_module = _load_module("track1c_api_track1e", TRACK1C_API_MODULE)

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

    server._track1e_restore_env = _restore_env  # type: ignore[attr-defined]
    return server, thread, f"http://127.0.0.1:{port}"


def _shutdown_local_backend(server: object, thread: threading.Thread) -> None:
    restore_env = getattr(server, "_track1e_restore_env", None)
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)
    if callable(restore_env):
        restore_env()


def _table_columns(database_path: Path, table_name: str) -> list[str]:
    with sqlite3.connect(database_path) as connection:
        rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    return [str(row[1]) for row in rows]


def _create_track1d_foundation_database(database_path: Path) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE products (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                marketplace TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE affiliate_offers (
                id TEXT PRIMARY KEY,
                product_id TEXT NOT NULL,
                program_name TEXT NOT NULL,
                commission_model TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE sources (
                id TEXT PRIMARY KEY,
                product_id TEXT NOT NULL,
                source_type TEXT NOT NULL,
                source_ref TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE collection_runs (
                id TEXT PRIMARY KEY,
                product_id TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE insights (
                id TEXT PRIMARY KEY,
                product_id TEXT NOT NULL,
                insight_type TEXT NOT NULL,
                summary TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE recommendations (
                id TEXT PRIMARY KEY,
                product_id TEXT NOT NULL,
                recommendation_type TEXT NOT NULL,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.commit()


def test_track1e_required_files_exist() -> None:
    for path in (
        TASK_FILE,
        DOC,
        THIS_TEST,
        TRACK1E_HELPER_MODULE,
    ):
        assert path.is_file(), f"missing Track 1E file: {path}"


def test_track1e_required_canonical_wording_exists_in_doc() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "Track 1E implements the Product Core API for the first usable local product slice.",
            "Track 1E continues Implementation Track 1 — Backend/API/Database Usable Product Slice.",
            "Track 1E builds on the Track 1C local backend/API skeleton.",
            "Track 1E builds on the Track 1D SQLite local-first storage runtime.",
            "Track 1E implements local Product and AffiliateOffer API endpoints.",
            "Track 1E uses SQLite local-first MVP storage through the Track 1D repository/data access boundary.",
            "Track 1E evolves the Track 1D SQLite local-first schema only within the local product-slice runtime boundary.",
            "Track 1E schema evolution does not approve production database runtime.",
            "Track 1E schema evolution does not approve PostgreSQL or Aurora runtime.",
            "Track 1E schema evolution remains limited to SQLite local-first MVP storage.",
            "Track 1E continues to use the Track 1D repository/data access boundary.",
            "Track 1E does not implement production authentication.",
            "Track 1E does not implement RBAC enforcement.",
            "Track 1E does not implement production signing.",
            "Track 1E does not implement verifier runtime.",
            "Track 1E does not implement key custody runtime.",
            "Track 1E does not implement insight generation.",
            "Track 1E does not implement recommendation runtime.",
            "Track 1E does not approve production promotion.",
            "Track 1E does not approve production deployment.",
            "Track 1E preserves the Phase 7D selected-gate manual boundary.",
            "Selected Runtime Domain: backend/API/database runtime",
            "Implementation Track: Implementation Track 1 — Backend/API/Database Usable Product Slice",
            "Product Goal: first usable local product slice",
            "Runtime Mode: local-only",
            "Storage Runtime: SQLite local-first MVP",
            "Product Core API Status: implemented in Track 1E",
            "Production Promotion Status: not approved",
            "Production Deployment Status: not approved",
            "Production Authentication Status: deferred",
            "RBAC Enforcement Status: deferred",
            "Production Signing Status: deferred",
            "Verifier Runtime Status: deferred",
            "Key Custody Runtime Status: deferred",
            "Phase 7D Boundary Status: preserved",
            "Track 1F is the first approved point for Minimal Usable UI/operator flow implementation, if Track 1E is accepted.",
        ),
        label="canonical wording",
    )


def test_track1e_required_canonical_wording_exists_in_task_file() -> None:
    text = _text(TASK_FILE)
    _assert_all_tokens(
        text,
        (
            "Track 1E implements the Product Core API for the first usable local product slice.",
            "Track 1E evolves the Track 1D SQLite local-first schema only within the local product-slice runtime boundary.",
            "Track 1E schema evolution does not approve production database runtime.",
            "Track 1E schema evolution does not approve PostgreSQL or Aurora runtime.",
            "Track 1E schema evolution remains limited to SQLite local-first MVP storage.",
            "Track 1E continues to use the Track 1D repository/data access boundary.",
            "Track 1E does not implement insight generation.",
            "Track 1E does not implement recommendation runtime.",
            "Track 1E does not approve production promotion.",
            "Track 1E does not approve production deployment.",
            "Track 1E preserves the Phase 7D selected-gate manual boundary.",
        ),
        label="task wording",
    )


def test_track1e_required_sections_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "track 1e purpose",
            "relationship to track 1a",
            "relationship to track 1b",
            "relationship to track 1c",
            "relationship to track 1d",
            "local product core api scope",
            "product endpoint contract",
            "affiliateoffer endpoint contract",
            "validation and error handling contract",
            "repository/data access integration",
            "sqlite local-first storage boundary",
            "runtime status contract",
            "deferred source api scope",
            "deferred collectionrun workflow api scope",
            "deferred insight generation scope",
            "deferred recommendation runtime scope",
            "deferred security and hardening scope",
            "production database exclusion",
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


def test_track1e_required_matrices_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "| API Area | Endpoint | Method | Purpose | Required Validation | Track Introduced |",
            "| Field | Required | Type | Validation | Default | Storage Mapping |",
            "| Error Case | HTTP Status | Error Code | Required Response Fields | Deterministic Behavior | Track Introduced |",
            "| Repository Operation | Purpose | Storage Table | Allowed Behavior | Forbidden Behavior | Track Introduced |",
            "| Status Field | Required Value | Purpose | Boundary Signal | Track Introduced |",
            "| Deferred Area | Current Status | Deferred Reason | First Eligible Track | Required Future Approval |",
            "| Product | /products | POST |",
            "| Product | /products | GET |",
            "| Product | /products/{id} | GET |",
            "| Product | /products/{id} | PATCH |",
            "| AffiliateOffer | /affiliate-offers | POST |",
            "| AffiliateOffer | /affiliate-offers | GET |",
            "| Source API endpoints |",
            "| CollectionRun workflow API |",
            "| insight generation |",
            "| recommendation runtime |",
            "| production database runtime |",
            "| PostgreSQL/Aurora runtime |",
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
        ),
        label="matrix token",
    )


def test_track1e_implements_product_core_api_and_builds_on_track1c_and_track1d() -> None:
    flat_doc = _flat(DOC)
    assert "track 1e implements the product core api for the first usable local product slice." in flat_doc
    assert "track 1e builds on the track 1c local backend/api skeleton." in flat_doc
    assert "track 1e builds on the track 1d sqlite local-first storage runtime." in flat_doc


def test_track1e_schema_evolution_supports_fresh_database(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1e_fresh", TRACK1D_STORAGE_MODULE)
    database_path = tmp_path / "track1e-fresh.sqlite3"
    config = storage_module.load_local_storage_config({"AFFILIATE_STORAGE_PATH": str(database_path)})

    result = storage_module.ensure_track1e_schema(config)

    assert result["schema_version"] == "track1e"
    assert set(REQUIRED_TRACK1E_TABLES).issubset(set(result["tables"]))
    assert "category" in _table_columns(database_path, "products")
    assert "metadata" in _table_columns(database_path, "products")
    assert "source_id" in _table_columns(database_path, "affiliate_offers")
    assert "offer_url" in _table_columns(database_path, "affiliate_offers")


def test_track1e_schema_evolution_supports_existing_track1d_database(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1e_existing", TRACK1D_STORAGE_MODULE)
    database_path = tmp_path / "track1e-existing.sqlite3"
    _create_track1d_foundation_database(database_path)
    config = storage_module.load_local_storage_config({"AFFILIATE_STORAGE_PATH": str(database_path)})

    result = storage_module.ensure_track1e_schema(config)

    assert result["schema_version"] == "track1e"
    assert "category" in _table_columns(database_path, "products")
    assert "description" in _table_columns(database_path, "products")
    assert "source_id" in _table_columns(database_path, "affiliate_offers")
    assert "commission_rate" in _table_columns(database_path, "affiliate_offers")


def test_track1e_seed_data_uses_category_and_reusable_demo_source(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1e_seed", TRACK1D_STORAGE_MODULE)
    repository_module = _load_module("track1d_repo_track1e_seed", TRACK1D_REPOSITORY_MODULE)
    database_path = tmp_path / "track1e-seed.sqlite3"
    config = storage_module.load_local_storage_config({"AFFILIATE_STORAGE_PATH": str(database_path)})

    storage_module.seed_demo_data(config)
    repository = repository_module.Track1DRepository.connect(config.database_path)
    try:
        product = repository.get_product("demo-product-track1e")
        assert product is not None
        assert product["category"] == "productivity"
        assert repository.source_exists("demo-source-track1d")
    finally:
        repository.close()


def test_track1e_health_endpoint_still_works(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1e_health", TRACK1D_STORAGE_MODULE)
    database_path = tmp_path / "track1e-health.sqlite3"
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


def test_track1e_version_endpoint_still_works(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1e_version", TRACK1D_STORAGE_MODULE)
    database_path = tmp_path / "track1e-version.sqlite3"
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


def test_track1e_runtime_status_reports_product_core_api_implemented(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1e_runtime", TRACK1D_STORAGE_MODULE)
    database_path = tmp_path / "track1e-runtime.sqlite3"
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
    assert payload["product_endpoint_status"] == "implemented in Track 1E"
    assert payload["affiliate_offer_endpoint_status"] == "implemented in Track 1E"
    assert payload["insight_generation_status"] == "not implemented in Track 1E"
    assert payload["recommendation_runtime_status"] == "not implemented in Track 1E"


def test_post_products_creates_valid_product(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1e_post_product", TRACK1D_STORAGE_MODULE)
    database_path = tmp_path / "track1e-post-product.sqlite3"
    config = storage_module.load_local_storage_config({"AFFILIATE_STORAGE_PATH": str(database_path)})
    storage_module.ensure_track1e_schema(config)

    server, thread, base_url = _start_local_backend(database_path)
    try:
        status, payload = _request_json(
            f"{base_url}/products",
            method="POST",
            data={
                "name": "Desk Lamp",
                "category": "lighting",
                "description": "Local demo product.",
                "metadata": {"channel": "demo"},
            },
        )
    finally:
        _shutdown_local_backend(server, thread)

    assert status == 200
    assert payload["name"] == "Desk Lamp"
    assert payload["category"] == "lighting"
    assert payload["description"] == "Local demo product."
    assert payload["status"] == "active"
    assert payload["metadata"] == {"channel": "demo"}
    assert payload["id"]


def test_get_products_lists_products(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1e_list_products", TRACK1D_STORAGE_MODULE)
    database_path = tmp_path / "track1e-list-products.sqlite3"
    config = storage_module.load_local_storage_config({"AFFILIATE_STORAGE_PATH": str(database_path)})
    storage_module.seed_demo_data(config)

    server, thread, base_url = _start_local_backend(database_path)
    try:
        status, payload = _request_json(f"{base_url}/products")
    finally:
        _shutdown_local_backend(server, thread)

    assert status == 200
    assert payload["count"] >= 1
    assert payload["products"][0]["category"]


def test_get_product_by_id_returns_one_product(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1e_get_product", TRACK1D_STORAGE_MODULE)
    database_path = tmp_path / "track1e-get-product.sqlite3"
    config = storage_module.load_local_storage_config({"AFFILIATE_STORAGE_PATH": str(database_path)})
    storage_module.seed_demo_data(config)

    server, thread, base_url = _start_local_backend(database_path)
    try:
        status, payload = _request_json(f"{base_url}/products/demo-product-track1e")
    finally:
        _shutdown_local_backend(server, thread)

    assert status == 200
    assert payload["id"] == "demo-product-track1e"
    assert payload["category"] == "productivity"


def test_patch_product_updates_allowed_fields(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1e_patch_product", TRACK1D_STORAGE_MODULE)
    database_path = tmp_path / "track1e-patch-product.sqlite3"
    config = storage_module.load_local_storage_config({"AFFILIATE_STORAGE_PATH": str(database_path)})
    storage_module.seed_demo_data(config)

    server, thread, base_url = _start_local_backend(database_path)
    try:
        status, payload = _request_json(
            f"{base_url}/products/demo-product-track1e",
            method="PATCH",
            data={"status": "inactive", "description": "Updated description."},
        )
    finally:
        _shutdown_local_backend(server, thread)

    assert status == 200
    assert payload["status"] == "inactive"
    assert payload["description"] == "Updated description."


def test_invalid_product_create_returns_deterministic_validation_error(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1e_invalid_product", TRACK1D_STORAGE_MODULE)
    database_path = tmp_path / "track1e-invalid-product.sqlite3"
    config = storage_module.load_local_storage_config({"AFFILIATE_STORAGE_PATH": str(database_path)})
    storage_module.ensure_track1e_schema(config)

    server, thread, base_url = _start_local_backend(database_path)
    try:
        status, payload = _request_json(
            f"{base_url}/products",
            method="POST",
            data={"name": "", "category": "lighting"},
        )
    finally:
        _shutdown_local_backend(server, thread)

    assert status == 422
    assert payload["error"] == "validation_error"
    assert payload["status_code"] == 422


def test_unknown_product_id_returns_deterministic_not_found_error(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1e_missing_product", TRACK1D_STORAGE_MODULE)
    database_path = tmp_path / "track1e-missing-product.sqlite3"
    config = storage_module.load_local_storage_config({"AFFILIATE_STORAGE_PATH": str(database_path)})
    storage_module.ensure_track1e_schema(config)

    server, thread, base_url = _start_local_backend(database_path)
    try:
        status, payload = _request_json(f"{base_url}/products/missing-product")
    finally:
        _shutdown_local_backend(server, thread)

    assert status == 404
    assert payload == {
        "error": "not_found",
        "message": "Product not found: missing-product",
        "status_code": 404,
    }


def test_post_affiliate_offers_creates_valid_offer_linked_to_product_and_source(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1e_post_offer", TRACK1D_STORAGE_MODULE)
    database_path = tmp_path / "track1e-post-offer.sqlite3"
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
                "offer_url": "https://example.com/offer",
                "title": "Demo Offer",
                "price": 19.99,
                "currency": "USD",
                "commission_rate": 12.5,
                "metadata": {"network": "demo"},
            },
        )
    finally:
        _shutdown_local_backend(server, thread)

    assert status == 200
    assert payload["product_id"] == "demo-product-track1e"
    assert payload["source_id"] == "demo-source-track1d"
    assert payload["offer_url"] == "https://example.com/offer"
    assert payload["status"] == "active"


def test_get_affiliate_offers_lists_affiliate_offers(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1e_list_offers", TRACK1D_STORAGE_MODULE)
    database_path = tmp_path / "track1e-list-offers.sqlite3"
    config = storage_module.load_local_storage_config({"AFFILIATE_STORAGE_PATH": str(database_path)})
    storage_module.seed_demo_data(config)

    server, thread, base_url = _start_local_backend(database_path)
    try:
        status, payload = _request_json(f"{base_url}/affiliate-offers")
    finally:
        _shutdown_local_backend(server, thread)

    assert status == 200
    assert payload["count"] >= 1
    assert payload["affiliate_offers"][0]["product_id"]


def test_invalid_affiliate_offer_product_id_returns_deterministic_validation_error(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1e_invalid_offer_product", TRACK1D_STORAGE_MODULE)
    database_path = tmp_path / "track1e-invalid-offer-product.sqlite3"
    config = storage_module.load_local_storage_config({"AFFILIATE_STORAGE_PATH": str(database_path)})
    storage_module.seed_demo_data(config)

    server, thread, base_url = _start_local_backend(database_path)
    try:
        status, payload = _request_json(
            f"{base_url}/affiliate-offers",
            method="POST",
            data={
                "product_id": "missing-product",
                "source_id": "demo-source-track1d",
                "offer_url": "https://example.com/offer",
            },
        )
    finally:
        _shutdown_local_backend(server, thread)

    assert status == 422
    assert payload["error"] == "validation_error"
    assert payload["status_code"] == 422


def test_invalid_affiliate_offer_source_id_returns_deterministic_validation_error(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1e_invalid_offer_source", TRACK1D_STORAGE_MODULE)
    database_path = tmp_path / "track1e-invalid-offer-source.sqlite3"
    config = storage_module.load_local_storage_config({"AFFILIATE_STORAGE_PATH": str(database_path)})
    storage_module.seed_demo_data(config)

    server, thread, base_url = _start_local_backend(database_path)
    try:
        status, payload = _request_json(
            f"{base_url}/affiliate-offers",
            method="POST",
            data={
                "product_id": "demo-product-track1e",
                "source_id": "missing-source",
                "offer_url": "https://example.com/offer",
            },
        )
    finally:
        _shutdown_local_backend(server, thread)

    assert status == 422
    assert payload["error"] == "validation_error"
    assert payload["status_code"] == 422


def test_unsupported_route_returns_deterministic_not_found_error(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1e_not_found_route", TRACK1D_STORAGE_MODULE)
    database_path = tmp_path / "track1e-not-found-route.sqlite3"
    config = storage_module.load_local_storage_config({"AFFILIATE_STORAGE_PATH": str(database_path)})
    storage_module.ensure_track1e_schema(config)

    server, thread, base_url = _start_local_backend(database_path)
    try:
        status, payload = _request_json(f"{base_url}/unknown-route")
    finally:
        _shutdown_local_backend(server, thread)

    assert status == 404
    assert payload == {
        "error": "not_found",
        "message": "Route not found: /unknown-route",
        "status_code": 404,
    }


def test_unsupported_method_returns_deterministic_method_not_allowed_error(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1e_method_not_allowed", TRACK1D_STORAGE_MODULE)
    database_path = tmp_path / "track1e-method-not-allowed.sqlite3"
    config = storage_module.load_local_storage_config({"AFFILIATE_STORAGE_PATH": str(database_path)})
    storage_module.ensure_track1e_schema(config)

    server, thread, base_url = _start_local_backend(database_path)
    try:
        status, payload = _request_json(f"{base_url}/products", method="DELETE")
    finally:
        _shutdown_local_backend(server, thread)

    assert status == 405
    assert payload == {
        "error": "method_not_allowed",
        "message": "Method DELETE is not allowed for /products",
        "status_code": 405,
    }


def test_malformed_json_returns_deterministic_validation_error(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1e_bad_json", TRACK1D_STORAGE_MODULE)
    database_path = tmp_path / "track1e-bad-json.sqlite3"
    config = storage_module.load_local_storage_config({"AFFILIATE_STORAGE_PATH": str(database_path)})
    storage_module.ensure_track1e_schema(config)

    server, thread, base_url = _start_local_backend(database_path)
    try:
        status, payload = _request_json(
            f"{base_url}/products",
            method="POST",
            raw_body=b'{"name":"Desk Lamp","category":',
        )
    finally:
        _shutdown_local_backend(server, thread)

    assert status == 400
    assert payload == {
        "error": "validation_error",
        "message": "Request body must be valid JSON.",
        "status_code": 400,
    }


def test_product_and_affiliate_offer_api_use_sqlite_local_first_storage(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_track1e_sqlite_boundary", TRACK1D_STORAGE_MODULE)
    database_path = tmp_path / "track1e-sqlite-boundary.sqlite3"
    config = storage_module.load_local_storage_config({"AFFILIATE_STORAGE_PATH": str(database_path)})

    status = storage_module.ensure_track1e_schema(config)

    assert status["storage_runtime"] == "SQLite local-first MVP"
    assert status["runtime_mode"] == "local-only"


def test_track1e_insight_generation_is_not_implemented() -> None:
    text = _text(DOC)
    assert "Track 1E does not implement insight generation." in text
    assert "POST /insights/generate" not in text


def test_track1e_recommendation_runtime_is_not_implemented() -> None:
    text = _text(DOC)
    assert "Track 1E does not implement recommendation runtime." in text


def test_track1e_production_promotion_is_not_approved() -> None:
    text = _text(DOC)
    assert "Track 1E does not approve production promotion." in text
    assert "Production Promotion Status: not approved" in text


def test_track1e_production_deployment_is_not_approved() -> None:
    text = _text(DOC)
    assert "Track 1E does not approve production deployment." in text
    assert "Production Deployment Status: not approved" in text


def test_track1e_auth_rbac_signing_verifier_and_key_custody_remain_deferred() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "Track 1E does not implement production authentication.",
            "Track 1E does not implement RBAC enforcement.",
            "Track 1E does not implement production signing.",
            "Track 1E does not implement verifier runtime.",
            "Track 1E does not implement key custody runtime.",
        ),
        label="security boundary wording",
    )


def test_track1e_docs_and_state_pointers_reference_track1e() -> None:
    for path in (ROADMAP, PROJECT_STATE, TRACK1D_DOC):
        assert "Track 1E" in _text(path), f"missing Track 1E reference in {path}"


def test_track1e_no_production_database_files_are_introduced() -> None:
    forbidden = (
        REPO_ROOT / "scripts/dev/track1e_postgres_runtime.py",
        REPO_ROOT / "scripts/dev/track1e_aurora_runtime.py",
        REPO_ROOT / "scripts/dev/run_track1e_postgres_runtime.sh",
    )
    for path in forbidden:
        assert not path.exists(), f"unexpected production database file: {path}"


def test_track1e_no_deployment_or_cloud_infrastructure_files_are_introduced() -> None:
    forbidden = (
        REPO_ROOT / "scripts/dev/track1e_deploy.py",
        REPO_ROOT / ".github/workflows/track1e-deploy.yml",
        REPO_ROOT / "infra/track1e",
    )
    for path in forbidden:
        assert not path.exists(), f"unexpected deployment or cloud file: {path}"


def test_track1e_no_production_auth_rbac_signing_verifier_or_key_custody_runtime_files_are_introduced() -> None:
    forbidden = (
        REPO_ROOT / "scripts/dev/track1e_auth_runtime.py",
        REPO_ROOT / "scripts/dev/track1e_rbac_runtime.py",
        REPO_ROOT / "scripts/dev/track1e_signing_runtime.py",
        REPO_ROOT / "scripts/dev/track1e_verifier_runtime.py",
        REPO_ROOT / "scripts/dev/track1e_key_custody_runtime.py",
    )
    for path in forbidden:
        assert not path.exists(), f"unexpected Track 1E security-runtime file: {path}"
