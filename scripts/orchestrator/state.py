#!/usr/bin/env python3
"""Atomic JSON checkpoint storage for the nightly orchestrator.

State is deliberately local and file based.  It contains one current record
per pipeline stage plus a small checkpoint history so an interrupted run can
resume at the first stage that did not complete successfully.

Ref: codex/tasks/006-orchestrator-scheduler.md
"""
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4


CHECKPOINT_STATUSES = {"running", "retrying", "success", "failed", "timed_out"}


class StateError(RuntimeError):
    """Raised when persisted orchestrator state is missing or malformed."""


def utc_now() -> str:
    """Return an ISO-8601 UTC timestamp without fractional seconds."""

    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_run_id(timestamp: str | None = None) -> str:
    """Create a readable run identifier with a collision-resistant suffix."""

    stamp = (timestamp or utc_now()).replace("-", "").replace(":", "")
    stamp = stamp.removesuffix("Z")
    return f"nightly-{stamp}-{uuid4().hex[:8]}"


def new_state(*, run_id: str | None = None, timestamp: str | None = None) -> dict[str, Any]:
    """Return an empty, schema-versioned run state document."""

    now = timestamp or utc_now()
    return {
        "version": 1,
        "run_id": run_id or new_run_id(now),
        "run_status": "running",
        "started_at": now,
        "updated_at": now,
        "finished_at": None,
        "stage_name": None,
        "status": None,
        "timestamp": now,
        "error": None,
        "stages": [],
        "history": [],
    }


def _validate_state(data: Any, path: Path | None = None) -> dict[str, Any]:
    label = str(path) if path is not None else "state"
    if not isinstance(data, dict):
        raise StateError(f"{label}: state JSON must contain an object")
    if not isinstance(data.get("run_id"), str) or not data["run_id"].strip():
        raise StateError(f"{label}: state is missing run_id")
    if not isinstance(data.get("stages"), list):
        raise StateError(f"{label}: state stages must be a list")
    if not isinstance(data.get("history", []), list):
        raise StateError(f"{label}: state history must be a list")
    return data


def load_state(path: Path) -> dict[str, Any]:
    """Load and minimally validate a checkpoint file."""

    state_path = Path(path)
    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise
    except (OSError, json.JSONDecodeError) as exc:
        raise StateError(f"Unable to read orchestrator state: {state_path}") from exc
    return _validate_state(data, state_path)


def save_state(path: Path, state: dict[str, Any]) -> Path:
    """Atomically persist a state document."""

    state_path = Path(path)
    _validate_state(state, state_path)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = state_path.with_name(f".{state_path.name}.tmp")
    temporary.write_text(
        json.dumps(state, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(state_path)
    return state_path


def _checkpoint_record(
    stage_name: str,
    status: str,
    timestamp: str,
    error: str | None,
    attempts: int,
) -> dict[str, Any]:
    return {
        "stage_name": stage_name,
        "status": status,
        "timestamp": timestamp,
        "error": error,
        "attempts": attempts,
    }


def write_checkpoint(
    path: Path,
    stage_name: str,
    status: str,
    *,
    error: str | None = None,
    attempts: int = 1,
    timestamp: str | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Create or update a stage checkpoint and return the persisted state."""

    if not isinstance(stage_name, str) or not stage_name.strip():
        raise ValueError("stage_name must be a non-empty string")
    if status not in CHECKPOINT_STATUSES:
        expected = ", ".join(sorted(CHECKPOINT_STATUSES))
        raise ValueError(f"Unknown checkpoint status {status!r}; expected one of: {expected}")
    if isinstance(attempts, bool) or not isinstance(attempts, int) or attempts < 1:
        raise ValueError("attempts must be a positive integer")

    state_path = Path(path)
    now = timestamp or utc_now()
    state = load_state(state_path) if state_path.exists() else new_state(run_id=run_id, timestamp=now)
    record = _checkpoint_record(stage_name.strip(), status, now, error, attempts)

    stages = state["stages"]
    for index, existing in enumerate(stages):
        if isinstance(existing, dict) and existing.get("stage_name") == record["stage_name"]:
            stages[index] = record
            break
    else:
        stages.append(record)

    state.setdefault("history", []).append(dict(record))
    state.update(
        {
            "stage_name": record["stage_name"],
            "status": record["status"],
            "timestamp": now,
            "error": error,
            "updated_at": now,
        }
    )
    save_state(state_path, state)
    return state


def next_stage_index(state: dict[str, Any], stage_order: Iterable[str]) -> int:
    """Return the first stage index without a successful checkpoint."""

    records = {
        record.get("stage_name"): record
        for record in state.get("stages", [])
        if isinstance(record, dict)
    }
    order = list(stage_order)
    for index, stage_name in enumerate(order):
        if records.get(stage_name, {}).get("status") != "success":
            return index
    return len(order)


class StateStore:
    """Small state-management facade used by the orchestrator and tests."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.state: dict[str, Any] | None = None

    def start(self, *, resume: bool = False, timestamp: str | None = None) -> dict[str, Any]:
        if resume and self.path.exists():
            self.state = load_state(self.path)
            self.state["run_status"] = "running"
            self.state["finished_at"] = None
            self.state["updated_at"] = timestamp or utc_now()
        else:
            self.state = new_state(timestamp=timestamp)
        save_state(self.path, self.state)
        return self.state

    def checkpoint(
        self,
        stage_name: str,
        status: str,
        *,
        error: str | None = None,
        attempts: int = 1,
        timestamp: str | None = None,
    ) -> dict[str, Any]:
        if self.state is None:
            raise StateError("StateStore.start() must be called before checkpoint()")
        self.state = write_checkpoint(
            self.path,
            stage_name,
            status,
            error=error,
            attempts=attempts,
            timestamp=timestamp,
            run_id=self.state["run_id"],
        )
        return self.state

    def next_stage_index(self, stage_order: Iterable[str]) -> int:
        if self.state is None:
            raise StateError("StateStore.start() must be called before next_stage_index()")
        return next_stage_index(self.state, stage_order)

    def finish(self, run_status: str, *, timestamp: str | None = None) -> dict[str, Any]:
        if self.state is None:
            raise StateError("StateStore.start() must be called before finish()")
        now = timestamp or utc_now()
        self.state["run_status"] = run_status
        self.state["finished_at"] = now
        self.state["updated_at"] = now
        save_state(self.path, self.state)
        return self.state
