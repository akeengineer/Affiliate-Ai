"""Retry and Fallback Engine for 9ake-kiro-agents.

Handles retry logic (max attempts with exponential backoff) and
cross-agent fallback (Claude <-> Codex) when an agent fails.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from scripts.agents.core.models.config import AgentConfig, ProjectConfig
from scripts.agents.core.models.result import AgentResult, ResultStatus
from scripts.agents.core.models.task import Task, TaskStatus


@dataclass
class RetryAttempt:
    """Record of a single retry/fallback attempt."""

    attempt: int
    agent: str
    status: str
    error: str
    is_fallback: bool
    duration_seconds: float
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class RetryLog:
    """Full log of all retry/fallback attempts for a task."""

    task_id: str
    attempts: List[RetryAttempt] = field(default_factory=list)
    final_status: str = ""
    final_agent: str = ""
    total_duration_seconds: float = 0.0

    def add_attempt(self, attempt: RetryAttempt) -> None:
        """Add an attempt to the log."""
        self.attempts.append(attempt)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "task_id": self.task_id,
            "attempts": [asdict(a) for a in self.attempts],
            "final_status": self.final_status,
            "final_agent": self.final_agent,
            "total_duration_seconds": self.total_duration_seconds,
        }

    def save(self, directory: Path) -> Path:
        """Save retry log to a file.

        Args:
            directory: Directory to save in.

        Returns:
            Path to the saved file.
        """
        directory.mkdir(parents=True, exist_ok=True)
        file_path = directory / f"{self.task_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            f.write("\n")
        return file_path


# Type alias for dispatch+collect function
DispatchFn = Callable[[Task, AgentConfig, int, bool], AgentResult]


class RetryEngine:
    """Handles retry with exponential backoff and cross-agent fallback.

    Strategy:
    1. Dispatch to the preferred agent.
    2. If it fails, wait (backoff) and retry the same agent up to retry_max times.
    3. If all retries fail and fallback is enabled, try the fallback agent.
    4. If the fallback also fails, return the final failure result.
    """

    def __init__(self, config: ProjectConfig, sleep_fn: Optional[Callable] = None) -> None:
        """Initialize retry engine.

        Args:
            config: Project configuration with retry/fallback settings.
            sleep_fn: Optional sleep function for testing (default: time.sleep).
        """
        self.config = config
        self._sleep = sleep_fn or time.sleep
        self._project_root = config.project_root or Path.cwd()

    def execute_with_retry(
        self,
        task: Task,
        agent: AgentConfig,
        dispatch_fn: DispatchFn,
    ) -> Tuple[AgentResult, RetryLog]:
        """Execute a task with retry and fallback logic.

        Args:
            task: The task to execute.
            agent: The primary agent to try first.
            dispatch_fn: Function that dispatches task to agent and returns result.
                Signature: (task, agent_config, attempt_number, is_fallback) -> AgentResult

        Returns:
            Tuple of (final AgentResult, RetryLog with all attempts).
        """
        retry_log = RetryLog(task_id=task.id)
        start_time = time.time()

        retry_max = min(task.max_retries, self.config.dispatch.retry_max)
        backoff_seconds = self.config.dispatch.retry_backoff_seconds

        # Phase 1: Try primary agent with retries
        result = self._try_agent(
            task=task,
            agent=agent,
            dispatch_fn=dispatch_fn,
            retry_log=retry_log,
            max_attempts=retry_max + 1,  # +1 for the initial attempt
            backoff_seconds=backoff_seconds,
            is_fallback=False,
        )

        # If succeeded, we're done
        if result.is_success:
            retry_log.final_status = result.status.value
            retry_log.final_agent = agent.name
            retry_log.total_duration_seconds = time.time() - start_time
            self._save_retry_log(retry_log)
            return result, retry_log

        # Phase 2: Try fallback agent (if enabled)
        if self.config.dispatch.fallback_enabled and agent.fallback_to:
            fallback_agent = self.config.get_agent(agent.fallback_to)
            if fallback_agent:
                # Reset task status for fallback attempt
                task.status = TaskStatus.QUEUED

                result = self._try_agent(
                    task=task,
                    agent=fallback_agent,
                    dispatch_fn=dispatch_fn,
                    retry_log=retry_log,
                    max_attempts=1,  # Fallback gets one shot
                    backoff_seconds=[],
                    is_fallback=True,
                )

                retry_log.final_status = result.status.value
                retry_log.final_agent = fallback_agent.name
                retry_log.total_duration_seconds = time.time() - start_time
                self._save_retry_log(retry_log)
                return result, retry_log

        # No fallback available or disabled — return last failure
        retry_log.final_status = result.status.value
        retry_log.final_agent = agent.name
        retry_log.total_duration_seconds = time.time() - start_time
        self._save_retry_log(retry_log)
        return result, retry_log

    def _try_agent(
        self,
        task: Task,
        agent: AgentConfig,
        dispatch_fn: DispatchFn,
        retry_log: RetryLog,
        max_attempts: int,
        backoff_seconds: List[int],
        is_fallback: bool,
    ) -> AgentResult:
        """Try an agent with retries.

        Args:
            task: Task to execute.
            agent: Agent to use.
            dispatch_fn: Dispatch function.
            retry_log: Log to record attempts.
            max_attempts: Max number of attempts.
            backoff_seconds: List of wait times between retries.
            is_fallback: Whether this is a fallback agent.

        Returns:
            The last AgentResult (success or final failure).
        """
        result: Optional[AgentResult] = None

        for attempt_idx in range(max_attempts):
            attempt_num = len(retry_log.attempts) + 1

            # Wait before retry (not before first attempt)
            if attempt_idx > 0 and backoff_seconds:
                wait_idx = min(attempt_idx - 1, len(backoff_seconds) - 1)
                wait_time = backoff_seconds[wait_idx]
                self._sleep(wait_time)

            # Dispatch
            attempt_start = time.time()
            result = dispatch_fn(task, agent, attempt_num, is_fallback)
            attempt_duration = time.time() - attempt_start

            # Log the attempt
            error_msg = "; ".join(result.errors) if result.errors else ""
            retry_log.add_attempt(RetryAttempt(
                attempt=attempt_num,
                agent=agent.name,
                status=result.status.value,
                error=error_msg,
                is_fallback=is_fallback,
                duration_seconds=attempt_duration,
            ))

            # Success — stop retrying
            if result.is_success:
                return result

            # Non-retriable failure — stop
            if not result.is_retriable:
                return result

        return result  # type: ignore[return-value]

    def _save_retry_log(self, retry_log: RetryLog) -> None:
        """Save the retry log to disk.

        Args:
            retry_log: Log to save.
        """
        retries_dir = self._project_root / self.config.paths.state / "retries"
        retry_log.save(retries_dir)

    @staticmethod
    def build_fallback_prompt_prefix(original_errors: List[str]) -> str:
        """Build a prompt prefix for the fallback agent explaining the previous failure.

        Args:
            original_errors: Error messages from the failed primary agent.

        Returns:
            Text to prepend to the task prompt for the fallback agent.
        """
        errors_text = "\n".join(f"  - {e}" for e in original_errors) if original_errors else "  - Unknown error"
        return (
            "NOTE: A previous agent attempted this task and failed with the following errors:\n"
            f"{errors_text}\n"
            "Please try a different approach to complete this task.\n\n"
        )
