#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from track1d_local_storage import load_local_storage_config, reset_storage, seed_demo_data
from track1e_product_core_api import (
    handle_affiliate_offer_create,
    handle_affiliate_offer_list,
    handle_product_create,
    handle_product_list,
)
from track1f_operator_page import render_operator_page


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_PATH = REPO_ROOT / "tmp" / "track1g-demo-pack" / "track1g-demo.sqlite3"
DEFAULT_OUTPUT_PATH = REPO_ROOT / "tmp" / "track1g-demo-pack" / "summary.json"

DEMO_PRODUCT_PAYLOAD = {
    "name": "Track 1G Demo Product",
    "category": "productivity",
    "description": "Created by the deterministic Track 1G demo pack.",
    "metadata": {"track": "1G", "demo": True},
}
DEMO_AFFILIATE_OFFER_PAYLOAD = {
    "product_id": "demo-product-track1e",
    "source_id": "demo-source-track1d",
    "offer_url": "https://example.com/track1g-demo-offer",
    "title": "Track 1G Demo Offer",
    "price": 29.99,
    "currency": "USD",
    "commission_rate": 10.0,
    "metadata": {"track": "1G", "demo": True},
}


def _json_bytes(payload: dict[str, object]) -> bytes:
    return json.dumps(payload, separators=(",", ":"), ensure_ascii=True, sort_keys=True).encode("utf-8")


def _call_handler(result: tuple[int, dict[str, object]], *, expected_status: int) -> dict[str, object]:
    status_code, payload = result
    if status_code != expected_status:
        raise RuntimeError(json.dumps(payload, separators=(",", ":"), ensure_ascii=True, sort_keys=True))
    return payload


def _runtime_status() -> dict[str, object]:
    return {
        "runtime_mode": "local-only",
        "storage_runtime": "SQLite local-first MVP",
        "product_core_api_status": "implemented in Track 1E",
        "minimal_operator_flow_status": "implemented in Track 1F",
        "end_to_end_demo_pack_status": "implemented in Track 1G",
        "demo_workflow_status": "implemented in Track 1G",
        "production_demo_deployment_status": "not approved",
    }


def _verify_operator_surface() -> str:
    html = render_operator_page()
    required = "Track 1F provides a local-only operator flow"
    if required not in html:
        raise RuntimeError("Track 1F operator surface is unavailable.")
    return "available"


def run_demo(
    *,
    database_path: str | None = None,
    output_path: str | None = None,
) -> dict[str, object]:
    resolved_database_path = Path(database_path) if database_path else DEFAULT_DATABASE_PATH
    resolved_output_path = Path(output_path) if output_path else DEFAULT_OUTPUT_PATH

    config = load_local_storage_config(database_path_override=str(resolved_database_path))
    reset_storage(config)
    seed_demo_data(config)

    runtime_status = _runtime_status()
    operator_surface_status = _verify_operator_surface()

    created_product = _call_handler(
        handle_product_create(_json_bytes(DEMO_PRODUCT_PAYLOAD), database_path=str(resolved_database_path)),
        expected_status=200,
    )
    product_list = _call_handler(
        handle_product_list(database_path=str(resolved_database_path)),
        expected_status=200,
    )

    created_offer = _call_handler(
        handle_affiliate_offer_create(
            _json_bytes(DEMO_AFFILIATE_OFFER_PAYLOAD),
            database_path=str(resolved_database_path),
        ),
        expected_status=200,
    )
    offer_list = _call_handler(
        handle_affiliate_offer_list(database_path=str(resolved_database_path)),
        expected_status=200,
    )

    summary: dict[str, object] = {
        "demo_status": "ok",
        "runtime_mode": runtime_status["runtime_mode"],
        "storage_runtime": runtime_status["storage_runtime"],
        "product_core_api_status": runtime_status["product_core_api_status"],
        "minimal_operator_flow_status": runtime_status["minimal_operator_flow_status"],
        "end_to_end_demo_pack_status": runtime_status["end_to_end_demo_pack_status"],
        "demo_workflow_status": runtime_status["demo_workflow_status"],
        "production_demo_deployment_status": runtime_status["production_demo_deployment_status"],
        "operator_surface_status": operator_surface_status,
        "created_product_id": str(created_product["id"]),
        "created_affiliate_offer_id": str(created_offer["id"]),
        "demo_product_count": int(product_list["count"]),
        "demo_affiliate_offer_count": int(offer_list["count"]),
        "database_path": str(resolved_database_path),
        "output_path": str(resolved_output_path),
    }

    resolved_output_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_output_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Track 1G end-to-end local demo pack.")
    parser.add_argument("--database-path", help="Local SQLite demo database path.")
    parser.add_argument("--output-path", help="Deterministic JSON summary output path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        summary = run_demo(database_path=args.database_path, output_path=args.output_path)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(summary, separators=(",", ":"), ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
