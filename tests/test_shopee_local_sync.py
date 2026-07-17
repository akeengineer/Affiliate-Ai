"""Tests for the Windows Shopee scraper and EC2 synchronization helper.

Ref: codex/tasks/004-shopee-scraper.md
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "scripts" / "shopee" / "config.yaml"

from scripts.shopee import scraper_local, sync_to_ec2  # noqa: E402
from scripts.shopee.scraper import load_config  # noqa: E402


def test_local_scraper_dry_run_does_not_read_cookies_or_launch_browser(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        scraper_local,
        "load_shopee_cookies",
        MagicMock(side_effect=AssertionError("cookies must not be read")),
    )

    exit_code = scraper_local.main(["--config", str(CONFIG_PATH), "--dry-run"])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "dry_run_ok"
    assert payload["browser"] == "playwright-chromium"
    assert payload["cdp"] is True
    assert payload["cdp_url"] == "http://localhost:9222"
    assert payload["proxy"] is None
    assert payload["output_dir"] == ".cache/shopee/scraped"


def test_local_scraper_connects_over_cdp_and_reuses_authenticated_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = copy.deepcopy(load_config(CONFIG_PATH))
    config["niches"] = [
        {"name": "test", "keywords": ["desk lamp"], "max_products": 1}
    ]
    config["filters"] = {"min_sold": 0, "min_rating": 0}
    config["scraping"]["min_delay_seconds"] = 0
    config["scraping"]["max_delay_seconds"] = 0
    product = {
        "product_name": "Desk Lamp",
        "product_url": "https://shopee.co.th/product/1/2",
        "price": 299.0,
        "sold_count": 500,
        "rating": 4.8,
        "shop_name": "Test Shop",
    }

    manager = MagicMock()
    playwright_runtime = manager.__enter__.return_value
    browser = playwright_runtime.chromium.connect_over_cdp.return_value
    context = MagicMock()
    page = MagicMock()
    browser.contexts = [context]
    context.pages = [page]

    sync_api_module = ModuleType("playwright.sync_api")
    sync_api_module.sync_playwright = lambda: manager  # type: ignore[attr-defined]
    playwright_module = ModuleType("playwright")
    playwright_module.sync_api = sync_api_module  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "playwright", playwright_module)
    monkeypatch.setitem(sys.modules, "playwright.sync_api", sync_api_module)
    load_cookies = MagicMock(side_effect=AssertionError("CDP must reuse Chrome cookies"))
    monkeypatch.setattr(scraper_local, "load_shopee_cookies", load_cookies)
    scrape = MagicMock(return_value=[dict(product)])
    monkeypatch.setattr(scraper_local, "scrape_with_retry", scrape)

    results = scraper_local.run_local_scraper(
        config,
        cdp_url="http://localhost:9333",
    )

    playwright_runtime.chromium.connect_over_cdp.assert_called_once_with(
        "http://localhost:9333"
    )
    playwright_runtime.chromium.launch.assert_not_called()
    load_cookies.assert_not_called()
    context.new_page.assert_not_called()
    scrape.assert_called_once_with(page, "desk lamp", config, 1)
    context.close.assert_not_called()
    browser.close.assert_not_called()
    assert results["niches"]["test"][0]["search_keyword"] == "desk lamp"


def test_local_scraper_launches_chrome_without_proxy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = copy.deepcopy(load_config(CONFIG_PATH))
    config["niches"] = [
        {"name": "test", "keywords": ["desk lamp"], "max_products": 1}
    ]
    config["filters"] = {"min_sold": 0, "min_rating": 0}
    config["scraping"]["min_delay_seconds"] = 0
    config["scraping"]["max_delay_seconds"] = 0
    cookies = [
        {
            "name": "SPC_EC",
            "value": "fake-session",
            "domain": ".shopee.co.th",
            "path": "/",
        }
    ]
    product = {
        "product_name": "Desk Lamp",
        "product_url": "https://shopee.co.th/product/1/2",
        "price": 299.0,
        "sold_count": 500,
        "rating": 4.8,
        "shop_name": "Test Shop",
    }

    manager = MagicMock()
    playwright_runtime = manager.__enter__.return_value
    browser = playwright_runtime.chromium.launch.return_value
    context = browser.new_context.return_value

    sync_api_module = ModuleType("playwright.sync_api")
    sync_api_module.sync_playwright = lambda: manager  # type: ignore[attr-defined]
    playwright_module = ModuleType("playwright")
    playwright_module.sync_api = sync_api_module  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "playwright", playwright_module)
    monkeypatch.setitem(sys.modules, "playwright.sync_api", sync_api_module)
    monkeypatch.setattr(scraper_local, "load_shopee_cookies", lambda _config: cookies)
    monkeypatch.setattr(
        scraper_local,
        "scrape_with_retry",
        lambda _page, _keyword, _config, _maximum: [dict(product)],
    )

    results = scraper_local.run_local_scraper(config, cdp=False)

    playwright_runtime.chromium.launch.assert_called_once_with(
        channel="chrome", headless=False
    )
    assert "proxy" not in playwright_runtime.chromium.launch.call_args.kwargs
    assert "Windows NT" in browser.new_context.call_args.kwargs["user_agent"]
    assert "Chrome/" in browser.new_context.call_args.kwargs["user_agent"]
    context.add_cookies.assert_called_once_with(cookies)
    assert results["niches"]["test"][0]["search_keyword"] == "desk lamp"


def test_sync_uploads_json_and_runs_remote_transform(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    input_dir = tmp_path / "scraped"
    input_dir.mkdir()
    for name in ("shopee_scraped_1.json", "shopee_scraped_2.json"):
        (input_dir / name).write_text("{}\n", encoding="utf-8")
    run = MagicMock()
    monkeypatch.setattr(sync_to_ec2.subprocess, "run", run)

    summary = sync_to_ec2.sync_to_ec2(
        input_dir,
        host="test-ec2",
        remote_repo="Affiliate-Ai",
    )

    commands = [call.args[0] for call in run.call_args_list]
    assert commands[0][0:2] == ["ssh", "test-ec2"]
    assert commands[1][0] == "scp"
    assert commands[1][-1] == "test-ec2:Affiliate-Ai/.cache/shopee/scraped/"
    assert all("to_candidate.py" in command[2] for command in commands[2:])
    assert summary["files_synced"] == 2
    assert run.call_count == 4


def test_remote_repo_supports_ssh_home_path() -> None:
    assert sync_to_ec2._remote_shell_path("~/Affiliate-Ai") == "$HOME/Affiliate-Ai"
