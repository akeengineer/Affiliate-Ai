#!/usr/bin/env python3
"""Learn bounded emphasis changes from recorded prediction outcomes.

This module uses transparent heuristics rather than ML. Runtime state is kept
in an Obsidian ``nightly_config`` note and every cycle writes an auditable
``learning_log`` note. The tracked YAML contains limits, never learned state.

Ref: codex/tasks/008-agent-brainstorming.md
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

try:
    from .agent_runner import (
        DEFAULT_VAULT_ROOT,
        VaultNote,
        cli_main_error,
        discover_notes,
        existing_created_at,
        note_reference,
        read_note,
        safe_slug,
        sanitize_data,
        sanitize_text,
        utc_now,
        write_note,
    )
except ImportError:  # pragma: no cover
    from agent_runner import (  # type: ignore
        DEFAULT_VAULT_ROOT,
        VaultNote,
        cli_main_error,
        discover_notes,
        existing_created_at,
        note_reference,
        read_note,
        safe_slug,
        sanitize_data,
        sanitize_text,
        utc_now,
        write_note,
    )


DEFAULT_CONFIG_PATH = Path(__file__).with_name("config") / "learning.yaml"
NIGHTLY_CONFIG_RELATIVE_PATH = Path("config") / "next-nightly-config.md"
WEIGHT_SOURCE_FIELDS = {
    "demand_score": "demand_score",
    "trend_velocity_score": "trend_velocity_score",
    "marketplace_rank_score": "marketplace_rank_score",
    "commission_score": "commission_score",
    "content_fit_score": "content_fit_score",
    "competition_gap_score": "competition_gap_score",
    "risk_penalty_inverse": "risk_score",
}
ACTUAL_SCORE_FIELDS = ("actual_performance_score", "outcome_score", "actual_score")
OUTCOME_SCORE_MAP = {
    "success": 100.0,
    "launch": 100.0,
    "small_batch_test": 75.0,
    "watchlist": 50.0,
    "reject": 0.0,
    "failure": 0.0,
}


@dataclass(frozen=True)
class PerformanceRecord:
    product_id: str
    prediction: float
    actual: float
    components: dict[str, float]
    niche: str
    keywords: tuple[str, ...]
    source_path: Path

    @property
    def error(self) -> float:
        return self.actual - self.prediction


def _finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be numeric")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be numeric") from exc
    if not math.isfinite(number):
        raise ValueError(f"{field} must be finite")
    return number


def load_learning_config(path: Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    """Load and validate hard bounds for learning and niche activation."""

    with Path(path).open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}
    if not isinstance(config, dict):
        raise ValueError("learning.yaml must contain a mapping")
    weights = config.get("weight_bounds")
    niches = config.get("niche_limits")
    keywords = config.get("keyword_limits")
    if not isinstance(weights, Mapping) or not isinstance(niches, Mapping):
        raise ValueError("learning.yaml must define weight_bounds and niche_limits")
    if not isinstance(keywords, Mapping):
        raise ValueError("learning.yaml must define keyword_limits")

    max_change = _finite_number(
        weights.get("max_change_percent_per_cycle"),
        "weight_bounds.max_change_percent_per_cycle",
    )
    if not 0 < max_change <= 10:
        raise ValueError("Weight change limit must be greater than 0 and no more than 10 percent")
    minimum = _finite_number(weights.get("minimum_emphasis"), "minimum_emphasis")
    maximum = _finite_number(weights.get("maximum_emphasis"), "maximum_emphasis")
    fields = weights.get("fields")
    if (
        minimum < 0.90
        or maximum > 1.10
        or maximum < minimum
        or not isinstance(fields, Mapping)
        or set(fields) != set(WEIGHT_SOURCE_FIELDS)
    ):
        raise ValueError("Invalid weight emphasis bounds")
    adjustment_step = _finite_number(
        weights.get("adjustment_step_percent"), "adjustment_step_percent"
    )
    if not 0 < adjustment_step <= max_change:
        raise ValueError("Weight adjustment step must fit the per-cycle limit")
    for field, value in fields.items():
        emphasis = _finite_number(value, f"weight field {field}")
        if not minimum <= emphasis <= maximum:
            raise ValueError(f"Initial emphasis for {field} is outside configured bounds")

    active = niches.get("active_niches")
    allowed = niches.get("allowed_niches")
    max_active = int(niches.get("max_active_niches", 0))
    if (
        not isinstance(active, list)
        or not isinstance(allowed, list)
        or not all(isinstance(niche, str) and niche for niche in [*active, *allowed])
        or len(active) != len(set(active))
        or len(allowed) != len(set(allowed))
        or max_active < 1
    ):
        raise ValueError("Invalid niche limits")
    if len(active) > max_active or not set(active).issubset(set(allowed)):
        raise ValueError("Active niches must be allowed and within max_active_niches")
    niche_cycle_limit = _finite_number(
        niches.get("max_priority_change_percent_per_cycle"),
        "max_priority_change_percent_per_cycle",
    )
    if not 0 < niche_cycle_limit <= 10:
        raise ValueError("Niche priority change limit must be no more than 10 percent")
    minimum_priority = _finite_number(niches.get("minimum_priority"), "minimum_priority")
    maximum_priority = _finite_number(niches.get("maximum_priority"), "maximum_priority")
    if minimum_priority <= 0 or maximum_priority < minimum_priority:
        raise ValueError("Invalid niche priority bounds")
    max_additions = int(keywords.get("max_additions_per_cycle", 0))
    max_per_niche = int(keywords.get("max_keywords_per_niche", 0))
    if max_additions < 0 or max_per_niche < 1 or max_additions > max_per_niche:
        raise ValueError("Invalid keyword limits")
    outcomes = config.get("outcomes", {})
    if not isinstance(outcomes, Mapping):
        raise ValueError("learning.yaml outcomes must be a mapping")
    success_score = _finite_number(outcomes.get("success_score", 70), "outcomes.success_score")
    if not 0 <= success_score <= 100:
        raise ValueError("outcomes.success_score must be within 0-100")
    return config


def adjust_weights(
    current_weights: Mapping[str, float],
    requested_changes_percent: Mapping[str, float],
    config: Mapping[str, Any],
) -> dict[str, float]:
    """Apply per-cycle relative changes, clamped to global and ±10% bounds."""

    bounds = config.get("weight_bounds", config)
    if not isinstance(bounds, Mapping):
        raise ValueError("Weight bounds must be a mapping")
    max_cycle = min(
        10.0,
        _finite_number(bounds.get("max_change_percent_per_cycle"), "max weight change"),
    )
    minimum = _finite_number(bounds.get("minimum_emphasis"), "minimum emphasis")
    maximum = _finite_number(bounds.get("maximum_emphasis"), "maximum emphasis")
    adjusted: dict[str, float] = {}
    for field, raw_current in current_weights.items():
        current = _finite_number(raw_current, f"current weight {field}")
        if not minimum <= current <= maximum:
            raise ValueError(f"Current emphasis for {field} is outside configured bounds")
        requested = _finite_number(requested_changes_percent.get(field, 0), f"change {field}")
        bounded_request = max(-max_cycle, min(max_cycle, requested))
        cycle_min = current * (1 - max_cycle / 100)
        cycle_max = current * (1 + max_cycle / 100)
        candidate = current * (1 + bounded_request / 100)
        adjusted[field] = round(
            max(minimum, cycle_min, min(maximum, cycle_max, candidate)),
            6,
        )
    return adjusted


def _string_list(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        values = [part.strip() for part in value.split(",")]
    elif isinstance(value, Sequence):
        values = [sanitize_text(item) for item in value]
    else:
        values = []
    return tuple(value for value in values if value)


def _actual_score(frontmatter: Mapping[str, Any]) -> float | None:
    for field in ACTUAL_SCORE_FIELDS:
        if frontmatter.get(field) not in (None, ""):
            value = _finite_number(frontmatter[field], field)
            if not 0 <= value <= 100:
                raise ValueError(f"{field} must be within 0-100")
            return value
    outcome = str(frontmatter.get("actual_outcome", "")).strip().lower()
    return OUTCOME_SCORE_MAP.get(outcome)


def collect_performance_records(vault_root: Path) -> list[PerformanceRecord]:
    """Read product candidates that contain both a prediction and an outcome."""

    records: list[PerformanceRecord] = []
    candidates: dict[str, VaultNote] = {}
    for note in discover_notes(Path(vault_root), "product_candidate"):
        product_id = str(note.frontmatter.get("product_id", note.path.stem))
        current = candidates.get(product_id)
        if current is None or (
            "samples" in current.path.parts and "samples" not in note.path.parts
        ):
            candidates[product_id] = note
    for note in candidates.values():
        frontmatter = note.frontmatter
        if frontmatter.get("product_opportunity_score") in (None, ""):
            continue
        actual = _actual_score(frontmatter)
        if actual is None:
            continue
        prediction = _finite_number(
            frontmatter["product_opportunity_score"], "product_opportunity_score"
        )
        if not 0 <= prediction <= 100:
            raise ValueError("product_opportunity_score must be within 0-100")
        components: dict[str, float] = {}
        for emphasis_field, source_field in WEIGHT_SOURCE_FIELDS.items():
            if frontmatter.get(source_field) in (None, ""):
                continue
            score = _finite_number(frontmatter[source_field], source_field)
            if not 0 <= score <= 100:
                raise ValueError(f"{source_field} must be within 0-100")
            components[emphasis_field] = 100 - score if source_field == "risk_score" else score
        records.append(
            PerformanceRecord(
                product_id=str(frontmatter.get("product_id", note.path.stem)),
                prediction=prediction,
                actual=actual,
                components=components,
                niche=sanitize_text(frontmatter.get("niche", "")).lower(),
                keywords=_string_list(
                    frontmatter.get("search_keywords", frontmatter.get("keywords", []))
                ),
                source_path=note.path,
            )
        )
    return records


def _default_nightly_frontmatter(config: Mapping[str, Any], timestamp: str) -> dict[str, Any]:
    niches = config["niche_limits"]
    return {
        "type": "nightly_config",
        "config_id": "next-nightly",
        "active_niches": list(niches["active_niches"]),
        "search_keywords": {niche: [] for niche in niches["active_niches"]},
        "scoring_weight_emphasis": dict(config["weight_bounds"]["fields"]),
        "niche_priorities": {niche: 1.0 for niche in niches["active_niches"]},
        "approved_proposal_ids": [],
        "approved_ideas": [],
        "created_at": timestamp,
        "updated_at": timestamp,
        "status": "active",
    }


def validate_nightly_state(state: Mapping[str, Any], config: Mapping[str, Any]) -> None:
    """Reject out-of-bounds or unapproved runtime state before mutation."""

    limits = config["niche_limits"]
    active = state.get("active_niches")
    if (
        not isinstance(active, list)
        or not all(isinstance(niche, str) and niche for niche in active)
        or len(active) != len(set(active))
    ):
        raise ValueError("nightly_config active_niches must be a unique list")
    allowed = set(limits["allowed_niches"])
    if len(active) > int(limits["max_active_niches"]) or not set(active).issubset(allowed):
        raise ValueError("nightly_config active_niches exceed configured niche limits")

    approved_ideas = state.get("approved_ideas", [])
    if not isinstance(approved_ideas, list):
        raise ValueError("nightly_config approved_ideas must be a list")
    approved_scope = {
        str(item.get("target_niche", ""))
        for item in approved_ideas
        if isinstance(item, Mapping)
        and item.get("idea_type") in {"new_niche", "new_category"}
    }
    initial = set(limits["active_niches"])
    unapproved = set(active) - initial - approved_scope
    if unapproved:
        raise ValueError(
            "nightly_config contains niche(s) without approved proposals: "
            f"{', '.join(sorted(unapproved))}"
        )

    weights = state.get("scoring_weight_emphasis")
    configured_fields = config["weight_bounds"]["fields"]
    if not isinstance(weights, Mapping) or set(weights) != set(configured_fields):
        raise ValueError("nightly_config scoring_weight_emphasis fields are invalid")
    minimum_weight = float(config["weight_bounds"]["minimum_emphasis"])
    maximum_weight = float(config["weight_bounds"]["maximum_emphasis"])
    for field, value in weights.items():
        number = _finite_number(value, f"scoring_weight_emphasis.{field}")
        if not minimum_weight <= number <= maximum_weight:
            raise ValueError(f"nightly_config emphasis for {field} is outside bounds")

    priorities = state.get("niche_priorities")
    if not isinstance(priorities, Mapping) or not set(active).issubset(priorities):
        raise ValueError("nightly_config niche_priorities must cover active niches")
    minimum_priority = float(limits["minimum_priority"])
    maximum_priority = float(limits["maximum_priority"])
    for niche in active:
        priority = _finite_number(priorities[niche], f"niche priority {niche}")
        if not minimum_priority <= priority <= maximum_priority:
            raise ValueError(f"nightly_config priority for {niche} is outside bounds")

    keywords = state.get("search_keywords")
    if not isinstance(keywords, Mapping) or not set(active).issubset(keywords):
        raise ValueError("nightly_config search_keywords must cover active niches")
    maximum_keywords = int(config["keyword_limits"]["max_keywords_per_niche"])
    for niche in active:
        values = keywords[niche]
        if (
            not isinstance(values, Sequence)
            or isinstance(values, (str, bytes))
            or len(values) > maximum_keywords
        ):
            raise ValueError(f"nightly_config keywords for {niche} exceed configured limits")


def load_nightly_config(
    vault_root: Path,
    config: Mapping[str, Any],
    *,
    timestamp: str | None = None,
) -> tuple[Path, dict[str, Any]]:
    """Load runtime learning state or construct its initial bounded state."""

    path = Path(vault_root) / NIGHTLY_CONFIG_RELATIVE_PATH
    now = timestamp or utc_now()
    if not path.exists():
        state = _default_nightly_frontmatter(config, now)
        validate_nightly_state(state, config)
        return path, state
    note = read_note(path)
    if note.frontmatter.get("type") != "nightly_config":
        raise ValueError(f"Expected nightly_config note: {path}")
    state = dict(note.frontmatter)
    state["created_at"] = existing_created_at(path, now)
    validate_nightly_state(state, config)
    return path, state


def write_nightly_config(
    vault_root: Path,
    path: Path,
    state: Mapping[str, Any],
    *,
    reason: str,
    config: Mapping[str, Any] | None = None,
) -> Path:
    if config is not None:
        validate_nightly_state(state, config)
    body = "\n".join(
        (
            "# Next Nightly Configuration",
            "",
            "This runtime configuration is bounded by `scripts/agents/config/learning.yaml`.",
            "It does not authorize publishing or unapproved niche expansion.",
            "",
            "## Last Update",
            "",
            sanitize_text(reason),
        )
    )
    return write_note(Path(vault_root), path, sanitize_data(dict(state)), body)


def _requested_weight_changes(
    records: Sequence[PerformanceRecord], fields: Sequence[str], step: float
) -> dict[str, float]:
    changes: dict[str, float] = {}
    for field in fields:
        correction_signals = [
            (record.components[field] - record.prediction) * record.error
            for record in records
            if field in record.components and record.error != 0
        ]
        aggregate = sum(correction_signals)
        changes[field] = step if aggregate > 0 else -step if aggregate < 0 else 0.0
    return changes


def _adjust_niche_priorities(
    current: Mapping[str, Any],
    records: Sequence[PerformanceRecord],
    config: Mapping[str, Any],
) -> dict[str, float]:
    limits = config["niche_limits"]
    max_cycle = min(10.0, float(limits["max_priority_change_percent_per_cycle"]))
    step = min(max_cycle, float(config["weight_bounds"]["adjustment_step_percent"]))
    minimum = float(limits["minimum_priority"])
    maximum = float(limits["maximum_priority"])
    error_by_niche: dict[str, list[float]] = defaultdict(list)
    for record in records:
        if record.niche in current:
            error_by_niche[record.niche].append(record.error)

    updated: dict[str, float] = {}
    for niche, value in current.items():
        priority = _finite_number(value, f"niche priority {niche}")
        aggregate = sum(error_by_niche.get(niche, []))
        requested = step if aggregate > 0 else -step if aggregate < 0 else 0.0
        candidate = priority * (1 + requested / 100)
        cycle_min = priority * (1 - max_cycle / 100)
        cycle_max = priority * (1 + max_cycle / 100)
        updated[niche] = round(
            max(minimum, cycle_min, min(maximum, cycle_max, candidate)), 6
        )
    return updated


def _keyword_additions(
    records: Sequence[PerformanceRecord],
    state: Mapping[str, Any],
    config: Mapping[str, Any],
) -> dict[str, list[str]]:
    limits = config["keyword_limits"]
    remaining_cycle = int(limits["max_additions_per_cycle"])
    max_per_niche = int(limits["max_keywords_per_niche"])
    success_score = float(config.get("outcomes", {}).get("success_score", 70))
    active = set(state.get("active_niches", []))
    existing_raw = state.get("search_keywords", {})
    existing = existing_raw if isinstance(existing_raw, Mapping) else {}
    candidates: list[tuple[float, str, str]] = []
    for record in records:
        if record.actual < success_score or record.niche not in active:
            continue
        for keyword in record.keywords:
            candidates.append((record.actual, record.niche, keyword))
    additions: dict[str, list[str]] = defaultdict(list)
    for _score, niche, keyword in sorted(candidates, key=lambda item: (-item[0], item[1], item[2])):
        known = list(existing.get(niche, [])) + additions[niche]
        if remaining_cycle <= 0 or len(known) >= max_per_niche:
            continue
        if keyword not in known:
            additions[niche].append(keyword)
            remaining_cycle -= 1
    return dict(additions)


def learn_from_results(
    vault_root: Path = DEFAULT_VAULT_ROOT,
    *,
    config_path: Path = DEFAULT_CONFIG_PATH,
) -> Path:
    """Apply one bounded learning cycle and return its ``learning_log`` path."""

    root = Path(vault_root)
    config = load_learning_config(config_path)
    records = collect_performance_records(root)
    timestamp = utc_now()
    nightly_path, state = load_nightly_config(root, config, timestamp=timestamp)

    fields = list(config["weight_bounds"]["fields"])
    current_weights = {
        field: float(state.get("scoring_weight_emphasis", {}).get(field, initial))
        for field, initial in config["weight_bounds"]["fields"].items()
    }
    requested = _requested_weight_changes(
        records,
        fields,
        float(config["weight_bounds"]["adjustment_step_percent"]),
    )
    updated_weights = adjust_weights(current_weights, requested, config)

    current_priorities = state.get("niche_priorities", {})
    if not isinstance(current_priorities, Mapping):
        current_priorities = {}
    for niche in state.get("active_niches", []):
        current_priorities = {**current_priorities, niche: current_priorities.get(niche, 1.0)}
    updated_priorities = _adjust_niche_priorities(current_priorities, records, config)
    additions = _keyword_additions(records, state, config)
    search_keywords = {
        str(niche): list(values)
        for niche, values in (state.get("search_keywords", {}) or {}).items()
    }
    for niche in state.get("active_niches", []):
        search_keywords.setdefault(niche, [])
    for niche, values in additions.items():
        search_keywords[niche].extend(values)

    weight_changes = {
        field: round(updated_weights[field] - current_weights[field], 6)
        for field in fields
        if updated_weights[field] != current_weights[field]
    }
    priority_changes = {
        niche: round(updated_priorities[niche] - float(current_priorities[niche]), 6)
        for niche in updated_priorities
        if updated_priorities[niche] != float(current_priorities[niche])
    }
    changes_applied = (
        len(weight_changes) + len(priority_changes) + sum(map(len, additions.values()))
    )

    state.update(
        {
            "scoring_weight_emphasis": updated_weights,
            "niche_priorities": updated_priorities,
            "search_keywords": search_keywords,
            "updated_at": timestamp,
            "status": "active",
        }
    )
    write_nightly_config(
        root,
        nightly_path,
        state,
        reason=f"Learning cycle compared {len(records)} prediction/outcome record(s).",
        config=config,
    )

    instant = datetime.now(UTC)
    learning_id = f"learning-{instant.strftime('%Y%m%dT%H%M%S%fZ')}"
    log_path = root / "learning" / f"{safe_slug(learning_id)}.md"
    frontmatter = {
        "type": "learning_log",
        "learning_id": learning_id,
        "source_record_count": len(records),
        "source_product_ids": sorted(record.product_id for record in records),
        "previous_weight_emphasis": current_weights,
        "updated_weight_emphasis": updated_weights,
        "weight_changes": weight_changes,
        "niche_priority_changes": priority_changes,
        "keyword_additions": additions,
        "changes_applied": changes_applied,
        "nightly_config_note": note_reference(root, nightly_path),
        "created_at": existing_created_at(log_path, timestamp),
        "updated_at": timestamp,
        "status": "complete",
    }
    change_lines = [
        f"- Weight `{field}`: {current_weights[field]} → {updated_weights[field]}"
        for field in weight_changes
    ]
    change_lines.extend(
        f"- Niche `{niche}` priority: {current_priorities[niche]} → {updated_priorities[niche]}"
        for niche in priority_changes
    )
    change_lines.extend(
        f"- Added keyword `{keyword}` to active niche `{niche}`"
        for niche, values in additions.items()
        for keyword in values
    )
    if not change_lines:
        change_lines = ["- No bounded changes were indicated by recorded outcomes."]
    source_lines = [
        f"- `{record.product_id}`: predicted {record.prediction}, actual {record.actual}, "
        f"error {record.error:+.2f}"
        for record in records
    ] or ["- No product candidates contained both prediction and outcome fields."]
    body = "\n".join(
        (
            "# Learning Log",
            "",
            "## Prediction vs Outcome",
            "",
            *source_lines,
            "",
            "## Bounded Changes",
            "",
            *change_lines,
            "",
            "## Guardrails",
            "",
            "- Weight and niche-priority changes were capped at ±10% for this cycle.",
            "- Learning did not activate any new niche; only explicit user approval may do so.",
            "- The fixed scoring formula remains unchanged.",
        )
    )
    return write_note(root, log_path, frontmatter, body)


run = learn_from_results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one bounded learning cycle.")
    parser.add_argument("--vault-root", type=Path, default=DEFAULT_VAULT_ROOT)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        path = learn_from_results(args.vault_root, config_path=args.config)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(cli_main_error(exc), file=sys.stderr)
        return 1
    print(json.dumps({"status": "success", "output": str(path)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
