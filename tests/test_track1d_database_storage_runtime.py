from __future__ import annotations

import importlib.util
import json
import os
import socket
import sqlite3
import threading
import urllib.request
from pathlib import Path
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/099-track1d-database-storage-runtime.md"
DOC = REPO_ROOT / "docs/TRACK1D_DATABASE_STORAGE_RUNTIME.md"
THIS_TEST = Path(__file__)

STORAGE_MODULE = REPO_ROOT / "scripts/dev/track1d_local_storage.py"
REPOSITORY_MODULE = REPO_ROOT / "scripts/dev/track1d_repository.py"
RUNNER_SCRIPT = REPO_ROOT / "scripts/dev/run_track1d_local_storage.py"
RUNNER_WRAPPER = REPO_ROOT / "scripts/dev/run_track1d_local_storage.sh"

TRACK1C_API_MODULE = REPO_ROOT / "scripts/dev/track1c_local_backend_api.py"
TRACK1C_CONFIG_MODULE = REPO_ROOT / "scripts/dev/track1c_local_backend_config.py"

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
TRACK1C_DOC = REPO_ROOT / "docs/TRACK1C_LOCAL_BACKEND_API_SKELETON.md"

REQUIRED_TABLES = (
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


def _request_json(url: str) -> tuple[int, dict[str, object]]:
    request = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(request, timeout=5) as response:
        payload = json.loads(response.read().decode("utf-8"))
        return response.status, payload


def _start_local_backend(storage_path: Path) -> tuple[object, threading.Thread, str]:
    previous_storage_path = os.environ.get("AFFILIATE_STORAGE_PATH")
    os.environ["AFFILIATE_STORAGE_PATH"] = str(storage_path)
    config_module = _load_module("track1c_config_track1d", TRACK1C_CONFIG_MODULE)
    api_module = _load_module("track1c_api_track1d", TRACK1C_API_MODULE)

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

    server._track1d_restore_env = _restore_env  # type: ignore[attr-defined]
    return server, thread, f"http://127.0.0.1:{port}"


def _shutdown_local_backend(server: object, thread: threading.Thread) -> None:
    restore_env = getattr(server, "_track1d_restore_env", None)
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)
    if callable(restore_env):
        restore_env()


def _table_names(database_path: Path) -> set[str]:
    with sqlite3.connect(database_path) as connection:
        rows = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
    return {str(row[0]) for row in rows}


def test_track1d_required_files_exist() -> None:
    for path in (
        TASK_FILE,
        DOC,
        THIS_TEST,
        STORAGE_MODULE,
        REPOSITORY_MODULE,
        RUNNER_SCRIPT,
        RUNNER_WRAPPER,
    ):
        assert path.is_file(), f"missing Track 1D file: {path}"


def test_track1d_required_canonical_wording_exists_in_doc() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "Track 1D implements the local database/storage runtime for the first usable local product slice.",
            "Track 1D uses SQLite for local-first MVP storage.",
            "Track 1D continues Implementation Track 1 — Backend/API/Database Usable Product Slice.",
            "Track 1D is an explicit local product-slice runtime exception to the earlier Phase 1 Obsidian-only/no-database constraint.",
            "The Track 1D exception is limited to SQLite local-first MVP storage for Implementation Track 1.",
            "The Track 1D exception does not approve production database runtime.",
            "The Track 1D exception does not approve production promotion.",
            "The Track 1D exception does not approve production deployment.",
            "Track 1D does not implement Product or AffiliateOffer full CRUD API.",
            "Track 1D does not implement insight generation.",
            "Track 1D does not implement recommendation runtime.",
            "Track 1D preserves the Phase 7D selected-gate manual boundary.",
            "Selected Runtime Domain: backend/API/database runtime",
            "Implementation Track: Implementation Track 1 — Backend/API/Database Usable Product Slice",
            "Product Goal: first usable local product slice",
            "Runtime Mode: local-only",
            "Storage Runtime: SQLite local-first MVP",
            "Production Promotion Status: not approved",
            "Production Deployment Status: not approved",
            "Production Authentication Status: deferred",
            "RBAC Enforcement Status: deferred",
            "Production Signing Status: deferred",
            "Verifier Runtime Status: deferred",
            "Key Custody Runtime Status: deferred",
            "Phase 7D Boundary Status: preserved",
            "Track 1E is the first approved point for Product Core API implementation, if Track 1D is accepted.",
        ),
        label="canonical wording",
    )


