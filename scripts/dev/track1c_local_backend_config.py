#!/usr/bin/env python3
from __future__ import annotations

import os
from typing import Mapping


LOCAL_ONLY_HOSTS = {"127.0.0.1", "localhost"}


class LocalBackendConfig:
    __slots__ = (
        "host",
        "port",
        "service",
        "version",
        "track",
        "implementation_track",
        "selected_runtime_domain",
        "runtime_mode",
    )

    def __init__(
        self,
        *,
        host: str,
        port: int,
        service: str,
        version: str,
        track: str,
        implementation_track: str,
        selected_runtime_domain: str,
        runtime_mode: str,
    ) -> None:
        self.host = host
        self.port = port
        self.service = service
        self.version = version
        self.track = track
        self.implementation_track = implementation_track
        self.selected_runtime_domain = selected_runtime_domain
        self.runtime_mode = runtime_mode


def _normalize_host(value: str | None) -> str:
    host = (value or "127.0.0.1").strip() or "127.0.0.1"
    if host not in LOCAL_ONLY_HOSTS:
        raise ValueError(f"Track 1C is local-only and does not allow host: {host}")
    return host


def _normalize_port(value: str | int | None) -> int:
    raw = 8001 if value in (None, "") else value
    try:
        port = int(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid Track 1C port: {raw}") from exc
    if port < 0 or port > 65535:
        raise ValueError(f"Track 1C port must be between 0 and 65535: {port}")
    return port


def load_local_backend_config(
    env: Mapping[str, str] | None = None,
    *,
    host_override: str | None = None,
    port_override: int | None = None,
) -> LocalBackendConfig:
    source = os.environ if env is None else env
    host = _normalize_host(host_override if host_override is not None else source.get("AFFILIATE_BACKEND_HOST"))
    port = _normalize_port(port_override if port_override is not None else source.get("AFFILIATE_BACKEND_PORT"))
    return LocalBackendConfig(
        host=host,
        port=port,
        service="affiliate-ai-backend",
        version="local-dev",
        track="Track 1C",
        implementation_track="Implementation Track 1 — Backend/API/Database Usable Product Slice",
        selected_runtime_domain="backend/API/database runtime",
        runtime_mode="local-only",
    )
