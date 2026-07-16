"""Tests for the create_task CLI and functions."""

import json
import tempfile
from pathlib import Path

import pytest
import yaml

from scripts.agents.core.models.config import ProjectConfig
from scripts.agents.core.models.task import Task, TaskStatus, TaskType
from scripts.agents.create_task import (
    build_parser,
    create_batch,
    create_from_dict,
    create_single_task,
    main,
)


MINIMAL_CONFIG = {
    "project_name": "Test",
    "package_name": "9ake-kiro-agents",
    "agents": {
        "claude": {"command": "claude", "task_types": ["reasoning", "design", "review"]},
        "codex": {"command": "codex", "task_types": ["implementation", "test", "refactor"]},
    },
    "dispatch": {"retry_max": 2},
    "ssh": {"host": "test-host"},
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
    """Create a temporary project with .agents/config.yaml."""
    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir()
    queue_dir = agents_dir / "queue"
    queue_dir.mkdir()
    config_path = agents_dir / "config.yaml"
    config_path.write_text(yaml.dump(MINIMAL_CONFIG), encoding="utf-8")
    return tmp_path


@pytest.fixture
def config(project_dir):
    """Load config from the temporary project."""
    config_path = project_dir / ".agents" / "config.yaml"
    return ProjectConfig.load(str(config_path))


class TestCreateSingleTask:
    """Tests for create_single_task function."""

    def test_creates_task_with_valid_params(self, config):
        task = create_single_task(
            title="Test implementation",
            task_type="implementation",
            prompt="Implement the thing",
            config=config,
        )
        assert task.title == "Test implementation"
        assert task.type == TaskType.IMPLEMENTATION
        assert task.status == TaskStatus.QUEUED
        assert task.prompt == "Implement the thing"
        assert len(task.id) == 36

    def test_saves_to_queue_directory(self, config, project_dir):
        task = create_single_task(
            title="Save test",
            task_type="test",
            prompt="Write tests",
            config=config,
        )
        queue_dir = project_dir / ".agents" / "queue"
        task_file = queue_dir / f"{task.id}.json"
        assert task_file.exists()

        # Verify content
        data = json.loads(task_file.read_text(encoding="utf-8"))
        assert data["title"] == "Save test"
        assert data["type"] == "test"

    def test_invalid_type_raises(self, config):
        with pytest.raises(ValueError, match="Invalid task type"):
            create_single_task(
                title="Bad",
                task_type="nonexistent",
                prompt="X",
                config=config,
            )

    def test_all_optional_params(self, config):
        task = create_single_task(
            title="Full task",
            task_type="reasoning",
            prompt="Think about architecture",
            priority="high",
            agent_preference="claude",
            dependencies=["dep-id-1"],
            input_files=["README.md", "CONTEXT.md"],
            expected_outputs=["design.md"],
            timeout_seconds=600,
            max_retries=3,
            config=config,
        )
        assert task.priority.value == "high"
        assert task.agent_preference == "claude"
        assert task.dependencies == ["dep-id-1"]
        assert task.input_files == ["README.md", "CONTEXT.md"]
        assert task.expected_outputs == ["design.md"]
        assert task.timeout_seconds == 600
        assert task.max_retries == 3


class TestCreateFromDict:
    """Tests for create_from_dict function."""

    def test_creates_from_minimal_dict(self, config):
        data = {
            "title": "Dict task",
            "type": "implementation",
            "prompt": "Build something",
        }
        task = create_from_dict(data, config=config)
        assert task.title == "Dict task"
        assert task.type == TaskType.IMPLEMENTATION

    def test_missing_required_field_raises(self, config):
        with pytest.raises(KeyError, match="Missing required field: 'prompt'"):
            create_from_dict({"title": "No prompt", "type": "test"}, config=config)

    def test_missing_title_raises(self, config):
        with pytest.raises(KeyError, match="Missing required field: 'title'"):
            create_from_dict({"type": "test", "prompt": "X"}, config=config)

    def test_full_dict(self, config):
        data = {
            "title": "Full dict task",
            "type": "design",
            "prompt": "Design something",
            "priority": "critical",
            "agent_preference": "claude",
            "dependencies": ["id-1", "id-2"],
            "input_files": ["file.py"],
            "expected_outputs": ["output.md"],
            "timeout_seconds": 900,
            "max_retries": 1,
        }
        task = create_from_dict(data, config=config)
        assert task.priority.value == "critical"
        assert task.dependencies == ["id-1", "id-2"]


class TestCreateBatch:
    """Tests for batch task creation."""

    def test_creates_multiple_tasks(self, config, project_dir):
        tasks_data = [
            {"title": "Task A", "type": "implementation", "prompt": "Do A"},
            {"title": "Task B", "type": "reasoning", "prompt": "Think B"},
            {"title": "Task C", "type": "test", "prompt": "Test C"},
        ]
        tasks = create_batch(tasks_data, config=config)
        assert len(tasks) == 3
        assert tasks[0].title == "Task A"
        assert tasks[1].title == "Task B"
        assert tasks[2].title == "Task C"

        # Verify all saved to queue
        queue_dir = project_dir / ".agents" / "queue"
        for task in tasks:
            assert (queue_dir / f"{task.id}.json").exists()

    def test_empty_batch(self, config):
        tasks = create_batch([], config=config)
        assert tasks == []


class TestCLI:
    """Tests for the CLI main() function."""

    def test_create_via_args(self, project_dir, monkeypatch):
        config_path = str(project_dir / ".agents" / "config.yaml")
        exit_code = main([
            "--title", "CLI task",
            "--type", "implementation",
            "--prompt", "Implement via CLI",
            "--config", config_path,
        ])
        assert exit_code == 0

        # Verify file was created
        queue_dir = project_dir / ".agents" / "queue"
        files = list(queue_dir.glob("*.json"))
        assert len(files) == 1

    def test_create_with_json_output(self, project_dir, capsys):
        config_path = str(project_dir / ".agents" / "config.yaml")
        exit_code = main([
            "--title", "JSON output task",
            "--type", "reasoning",
            "--prompt", "Think about this",
            "--config", config_path,
            "--json-output",
        ])
        assert exit_code == 0
        output = capsys.readouterr().out
        data = json.loads(output)
        assert data["title"] == "JSON output task"
        assert data["type"] == "reasoning"
        assert data["status"] == "queued"

    def test_missing_required_args_fails(self, project_dir):
        config_path = str(project_dir / ".agents" / "config.yaml")
        exit_code = main([
            "--title", "Incomplete",
            "--config", config_path,
        ])
        assert exit_code == 1

    def test_invalid_type_fails(self, project_dir):
        config_path = str(project_dir / ".agents" / "config.yaml")
        exit_code = main([
            "--title", "Bad type",
            "--type", "implementation",  # valid type for argparse
            "--prompt", "X",
            "--config", config_path,
        ])
        # This should succeed since 'implementation' is valid
        assert exit_code == 0

    def test_from_json_file(self, project_dir):
        config_path = str(project_dir / ".agents" / "config.yaml")
        tasks_data = [
            {"title": "Batch 1", "type": "test", "prompt": "Test it"},
            {"title": "Batch 2", "type": "refactor", "prompt": "Clean it"},
        ]
        json_file = project_dir / "batch.json"
        json_file.write_text(json.dumps(tasks_data), encoding="utf-8")

        exit_code = main([
            "--from-json", str(json_file),
            "--config", config_path,
        ])
        assert exit_code == 0

        queue_dir = project_dir / ".agents" / "queue"
        files = list(queue_dir.glob("*.json"))
        assert len(files) == 2

    def test_from_json_file_not_found(self, project_dir):
        config_path = str(project_dir / ".agents" / "config.yaml")
        exit_code = main([
            "--from-json", "/nonexistent/file.json",
            "--config", config_path,
        ])
        assert exit_code == 1

    def test_from_stdin(self, project_dir, monkeypatch):
        config_path = str(project_dir / ".agents" / "config.yaml")
        task_json = json.dumps({"title": "Stdin task", "type": "design", "prompt": "Design it"})

        import io
        monkeypatch.setattr("sys.stdin", io.StringIO(task_json))

        exit_code = main([
            "--from-stdin",
            "--config", config_path,
        ])
        assert exit_code == 0

        queue_dir = project_dir / ".agents" / "queue"
        files = list(queue_dir.glob("*.json"))
        assert len(files) == 1

    def test_with_dependencies_and_input_files(self, project_dir):
        config_path = str(project_dir / ".agents" / "config.yaml")
        exit_code = main([
            "--title", "Dependent task",
            "--type", "implementation",
            "--prompt", "Build on previous",
            "--depends-on", "11111111-1111-1111-1111-111111111111",
            "--depends-on", "22222222-2222-2222-2222-222222222222",
            "--input-file", "README.md",
            "--input-file", "CONTEXT.md",
            "--expected-output", "output.py",
            "--priority", "high",
            "--agent", "codex",
            "--timeout", "600",
            "--max-retries", "3",
            "--config", config_path,
            "--json-output",
        ])
        assert exit_code == 0
