#!/usr/bin/env python3
"""Phase 4A Local Read-only UI Mock generator.

Builds ONE self-contained static HTML file from existing read-only artifacts
(Phase 3B portfolio, Phase 3A dashboards, Phase 2E score JSON fallback). It
reads only generated artifacts — never the vault — and writes only the output
HTML. The page has inline CSS, zero JavaScript, and no external resources.

Reuses frontmatter parsing, guardrails, and scrubbing from dashboard_summary so
there is a single source of truth for the safety rules.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any

from dashboard_summary import (
    DashboardError,
    WEEK_RE,
    _check_guardrails,
    _fm_str,
    _now_utc,
    _safe_frontmatter,
    assert_clean,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

PORTFOLIO_DIR = REPO_ROOT / "tmp" / "phase3b-portfolio-dashboard"
DASHBOARD_DIR = REPO_ROOT / "tmp" / "phase3a-dashboard"
SCORES_DIR = REPO_ROOT / "tmp" / "phase2e-import-score-report" / "scores"
DEFAULT_OUT = REPO_ROOT / "tmp" / "phase4a-ui" / "index.html"

PRODUCT_ID_RE = re.compile(r"^[a-z0-9-]+$")
VALID_DECISIONS = ("launch", "small_batch_test", "watchlist", "reject")
DECISION_HEADINGS = {
    "launch": "Launch",
    "small_batch_test": "Small Batch Test",
    "watchlist": "Watchlist",
    "reject": "Reject",
}

PER_PRODUCT_FIELDS = (
    "report_status",
    "hermes_summary_status",
    "governance_summary_status",
    "promote_status",
    "decision_status",
    "finalization_status",
    "next_allowed_action",
)

COUNT_KEYS = (
    "total_products",
    "launch_count",
    "small_batch_test_count",
    "watchlist_count",
    "reject_count",
    "promoted_count",
    "decision_draft_count",
    "decision_complete_count",
)


def esc(value: Any) -> str:
    if value is None:
        return "&mdash;"
    return html.escape(str(value))


def _int_or_none(frontmatter: dict[str, Any] | None, key: str) -> int | None:
    text = _fm_str(frontmatter, key)
    if text is None:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def gather_products(week: str) -> dict[str, dict[str, Any]]:
    """Collect per-product records: Phase 3A artifacts first, score JSON fallback.

    Never carries score JSON input_path or note_refs.
    """
    records: dict[str, dict[str, Any]] = {}

    for path in sorted(DASHBOARD_DIR.glob(f"dashboard-*-{week}.md")):
        fm = _safe_frontmatter(path)
        if not fm:
            continue
        product_id = _fm_str(fm, "product_id")
        if product_id is None or not PRODUCT_ID_RE.match(product_id):
            continue
        record = {
            "product_id": product_id,
            "product_name": _fm_str(fm, "product_name"),
            "score": fm.get("product_opportunity_score"),
            "score_decision": _fm_str(fm, "score_decision"),
            "confidence_score": fm.get("confidence_score"),
            "source": "phase3a",
        }
        for field in PER_PRODUCT_FIELDS:
            record[field] = _fm_str(fm, field)
        records[product_id] = record

    if SCORES_DIR.is_dir():
        for path in sorted(SCORES_DIR.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            if not isinstance(data, dict):
                continue
            product_id = str(data.get("product_id", "")).strip()
            if not PRODUCT_ID_RE.match(product_id) or product_id in records:
                continue
            records[product_id] = {
                "product_id": product_id,
                "product_name": str(data.get("product_name", "")).strip() or None,
                "score": data.get("product_opportunity_score"),
                "score_decision": str(data.get("score_decision", "")).strip() or None,
                "confidence_score": data.get("confidence_score"),
                "source": "score_json",
            }

    return records


def _score_key(record: dict[str, Any]) -> tuple[float, str]:
    score = record.get("score")
    try:
        numeric = float(score)
    except (TypeError, ValueError):
        numeric = float("-inf")
    return (-numeric, record["product_id"])


def build_model(week: str) -> dict[str, Any]:
    records = gather_products(week)
    portfolio_fm = _safe_frontmatter(PORTFOLIO_DIR / f"portfolio-{week}.md")

    ranked = sorted(records.values(), key=_score_key)
    top_n = _int_or_none(portfolio_fm, "top_n") or 10

    # Counts: prefer the scrubbed Phase 3B artifact; otherwise derive what we can.
    counts: dict[str, Any] = {}
    if portfolio_fm is not None:
        for key in COUNT_KEYS:
            counts[key] = _int_or_none(portfolio_fm, key)
    else:
        counts["total_products"] = len(ranked)
        for decision in VALID_DECISIONS:
            counts[f"{decision}_count"] = sum(1 for r in ranked if r["score_decision"] == decision)
        # Promotion/decision counts come ONLY from the Phase 3B artifact.
        counts["promoted_count"] = None
        counts["decision_draft_count"] = None
        counts["decision_complete_count"] = None

    has_artifacts = portfolio_fm is not None or bool(ranked)

    return {
        "week": week,
        "counts": counts,
        "top_n": top_n,
        "top": ranked[:top_n],
        "ranked": ranked,
        "cards": sorted(records.values(), key=lambda r: r["product_id"]),
        "has_artifacts": has_artifacts,
    }


PAGE_CSS = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
  margin: 0; padding: 0 0 3rem; color: #1b1b1f; background: #f5f6f8; }
header { background: #1f2a44; color: #fff; padding: 1.25rem 1.5rem; }
header h1 { margin: 0 0 .25rem; font-size: 1.25rem; }
.badge { display: inline-block; background: #b3261e; color: #fff;
  font-weight: 600; padding: .15rem .55rem; border-radius: .35rem; font-size: .8rem; }
.notice { background: #fff3cd; color: #664d03; border: 1px solid #ffe69c;
  margin: 1rem 1.5rem; padding: .75rem 1rem; border-radius: .4rem; }
main { padding: 1rem 1.5rem; max-width: 1000px; }
section { background: #fff; border: 1px solid #e3e5e9; border-radius: .5rem;
  padding: 1rem 1.25rem; margin-bottom: 1.25rem; }
h2 { font-size: 1.05rem; margin: 0 0 .75rem; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: .6rem; }
.metric { background: #f0f2f6; border-radius: .4rem; padding: .55rem .7rem; }
.metric .k { font-size: .72rem; color: #5a5f6a; text-transform: uppercase; letter-spacing: .03em; }
.metric .v { font-size: 1.3rem; font-weight: 700; }
table { width: 100%; border-collapse: collapse; font-size: .9rem; }
th, td { text-align: left; padding: .4rem .5rem; border-bottom: 1px solid #eceef2; }
th { color: #5a5f6a; font-size: .75rem; text-transform: uppercase; }
.card { border: 1px solid #e3e5e9; border-radius: .45rem; padding: .8rem 1rem; margin-bottom: .75rem; }
.card h3 { margin: 0 0 .5rem; font-size: .98rem; }
.kv { display: grid; grid-template-columns: max-content 1fr; gap: .15rem .8rem; font-size: .85rem; }
.kv .k { color: #5a5f6a; }
.bucket { margin-bottom: .6rem; }
.bucket h3 { font-size: .9rem; margin: 0 0 .25rem; }
footer { color: #5a5f6a; font-size: .8rem; padding: 0 1.5rem; max-width: 1000px; }
""".strip()


