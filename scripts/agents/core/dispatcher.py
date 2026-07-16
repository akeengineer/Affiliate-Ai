"""Core Dispatcher for 9ake-kiro-agents.

Reads the task queue, classifies tasks, selects the appropriate agent,
builds CLI commands, and spawns subprocess(es) for execution.
Supports parallel dispatch for independent tasks and sequential for dependent ones.
"""

from __future__ import annotations

import asyncio
import json
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from scripts.agents.core.models.config import AgentConfig, ProjectConfig
from scripts.agents.core.models.task import Task, TaskStatus, TaskType


@dataclass
class DispatchCommand:
    """A fully-constructed CLI command ready to execute."""

    task: Task
    agent: AgentConfig
    command: List[str]
    prompt: str
    is_fallback: bool = False

    @property
    def command_str(self) -> str:
        """Return the full command as a string for display."""
        return " ".join(self.command)


@dataclass
class DispatchPlan:
    """A plan showing what will be dispatched and in what order."""

    parallel_groups: List[List[DispatchCommand]] = field(default_factory=list)
    skipped: List[Tuple[Task, str]] = field(default_factory=list)

    @property
    def total_tasks(self) -> int:
        """Total number of tasks in the plan."""
        return sum(len(group) for group in self.parallel_groups)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize plan to dict for reporting."""
        return {
            "parallel_groups": [
                [
                    {
                        "task_id": cmd.task.id,
                        "title": cmd.task.title,
                        "agent": cmd.agent.name,
                        "command": cmd.command_str,
                        "is_fallback": cmd.is_fallback,
                    }
                    for cmd in group
                ]
                for group in self.parallel_groups
            ],
            "skipped": [
                {"task_id": t.id, "title": t.title, "reason": reason}
                for t, reason in self.skipped
            ],
        }


class Dispatcher:
    """Dispatches tasks to CLI agents based on configuration.

    The dispatcher:
    1. Reads queued tasks from the queue directory
    2. Resolves dependencies (topological sort)
    3. Selects the appropriate agent for each task
    4. Builds CLI commands
    5. Executes tasks (parallel for independent, sequential for dependent)
    """

    def __init__(self, config: ProjectConfig) -> None:
        """Initialize dispatcher with project configuration.

        Args:
            config: Loaded project configuration.
        """
        self.config = config
        self._project_root = config.project_root or Path.cwd()

    def load_queue(self) -> List[Task]:
        """Load all queued tasks from the queue directory.

        Returns:
            List of Task objects with status 'queued'.
        """
        queue_dir = self._project_root / self.config.paths.queue
        if not queue_dir.exists():
            return []

        tasks = []
        for file_path in sorted(queue_dir.glob("*.json")):
            try:
                task = Task.load(file_path)
                if task.status == TaskStatus.QUEUED:
                    tasks.append(task)
            except (json.JSONDecodeError, KeyError, ValueError):
                continue  # Skip malformed task files
        return tasks

    def select_agent(self, task: Task) -> Optional[AgentConfig]:
        """Select the appropriate agent for a task.

        Logic:
        1. If task has explicit agent_preference (not 'auto'), use that.
        2. Otherwise, match task.type to agent.task_types from config.

        Args:
            task: The task to find an agent for.

        Returns:
            AgentConfig for the selected agent, or None if no match.
        """
        # Explicit preference
        if task.agent_preference != "auto":
            agent = self.config.get_agent(task.agent_preference)
            if agent:
                return agent

        # Match by task type
        return self.config.get_agent_for_task_type(task.type.value)

    def build_command(self, task: Task, agent: AgentConfig) -> List[str]:
        """Build the CLI command for dispatching a task to an agent.

        Args:
            task: The task to dispatch.
            agent: The agent configuration.

        Returns:
            List of command parts ready for subprocess.
        """
        cmd = [agent.command] + list(agent.flags)

        # Add agent-specific options
        if agent.name == "claude":
            # Add system prompt file if specified
            if agent.system_prompt:
                prompt_path = self._project_root / agent.system_prompt
                cmd.extend(["--system-prompt-file", str(prompt_path)])
            # Add max turns
            if agent.max_turns:
                cmd.extend(["--max-turns", str(agent.max_turns)])
            # Add budget limit
            if agent.max_budget_usd:
                cmd.extend(["--max-budget-usd", str(agent.max_budget_usd)])

        elif agent.name == "codex":
            # Codex uses the prompt as the argument
            pass  # flags already added, prompt goes at the end

        # Build the task prompt with context
        full_prompt = self._build_task_prompt(task)

        # The prompt is the final argument
        cmd.append(full_prompt)

        return cmd

    def _build_task_prompt(self, task: Task) -> str:
        """Build the full prompt string for a task.

        Combines:
        - Task title and type
        - Task prompt/instruction
        - Input file references
        - Expected outputs
        - Task ID for result tracking

        Args:
            task: The task to build a prompt for.

        Returns:
            The full prompt string.
        """
        parts = [
            f"TASK_ID: {task.id}",
            f"TASK_TYPE: {task.type.value}",
            f"TITLE: {task.title}",
            "",
            "INSTRUCTION:",
            task.prompt,
        ]

        if task.input_files:
            parts.append("")
            parts.append("INPUT FILES (read these for context):")
            for f in task.input_files:
                parts.append(f"  - {f}")

        if task.expected_outputs:
            parts.append("")
            parts.append("EXPECTED OUTPUTS:")
            for f in task.expected_outputs:
                parts.append(f"  - {f}")

        parts.append("")
        parts.append(
            "Return your result as JSON matching the output contract in your system prompt."
        )

        return "\n".join(parts)

    def build_dispatch_command(
        self, task: Task, is_fallback: bool = False
    ) -> Optional[DispatchCommand]:
        """Build a complete DispatchCommand for a task.

        Args:
            task: Task to dispatch.
            is_fallback: Whether this is a fallback dispatch.

        Returns:
            DispatchCommand or None if no suitable agent found.
        """
        agent = self.select_agent(task)
        if not agent:
            return None

        command = self.build_command(task, agent)
        prompt = self._build_task_prompt(task)

        return DispatchCommand(
            task=task,
            agent=agent,
            command=command,
            prompt=prompt,
            is_fallback=is_fallback,
        )

    def resolve_dependencies(self, tasks: List[Task]) -> List[List[Task]]:
        """Resolve task dependencies and return execution groups.

        Tasks in the same group can run in parallel.
        Groups must be executed sequentially.

        Uses topological sort to determine execution order.

        Args:
            tasks: List of tasks to organize.

        Returns:
            List of groups, where each group is a list of tasks
            that can run in parallel.
        """
        if not tasks:
            return []

        # Build dependency graph
        task_map = {t.id: t for t in tasks}
        # Track completed tasks (not in current queue)
        completed_ids: set = set()

        # Kahn's algorithm for topological sort into levels
        # In-degree: how many unresolved dependencies each task has
        in_degree: Dict[str, int] = {}
        for task in tasks:
            count = 0
            for dep_id in task.dependencies:
                # Only count dependencies that are in our current task set
                if dep_id in task_map:
                    count += 1
                # Dependencies not in the queue are assumed completed
            in_degree[task.id] = count

        groups: List[List[Task]] = []
        remaining = set(task_map.keys())

        while remaining:
            # Find all tasks with no unresolved dependencies
            ready = [
                tid for tid in remaining
                if in_degree.get(tid, 0) == 0
            ]

            if not ready:
                # Circular dependency — add remaining as a single group
                groups.append([task_map[tid] for tid in remaining])
                break

            # Sort by priority for deterministic ordering within a group
            priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            ready.sort(key=lambda tid: priority_order.get(task_map[tid].priority.value, 2))

            # Limit parallel group size
            max_parallel = self.config.dispatch.parallel_max
            group = [task_map[tid] for tid in ready[:max_parallel]]
            overflow = ready[max_parallel:]

            groups.append(group)

            # Remove dispatched tasks from remaining
            for tid in ready[:max_parallel]:
                remaining.discard(tid)
                # Decrease in-degree of dependents
                for other_tid in remaining:
                    if tid in task_map[other_tid].dependencies:
                        in_degree[other_tid] = max(0, in_degree[other_tid] - 1)

            # Overflow goes back as ready in next iteration (in_degree already 0)

        return groups

    def create_plan(self, tasks: Optional[List[Task]] = None) -> DispatchPlan:
        """Create a dispatch plan without executing anything.

        Useful for dry-run mode.

        Args:
            tasks: Tasks to plan for. If None, loads from queue.

        Returns:
            DispatchPlan showing execution order and commands.
        """
        if tasks is None:
            tasks = self.load_queue()

        plan = DispatchPlan()

        if not tasks:
            return plan

        # Resolve into execution groups
        groups = self.resolve_dependencies(tasks)

        for group in groups:
            dispatch_group = []
            for task in group:
                cmd = self.build_dispatch_command(task)
                if cmd:
                    dispatch_group.append(cmd)
                else:
                    plan.skipped.append((task, f"No agent found for type '{task.type.value}'"))
            if dispatch_group:
                plan.parallel_groups.append(dispatch_group)

        return plan

    def execute_command(self, dispatch_cmd: DispatchCommand) -> subprocess.CompletedProcess:
        """Execute a single dispatch command synchronously.

        Args:
            dispatch_cmd: The command to execute.

        Returns:
            CompletedProcess with stdout/stderr.
        """
        dispatch_cmd.task.mark_active()
        self._save_task_state(dispatch_cmd.task)

        try:
            result = subprocess.run(
                dispatch_cmd.command,
                capture_output=True,
                text=True,
                timeout=dispatch_cmd.task.timeout_seconds,
                cwd=str(self._project_root),
            )
            return result
        except subprocess.TimeoutExpired:
            # Create a fake CompletedProcess for timeout
            return subprocess.CompletedProcess(
                args=dispatch_cmd.command,
                returncode=-1,
                stdout="",
                stderr=f"TIMEOUT: Task exceeded {dispatch_cmd.task.timeout_seconds}s limit",
            )

    async def execute_command_async(
        self, dispatch_cmd: DispatchCommand
    ) -> Tuple[DispatchCommand, subprocess.CompletedProcess]:
        """Execute a dispatch command asynchronously.

        Args:
            dispatch_cmd: The command to execute.

        Returns:
            Tuple of (DispatchCommand, CompletedProcess).
        """
        dispatch_cmd.task.mark_active()
        self._save_task_state(dispatch_cmd.task)

        try:
            process = await asyncio.create_subprocess_exec(
                *dispatch_cmd.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self._project_root),
            )

            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    process.communicate(),
                    timeout=dispatch_cmd.task.timeout_seconds,
                )
                stdout = stdout_bytes.decode("utf-8", errors="replace") if stdout_bytes else ""
                stderr = stderr_bytes.decode("utf-8", errors="replace") if stderr_bytes else ""
                returncode = process.returncode or 0
            except asyncio.TimeoutError:
                process.kill()
                await process.communicate()
                stdout = ""
                stderr = f"TIMEOUT: Task exceeded {dispatch_cmd.task.timeout_seconds}s limit"
                returncode = -1

        except FileNotFoundError as e:
            stdout = ""
            stderr = f"Command not found: {dispatch_cmd.command[0]} ({e})"
            returncode = 127

        completed = subprocess.CompletedProcess(
            args=dispatch_cmd.command,
            returncode=returncode,
            stdout=stdout,
            stderr=stderr,
        )
        return dispatch_cmd, completed

    async def dispatch_group_async(
        self, group: List[DispatchCommand]
    ) -> List[Tuple[DispatchCommand, subprocess.CompletedProcess]]:
        """Dispatch a group of commands in parallel.

        Args:
            group: List of commands to run concurrently.

        Returns:
            List of (command, result) tuples.
        """
        coros = [self.execute_command_async(cmd) for cmd in group]
        return await asyncio.gather(*coros)

    def dispatch_all(
        self, tasks: Optional[List[Task]] = None, dry_run: bool = False
    ) -> DispatchPlan:
        """Dispatch all queued tasks according to their dependencies.

        Args:
            tasks: Tasks to dispatch. If None, loads from queue.
            dry_run: If True, only plan without executing.

        Returns:
            The dispatch plan (with results populated if not dry_run).
        """
        plan = self.create_plan(tasks)

        if dry_run:
            return plan

        # Execute groups sequentially, tasks within groups in parallel
        for group in plan.parallel_groups:
            if len(group) == 1:
                # Single task — run synchronously
                self.execute_command(group[0])
            else:
                # Multiple tasks — run in parallel
                asyncio.run(self.dispatch_group_async(group))

        return plan

    def _save_task_state(self, task: Task) -> None:
        """Save task state to the state directory.

        Args:
            task: Task to save state for.
        """
        state_dir = self._project_root / self.config.paths.state
        state_dir.mkdir(parents=True, exist_ok=True)
        task.save(state_dir)
