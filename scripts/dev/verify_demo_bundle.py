#!/usr/bin/env python3
"""Phase 4D Static Demo Bundle Verifier.

Read-only verifier over the Phase 4B snapshot and Phase 4C catalog. It checks
structure, manifest integrity, catalog↔snapshot consistency, relative-link
resolution, and safety (no external URLs, vault paths, affiliate URLs, secrets,
content markers, or raw artifacts), then writes a verification report and
summary under the Phase 4D output directory.

Verifier only: it never regenerates Phase 4B/4C, never reads/writes the vault,
never calls external services, and never triggers approved workflows. Its own
output is held to the same safety checks; findings are reported by class name,
never by echoing offending content.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from dashboard_summary import (
    AFFILIATE_URL_PATTERNS,
    PRIVATE_VAULT_PATHS,
    SECRET_RES,
    DashboardError,
    _check_guardrails,
    _now_utc,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
TMP_DIR = REPO_ROOT / "tmp"

SNAPSHOT_DEFAULT = TMP_DIR / "phase4b-ui-snapshot"
CATALOG_DEFAULT = TMP_DIR / "phase4c-snapshot-catalog"
OUT_DEFAULT = TMP_DIR / "phase4d-demo-verifier"

SNAPSHOT_REL = "tmp/phase4b-ui-snapshot"
CATALOG_REL = "tmp/phase4c-snapshot-catalog"
GUARDED_SUFFIX = "tmp/phase4d-demo-verifier"

SNAPSHOT_FILES = ("index.html", "manifest.json", "README.md", "INVENTORY.md", "GUARDRAILS.md")
CATALOG_FILES = ("index.html", "catalog.json", "README.md", "GUARDRAILS.md")
OUT_FILES = ("verification-report.md", "verification-summary.json")
ALLOWED_JSON = {"manifest.json", "catalog.json", "verification-summary.json"}

# Affiliate-content field markers. "autopublish" is intentionally excluded: the
# bundle's GUARDRAILS files legitimately state "no autopublish".
CONTENT_MARKERS = ("content_draft", "campaign_copy", "tiktok_script", "hook_text", "blog_post")

HREF_RE = re.compile(r'href="([^"]*)"')


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def scan_text(text: str) -> set[str]:
    """Return the set of safety-violation classes present in text."""
    found: set[str] = set()
    if "http://" in text or "https://" in text:
        found.add("external_url")
    for pattern in PRIVATE_VAULT_PATHS:
        if pattern in text:
            found.add("vault_path")
    for pattern in AFFILIATE_URL_PATTERNS:
        if pattern in text:
            found.add("affiliate_url")
    for pattern in CONTENT_MARKERS:
        if pattern in text:
            found.add("content_marker")
    for regex in SECRET_RES:
        if regex.search(text):
            found.add("secret")
    return found


def _dir_files(directory: Path) -> set[str]:
    return {p.name for p in directory.iterdir() if p.is_file()} if directory.is_dir() else set()


def _has_raw_artifacts(dirs: list[Path]) -> bool:
    for directory in dirs:
        if not directory.is_dir():
            continue
        for path in directory.iterdir():
            if not path.is_file():
                continue
            name = path.name
            if name.startswith("dashboard-") and name.endswith(".md"):
                return True
            if name.startswith("portfolio-") and name.endswith(".md"):
                return True
            if name.endswith(".json") and name not in ALLOWED_JSON:
                return True
    return False


def _guarded_out_dir(out: str) -> Path:
    out_path = Path(out)
    if not out_path.is_absolute():
        out_path = REPO_ROOT / out_path
    resolved = out_path.resolve()
    if resolved != OUT_DEFAULT.resolve() and not str(resolved).endswith(GUARDED_SUFFIX):
        raise DashboardError(
            f"refusing to use unguarded output directory: {resolved} "
            f"(must be {OUT_DEFAULT} or end with {GUARDED_SUFFIX})"
        )
    return resolved


def verify(snapshot_dir: Path, catalog_dir: Path, out_dir: Path) -> dict[str, Any]:
    # ── Phase 4B structure + manifest ────────────────────────────────────────
    b_files = _dir_files(snapshot_dir)
    b_files_ok = b_files == set(SNAPSHOT_FILES)

    manifest: dict[str, Any] = {}
    manifest_valid = False
    try:
        manifest = json.loads(_read_text(snapshot_dir / "manifest.json"))
        manifest_valid = isinstance(manifest, dict)
    except json.JSONDecodeError:
        manifest_valid = False
    if not isinstance(manifest, dict):
        manifest = {}

    manifest_type = str(manifest.get("type", ""))
    manifest_type_ok = manifest_type == "phase4b_ui_snapshot"
    source_summary = manifest.get("source_summary") if isinstance(manifest.get("source_summary"), dict) else {}
    vault_included = bool(source_summary.get("vault_included", True))
    vault_included_false = vault_included is False
    report_week = str(manifest.get("report_week", ""))

    files_meta = manifest.get("files") if isinstance(manifest.get("files"), list) else []
    index_sha256_b = ""
    hashes_match = manifest_valid and manifest_type_ok and bool(files_meta)
    for entry in files_meta:
        if not isinstance(entry, dict):
            hashes_match = False
            continue
        name = str(entry.get("name", ""))
        target = snapshot_dir / name
        if not target.is_file():
            hashes_match = False
            continue
        data = target.read_bytes()
        if name == "index.html":
            index_sha256_b = _sha256_bytes(data)
        if int(entry.get("bytes", -1)) != len(data):
            hashes_match = False
        if str(entry.get("sha256", "")) != _sha256_bytes(data):
            hashes_match = False

    # ── Phase 4C structure + catalog ─────────────────────────────────────────
    c_files = _dir_files(catalog_dir)
    c_files_ok = c_files == set(CATALOG_FILES)

    catalog: dict[str, Any] = {}
    catalog_valid = False
    try:
        catalog = json.loads(_read_text(catalog_dir / "catalog.json"))
        catalog_valid = isinstance(catalog, dict)
    except json.JSONDecodeError:
        catalog_valid = False
    if not isinstance(catalog, dict):
        catalog = {}

    catalog_type = str(catalog.get("type", ""))
    catalog_type_ok = catalog_type == "phase4c_snapshot_catalog"
    snapshots = catalog.get("snapshots") if isinstance(catalog.get("snapshots"), list) else []
    snapshot_count = int(catalog.get("snapshot_count", len(snapshots)) or 0)
    skipped_count = int(catalog.get("skipped_count", 0) or 0)

    references_phase4b = False
    for entry in snapshots:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("source_dir", "")) == SNAPSHOT_REL:
            if index_sha256_b and str(entry.get("index_sha256", "")) == index_sha256_b:
                references_phase4b = True
            break
    catalog_consistency = (
        catalog_valid and catalog_type_ok and snapshot_count >= 1 and references_phase4b
    )

    # ── Relative link resolution (Phase 4C index.html) ───────────────────────
    catalog_index = _read_text(catalog_dir / "index.html")
    hrefs = HREF_RE.findall(catalog_index)
    relative_link_resolves = bool(hrefs)
    for href in hrefs:
        if href.startswith("http://") or href.startswith("https://") or href.startswith("/"):
            relative_link_resolves = False
            break
        if not (catalog_dir / href).resolve().is_file():
            relative_link_resolves = False
            break

    # ── Safety scan over all bundle files ────────────────────────────────────
    violations: set[str] = set()
    for name in SNAPSHOT_FILES:
        violations |= scan_text(_read_text(snapshot_dir / name))
    for name in CATALOG_FILES:
        violations |= scan_text(_read_text(catalog_dir / name))

    no_external_urls = "external_url" not in violations
    no_vault_paths = "vault_path" not in violations
    no_affiliate_urls = "affiliate_url" not in violations
    no_secrets = "secret" not in violations
    no_content_markers = "content_marker" not in violations
    no_raw_artifacts = not _has_raw_artifacts([snapshot_dir, catalog_dir, out_dir])

    rows = {
        "Phase 4B files": b_files_ok,
        "Phase 4B manifest hashes": manifest_valid and manifest_type_ok and hashes_match,
        "Phase 4B vault_included": vault_included_false,
        "Phase 4C files": c_files_ok,
        "Phase 4C catalog references Phase 4B": catalog_consistency,
        "Relative link resolves": relative_link_resolves,
        "No external URLs": no_external_urls,
        "No vault paths": no_vault_paths,
        "No affiliate URLs": no_affiliate_urls,
        "No secrets": no_secrets,
        "No content markers": no_content_markers,
        "No raw artifact export": no_raw_artifacts,
    }
    status = "success" if all(rows.values()) else "failed"

    summary = {
        "type": "phase4d_demo_bundle_verification",
        "generated_at": _now_utc(),
        "status": status,
        "checked_paths": [SNAPSHOT_REL, CATALOG_REL],
        "phase4b": {
            "file_count": len(b_files),
            "manifest_type": manifest_type,
            "report_week": report_week,
            "manifest_hashes_match": bool(manifest_valid and manifest_type_ok and hashes_match),
            "vault_included": vault_included,
        },
        "phase4c": {
            "file_count": len(c_files),
            "catalog_type": catalog_type,
            "snapshot_count": snapshot_count,
            "skipped_count": skipped_count,
            "references_phase4b": references_phase4b,
            "relative_link_resolves": relative_link_resolves,
        },
        "safety": {
            "no_external_urls": no_external_urls,
            "no_vault_paths": no_vault_paths,
            "no_affiliate_urls": no_affiliate_urls,
            "no_secrets": no_secrets,
            "no_content_markers": no_content_markers,
            "no_raw_artifacts": no_raw_artifacts,
        },
        "vault": {"vault_read": False, "vault_write": False},
    }
    return {"summary": summary, "rows": rows, "status": status}


def render_report(summary: dict[str, Any], rows: dict[str, bool]) -> str:
    lines = [
        "# Phase 4D Demo Bundle Verification Report",
        "",
        f"Status: {summary['status']}",
        "",
        "## Checked inputs",
        "",
        f"- Phase 4B snapshot path: {SNAPSHOT_REL}",
        f"- Phase 4C catalog path: {CATALOG_REL}",
        "",
        "## Verification table",
        "",
        "| check | result |",
        "| --- | --- |",
    ]
    for title, ok in rows.items():
        lines.append(f"| {title} | {'PASS' if ok else 'FAIL'} |")
    lines += [
        "",
        "## Output",
        "",
        "- verification-summary.json",
        "",
        "## Known limitations",
        "",
        "- verifier checks existing generated bundle only",
        "- verifier does not regenerate Phase 4B or Phase 4C",
        "- stale input remains stale until upstream phases are rebuilt",
        "- generated_at makes report non-byte-deterministic",
        "",
    ]
    return "\n".join(lines)


def _assert_output_safe(text: str) -> None:
    found = scan_text(text)
    if found:
        raise DashboardError(f"verifier output failed its own safety scan: {sorted(found)}")
    if "http://" in text or "https://" in text:
        raise DashboardError("verifier output contains an external URL scheme")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 4D static demo bundle verifier.")
    parser.add_argument("--snapshot-dir", default=str(SNAPSHOT_DEFAULT))
    parser.add_argument("--catalog-dir", default=str(CATALOG_DEFAULT))
    parser.add_argument("--out", default=str(OUT_DEFAULT))
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        _check_guardrails()
        out_dir = _guarded_out_dir(args.out)
        snapshot_dir = Path(args.snapshot_dir)
        if not snapshot_dir.is_absolute():
            snapshot_dir = REPO_ROOT / snapshot_dir
        catalog_dir = Path(args.catalog_dir)
        if not catalog_dir.is_absolute():
            catalog_dir = REPO_ROOT / catalog_dir

        result = verify(snapshot_dir, catalog_dir, out_dir)
        summary_text = json.dumps(result["summary"], indent=2, sort_keys=False) + "\n"
        report_text = render_report(result["summary"], result["rows"])

        _assert_output_safe(summary_text)
        _assert_output_safe(report_text)

        out_dir.mkdir(parents=True, exist_ok=True)
        for name in OUT_FILES:
            (out_dir / name).unlink(missing_ok=True)
        (out_dir / "verification-report.md").write_text(report_text, encoding="utf-8")
        (out_dir / "verification-summary.json").write_text(summary_text, encoding="utf-8")
    except DashboardError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    rel = out_dir.relative_to(REPO_ROOT) if out_dir.is_relative_to(REPO_ROOT) else out_dir
    print(f"verification_path: {rel}")
    for name in OUT_FILES:
        print(f"verification_file: {name}")
    print(f"verdict: {'ready' if result['status'] == 'success' else 'not_ready'}")
    if result["status"] == "success":
        print("phase4d_status: success")
        return 0
    print("phase4d_status: failed")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
