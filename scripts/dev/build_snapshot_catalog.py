#!/usr/bin/env python3
"""Phase 4C Static UI Snapshot Catalog / Multi-snapshot Index.

Builds a static catalog over Phase 4B snapshot manifests. It reads only
`tmp/phase4b-ui-snapshot*/manifest.json` (metadata), never the vault, never raw
artifacts, and never the Phase 4B HTML body. It copies no snapshot files; it
summarizes metadata and emits a self-contained static catalog.

Read-only: writes only under the catalog directory; no vault, no external calls,
no server/router/approval surface.
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any

from dashboard_summary import (
    AFFILIATE_URL_PATTERNS,
    PRIVATE_VAULT_PATHS,
    SECRET_RES,
    WEEK_RE,
    DashboardError,
    _check_guardrails,
    _now_utc,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
TMP_DIR = REPO_ROOT / "tmp"
DEFAULT_OUT = TMP_DIR / "phase4c-snapshot-catalog"

SNAPSHOT_GLOB = "phase4b-ui-snapshot*/manifest.json"
CATALOG_FILES = ("index.html", "catalog.json", "README.md", "GUARDRAILS.md")
GUARDED_SUFFIX = "tmp/phase4c-snapshot-catalog"

# Affiliate-content field markers that must never leak. "autopublish" is omitted
# on purpose: GUARDRAILS must state "no autopublish" (a policy negation).
SNAPSHOT_CONTENT_MARKERS = (
    "content_draft",
    "campaign_copy",
    "tiktok_script",
    "hook_text",
    "blog_post",
)

GUARDRAILS = (
    "no database",
    "no FastAPI",
    "no backend service",
    "no external APIs",
    "no external URLs",
    "no affiliate content generation",
    "no autopublish",
    "no campaign launch",
    "no vault reads",
    "no vault writes",
    "no approval mutation",
    "no Phase 2G/2H/2I triggering",
    "no marketplace connector",
    "no raw artifact export",
    "read-only only",
)


def esc(value: Any) -> str:
    return html.escape(str(value)) if value is not None else "&mdash;"


def _scrub(text: str) -> None:
    for pattern in PRIVATE_VAULT_PATHS:
        if pattern in text:
            raise DashboardError(f"catalog file contains private vault path: {pattern}")
    for pattern in AFFILIATE_URL_PATTERNS:
        if pattern in text:
            raise DashboardError(f"catalog file contains affiliate tracking pattern: {pattern}")
    for pattern in SNAPSHOT_CONTENT_MARKERS:
        if pattern in text:
            raise DashboardError(f"catalog file contains affiliate content marker: {pattern}")
    for regex in SECRET_RES:
        if regex.search(text):
            raise DashboardError("catalog file contains a secret pattern")
    for pattern in ("http://", "https://"):
        if pattern in text:
            raise DashboardError(f"catalog file contains an external URL pattern: {pattern}")


def _guarded_out_dir(out: str) -> Path:
    out_path = Path(out)
    if not out_path.is_absolute():
        out_path = REPO_ROOT / out_path
    resolved = out_path.resolve()
    if resolved != DEFAULT_OUT.resolve() and not str(resolved).endswith(GUARDED_SUFFIX):
        raise DashboardError(
            f"refusing to use unguarded output directory: {resolved} "
            f"(must be {DEFAULT_OUT} or end with {GUARDED_SUFFIX})"
        )
    return resolved


def _clear_known_files(out_dir: Path) -> None:
    for name in CATALOG_FILES:
        (out_dir / name).unlink(missing_ok=True)


def _parse_manifest(path: Path) -> dict[str, Any] | None:
    """Return a catalog snapshot entry, or None to skip (with a stderr warning)."""
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"warning: skipping unreadable manifest {path}: {exc}", file=sys.stderr)
        return None
    if not isinstance(manifest, dict) or manifest.get("type") != "phase4b_ui_snapshot":
        print(f"warning: skipping non-phase4b manifest {path}", file=sys.stderr)
        return None

    source_summary = manifest.get("source_summary")
    if not isinstance(source_summary, dict):
        source_summary = {}
    if source_summary.get("vault_included") is True:
        print(f"warning: skipping unsafe manifest (vault_included=true) {path}", file=sys.stderr)
        return None

    files = manifest.get("files")
    if not isinstance(files, list):
        files = []

    file_count = len(files)
    total_bytes = 0
    index_sha256 = ""
    for entry in files:
        if not isinstance(entry, dict):
            continue
        try:
            total_bytes += int(entry.get("bytes", 0))
        except (TypeError, ValueError):
            pass
        if entry.get("name") == "index.html":
            index_sha256 = str(entry.get("sha256", ""))

    report_week = str(manifest.get("report_week", "")).strip()
    if not WEEK_RE.match(report_week):
        report_week = "unknown"

    source_dir = path.parent
    rel_dir = source_dir.relative_to(REPO_ROOT).as_posix() if source_dir.is_relative_to(REPO_ROOT) else source_dir.name

    return {
        "source_dir": rel_dir,
        "report_week": report_week,
        "generated_at": str(manifest.get("generated_at", "")),
        "file_count": file_count,
        "total_bytes": total_bytes,
        "index_sha256": index_sha256,
        "source_summary": {
            "portfolio_artifact": str(source_summary.get("portfolio_artifact", "absent")),
            "product_dashboards": int(source_summary.get("product_dashboards", 0) or 0),
            "score_files": int(source_summary.get("score_files", 0) or 0),
            "vault_included": False,
        },
    }


def build_catalog_model() -> dict[str, Any]:
    snapshots: list[dict[str, Any]] = []
    skipped = 0
    for manifest_path in sorted(TMP_DIR.glob(SNAPSHOT_GLOB)):
        entry = _parse_manifest(manifest_path)
        if entry is None:
            skipped += 1
            continue
        snapshots.append(entry)

    snapshots.sort(key=lambda s: (s["report_week"], s["source_dir"]))

    return {
        "type": "phase4c_snapshot_catalog",
        "generated_at": _now_utc(),
        "snapshot_count": len(snapshots),
        "skipped_count": skipped,
        "snapshots": snapshots,
    }


PAGE_CSS = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
  margin: 0; padding: 0 0 3rem; color: #1b1b1f; background: #f5f6f8; }
header { background: #1f2a44; color: #fff; padding: 1.25rem 1.5rem; }
header h1 { margin: 0 0 .25rem; font-size: 1.25rem; }
.badge { display: inline-block; background: #0b6b3a; color: #fff;
  font-weight: 600; padding: .15rem .55rem; border-radius: .35rem; font-size: .8rem; }
.notice { background: #fff3cd; color: #664d03; border: 1px solid #ffe69c;
  margin: 1rem 1.5rem; padding: .75rem 1rem; border-radius: .4rem; }
main { padding: 1rem 1.5rem; max-width: 1100px; }
section { background: #fff; border: 1px solid #e3e5e9; border-radius: .5rem;
  padding: 1rem 1.25rem; margin-bottom: 1.25rem; }
h2 { font-size: 1.05rem; margin: 0 0 .75rem; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: .6rem; }
.metric { background: #f0f2f6; border-radius: .4rem; padding: .55rem .7rem; }
.metric .k { font-size: .72rem; color: #5a5f6a; text-transform: uppercase; letter-spacing: .03em; }
.metric .v { font-size: 1.3rem; font-weight: 700; }
table { width: 100%; border-collapse: collapse; font-size: .88rem; }
th, td { text-align: left; padding: .4rem .5rem; border-bottom: 1px solid #eceef2; }
th { color: #5a5f6a; font-size: .72rem; text-transform: uppercase; }
code { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: .8rem; }
footer { color: #5a5f6a; font-size: .8rem; padding: 0 1.5rem; max-width: 1100px; }
""".strip()


