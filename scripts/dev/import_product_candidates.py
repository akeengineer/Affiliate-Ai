#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "tmp/phase2d-import/products"
SAFE_OUTPUT_ROOT = REPO_ROOT / "tmp/phase2d-import"
SAFE_INPUT_ROOTS = (
    REPO_ROOT / "vault/samples/import",
    REPO_ROOT / "tmp/phase2d-import/input",
)
REQUIRED_COLUMNS = (
    "product_id",
    "product_name",
    "marketplace",
    "currency",
    "demand_score",
    "trend_velocity_score",
    "marketplace_rank_score",
    "commission_score",
    "content_fit_score",
    "competition_gap_score",
    "risk_score",
)
OPTIONAL_COLUMNS = (
    "brand",
    "niche",
    "product_url",
    "trend_signal_note",
    "marketplace_signal_note",
    "commission_signal_note",
    "compliance_result_note",
)
SCORE_COLUMNS = (
    "demand_score",
    "trend_velocity_score",
    "marketplace_rank_score",
    "commission_score",
    "content_fit_score",
    "competition_gap_score",
    "risk_score",
)
NOTE_REF_COLUMNS = (
    "trend_signal_note",
    "marketplace_signal_note",
    "commission_signal_note",
    "compliance_result_note",
)
PRODUCT_ID_PATTERN = re.compile(r"^[a-z0-9-]+$")


@dataclass(frozen=True)
class ImportedCandidate:
    output_path: Path
    frontmatter: dict[str, Any]


def _is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


def _resolve_safe_path(path: Path) -> Path:
    return path.expanduser().resolve(strict=False)


def _require_safe_input_path(input_path: Path) -> Path:
    resolved = _resolve_safe_path(input_path)
    if not any(_is_relative_to(resolved, root.resolve()) for root in SAFE_INPUT_ROOTS):
        raise ValueError(f"Unsafe input_csv path: {input_path}")
    return resolved


def _require_safe_output_path(output_dir: Path) -> Path:
    resolved = _resolve_safe_path(output_dir)
    if not _is_relative_to(resolved, SAFE_OUTPUT_ROOT.resolve()):
        raise ValueError(f"Unsafe output_dir path: {output_dir}")
    return resolved


def _clean_cell(row: dict[str, str | None], column: str) -> str:
    return str(row.get(column, "") or "").strip()


def _validate_headers(fieldnames: list[str] | None) -> list[str]:
    if not fieldnames:
        raise ValueError("CSV header row is missing")

    cleaned = [field.strip() for field in fieldnames]
    missing = [column for column in REQUIRED_COLUMNS if column not in cleaned]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    allowed = set(REQUIRED_COLUMNS) | set(OPTIONAL_COLUMNS)
    unknown = [column for column in cleaned if column not in allowed]
    if unknown:
        raise ValueError(f"Unknown columns: {', '.join(unknown)}")

    return cleaned


def _parse_score(row_number: int, column: str, raw_value: str) -> int | float:
    try:
        value = float(raw_value)
    except ValueError as exc:
        raise ValueError(f"Row {row_number}: {column} must be numeric") from exc

    if not 0 <= value <= 100:
        raise ValueError(f"Row {row_number}: {column} must be within 0-100")

    if value.is_integer():
        return int(value)
    return round(value, 2)


def _validate_note_ref(row_number: int, column: str, value: str) -> str:
    if value.startswith("/") or ".." in Path(value).parts:
        raise ValueError(f"Row {row_number}: {column} must be repo-relative")
    return value


def _note_body(product_name: str) -> str:
    return (
        f"# {product_name}\n\n"
        "## Summary\n"
        "- Imported from sanitized CSV.\n"
    )


