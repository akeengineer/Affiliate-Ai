"""Concurrency Manager for 9ake-kiro-agents.

Tracks running agent processes so Kiro can:
- Check if agents are currently busy
- Ask user about queue vs parallel when agents are active
- Know which tasks are in-flight
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class RunningProcess:
    """Record of an active agent process."""

    task_id: str
    terminal_id: str
    agent_name: str
    task_title: str
    started_at: str = ""
    status: str = "running"  # running, completed, failed

    def __post_init__(self) -> None:
        if not self.started_at:
            self.started_at = datetime.now(timezone.utc).isoformat()


@dataclass
class ConcurrencyState:
    """Full concurrency state tracking all processes."""

    processes: Dict[str, RunningProcess] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"processes": {k: asdict(v) for k, v in self.processes.items()}}

    @classmethod
    def from_dict(cls, data: dict) -> "ConcurrencyState":
        processes = {}
        for task_id, proc_data in data.get("processes", {}).items():
            processes[task_id] = RunningProcess(**proc_data)
        return cls(processes=processes)


class AgentProcessManager:
    """Manages concurrent agent process tracking.

    Persists state to .agents/state/active_processes.json so it survives
    across Kiro sessions.
    """

    def __init__(self, state_dir: Optional[Path] = None) -> None:
        """Initialize the process manager.

        Args:
            state_dir: Directory for state persistence.
                Defaults to .agents/state/ in CWD.
        """
        self._state_dir = state_dir or (Path.cwd() / ".agents" / "state")
        self._state_file = self._state_dir / "active_processes.json"
        self._state = self._load_state()

    def _load_state(self) -> ConcurrencyState:
        """Load state from disk."""
        if self._state_file.exists():
            try:
                data = json.loads(self._state_file.read_text(encoding="utf-8"))
                return ConcurrencyState.from_dict(data)
            except (json.JSONDecodeError, KeyError, TypeError):
                return ConcurrencyState()
        return ConcurrencyState()

    def _save_state(self) -> None:
        """Save state to disk."""
        self._state_dir.mkdir(parents=True, exist_ok=True)
        with open(self._state_file, "w", encoding="utf-8") as f:
            json.dump(self._state.to_dict(), f, indent=2, ensure_ascii=False)
            f.write("\n")

    def register_process(
        self,
        task_id: str,
        terminal_id: str,
        agent_name: str,
        task_title: str = "",
    ) -> None:
        """Register a new running agent process.

        Args:
            task_id: UUID of the task.
            terminal_id: Kiro terminal/process ID from control_pwsh_process.
            agent_name: Agent name ('claude' or 'codex').
            task_title: Human-readable task title.
        """
        self._state.processes[task_id] = RunningProcess(
            task_id=task_id,
            terminal_id=terminal_id,
            agent_name=agent_name,
            task_title=task_title or task_id,
        )
        self._save_state()

    def mark_complete(self, task_id: str) -> None:
        """Mark a process as completed and remove from active tracking.

        Args:
            task_id: UUID of the task.
        """
        if task_id in self._state.processes:
            self._state.processes[task_id].status = "completed"
            del self._state.processes[task_id]
            self._save_state()

    def mark_failed(self, task_id: str) -> None:
        """Mark a process as failed and remove from active tracking.

        Args:
            task_id: UUID of the task.
        """
        if task_id in self._state.processes:
            self._state.processes[task_id].status = "failed"
            del self._state.processes[task_id]
            self._save_state()

    def is_any_running(self) -> bool:
        """Check if any agent processes are currently running.

        Returns:
            True if at least one process is active.
        """
        return len(self._state.processes) > 0

    def get_running_count(self) -> int:
        """Get the number of currently running processes.

        Returns:
            Count of active processes.
        """
        return len(self._state.processes)

    def get_running_tasks(self) -> List[RunningProcess]:
        """Get all currently running processes.

        Returns:
            List of RunningProcess objects.
        """
        return list(self._state.processes.values())

    def get_process(self, task_id: str) -> Optional[RunningProcess]:
        """Get a specific running process by task ID.

        Args:
            task_id: UUID of the task.

        Returns:
            RunningProcess or None.
        """
        return self._state.processes.get(task_id)

    def get_running_summary(self) -> str:
        """Get a human-readable summary of running processes.

        Returns:
            Summary string for display to user.
        """
        if not self._state.processes:
            return "No agents currently running."

        lines = [f"{len(self._state.processes)} agent(s) currently running:"]
        for proc in self._state.processes.values():
            lines.append(f"  - [{proc.agent_name}] {proc.task_title} (started: {proc.started_at[:19]})")
        return "\n".join(lines)

    def clear_all(self) -> None:
        """Clear all tracked processes (e.g., after restart)."""
        self._state.processes.clear()
        self._save_state()
