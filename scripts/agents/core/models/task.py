"""Task model for 9ake-kiro-agents orchestration."""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class TaskType(str, Enum):
    """Types of tasks that can be dispatched."""

    REASONING = "reasoning"
    DESIGN = "design"
    REVIEW = "review"
    IMPLEMENTATION = "implementation"
    TEST = "test"
    REFACTOR = "refactor"


class TaskStatus(str, Enum):
    """Status of a task in the orchestration pipeline."""

    QUEUED = "queued"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class TaskPriority(str, Enum):
    """Priority levels for task dispatch ordering."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Task:
    """A task to be dispatched to a CLI agent."""

    id: str
    title: str
    type: TaskType
    status: TaskStatus
    prompt: str
    priority: TaskPriority = TaskPriority.MEDIUM
    agent_preference: str = "auto"
    dependencies: List[str] = field(default_factory=list)
    input_files: List[str] = field(default_factory=list)
    expected_outputs: List[str] = field(default_factory=list)
    timeout_seconds: int = 300
    max_retries: int = 2
    created_at: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Set defaults after initialization."""
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        # Ensure enums are correct type
        if isinstance(self.type, str):
            self.type = TaskType(self.type)
        if isinstance(self.status, str):
            self.status = TaskStatus(self.status)
        if isinstance(self.priority, str):
            self.priority = TaskPriority(self.priority)

    @classmethod
    def create(
        cls,
        title: str,
        task_type: str,
        prompt: str,
        priority: str = "medium",
        agent_preference: str = "auto",
        dependencies: Optional[List[str]] = None,
        input_files: Optional[List[str]] = None,
        expected_outputs: Optional[List[str]] = None,
        timeout_seconds: int = 300,
        max_retries: int = 2,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "Task":
        """Create a new task with a generated UUID and timestamp.

        Args:
            title: Human-readable task title.
            task_type: Type of task (must be a valid TaskType value).
            prompt: The prompt/instruction for the agent.
            priority: Task priority level.
            agent_preference: Preferred agent ('claude', 'codex', 'auto').
            dependencies: Task IDs that must complete first.
            input_files: Files the agent should read.
            expected_outputs: Expected output files/artifacts.
            timeout_seconds: Max execution time.
            max_retries: Max retry attempts.
            metadata: Additional metadata.

        Returns:
            A new Task instance with generated ID and timestamp.
        """
        return cls(
            id=str(uuid.uuid4()),
            title=title,
            type=TaskType(task_type),
            status=TaskStatus.QUEUED,
            prompt=prompt,
            priority=TaskPriority(priority),
            agent_preference=agent_preference,
            dependencies=dependencies or [],
            input_files=input_files or [],
            expected_outputs=expected_outputs or [],
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            metadata=metadata or {},
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize task to a dictionary suitable for JSON."""
        data = asdict(self)
        # Convert enums to their string values
        data["type"] = self.type.value
        data["status"] = self.status.value
        data["priority"] = self.priority.value
        return data

    def to_json(self, indent: int = 2) -> str:
        """Serialize task to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Deserialize task from a dictionary.

        Args:
            data: Dictionary with task fields.

        Returns:
            Task instance.
        """
        return cls(
            id=data["id"],
            title=data["title"],
            type=TaskType(data["type"]),
            status=TaskStatus(data["status"]),
            prompt=data["prompt"],
            priority=TaskPriority(data.get("priority", "medium")),
            agent_preference=data.get("agent_preference", "auto"),
            dependencies=data.get("dependencies", []),
            input_files=data.get("input_files", []),
            expected_outputs=data.get("expected_outputs", []),
            timeout_seconds=data.get("timeout_seconds", 300),
            max_retries=data.get("max_retries", 2),
            created_at=data.get("created_at", ""),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "Task":
        """Deserialize task from a JSON string."""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def load(cls, path: Path) -> "Task":
        """Load task from a JSON file.

        Args:
            path: Path to the task JSON file.

        Returns:
            Task instance.

        Raises:
            FileNotFoundError: If file doesn't exist.
            json.JSONDecodeError: If file isn't valid JSON.
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def save(self, directory: Path) -> Path:
        """Save task to a JSON file in the specified directory.

        Args:
            directory: Directory to save the task file in.

        Returns:
            Path to the saved file.
        """
        directory.mkdir(parents=True, exist_ok=True)
        file_path = directory / f"{self.id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.to_json())
            f.write("\n")
        return file_path

    def mark_active(self) -> None:
        """Mark task as actively running."""
        self.status = TaskStatus.ACTIVE
        self.started_at = datetime.now(timezone.utc).isoformat()

    def mark_completed(self) -> None:
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc).isoformat()

    def mark_failed(self) -> None:
        """Mark task as failed."""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now(timezone.utc).isoformat()

    def mark_retrying(self) -> None:
        """Mark task as retrying."""
        self.status = TaskStatus.RETRYING

    @property
    def is_ready(self) -> bool:
        """Check if task is ready to dispatch (queued, no unmet dependencies)."""
        return self.status == TaskStatus.QUEUED

    @property
    def is_terminal(self) -> bool:
        """Check if task is in a terminal state (completed or failed)."""
        return self.status in (TaskStatus.COMPLETED, TaskStatus.FAILED)
