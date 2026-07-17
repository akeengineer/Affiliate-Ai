"""Mocked tests for the four Phase 7 enhancement components."""
from __future__ import annotations

import inspect
from pathlib import Path

import pytest
import yaml

from scripts.content import draft_generator
from scripts.dashboard import portfolio_web
from scripts.experiments import ab_test_weights
from scripts.shopee import multi_marketplace


TIMESTAMP = "2026-07-17T08:00:00Z"


def _write_note(path: Path, frontmatter: dict, body: str = "# Sample\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        + yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True)
        + "---\n"
        + body,
        encoding="utf-8",
    )
    return path


def _product_frontmatter(product_id: str = "prod-phase7", product_name: str = "Desk Lamp") -> dict:
    return {
        "type": "product_candidate",
        "product_id": product_id,
        "product_name": product_name,
        "marketplace": "Shopee",
        "currency": "THB",
        "demand_score": 90,
        "trend_velocity_score": 88,
        "marketplace_rank_score": 82,
        "commission_score": 75,
        "content_fit_score": 90,
        "competition_gap_score": 70,
        "risk_score": 10,
        "product_opportunity_score": 84.35,
        "score_decision": "small_batch_test",
        "confidence_score": 100,
        "trend_signal_note": "trends/phase7.md",
        "marketplace_signal_note": "marketplace-signals/phase7.md",
        "commission_signal_note": "commissions/phase7.md",
        "compliance_result_note": "compliance/phase7.md",
        "created_at": TIMESTAMP,
        "updated_at": TIMESTAMP,
        "status": "scored",
    }


def _decision_frontmatter(product_id: str = "prod-phase7") -> dict:
    return {
        "type": "decision",
        "decision_id": f"dec-{product_id}-2026-W29",
        "product_id": product_id,
        "final_decision": "small_batch_test",
        "vote_count": 3,
        "compliance_status": "approved",
        "created_at": TIMESTAMP,
        "updated_at": TIMESTAMP,
        "status": "complete",
    }


