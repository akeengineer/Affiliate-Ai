#!/usr/bin/env python3
"""Phase 4B UI Snapshot Pack / Demo Export.

Packages the Phase 4A static UI mock into a deterministic local snapshot folder
with manifest, README, inventory, and guardrail statement. It regenerates the
Phase 4A mock first (safe source path), then copies only the scrubbed static
HTML — never raw score/dashboard/portfolio artifacts and never the vault.

Read-only: writes only under the snapshot directory; no vault, no external
calls, no server.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import sys
from pathlib import Path

import build_ui_mock
from dashboard_summary import (
    AFFILIATE_URL_PATTERNS,
    PRIVATE_VAULT_PATHS,
    SECRET_RES,
    DashboardError,
    WEEK_RE,
    _check_guardrails,
    _now_utc,
)

# Affiliate-content field markers that must never leak into the export. Note we
# deliberately exclude the word "autopublish": the GUARDRAILS statement must say
# "no autopublish", which is a policy negation, not leaked affiliate content.
SNAPSHOT_CONTENT_MARKERS = (
    "content_draft",
    "campaign_copy",
    "tiktok_script",
    "hook_text",
    "blog_post",
)

REPO_ROOT = Path(__file__).resolve().parents[2]

PHASE4A_HTML = REPO_ROOT / "tmp" / "phase4a-ui" / "index.html"
PORTFOLIO_DIR = REPO_ROOT / "tmp" / "phase3b-portfolio-dashboard"
DASHBOARD_DIR = REPO_ROOT / "tmp" / "phase3a-dashboard"
SCORES_DIR = REPO_ROOT / "tmp" / "phase2e-import-score-report" / "scores"
DEFAULT_OUT = REPO_ROOT / "tmp" / "phase4b-ui-snapshot"

SNAPSHOT_FILES = ("index.html", "manifest.json", "README.md", "INVENTORY.md", "GUARDRAILS.md")
GUARDED_SUFFIX = "tmp/phase4b-ui-snapshot"

GUARDRAILS = (
    "no database",
    "no FastAPI",
    "no backend service",
    "no external APIs",
    "no external URLs",
    "no affiliate content generation",
    "no autopublish",
    "no campaign launch",
    "no vault writes",
    "no approval mutation",
    "no Phase 2G/2H/2I triggering",
    "no marketplace connector",
    "read-only only",
)


def _scrub(text: str) -> None:
    """Reject vault paths, affiliate URLs, secrets, content fields, external URLs."""
    for pattern in PRIVATE_VAULT_PATHS:
        if pattern in text:
            raise DashboardError(f"snapshot file contains private vault path: {pattern}")
    for pattern in AFFILIATE_URL_PATTERNS:
        if pattern in text:
            raise DashboardError(f"snapshot file contains affiliate tracking pattern: {pattern}")
    for pattern in SNAPSHOT_CONTENT_MARKERS:
        if pattern in text:
            raise DashboardError(f"snapshot file contains affiliate content marker: {pattern}")
    for regex in SECRET_RES:
        if regex.search(text):
            raise DashboardError("snapshot file contains a secret pattern")
    for pattern in ("http://", "https://"):
        if pattern in text:
            raise DashboardError(f"snapshot file contains an external URL pattern: {pattern}")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _count_glob(directory: Path, pattern: str) -> int:
    return len(list(directory.glob(pattern))) if directory.is_dir() else 0


def _regenerate_mock(week: str) -> int:
    """Regenerate the Phase 4A mock via its own builder (safe source path)."""
    # Suppress the Phase 4A builder's stdout so only the snapshot output is shown.
    with contextlib.redirect_stdout(io.StringIO()):
        return build_ui_mock.main(["--week", week])


def _guarded_out_dir(out: str) -> Path:
    out_path = Path(out)
    if not out_path.is_absolute():
        out_path = REPO_ROOT / out_path
    resolved = out_path.resolve()
    # Guard: only operate on the canonical snapshot dir or an explicit --out path
    # that is itself named like the snapshot dir; never arbitrary directories.
    if resolved != DEFAULT_OUT.resolve() and not str(resolved).endswith(GUARDED_SUFFIX):
        raise DashboardError(
            f"refusing to use unguarded output directory: {resolved} "
            f"(must be {DEFAULT_OUT} or end with {GUARDED_SUFFIX})"
        )
    return resolved


def _clear_known_files(out_dir: Path) -> None:
    for name in SNAPSHOT_FILES:
        (out_dir / name).unlink(missing_ok=True)


def _render_readme(week: str) -> str:
    return f"""# UI Snapshot Pack — {week}

## 1. Purpose

This folder is a deterministic, read-only demo export of the Phase 4A static UI
mock plus supporting metadata. It lets a demo operator open the dashboard view
locally without any server, backend, or network access.

## 2. How to open

Open `index.html` in a local browser, for example via a `file://` URL pointing
at this folder's `index.html`. No server is required.

## 3. Exact command

```
bash scripts/dev/run_phase4b_ui_snapshot.sh {week}
```

## 4. What is included

