#!/usr/bin/env python3

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "tmp" / "phase7d-single-gate-wrapper"

PRODUCT_ID_RE = re.compile(r"^[a-z0-9-]+$")
WEEK_RE = re.compile(r"^\d{4}-W\d{2}$")
DECISION_ID_RE = re.compile(r"^dec-[a-z0-9-]+-\d{4}-W\d{2}$")

ALLOWED_GATES = ("promote", "decision", "finalization")
VALID_DECISIONS = ("launch", "small_batch_test", "watchlist", "reject")
VALID_COMPLIANCE = ("pending", "approved", "needs_review", "blocked", "not_evaluated")
TRUTHY = {"1", "true", "yes", "y", "on"}
PLACEHOLDERS = {
    "<operator-placeholder>",
    "<reason-placeholder>",
    "<intent-placeholder>",
    "operator-placeholder",
    "reason-placeholder",
    "intent-placeholder",
}

PRIMITIVE_ALLOWLIST = {
    "promote": "promote_product_candidates.py",
    "decision": "create_decision.py",
    "finalization": "finalize_decision.py",
}
APPROVAL_FLAGS = {
    "promote": "APPROVE_PROMOTE",
    "decision": "APPROVE_DECISION",
    "finalization": "APPROVE_FINALIZE",
}
GLOBAL_APPROVAL_ENV = (
    "APPROVE_ALL",
    "GLOBAL_APPROVAL",
    "APPROVE_GLOBAL",
    "ENABLE_GLOBAL_APPROVAL",
)
OUTCOME_EXIT = {
    "success": 0,
    "prevented": 2,
    "blocked": 3,
    "failure": 4,
}
AUDIT_SCHEMA_VERSION = "1"
WRAPPER_VERSION = "phase7d-1"
EXIT_AUDIT_FAILURE = 5


class Phase7DError(Exception):
    def __init__(self, message: str, *, exit_code: int, outcome: str | None = None) -> None:
        super().__init__(message)
        self.exit_code = exit_code
        self.outcome = outcome


class InvalidCliError(Phase7DError):
    def __init__(self, message: str) -> None:
        super().__init__(message, exit_code=1)


class PreventedError(Phase7DError):
    def __init__(self, message: str) -> None:
        super().__init__(message, exit_code=2, outcome="prevented")


class BlockedError(Phase7DError):
    def __init__(self, message: str) -> None:
        super().__init__(message, exit_code=3, outcome="blocked")


class Phase7DArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise InvalidCliError(message)


@dataclass(frozen=True)
class RuntimeContext:
    gate: str
    product_id: str
    report_week: str
    operator: str
    reason: str
    intent: str
    execute: bool
    confirm: str | None


def _now_utc() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _is_truthy(value: str | None) -> bool:
    return value is not None and value.strip().lower() in TRUTHY


def _contains_global_approval(text: str) -> bool:
    low = text.lower()
    return any(token in low for token in ("approve-all", "approve all", "approve_all", "global approval", "global-approve", "global_approve"))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = Phase7DArgumentParser(
        description="Phase 7D runtime single-gate manual approval wrapper."
    )
    parser.add_argument("gate")
    parser.add_argument("product_id")
    parser.add_argument("report_week")
    parser.add_argument("--operator", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--intent", required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirm")
    args, extras = parser.parse_known_args(argv)
    if extras:
        if any(extra in ALLOWED_GATES for extra in extras):
            raise InvalidCliError("multiple gate values are not allowed")
        raise InvalidCliError(f"unexpected extra arguments: {' '.join(extras)}")
    return args


