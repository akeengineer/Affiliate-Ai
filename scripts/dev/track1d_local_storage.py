#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Mapping


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_PATH = REPO_ROOT / "tmp" / "track1d-local-storage" / "track1d.sqlite3"
REQUIRED_TABLES = (
    "products",
    "affiliate_offers",
    "sources",
    "collection_runs",
    "insights",
    "recommendations",
)

TRACK1E_PRODUCT_COLUMNS = (
    "id",
    "name",
    "category",
    "description",
    "status",
    "metadata",
    "created_at",
    "updated_at",
)
TRACK1E_AFFILIATE_OFFER_COLUMNS = (
    "id",
    "product_id",
    "source_id",
    "title",
    "offer_url",
    "price",
    "currency",
    "commission_rate",
    "status",
    "metadata",
    "created_at",
    "updated_at",
)

DEMO_PRODUCT_ID = "demo-product-track1e"
DEMO_SOURCE_ID = "demo-source-track1d"
DEMO_AFFILIATE_OFFER_ID = "demo-affiliate-offer-track1e"
DEMO_TIMESTAMP = "2026-07-13T00:00:00Z"


class LocalStorageConfig:
    __slots__ = ("database_path", "runtime_mode", "storage_runtime")

    def __init__(self, *, database_path: Path, runtime_mode: str, storage_runtime: str) -> None:
        self.database_path = database_path
        self.runtime_mode = runtime_mode
        self.storage_runtime = storage_runtime


def _normalize_database_path(value: str | os.PathLike[str] | None) -> Path:
    if value in (None, ""):
        return DEFAULT_DATABASE_PATH
    return Path(value).expanduser()


def load_local_storage_config(
    env: Mapping[str, str] | None = None,
    *,
    database_path_override: str | None = None,
) -> LocalStorageConfig:
    source = os.environ if env is None else env
    database_path = _normalize_database_path(
        database_path_override if database_path_override is not None else source.get("AFFILIATE_STORAGE_PATH")
    )
    return LocalStorageConfig(
        database_path=database_path,
        runtime_mode="local-only",
        storage_runtime="SQLite local-first MVP",
    )


def _connect(database_path: Path) -> sqlite3.Connection:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _json_text(value: object) -> str:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=True)


def _table_names(connection: sqlite3.Connection) -> list[str]:
    rows = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    ).fetchall()
    return [str(row["name"]) for row in rows]


def _table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
    return table_name in set(_table_names(connection))


def _table_columns(connection: sqlite3.Connection, table_name: str) -> list[str]:
    rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    return [str(row["name"]) for row in rows]


def _schema_statements_track1e() -> tuple[str, ...]:
    return (
        """
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS sources (
            id TEXT PRIMARY KEY,
            product_id TEXT NOT NULL,
            source_type TEXT NOT NULL,
            source_ref TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS affiliate_offers (
            id TEXT PRIMARY KEY,
            product_id TEXT NOT NULL,
            source_id TEXT NOT NULL,
            title TEXT NOT NULL,
            offer_url TEXT NOT NULL,
            price REAL,
            currency TEXT NOT NULL,
            commission_rate REAL,
            status TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE,
            FOREIGN KEY(source_id) REFERENCES sources(id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS collection_runs (
            id TEXT PRIMARY KEY,
            product_id TEXT NOT NULL,
            status TEXT NOT NULL,
            started_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS insights (
            id TEXT PRIMARY KEY,
            product_id TEXT NOT NULL,
            insight_type TEXT NOT NULL,
            summary TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS recommendations (
            id TEXT PRIMARY KEY,
            product_id TEXT NOT NULL,
            recommendation_type TEXT NOT NULL,
            reason TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
        )
        """,
    )