def _build_candidate(row_number: int, row: dict[str, str | None], output_dir: Path) -> ImportedCandidate:
    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    product_id = _clean_cell(row, "product_id")
    if not product_id:
        raise ValueError(f"Row {row_number}: product_id is required")
    if not PRODUCT_ID_PATTERN.fullmatch(product_id):
        raise ValueError(
            f"Row {row_number}: product_id must use lowercase letters, digits, and hyphens only"
        )

    frontmatter: dict[str, Any] = {
        "type": "product_candidate",
        "product_id": product_id,
    }

    for column in ("product_name", "marketplace", "currency"):
        value = _clean_cell(row, column)
        if not value:
            raise ValueError(f"Row {row_number}: {column} is required")
        frontmatter[column] = value

    for column in SCORE_COLUMNS:
        raw_value = _clean_cell(row, column)
        if not raw_value:
            raise ValueError(f"Row {row_number}: {column} is required")
        frontmatter[column] = _parse_score(row_number, column, raw_value)

    for column in OPTIONAL_COLUMNS:
        value = _clean_cell(row, column)
        if not value:
            continue
        if column in NOTE_REF_COLUMNS:
            value = _validate_note_ref(row_number, column, value)
        frontmatter[column] = value

    frontmatter["status"] = "draft"
    frontmatter["created_at"] = timestamp
    frontmatter["updated_at"] = timestamp

    return ImportedCandidate(output_path=output_dir / f"{product_id}.md", frontmatter=frontmatter)


def load_candidates(input_csv: Path, output_dir: Path) -> list[ImportedCandidate]:
    resolved_input = _require_safe_input_path(input_csv)
    if not resolved_input.is_file():
        raise ValueError(f"Missing input_csv: {input_csv}")

    resolved_output = _require_safe_output_path(output_dir)

    with resolved_input.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        _validate_headers(reader.fieldnames)

        candidates: list[ImportedCandidate] = []
        seen_ids: set[str] = set()
        seen_paths: set[Path] = set()

        for row_number, row in enumerate(reader, start=2):
            candidate = _build_candidate(row_number, row, resolved_output)
            product_id = str(candidate.frontmatter["product_id"])
            if product_id in seen_ids:
                raise ValueError(f"Duplicate product_id: {product_id}")
            if candidate.output_path in seen_paths:
                raise ValueError(f"Duplicate output path: {candidate.output_path}")
            if candidate.output_path.exists():
                raise ValueError(f"Output note already exists: {candidate.output_path}")
            seen_ids.add(product_id)
            seen_paths.add(candidate.output_path)
            candidates.append(candidate)

    if not candidates:
        raise ValueError("CSV must contain at least one product row")

    return candidates


def write_candidates(candidates: list[ImportedCandidate]) -> None:
    for candidate in candidates:
        candidate.output_path.parent.mkdir(parents=True, exist_ok=True)
        note_text = "\n".join(
            [
                "---",
                yaml.safe_dump(candidate.frontmatter, sort_keys=False).strip(),
                "---",
                "",
                _note_body(str(candidate.frontmatter["product_name"])).rstrip(),
                "",
            ]
        )
        candidate.output_path.write_text(note_text, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Import sanitized CSV product candidates into Markdown notes.")
    parser.add_argument("--input-csv", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        candidates = load_candidates(args.input_csv, args.output_dir)
        if args.dry_run:
            print("phase2d_import: dry_run")
            print(f"input_csv: {args.input_csv}")
            print(f"output_dir: {args.output_dir}")
            print(f"validated_rows: {len(candidates)}")
            print("planned_files:")
            for candidate in candidates:
                print(f"- {candidate.output_path}")
            return 0

        write_candidates(candidates)
    except Exception as exc:
        # ponytail: keep CLI failures single-line and script-friendly.
        print(str(exc), file=sys.stderr)
        return 1

    print("phase2d_import: success")
    print(f"input_csv: {args.input_csv}")
    print(f"output_dir: {args.output_dir}")
    print(f"imported_rows: {len(candidates)}")
    print("written_files:")
    for candidate in candidates:
        print(f"- {candidate.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