def validate_cli_args(args: argparse.Namespace) -> RuntimeContext:
    gate = str(args.gate)
    product_id = str(args.product_id)
    report_week = str(args.report_week)
    operator = str(args.operator).strip()
    reason = str(args.reason).strip()
    intent = str(args.intent).strip()

    if gate not in ALLOWED_GATES:
        raise InvalidCliError(f"gate must be one of {ALLOWED_GATES}, got {gate!r}")
    if not PRODUCT_ID_RE.fullmatch(product_id):
        raise InvalidCliError(f"product_id must match {PRODUCT_ID_RE.pattern}, got {product_id!r}")
    if not WEEK_RE.fullmatch(report_week):
        raise InvalidCliError(f"report_week must match {WEEK_RE.pattern}, got {report_week!r}")
    if not operator or operator in PLACEHOLDERS:
        raise InvalidCliError("operator is required and must not be a placeholder")
    if not reason or reason in PLACEHOLDERS:
        raise InvalidCliError("reason is required and must not be a placeholder")
    if not intent or intent in PLACEHOLDERS:
        raise InvalidCliError("intent is required and must not be a placeholder")

    return RuntimeContext(
        gate=gate,
        product_id=product_id,
        report_week=report_week,
        operator=operator,
        reason=reason,
        intent=intent,
        execute=bool(args.execute),
        confirm=args.confirm,
    )


def validate_operator_intent(context: RuntimeContext) -> None:
    if _contains_global_approval(context.reason) or _contains_global_approval(context.intent):
        raise PreventedError("approve-all or global approval wording is not allowed")


def discover_evidence_paths(product_id: str, report_week: str) -> dict[str, str]:
    return {
        "packet_path": f"tmp/phase6b-approval-review/review-{product_id}-{report_week}.json",
        "verifier_path": f"tmp/phase6c-approval-review-verifier/verification-review-{product_id}-{report_week}.json",
        "execution_plan_path": f"tmp/phase6e-approval-execution-plan/execution-plan-{product_id}-{report_week}.json",
    }


def validate_path_safety(path_str: str, *, expected_prefix: str | None = None) -> None:
    if any(path_str.startswith(prefix) for prefix in ("http://", "https://", "file://")):
        raise PreventedError("external URL schemes are not allowed")
    if path_str.startswith("/"):
        raise PreventedError("absolute paths are not allowed")
    if ".." in path_str.split("/"):
        raise PreventedError("path traversal is not allowed")
    if "vault/" in path_str:
        raise PreventedError("vault paths are not allowed in evidence references")
    if not path_str.startswith("tmp/"):
        raise PreventedError("evidence paths must remain under tmp/")
    if expected_prefix and not path_str.startswith(expected_prefix):
        raise PreventedError(f"path must start with {expected_prefix}")


def safe_output_dir() -> Path:
    out = OUT_DIR.resolve()
    expected = str((REPO_ROOT / "tmp" / "phase7d-single-gate-wrapper").resolve())
    if str(out) != expected:
        raise PreventedError("refusing to write outside tmp/phase7d-single-gate-wrapper")
    out.mkdir(parents=True, exist_ok=True)
    return out


def load_json_file(path_str: str) -> dict[str, Any]:
    validate_path_safety(path_str)
    full_path = REPO_ROOT / path_str
    if not full_path.is_file():
        raise BlockedError(f"missing evidence: {path_str}")
    try:
        payload = json.loads(full_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BlockedError(f"invalid JSON in {path_str}") from exc
    if not isinstance(payload, dict):
        raise BlockedError(f"JSON root must be an object: {path_str}")
    return payload


def _read_frontmatter(note_path: Path) -> dict[str, Any]:
    text = note_path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL)
    if not match:
        raise BlockedError(f"malformed frontmatter in {note_path.name}")
    payload = yaml.safe_load(match.group(1)) or {}
    if not isinstance(payload, dict):
        raise BlockedError(f"frontmatter must be a mapping in {note_path.name}")
    return payload


def _derive_phase2e_root(packet: dict[str, Any], product_id: str) -> str:
    sources = packet.get("sources")
    if not isinstance(sources, list):
        raise BlockedError("Phase 6B sources list missing")
    target = None
    for entry in sources:
        if isinstance(entry, dict) and entry.get("name") == "phase2e_score":
            target = entry.get("path")
            break
    if not isinstance(target, str):
        raise BlockedError("Phase 6B phase2e_score source path missing")
    validate_path_safety(target, expected_prefix="tmp/phase2e-import-score-report/")
    score_path = Path(target)
    if score_path.name != f"{product_id}.json":
        raise BlockedError("Phase 2E score path does not match product_id")
    if score_path.parent.name != "scores":
        raise BlockedError("Phase 2E score path must be under scores/")
    return score_path.parent.parent.as_posix()


