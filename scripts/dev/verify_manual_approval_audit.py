#!/usr/bin/env python3
"""Phase 7B Manual Approval Audit Verifier.

Runtime read-only verifier over one JSON manual approval audit artifact that a
future single-gate manual approval wrapper would produce. It reads exactly one
audit artifact (the verification target), validates required fields, gate/
primitive/flag mapping, mutation consistency, referenced artifact path safety,
and scans the raw body for forbidden content, then writes a verification
report/summary under tmp/phase7b-audit-verifier/. It never reads or writes the
vault, never executes an approval primitive, never mutates the input, and never
uses an approval flag.

Forbidden content is reported by category label only; the verifier never echoes
raw dangerous substrings into its output. Dangerous literals are composed at
runtime so this source carries no contiguous forbidden token (keeps the CI-C
static guard green and prevents the verifier from matching itself).
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
OUT_DIR = REPO_ROOT / "tmp" / "phase7b-audit-verifier"
GUARDED_SUFFIX = "tmp/phase7b-audit-verifier"
CURRENT_SCHEMA_VERSION = "1"

REQUIRED_FIELDS = (
    "product_id",
    "report_week",
    "selected_gate",
    "primitive_name",
    "operator",
    "approval_reason",
    "timestamp",
    "source_packet_path",
    "verifier_path",
    "execution_plan_path",
    "precondition_summary",
    "result_summary",
    "outcome",
    "mutation_attempted",
    "gate_specific_approval_intent",
    "approved_flag_name",
    "wrapper_version",
    "audit_schema_version",
)

ALLOWED_GATES = ("promote", "decision", "finalization")
GATE_PRIMITIVE = {
    "promote": "promote_product_candidates.py",
    "decision": "create_decision.py",
    "finalization": "finalize_decision.py",
}
GATE_FLAG = {
    "promote": "APPROVE_PROMOTE",
    "decision": "APPROVE_DECISION",
    "finalization": "APPROVE_FINALIZE",
}
ALLOWED_OUTCOMES = ("success", "failure", "blocked", "prevented")
REF_PREFIX = {
    "source_packet_path": "tmp/phase6b-approval-review/",
    "verifier_path": "tmp/phase6c-approval-review-verifier/",
    "execution_plan_path": "tmp/phase6e-approval-execution-plan/",
}

# ── Composed dangerous literals (no contiguous forbidden token in source) ──────
OPERATOR_PATH = "/home/ubuntu/" + "Affiliate-Ai"
TRAVERSAL = ".." + "/"
VAULT_MARKER = "vault" + "/"
URL_SCHEMES = ("http" + "://", "https" + "://", "file" + "://")
APPROVE_ASSIGN = (
    "APPROVE_PROMOTE" + "=true",
    "APPROVE_DECISION" + "=true",
    "APPROVE_FINALIZE" + "=true",
)
RUN_FORMS = (
    "bash scripts/dev/run_phase2" + "g",
    "bash scripts/dev/run_phase2" + "h",
    "bash scripts/dev/run_phase2" + "i",
)
PY_FORMS = tuple("python scripts/dev/" + name for name in GATE_PRIMITIVE.values())
SECRET_MARKERS = ("AWS_SECRET_" + "ACCESS_KEY", "BEGIN PRIVATE " + "KEY", "OPENAI_" + "API_KEY")
GLOBAL_APPROVAL_TOKENS = (
    "approve-all",
    "approve_all",
    "approve all",
    "global approval",
    "global-approve",
    "global_approve",
    "multi-gate",
    "multi_gate",
    "next-gate",
    "chain execution",
)

EVENT_HANDLER_RE = re.compile(r"<[^>]*\son[a-z]+\s*=", re.IGNORECASE)

# Category labels are the only evidence emitted; never the raw match.
FORBIDDEN_CATEGORIES = (
    "approval_assignment",
    "phase2_run_command_form",
    "primitive_python_command_form",
    "external_url",
    "secret_marker",
    "operator_local_path",
    "vault_path",
    "traversal_marker",
    "multi_gate_or_global_approval",
)

# Output must never contain any of these raw tokens.
OUTPUT_FORBIDDEN = (
    *URL_SCHEMES,
    OPERATOR_PATH,
    VAULT_MARKER,
    TRAVERSAL,
    *APPROVE_ASSIGN,
    *RUN_FORMS,
    *PY_FORMS,
    *SECRET_MARKERS,
    "AKIA",
    "sk-",
)


def _scan_forbidden(text: str) -> list[str]:
    """Return sorted forbidden category labels found in the raw audit body."""
    low = text.lower()
    cats: set[str] = set()
    if any(tok in text for tok in APPROVE_ASSIGN):
        cats.add("approval_assignment")
    if any(tok in text for tok in RUN_FORMS):
        cats.add("phase2_run_command_form")
    if any(tok in text for tok in PY_FORMS):
        cats.add("primitive_python_command_form")
    if any(scheme in text for scheme in URL_SCHEMES) or any(p in text for p in AFFILIATE_URL_PATTERNS):
        cats.add("external_url")
    if any(tok in text for tok in SECRET_MARKERS) or any(rx.search(text) for rx in SECRET_RES):
        cats.add("secret_marker")
    if OPERATOR_PATH in text:
        cats.add("operator_local_path")
    if VAULT_MARKER in text:
        cats.add("vault_path")
    if TRAVERSAL in text:
        cats.add("traversal_marker")
    if any(tok in low for tok in GLOBAL_APPROVAL_TOKENS):
        cats.add("multi_gate_or_global_approval")
    return sorted(cats)


def _safe_input_path(path: str) -> tuple[bool, str]:
    if not isinstance(path, str) or not path:
        return False, "empty"
    if any(scheme in path for scheme in URL_SCHEMES):
        return False, "external_url"
    if OPERATOR_PATH in path:
        return False, "operator_local_path"
    if path.startswith("/"):
        return False, "absolute"
    if ".." in path.split("/"):
        return False, "traversal"
    if not path.startswith("tmp/"):
        return False, "not_tmp"
    if VAULT_MARKER in path:
        return False, "vault"
    return True, "ok"


def _safe_ref_path(path: Any, prefix: str) -> bool:
    if not isinstance(path, str) or not path:
        return False
    if any(scheme in path for scheme in URL_SCHEMES):
        return False
    if OPERATOR_PATH in path:
        return False
    if path.startswith("/") or ".." in path.split("/"):
        return False
    if VAULT_MARKER in path:
        return False
    return path.startswith(prefix)


def build_result(raw_path: str) -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []

    in_ok, in_cat = _safe_input_path(raw_path)
    result: dict[str, Any] = {
        "type": "phase7b_manual_approval_audit_verification",
        "generated_at": _now_utc(),
        "source_audit_path": raw_path if in_ok else None,
        "source_audit_sha256": None,
        "source_audit_bytes": None,
        "product_id": None,
        "report_week": None,
        "selected_gate": None,
        "required_fields": {"present": [], "missing": list(REQUIRED_FIELDS), "ok": False},
        "gate_consistency": {"ok": False},
        "path_safety": {"input_path_safe": in_ok, "referenced_paths_safe": None, "ok": False},
        "mutation_consistency": {"ok": False, "reason": "not_evaluated"},
        "forbidden_content": {"clean": True, "categories": []},
        "referenced_artifacts": [],
        "warnings": [],
        "failures": [],
        "verdict": "invalid",
        "statement": "",
    }

    if not in_ok:
        result["failures"] = ["unsafe_input_path"]
        result["verdict"] = "invalid"
        result["statement"] = _statement("invalid")
        return result

    full = REPO_ROOT / raw_path
    if not full.is_file():
        result["failures"] = ["input_artifact_missing"]
        result["statement"] = _statement("invalid")
        return result

    raw_bytes = full.read_bytes()
    raw_text = raw_bytes.decode("utf-8", errors="replace")
    result["source_audit_sha256"] = hashlib.sha256(raw_bytes).hexdigest()
    result["source_audit_bytes"] = len(raw_bytes)

    cats = _scan_forbidden(raw_text)
    result["forbidden_content"] = {"clean": not cats, "categories": cats}
    failures.extend(cats)

    try:
        audit = json.loads(raw_text)
        if not isinstance(audit, dict):
            raise ValueError("audit root is not an object")
    except (json.JSONDecodeError, ValueError):
        failures.append("invalid_json")
        result["failures"] = sorted(set(failures))
        result["statement"] = _statement("invalid")
        return result

    present = [f for f in REQUIRED_FIELDS if f in audit]
    missing = [f for f in REQUIRED_FIELDS if f not in audit]
    result["required_fields"] = {"present": present, "missing": missing, "ok": not missing}
    if missing:
        failures.append("missing_required_field")

    pid = audit.get("product_id")
    week = audit.get("report_week")
    gate = audit.get("selected_gate")
    pid_safe = isinstance(pid, str) and bool(PRODUCT_ID_RE.match(pid))
    week_safe = isinstance(week, str) and bool(WEEK_RE.match(week))
    gate_valid = gate in ALLOWED_GATES

    result["product_id"] = pid if pid_safe else None
    result["report_week"] = week if week_safe else None
    result["selected_gate"] = gate if gate_valid else None
    if not pid_safe or not week_safe:
        failures.append("unsafe_filename_field")

    primitive = audit.get("primitive_name")
    flag = audit.get("approved_flag_name")
    primitive_match = gate_valid and primitive == GATE_PRIMITIVE[gate]
    flag_match = gate_valid and flag == GATE_FLAG[gate]
    single_gate = "multi_gate_or_global_approval" not in cats
    result["gate_consistency"] = {
        "selected_gate_valid": gate_valid,
        "primitive_match": primitive_match,
        "flag_match": flag_match,
        "single_gate": single_gate,
        "ok": gate_valid and primitive_match and flag_match and single_gate,
    }
    if not gate_valid:
        failures.append("invalid_selected_gate")
    if gate_valid and not primitive_match:
        failures.append("primitive_mapping_mismatch")
    if gate_valid and not flag_match:
        failures.append("approval_flag_mapping_mismatch")

    outcome = audit.get("outcome")
    mutation = audit.get("mutation_attempted")
    if outcome not in ALLOWED_OUTCOMES:
        failures.append("invalid_outcome")
    if not isinstance(mutation, bool):
        mut_ok, mut_reason = False, "mutation_attempted_not_boolean"
    elif outcome in ("blocked", "prevented"):
        mut_ok = mutation is False
        mut_reason = "ok" if mut_ok else "blocked_prevented_require_false"
    elif outcome in ("success", "failure"):
        mut_ok, mut_reason = True, "explicit_boolean_ok"
    else:
        mut_ok, mut_reason = False, "outcome_invalid"
    result["mutation_consistency"] = {"ok": mut_ok, "reason": mut_reason}
    if not mut_ok:
        failures.append("mutation_inconsistency")

    ref_entries: list[dict[str, Any]] = []
    ref_all_safe = True
    for field, prefix in REF_PREFIX.items():
        val = audit.get(field)
        safe = _safe_ref_path(val, prefix)
        entry: dict[str, Any] = {"field": field, "expected_prefix": prefix, "safe": safe}
        if not safe:
            ref_all_safe = False
            entry["exists"] = None
            entry["fresh"] = None
        else:
            exists = (REPO_ROOT / val).is_file()
            entry["exists"] = exists
            entry["fresh"] = exists
            if not exists:
                warnings.append(f"referenced_artifact_missing:{field}")
        ref_entries.append(entry)
    result["referenced_artifacts"] = ref_entries
    result["path_safety"] = {
        "input_path_safe": in_ok,
        "referenced_paths_safe": ref_all_safe,
        "ok": in_ok and ref_all_safe,
    }
    if not ref_all_safe:
        failures.append("unsafe_referenced_path")

    if audit.get("audit_schema_version") != CURRENT_SCHEMA_VERSION:
        warnings.append("audit_schema_version_stale")

    failures = sorted(set(failures))
    warnings = sorted(set(warnings))
    result["failures"] = failures
    result["warnings"] = warnings
    if failures:
        verdict = "invalid"
    elif warnings:
        verdict = "warning"
    else:
        verdict = "valid"
    result["verdict"] = verdict
    result["statement"] = _statement(verdict)
    return result


def _statement(verdict: str) -> str:
    return (
        f"Read-only manual approval audit verification: {verdict}. "
        "No vault read/write, no approval mutation, no primitive execution, "
        "no approval inference."
    )


def _out_basename(result: dict[str, Any]) -> str:
    pid = result.get("product_id")
    week = result.get("report_week")
    gate = result.get("selected_gate")
    if isinstance(pid, str) and isinstance(week, str) and gate in ALLOWED_GATES:
        return f"audit-verification-{pid}-{week}-{gate}"
    return "audit-verification-invalid"


def render_md(result: dict[str, Any]) -> str:
    lines = [
        "# Phase 7B Manual Approval Audit Verification",
        "",
        f"Source audit path: {result.get('source_audit_path')}",
        f"Product: {result.get('product_id')}",
        f"Report week: {result.get('report_week')}",
        f"Selected gate: {result.get('selected_gate')}",
        f"Generated at: {result['generated_at']}",
        f"Verdict: {result['verdict']}",
        "",
        "## Warnings",
        "",
    ]
    if result["warnings"]:
        lines += [f"- WARN: {w}" for w in result["warnings"]]
    else:
        lines.append("- none")
    lines += ["", "## Failures (category labels only)", ""]
    if result["failures"]:
        lines += [f"- FAIL: {f}" for f in result["failures"]]
    else:
        lines.append("- none")
    lines += ["", "## Forbidden content categories", ""]
    if result["forbidden_content"]["categories"]:
        lines += [f"- {c}" for c in result["forbidden_content"]["categories"]]
    else:
        lines.append("- none")
    lines += [
        "",
        "## Guardrails",
        "",
        "- read-only verifier; reads one audit artifact only",
        "- no vault read/write, no approval mutation, no primitive execution",
        "- no approval flag use, no external URLs, no network",
        "- forbidden content reported by category label only",
        "",
        f"## Statement\n\n{result['statement']}\n",
    ]
    return "\n".join(lines)


def _assert_output_safe(text: str) -> None:
    if any(tok in text for tok in OUTPUT_FORBIDDEN):
        raise DashboardError("Phase 7B output failed its own safety scan")
    if any(p in text for p in AFFILIATE_URL_PATTERNS):
        raise DashboardError("Phase 7B output failed its own safety scan")
    if any(rx.search(text) for rx in SECRET_RES):
        raise DashboardError("Phase 7B output failed its own safety scan")
    if EVENT_HANDLER_RE.search(text):
        raise DashboardError("Phase 7B output failed its own safety scan")


def _safe_invalid_result(generated_at: str) -> dict[str, Any]:
    return {
        "type": "phase7b_manual_approval_audit_verification",
        "generated_at": generated_at,
        "source_audit_path": None,
        "source_audit_sha256": None,
        "source_audit_bytes": None,
        "product_id": None,
        "report_week": None,
        "selected_gate": None,
        "required_fields": {"present": [], "missing": list(REQUIRED_FIELDS), "ok": False},
        "gate_consistency": {"ok": False},
        "path_safety": {"input_path_safe": False, "referenced_paths_safe": False, "ok": False},
        "mutation_consistency": {"ok": False, "reason": "not_evaluated"},
        "forbidden_content": {"clean": False, "categories": ["output_self_safety_fallback"]},
        "referenced_artifacts": [],
        "warnings": [],
        "failures": ["output_self_safety_fallback"],
        "verdict": "invalid",
        "statement": _statement("invalid"),
    }


def _guarded_out_dir() -> Path:
    out = OUT_DIR.resolve()
    if not str(out).endswith(GUARDED_SUFFIX):
        raise DashboardError(f"refusing to write outside {GUARDED_SUFFIX}: {out}")
    return out


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 7B manual approval audit verifier.")
    parser.add_argument("audit_path", help="relative tmp/ path to one JSON audit artifact")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        result = build_result(args.audit_path)
        result_json = json.dumps(result, indent=2) + "\n"
        result_md = render_md(result)
        try:
            _assert_output_safe(result_json)
            _assert_output_safe(result_md)
        except DashboardError:
            result = _safe_invalid_result(result["generated_at"])
            result_json = json.dumps(result, indent=2) + "\n"
            result_md = render_md(result)
            _assert_output_safe(result_json)
            _assert_output_safe(result_md)
        out_dir = _guarded_out_dir()
        out_dir.mkdir(parents=True, exist_ok=True)
        basename = _out_basename(result)
        json_path = out_dir / f"{basename}.json"
        md_path = out_dir / f"{basename}.md"
        json_path.write_text(result_json, encoding="utf-8")
        md_path.write_text(result_md, encoding="utf-8")
    except DashboardError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    verdict = result["verdict"]
    print(f"audit_verification_json: {GUARDED_SUFFIX}/{basename}.json")
    print(f"audit_verification_md: {GUARDED_SUFFIX}/{basename}.md")
    print(f"verdict: {verdict}")
    if verdict == "invalid":
        print("phase7b_status: invalid")
        return 1
    print("phase7b_status: success")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
