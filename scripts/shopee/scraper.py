#!/usr/bin/env python3
"""Shopee product scraper using Camoufox and Playwright.

Scrapes product data from Shopee Thailand (.co.th) based on configured
niches and keywords. Outputs JSON files for downstream processing.

Usage:
    python scripts/shopee/scraper.py --config scripts/shopee/config.yaml
    python scripts/shopee/scraper.py --config scripts/shopee/config.yaml --niche gadgets
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

import yaml


def load_config(config_path: Path) -> dict[str, Any]:
    """Load and validate scraper configuration."""
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    _validate_config(config)
    return config


def _validate_config(config: dict[str, Any]) -> None:
    """Validate required config fields."""
    required = ["base_url", "niches", "scraping", "user_agents", "output"]
    missing = [k for k in required if k not in config]
    if missing:
        raise ValueError(f"Missing config fields: {', '.join(missing)}")
    if not config["niches"]:
        raise ValueError("At least one niche must be configured")
    if not config["user_agents"]:
        raise ValueError("At least one user-agent must be configured")


def get_random_user_agent(config: dict[str, Any]) -> str:
    """Select a random user-agent from the configured list."""
    return random.choice(config["user_agents"])


def get_delay(config: dict[str, Any]) -> float:
    """Calculate a randomized delay between requests."""
    scraping = config["scraping"]
    return random.uniform(
        scraping["min_delay_seconds"],
        scraping["max_delay_seconds"],
    )


def get_proxy_options(config: dict[str, Any]) -> dict[str, str] | None:
    """Build Playwright-compatible proxy options from scraper configuration."""
    proxy_config = config.get("proxy", {})
    env_var = str(proxy_config.get("env_var", "SCRAPER_PROXY_URL")).strip()
    proxy_url = os.getenv(env_var, "").strip()
    if not proxy_url:
        proxy_url = str(proxy_config.get("default_url", "")).strip()
    if not proxy_url:
        return None
    return {"server": proxy_url}


def scrape_search_page(
    page: Any,
    keyword: str,
    config: dict[str, Any],
    max_products: int,
) -> list[dict[str, Any]]:
    """Scrape products by intercepting Shopee's search API responses.

    Shopee's public API returns 403 for direct HTTP requests, so the only
    reliable path is to drive a real browser and capture the JSON that the
    search page fetches from ``/api/v4/search/search_items`` in the
    background.

    Args:
        page: Playwright page object.
        keyword: Search keyword.
        config: Full configuration dict.
        max_products: Maximum products to collect.

    Returns:
        List of raw product data dicts.
    """
    base_url = config["base_url"]
    search_url = f"{base_url}/search?keyword={quote(keyword)}"
    timeout = config["scraping"]["timeout_seconds"] * 1000

    captured_items: list[dict[str, Any]] = []

    def handle_response(response: Any) -> None:
        # Shopee search results arrive via .../api/v4/search/search_items
        if "search_items" not in response.url:
            return
        try:
            payload = response.json()
        except Exception:
            return
        captured_items.extend(_extract_items_from_payload(payload))

    page.on("response", handle_response)
    try:
        page.goto(search_url, wait_until="domcontentloaded", timeout=timeout)
        _wait_for_search_data(page, captured_items, max_products, config)
    finally:
        try:
            page.remove_listener("response", handle_response)
        except Exception:
            pass

    products: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    for item in captured_items:
        product = _extract_product_from_item(item, base_url)
        if not product:
            continue
        if product["product_url"] in seen_urls:
            continue
        seen_urls.add(product["product_url"])
        products.append(product)
        if len(products) >= max_products:
            break
    return products


def _wait_for_search_data(
    page: Any,
    captured_items: list[dict[str, Any]],
    max_products: int,
    config: dict[str, Any],
) -> None:
    """Poll (and scroll) until search results arrive or the timeout elapses."""
    max_wait = config["scraping"]["timeout_seconds"]
    deadline = time.monotonic() + max_wait
    while len(captured_items) < max_products and time.monotonic() < deadline:
        page.wait_for_timeout(1000)
        try:
            page.evaluate("window.scrollBy(0, window.innerHeight)")
        except Exception:
            pass
    # Let any in-flight response finish once data has started arriving.
    if captured_items:
        page.wait_for_timeout(1000)


def _extract_items_from_payload(payload: Any) -> list[dict[str, Any]]:
    """Pull the item list out of a Shopee search_items API response."""
    if not isinstance(payload, dict):
        return []
    items = payload.get("items")
    if not isinstance(items, list):
        return []
    return [it for it in items if isinstance(it, dict)]


def _extract_product_from_item(
    item: dict[str, Any], base_url: str
) -> dict[str, Any] | None:
    """Convert one intercepted Shopee item into a raw product dict."""
    basic = item.get("item_basic")
    if not isinstance(basic, dict):
        basic = item
    name = str(basic.get("name") or "").strip()
    itemid = basic.get("itemid")
    shopid = basic.get("shopid")
    if not name or itemid is None or shopid is None:
        return None

    raw_price = basic.get("price")
    if raw_price is None:
        raw_price = basic.get("price_min")
    # Shopee encodes prices in micro-units (actual price * 100000).
    price = (
        round(raw_price / 100000, 2)
        if isinstance(raw_price, (int, float)) and raw_price
        else 0.0
    )

    sold = basic.get("historical_sold")
    if not sold:
        sold = basic.get("sold") or 0

    rating = 0.0
    rating_obj = basic.get("item_rating")
    if isinstance(rating_obj, dict):
        try:
            rating = round(float(rating_obj.get("rating_star") or 0.0), 2)
        except (TypeError, ValueError):
            rating = 0.0

    return {
        "product_name": name,
        "product_url": f"{base_url}/product/{shopid}/{itemid}",
        "price": price,
        "currency": "THB",
        "sold_count": int(sold),
        "rating": rating,
        "shop_name": str(basic.get("shop_name") or "").strip(),
        "scraped_at": datetime.now(UTC).isoformat(),
    }


def _parse_price(text: str) -> float:
    """Parse price text to float, handling Thai formatting."""
    cleaned = text.replace("฿", "").replace(",", "").replace(" ", "").strip()
    # Handle range prices (e.g., "199 - 599"), take lower bound
    if "-" in cleaned:
        cleaned = cleaned.split("-")[0].strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def _parse_sold(text: str) -> int:
    """Parse sold count text (e.g., '1.2พัน ชิ้น', '500 sold')."""
    cleaned = text.lower().replace(",", "").strip()
    # Handle Thai abbreviations
    if "พัน" in cleaned:
        cleaned = cleaned.replace("พัน", "").replace("ชิ้น", "").strip()
        try:
            return int(float(cleaned) * 1000)
        except ValueError:
            return 0
    if "หมื่น" in cleaned:
        cleaned = cleaned.replace("หมื่น", "").replace("ชิ้น", "").strip()
        try:
            return int(float(cleaned) * 10000)
        except ValueError:
            return 0
    # Strip non-numeric suffix
    digits = "".join(c for c in cleaned if c.isdigit() or c == ".")
    try:
        return int(float(digits)) if digits else 0
    except ValueError:
        return 0


def apply_filters(
    products: list[dict[str, Any]], config: dict[str, Any]
) -> list[dict[str, Any]]:
    """Filter products by minimum thresholds."""
    filters = config.get("filters", {})
    min_sold = filters.get("min_sold", 0)
    min_rating = filters.get("min_rating", 0.0)
    min_rating_count = filters.get("min_rating_count", 0)

    filtered = []
    for p in products:
        if p.get("sold_count", 0) < min_sold:
            continue
        if p.get("rating", 0) < min_rating:
            continue
        filtered.append(p)
    return filtered


def scrape_niche(
    page: Any,
    niche: dict[str, Any],
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    """Scrape all keywords for a single niche."""
    all_products: list[dict[str, Any]] = []
    max_products = niche.get("max_products", 30)
    seen_urls: set[str] = set()

    for keyword in niche.get("keywords", []):
        products = scrape_with_retry(page, keyword, config, max_products)
        for p in products:
            url = p.get("product_url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                p["niche"] = niche["name"]
                p["search_keyword"] = keyword
                all_products.append(p)

        time.sleep(get_delay(config))

    return apply_filters(all_products, config)


def scrape_with_retry(
    page: Any,
    keyword: str,
    config: dict[str, Any],
    max_products: int,
) -> list[dict[str, Any]]:
    """Scrape with exponential backoff retry."""
    max_retries = config["scraping"]["max_retries"]
    backoff = config["scraping"]["backoff_multiplier"]

    for attempt in range(max_retries):
        try:
            return scrape_search_page(page, keyword, config, max_products)
        except Exception as exc:
            if attempt == max_retries - 1:
                print(f"[ERROR] Failed after {max_retries} attempts for '{keyword}': {exc}", file=sys.stderr)
                return []
            wait = (backoff ** attempt) * get_delay(config)
            print(f"[RETRY] Attempt {attempt + 1} failed for '{keyword}', waiting {wait:.1f}s", file=sys.stderr)
            time.sleep(wait)
    return []


def run_scraper(config: dict[str, Any], niche_filter: str | None = None) -> dict[str, Any]:
    """Run the full scraping pipeline.

    Args:
        config: Loaded configuration.
        niche_filter: Optional niche name to scrape only one niche.

    Returns:
        Results dict with scraped products per niche.
    """
    try:
        from camoufox.sync_api import Camoufox
    except ImportError:
        print(
            "[ERROR] camoufox not installed. Run: pip install -r requirements-shopee.txt && camoufox fetch",
            file=sys.stderr,
        )
        sys.exit(1)

    niches = config["niches"]
    if niche_filter:
        niches = [n for n in niches if n["name"] == niche_filter]
        if not niches:
            print(f"[ERROR] Niche '{niche_filter}' not found in config", file=sys.stderr)
            sys.exit(1)

    results: dict[str, Any] = {
        "scraped_at": datetime.now(UTC).isoformat(),
        "niches": {},
    }

    with Camoufox(
        headless=True,
        proxy=get_proxy_options(config),
    ) as browser:
        context = browser.new_context(
            user_agent=get_random_user_agent(config),
            viewport={"width": 1920, "height": 1080},
            locale="th-TH",
            extra_http_headers={"Accept-Language": "th-TH,th;q=0.9,en;q=0.8"},
        )
        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )
        page = context.new_page()

        for niche in niches:
            niche_name = niche["name"]
            print(f"[INFO] Scraping niche: {niche_name}", file=sys.stderr)
            products = scrape_niche(page, niche, config)
            results["niches"][niche_name] = products
            print(f"[INFO] Found {len(products)} products for '{niche_name}'", file=sys.stderr)

        context.close()

    return results


def save_results(results: dict[str, Any], config: dict[str, Any]) -> Path:
    """Save scraped results to JSON file."""
    output_dir = Path(config["output"]["scraped_json_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"shopee_scraped_{timestamp}.json"
    output_path.write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"[INFO] Results saved to: {output_path}", file=sys.stderr)
    return output_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scrape Shopee Thailand products.")
    parser.add_argument("--config", required=True, type=Path, help="Path to config.yaml")
    parser.add_argument("--niche", type=str, default=None, help="Scrape only this niche")
    parser.add_argument("--dry-run", action="store_true", help="Validate config without scraping")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        config = load_config(args.config)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        print("[OK] Config valid. Niches configured:", file=sys.stderr)
        for niche in config["niches"]:
            print(f"  - {niche['name']}: {len(niche.get('keywords', []))} keywords", file=sys.stderr)
        return 0

    results = run_scraper(config, niche_filter=args.niche)
    save_results(results, config)

    total = sum(len(products) for products in results["niches"].values())
    print(json.dumps({"status": "success", "total_products": total}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
