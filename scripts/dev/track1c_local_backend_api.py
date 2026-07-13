#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from track1f_operator_page import render_operator_page
from track1e_product_core_api import (
    error_response,
    handle_affiliate_offer_create,
    handle_affiliate_offer_list,
    handle_product_create,
    handle_product_get,
    handle_product_list,
    handle_product_patch,
)


def _health_payload(config: Any) -> dict[str, str]:
    return {
        "status": "ok",
        "service": config.service,
        "runtime_mode": config.runtime_mode,
    }


def _version_payload(config: Any) -> dict[str, str]:
    return {
        "service": config.service,
        "version": config.version,
        "implementation_track": config.implementation_track,
        "track": config.track,
    }


def _track1d_storage_status() -> dict[str, str]:
    module_path = Path(__file__).with_name("track1d_local_storage.py")
    if not module_path.is_file():
        return {
            "database_storage_runtime_status": "not implemented in Track 1C",
            "storage_runtime": "unavailable",
        }

    spec = importlib.util.spec_from_file_location("track1d_local_storage_for_track1c", module_path)
    if spec is None or spec.loader is None:
        return {
            "database_storage_runtime_status": "not implemented in Track 1C",
            "storage_runtime": "unavailable",
        }

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    config = module.load_local_storage_config()
    status = module.get_storage_status(config)
    return {
        "database_storage_runtime_status": str(status["database_storage_runtime_status"]),
        "storage_runtime": str(status["storage_runtime"]),
    }


def _runtime_status_payload(config: Any) -> dict[str, str]:
    storage_status = _track1d_storage_status()
    return {
        "selected_runtime_domain": config.selected_runtime_domain,
        "runtime_mode": config.runtime_mode,
        "production_frontend_deployment_status": "not approved",
        "production_promotion_status": "not approved",
        "production_deployment_status": "not approved",
        "production_authentication_status": "deferred",
        "rbac_enforcement_status": "deferred",
        "production_signing_status": "deferred",
        "verifier_runtime_status": "deferred",
        "key_custody_runtime_status": "deferred",
        "phase_7d_boundary_status": "preserved",
        "database_storage_runtime_status": storage_status["database_storage_runtime_status"],
        "storage_runtime": storage_status["storage_runtime"],
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


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")


def _product_id_from_path(path: str) -> str | None:
    prefix = "/products/"
    if not path.startswith(prefix):
        return None
    product_id = path[len(prefix) :]
    if not product_id or "/" in product_id:
        return None
    return product_id


def _known_route(path: str) -> bool:
    return path in {"/health", "/version", "/runtime/status", "/operator", "/products", "/affiliate-offers"} or _product_id_from_path(path) is not None


def create_handler(config: Any) -> type[BaseHTTPRequestHandler]:
    routes = {
        "/health": _health_payload(config),
        "/version": _version_payload(config),
        "/runtime/status": _runtime_status_payload(config),
    }

    class Track1CLocalBackendHandler(BaseHTTPRequestHandler):
        server_version = "affiliate-ai-backend"
        sys_version = ""

        def do_GET(self) -> None:  # noqa: N802 - stdlib handler naming.
            path = urlparse(self.path).path
            if path in routes:
                self._send_json(HTTPStatus.OK, routes[path])
                return
            if path == "/operator":
                self._send_html(HTTPStatus.OK, render_operator_page())
                return
            if path == "/products":
                self._send_handler_result(handle_product_list())
                return
            if path == "/affiliate-offers":
                self._send_handler_result(handle_affiliate_offer_list())
                return
            product_id = _product_id_from_path(path)
            if product_id is not None:
                self._send_handler_result(handle_product_get(product_id))
                return
            self._send_handler_result(error_response(404, "not_found", f"Route not found: {path}"))

        def do_POST(self) -> None:  # noqa: N802 - stdlib handler naming.
            path = urlparse(self.path).path
            if path == "/products":
                self._send_handler_result(handle_product_create(self._read_body()))
                return
            if path == "/affiliate-offers":
                self._send_handler_result(handle_affiliate_offer_create(self._read_body()))
                return
            if _known_route(path):
                self._send_handler_result(error_response(405, "method_not_allowed", f"Method POST is not allowed for {path}"))
                return
            self._send_handler_result(error_response(404, "not_found", f"Route not found: {path}"))

        def do_PATCH(self) -> None:  # noqa: N802 - stdlib handler naming.
            path = urlparse(self.path).path
            product_id = _product_id_from_path(path)
            if product_id is not None:
                self._send_handler_result(handle_product_patch(product_id, self._read_body()))
                return
            if _known_route(path):
                self._send_handler_result(error_response(405, "method_not_allowed", f"Method PATCH is not allowed for {path}"))
                return
            self._send_handler_result(error_response(404, "not_found", f"Route not found: {path}"))

        def do_DELETE(self) -> None:  # noqa: N802 - stdlib handler naming.
            path = urlparse(self.path).path
            if _known_route(path):
                self._send_handler_result(error_response(405, "method_not_allowed", f"Method DELETE is not allowed for {path}"))
                return
            self._send_handler_result(error_response(404, "not_found", f"Route not found: {path}"))

        def log_message(self, format: str, *args: object) -> None:  # noqa: A003 - stdlib signature.
            return

        def _read_body(self) -> bytes:
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                length = 0
            if length <= 0:
                return b""
            return self.rfile.read(length)

        def _send_handler_result(self, result: tuple[int, dict[str, object]]) -> None:
            status_code, payload = result
            self._send_json(HTTPStatus(status_code), payload)

        def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
            body = _json_bytes(payload)
            self._send_bytes(status, "application/json; charset=utf-8", body)

        def _send_html(self, status: HTTPStatus, body_text: str) -> None:
            body = body_text.encode("utf-8")
            self._send_bytes(status, "text/html; charset=utf-8", body)

        def _send_bytes(self, status: HTTPStatus, content_type: str, body: bytes) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return Track1CLocalBackendHandler


def create_server(config: Any) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((config.host, config.port), create_handler(config))
    server.daemon_threads = True
    return server
