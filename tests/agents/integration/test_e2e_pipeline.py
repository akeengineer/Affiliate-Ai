"""Integration Test — Full E2E Pipeline with Mock Agents.

Proves the complete orchestration pipeline works end-to-end:
  create task -> enqueue -> dispatch (mocked) -> collect -> validate -> report

Uses mock subprocess responses simulating real Claude/Codex output.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from scripts.agents.core.collector import Collector
from scripts.agents.core.dispatcher import Dispatcher
from scripts.agents.core.models.config import ProjectConfig
from scripts.agents.core.models.result import AgentResult, ResultStatus
from scripts.agents.core.models.task import Task, TaskStatus
from scripts.agents.core.reporter import Reporter
from scripts.agents.core.retry import RetryEngine
from scripts.agents.create_task import create_batch


FULL_CONFIG = {
    "project_name": "E2E Test Project",
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
        "retry_backoff_seconds": [1, 2],
        "fallback_enabled": True,
        "parallel_max": 2,
        "default_timeout_seconds": 60,
    },
    "ssh": {"host": "", "project_path": "", "user": ""},
    "validation": {
        "run_tests": False,
        "test_command": "python -m pytest",
        "check_files_exist": True,
    },
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
    """Create a full project setup for E2E testing."""
    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir()
    for sub in ["queue", "results", "state", "reports", "prompts", "schemas"]:
        (agents_dir / sub).mkdir()

    # Config
    config_path = agents_dir / "config.yaml"
    config_path.write_text(yaml.dump(FULL_CONFIG), encoding="utf-8")

    # Prompts
    (agents_dir / "prompts" / "claude-cli-agent.md").write_text(
        "# Claude Agent\nReasoning agent.", encoding="utf-8"
    )
    (agents_dir / "prompts" / "codex-cli-agent.md").write_text(
        "# Codex Agent\nImplementation agent.", encoding="utf-8"
    )

    return tmp_path


@pytest.fixture
def config(project_dir):
    return ProjectConfig.load(str(project_dir / ".agents" / "config.yaml"))


def mock_claude_success(task_id: str) -> str:
    """Simulate Claude returning structured JSON."""
    return json.dumps({
        "task_id": task_id,
        "status": "success",
        "summary": "Analyzed the scoring architecture and designed 3 interfaces",
        "files_modified": [],
        "files_created": [],
        "tests_run": None,
        "tests_passed": None,
        "errors": [],
        "next_steps": ["Implement ScoreCalculator class", "Add validation layer"],
        "reasoning": {
            "analysis": "The scoring system needs separation of parsing and calculation",
            "options_considered": ["Monolithic script", "Class-based with interfaces"],
            "recommendation": "Class-based approach for testability",
            "risks": ["Over-engineering for Phase 1"],
        },
    })


def mock_codex_success(task_id: str, project_dir: Path) -> str:
    """Simulate Codex returning structured JSON and creating files."""
    # Create the files that Codex would have created
    output_file = project_dir / "scripts" / "dev" / "score_product.py"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("# Score product script\ndef score(): pass\n", encoding="utf-8")

    return json.dumps({
        "task_id": task_id,
        "status": "success",
        "summary": "Implemented score_product.py with threshold logic",
        "files_modified": [],
        "files_created": ["scripts/dev/score_product.py"],
        "tests_run": "python -m pytest tests/test_score_product.py",
        "tests_passed": True,
        "errors": [],
        "next_steps": ["Add edge case tests"],
    })


def mock_codex_failure() -> str:
    """Simulate Codex failing."""
    return json.dumps({
        "status": "fail",
        "summary": "Could not parse input markdown",
        "errors": ["FileNotFoundError: vault/samples/product.md not found"],
        "next_steps": ["Create sample markdown file first"],
    })


class TestE2EPipelineParallel:
    """Test full pipeline with parallel independent tasks."""

    @patch("scripts.agents.core.dispatcher.subprocess.run")
    def test_parallel_tasks_dispatch_and_collect(self, mock_run, config, project_dir):
        """Two independent tasks (design + implementation) run in parallel."""
        # Create tasks
        tasks_data = [
            {
                "title": "Design scoring interface",
                "type": "design",
                "prompt": "Design the scoring module interfaces",
                "priority": "high",
            },
            {
                "title": "Implement score_product.py",
                "type": "implementation",
                "prompt": "Implement scoring script following docs/SCORING_SPEC.md",
                "expected_outputs": ["scripts/dev/score_product.py"],
            },
        ]
        tasks = create_batch(tasks_data, config=config)
        assert len(tasks) == 2

        # Mock subprocess to return appropriate responses
        def side_effect(cmd, **kwargs):
            cmd_str = " ".join(cmd)
            if "claude" in cmd_str:
                return MagicMock(
                    returncode=0,
                    stdout=mock_claude_success(tasks[0].id),
                    stderr="",
                )
            elif "codex" in cmd_str:
                return MagicMock(
                    returncode=0,
                    stdout=mock_codex_success(tasks[1].id, project_dir),
                    stderr="",
                )
            return MagicMock(returncode=1, stdout="", stderr="Unknown command")

        mock_run.side_effect = side_effect

        # Dispatch
        dispatcher = Dispatcher(config)
        collector = Collector(config)
        retry_engine = RetryEngine(config, sleep_fn=lambda s: None)

        # Load from queue
        queued = dispatcher.load_queue()
        assert len(queued) == 2

        # Create plan
        plan = dispatcher.create_plan(queued)
        assert plan.total_tasks == 2
        # Both should be in same group (independent, parallel_max=2)
        assert len(plan.parallel_groups) == 1
        assert len(plan.parallel_groups[0]) == 2

        # Execute with retry
        results = []
        for group in plan.parallel_groups:
            for dispatch_cmd in group:
                agent = dispatch_cmd.agent

                def dispatch_fn(t, a, attempt, is_fallback):
                    cmd = dispatcher.build_dispatch_command(t)
                    if is_fallback:
                        cmd.agent = a
                        cmd.command = dispatcher.build_command(t, a)
                    process_result = dispatcher.execute_command(cmd)
                    return collector.collect(cmd, process_result, attempt=attempt, is_fallback=is_fallback)

                result, log = retry_engine.execute_with_retry(dispatch_cmd.task, agent, dispatch_fn)
                results.append(result)

        # Verify results
        assert len(results) == 2
        assert all(r.is_success for r in results)

        # Verify state transitions
        state_dir = project_dir / ".agents" / "state"
        for task in tasks:
            state_file = state_dir / f"{task.id}.json"
            assert state_file.exists()

        # Verify results saved
        results_dir = project_dir / ".agents" / "results"
        assert len(list(results_dir.glob("*.json"))) == 2

        # Generate report
        reporter = Reporter(config)
        report_path = reporter.generate(results, title="E2E Parallel Test")
        assert report_path.exists()
        report_content = report_path.read_text(encoding="utf-8")
        assert "E2E Parallel Test" in report_content
        assert "Success | 2" in report_content


class TestE2EPipelineSequential:
    """Test pipeline with dependent tasks (sequential execution)."""

    @patch("scripts.agents.core.dispatcher.subprocess.run")
    def test_dependent_tasks_run_sequentially(self, mock_run, config, project_dir):
        """Task B depends on Task A — must run after A completes."""
        # Create tasks with dependency
        task_a = Task.create(
            title="Design API",
            task_type="design",
            prompt="Design the API interfaces",
        )
        queue_dir = Path(config.project_root) / config.paths.queue
        task_a.save(queue_dir)

        task_b = Task.create(
            title="Implement API",
            task_type="implementation",
            prompt="Implement the API",
            dependencies=[task_a.id],
        )
        task_b.save(queue_dir)

        # Mock
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"status": "success", "summary": "Done"}),
            stderr="",
        )

        # Dispatch
        dispatcher = Dispatcher(config)
        queued = dispatcher.load_queue()
        plan = dispatcher.create_plan(queued)

        # Should be 2 groups (sequential due to dependency)
        assert len(plan.parallel_groups) == 2
        assert plan.parallel_groups[0][0].task.id == task_a.id
        assert plan.parallel_groups[1][0].task.id == task_b.id


class TestE2ERetryFallback:
    """Test pipeline with retry and fallback scenarios."""

    @patch("scripts.agents.core.dispatcher.subprocess.run")
    def test_retry_then_fallback_succeeds(self, mock_run, config, project_dir):
        """Codex fails twice, then Claude (fallback) succeeds."""
        task = Task.create(
            title="Tricky implementation",
            task_type="implementation",
            prompt="Implement something difficult",
        )
        queue_dir = Path(config.project_root) / config.paths.queue
        task.save(queue_dir)

        call_count = [0]

        def side_effect(cmd, **kwargs):
            call_count[0] += 1
            cmd_str = " ".join(cmd)
            if call_count[0] <= 3:
                # First 3 calls (codex retries) fail
                return MagicMock(
                    returncode=0,
                    stdout=json.dumps({
                        "status": "fail",
                        "summary": "Failed attempt",
                        "errors": ["Cannot parse input"],
                    }),
                    stderr="",
                )
            else:
                # 4th call (claude fallback) succeeds
                return MagicMock(
                    returncode=0,
                    stdout=json.dumps({
                        "status": "success",
                        "summary": "Claude fallback succeeded",
                    }),
                    stderr="",
                )

        mock_run.side_effect = side_effect

        # Execute
        dispatcher = Dispatcher(config)
        collector = Collector(config)
        retry_engine = RetryEngine(config, sleep_fn=lambda s: None)

        agent = dispatcher.select_agent(task)
        assert agent.name == "codex"

        def dispatch_fn(t, agent_cfg, attempt, is_fallback):
            cmd = dispatcher.build_dispatch_command(t, is_fallback=is_fallback)
            if is_fallback:
                cmd.agent = agent_cfg
                cmd.command = dispatcher.build_command(t, agent_cfg)
            process_result = dispatcher.execute_command(cmd)
            return collector.collect(cmd, process_result, attempt=attempt, is_fallback=is_fallback)

        result, log = retry_engine.execute_with_retry(task, agent, dispatch_fn)

        # Should succeed via fallback
        assert result.is_success
        assert result.summary == "Claude fallback succeeded"
        assert log.final_agent == "claude"
        assert len(log.attempts) == 4  # 3 codex + 1 claude


class TestE2EFullPipelineFlow:
    """Test the complete flow from creation through reporting."""

    @patch("scripts.agents.core.dispatcher.subprocess.run")
    def test_create_dispatch_collect_report(self, mock_run, config, project_dir):
        """Full E2E: create 3 tasks -> dispatch -> collect -> validate -> report."""
        # Create 3 tasks
        tasks_data = [
            {"title": "Design module", "type": "design", "prompt": "Design it"},
            {"title": "Implement module", "type": "implementation", "prompt": "Build it"},
            {"title": "Review code", "type": "review", "prompt": "Review the code"},
        ]
        tasks = create_batch(tasks_data, config=config)

        # Verify queue
        queue_dir = project_dir / ".agents" / "queue"
        assert len(list(queue_dir.glob("*.json"))) == 3

        # Mock all subprocess calls as successful
        def side_effect(cmd, **kwargs):
            return MagicMock(
                returncode=0,
                stdout=json.dumps({
                    "status": "success",
                    "summary": "Task completed successfully",
                    "files_modified": [],
                    "files_created": [],
                }),
                stderr="",
            )

        mock_run.side_effect = side_effect

        # Dispatch all
        dispatcher = Dispatcher(config)
        collector = Collector(config)
        retry_engine = RetryEngine(config, sleep_fn=lambda s: None)

        queued = dispatcher.load_queue()
        plan = dispatcher.create_plan(queued)

        results = []
        for group in plan.parallel_groups:
            for dispatch_cmd in group:
                def dispatch_fn(t, a, attempt, is_fallback):
                    cmd = dispatcher.build_dispatch_command(t)
                    process_result = dispatcher.execute_command(cmd)
                    return collector.collect(cmd, process_result, attempt=attempt)

                result, _ = retry_engine.execute_with_retry(
                    dispatch_cmd.task, dispatch_cmd.agent, dispatch_fn
                )
                results.append(result)

        # All should succeed
        assert len(results) == 3
        assert all(r.is_success for r in results)

        # Results persisted
        results_dir = project_dir / ".agents" / "results"
        assert len(list(results_dir.glob("*.json"))) == 3

        # Generate report
        reporter = Reporter(config)
        report_path = reporter.generate(results, title="Full E2E Test")
        assert report_path.exists()

        content = report_path.read_text(encoding="utf-8")
        assert "Success | 3" in content
        assert "Full E2E Test" in content

        # JSON summary also created
        json_path = report_path.with_name(
            report_path.stem.replace("-report", "-summary") + ".json"
        )
        assert json_path.exists()
        summary = json.loads(json_path.read_text(encoding="utf-8"))
        assert summary["total_tasks"] == 3
        assert summary["status_counts"]["success"] == 3

    @patch("scripts.agents.core.dispatcher.subprocess.run")
    def test_mixed_results_pipeline(self, mock_run, config, project_dir):
        """Pipeline where some tasks succeed and some fail."""
        tasks_data = [
            {"title": "Good task", "type": "implementation", "prompt": "Build"},
            {"title": "Bad task", "type": "implementation", "prompt": "Build impossible thing"},
        ]
        tasks = create_batch(tasks_data, config=config)

        call_idx = [0]

        def side_effect(cmd, **kwargs):
            call_idx[0] += 1
            # First few calls succeed (good task), rest fail (bad task + retries)
            if call_idx[0] <= 1:
                return MagicMock(
                    returncode=0,
                    stdout=json.dumps({"status": "success", "summary": "Built it"}),
                    stderr="",
                )
            return MagicMock(
                returncode=0,
                stdout=json.dumps({
                    "status": "fail",
                    "summary": "Impossible task",
                    "errors": ["Cannot be done"],
                }),
                stderr="",
            )

        mock_run.side_effect = side_effect

        dispatcher = Dispatcher(config)
        collector = Collector(config)
        retry_engine = RetryEngine(config, sleep_fn=lambda s: None)

        queued = dispatcher.load_queue()
        plan = dispatcher.create_plan(queued)

        results = []
        for group in plan.parallel_groups:
            for dispatch_cmd in group:
                def dispatch_fn(t, a, attempt, is_fallback):
                    cmd = dispatcher.build_dispatch_command(t)
                    if is_fallback:
                        cmd.agent = a
                        cmd.command = dispatcher.build_command(t, a)
                    process_result = dispatcher.execute_command(cmd)
                    return collector.collect(cmd, process_result, attempt=attempt, is_fallback=is_fallback)

                result, _ = retry_engine.execute_with_retry(
                    dispatch_cmd.task, dispatch_cmd.agent, dispatch_fn
                )
                results.append(result)

        # Should have 1 success + 1 failure
        successes = [r for r in results if r.is_success]
        failures = [r for r in results if r.is_failure]
        assert len(successes) >= 1
        assert len(failures) >= 1

        # Report reflects mixed results
        reporter = Reporter(config)
        summary = reporter.generate_summary(results)
        assert summary["status_counts"].get("success", 0) >= 1
        assert summary["status_counts"].get("fail", 0) >= 1
