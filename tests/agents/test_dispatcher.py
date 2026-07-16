"""Tests for the Core Dispatcher."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from scripts.agents.core.dispatcher import Dispatcher, DispatchCommand, DispatchPlan
from scripts.agents.core.models.config import AgentConfig, ProjectConfig
from scripts.agents.core.models.task import Task, TaskPriority, TaskStatus, TaskType


MINIMAL_CONFIG = {
    "project_name": "Test",
    "package_name": "9ake-kiro-agents",
    "agents": {
        "claude": {
            "command": "claude",
            "flags": ["-p", "--dangerously-skip-permissions", "--output-format", "json"],
            "system_prompt": ".agents/prompts/claude-cli-agent.md",
            "max_turns": 10,
            "max_budget_usd": 5.0,
            "task_types": ["reasoning", "design", "review"],
            "fallback_to": "codex",
        },
        "codex": {
            "command": "codex",
            "flags": ["-q", "--approval-mode", "full-auto"],
            "system_prompt": ".agents/prompts/codex-cli-agent.md",
            "task_types": ["implementation", "test", "refactor"],
            "fallback_to": "claude",
        },
    },
    "dispatch": {
        "retry_max": 2,
        "retry_backoff_seconds": [5, 15],
        "fallback_enabled": True,
        "parallel_max": 2,
        "default_timeout_seconds": 300,
    },
    "ssh": {"host": "test-host", "project_path": "/test"},
    "validation": {"run_tests": True, "test_command": "python -m pytest"},
    "paths": {
        "queue": ".agents/queue",
        "results": ".agents/results",
        "state": ".agents/state",
        "reports": ".agents/reports",
        "prompts": ".agents/prompts",
        "schemas": ".agents/schemas",
    },
}


@pytest.fixture
def project_dir(tmp_path):
    """Create a project with config and queue."""
    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir()
    (agents_dir / "queue").mkdir()
    (agents_dir / "state").mkdir()
    (agents_dir / "prompts").mkdir()
    (agents_dir / "prompts" / "claude-cli-agent.md").write_text("# Claude", encoding="utf-8")
    (agents_dir / "prompts" / "codex-cli-agent.md").write_text("# Codex", encoding="utf-8")

    config_path = agents_dir / "config.yaml"
    config_path.write_text(yaml.dump(MINIMAL_CONFIG), encoding="utf-8")
    return tmp_path


@pytest.fixture
def config(project_dir):
    """Load config from the temporary project."""
    return ProjectConfig.load(str(project_dir / ".agents" / "config.yaml"))


@pytest.fixture
def dispatcher(config):
    """Create a Dispatcher instance."""
    return Dispatcher(config)


def make_task(
    task_type: str = "implementation",
    title: str = "Test task",
    prompt: str = "Do the thing",
    priority: str = "medium",
    agent_preference: str = "auto",
    dependencies: list = None,
) -> Task:
    """Helper to create a task."""
    return Task.create(
        title=title,
        task_type=task_type,
        prompt=prompt,
        priority=priority,
        agent_preference=agent_preference,
        dependencies=dependencies,
    )


class TestAgentSelection:
    """Tests for task-to-agent mapping."""

    def test_implementation_maps_to_codex(self, dispatcher):
        task = make_task(task_type="implementation")
        agent = dispatcher.select_agent(task)
        assert agent is not None
        assert agent.name == "codex"

    def test_test_maps_to_codex(self, dispatcher):
        task = make_task(task_type="test")
        agent = dispatcher.select_agent(task)
        assert agent.name == "codex"

    def test_refactor_maps_to_codex(self, dispatcher):
        task = make_task(task_type="refactor")
        agent = dispatcher.select_agent(task)
        assert agent.name == "codex"

    def test_reasoning_maps_to_claude(self, dispatcher):
        task = make_task(task_type="reasoning")
        agent = dispatcher.select_agent(task)
        assert agent.name == "claude"

    def test_design_maps_to_claude(self, dispatcher):
        task = make_task(task_type="design")
        agent = dispatcher.select_agent(task)
        assert agent.name == "claude"

    def test_review_maps_to_claude(self, dispatcher):
        task = make_task(task_type="review")
        agent = dispatcher.select_agent(task)
        assert agent.name == "claude"

    def test_explicit_agent_preference(self, dispatcher):
        task = make_task(task_type="implementation", agent_preference="claude")
        agent = dispatcher.select_agent(task)
        assert agent.name == "claude"

    def test_unknown_preference_falls_back_to_type(self, dispatcher):
        task = make_task(task_type="implementation", agent_preference="nonexistent")
        agent = dispatcher.select_agent(task)
        # Falls through to type-based matching
        assert agent is not None


class TestCommandBuilding:
    """Tests for CLI command construction."""

    def test_claude_command_structure(self, dispatcher):
        task = make_task(task_type="reasoning", prompt="Analyze the problem")
        agent = dispatcher.select_agent(task)
        cmd = dispatcher.build_command(task, agent)

        assert cmd[0] == "claude"
        assert "-p" in cmd
        assert "--dangerously-skip-permissions" in cmd
        assert "--output-format" in cmd
        assert "--system-prompt-file" in cmd
        assert "--max-turns" in cmd
        assert "10" in cmd
        assert "--max-budget-usd" in cmd
        # Last element is the prompt
        assert "TASK_ID:" in cmd[-1]

    def test_codex_command_structure(self, dispatcher):
        task = make_task(task_type="implementation", prompt="Build it")
        agent = dispatcher.select_agent(task)
        cmd = dispatcher.build_command(task, agent)

        assert cmd[0] == "codex"
        assert "-q" in cmd
        assert "--approval-mode" in cmd
        assert "full-auto" in cmd
        # Last element is the prompt
        assert "TASK_ID:" in cmd[-1]

    def test_prompt_includes_task_id(self, dispatcher):
        task = make_task(prompt="Build the scorer")
        agent = dispatcher.select_agent(task)
        cmd = dispatcher.build_command(task, agent)
        prompt = cmd[-1]
        assert task.id in prompt

    def test_prompt_includes_input_files(self, dispatcher):
        task = make_task(prompt="Implement scoring")
        task.input_files = ["docs/SCORING_SPEC.md", "AGENTS.md"]
        agent = dispatcher.select_agent(task)
        cmd = dispatcher.build_command(task, agent)
        prompt = cmd[-1]
        assert "docs/SCORING_SPEC.md" in prompt
        assert "AGENTS.md" in prompt

    def test_prompt_includes_expected_outputs(self, dispatcher):
        task = make_task(prompt="Create scorer")
        task.expected_outputs = ["scripts/dev/score_product.py"]
        agent = dispatcher.select_agent(task)
        cmd = dispatcher.build_command(task, agent)
        prompt = cmd[-1]
        assert "scripts/dev/score_product.py" in prompt


class TestDependencyResolution:
    """Tests for topological sort and grouping."""

    def test_independent_tasks_in_one_group(self, dispatcher):
        tasks = [
            make_task(title="A", task_type="implementation"),
            make_task(title="B", task_type="reasoning"),
        ]
        groups = dispatcher.resolve_dependencies(tasks)
        assert len(groups) == 1
        assert len(groups[0]) == 2

    def test_dependent_tasks_in_separate_groups(self, dispatcher):
        task_a = make_task(title="A", task_type="implementation")
        task_b = make_task(title="B", task_type="test", dependencies=[task_a.id])
        tasks = [task_a, task_b]

        groups = dispatcher.resolve_dependencies(tasks)
        assert len(groups) == 2
        assert groups[0][0].id == task_a.id
        assert groups[1][0].id == task_b.id

    def test_parallel_max_limits_group_size(self, dispatcher):
        # parallel_max is 2 in config
        tasks = [
            make_task(title="A"),
            make_task(title="B"),
            make_task(title="C"),
        ]
        groups = dispatcher.resolve_dependencies(tasks)
        # First group has max 2, remaining in next group
        assert len(groups[0]) <= 2
        total = sum(len(g) for g in groups)
        assert total == 3

    def test_empty_tasks_returns_empty(self, dispatcher):
        groups = dispatcher.resolve_dependencies([])
        assert groups == []

    def test_priority_ordering_within_group(self, dispatcher):
        tasks = [
            make_task(title="Low", priority="low"),
            make_task(title="Critical", priority="critical"),
            make_task(title="High", priority="high"),
        ]
        groups = dispatcher.resolve_dependencies(tasks)
        # First group should have critical and high (parallel_max=2)
        first_titles = [t.title for t in groups[0]]
        assert "Critical" in first_titles

    def test_external_dependency_assumed_complete(self, dispatcher):
        """Dependencies not in the queue are assumed already completed."""
        task = make_task(
            title="Depends on external",
            dependencies=["99999999-9999-9999-9999-999999999999"],
        )
        groups = dispatcher.resolve_dependencies([task])
        assert len(groups) == 1
        assert groups[0][0].id == task.id


class TestDispatchPlan:
    """Tests for the planning (dry-run) functionality."""

    def test_create_plan_from_queue(self, dispatcher, project_dir):
        # Add tasks to queue
        queue_dir = project_dir / ".agents" / "queue"
        task1 = make_task(title="Impl", task_type="implementation")
        task1.save(queue_dir)
        task2 = make_task(title="Design", task_type="design")
        task2.save(queue_dir)

        plan = dispatcher.create_plan()
        assert plan.total_tasks == 2
        assert len(plan.skipped) == 0

    def test_plan_with_no_queue(self, dispatcher):
        plan = dispatcher.create_plan()
        assert plan.total_tasks == 0

    def test_plan_to_dict(self, dispatcher):
        tasks = [make_task(title="A"), make_task(title="B", task_type="design")]
        plan = dispatcher.create_plan(tasks)
        d = plan.to_dict()
        assert "parallel_groups" in d
        assert "skipped" in d

    def test_dry_run_does_not_execute(self, dispatcher):
        tasks = [make_task(title="DryRun")]
        plan = dispatcher.dispatch_all(tasks, dry_run=True)
        # Task should still be queued (not active)
        assert tasks[0].status == TaskStatus.QUEUED
        assert plan.total_tasks == 1


class TestExecution:
    """Tests for actual command execution (mocked subprocess)."""

    @patch("scripts.agents.core.dispatcher.subprocess.run")
    def test_execute_single_task(self, mock_run, dispatcher):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"status": "success", "summary": "Done"}',
            stderr="",
        )

        task = make_task(title="Execute me")
        cmd = dispatcher.build_dispatch_command(task)
        result = dispatcher.execute_command(cmd)

        assert mock_run.called
        assert result.returncode == 0
        assert task.status == TaskStatus.ACTIVE

    @patch("scripts.agents.core.dispatcher.subprocess.run")
    def test_execute_timeout_returns_negative_one(self, mock_run, dispatcher):
        import subprocess as sp
        mock_run.side_effect = sp.TimeoutExpired(cmd="test", timeout=300)

        task = make_task(title="Slow task")
        cmd = dispatcher.build_dispatch_command(task)
        result = dispatcher.execute_command(cmd)

        assert result.returncode == -1
        assert "TIMEOUT" in result.stderr

    @patch("scripts.agents.core.dispatcher.subprocess.run")
    def test_dispatch_all_calls_subprocess(self, mock_run, dispatcher):
        mock_run.return_value = MagicMock(returncode=0, stdout="{}", stderr="")

        tasks = [make_task(title="Single")]
        dispatcher.dispatch_all(tasks, dry_run=False)

        assert mock_run.called


class TestLoadQueue:
    """Tests for loading tasks from the queue directory."""

    def test_loads_queued_tasks(self, dispatcher, project_dir):
        queue_dir = project_dir / ".agents" / "queue"
        task = make_task(title="Queued task")
        task.save(queue_dir)

        loaded = dispatcher.load_queue()
        assert len(loaded) == 1
        assert loaded[0].id == task.id

    def test_skips_non_queued_tasks(self, dispatcher, project_dir):
        queue_dir = project_dir / ".agents" / "queue"
        task = make_task(title="Active task")
        task.mark_active()
        task.save(queue_dir)

        loaded = dispatcher.load_queue()
        assert len(loaded) == 0

    def test_skips_malformed_files(self, dispatcher, project_dir):
        queue_dir = project_dir / ".agents" / "queue"
        # Write invalid JSON
        (queue_dir / "bad.json").write_text("not valid json", encoding="utf-8")
        # Write valid task
        task = make_task(title="Good task")
        task.save(queue_dir)

        loaded = dispatcher.load_queue()
        assert len(loaded) == 1
        assert loaded[0].title == "Good task"

    def test_empty_queue(self, dispatcher):
        loaded = dispatcher.load_queue()
        assert loaded == []
