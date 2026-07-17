#!/usr/bin/env python3
"""Compare deterministic product scores under multiple weight configurations.

Experiment YAML accepts a ``configurations`` mapping. Each configuration maps
the seven scoring weights directly or under a ``weights`` key. Weights may sum
to 1.0 or 100. The ``risk_score`` alias means risk-penalty-inverse weight.

Ref: codex/tasks/104-phase7-enhancement.md
"""
from __future__ import annotations

import argparse
import math
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.dev.score_product import read_frontmatter, score_product_note  # noqa: E402


DEFAULT_VAULT_DIR = REPO_ROOT / "vault"
WEIGHT_FIELDS = (
    "demand_score",
    "trend_velocity_score",
    "marketplace_rank_score",
    "commission_score",
    "content_fit_score",
    "competition_gap_score",
    "risk_penalty_inverse",
)


class ExperimentError(ValueError):
    """Raised for invalid experiment configuration or scoring input."""


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_weights(name: str, raw: Mapping[str, Any]) -> dict[str, float]:
    values = dict(raw)
    if "risk_score" in values and "risk_penalty_inverse" not in values:
        values["risk_penalty_inverse"] = values.pop("risk_score")
    missing = [field for field in WEIGHT_FIELDS if field not in values]
    unknown = sorted(set(values) - set(WEIGHT_FIELDS))
    if missing or unknown:
        details = []
        if missing:
            details.append(f"missing: {', '.join(missing)}")
        if unknown:
            details.append(f"unknown: {', '.join(unknown)}")
        raise ExperimentError(f"Configuration {name!r} has invalid weights ({'; '.join(details)})")

    weights: dict[str, float] = {}
    for field in WEIGHT_FIELDS:
        value = values[field]
        if isinstance(value, bool):
            raise ExperimentError(f"Configuration {name!r} weight {field} must be numeric")
        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise ExperimentError(
                f"Configuration {name!r} weight {field} must be numeric"
            ) from exc
        if number < 0:
            raise ExperimentError(f"Configuration {name!r} weight {field} must be non-negative")
        weights[field] = number

    total = sum(weights.values())
    if math.isclose(total, 100.0, abs_tol=1e-6):
        weights = {field: value / 100.0 for field, value in weights.items()}
        total = 1.0
    if not math.isclose(total, 1.0, abs_tol=1e-6):
        raise ExperimentError(f"Configuration {name!r} weights must sum to 1.0 or 100")
    return weights


def load_experiment(path: Path) -> tuple[str, dict[str, dict[str, float]]]:
    if not path.is_file():
        raise ExperimentError(f"Experiment file not found: {path}")
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ExperimentError(f"Invalid experiment YAML: {path}") from exc
    if not isinstance(payload, dict):
        raise ExperimentError("Experiment YAML must contain a mapping")

    experiment_name = str(payload.get("name") or path.stem)
    raw_configurations = payload.get("configurations")
    if raw_configurations is None:
        raw_configurations = payload.get("variants")
    if raw_configurations is None:
        raw_configurations = payload.get("experiments")
    if isinstance(raw_configurations, list):
        raw_configurations = {
            str(item.get("name", "")): item.get("weights")
            for item in raw_configurations
            if isinstance(item, dict)
        }
    if not isinstance(raw_configurations, dict) or len(raw_configurations) < 2:
        raise ExperimentError("Experiment requires at least two configurations")

    configurations: dict[str, dict[str, float]] = {}
    for raw_name, raw_configuration in raw_configurations.items():
        name = str(raw_name).strip()
        if not name:
            raise ExperimentError("Configuration names must be non-empty")
        if not isinstance(raw_configuration, dict):
            raise ExperimentError(f"Configuration {name!r} must be a mapping")
        raw_weights = raw_configuration.get("weights", raw_configuration)
        if not isinstance(raw_weights, dict):
            raise ExperimentError(f"Configuration {name!r} weights must be a mapping")
        configurations[name] = _normalize_weights(name, raw_weights)
    return experiment_name, configurations


def _decision_for_score(score: float) -> str:
    if score >= 85:
        return "launch"
    if score >= 75:
        return "small_batch_test"
    if score >= 65:
        return "watchlist"
    return "reject"


