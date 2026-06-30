#!/usr/bin/env python3
"""Phase 6E Dry-run Manual Approval Execution Planner.

Generates a dry-run execution plan from the Phase 6B packet and Phase 6C
verifier output, using the Phase 6D boundary doc as a contract reference
(existence/size/hash only). It shows what a future manual approval command would
require before executing, but executes nothing: no vault access, no primitive
execution, no approval flag use.
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
    _now_utc,
)

PRODUCT_ID_RE = re.compile(r"^[a-z0-9-]+$")
OUT_DIR = REPO_ROOT / "tmp" / "phase6e-approval-execution-plan"
GUARDED_SUFFIX = "tmp/phase6e-approval-execution-plan"
BOUNDARY_DOC_REL = "docs/MANUAL_APPROVAL_EXECUTION_BOUNDARY.md"

GATE_ORDER = ["promote", "decision", "finalization"]
PRIMITIVES = {
    "promote": "promote_product_candidates.py",
    "decision": "create_decision.py",
    "finalization": "finalize_decision.py",
}
FLAGS = {
    "promote": "APPROVE_PROMOTE",
    "decision": "APPROVE_DECISION",
    "finalization": "APPROVE_FINALIZE",
}

# Composed so this source carries no contiguous operator-path or approval
# execution literal (keeps the CI-C guard green and avoids self-matching).
OPERATOR_PATH = "/home/ubuntu/" + "Affiliate-Ai"
APPROVE_EXEC = tuple(f"{flag}={'true'}" for flag in FLAGS.values())
COMMAND_FORMS = tuple(f"python scripts/dev/{p}" for p in PRIMITIVES.values())

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
    *COMMAND_FORMS,
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
    "Dry-run only. This plan does not approve, promote, decide, finalize, or "
    "write the vault."
)


def _load_json(rel: str) -> dict[str, Any] | None:
    path = REPO_ROOT / rel
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def _meta(rel: str) -> dict[str, Any]:
    path = REPO_ROOT / rel
    if not path.is_file():
        return {"present": False, "bytes": None, "sha256": None}
    data = path.read_bytes()
    return {"present": True, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def build_plan(product_id: str, week: str) -> dict[str, Any]:
    packet_rel = f"tmp/phase6b-approval-review/review-{product_id}-{week}.json"
    verifier_rel = f"tmp/phase6c-approval-review-verifier/verification-review-{product_id}-{week}.json"

    packet = _load_json(packet_rel)
    verifier = _load_json(verifier_rel)
    packet_text = (REPO_ROOT / packet_rel).read_text(encoding="utf-8") if (REPO_ROOT / packet_rel).is_file() else ""
    boundary_meta = _meta(BOUNDARY_DOC_REL)

    pkt = packet or {}
    vrf = verifier or {}
    vchecks = vrf.get("checks") if isinstance(vrf.get("checks"), dict) else {}
    gates = pkt.get("gates") if isinstance(pkt.get("gates"), dict) else {}
    compliance_status = pkt.get("compliance_status")
    verifier_verdict = vrf.get("verdict")

    no_exec_signal = not any(tok in packet_text for tok in (*APPROVE_EXEC, *COMMAND_FORMS, "next_allowed_action"))
    ids_match = (
        pkt.get("product_id") == product_id
        and pkt.get("report_week") == week
        and vrf.get("product_id") == product_id
        and vrf.get("report_week") == week
    )

    preconditions = {
        "packet_exists": packet is not None,
        "verifier_exists": verifier is not None,
        "verifier_ready": verifier_verdict == "ready",
        "ids_match": ids_match,
        "packet_dry_run_true": pkt.get("dry_run") is True,
        "no_approval_execution_signal": no_exec_signal,
        "no_leakage_confirmed": vchecks.get("no_leakage") is True,
        "sources_tmp_only_confirmed": vchecks.get("sources_tmp_only") is True,
        "finalization_consistent": vchecks.get("finalization_consistent") is True,
        "boundary_doc_exists": boundary_meta["present"],
        "gate_order_defined": True,
        "finalization_blocked_unless_compliance_approved": True,
    }

    # ── Hard-fail conditions -> verdict failed ───────────────────────────────
    hard_fail = (
        packet is None
        or verifier is None
        or not boundary_meta["present"]
        or verifier_verdict not in ("ready", "warning")
        or not ids_match
        or pkt.get("dry_run") is not True
        or not no_exec_signal
        or vchecks.get("no_leakage") is not True
        or vchecks.get("sources_tmp_only") is not True
        or vchecks.get("finalization_consistent") is not True
    )

    blockers: list[str] = []
    per_gate_plan: dict[str, Any] = {}

    if hard_fail:
        for gate in GATE_ORDER:
            per_gate_plan[gate] = {
                "primitive_name": PRIMITIVES[gate],
                "required_flag_name": FLAGS[gate],
                "plan_ready": False,
                "blocked_reason": "hard precondition failed",
            }
        blockers.append("hard precondition failed")
        verdict = "failed"
    else:
        promote_ready = gates.get("promote_gate_ready") is True
        decision_ready = promote_ready and gates.get("decision_gate_ready") is True
        finalization_ready = (
            decision_ready and gates.get("finalization_gate_ready") is True and compliance_status == "approved"
        )
        ready_map = {"promote": promote_ready, "decision": decision_ready, "finalization": finalization_ready}
        for gate in GATE_ORDER:
            reason = None
            if not ready_map[gate]:
                if gate == "finalization" and compliance_status != "approved":
                    reason = "compliance_status not approved"
                else:
                    reason = f"{gate} gate not ready in packet"
                blockers.append(f"{gate}: {reason}")
            per_gate_plan[gate] = {
                "primitive_name": PRIMITIVES[gate],
                "required_flag_name": FLAGS[gate],
                "plan_ready": ready_map[gate],
                "blocked_reason": reason,
            }
        if verifier_verdict == "warning":
            verdict = "blocked"
            blockers.append("verifier verdict is warning (evidence stale)")
        elif all(ready_map.values()):
            verdict = "ready"
        else:
            verdict = "blocked"

    plan = {
        "type": "phase6e_approval_execution_plan",
        "product_id": product_id,
        "report_week": week,
        "generated_at": _now_utc(),
        "dry_run": True,
        "packet_path": packet_rel,
        "verifier_path": verifier_rel,
        "boundary_doc_path": BOUNDARY_DOC_REL,
        "boundary_doc": boundary_meta,
        "verifier_verdict": verifier_verdict,
        "preconditions": preconditions,
        "proposed_gate_sequence": list(GATE_ORDER),
        "per_gate_plan": per_gate_plan,
        "required_future_operator_inputs": [
            "operator identity",
            "approval reason",
            "gate-specific approval intent",
        ],
        "audit_preview": {
            "product_id": product_id,
            "report_week": week,
            "gate_name": "<gate-name-placeholder>",
            "primitive_name": "<primitive-name-placeholder>",
            "operator": OPERATOR_PLACEHOLDER,
            "approval_reason": REASON_PLACEHOLDER,
            "timestamp": _now_utc(),
            "source_packet_path": packet_rel,
            "verifier_path": verifier_rel,
            "precondition_summary": "dry_run_plan_preconditions",
            "result_summary": "dry_run_plan",
        },
        "blockers": blockers,
        "verdict": verdict,
        "statement": STATEMENT,
    }
    return plan


def _b(value: Any) -> str:
    return "true" if value is True else ("false" if value is False else str(value))


def render_md(plan: dict[str, Any]) -> str:
    lines = [
        "# Phase 6E Approval Execution Plan (dry-run)",
        "",
        f"Product: {plan['product_id']}",
        f"Report week: {plan['report_week']}",
        f"Generated at: {plan['generated_at']}",
        f"Verifier verdict: {plan['verifier_verdict']}",
        f"Verdict: {plan['verdict']}",
        "",
        "## Preconditions",
        "",
        "| precondition | result |",
        "| --- | --- |",
    ]
    for key, ok in plan["preconditions"].items():
        lines.append(f"| {key} | {_b(ok)} |")
    lines += [
        "",
        f"## Proposed gate sequence: {' -> '.join(plan['proposed_gate_sequence'])}",
        "",
        "## Gate plan",
        "",
        "| gate | primitive | flag | plan_ready | blocked_reason |",
        "| --- | --- | --- | --- | --- |",
    ]
    for gate in plan["proposed_gate_sequence"]:
        g = plan["per_gate_plan"][gate]
        lines.append(
            f"| {gate} | {g['primitive_name']} | {g['required_flag_name']} | "
            f"{_b(g['plan_ready'])} | {g['blocked_reason'] or '-'} |"
        )
    lines += ["", "## Required future operator inputs", ""]
    for item in plan["required_future_operator_inputs"]:
        lines.append(f"- {item}")
    ap = plan["audit_preview"]
    lines += [
        "",
        "## Audit preview",
        "",
        f"- product_id: {ap['product_id']}",
        f"- report_week: {ap['report_week']}",
        f"- gate_name: {ap['gate_name']}",
        f"- primitive_name: {ap['primitive_name']}",
        f"- operator: {ap['operator']}",
        f"- approval_reason: {ap['approval_reason']}",
        f"- timestamp: {ap['timestamp']}",
        f"- source_packet_path: {ap['source_packet_path']}",
        f"- verifier_path: {ap['verifier_path']}",
        f"- precondition_summary: {ap['precondition_summary']}",
        f"- result_summary: {ap['result_summary']}",
        "",
        "## Blockers",
        "",
    ]
    if plan["blockers"]:
        for b in plan["blockers"]:
            lines.append(f"- {b}")
    else:
        lines.append("- none")
    lines += [
        "",
        "## Dry-run statement",
        "",
        plan["statement"],
        "",
        "## Guardrails",
        "",
        "- dry-run plan only; no execution",
        "- no vault reads/writes, no approval mutation, no primitive execution",
        "- no approval flag use, no external URLs, no network",
        "",
    ]
    return "\n".join(lines)


def _assert_output_safe(text: str) -> None:
    if any(tok in text for tok in OUTPUT_FORBIDDEN):
        raise DashboardError("Phase 6E output failed its own safety scan")
    if any(p in text for p in AFFILIATE_URL_PATTERNS):
        raise DashboardError("Phase 6E output failed its own safety scan")
    if any(rx.search(text) for rx in SECRET_RES):
        raise DashboardError("Phase 6E output failed its own safety scan")
    if EVENT_HANDLER_RE.search(text):
        raise DashboardError("Phase 6E output failed its own safety scan")


def _guarded_out_dir() -> Path:
    out = OUT_DIR.resolve()
    if not str(out).endswith(GUARDED_SUFFIX):
        raise DashboardError(f"refusing to write outside {GUARDED_SUFFIX}: {out}")
    return out


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 6E dry-run approval execution planner.")
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
        plan = build_plan(args.product_id, args.week)
        plan_json = json.dumps(plan, indent=2) + "\n"
        plan_md = render_md(plan)
        _assert_output_safe(plan_json)
        _assert_output_safe(plan_md)
        out_dir = _guarded_out_dir()
        out_dir.mkdir(parents=True, exist_ok=True)
        json_path = out_dir / f"execution-plan-{args.product_id}-{args.week}.json"
        md_path = out_dir / f"execution-plan-{args.product_id}-{args.week}.md"
        json_path.write_text(plan_json, encoding="utf-8")
        md_path.write_text(plan_md, encoding="utf-8")
    except DashboardError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    verdict = plan["verdict"]
    print(f"execution_plan_json: {GUARDED_SUFFIX}/execution-plan-{args.product_id}-{args.week}.json")
    print(f"execution_plan_md: {GUARDED_SUFFIX}/execution-plan-{args.product_id}-{args.week}.md")
    print(f"verdict: {verdict}")
    if verdict == "failed":
        print("phase6e_status: failed")
        return 1
    print("phase6e_status: success")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
