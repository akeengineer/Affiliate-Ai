"""Result model for 9ake-kiro-agents orchestration."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class ResultStatus(str, Enum):
    """Status of an agent execution result."""

    SUCCESS = "success"
    FAIL = "fail"
    PARTIAL = "partial"
    TIMEOUT = "timeout"


@dataclass
class AgentResult:
    """The result returned by a CLI agent after executing a task."""

    task_id: str
    agent: str
    status: ResultStatus
    summary: str
    completed_at: str
    files_modified: List[str] = field(default_factory=list)
    files_created: List[str] = field(default_factory=list)
    tests_run: Optional[str] = None
    tests_passed: Optional[bool] = None
    errors: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    attempt: int = 1
    is_fallback: bool = False
    raw_output: Optional[str] = None
    next_steps: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Ensure enums are correct type."""
        if isinstance(self.status, str):
            self.status = ResultStatus(self.status)

    @classmethod
    def create(
        cls,
        task_id: str,
        agent: str,
        status: str,
        summary: str,
        duration_seconds: float = 0.0,
        files_modified: Optional[List[str]] = None,
        files_created: Optional[List[str]] = None,
        tests_run: Optional[str] = None,
        tests_passed: Optional[bool] = None,
        errors: Optional[List[str]] = None,
        attempt: int = 1,
        is_fallback: bool = False,
        raw_output: Optional[str] = None,
        next_steps: Optional[List[str]] = None,
    ) -> "AgentResult":
        """Create a new result with the current timestamp.

        Args:
            task_id: UUID of the task this result belongs to.
            agent: Name of the agent that executed ('claude' or 'codex').
            status: Execution status ('success', 'fail', 'partial', 'timeout').
            summary: Human-readable summary.
            duration_seconds: Execution time.
            files_modified: List of modified files.
            files_created: List of created files.
            tests_run: Test command run.
            tests_passed: Whether tests passed.
            errors: Error messages.
            attempt: Which attempt this is (1-based).
            is_fallback: Whether a fallback agent handled this.
            raw_output: Raw CLI stdout.
            next_steps: Recommended follow-up actions.

        Returns:
            A new AgentResult instance.
        """
        return cls(
            task_id=task_id,
            agent=agent,
            status=ResultStatus(status),
            summary=summary,
            completed_at=datetime.now(timezone.utc).isoformat(),
            files_modified=files_modified or [],
            files_created=files_created or [],
            tests_run=tests_run,
            tests_passed=tests_passed,
            errors=errors or [],
            duration_seconds=duration_seconds,
            attempt=attempt,
            is_fallback=is_fallback,
            raw_output=raw_output,
            next_steps=next_steps or [],
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize result to a dictionary suitable for JSON."""
        data = asdict(self)
        data["status"] = self.status.value
        return data

    def to_json(self, indent: int = 2) -> str:
        """Serialize result to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentResult":
        """Deserialize result from a dictionary.

        Args:
            data: Dictionary with result fields.

        Returns:
            AgentResult instance.
        """
        return cls(
            task_id=data["task_id"],
            agent=data["agent"],
            status=ResultStatus(data["status"]),
            summary=data["summary"],
            completed_at=data["completed_at"],
            files_modified=data.get("files_modified", []),
            files_created=data.get("files_created", []),
            tests_run=data.get("tests_run"),
            tests_passed=data.get("tests_passed"),
            errors=data.get("errors", []),
            duration_seconds=data.get("duration_seconds", 0.0),
            attempt=data.get("attempt", 1),
            is_fallback=data.get("is_fallback", False),
            raw_output=data.get("raw_output"),
            next_steps=data.get("next_steps", []),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "AgentResult":
        """Deserialize result from a JSON string."""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def load(cls, path: Path) -> "AgentResult":
        """Load result from a JSON file.

        Args:
            path: Path to the result JSON file.

        Returns:
            AgentResult instance.

        Raises:
            FileNotFoundError: If file doesn't exist.
            json.JSONDecodeError: If file isn't valid JSON.
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def save(self, directory: Path) -> Path:
        """Save result to a JSON file in the specified directory.

        Args:
            directory: Directory to save the result file in.

        Returns:
            Path to the saved file.
        """
        directory.mkdir(parents=True, exist_ok=True)
        file_path = directory / f"{self.task_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.to_json())
            f.write("\n")
        return file_path

    @property
    def is_success(self) -> bool:
        """Check if result indicates success."""
        return self.status == ResultStatus.SUCCESS

    @property
    def is_failure(self) -> bool:
        """Check if result indicates failure (fail or timeout)."""
        return self.status in (ResultStatus.FAIL, ResultStatus.TIMEOUT)

    @property
    def is_retriable(self) -> bool:
        """Check if this result suggests the task could be retried."""
        return self.status in (ResultStatus.FAIL, ResultStatus.TIMEOUT, ResultStatus.PARTIAL)
