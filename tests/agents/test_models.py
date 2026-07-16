"""Tests for Task and AgentResult models."""

import json
import tempfile
from pathlib import Path

import pytest

from scripts.agents.core.models.result import AgentResult, ResultStatus
from scripts.agents.core.models.task import Task, TaskPriority, TaskStatus, TaskType


class TestTask:
    """Tests for the Task model."""

    def test_create_generates_uuid_and_timestamp(self):
        task = Task.create(
            title="Test task",
            task_type="implementation",
            prompt="Do something",
        )
        assert len(task.id) == 36  # UUID format
        assert task.title == "Test task"
        assert task.type == TaskType.IMPLEMENTATION
        assert task.status == TaskStatus.QUEUED
        assert task.prompt == "Do something"
        assert task.created_at != ""

    def test_create_with_all_fields(self):
        task = Task.create(
            title="Full task",
            task_type="reasoning",
            prompt="Think about this",
            priority="high",
            agent_preference="claude",
            dependencies=["abc-123"],
            input_files=["README.md"],
            expected_outputs=["output.json"],
            timeout_seconds=600,
            max_retries=3,
            metadata={"source": "test"},
        )
        assert task.priority == TaskPriority.HIGH
        assert task.agent_preference == "claude"
        assert task.dependencies == ["abc-123"]
        assert task.input_files == ["README.md"]
        assert task.expected_outputs == ["output.json"]
        assert task.timeout_seconds == 600
        assert task.max_retries == 3
        assert task.metadata == {"source": "test"}

    def test_serialization_roundtrip(self):
        task = Task.create(
            title="Roundtrip test",
            task_type="design",
            prompt="Design an interface",
        )
        json_str = task.to_json()
        restored = Task.from_json(json_str)
        assert restored.id == task.id
        assert restored.title == task.title
        assert restored.type == task.type
        assert restored.status == task.status
        assert restored.prompt == task.prompt
        assert restored.created_at == task.created_at

    def test_to_dict_has_string_enums(self):
        task = Task.create(title="Dict test", task_type="review", prompt="Review code")
        d = task.to_dict()
        assert d["type"] == "review"
        assert d["status"] == "queued"
        assert d["priority"] == "medium"

    def test_from_dict_with_string_enums(self):
        data = {
            "id": "12345678-1234-1234-1234-123456789abc",
            "title": "From dict",
            "type": "test",
            "status": "active",
            "prompt": "Run tests",
            "created_at": "2024-01-01T00:00:00+00:00",
        }
        task = Task.from_dict(data)
        assert task.type == TaskType.TEST
        assert task.status == TaskStatus.ACTIVE

    def test_save_and_load(self):
        task = Task.create(title="Save test", task_type="implementation", prompt="Build it")
        with tempfile.TemporaryDirectory() as tmpdir:
            path = task.save(Path(tmpdir))
            assert path.exists()
            loaded = Task.load(path)
            assert loaded.id == task.id
            assert loaded.title == task.title

    def test_status_transitions(self):
        task = Task.create(title="Transition", task_type="implementation", prompt="Go")
        assert task.is_ready
        assert not task.is_terminal

        task.mark_active()
        assert task.status == TaskStatus.ACTIVE
        assert task.started_at is not None

        task.mark_completed()
        assert task.status == TaskStatus.COMPLETED
        assert task.completed_at is not None
        assert task.is_terminal

    def test_mark_failed(self):
        task = Task.create(title="Fail", task_type="implementation", prompt="Fail")
        task.mark_active()
        task.mark_failed()
        assert task.status == TaskStatus.FAILED
        assert task.is_terminal

    def test_mark_retrying(self):
        task = Task.create(title="Retry", task_type="implementation", prompt="Retry")
        task.mark_retrying()
        assert task.status == TaskStatus.RETRYING
        assert not task.is_terminal

    def test_invalid_task_type_raises(self):
        with pytest.raises(ValueError):
            Task.create(title="Bad", task_type="invalid_type", prompt="X")

    def test_invalid_priority_raises(self):
        with pytest.raises(ValueError):
            Task.create(title="Bad", task_type="implementation", prompt="X", priority="ultra")


class TestAgentResult:
    """Tests for the AgentResult model."""

    def test_create_with_defaults(self):
        result = AgentResult.create(
            task_id="12345678-1234-1234-1234-123456789abc",
            agent="claude",
            status="success",
            summary="Did the thing",
        )
        assert result.task_id == "12345678-1234-1234-1234-123456789abc"
        assert result.agent == "claude"
        assert result.status == ResultStatus.SUCCESS
        assert result.summary == "Did the thing"
        assert result.completed_at != ""
        assert result.attempt == 1
        assert result.is_fallback is False
        assert result.is_success

    def test_create_failure(self):
        result = AgentResult.create(
            task_id="12345678-1234-1234-1234-123456789abc",
            agent="codex",
            status="fail",
            summary="Could not complete",
            errors=["File not found: input.md"],
            attempt=2,
            is_fallback=True,
        )
        assert result.status == ResultStatus.FAIL
        assert result.is_failure
        assert result.is_retriable
        assert result.errors == ["File not found: input.md"]
        assert result.attempt == 2
        assert result.is_fallback

    def test_serialization_roundtrip(self):
        result = AgentResult.create(
            task_id="12345678-1234-1234-1234-123456789abc",
            agent="codex",
            status="success",
            summary="All good",
            files_modified=["main.py"],
            files_created=["test_main.py"],
            tests_run="pytest",
            tests_passed=True,
            duration_seconds=12.5,
        )
        json_str = result.to_json()
        restored = AgentResult.from_json(json_str)
        assert restored.task_id == result.task_id
        assert restored.agent == result.agent
        assert restored.status == result.status
        assert restored.files_modified == ["main.py"]
        assert restored.tests_passed is True
        assert restored.duration_seconds == 12.5

    def test_save_and_load(self):
        result = AgentResult.create(
            task_id="12345678-1234-1234-1234-123456789abc",
            agent="claude",
            status="partial",
            summary="Partial result",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            path = result.save(Path(tmpdir))
            assert path.exists()
            loaded = AgentResult.load(path)
            assert loaded.task_id == result.task_id
            assert loaded.status == ResultStatus.PARTIAL

    def test_timeout_is_retriable(self):
        result = AgentResult.create(
            task_id="12345678-1234-1234-1234-123456789abc",
            agent="codex",
            status="timeout",
            summary="Timed out",
        )
        assert result.status == ResultStatus.TIMEOUT
        assert result.is_failure
        assert result.is_retriable

    def test_to_dict_has_string_enum(self):
        result = AgentResult.create(
            task_id="12345678-1234-1234-1234-123456789abc",
            agent="claude",
            status="success",
            summary="OK",
        )
        d = result.to_dict()
        assert d["status"] == "success"
        assert isinstance(d["status"], str)
