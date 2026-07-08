#!/usr/bin/env python3
from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse


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


def _runtime_status_payload(config: Any) -> dict[str, str]:
    return {
        "selected_runtime_domain": config.selected_runtime_domain,
        "runtime_mode": config.runtime_mode,
        "production_promotion_status": "not approved",
        "production_deployment_status": "not approved",
        "production_authentication_status": "deferred",
        "rbac_enforcement_status": "deferred",
        "production_signing_status": "deferred",
        "verifier_runtime_status": "deferred",
        "key_custody_runtime_status": "deferred",
        "phase_7d_boundary_status": "preserved",
        "database_storage_runtime_status": "not implemented in Track 1C",
        "product_crud_status": "not implemented in Track 1C",
        "insight_generation_status": "not implemented in Track 1C",
    }


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")


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
            payload = routes.get(path)
            if payload is None:
                self._send_json(
                    HTTPStatus.NOT_FOUND,
                    {
                        "error": "not_found",
                        "path": path,
                        "runtime_mode": config.runtime_mode,
                    },
                )
                return
            self._send_json(HTTPStatus.OK, payload)

        def log_message(self, format: str, *args: object) -> None:  # noqa: A003 - stdlib signature.
            return

        def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
            body = _json_bytes(payload)
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return Track1CLocalBackendHandler


def create_server(config: Any) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((config.host, config.port), create_handler(config))
    server.daemon_threads = True
    return server