def test_draft_generator_reads_context_calls_runner_and_writes_review_note(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    _write_note(vault / "products/prod-phase7.md", _product_frontmatter(), "Useful desk lighting.")
    _write_note(vault / "decisions/decision.md", _decision_frontmatter(), "Approved for a small test.")
    prompts: list[str] = []

    def fake_claude(prompt: str) -> dict[str, str]:
        prompts.append(prompt)
        return {
            "title": "A calmer desk setup",
            "hook": "Better light can change how a workspace feels.",
            "body": "This compact lamp is designed for focused desk lighting.",
            "cta": "Review the product details to see whether it fits your setup.",
        }

    output = draft_generator.generate_draft(
        vault,
        "prod-phase7",
        runner=fake_claude,
        timestamp=TIMESTAMP,
    )

    assert len(prompts) == 1
    assert "<vault_context>" in prompts[0]
    note = draft_generator.read_note(output)
    assert note.frontmatter["type"] == "content_draft"
    assert note.frontmatter["product_id"] == "prod-phase7"
    assert note.frontmatter["status"] == "draft"
    assert note.frontmatter["publish_status"] == "review_required"
    assert "## Hook" in note.body and "## CTA" in note.body
    assert "not been published" in note.body


def test_draft_generator_rejects_unapproved_decision_before_runner(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    _write_note(vault / "products/product.md", _product_frontmatter())
    decision = _decision_frontmatter()
    decision["compliance_status"] = "needs_review"
    _write_note(vault / "decisions/decision.md", decision)
    called = False

    def fake_claude(_prompt: str) -> dict[str, str]:
        nonlocal called
        called = True
        return {}

    with pytest.raises(draft_generator.DraftGenerationError, match="compliance_status"):
        draft_generator.generate_draft(vault, "prod-phase7", runner=fake_claude)
    assert called is False
    assert not (vault / "contents").exists()


def test_portfolio_web_renders_scores_decisions_and_weekly_trends(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    product = _product_frontmatter(product_name="Lamp <script>alert(1)</script>")
    _write_note(vault / "products/product.md", product)
    _write_note(vault / "decisions/decision.md", _decision_frontmatter())
    _write_note(
        vault / "reports/weekly.md",
        {
            "type": "weekly_report",
            "report_id": "weekly-2026-W29",
            "report_week": "2026-W29",
            "generated_at": TIMESTAMP,
            "candidate_count": 4,
            "launch_count": 1,
            "small_batch_test_count": 2,
            "watchlist_count": 1,
            "reject_count": 0,
            "created_at": TIMESTAMP,
            "updated_at": TIMESTAMP,
            "status": "complete",
        },
    )
    _write_note(
        vault / "trends/trend.md",
        {
            "type": "trend_signal",
            "signal_id": "trend-phase7",
            "product_id": "prod-phase7",
            "source": "mock",
            "signal_date": "2026-07-16",
            "trend_velocity_score": 88,
            "created_at": TIMESTAMP,
            "updated_at": TIMESTAMP,
            "status": "complete",
        },
    )

    page = portfolio_web.render_dashboard(vault)

    assert "Affiliate Product Portfolio" in page
    assert "84.35" in page
    assert "small_batch_test" in page
    assert "2026-W29" in page
    assert "88.00" in page
    assert "<script>" not in page
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in page
    assert portfolio_web.DEFAULT_HOST == "127.0.0.1"
    assert portfolio_web.DEFAULT_PORT == 8501


def test_marketplace_interface_and_disabled_skeletons() -> None:
    assert inspect.isabstract(multi_marketplace.MarketplaceAdapter)
    selected, configs = multi_marketplace.load_marketplace_config(
        Path("scripts/shopee/config.yaml")
    )
    assert selected == "shopee"
    assert configs["shopee"].enabled is True
    assert configs["lazada"].enabled is False
    assert configs["tiktok_shop"].status == "skeleton"

    lazada = multi_marketplace.LazadaAdapter(configs["lazada"])
    tiktok = multi_marketplace.TikTokShopAdapter(configs["tiktok_shop"])
    with pytest.raises(NotImplementedError, match="skeleton"):
        lazada.search_products("desk lamp")
    with pytest.raises(NotImplementedError, match="skeleton"):
        tiktok.search_products("desk lamp")


def test_ab_weight_experiment_compares_configurations_in_markdown(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    _write_note(vault / "products/product.md", _product_frontmatter())
    experiment_path = tmp_path / "weights.yaml"
    experiment_path.write_text(
        yaml.safe_dump(
            {
                "name": "demand-vs-content",
                "configurations": {
                    "baseline": {
                        "demand_score": 25,
                        "trend_velocity_score": 20,
                        "marketplace_rank_score": 15,
                        "commission_score": 15,
                        "content_fit_score": 10,
                        "competition_gap_score": 10,
                        "risk_score": 5,
                    },
                    "content_heavy": {
                        "weights": {
                            "demand_score": 15,
                            "trend_velocity_score": 15,
                            "marketplace_rank_score": 10,
                            "commission_score": 10,
                            "content_fit_score": 35,
                            "competition_gap_score": 10,
                            "risk_penalty_inverse": 5,
                        }
                    },
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    name, configurations = ab_test_weights.load_experiment(experiment_path)
    results = ab_test_weights.run_experiment(vault, configurations)
    report = ab_test_weights.render_report(name, configurations, results, TIMESTAMP)

    assert set(results) == {"baseline", "content_heavy"}
    assert results["baseline"][0]["product_id"] == "prod-phase7"
    assert results["baseline"][0]["product_opportunity_score"] != results["content_heavy"][0]["product_opportunity_score"]
    assert "## Side-by-Side Results" in report
    assert "baseline Score" in report
    assert "content_heavy Decision" in report
    assert "This report changes no product notes" in report
