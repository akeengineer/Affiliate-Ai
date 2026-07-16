"""Tests for the Retry and Fallback Engine."""

import json
from pathlib import Path
from typing import List

import pytest
import yaml

from scripts.agents.core.models.config import AgentConfig, ProjectConfig
from scripts.agents.core.models.result import AgentResult, ResultStatus
from scripts.agents.core.models.task import Task, TaskStatus
from scripts.agents.core.retry import RetryAttempt, RetryEngine, RetryLog


MINIMAL_CONFIG = {
    "project_name": "Test",
    "package_name": "9ake-kiro-agents",
    "agents": {
        "claude": {
            "command": "claude",
            "flags": ["-p"],
            "task_types": ["reasoning", "design", "review"],
            "fallback_to": "codex",
        },
        "codex": {
            "command": "codex",
            "flags": ["-q"],
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
    "ssh": {"host": "test"},
    "validation": {"run_tests": True},
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
    """Create temp project."""
    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir()
    for sub in ["queue", "results", "state"]:
        (agents_dir / sub).mkdir()
    config_path = agents_dir / "config.yaml"
    config_path.write_text(yaml.dump(MINIMAL_CONFIG), encoding="utf-8")
    return tmp_path


@pytest.fixture
def config(project_dir):
    return ProjectConfig.load(str(project_dir / ".agents" / "config.yaml"))


@pytest.fixture
def engine(config):
    """Create retry engine with instant sleep (no real waiting)."""
    sleep_calls: List[float] = []

    def fake_sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    eng = RetryEngine(config, sleep_fn=fake_sleep)
    eng._sleep_calls = sleep_calls  # type: ignore[attr-defined]
    return eng


def make_task() -> Task:
    return Task.create(
        title="Retry test",
        task_type="implementation",
        prompt="Build something",
        max_retries=2,
    )


def make_result(status: str = "success", errors: list = None) -> AgentResult:
    return AgentResult.create(
        task_id="test-id",
        agent="codex",
        status=status,
        summary=f"Status: {status}",
        errors=errors or [],
    )


class TestSuccessOnFirstTry:
    """Tests for immediate success (no retry needed)."""

    def test_returns_success_immediately(self, engine, config):
        task = make_task()
        agent = config.get_agent("codex")

        def dispatch_fn(t, a, attempt, is_fallback):
            return AgentResult.create(
                task_id=t.id, agent=a.name, status="success", summary="Done"
            )

        result, log = engine.execute_with_retry(task, agent, dispatch_fn)
        assert result.is_success
        assert len(log.attempts) == 1
        assert log.final_status == "success"
        assert log.final_agent == "codex"

    def test_no_sleep_on_first_success(self, engine, config):
        task = make_task()
        agent = config.get_agent("codex")

        def dispatch_fn(t, a, attempt, is_fallback):
            return AgentResult.create(
                task_id=t.id, agent=a.name, status="success", summary="Done"
            )

        engine.execute_with_retry(task, agent, dispatch_fn)
        assert engine._sleep_calls == []  # type: ignore[attr-defined]


class TestRetryOnFailure:
    """Tests for retry behavior."""

    def test_retries_on_failure_then_succeeds(self, engine, config):
        task = make_task()
        agent = config.get_agent("codex")
        call_count = [0]

        def dispatch_fn(t, a, attempt, is_fallback):
            call_count[0] += 1
            if call_count[0] < 3:
                return AgentResult.create(
                    task_id=t.id, agent=a.name, status="fail",
                    summary="Failed", errors=["Error"]
                )
            return AgentResult.create(
                task_id=t.id, agent=a.name, status="success", summary="OK"
            )

        result, log = engine.execute_with_retry(task, agent, dispatch_fn)
        assert result.is_success
        assert len(log.attempts) == 3  # 1 initial + 2 retries
        assert log.final_status == "success"

    def test_uses_backoff_between_retries(self, engine, config):
        task = make_task()
        agent = config.get_agent("codex")
        call_count = [0]

        def dispatch_fn(t, a, attempt, is_fallback):
            call_count[0] += 1
            if call_count[0] <= 3:
                return AgentResult.create(
                    task_id=t.id, agent=a.name, status="fail",
                    summary="Failed", errors=["Error"]
                )
            return AgentResult.create(
                task_id=t.id, agent=a.name, status="success", summary="OK"
            )

        engine.execute_with_retry(task, agent, dispatch_fn)
        # Should have slept between retries: [5, 15]
        assert engine._sleep_calls == [5, 15]  # type: ignore[attr-defined]

    def test_respects_max_retries(self, engine, config):
        task = make_task()  # max_retries=2
        agent = config.get_agent("codex")

        def dispatch_fn(t, a, attempt, is_fallback):
            return AgentResult.create(
                task_id=t.id, agent=a.name, status="fail",
                summary="Always fails", errors=["Nope"]
            )

        result, log = engine.execute_with_retry(task, agent, dispatch_fn)
        # 1 initial + 2 retries = 3 attempts for primary, then 1 fallback
        primary_attempts = [a for a in log.attempts if not a.is_fallback]
        assert len(primary_attempts) == 3

    def test_timeout_is_retriable(self, engine, config):
        task = make_task()
        agent = config.get_agent("codex")
        call_count = [0]

        def dispatch_fn(t, a, attempt, is_fallback):
            call_count[0] += 1
            if call_count[0] == 1:
                return AgentResult.create(
                    task_id=t.id, agent=a.name, status="timeout",
                    summary="Timed out", errors=["TIMEOUT"]
                )
            return AgentResult.create(
                task_id=t.id, agent=a.name, status="success", summary="OK"
            )

        result, log = engine.execute_with_retry(task, agent, dispatch_fn)
        assert result.is_success
        assert len(log.attempts) == 2


class TestFallback:
    """Tests for cross-agent fallback."""

    def test_falls_back_to_other_agent(self, engine, config):
        task = make_task()
        agent = config.get_agent("codex")

        def dispatch_fn(t, a, attempt, is_fallback):
            if a.name == "codex":
                return AgentResult.create(
                    task_id=t.id, agent=a.name, status="fail",
                    summary="Codex failed", errors=["Error"]
                )
            return AgentResult.create(
                task_id=t.id, agent=a.name, status="success",
                summary="Claude saved the day"
            )

        result, log = engine.execute_with_retry(task, agent, dispatch_fn)
        assert result.is_success
        assert result.summary == "Claude saved the day"
        assert log.final_agent == "claude"
        # Should have fallback attempt
        fallback_attempts = [a for a in log.attempts if a.is_fallback]
        assert len(fallback_attempts) == 1

    def test_fallback_also_fails(self, engine, config):
        task = make_task()
        agent = config.get_agent("codex")

        def dispatch_fn(t, a, attempt, is_fallback):
            return AgentResult.create(
                task_id=t.id, agent=a.name, status="fail",
                summary=f"{a.name} failed", errors=["Error"]
            )

        result, log = engine.execute_with_retry(task, agent, dispatch_fn)
        assert result.is_failure
        assert log.final_agent == "claude"  # fallback agent
        # 3 primary (codex) + 1 fallback (claude) = 4
        assert len(log.attempts) == 4

    def test_fallback_disabled(self, config):
        # Disable fallback in config
        config.dispatch.fallback_enabled = False
        engine = RetryEngine(config, sleep_fn=lambda s: None)
        task = make_task()
        agent = config.get_agent("codex")

        def dispatch_fn(t, a, attempt, is_fallback):
            return AgentResult.create(
                task_id=t.id, agent=a.name, status="fail",
                summary="Failed", errors=["Error"]
            )

        result, log = engine.execute_with_retry(task, agent, dispatch_fn)
        assert result.is_failure
        # Only primary attempts, no fallback
        assert all(not a.is_fallback for a in log.attempts)
        assert len(log.attempts) == 3  # 1 + 2 retries

    def test_no_fallback_agent_configured(self, config):
        # Remove fallback_to
        config.agents["codex"].fallback_to = None
        engine = RetryEngine(config, sleep_fn=lambda s: None)
        task = make_task()
        agent = config.get_agent("codex")

        def dispatch_fn(t, a, attempt, is_fallback):
            return AgentResult.create(
                task_id=t.id, agent=a.name, status="fail",
                summary="Failed", errors=["Error"]
            )

        result, log = engine.execute_with_retry(task, agent, dispatch_fn)
        assert result.is_failure
        assert log.final_agent == "codex"


class TestRetryLog:
    """Tests for retry log persistence."""

    def test_log_saved_to_disk(self, engine, config, project_dir):
        task = make_task()
        agent = config.get_agent("codex")

        def dispatch_fn(t, a, attempt, is_fallback):
            return AgentResult.create(
                task_id=t.id, agent=a.name, status="success", summary="OK"
            )

        result, log = engine.execute_with_retry(task, agent, dispatch_fn)

        log_path = project_dir / ".agents" / "state" / "retries" / f"{task.id}.json"
        assert log_path.exists()
        data = json.loads(log_path.read_text(encoding="utf-8"))
        assert data["task_id"] == task.id
        assert len(data["attempts"]) == 1

    def test_log_records_all_attempts(self, engine, config, project_dir):
        task = make_task()
        agent = config.get_agent("codex")
        call_count = [0]

        def dispatch_fn(t, a, attempt, is_fallback):
            call_count[0] += 1
            if not is_fallback:
                return AgentResult.create(
                    task_id=t.id, agent=a.name, status="fail",
                    summary="Failed", errors=["Err"]
                )
            return AgentResult.create(
                task_id=t.id, agent=a.name, status="success", summary="Fallback OK"
            )

        result, log = engine.execute_with_retry(task, agent, dispatch_fn)

        log_path = project_dir / ".agents" / "state" / "retries" / f"{task.id}.json"
        data = json.loads(log_path.read_text(encoding="utf-8"))
        assert len(data["attempts"]) == 4  # 3 primary + 1 fallback
        assert data["final_status"] == "success"
        assert data["final_agent"] == "claude"


class TestFallbackPromptPrefix:
    """Tests for the fallback prompt helper."""

    def test_builds_prefix_with_errors(self):
        prefix = RetryEngine.build_fallback_prompt_prefix(["File not found", "Timeout"])
        assert "previous agent attempted" in prefix.lower()
        assert "File not found" in prefix
        assert "Timeout" in prefix
        assert "different approach" in prefix

    def test_builds_prefix_with_empty_errors(self):
        prefix = RetryEngine.build_fallback_prompt_prefix([])
        assert "Unknown error" in prefix
