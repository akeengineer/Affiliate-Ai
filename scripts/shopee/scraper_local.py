#!/usr/bin/env python3
"""Scrape Shopee from an operator's Windows machine with Playwright Chromium.

By default, the scraper connects over CDP to an operator-started Chrome browser
whose existing context contains the Shopee login session. A standalone launch
mode remains available and reads the same cookie file as the EC2 scraper. Both
modes write the same JSON format for ``to_candidate.py``.

Ref: codex/tasks/004-shopee-scraper.md
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

try:  # Package import for tests and module execution.
    from .scraper import (
        apply_filters,
        get_delay,
        get_random_user_agent,
        load_config,
        load_shopee_cookies,
        save_results,
        scrape_with_retry,
    )
except ImportError:  # pragma: no cover - direct script execution
    from scraper import (  # type: ignore
        apply_filters,
        get_delay,
        get_random_user_agent,
        load_config,
        load_shopee_cookies,
        save_results,
        scrape_with_retry,
    )


DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.yaml")


def _windows_chrome_user_agent(config: dict[str, Any]) -> str:
    """Choose a configured UA that matches the local Windows Chrome engine."""

    matching = [
        str(user_agent)
        for user_agent in config["user_agents"]
        if "Windows NT" in str(user_agent) and "Chrome/" in str(user_agent)
    ]
    return random.choice(matching) if matching else get_random_user_agent(config)


def _selected_niches(
    config: dict[str, Any], niche_filter: str | None
) -> list[dict[str, Any]]:
    niches = list(config["niches"])
    if not niche_filter:
        return niches
    selected = [niche for niche in niches if niche.get("name") == niche_filter]
    if not selected:
        raise ValueError(f"Niche {niche_filter!r} not found in config")
    return selected


def run_local_scraper(
    config: dict[str, Any],
    *,
    niche_filter: str | None = None,
    headless: bool = False,
    cdp: bool = True,
    cdp_url: str = "http://localhost:9222",
) -> dict[str, Any]:
    """Run the response-intercepting scraper in Playwright Chromium.

    No proxy is passed to Chromium: the Windows host's normal residential
    connection is intentionally used. CDP mode reuses the operator's first
    browser context and its authenticated Shopee session.
    """

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - depends on local install
        raise RuntimeError(
            "playwright is not installed; run: pip install -r requirements-shopee.txt"
        ) from exc

    niches = _selected_niches(config, niche_filter)
    results: dict[str, Any] = {
        "scraped_at": datetime.now(UTC).isoformat(),
        "niches": {},
    }

    with sync_playwright() as playwright:
        browser = None
        context = None
        try:
            if cdp:
                browser = playwright.chromium.connect_over_cdp(cdp_url)
                if not browser.contexts:
                    raise RuntimeError("Connected Chrome has no browser contexts")
                context = browser.contexts[0]
                page = context.pages[0] if context.pages else context.new_page()
            else:
                cookies = load_shopee_cookies(config)
                browser = playwright.chromium.launch(
                    channel="chrome", headless=headless
                )
                context = browser.new_context(
                    user_agent=_windows_chrome_user_agent(config),
                    viewport={"width": 1920, "height": 1080},
                    locale="th-TH",
                    extra_http_headers={
                        "Accept-Language": "th-TH,th;q=0.9,en;q=0.8"
                    },
                )
                context.add_cookies(cookies)
                page = context.new_page()

            for niche in niches:
                niche_name = str(niche["name"])
                max_products = int(niche.get("max_products", 30))
                products: list[dict[str, Any]] = []
                seen_urls: set[str] = set()
                print(f"[INFO] Scraping niche: {niche_name}", file=sys.stderr)

                for keyword in niche.get("keywords", []):
                    keyword_products = scrape_with_retry(
                        page,
                        str(keyword),
                        config,
                        max_products,
                    )
                    for product in keyword_products:
                        product_url = str(product.get("product_url", ""))
                        if not product_url or product_url in seen_urls:
                            continue
                        seen_urls.add(product_url)
                        product["niche"] = niche_name
                        product["search_keyword"] = str(keyword)
                        products.append(product)
                    time.sleep(get_delay(config))

                filtered = apply_filters(products, config)
                results["niches"][niche_name] = filtered
                print(
                    f"[INFO] Found {len(filtered)} products for {niche_name!r}",
                    file=sys.stderr,
                )
        finally:
            if not cdp:
                try:
                    if context is not None:
                        context.close()
                finally:
                    if browser is not None:
                        browser.close()

    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scrape Shopee Thailand from a local Windows Chrome browser."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--niche", default=None, help="Scrape only this configured niche")
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Hide Chrome in standalone mode (headed mode is the default).",
    )
    parser.add_argument(
        "--cdp",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Connect to an existing Chrome over CDP (default: enabled).",
    )
    parser.add_argument(
        "--cdp-url",
        default="http://localhost:9222",
        help="Chrome DevTools Protocol endpoint (default: http://localhost:9222).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate config without reading cookies or launching Chrome.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        config = load_config(args.config)
        selected = _selected_niches(config, args.niche)
        if args.dry_run:
            print(
                json.dumps(
                    {
                        "status": "dry_run_ok",
                        "browser": "playwright-chromium",
                        "cdp": args.cdp,
                        "cdp_url": args.cdp_url,
                        "proxy": None,
                        "niches": [niche["name"] for niche in selected],
                        "output_dir": config["output"]["scraped_json_dir"],
                    }
                )
            )
            return 0

        results = run_local_scraper(
            config,
            niche_filter=args.niche,
            headless=args.headless,
            cdp=args.cdp,
            cdp_url=args.cdp_url,
        )
        output_path = save_results(results, config)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("[ERROR] Scrape cancelled by operator", file=sys.stderr)
        return 130
    except Exception as exc:  # pragma: no cover - browser/runtime failure detail
        print(f"[ERROR] Local scrape failed: {exc}", file=sys.stderr)
        return 1

    total = sum(len(products) for products in results["niches"].values())
    print(
        json.dumps(
            {
                "status": "success",
                "total_products": total,
                "output_path": str(output_path),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
