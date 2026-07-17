#!/usr/bin/env python3
"""Transform scraped Shopee data into Obsidian-compatible product_candidate notes.

Reads JSON output from scraper.py and generates Markdown notes with YAML
frontmatter matching the vault/templates/product-candidate-template.md schema.

Usage:
    python scripts/shopee/to_candidate.py --input .cache/shopee/scraped/shopee_scraped_*.json --output-dir vault/candidates/
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml


def load_scraped_data(input_path: Path) -> dict[str, Any]:
    """Load scraped JSON data."""
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    with open(input_path, encoding="utf-8") as f:
        return json.load(f)


def generate_product_id(product: dict[str, Any]) -> str:
    """Generate a deterministic product ID from product data."""
    name = product.get("product_name", "unknown")
    # Slugify: lowercase, replace non-alphanumeric with hyphen, trim
    slug = re.sub(r"[^a-z0-9\u0e00-\u0e7f]+", "-", name.lower())
    slug = slug.strip("-")[:50]
    return f"prod-shopee-{slug}"


def estimate_scores(product: dict[str, Any]) -> dict[str, int]:
    """Estimate initial component scores from scraped metrics.

    These are rough heuristics. Agents will refine scores later.
    """
    sold = product.get("sold_count", 0)
    rating = product.get("rating", 0.0)
    price = product.get("price", 0.0)

    # Demand score: based on sold count
    if sold >= 10000:
        demand = 95
    elif sold >= 5000:
        demand = 85
    elif sold >= 1000:
        demand = 75
    elif sold >= 500:
        demand = 65
    elif sold >= 100:
        demand = 55
    else:
        demand = 40

    # Trend velocity: placeholder (agents will refine)
    trend = min(90, max(40, demand - 5))

    # Marketplace rank: based on rating
    marketplace = int(min(95, max(40, rating * 19)))

    # Commission: placeholder (unknown without API)
    commission = 60

    # Content fit: placeholder
    content_fit = 65

    # Competition gap: inverse of sold (high sold = more competition)
    if sold >= 10000:
        competition_gap = 40
    elif sold >= 5000:
        competition_gap = 55
    elif sold >= 1000:
        competition_gap = 70
    else:
        competition_gap = 80

    # Risk: lower price = lower risk
    if price <= 200:
        risk = 15
    elif price <= 500:
        risk = 20
    elif price <= 1000:
        risk = 30
    elif price <= 5000:
        risk = 40
    else:
        risk = 55

    return {
        "demand_score": demand,
        "trend_velocity_score": trend,
        "marketplace_rank_score": marketplace,
        "commission_score": commission,
        "content_fit_score": content_fit,
        "competition_gap_score": competition_gap,
        "risk_score": risk,
    }


def create_candidate_note(product: dict[str, Any]) -> str:
    """Generate a product_candidate Markdown note from product data."""
    now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    product_id = generate_product_id(product)
    scores = estimate_scores(product)

    frontmatter = {
        "type": "product_candidate",
        "product_id": product_id,
        "product_name": product.get("product_name", ""),
        "brand": product.get("shop_name", "Unknown"),
        "marketplace": "Shopee Thailand",
        "niche": product.get("niche", ""),
        "product_url": product.get("product_url", ""),
        "currency": "THB",
        "price": product.get("price", 0),
        "sold_count": product.get("sold_count", 0),
        "rating": product.get("rating", 0.0),
        "demand_score": scores["demand_score"],
        "trend_velocity_score": scores["trend_velocity_score"],
        "marketplace_rank_score": scores["marketplace_rank_score"],
        "commission_score": scores["commission_score"],
        "content_fit_score": scores["content_fit_score"],
        "competition_gap_score": scores["competition_gap_score"],
        "risk_score": scores["risk_score"],
        "trend_signal_note": "",
        "marketplace_signal_note": "",
        "commission_signal_note": "",
        "compliance_result_note": "",
        "status": "scraped",
        "source": "shopee_scraper",
        "search_keyword": product.get("search_keyword", ""),
        "scraped_at": product.get("scraped_at", now),
        "created_at": now,
        "updated_at": now,
    }

    body_lines = [
        f"# {product.get('product_name', 'Unknown')}",
        "",
        "## Summary",
        "",
        f"Scraped from Shopee Thailand via automated scraper.",
        f"- Shop: {product.get('shop_name', 'Unknown')}",
        f"- Price: ฿{product.get('price', 0):,.0f}",
        f"- Sold: {product.get('sold_count', 0):,}",
        f"- Rating: {product.get('rating', 0):.1f}/5.0",
        f"- Niche: {product.get('niche', '')}",
        f"- Keyword: {product.get('search_keyword', '')}",
        "",
        "## Notes",
        "",
        "- Initial scores are heuristic estimates from scraped metrics.",
        "- Agents will refine scores after signal analysis.",
        "- Commission score is estimated (no API data yet).",
    ]

    fm_yaml = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{fm_yaml}\n---\n\n" + "\n".join(body_lines) + "\n"


def save_candidate_note(note_content: str, product: dict[str, Any], output_dir: Path) -> Path:
    """Save candidate note to output directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    product_id = generate_product_id(product)
    filename = f"{product_id}.md"
    output_path = output_dir / filename

    # Avoid overwriting existing notes
    if output_path.exists():
        return output_path

    output_path.write_text(note_content, encoding="utf-8")
    return output_path


def transform_all(input_path: Path, output_dir: Path) -> list[Path]:
    """Transform all scraped products into candidate notes.

    Returns list of created file paths.
    """
    data = load_scraped_data(input_path)
    created: list[Path] = []

    for niche_name, products in data.get("niches", {}).items():
        for product in products:
            note = create_candidate_note(product)
            path = save_candidate_note(note, product, output_dir)
            created.append(path)

    return created


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Transform scraped Shopee data into product_candidate Markdown notes."
    )
    parser.add_argument("--input", required=True, type=Path, help="Path to scraped JSON file")
    parser.add_argument("--output-dir", required=True, type=Path, help="Output directory for candidate notes")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        created = transform_all(args.input, args.output_dir)
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    print(json.dumps({
        "status": "success",
        "candidates_created": len(created),
        "output_dir": str(args.output_dir),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