def test_track1d_required_canonical_wording_exists_in_task_file() -> None:
    text = _text(TASK_FILE)
    _assert_all_tokens(
        text,
        (
            "Track 1D implements the local database/storage runtime for the first usable local product slice.",
            "Track 1D uses SQLite for local-first MVP storage.",
            "Track 1D continues Implementation Track 1 — Backend/API/Database Usable Product Slice.",
            "Track 1D is an explicit local product-slice runtime exception to the earlier Phase 1 Obsidian-only/no-database constraint.",
            "The Track 1D exception is limited to SQLite local-first MVP storage for Implementation Track 1.",
            "The Track 1D exception does not approve production database runtime.",
            "The Track 1D exception does not approve production promotion.",
            "The Track 1D exception does not approve production deployment.",
            "Track 1D does not implement Product or AffiliateOffer full CRUD API.",
            "Track 1D does not implement insight generation.",
            "Track 1D does not implement recommendation runtime.",
            "Track 1D preserves the Phase 7D selected-gate manual boundary.",
            "Track 1E is the first approved point for Product Core API implementation, if Track 1D is accepted.",
        ),
        label="task token",
    )


def test_track1d_required_sections_exist() -> None:
    low = _flat(DOC)
    _assert_all_tokens(
        low,
        (
            "track 1d purpose",
            "relationship to track 1a",
            "relationship to track 1b",
            "relationship to track 1c",
            "local database/storage runtime scope",
            "sqlite local-first storage decision",
            "database schema contract",
            "migration/init plan",
            "reset and dev seed plan",
            "repository/data access plan",
            "storage status contract",
            "deferred product crud scope",
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


def test_track1d_required_matrices_exist() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "| Storage Component | Local Implementation | Purpose | Track Introduced | Production Status | Boundary Signal |",
            "| Table | Purpose | Required Columns | Relationship | Seed Behavior | Track Introduced |",
            "| Repository Area | Required Behavior | Allowed Operations | Forbidden Operations | Track Introduced |",
            "| Status Field | Required Value | Purpose | Boundary Signal | Track Introduced |",
            "| Deferred Area | Current Status | Deferred Reason | First Eligible Track | Required Future Approval |",
            "| products |",
            "| affiliate_offers |",
            "| sources |",
            "| collection_runs |",
            "| insights |",
            "| recommendations |",
            "| Product full CRUD API |",
            "| AffiliateOffer full CRUD API |",
            "| CollectionRun workflow API |",
            "| Insight generation |",
            "| Recommendation runtime |",
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
        ),
        label="matrix token",
    )


def test_track1d_implements_sqlite_local_first_storage_and_continues_track1() -> None:
    flat_doc = _flat(DOC)
    assert "track 1d uses sqlite for local-first mvp storage." in flat_doc
    assert "track 1d continues implementation track 1 — backend/api/database usable product slice." in flat_doc


