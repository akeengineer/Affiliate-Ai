"""Result Collector for 9ake-kiro-agents.

Collects agent output (stdout/files), parses results, validates them,
and stores them in the results directory.
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Optional

from scripts.agents.core.dispatcher import DispatchCommand
from scripts.agents.core.models.config import ProjectConfig, ValidationConfig
from scripts.agents.core.models.result import AgentResult, ResultStatus
from scripts.agents.core.models.task import Task, TaskStatus


class CollectorError(Exception):
    """Raised when collection or validation fails."""


class Collector:
    """Collects and validates agent execution results.

    Responsibilities:
    - Parse agent stdout into structured AgentResult
    - Validate results (check files exist, tests pass)
    - Save results to the results directory
    - Update task state based on results
    """

    def __init__(self, config: ProjectConfig) -> None:
        """Initialize collector with project configuration.

        Args:
            config: Loaded project configuration.
        """
        self.config = config
        self._project_root = config.project_root or Path.cwd()

    def collect(
        self,
        dispatch_cmd: DispatchCommand,
        process_result: subprocess.CompletedProcess,
        duration_seconds: float = 0.0,
        attempt: int = 1,
        is_fallback: bool = False,
    ) -> AgentResult:
        """Collect and process the result of an agent execution.

        Args:
            dispatch_cmd: The command that was dispatched.
            process_result: The completed subprocess result.
            duration_seconds: How long execution took.
            attempt: Which attempt this is (1-based).
            is_fallback: Whether a fallback agent handled this.

        Returns:
            Parsed and validated AgentResult.
        """
        task = dispatch_cmd.task
        agent_name = dispatch_cmd.agent.name

        # Check for timeout
        if process_result.returncode == -1 and "TIMEOUT" in (process_result.stderr or ""):
            result = AgentResult.create(
                task_id=task.id,
                agent=agent_name,
                status="timeout",
                summary=f"Task timed out after {task.timeout_seconds}s",
                duration_seconds=duration_seconds,
                errors=[process_result.stderr],
                attempt=attempt,
                is_fallback=is_fallback,
                raw_output=process_result.stdout,
            )
            task.mark_failed()
            self._save_result(result)
            self._save_task_state(task)
            return result

        # Check for command not found / non-zero exit
        if process_result.returncode != 0:
            result = AgentResult.create(
                task_id=task.id,
                agent=agent_name,
                status="fail",
                summary=f"Agent exited with code {process_result.returncode}",
                duration_seconds=duration_seconds,
                errors=[process_result.stderr or f"Exit code: {process_result.returncode}"],
                attempt=attempt,
                is_fallback=is_fallback,
                raw_output=process_result.stdout,
            )
            task.mark_failed()
            self._save_result(result)
            self._save_task_state(task)
            return result

        # Try to parse structured JSON output
        result = self._parse_agent_output(
            stdout=process_result.stdout,
            task=task,
            agent_name=agent_name,
            duration_seconds=duration_seconds,
            attempt=attempt,
            is_fallback=is_fallback,
        )

        # Validate result if configured
        validation_errors = self._validate_result(result, task)
        if validation_errors:
            result.errors.extend(validation_errors)
            if result.status == ResultStatus.SUCCESS:
                result.status = ResultStatus.PARTIAL

        # Update task state
        if result.is_success:
            task.mark_completed()
        else:
            task.mark_failed()

        # Persist
        self._save_result(result)
        self._save_task_state(task)

        return result

    def _parse_agent_output(
        self,
        stdout: str,
        task: Task,
        agent_name: str,
        duration_seconds: float,
        attempt: int,
        is_fallback: bool,
    ) -> AgentResult:
        """Parse agent stdout into an AgentResult.

        Tries to extract JSON from the output. Falls back to treating
        the entire output as a summary if JSON parsing fails.

        Args:
            stdout: Raw stdout from the agent.
            task: The task that was executed.
            agent_name: Name of the agent.
            duration_seconds: Execution duration.
            attempt: Attempt number.
            is_fallback: Whether this was a fallback execution.

        Returns:
            Parsed AgentResult.
        """
        # Try to parse as JSON directly
        parsed = self._extract_json(stdout)

        if parsed:
            return AgentResult.create(
                task_id=task.id,
                agent=agent_name,
                status=parsed.get("status", "success"),
                summary=parsed.get("summary", "Task completed"),
                duration_seconds=duration_seconds,
                files_modified=parsed.get("files_modified", []),
                files_created=parsed.get("files_created", []),
                tests_run=parsed.get("tests_run"),
                tests_passed=parsed.get("tests_passed"),
                errors=parsed.get("errors", []),
                attempt=attempt,
                is_fallback=is_fallback,
                raw_output=stdout,
                next_steps=parsed.get("next_steps", []),
            )

        # Fallback: treat stdout as unstructured output
        # Consider it success if exit code was 0 (checked before this call)
        return AgentResult.create(
            task_id=task.id,
            agent=agent_name,
            status="partial",
            summary="Agent completed but did not return structured JSON output",
            duration_seconds=duration_seconds,
            errors=["Output was not valid JSON. Raw output saved in raw_output field."],
            attempt=attempt,
            is_fallback=is_fallback,
            raw_output=stdout,
        )

    def _extract_json(self, text: str) -> Optional[dict]:
        """Extract a JSON object from text.

        Tries multiple strategies:
        1. Parse the entire text as JSON
        2. Find JSON object within the text (between first { and last })

        Args:
            text: Text that may contain JSON.

        Returns:
            Parsed dict or None if no valid JSON found.
        """
        if not text or not text.strip():
            return None

        text = text.strip()

        # Strategy 1: direct parse
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass

        # Strategy 2: find JSON object boundaries
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace > first_brace:
            candidate = text[first_brace : last_brace + 1]
            try:
                data = json.loads(candidate)
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                pass

        return None

    def _validate_result(self, result: AgentResult, task: Task) -> list:
        """Validate result against task expectations and config.

        Checks:
        - Expected output files exist (if configured)
        - Tests pass (if configured and applicable)

        Args:
            result: The agent result to validate.
            task: The original task.

        Returns:
            List of validation error strings (empty if valid).
        """
        errors = []
        validation = self.config.validation

        # Check expected output files exist
        if validation.check_files_exist and task.expected_outputs:
            for expected_file in task.expected_outputs:
                file_path = self._project_root / expected_file
                if not file_path.exists():
                    errors.append(f"Expected output file not found: {expected_file}")

        # Check files_created actually exist
        if validation.check_files_exist and result.files_created:
            for created_file in result.files_created:
                file_path = self._project_root / created_file
                if not file_path.exists():
                    errors.append(f"Claimed created file not found: {created_file}")

        return errors

    def run_tests(self, test_command: Optional[str] = None) -> tuple:
        """Run the project test suite.

        Args:
            test_command: Custom test command. Defaults to config value.

        Returns:
            Tuple of (passed: bool, output: str).
        """
        cmd = test_command or self.config.validation.test_command
        try:
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(self._project_root),
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Test command timed out"
        except FileNotFoundError:
            return False, f"Test command not found: {cmd}"

    def _save_result(self, result: AgentResult) -> Path:
        """Save result to the results directory.

        Args:
            result: AgentResult to save.

        Returns:
            Path to the saved file.
        """
        results_dir = self._project_root / self.config.paths.results
        return result.save(results_dir)

    def _save_task_state(self, task: Task) -> None:
        """Update task state in the state directory.

        Args:
            task: Task with updated state.
        """
        state_dir = self._project_root / self.config.paths.state
        task.save(state_dir)

    def load_result(self, task_id: str) -> Optional[AgentResult]:
        """Load a previously saved result by task ID.

        Args:
            task_id: UUID of the task.

        Returns:
            AgentResult or None if not found.
        """
        results_dir = self._project_root / self.config.paths.results
        result_path = results_dir / f"{task_id}.json"
        if result_path.exists():
            return AgentResult.load(result_path)
        return None

    def load_all_results(self) -> list:
        """Load all results from the results directory.

        Returns:
            List of AgentResult objects.
        """
        results_dir = self._project_root / self.config.paths.results
        if not results_dir.exists():
            return []

        results = []
        for file_path in sorted(results_dir.glob("*.json")):
            try:
                result = AgentResult.load(file_path)
                results.append(result)
            except (json.JSONDecodeError, KeyError, ValueError):
                continue
        return results
