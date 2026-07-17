#!/usr/bin/env python3
"""Marketplace adapter interface and Phase 7 configuration skeletons.

Lazada and TikTok Shop deliberately expose no network implementation. Future
connectors can implement the interface only after an explicitly scoped task.

Ref: codex/tasks/104-phase7-enhancement.md
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

import yaml


DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.yaml")


class MarketplaceConfigurationError(ValueError):
    """Raised when marketplace selection or adapter configuration is invalid."""


@dataclass(frozen=True)
class MarketplaceConfig:
    name: str
    enabled: bool
    base_url: str
    country: str
    currency: str
    status: str
    options: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, name: str, data: Mapping[str, Any]) -> "MarketplaceConfig":
        required = ("enabled", "base_url", "country", "currency", "status")
        missing = [field_name for field_name in required if field_name not in data]
        if missing:
            raise MarketplaceConfigurationError(
                f"Marketplace {name!r} is missing config fields: {', '.join(missing)}"
            )
        if not isinstance(data["enabled"], bool):
            raise MarketplaceConfigurationError(f"Marketplace {name!r} enabled must be boolean")
        return cls(
            name=name,
            enabled=data["enabled"],
            base_url=str(data["base_url"]),
            country=str(data["country"]),
            currency=str(data["currency"]),
            status=str(data["status"]),
            options={key: value for key, value in data.items() if key not in required},
        )


class MarketplaceAdapter(ABC):
    """Contract for marketplace discovery and normalization implementations."""

    marketplace_name: str

    def __init__(self, config: MarketplaceConfig) -> None:
        if config.name != self.marketplace_name:
            raise MarketplaceConfigurationError(
                f"{self.__class__.__name__} requires {self.marketplace_name!r} config"
            )
        self.config = config

    @abstractmethod
    def search_products(self, keyword: str, limit: int = 30) -> list[dict[str, Any]]:
        """Return raw marketplace products for a keyword."""

    @abstractmethod
    def normalize_product(self, raw_product: Mapping[str, Any]) -> dict[str, Any]:
        """Normalize a raw marketplace product for candidate transformation."""


class ShopeeAdapter(MarketplaceAdapter):
    """Boundary adapter for the existing Shopee scraper implementation."""

    marketplace_name = "shopee"

    def search_products(self, keyword: str, limit: int = 30) -> list[dict[str, Any]]:
        raise NotImplementedError(
            "Shopee discovery remains in scripts/shopee/scraper.py; no adapter bridge is implemented"
        )

    def normalize_product(self, raw_product: Mapping[str, Any]) -> dict[str, Any]:
        normalized = dict(raw_product)
        normalized.setdefault("marketplace", "Shopee")
        normalized.setdefault("currency", self.config.currency)
        return normalized


class LazadaAdapter(MarketplaceAdapter):
    """Phase 7 Lazada configuration skeleton; no API or scraper calls."""

    marketplace_name = "lazada"

    def search_products(self, keyword: str, limit: int = 30) -> list[dict[str, Any]]:
        raise NotImplementedError("Lazada adapter is a Phase 7 skeleton (configuration only)")

    def normalize_product(self, raw_product: Mapping[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Lazada normalization is not implemented")


class TikTokShopAdapter(MarketplaceAdapter):
    """Phase 7 TikTok Shop configuration skeleton; no API or scraper calls."""

    marketplace_name = "tiktok_shop"

    def search_products(self, keyword: str, limit: int = 30) -> list[dict[str, Any]]:
        raise NotImplementedError("TikTok Shop adapter is a Phase 7 skeleton (configuration only)")

    def normalize_product(self, raw_product: Mapping[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("TikTok Shop normalization is not implemented")


ADAPTER_TYPES: dict[str, type[MarketplaceAdapter]] = {
    "shopee": ShopeeAdapter,
    "lazada": LazadaAdapter,
    "tiktok_shop": TikTokShopAdapter,
}


def load_marketplace_config(
    config_path: Path = DEFAULT_CONFIG_PATH,
) -> tuple[str, dict[str, MarketplaceConfig]]:
    if not config_path.is_file():
        raise FileNotFoundError(f"Config not found: {config_path}")
    try:
        payload = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise MarketplaceConfigurationError(f"Invalid YAML config: {config_path}") from exc
    marketplace = payload.get("marketplace")
    if not isinstance(marketplace, dict):
        raise MarketplaceConfigurationError("Config must contain a marketplace mapping")
    selected = str(marketplace.get("selected", "")).strip()
    adapters_raw = marketplace.get("adapters")
    if not isinstance(adapters_raw, dict) or not adapters_raw:
        raise MarketplaceConfigurationError("marketplace.adapters must be a non-empty mapping")
    unknown = sorted(set(adapters_raw) - set(ADAPTER_TYPES))
    if unknown:
        raise MarketplaceConfigurationError(f"Unknown marketplace adapters: {', '.join(unknown)}")
    adapters = {
        name: MarketplaceConfig.from_mapping(name, data)
        for name, data in adapters_raw.items()
        if isinstance(data, dict)
    }
    if selected not in adapters:
        raise MarketplaceConfigurationError(f"Selected marketplace {selected!r} is not configured")
    if not adapters[selected].enabled:
        raise MarketplaceConfigurationError(f"Selected marketplace {selected!r} is disabled")
    return selected, adapters


def selected_adapter(config_path: Path = DEFAULT_CONFIG_PATH) -> MarketplaceAdapter:
    selected, configs = load_marketplace_config(config_path)
    return ADAPTER_TYPES[selected](configs[selected])