def test_track1d_sqlite_storage_can_initialize_schema(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_init", STORAGE_MODULE)
    database_path = tmp_path / "track1d-init.sqlite3"
    config = storage_module.load_local_storage_config(
        {"AFFILIATE_STORAGE_PATH": str(database_path)}
    )

    result = storage_module.init_storage(config)

    assert result["database_storage_runtime_status"] == "implemented in Track 1D as SQLite local-first MVP"
    assert database_path.is_file()
    assert set(REQUIRED_TABLES).issubset(_table_names(database_path))


def test_track1d_sqlite_storage_can_reset_local_data_safely(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_reset", STORAGE_MODULE)
    database_path = tmp_path / "track1d-reset.sqlite3"
    config = storage_module.load_local_storage_config(
        {"AFFILIATE_STORAGE_PATH": str(database_path)}
    )

    storage_module.init_storage(config)
    storage_module.seed_demo_data(config)
    reset_result = storage_module.reset_storage(config)
    status = storage_module.get_storage_status(config)

    assert reset_result["reset_status"] == "completed"
    assert set(REQUIRED_TABLES).issubset(_table_names(database_path))
    assert status["row_counts"] == {table: 0 for table in REQUIRED_TABLES}


def test_track1d_sqlite_storage_can_seed_deterministic_demo_data(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_seed", STORAGE_MODULE)
    database_path = tmp_path / "track1d-seed.sqlite3"
    config = storage_module.load_local_storage_config(
        {"AFFILIATE_STORAGE_PATH": str(database_path)}
    )

    storage_module.init_storage(config)
    seed_result = storage_module.seed_demo_data(config)
    status = storage_module.get_storage_status(config)

    assert seed_result["seed_status"] == "completed"
    assert seed_result["seeded_tables"] == list(REQUIRED_TABLES)
    assert status["row_counts"] == {table: 1 for table in REQUIRED_TABLES}


def test_track1d_required_tables_exist(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_tables", STORAGE_MODULE)
    database_path = tmp_path / "track1d-tables.sqlite3"
    config = storage_module.load_local_storage_config(
        {"AFFILIATE_STORAGE_PATH": str(database_path)}
    )

    storage_module.init_storage(config)

    table_names = _table_names(database_path)
    for table in REQUIRED_TABLES:
        assert table in table_names, f"missing Track 1D table: {table}"


def test_track1d_required_repository_data_access_smoke_behavior_works(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_repo", STORAGE_MODULE)
    repository_module = _load_module("track1d_repo_smoke", REPOSITORY_MODULE)
    database_path = tmp_path / "track1d-repo.sqlite3"
    config = storage_module.load_local_storage_config(
        {"AFFILIATE_STORAGE_PATH": str(database_path)}
    )

    storage_module.init_storage(config)
    storage_module.seed_demo_data(config)
    repository = repository_module.Track1DRepository.connect(config.database_path)
    try:
        assert repository.table_names() == list(REQUIRED_TABLES)
        product = repository.get_product("demo-product-track1e")
        offers = repository.list_affiliate_offers()
        assert product is not None
        assert product["id"] == "demo-product-track1e"
        assert len(offers) == 1
        assert offers[0]["product_id"] == "demo-product-track1e"
        assert repository.count_rows("products") == 1
        assert repository.count_rows("recommendations") == 1
    finally:
        repository.close()


def test_track1d_runtime_storage_status_reports_sqlite_local_first_mvp(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_status", STORAGE_MODULE)
    database_path = tmp_path / "track1d-status.sqlite3"
    config = storage_module.load_local_storage_config(
        {"AFFILIATE_STORAGE_PATH": str(database_path)}
    )

    storage_module.init_storage(config)
    status = storage_module.get_storage_status(config)

    assert status["database_storage_runtime_status"] == "implemented in Track 1D as SQLite local-first MVP"
    assert status["storage_runtime"] == "SQLite local-first MVP"
    assert status["runtime_mode"] == "local-only"


def test_track1d_runtime_status_endpoint_reports_storage_runtime(tmp_path: Path) -> None:
    storage_module = _load_module("track1d_storage_api_status", STORAGE_MODULE)
    database_path = tmp_path / "track1d-api-status.sqlite3"
    storage_config = storage_module.load_local_storage_config(
        {"AFFILIATE_STORAGE_PATH": str(database_path)}
    )
    storage_module.init_storage(storage_config)

    server, thread, base_url = _start_local_backend(database_path)
    try:
        status, payload = _request_json(f"{base_url}/runtime/status")
    finally:
        _shutdown_local_backend(server, thread)

    assert status == 200
    assert payload["database_storage_runtime_status"] == "implemented in Track 1D as SQLite local-first MVP"
    assert payload["storage_runtime"] == "SQLite local-first MVP"
    assert payload["product_crud_status"] == "implemented in Track 1E"
    assert payload["product_core_api_status"] == "implemented in Track 1E"
    assert payload["product_endpoint_status"] == "implemented in Track 1E"
    assert payload["affiliate_offer_endpoint_status"] == "implemented in Track 1E"
    assert payload["insight_generation_status"] == "not implemented in Track 1E"
    assert payload["recommendation_runtime_status"] == "not implemented in Track 1E"


def test_track1d_product_and_affiliate_offer_full_crud_api_is_not_implemented() -> None:
    text = _text(DOC)
    assert "Track 1D does not implement Product or AffiliateOffer full CRUD API." in text
    assert "POST /products" not in text
    assert "PATCH /products/" not in text
    assert "POST /affiliate-offers" not in text


def test_track1d_insight_generation_is_not_implemented() -> None:
    text = _text(DOC)
    assert "Track 1D does not implement insight generation." in text
    assert "POST /insights/generate" not in text


def test_track1d_recommendation_runtime_is_not_implemented() -> None:
    text = _text(DOC)
    assert "Track 1D does not implement recommendation runtime." in text
    assert "recommendation runtime" in _flat(DOC)


def test_track1d_production_promotion_is_not_approved() -> None:
    text = _text(DOC)
    assert "The Track 1D exception does not approve production promotion." in text
    assert "Production Promotion Status: not approved" in text


def test_track1d_production_deployment_is_not_approved() -> None:
    text = _text(DOC)
    assert "The Track 1D exception does not approve production deployment." in text
    assert "Production Deployment Status: not approved" in text


def test_track1d_auth_rbac_signing_verifier_and_key_custody_remain_deferred() -> None:
    text = _text(DOC)
    _assert_all_tokens(
        text,
        (
            "Production Authentication Status: deferred",
            "RBAC Enforcement Status: deferred",
            "Production Signing Status: deferred",
            "Verifier Runtime Status: deferred",
            "Key Custody Runtime Status: deferred",
        ),
        label="deferred security wording",
    )


def test_track1d_docs_and_state_pointers_reference_track1d() -> None:
    for path in (ROADMAP, PROJECT_STATE, TRACK1C_DOC):
        assert "Track 1D" in _text(path), f"missing Track 1D reference in {path}"


def test_track1d_no_production_database_files_are_introduced() -> None:
    forbidden = (
        REPO_ROOT / "scripts/dev/track1d_postgres_runtime.py",
        REPO_ROOT / "scripts/dev/track1d_aurora_runtime.py",
        REPO_ROOT / "scripts/dev/run_track1d_postgres_runtime.sh",
    )
    for path in forbidden:
        assert not path.exists(), f"unexpected production database file: {path}"


def test_track1d_no_deployment_or_cloud_infrastructure_files_are_introduced() -> None:
    forbidden = (
        REPO_ROOT / "scripts/dev/track1d_deploy.py",
        REPO_ROOT / ".github/workflows/track1d-deploy.yml",
        REPO_ROOT / "infra/track1d",
    )
    for path in forbidden:
        assert not path.exists(), f"unexpected deployment or cloud file: {path}"


def test_track1d_no_production_auth_rbac_signing_verifier_or_key_custody_runtime_files_are_introduced() -> None:
    forbidden = (
        REPO_ROOT / "scripts/dev/track1d_auth_runtime.py",
        REPO_ROOT / "scripts/dev/track1d_rbac_runtime.py",
        REPO_ROOT / "scripts/dev/track1d_signing_runtime.py",
        REPO_ROOT / "scripts/dev/track1d_verifier_runtime.py",
        REPO_ROOT / "scripts/dev/track1d_key_custody_runtime.py",
    )
    for path in forbidden:
        assert not path.exists(), f"unexpected Track 1D security-runtime file: {path}"
