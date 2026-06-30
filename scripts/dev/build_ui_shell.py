#!/usr/bin/env python3
"""Phase 5B Local Static UI Shell Prototype generator.

Builds ONE self-contained, read-only static HTML shell that summarizes the
Phase 4 demo pipeline (4E readiness, 4B snapshot, 4C catalog, 4D verification)
and links to the existing local static Phase 4 outputs with relative links.

Read-only: reads only four Phase 4 JSON summary files, never the vault, never
raw score JSON, never Phase 3 artifacts, and never raw Phase 4 HTML bodies. It
writes only under tmp/phase5b-ui-shell/, calls no external services, and emits
no JavaScript.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

# Make the shared helpers importable whether run as a script or imported.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dashboard_summary import (  # noqa: E402
    AFFILIATE_URL_PATTERNS,
    CONTENT_MARKERS,
    PRIVATE_VAULT_PATHS,
    SECRET_RES,
    WEEK_RE,
    DashboardError,
    _now_utc,
)

OUT_DEFAULT_REL = "tmp/phase5b-ui-shell/index.html"
OUT_GUARD_DIR = REPO_ROOT / "tmp" / "phase5b-ui-shell"

# Phase 4 JSON summary sources (the ONLY inputs this tool may read).
SOURCES = {
    "phase4e": REPO_ROOT / "tmp/phase4e-demo-bundle/demo-bundle-summary.json",
    "phase4b": REPO_ROOT / "tmp/phase4b-ui-snapshot/manifest.json",
    "phase4c": REPO_ROOT / "tmp/phase4c-snapshot-catalog/catalog.json",
    "phase4d": REPO_ROOT / "tmp/phase4d-demo-verifier/verification-summary.json",
}

# Relative links to existing local static Phase 4 files (rendered only if present).
LINK_TARGETS = (
    ("phase4b-ui-snapshot/index.html", "Phase 4B snapshot"),
    ("phase4c-snapshot-catalog/index.html", "Phase 4C catalog"),
    ("phase4d-demo-verifier/verification-report.md", "Phase 4D verification report"),
    ("phase4e-demo-bundle/DEMO_BUNDLE.md", "Phase 4E demo bundle"),
)

# Composed so this denylist source line does not itself contain the contiguous
# operator path literal (keeps the CI-C hardcoded-path guard green).
OPERATOR_PATH = "/home/ubuntu/" + "Affiliate-Ai"

# Forbidden substrings/regexes for the self-contained, zero-JS guarantee.
FORBIDDEN_SUBSTRINGS = (
    "http://",
    "https://",
    "file://",
    OPERATOR_PATH,
    "<script",
    "fetch(",
    "XMLHttpRequest",
    "import(",
    "<iframe",
    "<form",
    "<link",
)
EVENT_HANDLER_RE = re.compile(r"<[^>]*\son[a-z]+\s*=", re.IGNORECASE)


def esc(value: Any) -> str:
    return html.escape(str(value))


def assert_static_shell_clean(page: str) -> None:
    """Refuse to write a page that violates the static read-only boundary."""
    for pattern in PRIVATE_VAULT_PATHS:
        if pattern in page:
            raise DashboardError(f"output contains private vault path: {pattern}")
    for pattern in AFFILIATE_URL_PATTERNS:
        if pattern in page:
            raise DashboardError(f"output contains affiliate tracking pattern: {pattern}")
    for pattern in CONTENT_MARKERS:
        if pattern in page:
            raise DashboardError(f"output contains affiliate content marker: {pattern}")
    for regex in SECRET_RES:
        if regex.search(page):
            raise DashboardError("output contains a secret pattern")
    for pattern in FORBIDDEN_SUBSTRINGS:
        if pattern in page:
            raise DashboardError(f"output contains forbidden token: {pattern}")
    if EVENT_HANDLER_RE.search(page):
        raise DashboardError("output contains an inline event handler attribute")


def _load(name: str) -> tuple[dict[str, Any] | None, str]:
    """Return (data, status). status is 'present' or 'missing'. Invalid -> raise."""
    path = SOURCES[name]
    if not path.is_file():
        return None, "missing"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DashboardError(f"invalid JSON in {name} source: {exc}") from exc
    if not isinstance(data, dict):
        raise DashboardError(f"{name} source is not a JSON object")
    return data, "present"


def _missing_notice(name: str) -> str:
    return (
        f'<p class="notice">{esc(name)} output not found '
        "&mdash; run run_phase4e_demo_bundle.sh &lt;week&gt;</p>"
    )


def _week_mismatch_notice(label: str, found: Any, requested: str) -> str:
    return (
        f'<p class="warn">{esc(label)} report_week is {esc(found)}, '
        f"requested {esc(requested)} &mdash; data may be stale</p>"
    )


def _kv(label: str, value: Any) -> str:
    return f'<div class="kv"><span class="k">{esc(label)}</span>' f'<span class="v">{esc(value)}</span></div>'


def _badge(label: str, value: Any) -> str:
    ok = str(value).upper() in ("PASS", "READY", "SUCCESS", "TRUE")
    cls = "ok" if ok else "no"
    return f'<span class="badge {cls}">{esc(label)}: {esc(value)}</span>'


def _bool_row(label: str, value: Any) -> str:
    cls = "ok" if value is True else "no"
    text = "true" if value is True else ("false" if value is False else str(value))
    return f'<div class="kv"><span class="k">{esc(label)}</span>' f'<span class="v {cls}">{esc(text)}</span></div>'


def render_demo_readiness(data: dict[str, Any] | None, status: str, week: str) -> str:
    if status == "missing" or data is None:
        return _missing_notice("phase4e")
    parts = ['<div class="card-body">']
    parts.append(_kv("status", data.get("status", "unknown")))
    report_week = data.get("report_week")
    if report_week is not None:
        parts.append(_kv("report_week", report_week))
        if report_week != week:
            parts.append(_week_mismatch_notice("Phase 4E", report_week, week))
    steps = data.get("steps", {})
    if isinstance(steps, dict) and steps:
        parts.append('<div class="badges">')
        for step in ("acceptance", "snapshot", "catalog", "verifier"):
            if step in steps:
                parts.append(_badge(step, steps[step]))
        parts.append("</div>")
    guardrails = data.get("guardrails", {})
    if isinstance(guardrails, dict) and guardrails:
        parts.append('<p class="sub">guardrails</p>')
        for key in sorted(guardrails):
            parts.append(_bool_row(key, guardrails[key]))
    parts.append("</div>")
    return "".join(parts)


def render_snapshot(data: dict[str, Any] | None, status: str, week: str) -> str:
    if status == "missing" or data is None:
        return _missing_notice("phase4b")
    parts = ['<div class="card-body">']
    report_week = data.get("report_week")
    if report_week is not None:
        parts.append(_kv("report_week", report_week))
        if report_week != week:
            parts.append(_week_mismatch_notice("Phase 4B", report_week, week))
    parts.append(_kv("generated_at", data.get("generated_at", "unknown")))
    files = data.get("files", [])
    parts.append(_kv("file_count", len(files) if isinstance(files, list) else "unknown"))
    summary = data.get("source_summary", {})
    if isinstance(summary, dict):
        for key in sorted(summary):
            if isinstance(summary[key], bool):
                parts.append(_bool_row(key, summary[key]))
            else:
                parts.append(_kv(key, summary[key]))
    parts.append("</div>")
    return "".join(parts)


def render_catalog(data: dict[str, Any] | None, status: str) -> str:
    if status == "missing" or data is None:
        return _missing_notice("phase4c")
    parts = ['<div class="card-body">']
    parts.append(_kv("snapshot_count", data.get("snapshot_count", "unknown")))
    parts.append(_kv("skipped_count", data.get("skipped_count", "unknown")))
    snapshots = data.get("snapshots", [])
    if isinstance(snapshots, list) and snapshots:
        parts.append(
            '<table><thead><tr><th>source_dir</th><th>report_week</th>'
            "<th>file_count</th><th>total_bytes</th></tr></thead><tbody>"
        )
        for snap in snapshots:
            if not isinstance(snap, dict):
                continue
            parts.append(
                "<tr>"
                f"<td>{esc(snap.get('source_dir', ''))}</td>"
                f"<td>{esc(snap.get('report_week', ''))}</td>"
                f"<td>{esc(snap.get('file_count', ''))}</td>"
                f"<td>{esc(snap.get('total_bytes', ''))}</td>"
                "</tr>"
            )
        parts.append("</tbody></table>")
    parts.append("</div>")
    return "".join(parts)


def render_verification(data: dict[str, Any] | None, status: str) -> str:
    if status == "missing" or data is None:
        return _missing_notice("phase4d")
    parts = ['<div class="card-body">']
    parts.append(_kv("status", data.get("status", "unknown")))
    checked = data.get("checked_paths", [])
    if isinstance(checked, list) and checked:
        parts.append(_kv("checked_paths", len(checked)))
    safety = data.get("safety", {})
    if isinstance(safety, dict) and safety:
        parts.append('<p class="sub">safety</p>')
        for key in sorted(safety):
            parts.append(_bool_row(key, safety[key]))
    vault = data.get("vault", {})
    if isinstance(vault, dict) and vault:
        parts.append('<p class="sub">vault</p>')
        for key in sorted(vault):
            parts.append(_bool_row(key, vault[key]))
    parts.append("</div>")
    return "".join(parts)


def render_links() -> str:
    parts = ['<div class="card-body">']
    found = False
    for rel_target, label in LINK_TARGETS:
        if (REPO_ROOT / "tmp" / rel_target).exists():
            found = True
            parts.append(f'<div><a href="../{esc(rel_target)}">{esc(label)}</a></div>')
    if not found:
        parts.append('<p class="notice">no local Phase 4 outputs found to link</p>')
    parts.append("</div>")
    return "".join(parts)


CSS = (
    "body{font-family:system-ui,Arial,sans-serif;margin:0;background:#f4f5f7;color:#1a1a1a}"
    "header{background:#10243e;color:#fff;padding:18px 24px}"
    "header h1{margin:0 0 6px;font-size:20px}"
    ".badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:12px;margin:2px 4px 2px 0}"
    ".badge.ok{background:#1f7a3d;color:#fff}.badge.no{background:#9a2a2a;color:#fff}"
    ".tag{background:#c0392b;color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:700}"
    "main{padding:20px 24px;max-width:960px}"
    ".card{background:#fff;border:1px solid #dcdfe4;border-radius:8px;margin:0 0 16px;overflow:hidden}"
    ".card h2{margin:0;padding:12px 16px;background:#eef1f5;font-size:15px;border-bottom:1px solid #dcdfe4}"
    ".card-body{padding:12px 16px}"
    ".kv{display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px dotted #eee}"
    ".kv .k{color:#555}.kv .v{font-weight:600}.v.ok{color:#1f7a3d}.v.no{color:#9a2a2a}"
    ".sub{margin:10px 0 4px;font-weight:700;color:#333;font-size:13px}"
    "table{width:100%;border-collapse:collapse;font-size:13px}"
    "th,td{text-align:left;padding:6px 8px;border-bottom:1px solid #eee}th{background:#f7f8fa}"
    ".notice{background:#fff6e0;border:1px solid #e6c200;padding:8px 10px;border-radius:6px;color:#6a5200}"
    ".warn{background:#fdeaea;border:1px solid #d88;padding:6px 10px;border-radius:6px;color:#7a2a2a;font-size:13px}"
    "a{color:#10243e}"
    "footer{padding:14px 24px;color:#555;font-size:12px;border-top:1px solid #dcdfe4}"
    "footer li{margin:2px 0}"
)


def build_page(week: str) -> str:
    e4, s4 = _load("phase4e")
    b4, sb = _load("phase4b")
    c4, sc = _load("phase4c")
    d4, sd = _load("phase4d")

    all_missing = all(s == "missing" for s in (s4, sb, sc, sd))
    generated_at = _now_utc()

    parts: list[str] = []
    parts.append("<!doctype html>")
    parts.append('<html lang="en"><head><meta charset="utf-8">')
    parts.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    parts.append("<title>UI Shell</title>")
    parts.append(f"<style>{CSS}</style></head><body>")

    parts.append("<header>")
    parts.append("<h1>Affiliate Product Intelligence OS</h1>")
    parts.append('<span class="tag">READ-ONLY SHELL</span> ')
    parts.append('<span class="badge no">no live actions</span>')
    parts.append(f'<div class="kv"><span class="k">report week</span><span class="v">{esc(week)}</span></div>')
    parts.append(f'<div class="kv"><span class="k">generated</span><span class="v">{esc(generated_at)}</span></div>')
    parts.append("</header><main>")

    if all_missing:
        parts.append(
            '<p class="notice">no Phase 4 outputs found &mdash; '
            "run run_phase4e_demo_bundle.sh &lt;week&gt; first</p>"
        )

    parts.append(f'<section class="card"><h2>Demo readiness (Phase 4E)</h2>{render_demo_readiness(e4, s4, week)}</section>')
    parts.append(f'<section class="card"><h2>Snapshot status (Phase 4B)</h2>{render_snapshot(b4, sb, week)}</section>')
    parts.append(f'<section class="card"><h2>Catalog status (Phase 4C)</h2>{render_catalog(c4, sc)}</section>')
    parts.append(f'<section class="card"><h2>Verification status (Phase 4D)</h2>{render_verification(d4, sd)}</section>')
    parts.append(f'<section class="card"><h2>Local links</h2>{render_links()}</section>')

    parts.append("</main><footer><strong>Guardrails:</strong><ul>")
    for line in (
        "local static only",
        "read-only",
        "no backend",
        "no API",
        "no vault writes",
        "no external URLs",
        "no approval workflow",
    ):
        parts.append(f"<li>{esc(line)}</li>")
    parts.append("</ul></footer></body></html>")
    return "".join(parts)


def _resolve_out(out_arg: str) -> Path:
    out_path = Path(out_arg)
    if not out_path.is_absolute():
        out_path = REPO_ROOT / out_path
    out_path = out_path.resolve()
    guard = OUT_GUARD_DIR.resolve()
    if out_path != guard and guard not in out_path.parents:
        raise DashboardError(f"refusing to write outside {OUT_GUARD_DIR}: {out_path}")
    return out_path


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 5B local static UI shell generator (read-only).")
    parser.add_argument("--week", required=True)
    parser.add_argument("--out", default=OUT_DEFAULT_REL)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        if not WEEK_RE.match(args.week):
            raise DashboardError(f"week must match {WEEK_RE.pattern}, got: {args.week}")
        out_path = _resolve_out(args.out)
        page = build_page(args.week)
        assert_static_shell_clean(page)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(page, encoding="utf-8")
    except DashboardError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    rel = out_path.relative_to(REPO_ROOT) if out_path.is_relative_to(REPO_ROOT) else out_path
    print(f"ui_shell_path: {rel}")
    print("phase5b_status: success")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
