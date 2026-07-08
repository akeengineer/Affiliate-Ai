#!/usr/bin/env python3
from __future__ import annotations

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

DEMO_PRODUCT_ID = "demo-product-track1d"
DEMO_TIMESTAMP = "2026-07-08T00:00:00Z"


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


def _schema_statements() -> tuple[str, ...]:
    return (
        """
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            marketplace TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS affiliate_offers (
            id TEXT PRIMARY KEY,
            product_id TEXT NOT NULL,
            program_name TEXT NOT NULL,
            commission_model TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
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
                "Track 1D Demo Product",
                "local-demo-marketplace",
                "draft",
                DEMO_TIMESTAMP,
                DEMO_TIMESTAMP,
            ),
        ),
        "affiliate_offers": (
            (
                "demo-offer-track1d",
                DEMO_PRODUCT_ID,
                "Track 1D Demo Program",
                "flat_rate",
                DEMO_TIMESTAMP,
                DEMO_TIMESTAMP,
            ),
        ),
        "sources": (
            (
                "demo-source-track1d",
                DEMO_PRODUCT_ID,
                "operator_input",
                "vault/samples/products/smart-desk-pad.md",
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
                "Deterministic Track 1D demo insight.",
                DEMO_TIMESTAMP,
            ),
        ),
        "recommendations": (
            (
                "demo-recommendation-track1d",
                DEMO_PRODUCT_ID,
                "review",
                "Deterministic Track 1D demo recommendation.",
                DEMO_TIMESTAMP,
            ),
        ),
    }


def init_storage(config: LocalStorageConfig) -> dict[str, object]:
    with _connect(config.database_path) as connection:
        for statement in _schema_statements():
            connection.execute(statement)
        connection.commit()
    status = get_storage_status(config)
    status["init_status"] = "completed"
    return status


def reset_storage(config: LocalStorageConfig) -> dict[str, object]:
    if config.database_path.exists():
        config.database_path.unlink()
    status = init_storage(config)
    status["reset_status"] = "completed"
    return status


def seed_demo_data(config: LocalStorageConfig) -> dict[str, object]:
    init_storage(config)
    rows = _demo_rows()
    with _connect(config.database_path) as connection:
        # Clear dependent tables first so seed is deterministic on repeat runs.
        for table_name in ("recommendations", "insights", "collection_runs", "sources", "affiliate_offers", "products"):
            connection.execute(f"DELETE FROM {table_name}")
        connection.executemany(
            """
            INSERT INTO products (id, name, marketplace, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            rows["products"],
        )
        connection.executemany(
            """
            INSERT INTO affiliate_offers (
                id, product_id, program_name, commission_model, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            rows["affiliate_offers"],
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


def get_storage_status(config: LocalStorageConfig) -> dict[str, object]:
    if not config.database_path.exists():
        return {
            "database_storage_runtime_status": "implemented in Track 1D as SQLite local-first MVP",
            "storage_runtime": config.storage_runtime,
            "runtime_mode": config.runtime_mode,
            "database_path": str(config.database_path),
            "schema_initialized": False,
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
            "tables": table_names,
            "row_counts": _row_counts(connection),
        }