- `index.html` — the self-contained static UI mock (copied from Phase 4A)
- `manifest.json` — file inventory with sha256 and byte sizes
- `README.md` — this file
- `INVENTORY.md` — source artifact summary
- `GUARDRAILS.md` — guardrail statement

## 5. What is NOT included

- no vault files
- no raw score JSON
- no raw dashboard artifacts
- no secrets
- no external URLs
- no server
- no backend

## 6. Demo steps

1. Generate the upstream artifacts: `bash scripts/dev/run_phase3d_acceptance.sh`.
2. Build this snapshot: `bash scripts/dev/run_phase4b_ui_snapshot.sh {week}`.
3. Open `index.html` locally and walk through the portfolio overview, top
   products, per-product pipeline cards, and the guardrail footer.

## 7. Known limitations

- It is a static snapshot; it reflects the artifacts at build time.
- It is stale if the upstream artifacts are stale; rebuild to refresh.
- There is no interactivity and no live refresh.
- `manifest.json` includes a generated timestamp, so it is not byte-identical
  across rebuilds.
"""


def _render_inventory(week: str, portfolio_present: bool, dashboards: int, scores: int) -> str:
    return f"""# Snapshot Inventory

- report_week: {week}
- ui_mock_source: tmp/phase4a-ui/index.html (regenerated)
- portfolio_artifact: {"present" if portfolio_present else "absent"}
- product_dashboards: {dashboards}
- score_files: {scores}

## Snapshot files

- index.html
- manifest.json
- README.md
- INVENTORY.md
- GUARDRAILS.md

## Vault statement

no vault files included

vault_included: false
"""


def _render_guardrails() -> str:
    lines = ["# Guardrails", "", "This snapshot was produced under the following guardrails:", ""]
    lines += [f"- {item}" for item in GUARDRAILS]
    lines.append("")
    return "\n".join(lines)


def build_snapshot(week: str, out: str) -> dict:
    out_dir = _guarded_out_dir(out)

    # Regenerate the Phase 4A mock (safe source path) before packaging.
    rc = _regenerate_mock(week)
    if rc != 0:
        raise DashboardError("Phase 4A mock generation failed")
    if not PHASE4A_HTML.is_file():
        raise DashboardError(f"expected Phase 4A mock not found: {PHASE4A_HTML}")

    portfolio_present = (PORTFOLIO_DIR / f"portfolio-{week}.md").is_file()
    dashboards = _count_glob(DASHBOARD_DIR, f"dashboard-*-{week}.md")
    scores = _count_glob(SCORES_DIR, "*.json")

    index_html = PHASE4A_HTML.read_text(encoding="utf-8")
    readme = _render_readme(week)
    inventory = _render_inventory(week, portfolio_present, dashboards, scores)
    guardrails = _render_guardrails()

    generated_at = _now_utc()

    # Scrub every text payload before it is written.
    for payload in (index_html, readme, inventory, guardrails):
        _scrub(payload)

    # Compute the manifest over the non-manifest files first.
    contents = {
        "index.html": index_html,
        "README.md": readme,
        "INVENTORY.md": inventory,
        "GUARDRAILS.md": guardrails,
    }
    files_entries = []
    for name in ("index.html", "README.md", "INVENTORY.md", "GUARDRAILS.md"):
        data = contents[name].encode("utf-8")
        files_entries.append({"name": name, "sha256": _sha256(data), "bytes": len(data)})

    manifest = {
        "type": "phase4b_ui_snapshot",
        "report_week": week,
        "generated_at": generated_at,
        "files": files_entries,
        "source_summary": {
            "portfolio_artifact": "present" if portfolio_present else "absent",
            "product_dashboards": dashboards,
            "score_files": scores,
            "vault_included": False,
        },
    }
    manifest_text = json.dumps(manifest, indent=2, sort_keys=False) + "\n"
    _scrub(manifest_text)

    # Write atomically-ish: clear known files, then write all five.
    out_dir.mkdir(parents=True, exist_ok=True)
    _clear_known_files(out_dir)
    (out_dir / "index.html").write_text(index_html, encoding="utf-8")
    (out_dir / "README.md").write_text(readme, encoding="utf-8")
    (out_dir / "INVENTORY.md").write_text(inventory, encoding="utf-8")
    (out_dir / "GUARDRAILS.md").write_text(guardrails, encoding="utf-8")
    (out_dir / "manifest.json").write_text(manifest_text, encoding="utf-8")

    return {"out_dir": out_dir, "manifest": manifest}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 4B UI snapshot pack / demo export.")
    parser.add_argument("--week", required=True)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        _check_guardrails()
        if not WEEK_RE.match(args.week):
            raise DashboardError(f"week must match ^[0-9]{{4}}-W[0-9]{{2}}$, got: {args.week!r}")
        result = build_snapshot(args.week, args.out)
    except DashboardError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    out_dir = result["out_dir"]
    rel = out_dir.relative_to(REPO_ROOT) if out_dir.is_relative_to(REPO_ROOT) else out_dir
    print(f"snapshot_path: {rel}")
    for name in SNAPSHOT_FILES:
        print(f"snapshot_file: {name}")
    print("phase4b_status: success")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
