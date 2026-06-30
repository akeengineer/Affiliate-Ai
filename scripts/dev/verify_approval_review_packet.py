#!/usr/bin/env python3
"""Phase 6C Approval Review Packet Verifier.

Read-only verifier over the Phase 6B dry-run approval review packet. It reads the
packet JSON/Markdown bodies (the verification target), validates structure and
safety, checks each listed source by existence/size/hash only (never body
ingestion), and writes a verification report/summary under
tmp/phase6c-approval-review-verifier/. It never reads or writes the vault, never
executes an approval primitive, and never uses an approval flag.
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
PACKET_DIR = "tmp/phase6b-approval-review"
OUT_DIR = REPO_ROOT / "tmp" / "phase6c-approval-review-verifier"
GUARDED_SUFFIX = "tmp/phase6c-approval-review-verifier"

# Composed so this source carries no contiguous operator-path or approval
# execution literal (keeps the CI-C guard green and avoids self-matching).
OPERATOR_PATH = "/home/ubuntu/" + "Affiliate-Ai"
APPROVE_EXEC = (
    "APPROVE_PROMOTE" + "=true",
    "APPROVE_DECISION" + "=true",
    "APPROVE_FINALIZE" + "=true",
)
WORKFLOW_RUN_TOKENS = ("run_phase2" + "g", "run_phase2" + "h", "run_phase2" + "i")

EVENT_HANDLER_RE = re.compile(r"<[^>]*\son[a-z]+\s*=", re.IGNORECASE)
LEAK_TOKENS = (
    "http://",
    "https://",
    "file://",
    OPERATOR_PATH,
    "vault/",
    "input_path",
    "note_refs",
    "next_allowed_action",
    *APPROVE_EXEC,
)
OUTPUT_FORBIDDEN = (
    *LEAK_TOKENS,
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


def _is_scalar(value: Any) -> bool:
    return isinstance(value, (str, int, float, bool)) or value is None


def _safe_source_path(path: Any) -> bool:
    if not isinstance(path, str) or not path:
        return False
    if path.startswith("/") or ".." in path.split("/"):
        return False
    if not path.startswith("tmp/") or "vault/" in path:
        return False
    return True


def verify(product_id: str, week: str) -> dict[str, Any]:
    json_rel = f"{PACKET_DIR}/review-{product_id}-{week}.json"
    md_rel = f"{PACKET_DIR}/review-{product_id}-{week}.md"
    json_path = REPO_ROOT / json_rel
    md_path = REPO_ROOT / md_rel

    checks: dict[str, bool] = {}
    warnings: list[str] = []
    source_integrity: list[dict[str, Any]] = []

    checks["packet_json_exists"] = json_path.is_file()
    checks["packet_md_exists"] = md_path.is_file()

    packet: dict[str, Any] = {}
    packet_text = ""
    if checks["packet_json_exists"]:
        try:
            packet = json.loads(json_path.read_text(encoding="utf-8"))
            packet_text += json_path.read_text(encoding="utf-8")
        except (json.JSONDecodeError, OSError):
            packet = {}
    if checks["packet_md_exists"]:
        packet_text += "\n" + md_path.read_text(encoding="utf-8")
    if not isinstance(packet, dict):
        packet = {}

    score = packet.get("score") if isinstance(packet.get("score"), dict) else {}
    gates = packet.get("gates") if isinstance(packet.get("gates"), dict) else {}
    verifier = packet.get("verifier")
    compliance_status = packet.get("compliance_status")

    checks["packet_type_ok"] = packet.get("type") == "phase6b_approval_review"
    checks["dry_run_true"] = packet.get("dry_run") is True
    checks["ids_match"] = packet.get("product_id") == product_id and packet.get("report_week") == week
    checks["evidence_present"] = (
        score.get("score_decision") is not None
        and score.get("product_opportunity_score") is not None
        and score.get("confidence_score") is not None
        and compliance_status is not None
        and isinstance(verifier, dict)
        and isinstance(gates, dict)
    )
    checks["score_scalar_safe"] = bool(score) and all(_is_scalar(v) for v in score.values())
    checks["compliance_safe"] = isinstance(compliance_status, str) and not any(
        tok in compliance_status for tok in OUTPUT_FORBIDDEN
    )
    checks["verifier_present"] = isinstance(verifier, dict)
    checks["gates_complete"] = all(
        isinstance(gates.get(k), bool)
        for k in ("promote_gate_ready", "decision_gate_ready", "finalization_gate_ready")
    )
    checks["finalization_consistent"] = (gates.get("finalization_gate_ready") is not True) or (
        compliance_status == "approved"
    )

    # ── Source integrity (existence/size/hash only) ──────────────────────────
    sources = packet.get("sources") if isinstance(packet.get("sources"), list) else []
    sources_ok = bool(sources) or not checks["packet_json_exists"]
    for src in sources:
        if not isinstance(src, dict) or not _safe_source_path(src.get("path")):
            sources_ok = False
            continue
        rel = src["path"]
        cur = REPO_ROOT / rel
        recorded_present = src.get("present") is True
        entry = {"name": src.get("name"), "path": rel, "present": cur.is_file()}
        if not recorded_present:
            warnings.append(f"source marked not present: {src.get('name')}")
            entry["bytes_match"] = None
            entry["hash_match"] = None
        elif not cur.is_file():
            warnings.append(f"source missing but packet recorded present: {src.get('name')}")
            entry["bytes_match"] = False
            entry["hash_match"] = False
        else:
            data = cur.read_bytes()
            bytes_match = len(data) == src.get("bytes")
            hash_match = hashlib.sha256(data).hexdigest() == src.get("sha256")
            entry["bytes_match"] = bytes_match
            entry["hash_match"] = hash_match
            if not bytes_match or not hash_match:
                warnings.append(f"source changed since packet: {src.get('name')}")
        source_integrity.append(entry)
    checks["sources_tmp_only"] = sources_ok

    checks["no_leakage"] = not any(tok in packet_text for tok in LEAK_TOKENS) and not any(
        p in packet_text for p in AFFILIATE_URL_PATTERNS
    ) and not any(rx.search(packet_text) for rx in SECRET_RES)
    checks["no_approval_execution"] = not any(tok in packet_text for tok in APPROVE_EXEC) and not any(
        tok in packet_text for tok in WORKFLOW_RUN_TOKENS
    )
    note = packet.get("readiness_note", "")
    checks["readiness_note_ok"] = isinstance(note, str) and (
        "does not authorize" in note.lower() or "not authorization" in note.lower()
    )

    if not all(checks.values()):
        verdict = "failed"
    elif warnings:
        verdict = "warning"
    else:
        verdict = "ready"

    return {
        "type": "phase6c_approval_review_verification",
        "product_id": product_id,
        "report_week": week,
        "generated_at": _now_utc(),
        "verdict": verdict,
        "checks": checks,
        "warnings": warnings,
        "source_integrity": source_integrity,
        "packet_path": json_rel,
    }


CHECK_TITLES = {
    "packet_json_exists": "packet JSON exists",
    "packet_md_exists": "packet Markdown exists",
    "packet_type_ok": "packet type is phase6b_approval_review",
    "dry_run_true": "dry_run is true",
    "ids_match": "product_id and report_week match",
    "evidence_present": "required evidence fields present",
    "score_scalar_safe": "score fields are scalar and safe",
    "compliance_safe": "compliance_status is safe",
    "verifier_present": "verifier section present",
    "gates_complete": "gates contain three booleans",
    "finalization_consistent": "finalization false unless compliance approved",
    "sources_tmp_only": "all sources relative under tmp/",
    "no_leakage": "no leakage tokens in packet",
    "no_approval_execution": "no approval execution references",
    "readiness_note_ok": "readiness is not authorization to mutate",
}


def render_md(result: dict[str, Any]) -> str:
    lines = [
        "# Phase 6C Approval Review Packet Verification",
        "",
        f"Product: {result['product_id']}",
        f"Report week: {result['report_week']}",
        f"Generated at: {result['generated_at']}",
        f"Verdict: {result['verdict']}",
        "",
        "## Checks",
        "",
        "| check | result |",
        "| --- | --- |",
    ]
    for key, ok in result["checks"].items():
        lines.append(f"| {CHECK_TITLES.get(key, key)} | {'PASS' if ok else 'FAIL'} |")
    lines += ["", "## Warnings", ""]
    if result["warnings"]:
        for w in result["warnings"]:
            lines.append(f"- WARN: {w}")
    else:
        lines.append("- none")
    lines += ["", "## Source integrity", "", "| name | present | bytes_match | hash_match |", "| --- | --- | --- | --- |"]
    for s in result["source_integrity"]:
        lines.append(f"| {s['name']} | {s['present']} | {s['bytes_match']} | {s['hash_match']} |")
    lines += [
        "",
        "## Guardrails",
        "",
        "- read-only verifier; reads existing packet only",
        "- no vault reads/writes, no approval mutation, no primitive execution",
        "- no approval flag use, no external URLs, no network",
        "",
    ]
    return "\n".join(lines)


def _assert_output_safe(text: str) -> None:
    if any(tok in text for tok in OUTPUT_FORBIDDEN):
        raise DashboardError("Phase 6C output failed its own safety scan")
    if any(p in text for p in AFFILIATE_URL_PATTERNS):
        raise DashboardError("Phase 6C output failed its own safety scan")
    if any(rx.search(text) for rx in SECRET_RES):
        raise DashboardError("Phase 6C output failed its own safety scan")
    if EVENT_HANDLER_RE.search(text):
        raise DashboardError("Phase 6C output failed its own safety scan")


def _guarded_out_dir() -> Path:
    out = OUT_DIR.resolve()
    if not str(out).endswith(GUARDED_SUFFIX):
        raise DashboardError(f"refusing to write outside {GUARDED_SUFFIX}: {out}")
    return out


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 6C approval review packet verifier.")
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
        result = verify(args.product_id, args.week)
        result_json = json.dumps(result, indent=2) + "\n"
        result_md = render_md(result)
        _assert_output_safe(result_json)
        _assert_output_safe(result_md)
        out_dir = _guarded_out_dir()
        out_dir.mkdir(parents=True, exist_ok=True)
        json_path = out_dir / f"verification-review-{args.product_id}-{args.week}.json"
        md_path = out_dir / f"verification-review-{args.product_id}-{args.week}.md"
        json_path.write_text(result_json, encoding="utf-8")
        md_path.write_text(result_md, encoding="utf-8")
    except DashboardError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    verdict = result["verdict"]
    print(f"verification_review_json: {GUARDED_SUFFIX}/verification-review-{args.product_id}-{args.week}.json")
    print(f"verification_review_md: {GUARDED_SUFFIX}/verification-review-{args.product_id}-{args.week}.md")
    print(f"verdict: {verdict}")
    if verdict == "failed":
        print("phase6c_status: failed")
        return 1
    print("phase6c_status: success")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