def _metric(label: str, value: Any) -> str:
    return f'<div class="metric"><div class="k">{esc(label)}</div><div class="v">{esc(value)}</div></div>'


def render_html(model: dict[str, Any], generated_at: str) -> str:
    week = model["week"]
    counts = model["counts"]
    parts: list[str] = []

    parts.append("<!doctype html>")
    parts.append('<html lang="en">')
    parts.append("<head>")
    parts.append('<meta charset="utf-8">')
    parts.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    parts.append(f"<title>Product Intelligence UI Mock &mdash; {esc(week)}</title>")
    parts.append(f"<style>{PAGE_CSS}</style>")
    parts.append("</head>")
    parts.append("<body>")

    # Header
    parts.append("<header>")
    parts.append("<h1>Affiliate Product Intelligence OS</h1>")
    parts.append(f"<div>Report week: {esc(week)}</div>")
    parts.append('<div class="badge">READ-ONLY MOCK &mdash; no live actions</div>')
    parts.append("</header>")

    if not model["has_artifacts"]:
        parts.append(f'<div class="notice">no artifacts for {esc(week)}</div>')

    parts.append("<main>")

    # Portfolio overview
    parts.append("<section>")
    parts.append("<h2>Portfolio overview</h2>")
    parts.append('<div class="grid">')
    for key in COUNT_KEYS:
        parts.append(_metric(key, counts.get(key)))
    parts.append("</div>")
    parts.append("</section>")

    # Top products
    parts.append("<section>")
    parts.append(f"<h2>Top products (top {esc(model['top_n'])})</h2>")
    parts.append("<table>")
    parts.append(
        "<tr><th>rank</th><th>product_id</th><th>product_name</th>"
        "<th>score</th><th>score_decision</th><th>confidence</th></tr>"
    )
    if model["top"]:
        for rank, record in enumerate(model["top"], start=1):
            parts.append(
                f"<tr><td>{rank}</td><td>{esc(record['product_id'])}</td>"
                f"<td>{esc(record['product_name'])}</td><td>{esc(record['score'])}</td>"
                f"<td>{esc(record['score_decision'])}</td><td>{esc(record['confidence_score'])}</td></tr>"
            )
    else:
        parts.append('<tr><td colspan="6">No products.</td></tr>')
    parts.append("</table>")
    parts.append("</section>")

    # By decision
    parts.append("<section>")
    parts.append("<h2>By decision</h2>")
    for decision in VALID_DECISIONS:
        members = [r for r in model["ranked"] if r["score_decision"] == decision]
        parts.append('<div class="bucket">')
        parts.append(f"<h3>{esc(DECISION_HEADINGS[decision])}</h3>")
        if members:
            parts.append("<ul>")
            for record in members:
                parts.append(
                    f"<li>{esc(record['product_id'])} &mdash; {esc(record['product_name'])} "
                    f"(score {esc(record['score'])}, confidence {esc(record['confidence_score'])})</li>"
                )
            parts.append("</ul>")
        else:
            parts.append("<div>None</div>")
        parts.append("</div>")
    parts.append("</section>")

    # Per-product cards
    parts.append("<section>")
    parts.append("<h2>Per-product pipeline</h2>")
    if model["cards"]:
        for record in model["cards"]:
            parts.append('<div class="card">')
            parts.append(f"<h3>{esc(record['product_name'])} ({esc(record['product_id'])})</h3>")
            parts.append('<div class="kv">')
            rows = [
                ("product_opportunity_score", record.get("score")),
                ("score_decision", record.get("score_decision")),
                ("confidence_score", record.get("confidence_score")),
            ]
            for field in PER_PRODUCT_FIELDS:
                rows.append((field, record.get(field)))
            for key, value in rows:
                parts.append(f'<div class="k">{esc(key)}</div><div>{esc(value)}</div>')
            parts.append("</div>")
            parts.append("</div>")
    else:
        parts.append("<div>No per-product data.</div>")
    parts.append("</section>")

    parts.append("</main>")

    # Footer
    parts.append("<footer>")
    parts.append(f"<div>generated_at: {esc(generated_at)}</div>")
    parts.append("<div>generated from tmp artifacts</div>")
    parts.append(
        "<div>Guardrails: no database, no FastAPI, no backend, no external APIs, "
        "no vault writes, no approval mutation, no campaign launch.</div>"
    )
    parts.append("</footer>")

    parts.append("</body>")
    parts.append("</html>")

    return "\n".join(parts) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 4A local read-only UI mock generator.")
    parser.add_argument("--week", required=True)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        _check_guardrails()
        if not WEEK_RE.match(args.week):
            raise DashboardError(f"week must match ^[0-9]{{4}}-W[0-9]{{2}}$, got: {args.week!r}")

        model = build_model(args.week)
        generated_at = _now_utc()
        page = render_html(model, generated_at)

        assert_clean(page)

        out_path = Path(args.out)
        if not out_path.is_absolute():
            out_path = REPO_ROOT / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(page, encoding="utf-8")
    except DashboardError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    rel = out_path.relative_to(REPO_ROOT) if out_path.is_relative_to(REPO_ROOT) else out_path
    print(f"ui_mock_path: {rel}")
    print("phase4a_status: success")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
