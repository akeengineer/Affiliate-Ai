#!/usr/bin/env python3
"""Build the Phase 7G operator acceptance summary from safe scenario records."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "tmp" / "phase7g-operator-acceptance"
JSON_OUT = OUT_DIR / "operator-acceptance-summary.json"
MARKDOWN_OUT = OUT_DIR / "operator-acceptance-summary.md"

OPERATOR_CHECKLIST = [
    "Confirm the selected gate, product_id, and report_week.",
    "Confirm the Phase 6B packet, Phase 6C verification, and Phase 6E plan.",
    "Confirm the selected gate is plan_ready and the emergency stop is inactive.",
    "Confirm operator identity, reason, intent, and the exact confirmation string.",
    "Confirm only the matching approval flag is truthy.",
    "Confirm no global approval, approve-all, chain, or next-gate request exists.",
    "Use a non-production sample first.",
]

MANUAL_REVIEW_CHECKLIST = [
    "Inspect the result audit, intent audit, and wrapper exit code.",
    "Confirm whether a primitive was invoked or partial completion occurred.",
    "Do not rerun, run the next gate, or roll back automatically.",
    "Require operator review before retry.",
]

SAFETY_STATEMENT = (
    "Phase 7G exercises only prevented, blocked, invalid, or static-inspection "
    "paths. It supplies no runtime execution intent, invokes no approval "
    "primitive, and performs no business-memory write."
)


class SummaryError(RuntimeError):
    """Raised when safe scenario records are missing or invalid."""


def _load_scenarios() -> list[dict[str, Any]]:
    scenarios: list[dict[str, Any]] = []
    for path in sorted(OUT_DIR.glob("scenario-*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise SummaryError(f"scenario record must be an object: {path.name}")
        required = {
            "scenario_id",
            "expected_result",
            "observed_exit_code",
            "passed",
            "primitive_success",
            "audit_artifacts",
        }
        if not required.issubset(payload):
            raise SummaryError(f"scenario record is incomplete: {path.name}")
        if not isinstance(payload["observed_exit_code"], int):
            raise SummaryError(f"scenario exit code must be an integer: {path.name}")
        if payload["passed"] is not True:
            raise SummaryError(f"safe scenario did not meet expectations: {path.name}")
        if payload["primitive_success"] is True:
            raise SummaryError(f"primitive success is forbidden: {path.name}")
        scenarios.append(payload)
    if not scenarios:
        raise SummaryError("no safe scenario records found")
    return scenarios


def _build_summary(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    audits = sorted(
        {
            artifact
            for scenario in scenarios
            for artifact in scenario.get("audit_artifacts", [])
            if isinstance(artifact, str) and artifact
        }
    )
    return {
        "phase7g_status": "success",
        "phase7d_runtime_readiness": "implemented_manual_gate",
        "scenarios_executed": scenarios,
        "audit_artifacts_found": audits,
        "safety_statement": SAFETY_STATEMENT,
        "operator_checklist": OPERATOR_CHECKLIST,
        "manual_review_checklist": MANUAL_REVIEW_CHECKLIST,
        "next_recommended_phase": (
            "Phase 7H manual operator runbook hardening or "
            "Phase 8A durable audit store design."
        ),
    }


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Phase 7G Operator Acceptance Summary",
        "",
        "phase7g_status: success",
        "phase7d_runtime_readiness: implemented_manual_gate",
        "",
        "## Scenarios executed",
        "",
        "| Scenario | Expected result | Observed exit code | Passed |",
        "| --- | --- | ---: | --- |",
    ]
    for scenario in summary["scenarios_executed"]:
        lines.append(
            f"| {scenario['scenario_id']} | {scenario['expected_result']} | "
            f"{scenario['observed_exit_code']} | yes |"
        )
    lines.extend(
        [
            "",
            "## Audit artifacts found",
            "",
        ]
    )
    if summary["audit_artifacts_found"]:
        lines.extend(f"- `{path}`" for path in summary["audit_artifacts_found"])
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Safety statement",
            "",
            summary["safety_statement"],
            "",
            "## Operator checklist",
            "",
            *(f"- {item}" for item in summary["operator_checklist"]),
            "",
            "## Manual review checklist",
            "",
            *(f"- {item}" for item in summary["manual_review_checklist"]),
            "",
            "## Next recommended phase",
            "",
            summary["next_recommended_phase"],
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    scenarios = _load_scenarios()
    summary = _build_summary(scenarios)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    MARKDOWN_OUT.write_text(_markdown(summary), encoding="utf-8")
    print("phase7g_status: success")
    print(f"summary_json: {JSON_OUT.relative_to(REPO_ROOT)}")
    print(f"summary_markdown: {MARKDOWN_OUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