def _ensure_source_for_product(connection: sqlite3.Connection, product_id: str) -> str:
    row = connection.execute(
        """
        SELECT id
        FROM sources
        WHERE product_id = ?
        ORDER BY id
        LIMIT 1
        """,
        (product_id,),
    ).fetchone()
    if row is not None:
        return str(row["id"])

    source_id = f"migrated-source-{product_id}"
    connection.execute(
        """
        INSERT INTO sources (id, product_id, source_type, source_ref, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (source_id, product_id, "schema_evolution", "track1d-schema-evolution", DEMO_TIMESTAMP),
    )
    return source_id


def _rebuild_products_table(connection: sqlite3.Connection) -> None:
    old_columns = _table_columns(connection, "products")
    if tuple(old_columns) == TRACK1E_PRODUCT_COLUMNS:
        return

    connection.execute(
        """
        CREATE TABLE products__track1e_new (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    if old_columns:
        rows = connection.execute("SELECT * FROM products ORDER BY id").fetchall()
        for row in rows:
            mapping = {str(key): row[key] for key in row.keys()}
            category = str(mapping.get("category") or mapping.get("marketplace") or "uncategorized")
            description = str(mapping.get("description") or "")
            status = str(mapping.get("status") or "active")
            metadata_raw = mapping.get("metadata")
            metadata = metadata_raw if isinstance(metadata_raw, str) and metadata_raw else _json_text({})
            connection.execute(
                """
                INSERT INTO products__track1e_new (
                    id, name, category, description, status, metadata, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(mapping["id"]),
                    str(mapping["name"]),
                    category,
                    description,
                    status,
                    metadata,
                    str(mapping["created_at"]),
                    str(mapping["updated_at"]),
                ),
            )
    connection.execute("DROP TABLE products")
    connection.execute("ALTER TABLE products__track1e_new RENAME TO products")


def _rebuild_affiliate_offers_table(connection: sqlite3.Connection) -> None:
    old_columns = _table_columns(connection, "affiliate_offers")
    if tuple(old_columns) == TRACK1E_AFFILIATE_OFFER_COLUMNS:
        return

    connection.execute(
        """
        CREATE TABLE affiliate_offers__track1e_new (
            id TEXT PRIMARY KEY,
            product_id TEXT NOT NULL,
            source_id TEXT NOT NULL,
            title TEXT NOT NULL,
            offer_url TEXT NOT NULL,
            price REAL,
            currency TEXT NOT NULL,
            commission_rate REAL,
            status TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE,
            FOREIGN KEY(source_id) REFERENCES sources(id) ON DELETE CASCADE
        )
        """
    )
    if old_columns:
        rows = connection.execute("SELECT * FROM affiliate_offers ORDER BY id").fetchall()
        for row in rows:
            mapping = {str(key): row[key] for key in row.keys()}
            product_id = str(mapping["product_id"])
            source_id = str(mapping.get("source_id") or _ensure_source_for_product(connection, product_id))
            title = str(mapping.get("title") or mapping.get("program_name") or "")
            offer_url = str(mapping.get("offer_url") or f"https://example.invalid/track1d-offer/{mapping['id']}")
            currency = str(mapping.get("currency") or "")
            status = str(mapping.get("status") or "active")
            metadata_raw = mapping.get("metadata")
            if isinstance(metadata_raw, str) and metadata_raw:
                metadata = metadata_raw
            else:
                legacy_commission_model = mapping.get("commission_model")
                metadata = _json_text(
                    {"legacy_commission_model": str(legacy_commission_model)}
                    if legacy_commission_model not in (None, "")
                    else {}
                )
            connection.execute(
                """
                INSERT INTO affiliate_offers__track1e_new (
                    id, product_id, source_id, title, offer_url, price, currency,
                    commission_rate, status, metadata, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(mapping["id"]),
                    product_id,
                    source_id,
                    title,
                    offer_url,
                    mapping.get("price"),
                    currency,
                    mapping.get("commission_rate"),
                    status,
                    metadata,
                    str(mapping["created_at"]),
                    str(mapping["updated_at"]),
                ),
            )
    connection.execute("DROP TABLE affiliate_offers")
    connection.execute("ALTER TABLE affiliate_offers__track1e_new RENAME TO affiliate_offers")


def _ensure_support_tables(connection: sqlite3.Connection) -> None:
    for statement in _schema_statements_track1e():
        table_name = statement.split()[5]
        if table_name in ("products", "affiliate_offers"):
            continue
        connection.execute(statement)


def ensure_track1e_schema(config: LocalStorageConfig) -> dict[str, object]:
    with _connect(config.database_path) as connection:
        if not _table_exists(connection, "products"):
            connection.execute(_schema_statements_track1e()[0])
        else:
            _rebuild_products_table(connection)

        _ensure_support_tables(connection)

        if not _table_exists(connection, "affiliate_offers"):
            connection.execute(_schema_statements_track1e()[2])
        else:
            _rebuild_affiliate_offers_table(connection)

        connection.commit()
    status = get_storage_status(config)
    status["schema_version"] = "track1e"
    return status


def _row_counts(connection: sqlite3.Connection) -> dict[str, int]:
    names = set(_table_names(connection))
    counts: dict[str, int] = {}
    for table_name in REQUIRED_TABLES:
        if table_name not in names:
            counts[table_name] = 0
            continue
        counts[table_name] = int(
            connection.execute(f"SELECT COUNT(*) AS count FROM {table_name}").fetchone()["count"]
        )
    return counts


def _demo_rows() -> dict[str, tuple[tuple[object, ...], ...]]:
    return {
        "products": (
            (
                DEMO_PRODUCT_ID,
                "Track 1E Demo Product",
                "productivity",
                "",
                "active",
                _json_text({}),
                DEMO_TIMESTAMP,
                DEMO_TIMESTAMP,
            ),
        ),
        "sources": (
            (
                DEMO_SOURCE_ID,
                DEMO_PRODUCT_ID,
                "operator_input",
                "vault/samples/products/smart-desk-pad.md",
                DEMO_TIMESTAMP,
            ),
        ),
        "affiliate_offers": (
            (
                DEMO_AFFILIATE_OFFER_ID,
                DEMO_PRODUCT_ID,
                DEMO_SOURCE_ID,
                "Track 1E Demo Offer",
                "https://example.com/demo-offer-track1e",
                19.99,
                "USD",
                12.5,
                "active",
                _json_text({}),
                DEMO_TIMESTAMP,
                DEMO_TIMESTAMP,
            ),
        ),
        "collection_runs": (
            (
                "demo-collection-run-track1d",
                DEMO_PRODUCT_ID,
                "completed",
                DEMO_TIMESTAMP,
                DEMO_TIMESTAMP,
            ),
        ),
        "insights": (
            (
                "demo-insight-track1d",
                DEMO_PRODUCT_ID,
                "product_summary",
                "Deterministic Track 1E demo insight placeholder.",
                DEMO_TIMESTAMP,
            ),
        ),
        "recommendations": (
            (
                "demo-recommendation-track1d",
                DEMO_PRODUCT_ID,
                "review",
                "Deterministic Track 1E demo recommendation placeholder.",
                DEMO_TIMESTAMP,
            ),
        ),
    }


def init_storage(config: LocalStorageConfig) -> dict[str, object]:
    status = ensure_track1e_schema(config)
    status["init_status"] = "completed"
    return status


def reset_storage(config: LocalStorageConfig) -> dict[str, object]:
    if config.database_path.exists():
        config.database_path.unlink()
    status = ensure_track1e_schema(config)
    status["reset_status"] = "completed"
    return status


def seed_demo_data(config: LocalStorageConfig) -> dict[str, object]:
    ensure_track1e_schema(config)
    rows = _demo_rows()
    with _connect(config.database_path) as connection:
        for table_name in ("recommendations", "insights", "collection_runs", "affiliate_offers", "sources", "products"):
            connection.execute(f"DELETE FROM {table_name}")
        connection.executemany(
            """
            INSERT INTO products (
                id, name, category, description, status, metadata, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows["products"],
        )
        connection.executemany(
            """
            INSERT INTO sources (id, product_id, source_type, source_ref, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            rows["sources"],
        )
        connection.executemany(
            """
            INSERT INTO affiliate_offers (
                id, product_id, source_id, title, offer_url, price, currency,
                commission_rate, status, metadata, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows["affiliate_offers"],
        )
        connection.executemany(
            """
            INSERT INTO collection_runs (id, product_id, status, started_at, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            rows["collection_runs"],
        )
        connection.executemany(
            """
            INSERT INTO insights (id, product_id, insight_type, summary, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            rows["insights"],
        )
        connection.executemany(
            """
            INSERT INTO recommendations (
                id, product_id, recommendation_type, reason, created_at
            ) VALUES (?, ?, ?, ?, ?)
            """,
            rows["recommendations"],
        )
        connection.commit()
    status = get_storage_status(config)
    status["seed_status"] = "completed"
    status["seeded_tables"] = list(REQUIRED_TABLES)
    return status


def _schema_version(connection: sqlite3.Connection) -> str:
    if not _table_exists(connection, "products") or not _table_exists(connection, "affiliate_offers"):
        return "track1e"
    product_columns = tuple(_table_columns(connection, "products"))
    offer_columns = tuple(_table_columns(connection, "affiliate_offers"))
    if product_columns == TRACK1E_PRODUCT_COLUMNS and offer_columns == TRACK1E_AFFILIATE_OFFER_COLUMNS:
        return "track1e"
    return "track1d"


def get_storage_status(config: LocalStorageConfig) -> dict[str, object]:
    if not config.database_path.exists():
        return {
            "database_storage_runtime_status": "implemented in Track 1D as SQLite local-first MVP",
            "storage_runtime": config.storage_runtime,
            "runtime_mode": config.runtime_mode,
            "database_path": str(config.database_path),
            "schema_initialized": False,
            "schema_version": "track1e",
            "tables": [],
            "row_counts": {table_name: 0 for table_name in REQUIRED_TABLES},
        }

    with _connect(config.database_path) as connection:
        table_names = _table_names(connection)
        return {
            "database_storage_runtime_status": "implemented in Track 1D as SQLite local-first MVP",
            "storage_runtime": config.storage_runtime,
            "runtime_mode": config.runtime_mode,
            "database_path": str(config.database_path),
            "schema_initialized": set(REQUIRED_TABLES).issubset(set(table_names)),
            "schema_version": _schema_version(connection),
            "tables": table_names,
            "row_counts": _row_counts(connection),
        }
