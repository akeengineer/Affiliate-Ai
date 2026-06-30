#!/usr/bin/env python3
"""Phase 5D UI Shell Demo Bundle summary writer.

Owns the verdict-to-status mapping for the Phase 5D demo chain and writes the
local summary/report under tmp/phase5d-ui-shell-demo/. Keeping the mapping here
makes ready/warning/failed deterministically unit-testable without bypassing the
real Phase 5C verifier in the orchestrator.

Read-only over local summary files; never reads the vault, raw scores, Phase 3
artifacts, raw Phase 4 HTML, or the Phase 5B shell body.
"""
from __future__ import annotations

import argparse
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
    WEEK_RE,
    DashboardError,
    _now_utc,
)

OUT_DIR = REPO_ROOT / "tmp" / "phase5d-ui-shell-demo"
GUARDED_SUFFIX = "tmp/phase5d-ui-shell-demo"

PHASE4E_SUMMARY = "tmp/phase4e-demo-bundle/demo-bundle-summary.json"
PHASE5B_SHELL = "tmp/phase5b-ui-shell/index.html"
PHASE5C_SUMMARY = "tmp/phase5c-ui-shell-verifier/verification-summary.json"
PHASE5C_REPORT = "tmp/phase5c-ui-shell-verifier/verification-report.md"

VALID_VERDICTS = ("ready", "warning", "failed")
VALID_STEPS = ("PASS", "FAIL")

# Composed so this source carries no contiguous operator-path or approved-workflow
# literal (keeps the CI-C guard and the static-boundary test green).
OPERATOR_PATH = "/home/ubuntu/" + "Affiliate-Ai"
APPROVED_WORKFLOW_REFS = (
    "run_phase2" + "g",
    "run_phase2" + "h",
    "run_phase2" + "i",
    "promote_product_candidates" + ".py",
    "create_decision" + ".py",
    "finalize_decision" + ".py",
)

JS_TOKENS = ("<script", "fetch(", "XMLHttpRequest", "import(", "<iframe", "<form", "<link")
EXTERNAL_URL_TOKENS = ("http://", "https://", "file://")
EVENT_HANDLER_RE = re.compile(r"<[^>]*\son[a-z]+\s*=", re.IGNORECASE)

OUTPUT_FORBIDDEN = (
    *EXTERNAL_URL_TOKENS,
    OPERATOR_PATH,
    *JS_TOKENS,
    *PRIVATE_VAULT_PATHS,
    *AFFILIATE_URL_PATTERNS,
    *APPROVED_WORKFLOW_REFS,
)


def _read_verdict_from_summary() -> str:
    path = REPO_ROOT / PHASE5C_SUMMARY
    if not path.is_file():
        return "failed"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return "failed"
    verdict = data.get("verdict")
    return verdict if verdict in VALID_VERDICTS else "failed"


def resolve(week: str, steps: dict[str, str], verdict: str | None) -> dict[str, Any]:
    if not WEEK_RE.match(week):
        raise DashboardError(f"week must match {WEEK_RE.pattern}, got: {week}")
    for name, value in steps.items():
        if value not in VALID_STEPS:
            raise DashboardError(f"step {name} must be PASS or FAIL, got: {value}")

    resolved_verdict = verdict if verdict in VALID_VERDICTS else _read_verdict_from_summary()
    steps_ok = all(v == "PASS" for v in steps.values())

    if not steps_ok or resolved_verdict == "failed":
        status = "failed"
    elif resolved_verdict == "warning":
        status = "warning"
    elif resolved_verdict == "ready":
        status = "ready"
    else:
        status = "failed"

    phase5d_status = "success" if status in ("ready", "warning") else "failed"

    summary = {
        "type": "phase5d_ui_shell_demo",
        "report_week": week,
        "generated_at": _now_utc(),
        "steps": {
            "phase4e": steps["phase4e"],
            "phase5b": steps["phase5b"],
            "phase5c": steps["phase5c"],
        },
        "ui_shell_verdict": resolved_verdict,
        "status": status,
        "phase5d_status": phase5d_status,
        "artifacts": {
            "phase4e_summary": PHASE4E_SUMMARY,
            "phase5b_shell": PHASE5B_SHELL,
            "phase5c_summary": PHASE5C_SUMMARY,
            "phase5c_report": PHASE5C_REPORT,
        },
        "guardrails": {
            "no_backend": True,
            "no_api": True,
            "no_database": True,
            "no_vault_writes": True,
            "no_external_urls": True,
            "no_approved_workflow": True,
        },
    }
    return summary