def score_with_weights(note_path: Path, weights: Mapping[str, float]) -> dict[str, Any]:
    base = score_product_note(note_path)
    components = base["component_scores"]
    weighted_score = round(
        weights["demand_score"] * components["demand_score"]
        + weights["trend_velocity_score"] * components["trend_velocity_score"]
        + weights["marketplace_rank_score"] * components["marketplace_rank_score"]
        + weights["commission_score"] * components["commission_score"]
        + weights["content_fit_score"] * components["content_fit_score"]
        + weights["competition_gap_score"] * components["competition_gap_score"]
        + weights["risk_penalty_inverse"] * (100 - components["risk_score"]),
        2,
    )
    return {
        **base,
        "product_opportunity_score": weighted_score,
        "score_decision": _decision_for_score(weighted_score),
    }


def find_product_notes(vault_dir: Path) -> list[Path]:
    if not vault_dir.is_dir():
        raise ExperimentError(f"Vault directory not found: {vault_dir}")
    notes: list[Path] = []
    for path in sorted(vault_dir.rglob("*.md")):
        try:
            frontmatter, _body = read_frontmatter(path)
        except (OSError, ValueError, yaml.YAMLError):
            continue
        if frontmatter.get("type") == "product_candidate":
            notes.append(path)
    if not notes:
        raise ExperimentError("No product_candidate notes found in vault")
    return notes


def run_experiment(
    vault_dir: Path, configurations: Mapping[str, Mapping[str, float]]
) -> dict[str, list[dict[str, Any]]]:
    product_notes = find_product_notes(vault_dir)
    return {
        name: [score_with_weights(note_path, weights) for note_path in product_notes]
        for name, weights in configurations.items()
    }


def _md_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_report(
    experiment_name: str,
    configurations: Mapping[str, Mapping[str, float]],
    results: Mapping[str, list[dict[str, Any]]],
    generated_at: str | None = None,
) -> str:
    names = list(configurations)
    by_product: dict[str, dict[str, dict[str, Any]]] = {}
    for name in names:
        for row in results[name]:
            by_product.setdefault(row["product_id"], {})[name] = row

    lines = [
        f"# Scoring Weight Experiment — {_md_cell(experiment_name)}",
        "",
        f"Generated: {generated_at or utc_now()}",
        "",
        "## Weight Configurations",
        "",
        "| Configuration | " + " | ".join(WEIGHT_FIELDS) + " |",
        "| --- | " + " | ".join("---:" for _ in WEIGHT_FIELDS) + " |",
    ]
    for name in names:
        lines.append(
            f"| {_md_cell(name)} | "
            + " | ".join(f"{configurations[name][field]:.3f}" for field in WEIGHT_FIELDS)
            + " |"
        )

    headers = ["Product ID", "Product"]
    for name in names:
        headers.extend([f"{name} Score", f"{name} Decision"])
    lines.extend(
        [
            "",
            "## Side-by-Side Results",
            "",
            "| " + " | ".join(_md_cell(header) for header in headers) + " |",
            "| " + " | ".join("---" if index < 2 else "---:" if index % 2 == 0 else "---" for index in range(len(headers))) + " |",
        ]
    )
    for product_id in sorted(by_product):
        first = next(iter(by_product[product_id].values()))
        cells: list[Any] = [product_id, first["product_name"]]
        for name in names:
            row = by_product[product_id][name]
            cells.extend([f'{row["product_opportunity_score"]:.2f}', row["score_decision"]])
        lines.append("| " + " | ".join(_md_cell(cell) for cell in cells) + " |")

    lines.extend(["", "## Configuration Summary", ""])
    for name in names:
        rows = results[name]
        average = sum(float(row["product_opportunity_score"]) for row in rows) / len(rows)
        counts = {
            decision: sum(row["score_decision"] == decision for row in rows)
            for decision in ("launch", "small_batch_test", "watchlist", "reject")
        }
        lines.append(
            f"- **{_md_cell(name)}**: average {average:.2f}; "
            f"launch {counts['launch']}, small_batch_test {counts['small_batch_test']}, "
            f"watchlist {counts['watchlist']}, reject {counts['reject']}"
        )
    lines.extend(["", "This report changes no product notes or active scoring configuration.", ""])
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare scoring weight configurations.")
    parser.add_argument("--experiment-file", required=True, type=Path)
    parser.add_argument("--vault-dir", type=Path, default=DEFAULT_VAULT_DIR)
    parser.add_argument("--output", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        name, configurations = load_experiment(args.experiment_file)
        results = run_experiment(args.vault_dir, configurations)
        report = render_report(name, configurations, results)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    except (ExperimentError, OSError, ValueError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"experiment_report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
