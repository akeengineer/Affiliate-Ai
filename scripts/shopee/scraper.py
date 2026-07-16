#!/usr/bin/env python3
"""Shopee product scraper using Playwright.

Scrapes product data from Shopee Thailand (.co.th) based on configured
niches and keywords. Outputs JSON files for downstream processing.

Usage:
    python scripts/shopee/scraper.py --config scripts/shopee/config.yaml
    python scripts/shopee/scraper.py --config scripts/shopee/config.yaml --niche gadgets
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

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


def scrape_search_page(
    page: Any,
    keyword: str,
    config: dict[str, Any],
    max_products: int,
) -> list[dict[str, Any]]:
    """Scrape product listings from a Shopee search page.

    Args:
        page: Playwright page object.
        keyword: Search keyword.
        config: Full configuration dict.
        max_products: Maximum products to collect.

    Returns:
        List of raw product data dicts.
    """
    base_url = config["base_url"]
    search_url = f"{base_url}/search?keyword={keyword}"
    timeout = config["scraping"]["timeout_seconds"] * 1000

    page.goto(search_url, wait_until="networkidle", timeout=timeout)
    time.sleep(get_delay(config))

    # Scroll to load lazy content
    for _ in range(3):
        page.evaluate("window.scrollBy(0, window.innerHeight)")
        time.sleep(1)

    products: list[dict[str, Any]] = []

    # Extract product cards from Shopee search results
    product_cards = page.query_selector_all(
        "[data-sqe='item']"
    ) or page.query_selector_all(".shopee-search-item-result__item")

    for card in product_cards[:max_products]:
        try:
            product = _extract_product_from_card(card, base_url)
            if product:
                products.append(product)
        except Exception:
            continue  # Skip malformed cards

    return products


def _extract_product_from_card(card: Any, base_url: str) -> dict[str, Any] | None:
    """Extract product data from a single search result card."""
    # Product name
    name_el = card.query_selector("[data-sqe='name']") or card.query_selector(
        ".ie3A\\+n, .Cve6sh"
    )
    if not name_el:
        return None
    name = name_el.inner_text().strip()
    if not name:
        return None

    # Product link
    link_el = card.query_selector("a")
    product_url = ""
    if link_el:
        href = link_el.get_attribute("href") or ""
        product_url = href if href.startswith("http") else f"{base_url}{href}"

    # Price
    price_el = card.query_selector("[aria-label*='price']") or card.query_selector(
        ".ZEgDH9, .vioxXd"
    )
    price_text = price_el.inner_text().strip() if price_el else "0"
    price = _parse_price(price_text)

    # Sold count
    sold_el = card.query_selector("[class*='sold']") or card.query_selector(
        ".r6HknA, .OwmBnn"
    )
    sold_text = sold_el.inner_text().strip() if sold_el else "0"
    sold_count = _parse_sold(sold_text)

    # Rating
    rating_el = card.query_selector("[aria-label*='rating']") or card.query_selector(
        ".shopee-rating-stars__stars"
    )
    rating = _parse_rating(rating_el)

    # Shop name
    shop_el = card.query_selector("[data-sqe='shopName']") or card.query_selector(
        ".zGGwiV"
    )
    shop_name = shop_el.inner_text().strip() if shop_el else ""

    return {
        "product_name": name,
        "product_url": product_url,
        "price": price,
        "currency": "THB",
        "sold_count": sold_count,
        "rating": rating,
        "shop_name": shop_name,
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


def _parse_rating(el: Any) -> float:
    """Parse rating from element."""
    if not el:
        return 0.0
    aria = el.get_attribute("aria-label") or ""
    digits = "".join(c for c in aria if c.isdigit() or c == ".")
    try:
        return float(digits) if digits else 0.0
    except ValueError:
        return 0.0


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
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[ERROR] playwright not installed. Run: pip install playwright && playwright install chromium", file=sys.stderr)
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

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=get_random_user_agent(config),
            viewport={"width": 1920, "height": 1080},
            locale="th-TH",
        )
        page = context.new_page()

        for niche in niches:
            niche_name = niche["name"]
            print(f"[INFO] Scraping niche: {niche_name}", file=sys.stderr)
            products = scrape_niche(page, niche, config)
            results["niches"][niche_name] = products
            print(f"[INFO] Found {len(products)} products for '{niche_name}'", file=sys.stderr)

        browser.close()

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
