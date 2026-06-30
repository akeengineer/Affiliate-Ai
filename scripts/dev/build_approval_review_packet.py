#!/usr/bin/env python3
"""Phase 6B Dry-run Approval Review Packet builder.

Gathers whitelisted evidence from existing read-only tmp artifacts and writes an
operator-readable review packet under tmp/phase6b-approval-review/. This is a
DRY-RUN tool: it never reads or writes the vault, never executes an approval
primitive, never uses an APPROVE_* flag, and emits only whitelisted scalar
fields (never input_path, note_refs, next_allowed_action, or any path/URL/secret).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dashboard_summary import (  # noqa: E402
    AFFILIATE_URL_PATTERNS,
    SECRET_RES,
    WEEK_RE,
    DashboardError,
    _fm_str,
    _now_utc,
    _safe_frontmatter,
)

PRODUCT_ID_RE = re.compile(r"^[a-z0-9-]+$")

OUT_DIR = REPO_ROOT / "tmp" / "phase6b-approval-review"
GUARDED_SUFFIX = "tmp/phase6b-approval-review"

# Composed so this source carries no contiguous operator-path or approval
# execution literal (keeps the CI-C guard green and avoids self-matching).
OPERATOR_PATH = "/home/ubuntu/" + "Affiliate-Ai"
APPROVE_EXEC = (
    "APPROVE_PROMOTE" + "=true",
    "APPROVE_DECISION" + "=true",
    "APPROVE_FINALIZE" + "=true",
)

EVENT_HANDLER_RE = re.compile(r"<[^>]*\son[a-z]+\s*=", re.IGNORECASE)
OUTPUT_FORBIDDEN = (
    "http://",
    "https://",
    "file://",
    OPERATOR_PATH,
    "vault/",
    "input_path",
    "note_refs",
    "next_allowed_action",
    *APPROVE_EXEC,
    "tag=",
    "affiliate=",
    "AWS_SECRET_ACCESS_KEY",
    "BEGIN PRIVATE KEY",
    "OPENAI_API_KEY",
    "<script",
    "fetch(",
    "XMLHttpRequest",
    "import(",
    "<iframe",
    "<form",
)

OPERATOR_PLACEHOLDER = "<operator-placeholder>"
REASON_PLACEHOLDER = "<reason-placeholder>"
STATEMENT = (
    "Dry-run only. This packet does not approve, promote, decide, finalize, "
    "or write the vault."
)
READINESS_NOTE = (
    "Readiness is an evidence assessment only; it is not approval and does not "
    "authorize mutation."
)


def _meta(rel: str) -> dict[str, Any]:
    path = REPO_ROOT / rel
    if not path.is_file():
        return {"path": rel, "present": False, "bytes": None, "sha256": None}
    data = path.read_bytes()
    return {
        "path": rel,
        "present": True,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def _load_json(rel: str) -> dict[str, Any] | None:
    path = REPO_ROOT / rel
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def _pick(data: dict[str, Any] | None, keys: tuple[str, ...]) -> dict[str, Any]:
    if not data:
        return {}
    return {k: data[k] for k in keys if k in data}


def build_packet(product_id: str, week: str) -> tuple[dict[str, Any], dict[str, str]]:
    rels = {
        "phase2e_score": f"tmp/phase2e-import-score-report/scores/{product_id}.json",
        "phase2e_report": f"tmp/phase2e-import-score-report/weekly-report-{week}.md",
        "phase2f_summary": f"tmp/phase2f-hermes/operational-summary-{week}.md",
        "phase2j_governance": f"tmp/phase2j-hermes-governance/governance-summary-{week}.md",
        "phase3a_dashboard": f"tmp/phase3a-dashboard/dashboard-{product_id}-{week}.md",
        "phase3b_portfolio": f"tmp/phase3b-portfolio-dashboard/portfolio-{week}.md",
        "phase4d_verification": "tmp/phase4d-demo-verifier/verification-summary.json",
        "phase4e_demo_bundle": "tmp/phase4e-demo-bundle/demo-bundle-summary.json",
        "phase5c_verifier": "tmp/phase5c-ui-shell-verifier/verification-summary.json",
        "phase5d_demo": "tmp/phase5d-ui-shell-demo/ui-shell-demo-summary.json",
    }

    # ── Whitelisted scalar evidence ──────────────────────────────────────────
    score_raw = _load_json(rels["phase2e_score"])
    score = _pick(
        score_raw,
        ("score_decision", "product_opportunity_score", "confidence_score", "missing_signal_count"),
    )

    p4d = _load_json(rels["phase4d_verification"]) or {}
    p4e = _load_json(rels["phase4e_demo_bundle"]) or {}
    p5c = _load_json(rels["phase5c_verifier"]) or {}
    p5d = _load_json(rels["phase5d_demo"]) or {}
    verifier = {
        "phase4d_status": p4d.get("status"),
        "phase5c_verdict": p5c.get("verdict"),
        "phase5d_status": p5d.get("status"),
        "phase5d_verdict": p5d.get("ui_shell_verdict"),
    }

    gov_fm = _safe_frontmatter(REPO_ROOT / rels["phase2j_governance"])
    governance = {
        "promoted_status": _fm_str(gov_fm, "promoted_status"),
        "decision_status": _fm_str(gov_fm, "decision_status"),
        "finalization_status": _fm_str(gov_fm, "finalization_status"),
    }
    compliance_status = _fm_str(gov_fm, "compliance_gate_status") or "not_evaluated"

    sources = [{"name": name, **_meta(rel)} for name, rel in rels.items()]

    # ── Gate-readiness assessment (not permission to mutate) ─────────────────
    score_complete = bool(score) and all(
        score.get(k) is not None
        for k in ("score_decision", "product_opportunity_score", "confidence_score")
    )
    verifier_failed = any(v == "failed" for v in verifier.values() if v is not None)
    promote_gate_ready = score_complete and not verifier_failed
    decision_gate_ready = promote_gate_ready and (REPO_ROOT / rels["phase2j_governance"]).is_file()
    finalization_gate_ready = decision_gate_ready and compliance_status == "approved"

    packet = {
        "type": "phase6b_approval_review",
        "product_id": product_id,
        "report_week": week,
        "generated_at": _now_utc(),
        "score": score,
        "compliance_status": compliance_status,
        "verifier": verifier,
        "governance": governance,
        "sources": sources,
        "operator": OPERATOR_PLACEHOLDER,
        "approval_reason": REASON_PLACEHOLDER,
        "gates": {
            "promote_gate_ready": promote_gate_ready,
            "decision_gate_ready": decision_gate_ready,
            "finalization_gate_ready": finalization_gate_ready,
        },
        "dry_run": True,
        "statement": STATEMENT,
        "readiness_note": READINESS_NOTE,
    }
    return packet, rels


def _b(value: Any) -> str:
    return "true" if value is True else ("false" if value is False else str(value))


def render_md(p: dict[str, Any]) -> str:
    score = p["score"]
    lines = [
        "# Phase 6B Approval Review Packet (dry-run)",
        "",
        f"Product: {p['product_id']}",
        f"Report week: {p['report_week']}",
        f"Generated at: {p['generated_at']}",
        "",
        "## Evidence summary",
        "",
        "| field | value |",
        "| --- | --- |",
        f"| score_decision | {score.get('score_decision')} |",
        f"| product_opportunity_score | {score.get('product_opportunity_score')} |",
        f"| confidence_score | {score.get('confidence_score')} |",
        f"| missing_signal_count | {score.get('missing_signal_count')} |",
        f"| compliance_status | {p['compliance_status']} |",
        f"| phase4d_status | {p['verifier']['phase4d_status']} |",
        f"| phase5c_verdict | {p['verifier']['phase5c_verdict']} |",
        f"| phase5d_status | {p['verifier']['phase5d_status']} |",
        f"| phase5d_verdict | {p['verifier']['phase5d_verdict']} |",
        f"| operator | {p['operator']} |",
        f"| approval_reason | {p['approval_reason']} |",
        "",
        "## Source artifacts",
        "",
        "| name | present | bytes | sha256 |",
        "| --- | --- | --- | --- |",
    ]
    for s in p["sources"]:
        sha = s["sha256"][:16] + "..." if s["sha256"] else "-"
        lines.append(f"| {s['name']} | {_b(s['present'])} | {s['bytes'] if s['bytes'] is not None else '-'} | {sha} |")
    g = p["gates"]
    lines += [
        "",
        "## Gate readiness",
        "",
        f"- promote_gate_ready: {_b(g['promote_gate_ready'])}",
        f"- decision_gate_ready: {_b(g['decision_gate_ready'])}",
        f"- finalization_gate_ready: {_b(g['finalization_gate_ready'])}",
        "",
        p["readiness_note"],
        "",
        "## Dry-run statement",
        "",
        p["statement"],
        "",
        "## Guardrails",
        "",
        "- dry-run only; evidence packet",
        "- no vault reads, no vault writes",
        "- no approval mutation, no primitive execution",
        "- no approval flag use",
        "- no external URLs, no network",
        "",
    ]
    return "\n".join(lines)


def _assert_output_safe(text: str) -> None:
    if any(tok in text for tok in OUTPUT_FORBIDDEN):
        raise DashboardError("Phase 6B output failed its own safety scan")
    if any(p in text for p in AFFILIATE_URL_PATTERNS):
        raise DashboardError("Phase 6B output failed its own safety scan")
    if any(rx.search(text) for rx in SECRET_RES):
        raise DashboardError("Phase 6B output failed its own safety scan")
    if EVENT_HANDLER_RE.search(text):
        raise DashboardError("Phase 6B output failed its own safety scan")


def _guarded_out_dir() -> Path:
    out = OUT_DIR.resolve()
    if not str(out).endswith(GUARDED_SUFFIX):
        raise DashboardError(f"refusing to write outside {GUARDED_SUFFIX}: {out}")
    return out


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 6B dry-run approval review packet builder.")
    parser.add_argument("--product-id", required=True)
    parser.add_argument("--week", required=True)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        if not PRODUCT_ID_RE.match(args.product_id):
            raise DashboardError(f"product_id must match {PRODUCT_ID_RE.pattern}, got: {args.product_id}")
        if not WEEK_RE.match(args.week):
            raise DashboardError(f"week must match {WEEK_RE.pattern}, got: {args.week}")
        packet, _ = build_packet(args.product_id, args.week)
        packet_json = json.dumps(packet, indent=2) + "\n"
        packet_md = render_md(packet)
        _assert_output_safe(packet_json)
        _assert_output_safe(packet_md)
        out_dir = _guarded_out_dir()
        out_dir.mkdir(parents=True, exist_ok=True)
        json_path = out_dir / f"review-{args.product_id}-{args.week}.json"
        md_path = out_dir / f"review-{args.product_id}-{args.week}.md"
        json_path.write_text(packet_json, encoding="utf-8")
        md_path.write_text(packet_md, encoding="utf-8")
    except DashboardError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"review_packet_json: {GUARDED_SUFFIX}/review-{args.product_id}-{args.week}.json")
    print(f"review_packet_md: {GUARDED_SUFFIX}/review-{args.product_id}-{args.week}.md")
    print("phase6b_status: success")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
