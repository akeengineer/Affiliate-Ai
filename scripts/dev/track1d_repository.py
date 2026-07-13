#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


REQUIRED_TABLES = (
    "products",
    "affiliate_offers",
    "sources",
    "collection_runs",
    "insights",
    "recommendations",
)


def _decode_metadata(value: Any) -> dict[str, object]:
    if isinstance(value, str) and value:
        return json.loads(value)
    return {}


def _row_to_product(row: sqlite3.Row) -> dict[str, object]:
    return {
        "id": str(row["id"]),
        "name": str(row["name"]),
        "category": str(row["category"]),
        "description": str(row["description"]),
        "status": str(row["status"]),
        "metadata": _decode_metadata(row["metadata"]),
        "created_at": str(row["created_at"]),
        "updated_at": str(row["updated_at"]),
    }


def _row_to_affiliate_offer(row: sqlite3.Row) -> dict[str, object]:
    return {
        "id": str(row["id"]),
        "product_id": str(row["product_id"]),
        "source_id": str(row["source_id"]),
        "title": str(row["title"]),
        "offer_url": str(row["offer_url"]),
        "price": row["price"],
        "currency": str(row["currency"]),
        "commission_rate": row["commission_rate"],
        "status": str(row["status"]),
        "metadata": _decode_metadata(row["metadata"]),
        "created_at": str(row["created_at"]),
        "updated_at": str(row["updated_at"]),
    }


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

    def _next_id(self, prefix: str, table_name: str) -> str:
        return f"{prefix}-{self.count_rows(table_name) + 1:04d}"

    def create_product(self, data: dict[str, object]) -> dict[str, object]:
        self.connection.execute(
            """
            INSERT INTO products (
                id, name, category, description, status, metadata, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["id"],
                data["name"],
                data["category"],
                data["description"],
                data["status"],
                json.dumps(data["metadata"], separators=(",", ":"), ensure_ascii=True),
                data["created_at"],
                data["updated_at"],
            ),
        )
        self.connection.commit()
        row = self.connection.execute(
            "SELECT * FROM products WHERE id = ?",
            (data["id"],),
        ).fetchone()
        assert row is not None
        return _row_to_product(row)

    def list_products(self) -> list[dict[str, object]]:
        rows = self.connection.execute(
            """
            SELECT *
            FROM products
            ORDER BY created_at, id
            """
        ).fetchall()
        return [_row_to_product(row) for row in rows]

    def get_product(self, product_id: str) -> dict[str, object] | None:
        row = self.connection.execute(
            """
            SELECT *
            FROM products
            WHERE id = ?
            """,
            (product_id,),
        ).fetchone()
        if row is None:
            return None
        return _row_to_product(row)

    def update_product(self, product_id: str, fields: dict[str, object]) -> dict[str, object] | None:
        if not fields:
            return self.get_product(product_id)
        assignments = ", ".join(f"{column} = ?" for column in fields)
        values = []
        for value in fields.values():
            if isinstance(value, dict):
                values.append(json.dumps(value, separators=(",", ":"), ensure_ascii=True))
            else:
                values.append(value)
        values.append(product_id)
        cursor = self.connection.execute(
            f"UPDATE products SET {assignments} WHERE id = ?",
            tuple(values),
        )
        self.connection.commit()
        if cursor.rowcount == 0:
            return None
        return self.get_product(product_id)

    def product_exists(self, product_id: str) -> bool:
        row = self.connection.execute(
            "SELECT 1 AS found FROM products WHERE id = ? LIMIT 1",
            (product_id,),
        ).fetchone()
        return row is not None

    def source_exists(self, source_id: str) -> bool:
        row = self.connection.execute(
            "SELECT 1 AS found FROM sources WHERE id = ? LIMIT 1",
            (source_id,),
        ).fetchone()
        return row is not None

    def create_affiliate_offer(self, data: dict[str, object]) -> dict[str, object]:
        self.connection.execute(
            """
            INSERT INTO affiliate_offers (
                id, product_id, source_id, title, offer_url, price, currency,
                commission_rate, status, metadata, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["id"],
                data["product_id"],
                data["source_id"],
                data["title"],
                data["offer_url"],
                data["price"],
                data["currency"],
                data["commission_rate"],
                data["status"],
                json.dumps(data["metadata"], separators=(",", ":"), ensure_ascii=True),
                data["created_at"],
                data["updated_at"],
            ),
        )
        self.connection.commit()
        row = self.connection.execute(
            "SELECT * FROM affiliate_offers WHERE id = ?",
            (data["id"],),
        ).fetchone()
        assert row is not None
        return _row_to_affiliate_offer(row)

    def list_affiliate_offers(self) -> list[dict[str, object]]:
        rows = self.connection.execute(
            """
            SELECT *
            FROM affiliate_offers
            ORDER BY created_at, id
            """
        ).fetchall()
        return [_row_to_affiliate_offer(row) for row in rows]

    # Small helper methods for Track 1E creation flows.
    def next_product_id(self) -> str:
        return self._next_id("product", "products")

    def next_affiliate_offer_id(self) -> str:
        return self._next_id("affiliate-offer", "affiliate_offers")
