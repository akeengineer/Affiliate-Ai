"""Tests for Shopee scraper and candidate transformer.

Tests cover config loading, rate limiting, retry logic, candidate note
generation, frontmatter schema validation, and pipeline integration.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "shopee"))

from scraper import (  # noqa: E402
    _parse_price,
    _parse_sold,
    apply_filters,
    get_delay,
    get_random_user_agent,
    load_config,
)
from to_candidate import (  # noqa: E402
    create_candidate_note,
    estimate_scores,
    generate_product_id,
    load_scraped_data,
    transform_all,
)


# ---------- Config tests ----------

SAMPLE_CONFIG_PATH = REPO_ROOT / "scripts" / "shopee" / "config.yaml"


def test_scraper_config_loading():
    """Config loads and validates without error."""
    config = load_config(SAMPLE_CONFIG_PATH)
    assert "base_url" in config
    assert len(config["niches"]) >= 1
    assert len(config["user_agents"]) >= 1


def test_scraper_config_missing_file(tmp_path: Path):
    """Missing config raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "nonexistent.yaml")


def test_scraper_config_invalid(tmp_path: Path):
    """Invalid config raises ValueError."""
    bad_config = tmp_path / "bad.yaml"
    bad_config.write_text("base_url: x\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Missing config"):
        load_config(bad_config)


# ---------- Rate limiting tests ----------


def test_scraper_rate_limiting():
    """Delay is within configured bounds."""
    config = load_config(SAMPLE_CONFIG_PATH)
    for _ in range(50):
        delay = get_delay(config)
        assert config["scraping"]["min_delay_seconds"] <= delay <= config["scraping"]["max_delay_seconds"]


def test_random_user_agent():
    """User-agent is selected from configured list."""
    config = load_config(SAMPLE_CONFIG_PATH)
    ua = get_random_user_agent(config)
    assert ua in config["user_agents"]


# ---------- Price/sold parsing tests ----------


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("฿199", 199.0),
        ("฿1,299", 1299.0),
        ("199 - 599", 199.0),
        ("0", 0.0),
        ("abc", 0.0),
    ],
)
def test_parse_price(text: str, expected: float):
    assert _parse_price(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1.2พัน ชิ้น", 1200),
        ("500", 500),
        ("2หมื่น ชิ้น", 20000),
        ("sold 300", 300),
        ("", 0),
    ],
)
def test_parse_sold(text: str, expected: int):
    assert _parse_sold(text) == expected


# ---------- Filter tests ----------


def test_apply_filters():
    """Products below thresholds are filtered out."""
    config = load_config(SAMPLE_CONFIG_PATH)
    products = [
        {"sold_count": 500, "rating": 4.5},
        {"sold_count": 50, "rating": 4.8},  # below min_sold
        {"sold_count": 200, "rating": 3.5},  # below min_rating
    ]
    filtered = apply_filters(products, config)
    assert len(filtered) == 1
    assert filtered[0]["sold_count"] == 500


# ---------- Candidate transformer tests ----------


def test_generate_product_id():
    """Product ID is generated correctly."""
    product = {"product_name": "Smart Desk Pad Pro"}
    pid = generate_product_id(product)
    assert pid.startswith("prod-shopee-")
    assert "smart" in pid.lower()


def test_estimate_scores():
    """Scores are within 0-100 range."""
    product = {"sold_count": 5000, "rating": 4.7, "price": 299}
    scores = estimate_scores(product)
    for key, value in scores.items():
        assert 0 <= value <= 100, f"{key} out of range: {value}"


def test_to_candidate_valid_output():
    """Candidate note is valid Markdown with frontmatter."""
    product = {
        "product_name": "Test Gadget",
        "product_url": "https://shopee.co.th/test",
        "price": 599,
        "currency": "THB",
        "sold_count": 2000,
        "rating": 4.5,
        "shop_name": "TestShop",
        "niche": "gadgets",
        "search_keyword": "smart gadget",
        "scraped_at": "2026-07-16T02:00:00+00:00",
    }
    note = create_candidate_note(product)
    assert note.startswith("---\n")
    assert "\n---\n" in note
    assert "type: product_candidate" in note
    assert "product_name: Test Gadget" in note


def test_to_candidate_frontmatter_schema():
    """Frontmatter contains all required fields for score_product.py."""
    product = {
        "product_name": "Schema Test",
        "product_url": "https://shopee.co.th/schema",
        "price": 100,
        "sold_count": 500,
        "rating": 4.0,
        "shop_name": "Shop",
        "niche": "test",
    }
    note = create_candidate_note(product)

    required_fields = [
        "type",
        "product_id",
        "product_name",
        "marketplace",
        "currency",
        "demand_score",
        "trend_velocity_score",
        "marketplace_rank_score",
        "commission_score",
        "content_fit_score",
        "competition_gap_score",
        "risk_score",
        "status",
        "created_at",
        "updated_at",
    ]
    for field in required_fields:
        assert f"{field}:" in note, f"Missing field: {field}"


# ---------- Pipeline integration test ----------


def test_pipeline_integration(tmp_path: Path):
    """Full pipeline: scraped JSON → candidate notes → score_product.py."""
    # Create fake scraped data
    scraped = {
        "scraped_at": "2026-07-16T02:00:00Z",
        "niches": {
            "gadgets": [
                {
                    "product_name": "Integration Test Product",
                    "product_url": "https://shopee.co.th/integration-test",
                    "price": 399,
                    "currency": "THB",
                    "sold_count": 3000,
                    "rating": 4.6,
                    "shop_name": "IntTestShop",
                    "niche": "gadgets",
                    "search_keyword": "smart gadget",
                    "scraped_at": "2026-07-16T02:00:00Z",
                }
            ]
        },
    }
    input_file = tmp_path / "scraped.json"
    input_file.write_text(json.dumps(scraped), encoding="utf-8")

    output_dir = tmp_path / "candidates"
    created = transform_all(input_file, output_dir)

    assert len(created) == 1
    assert created[0].exists()

    # Verify the note can be scored by score_product.py
    import subprocess

    score_script = REPO_ROOT / "scripts" / "dev" / "score_product.py"
    result = subprocess.run(
        [sys.executable, str(score_script), str(created[0])],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT / "scripts" / "dev"),
    )
    assert result.returncode == 0, f"score_product failed: {result.stderr}"
    payload = json.loads(result.stdout)
    assert payload["product_id"].startswith("prod-shopee-")
    assert payload["score_decision"] in ("launch", "small_batch_test", "watchlist", "reject")


# ---------- Retry logic test ----------


def test_scraper_retry_on_failure():
    """Retry logic retries on failure and returns empty on final failure."""
    config = load_config(SAMPLE_CONFIG_PATH)
    config["scraping"]["max_retries"] = 2
    config["scraping"]["min_delay_seconds"] = 0.01
    config["scraping"]["max_delay_seconds"] = 0.02

    mock_page = MagicMock()
    mock_page.goto.side_effect = Exception("Network error")

    from scraper import scrape_with_retry

    result = scrape_with_retry(mock_page, "test", config, 10)
    assert result == []
    assert mock_page.goto.call_count == 2
