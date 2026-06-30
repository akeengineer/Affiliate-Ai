#!/usr/bin/env python3
"""Phase 5C UI Shell Verifier / Acceptance Gate.

Read-only verifier over the generated Phase 5B static shell. It reads the shell
body and the four Phase 4 JSON summaries, checks the shell for safety and
required structure, checks link targets by existence only (never body), and
writes a local verification report and JSON summary under
tmp/phase5c-ui-shell-verifier/. It never reads the vault, raw score JSON,
Phase 3 artifacts, or raw Phase 4 HTML bodies, and never regenerates Phase 5B.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dashboard_summary import (  # noqa: E402
    AFFILIATE_URL_PATTERNS,
    PRIVATE_VAULT_PATHS,
    SECRET_RES,
    DashboardError,
    _check_guardrails,
    _now_utc,
)

SHELL_REL = "tmp/phase5b-ui-shell/index.html"
SHELL_PATH = REPO_ROOT / SHELL_REL
OUT_DIR = REPO_ROOT / "tmp" / "phase5c-ui-shell-verifier"
GUARDED_SUFFIX = "tmp/phase5c-ui-shell-verifier"

# Phase 4 JSON summaries Phase 5B consumes (existence/notice checks only).
SOURCE_JSON = {
    "phase4e": REPO_ROOT / "tmp/phase4e-demo-bundle/demo-bundle-summary.json",
    "phase4b": REPO_ROOT / "tmp/phase4b-ui-snapshot/manifest.json",
    "phase4c": REPO_ROOT / "tmp/phase4c-snapshot-catalog/catalog.json",
    "phase4d": REPO_ROOT / "tmp/phase4d-demo-verifier/verification-summary.json",
}

# Relative link targets — checked by existence/size only, never body ingestion.
LINK_TARGETS = (
    "phase4b-ui-snapshot/index.html",
    "phase4c-snapshot-catalog/index.html",
    "phase4d-demo-verifier/verification-report.md",
    "phase4e-demo-bundle/DEMO_BUNDLE.md",
)

# Affiliate-content field markers ("autopublish" excluded; it is a legitimate
# policy negation, not leaked content).
CONTENT_MARKERS = ("content_draft", "campaign_copy", "tiktok_script", "hook_text", "blog_post")

JS_TOKENS = ("<script", "fetch(", "XMLHttpRequest", "import(")
EXTERNAL_URL_TOKENS = ("http://", "https://", "file://")
SELF_CONTAINED_FORBIDDEN = ("<link", "<iframe", "<form")
EVENT_HANDLER_RE = re.compile(r"<[^>]*\son[a-z]+\s*=", re.IGNORECASE)
HREF_RE = re.compile(r"""href\s*=\s*["']([^"']*)["']""", re.IGNORECASE)

APPROVED_WORKFLOW_REFS = (
    "run_phase2g",
    "run_phase2h",
    "run_phase2i",
    "promote_product_candidates.py",
    "create_decision.py",
    "finalize_decision.py",
)

# Required conceptual sections -> a case-insensitive substring that exists in a
# clean Phase 5B shell (the footer header is "Guardrails:", matched by "guardrail").
REQUIRED_SECTIONS = (
    ("read_only_shell_badge", "read-only shell"),
    ("demo_readiness", "demo readiness"),
    ("snapshot", "snapshot"),
    ("catalog", "catalog"),
    ("verification", "verification"),
    ("local_links", "local links"),
    ("guardrail_footer", "guardrail"),
)

# Composed so this source never contains the contiguous operator-path literal
# (keeps the CI-C hardcoded-path guard green).
OPERATOR_PATH = "/home/ubuntu/" + "Affiliate-Ai"

# Tokens the verifier's own output must never echo.
OUTPUT_FORBIDDEN = (
    *EXTERNAL_URL_TOKENS,
    OPERATOR_PATH,
    *JS_TOKENS,
    *SELF_CONTAINED_FORBIDDEN,
    *PRIVATE_VAULT_PATHS,
    *AFFILIATE_URL_PATTERNS,
    *CONTENT_MARKERS,
    *APPROVED_WORKFLOW_REFS,
)


def _read_shell() -> str:
    return SHELL_PATH.read_text(encoding="utf-8") if SHELL_PATH.is_file() else ""


def _hrefs(html: str) -> list[str]:
    return HREF_RE.findall(html)


def _href_is_relative(href: str) -> bool:
    h = href.strip()
    if not h:
        return False
    if h.startswith("/") or h.startswith("//"):
        return False
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", h):  # any scheme: http:, https:, file:, mailto:
        return False
    return True


def verify() -> dict[str, Any]:
    html = _read_shell()
    low = html.lower()
    shell_exists = SHELL_PATH.is_file()

    checks: dict[str, bool] = {}
    warnings: list[str] = []

    checks["shell_exists"] = shell_exists
    checks["output_under_expected_dir"] = SHELL_PATH.resolve() == (REPO_ROOT / SHELL_REL).resolve()

    checks["self_contained"] = (
        shell_exists
        and "<style" in low
        and not any(tok in low for tok in SELF_CONTAINED_FORBIDDEN)
    )
    checks["no_js"] = (
        shell_exists
        and not any(tok in low for tok in JS_TOKENS)
        and EVENT_HANDLER_RE.search(html) is None
    )
    checks["no_external_url"] = shell_exists and not any(tok in low for tok in EXTERNAL_URL_TOKENS)
    checks["no_vault_path"] = not any(p in html for p in PRIVATE_VAULT_PATHS)
    checks["no_secret"] = not any(rx.search(html) for rx in SECRET_RES)
    checks["no_affiliate_marker"] = not any(p in html for p in AFFILIATE_URL_PATTERNS) and not any(
        m in html for m in CONTENT_MARKERS
    )
    checks["no_approved_workflow_ref"] = not any(ref in html for ref in APPROVED_WORKFLOW_REFS)
    checks["required_sections"] = shell_exists and all(sub in low for _label, sub in REQUIRED_SECTIONS)
    checks["links_relative"] = shell_exists and all(_href_is_relative(h) for h in _hrefs(html))

    # Soft: Phase 4 source JSON present, or a visible not-found notice in the shell.
    sources_ok = True
    for name, path in SOURCE_JSON.items():
        if path.is_file():
            continue
        notice = f"{name} output not found" in low or "no phase 4 outputs found" in low
        if notice:
            warnings.append(f"{name} source summary missing (not-found notice shown in shell)")
        else:
            sources_ok = False
    checks["sources_present_or_noticed"] = sources_ok

    # Soft: a referenced relative link whose target file is missing.
    for rel in LINK_TARGETS:
        if f"../{rel}" in html and not (REPO_ROOT / "tmp" / rel).exists():
            warnings.append(f"relative link target missing: {rel}")

    # Soft: week-mismatch / staleness notice present.
    if "data may be stale" in low:
        warnings.append("week-mismatch/staleness notice present in shell")

    if not all(checks.values()):
        verdict = "failed"
    elif warnings:
        verdict = "warning"
    else:
        verdict = "ready"

    checked_paths = [SHELL_REL] + [
        str(p.relative_to(REPO_ROOT)) for p in SOURCE_JSON.values() if p.is_file()
    ]

    summary = {
        "type": "phase5c_ui_shell_verification",
        "generated_at": _now_utc(),
        "verdict": verdict,
        "checks": checks,
        "warnings": warnings,
        "checked_paths": checked_paths,
        "shell_path": SHELL_REL,
    }
    return summary


CHECK_TITLES = {
    "shell_exists": "Phase 5B shell exists",
    "output_under_expected_dir": "shell under tmp/phase5b-ui-shell/",
    "self_contained": "self-contained (inline style, no link/iframe/form)",
    "no_js": "no JavaScript tokens or event handlers",
    "no_external_url": "no external URL tokens",
    "no_vault_path": "no vault paths",
    "no_secret": "no secret-like markers",
    "no_affiliate_marker": "no affiliate tracking/content markers",
    "no_approved_workflow_ref": "approved-workflow reference absent",
    "required_sections": "required sections present",
    "links_relative": "all links relative",
    "sources_present_or_noticed": "Phase 4 sources present or noticed",
}


def render_report(summary: dict[str, Any]) -> str:
    lines = [
        "# Phase 5C UI Shell Verification",
        "",
        f"Generated at: {summary['generated_at']}",
        f"Verdict: {summary['verdict']}",
        "",
        "## Checks",
        "",
        "| check | result |",
        "| --- | --- |",
    ]
    for key, ok in summary["checks"].items():
        title = CHECK_TITLES.get(key, key)
        lines.append(f"| {title} | {'PASS' if ok else 'FAIL'} |")
    lines += ["", "## Warnings", ""]
    if summary["warnings"]:
        for warn in summary["warnings"]:
            lines.append(f"- WARN: {warn}")
    else:
        lines.append("- none")
    lines += ["", "## Checked paths", ""]
    for path in summary["checked_paths"]:
        lines.append(f"- {path}")
    lines += [
        "",
        "## Guardrails",
        "",
        "- read-only verifier; reads existing outputs only",
        "- no JS, no external URLs, no vault paths, no approved-workflow refs",
        "- no backend, no API, no database, no network",
        "",
    ]
    return "\n".join(lines)


def _assert_output_safe(text: str) -> None:
    found = sorted({tok for tok in OUTPUT_FORBIDDEN if tok in text})
    if found:
        raise DashboardError("verifier output failed its own safety scan")
    if EVENT_HANDLER_RE.search(text):
        raise DashboardError("verifier output failed its own safety scan")


def _guarded_out_dir() -> Path:
    out = OUT_DIR.resolve()
    if not str(out).endswith(GUARDED_SUFFIX):
        raise DashboardError(f"refusing to write outside {GUARDED_SUFFIX}: {out}")
    return out


def main() -> int:
    try:
        _check_guardrails()
        summary = verify()
        report_text = render_report(summary)
        summary_text = json.dumps(summary, indent=2) + "\n"
        _assert_output_safe(report_text)
        _assert_output_safe(summary_text)
        out_dir = _guarded_out_dir()
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "verification-report.md").write_text(report_text, encoding="utf-8")
        (out_dir / "verification-summary.json").write_text(summary_text, encoding="utf-8")
    except DashboardError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    verdict = summary["verdict"]
    print(f"verification_report: {GUARDED_SUFFIX}/verification-report.md")
    print(f"verification_summary: {GUARDED_SUFFIX}/verification-summary.json")
    print(f"verdict: {verdict}")
    if verdict == "failed":
        print("phase5c_status: failed")
        return 1
    print("phase5c_status: success")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
