#!/usr/bin/env python3
"""Read-only local web dashboard for the Obsidian product portfolio.

The HTTP layer uses only Python's standard library and binds to loopback. Vault
notes are parsed on each request so the page reflects current local state.

Ref: codex/tasks/104-phase7-enhancement.md
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from collections import defaultdict
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.dev.score_product import score_product_note  # noqa: E402


DEFAULT_VAULT_DIR = REPO_ROOT / "vault"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8501
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)


def read_frontmatter(path: Path) -> dict[str, Any] | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None
    try:
        frontmatter = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return None
    return frontmatter if isinstance(frontmatter, dict) else None


def _score_payload(path: Path, frontmatter: dict[str, Any]) -> dict[str, Any] | None:
    score = frontmatter.get("product_opportunity_score")
    score_decision = str(frontmatter.get("score_decision", "")).strip()
    if not isinstance(score, bool) and isinstance(score, (int, float)) and score_decision:
        return {
            "product_id": str(frontmatter.get("product_id", "")),
            "product_name": str(frontmatter.get("product_name", "")),
            "marketplace": str(frontmatter.get("marketplace", "")),
            "product_opportunity_score": float(score),
            "score_decision": score_decision,
            "confidence_score": frontmatter.get("confidence_score", "—"),
        }
    try:
        return score_product_note(path)
    except (OSError, ValueError, TypeError):
        return None


def _latest_decisions(notes: list[tuple[Path, dict[str, Any]]]) -> dict[str, dict[str, Any]]:
    candidates: dict[str, list[tuple[Path, dict[str, Any]]]] = defaultdict(list)
    for path, frontmatter in notes:
        if frontmatter.get("type") != "decision":
            continue
        product_id = str(frontmatter.get("product_id", "")).strip()
        if product_id:
            candidates[product_id].append((path, frontmatter))

    latest: dict[str, dict[str, Any]] = {}
    for product_id, decisions in candidates.items():
        decisions.sort(
            key=lambda item: (
                item[1].get("status") == "complete",
                str(item[1].get("updated_at", "")),
                str(item[0]),
            ),
            reverse=True,
        )
        latest[product_id] = decisions[0][1]
    return latest


def _signal_week(value: Any) -> str | None:
    try:
        parsed = date.fromisoformat(str(value)[:10])
    except ValueError:
        return None
    year, week, _weekday = parsed.isocalendar()
    return f"{year}-W{week:02d}"


def collect_portfolio(vault_dir: Path) -> dict[str, list[dict[str, Any]]]:
    notes: list[tuple[Path, dict[str, Any]]] = []
    if vault_dir.is_dir():
        for path in sorted(vault_dir.rglob("*.md")):
            frontmatter = read_frontmatter(path)
            if frontmatter is not None:
                notes.append((path, frontmatter))

    decisions = _latest_decisions(notes)
    products: list[dict[str, Any]] = []
    reports: list[dict[str, Any]] = []
    trend_groups: dict[str, list[float]] = defaultdict(list)

    for path, frontmatter in notes:
        note_type = frontmatter.get("type")
        if note_type == "product_candidate":
            score = _score_payload(path, frontmatter)
            if score is None:
                continue
            product_id = str(score["product_id"])
            decision = decisions.get(product_id, {})
            products.append(
                {
                    "product_id": product_id,
                    "product_name": score.get("product_name", product_id),
                    "marketplace": score.get("marketplace", frontmatter.get("marketplace", "")),
                    "score": score["product_opportunity_score"],
                    "score_decision": score["score_decision"],
                    "final_decision": decision.get("final_decision", "—"),
                    "confidence": score.get("confidence_score", "—"),
                }
            )
        elif note_type == "weekly_report":
            reports.append(
                {
                    "week": frontmatter.get("report_week", "—"),
                    "candidates": frontmatter.get("candidate_count", 0),
                    "launch": frontmatter.get("launch_count", 0),
                    "small_batch_test": frontmatter.get("small_batch_test_count", 0),
                    "watchlist": frontmatter.get("watchlist_count", 0),
                    "reject": frontmatter.get("reject_count", 0),
                }
            )
        elif note_type == "trend_signal":
            week = _signal_week(frontmatter.get("signal_date"))
            value = frontmatter.get("trend_velocity_score")
            if week and isinstance(value, (int, float)) and not isinstance(value, bool):
                trend_groups[week].append(float(value))

    products.sort(key=lambda row: (-float(row["score"]), str(row["product_id"])))
    reports.sort(key=lambda row: str(row["week"]), reverse=True)
    trend_signals = [
        {"week": week, "signal_count": len(values), "average_score": round(sum(values) / len(values), 2)}
        for week, values in sorted(trend_groups.items(), reverse=True)
    ]
    return {"products": products, "reports": reports, "trend_signals": trend_signals}


def _cell(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _table(headers: list[str], rows: list[list[Any]], empty_message: str) -> str:
    header_html = "".join(f"<th>{_cell(header)}</th>" for header in headers)
    if rows:
        body_html = "".join(
            "<tr>" + "".join(f"<td>{_cell(value)}</td>" for value in row) + "</tr>"
            for row in rows
        )
    else:
        body_html = f'<tr><td colspan="{len(headers)}">{_cell(empty_message)}</td></tr>'
    return f"<table><thead><tr>{header_html}</tr></thead><tbody>{body_html}</tbody></table>"


def render_dashboard(vault_dir: Path) -> str:
    data = collect_portfolio(vault_dir)
    product_rows = [
        [
            row["product_id"],
            row["product_name"],
            row["marketplace"],
            f'{float(row["score"]):.2f}',
            row["score_decision"],
            row["final_decision"],
            row["confidence"],
        ]
        for row in data["products"]
    ]
    report_rows = [
        [
            row["week"],
            row["candidates"],
            row["launch"],
            row["small_batch_test"],
            row["watchlist"],
            row["reject"],
        ]
        for row in data["reports"]
    ]
    trend_rows = [
        [row["week"], row["signal_count"], f'{row["average_score"]:.2f}']
        for row in data["trend_signals"]
    ]
    return "".join(
        [
            "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">",
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">",
            "<title>Affiliate Product Portfolio</title>",
            "<style>body{font-family:system-ui,sans-serif;margin:2rem;color:#172033;background:#f6f8fb}",
            "main{max-width:1200px;margin:auto}h1,h2{color:#102a43}section{margin:2rem 0}",
            "table{border-collapse:collapse;width:100%;background:white;box-shadow:0 1px 4px #ccd4df}",
            "th,td{padding:.65rem;text-align:left;border-bottom:1px solid #e2e8f0}th{background:#e9f0f7}</style>",
            "</head><body><main><h1>Affiliate Product Portfolio</h1>",
            f"<p>Read-only local view · {_cell(len(product_rows))} scored products</p>",
            "<section><h2>Product Portfolio</h2>",
            _table(
                ["Product ID", "Product", "Marketplace", "Score", "Score Decision", "Final Decision", "Confidence"],
                product_rows,
                "No scoreable product_candidate notes found.",
            ),
            "</section><section><h2>Weekly Portfolio Trends</h2>",
            _table(
                ["Week", "Candidates", "Launch", "Small Batch Test", "Watchlist", "Reject"],
                report_rows,
                "No weekly_report notes found.",
            ),
            "</section><section><h2>Weekly Trend Signal Average</h2>",
            _table(
                ["Week", "Signals", "Average Trend Score"],
                trend_rows,
                "No dated trend_signal notes found.",
            ),
            "</section></main></body></html>",
        ]
    )


class PortfolioHandler(BaseHTTPRequestHandler):
    vault_dir = DEFAULT_VAULT_DIR

    def _serve_dashboard(self, *, include_body: bool) -> None:
        if self.path not in ("/", "/index.html"):
            self.send_error(404, "Not found")
            return
        payload = render_dashboard(self.vault_dir).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'")
        self.end_headers()
        if include_body:
            self.wfile.write(payload)

    def do_GET(self) -> None:  # noqa: N802 (stdlib handler contract)
        self._serve_dashboard(include_body=True)

    def do_HEAD(self) -> None:  # noqa: N802 (stdlib handler contract)
        self._serve_dashboard(include_body=False)

    def log_message(self, format: str, *args: Any) -> None:
        print(f"portfolio_web: {format % args}", file=sys.stderr)


def handler_for(vault_dir: Path) -> type[PortfolioHandler]:
    """Create a request-handler class bound to one vault directory."""

    class BoundPortfolioHandler(PortfolioHandler):
        pass

    BoundPortfolioHandler.vault_dir = vault_dir
    return BoundPortfolioHandler


def run_server(vault_dir: Path, port: int = DEFAULT_PORT) -> None:
    server = ThreadingHTTPServer((DEFAULT_HOST, port), handler_for(vault_dir))
    print(f"Portfolio dashboard: http://localhost:{port}")
    print(f"Vault: {vault_dir}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Serve the read-only local portfolio dashboard.")
    parser.add_argument("--vault-dir", type=Path, default=DEFAULT_VAULT_DIR)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.vault_dir.is_dir():
        print(f"Vault directory not found: {args.vault_dir}", file=sys.stderr)
        return 1
    if not 1 <= args.port <= 65535:
        print("port must be within 1-65535", file=sys.stderr)
        return 1
    run_server(args.vault_dir, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