def _build_product_note_path(product_id: str) -> Path:
    return REPO_ROOT / "vault" / "products" / f"{product_id}.md"


def _build_decision_note_path(product_id: str, report_week: str) -> Path:
    decision_id = f"dec-{product_id}-{report_week}"
    if not DECISION_ID_RE.fullmatch(decision_id):
        raise InvalidCliError("derived decision_id is invalid")
    return REPO_ROOT / "vault" / "decisions" / f"{decision_id}.md"


def validate_evidence(context: RuntimeContext, packet: dict[str, Any], verifier: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    if packet.get("dry_run") is not True:
        raise BlockedError("Phase 6B dry_run must be true")
    if verifier.get("verdict") != "ready":
        raise BlockedError("Phase 6C verdict must be ready")
    if plan.get("dry_run") is not True:
        raise BlockedError("Phase 6E dry_run must be true")
    if plan.get("verdict") == "failed":
        raise BlockedError("Phase 6E verdict failed blocks execution")

    for payload_name, payload in (("Phase 6B", packet), ("Phase 6C", verifier), ("Phase 6E", plan)):
        pid = payload.get("product_id")
        week = payload.get("report_week")
        if pid is not None and pid != context.product_id:
            raise BlockedError(f"{payload_name} product_id mismatch")
        if week is not None and week != context.report_week:
            raise BlockedError(f"{payload_name} report_week mismatch")

    derived = {
        "phase2e_root": _derive_phase2e_root(packet, context.product_id),
        "decision_value": None,
        "compliance_status": None,
        "decision_id": f"dec-{context.product_id}-{context.report_week}",
    }

    score = packet.get("score")
    if not isinstance(score, dict):
        raise BlockedError("Phase 6B score section missing")
    decision_value = score.get("score_decision")
    if context.gate == "decision":
        if not isinstance(decision_value, str) or decision_value not in VALID_DECISIONS:
            raise PreventedError("score.score_decision must be present and valid for decision gate")
        derived["decision_value"] = decision_value

    compliance_status = packet.get("compliance_status")
    if compliance_status is not None:
        if not isinstance(compliance_status, str) or compliance_status not in VALID_COMPLIANCE:
            raise PreventedError("compliance_status in evidence is invalid or ambiguous")
        derived["compliance_status"] = compliance_status

    return derived


def validate_selected_gate(context: RuntimeContext, packet: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    per_gate_plan = plan.get("per_gate_plan")
    if not isinstance(per_gate_plan, dict):
        raise BlockedError("Phase 6E per_gate_plan missing")
    gate_plan = per_gate_plan.get(context.gate)
    if not isinstance(gate_plan, dict):
        raise BlockedError("selected gate missing from per_gate_plan")
    if gate_plan.get("plan_ready") is not True:
        raise BlockedError("selected gate plan_ready must be true")
    if gate_plan.get("blocked_reason") not in (None, ""):
        raise BlockedError("selected gate blocked_reason must be empty")

    packet_gates = packet.get("gates") if isinstance(packet.get("gates"), dict) else {}
    if context.gate == "decision":
        if packet_gates.get("promote_gate_ready") is not True or packet_gates.get("decision_gate_ready") is not True:
            raise BlockedError("decision gate requires promote completion evidence")
        product_note = _build_product_note_path(context.product_id)
        if not product_note.is_file():
            raise BlockedError("promoted product note missing for decision gate")
        fm = _read_frontmatter(product_note)
        if fm.get("type") != "product_candidate" or fm.get("status") != "scored":
            raise BlockedError("promoted product note state is not valid for decision gate")
    elif context.gate == "finalization":
        if packet_gates.get("decision_gate_ready") is not True:
            raise BlockedError("finalization requires decision completion evidence")
        decision_note = _build_decision_note_path(context.product_id, context.report_week)
        if not decision_note.is_file():
            raise BlockedError("decision draft missing for finalization gate")
        fm = _read_frontmatter(decision_note)
        if fm.get("type") != "decision" or fm.get("status") != "draft":
            raise BlockedError("decision draft state is not valid for finalization gate")
        if fm.get("decision_id") != f"dec-{context.product_id}-{context.report_week}":
            raise BlockedError("decision draft id mismatch")
        if fm.get("compliance_status") != "approved":
            raise BlockedError("finalization compliance_status must be approved")

    return gate_plan


def validate_approval_flags(context: RuntimeContext) -> str:
    if not context.execute:
        raise PreventedError("execute flag absent; dry-run/prevented mode only")
    expected_confirmation = f"EXECUTE_PHASE7D:{context.gate}:{context.product_id}:{context.report_week}"
    if not context.confirm or context.confirm != expected_confirmation:
        raise PreventedError("confirmation is missing or does not match the required string")

    for env_name in GLOBAL_APPROVAL_ENV:
        if _is_truthy(os.getenv(env_name)):
            raise PreventedError("global approval env is not allowed")

    truthy_flags = [name for name in APPROVAL_FLAGS.values() if _is_truthy(os.getenv(name))]
    expected_flag = APPROVAL_FLAGS[context.gate]
    if truthy_flags.count(expected_flag) != 1:
        raise PreventedError("matching gate-specific approval flag is required")
    if any(flag != expected_flag for flag in truthy_flags):
        raise PreventedError("unrelated truthy approval flags are not allowed")
    return expected_flag


def validate_emergency_stop() -> None:
    if _is_truthy(os.getenv("AFFILIATE_PHASE7D_EMERGENCY_STOP")):
        raise PreventedError("AFFILIATE_PHASE7D_EMERGENCY_STOP is active")
    stop_file = safe_output_dir() / "EMERGENCY_STOP"
    if stop_file.is_file():
        raise PreventedError("EMERGENCY_STOP file is active")


def build_audit_record(
    *,
    context: RuntimeContext,
    paths: dict[str, str],
    primitive_name: str,
    approved_flag_name: str,
    outcome: str,
    mutation_attempted: bool,
    precondition_summary: str,
    result_summary: str,
) -> dict[str, Any]:
    return {
        "product_id": context.product_id,
        "report_week": context.report_week,
        "selected_gate": context.gate,
        "primitive_name": primitive_name,
        "operator": context.operator,
        "approval_reason": context.reason,
        "timestamp": _now_utc(),
        "source_packet_path": paths["packet_path"],
        "verifier_path": paths["verifier_path"],
        "execution_plan_path": paths["execution_plan_path"],
        "precondition_summary": precondition_summary,
        "result_summary": result_summary,
        "outcome": outcome,
        "mutation_attempted": mutation_attempted,
        "gate_specific_approval_intent": context.intent,
        "approved_flag_name": approved_flag_name,
        "wrapper_version": WRAPPER_VERSION,
        "audit_schema_version": AUDIT_SCHEMA_VERSION,
    }


def write_audit_record(record: dict[str, Any], *, stage: str) -> str:
    out_dir = safe_output_dir()
    path = out_dir / f"audit-{stage}-{record['product_id']}-{record['report_week']}-{record['selected_gate']}.json"
    payload = json.dumps(record, indent=2) + "\n"
    path.write_text(payload, encoding="utf-8")
    return str(path.relative_to(REPO_ROOT))


def invoke_selected_primitive(
    *,
    gate: str,
    primitive_name: str,
    primitive_args: list[str],
    env: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(REPO_ROOT / "scripts" / "dev" / primitive_name), *primitive_args]
    return subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, env=env)


def _primitive_args(context: RuntimeContext, derived: dict[str, Any]) -> list[str]:
    if context.gate == "promote":
        return ["--source-dir", derived["phase2e_root"], "--report-week", context.report_week, "--approve"]
    if context.gate == "decision":
        args = [
            "--product-id",
            context.product_id,
            "--decision",
            str(derived["decision_value"]),
            "--report-week",
            context.report_week,
        ]
        if derived["compliance_status"] is not None:
            args.extend(["--compliance-status", str(derived["compliance_status"])])
        args.append("--approve")
        return args
    return [
        "--decision-id",
        str(derived["decision_id"]),
        "--finalization-reason",
        context.reason,
        "--approve",
    ]


def _primitive_env() -> dict[str, str]:
    env = os.environ.copy()
    env.pop("AFFILIATE_REQUIRE_OPERATOR_RUNTIME", None)
    for name in (*APPROVAL_FLAGS.values(), *GLOBAL_APPROVAL_ENV):
        env.pop(name, None)
    env.pop("AFFILIATE_PHASE7D_EMERGENCY_STOP", None)
    return env


def run_phase7d(context: RuntimeContext) -> int:
    primitive_name = PRIMITIVE_ALLOWLIST[context.gate]
    default_flag_name = APPROVAL_FLAGS[context.gate]
    paths = discover_evidence_paths(context.product_id, context.report_week)

    try:
        for key, prefix in (
            ("packet_path", "tmp/phase6b-approval-review/"),
            ("verifier_path", "tmp/phase6c-approval-review-verifier/"),
            ("execution_plan_path", "tmp/phase6e-approval-execution-plan/"),
        ):
            validate_path_safety(paths[key], expected_prefix=prefix)

        validate_operator_intent(context)
        packet = load_json_file(paths["packet_path"])
        verifier = load_json_file(paths["verifier_path"])
        plan = load_json_file(paths["execution_plan_path"])
        derived = validate_evidence(context, packet, verifier, plan)
        validate_selected_gate(context, packet, plan)
        approved_flag_name = validate_approval_flags(context)
        validate_emergency_stop()
    except Phase7DError as exc:
        if exc.outcome is not None:
            audit = build_audit_record(
                context=context,
                paths=paths,
                primitive_name=primitive_name,
                approved_flag_name=default_flag_name,
                outcome=exc.outcome,
                mutation_attempted=False,
                precondition_summary="preconditions_failed",
                result_summary=str(exc),
            )
            try:
                audit_path = write_audit_record(audit, stage="result")
                print(f"audit_path: {audit_path}")
            except OSError:
                return EXIT_AUDIT_FAILURE
        else:
            print(str(exc), file=sys.stderr)
        return exc.exit_code

    intent_audit = build_audit_record(
        context=context,
        paths=paths,
        primitive_name=primitive_name,
        approved_flag_name=approved_flag_name,
        outcome="success",
        mutation_attempted=False,
        precondition_summary="preconditions_ok",
        result_summary="intent_recorded",
    )
    try:
        write_audit_record(intent_audit, stage="intent")
    except OSError:
        return EXIT_AUDIT_FAILURE

    primitive_args = _primitive_args(context, derived)
    result = invoke_selected_primitive(
        gate=context.gate,
        primitive_name=primitive_name,
        primitive_args=primitive_args,
        env=_primitive_env(),
    )

    if result.returncode == 0:
        outcome = "success"
        exit_code = OUTCOME_EXIT[outcome]
        result_summary = "primitive_completed"
    else:
        outcome = "failure"
        exit_code = OUTCOME_EXIT[outcome]
        result_summary = "manual review required after primitive failure"

    result_audit = build_audit_record(
        context=context,
        paths=paths,
        primitive_name=primitive_name,
        approved_flag_name=approved_flag_name,
        outcome=outcome,
        mutation_attempted=True,
        precondition_summary="preconditions_ok",
        result_summary=result_summary,
    )
    try:
        audit_path = write_audit_record(result_audit, stage="result")
    except OSError:
        return EXIT_AUDIT_FAILURE

    print(f"audit_path: {audit_path}")
    return exit_code


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        context = validate_cli_args(args)
        return run_phase7d(context)
    except Phase7DError as exc:
        print(str(exc), file=sys.stderr)
        return exc.exit_code
    except Exception as exc:  # pragma: no cover - defensive final boundary
        print(f"unexpected internal error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
