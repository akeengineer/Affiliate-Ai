#!/usr/bin/env python3
from __future__ import annotations

import sqlite3
from pathlib import Path


REQUIRED_TABLES = (
    "products",
    "affiliate_offers",
    "sources",
    "collection_runs",
    "insights",
    "recommendations",
)


class Track1DRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    @classmethod
    def connect(cls, database_path: str | Path) -> "Track1DRepository":
        connection = sqlite3.connect(Path(database_path))
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return cls(connection)

    def close(self) -> None:
        self.connection.close()

    def table_names(self) -> list[str]:
        rows = self.connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        ).fetchall()
        names = [str(row["name"]) for row in rows]
        return [table_name for table_name in REQUIRED_TABLES if table_name in names]

    def count_rows(self, table_name: str) -> int:
        if table_name not in REQUIRED_TABLES:
            raise ValueError(f"Unsupported Track 1D table: {table_name}")
        row = self.connection.execute(f"SELECT COUNT(*) AS count FROM {table_name}").fetchone()
        return int(row["count"])

    def get_product(self, product_id: str) -> dict[str, str] | None:
        row = self.connection.execute(
            """
            SELECT id, name, marketplace, status, created_at, updated_at
            FROM products
            WHERE id = ?
            """,
            (product_id,),
        ).fetchone()
        if row is None:
            return None
        return {str(key): str(row[key]) for key in row.keys()}

    def list_affiliate_offers(self, product_id: str) -> list[dict[str, str]]:
        rows = self.connection.execute(
            """
            SELECT id, product_id, program_name, commission_model, created_at, updated_at
            FROM affiliate_offers
            WHERE product_id = ?
            ORDER BY id
            """,
            (product_id,),
        ).fetchall()
        return [{str(key): str(row[key]) for key in row.keys()} for row in rows]