def render_index_html(model: dict[str, Any]) -> str:
    parts: list[str] = []
    parts.append("<!doctype html>")
    parts.append('<html lang="en">')
    parts.append("<head>")
    parts.append('<meta charset="utf-8">')
    parts.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    parts.append("<title>Snapshot Catalog</title>")
    parts.append(f"<style>{PAGE_CSS}</style>")
    parts.append("</head>")
    parts.append("<body>")

    parts.append("<header>")
    parts.append("<h1>Affiliate Product Intelligence OS</h1>")
    parts.append("<div>Snapshot Catalog</div>")
    parts.append('<div class="badge">READ-ONLY CATALOG</div>')
    parts.append("</header>")

    if model["snapshot_count"] == 0:
        parts.append('<div class="notice">no snapshots found</div>')

    parts.append("<main>")

    parts.append("<section>")
    parts.append("<h2>Summary</h2>")
    parts.append('<div class="grid">')
    parts.append(f'<div class="metric"><div class="k">snapshot_count</div><div class="v">{esc(model["snapshot_count"])}</div></div>')
    parts.append(f'<div class="metric"><div class="k">skipped_count</div><div class="v">{esc(model["skipped_count"])}</div></div>')
    parts.append("</div>")
    parts.append("</section>")

    parts.append("<section>")
    parts.append("<h2>Snapshots</h2>")
    parts.append("<table>")
    parts.append(
        "<tr><th>report_week</th><th>source_dir</th><th>files</th><th>bytes</th>"
        "<th>index_sha256</th><th>portfolio</th><th>dashboards</th><th>scores</th><th>open</th></tr>"
    )
    if model["snapshots"]:
        for snap in model["snapshots"]:
            summary = snap["source_summary"]
            sha_short = snap["index_sha256"][:12]
            # Relative local link to the snapshot's index.html (one level up from
            # the catalog dir to the sibling snapshot dir).
            rel_href = f"../{Path(snap['source_dir']).name}/index.html"
            parts.append(
                "<tr>"
                f"<td>{esc(snap['report_week'])}</td>"
                f"<td><code>{esc(snap['source_dir'])}</code></td>"
                f"<td>{esc(snap['file_count'])}</td>"
                f"<td>{esc(snap['total_bytes'])}</td>"
                f"<td><code>{esc(sha_short)}</code></td>"
                f"<td>{esc(summary['portfolio_artifact'])}</td>"
                f"<td>{esc(summary['product_dashboards'])}</td>"
                f"<td>{esc(summary['score_files'])}</td>"
                f'<td><a href="{esc(rel_href)}">open</a></td>'
                "</tr>"
            )
    else:
        parts.append('<tr><td colspan="9">no snapshots found</td></tr>')
    parts.append("</table>")
    parts.append("</section>")

    parts.append("</main>")

    parts.append("<footer>")
    parts.append(f"<div>generated_at: {esc(model['generated_at'])}</div>")
    parts.append("<div>static metadata catalog</div>")
    parts.append("<div>no backend, no external URLs, no vault access, no approval mutation.</div>")
    parts.append("</footer>")

    parts.append("</body>")
    parts.append("</html>")
    return "\n".join(parts) + "\n"