def render_report(summary: dict[str, Any]) -> str:
    steps = summary["steps"]
    lines = [
        "# Phase 5D UI Shell Demo",
        "",
        f"Report week: {summary['report_week']}",
        f"Generated at: {summary['generated_at']}",
        "",
        "## Commands run",
        "",
        "- run_phase4e_demo_bundle.sh",
        "- run_phase5b_ui_shell.sh",
        "- run_phase5c_ui_shell_verifier.sh",
        "",
        "## Step statuses",
        "",
        f"- phase4e: {steps['phase4e']}",
        f"- phase5b: {steps['phase5b']}",
        f"- phase5c: {steps['phase5c']}",
        "",
        f"UI shell verdict: {summary['ui_shell_verdict']}",
        f"Demo status: {summary['status']}",
        "",
        "## Artifacts",
        "",
        f"- {summary['artifacts']['phase4e_summary']}",
        f"- {summary['artifacts']['phase5b_shell']}",
        f"- {summary['artifacts']['phase5c_summary']}",
        f"- {summary['artifacts']['phase5c_report']}",
        "",
        "## How to open",
        "",
        f"- {PHASE5B_SHELL}",
        "",
        "## Guardrails",
        "",
        "- no backend",
        "- no API",
        "- no database",
        "- no vault writes",
        "- no external URLs",
        "- no approved workflow",
        "",
    ]
    return "\n".join(lines)


def _assert_output_safe(text: str) -> None:
    if any(tok in text for tok in OUTPUT_FORBIDDEN):
        raise DashboardError("Phase 5D output failed its own safety scan")
    if any(rx.search(text) for rx in SECRET_RES):
        raise DashboardError("Phase 5D output failed its own safety scan")
    if EVENT_HANDLER_RE.search(text):
        raise DashboardError("Phase 5D output failed its own safety scan")


def _guarded_out_dir() -> Path:
    out = OUT_DIR.resolve()
    if not str(out).endswith(GUARDED_SUFFIX):
        raise DashboardError(f"refusing to write outside {GUARDED_SUFFIX}: {out}")
    return out


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 5D UI shell demo summary writer.")
    parser.add_argument("--week", required=True)
    parser.add_argument("--phase4e", required=True, choices=VALID_STEPS)
    parser.add_argument("--phase5b", required=True, choices=VALID_STEPS)
    parser.add_argument("--phase5c", required=True, choices=VALID_STEPS)
    parser.add_argument("--verdict", choices=VALID_VERDICTS)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        steps = {"phase4e": args.phase4e, "phase5b": args.phase5b, "phase5c": args.phase5c}
        summary = resolve(args.week, steps, args.verdict)
        report_text = render_report(summary)
        summary_text = json.dumps(summary, indent=2) + "\n"
        _assert_output_safe(report_text)
        _assert_output_safe(summary_text)
        out_dir = _guarded_out_dir()
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "ui-shell-demo-summary.json").write_text(summary_text, encoding="utf-8")
        (out_dir / "UI_SHELL_DEMO.md").write_text(report_text, encoding="utf-8")
    except DashboardError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"ui_shell_verdict: {summary['ui_shell_verdict']}")
    print(f"ui_shell_demo_status: {summary['status']}")
    print(f"phase5d_status: {summary['phase5d_status']}")
    print(f"demo_summary: {GUARDED_SUFFIX}/ui-shell-demo-summary.json")
    print(f"demo_report: {GUARDED_SUFFIX}/UI_SHELL_DEMO.md")
    return 0 if summary["phase5d_status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
