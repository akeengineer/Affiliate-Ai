"""Tests for the Concurrency Manager."""

import json
from pathlib import Path

import pytest

from scripts.agents.core.concurrency import AgentProcessManager, RunningProcess


@pytest.fixture
def state_dir(tmp_path):
    d = tmp_path / ".agents" / "state"
    d.mkdir(parents=True)
    return d


@pytest.fixture
def manager(state_dir):
    return AgentProcessManager(state_dir=state_dir)


class TestRegisterProcess:
    """Tests for registering processes."""

    def test_register_single(self, manager):
        manager.register_process("task-1", "term-1", "codex", "Build something")
        assert manager.is_any_running()
        assert manager.get_running_count() == 1

    def test_register_multiple(self, manager):
        manager.register_process("task-1", "term-1", "codex", "Task A")
        manager.register_process("task-2", "term-2", "claude", "Task B")
        assert manager.get_running_count() == 2

    def test_register_stores_details(self, manager):
        manager.register_process("task-1", "term-abc", "claude", "Design API")
        proc = manager.get_process("task-1")
        assert proc is not None
        assert proc.terminal_id == "term-abc"
        assert proc.agent_name == "claude"
        assert proc.task_title == "Design API"
        assert proc.started_at != ""


class TestMarkComplete:
    """Tests for marking processes complete."""

    def test_mark_complete_removes(self, manager):
        manager.register_process("task-1", "term-1", "codex", "Task")
        manager.mark_complete("task-1")
        assert not manager.is_any_running()
        assert manager.get_process("task-1") is None

    def test_mark_complete_unknown_is_safe(self, manager):
        manager.mark_complete("nonexistent")  # Should not raise

    def test_mark_failed_removes(self, manager):
        manager.register_process("task-1", "term-1", "codex", "Task")
        manager.mark_failed("task-1")
        assert not manager.is_any_running()


class TestGetRunningTasks:
    """Tests for querying running tasks."""

    def test_empty(self, manager):
        assert manager.get_running_tasks() == []

    def test_returns_all(self, manager):
        manager.register_process("task-1", "t1", "codex", "A")
        manager.register_process("task-2", "t2", "claude", "B")
        tasks = manager.get_running_tasks()
        assert len(tasks) == 2
        names = {t.agent_name for t in tasks}
        assert names == {"codex", "claude"}


class TestIsAnyRunning:
    """Tests for running status check."""

    def test_no_processes(self, manager):
        assert not manager.is_any_running()

    def test_with_process(self, manager):
        manager.register_process("task-1", "t1", "codex", "X")
        assert manager.is_any_running()

    def test_after_complete(self, manager):
        manager.register_process("task-1", "t1", "codex", "X")
        manager.mark_complete("task-1")
        assert not manager.is_any_running()


class TestPersistence:
    """Tests for state persistence to disk."""

    def test_persists_to_file(self, state_dir):
        mgr = AgentProcessManager(state_dir=state_dir)
        mgr.register_process("task-1", "t1", "codex", "Saved task")

        state_file = state_dir / "active_processes.json"
        assert state_file.exists()
        data = json.loads(state_file.read_text(encoding="utf-8"))
        assert "task-1" in data["processes"]

    def test_survives_reload(self, state_dir):
        mgr1 = AgentProcessManager(state_dir=state_dir)
        mgr1.register_process("task-1", "t1", "codex", "Persistent")

        # Create new manager (simulates new Kiro session)
        mgr2 = AgentProcessManager(state_dir=state_dir)
        assert mgr2.is_any_running()
        assert mgr2.get_process("task-1").task_title == "Persistent"

    def test_handles_corrupted_file(self, state_dir):
        state_file = state_dir / "active_processes.json"
        state_file.write_text("not valid json", encoding="utf-8")

        mgr = AgentProcessManager(state_dir=state_dir)
        assert not mgr.is_any_running()  # Should recover gracefully


class TestClearAll:
    """Tests for clearing all processes."""

    def test_clear(self, manager):
        manager.register_process("task-1", "t1", "codex", "A")
        manager.register_process("task-2", "t2", "claude", "B")
        manager.clear_all()
        assert not manager.is_any_running()
        assert manager.get_running_count() == 0


class TestGetRunningSummary:
    """Tests for the human-readable summary."""

    def test_no_running(self, manager):
        summary = manager.get_running_summary()
        assert "No agents" in summary

    def test_with_running(self, manager):
        manager.register_process("task-1", "t1", "codex", "Build scorer")
        summary = manager.get_running_summary()
        assert "1 agent" in summary
        assert "codex" in summary
        assert "Build scorer" in summary