def render_readme() -> str:
    return """# Snapshot Catalog

## Purpose

A static, read-only catalog over Phase 4B UI snapshot manifests. It summarizes
snapshot metadata only; it copies no snapshot files and reads no vault data.

## Exact command

```
bash scripts/dev/run_phase4c_snapshot_catalog.sh
```

## Generate a source snapshot first

```
bash scripts/dev/run_phase4b_ui_snapshot.sh 2026-W26
```

## How to open

Open `tmp/phase4c-snapshot-catalog/index.html` in a local browser. Each row links
to its snapshot's local `index.html` via a relative link. No server is required.

## What is included

- `catalog.json`
- `index.html`
- `README.md`
- `GUARDRAILS.md`

## What is NOT included

- no raw artifacts
- no score JSON
- no Phase 3A markdown
- no Phase 3B markdown
- no Phase 4B index copy
- no vault files
- no secrets
- no external URLs
- no backend
- no server

## Known limitations

- The catalog uses existing manifests; it does not regenerate snapshots.
- It is stale if the snapshot manifests are stale.
- There is no live refresh.
- There is no UI shell or router.
- There are no approval actions.
"""


def render_guardrails() -> str:
    lines = ["# Guardrails", "", "This catalog was produced under the following guardrails:", ""]
    lines += [f"- {item}" for item in GUARDRAILS]
    lines.append("")
    return "\n".join(lines)


def build_catalog(out: str) -> dict[str, Any]:
    out_dir = _guarded_out_dir(out)
    model = build_catalog_model()

    index_html = render_index_html(model)
    catalog_json = json.dumps(model, indent=2, sort_keys=False) + "\n"
    readme = render_readme()
    guardrails = render_guardrails()

    for payload in (index_html, catalog_json, readme, guardrails):
        _scrub(payload)

    out_dir.mkdir(parents=True, exist_ok=True)
    _clear_known_files(out_dir)
    (out_dir / "index.html").write_text(index_html, encoding="utf-8")
    (out_dir / "catalog.json").write_text(catalog_json, encoding="utf-8")
    (out_dir / "README.md").write_text(readme, encoding="utf-8")
    (out_dir / "GUARDRAILS.md").write_text(guardrails, encoding="utf-8")

    return {"out_dir": out_dir, "model": model}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 4C static UI snapshot catalog.")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        _check_guardrails()
        result = build_catalog(args.out)
    except DashboardError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    out_dir = result["out_dir"]
    rel = out_dir.relative_to(REPO_ROOT) if out_dir.is_relative_to(REPO_ROOT) else out_dir
    print(f"catalog_path: {rel}")
    for name in CATALOG_FILES:
        print(f"catalog_file: {name}")
    print("phase4c_status: success")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
