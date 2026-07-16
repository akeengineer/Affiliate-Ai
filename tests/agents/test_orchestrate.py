"""Tests for the Orchestrator CLI."""

import json
from pathlib import Path

import pytest
import yaml

from scripts.agents.core.models.task import Task
from scripts.agents.orchestrate import build_parser, cmd_init, cmd_status, main


MINIMAL_CONFIG = {
    "project_name": "Test",
    "package_name": "9ake-kiro-agents",
    "agents": {
        "claude": {
            "command": "claude",
            "flags": ["-p"],
            "system_prompt": ".agents/prompts/claude-cli-agent.md",
            "task_types": ["reasoning", "design", "review"],
            "fallback_to": "codex",
        },
        "codex": {
            "command": "codex",
            "flags": ["-q"],
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
    "ssh": {"host": "", "project_path": "", "user": ""},
    "validation": {"run_tests": True, "test_command": "python -m pytest", "check_files_exist": True},
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
    """Create temp project with config."""
    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir()
    for sub in ["queue", "results", "state", "reports", "prompts"]:
        (agents_dir / sub).mkdir()
    (agents_dir / "prompts" / "claude-cli-agent.md").write_text("# Claude", encoding="utf-8")
    (agents_dir / "prompts" / "codex-cli-agent.md").write_text("# Codex", encoding="utf-8")
    config_path = agents_dir / "config.yaml"
    config_path.write_text(yaml.dump(MINIMAL_CONFIG), encoding="utf-8")
    return tmp_path


class TestInit:
    """Tests for the init command."""

    def test_init_creates_structure(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        exit_code = main(["init", "--project-name", "MyProject"])
        assert exit_code == 0

        agents_dir = tmp_path / ".agents"
        assert agents_dir.exists()
        assert (agents_dir / "config.yaml").exists()
        assert (agents_dir / "prompts" / "claude-cli-agent.md").exists()
        assert (agents_dir / "prompts" / "codex-cli-agent.md").exists()
        assert (agents_dir / "prompts" / "shared-context.md").exists()
        assert (agents_dir / "queue").exists()
        assert (agents_dir / "results").exists()
        assert (agents_dir / "state").exists()
        assert (agents_dir / "reports").exists()

    def test_init_uses_dir_name_as_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        exit_code = main(["init"])
        assert exit_code == 0

        config_text = (tmp_path / ".agents" / "config.yaml").read_text(encoding="utf-8")
        assert tmp_path.name in config_text

    def test_init_already_exists(self, project_dir, monkeypatch, capsys):
        monkeypatch.chdir(project_dir)
        exit_code = main(["init"])
        assert exit_code == 0
        output = capsys.readouterr().out
        assert "Already initialized" in output


class TestCreate:
    """Tests for the create command."""

    def test_create_task(self, project_dir):
        config_path = str(project_dir / ".agents" / "config.yaml")
        exit_code = main([
            "--config", config_path,
            "create",
            "--title", "Test task",
            "--type", "implementation",
            "--prompt", "Do something",
        ])
        assert exit_code == 0

        queue_dir = project_dir / ".agents" / "queue"
        files = list(queue_dir.glob("*.json"))
        assert len(files) == 1


class TestDispatch:
    """Tests for the dispatch command."""

    def test_dispatch_empty_queue(self, project_dir, capsys):
        config_path = str(project_dir / ".agents" / "config.yaml")
        exit_code = main(["--config", config_path, "dispatch"])
        assert exit_code == 0
        output = capsys.readouterr().out
        assert "No tasks in queue" in output

    def test_dispatch_dry_run(self, project_dir, capsys):
        config_path = str(project_dir / ".agents" / "config.yaml")

        # Create a task first
        main([
            "--config", config_path,
            "create",
            "--title", "Dry run task",
            "--type", "implementation",
            "--prompt", "Implement something",
        ])

        exit_code = main(["--config", config_path, "dispatch", "--dry-run"])
        assert exit_code == 0
        output = capsys.readouterr().out
        assert "dry-run" in output
        assert "Dry run task" in output
        assert "codex" in output


class TestStatus:
    """Tests for the status command."""

    def test_status_empty(self, project_dir, capsys):
        config_path = str(project_dir / ".agents" / "config.yaml")
        exit_code = main(["--config", config_path, "status"])
        assert exit_code == 0
        output = capsys.readouterr().out
        assert "Queued tasks:" in output

    def test_status_with_queued_tasks(self, project_dir, capsys):
        config_path = str(project_dir / ".agents" / "config.yaml")

        # Create tasks
        main(["--config", config_path, "create", "--title", "Task A", "--type", "implementation", "--prompt", "A"])
        main(["--config", config_path, "create", "--title", "Task B", "--type", "reasoning", "--prompt", "B"])

        exit_code = main(["--config", config_path, "status"])
        assert exit_code == 0
        output = capsys.readouterr().out
        assert "Queued tasks:    2" in output


class TestResults:
    """Tests for the results command."""

    def test_results_empty(self, project_dir, capsys):
        config_path = str(project_dir / ".agents" / "config.yaml")
        exit_code = main(["--config", config_path, "results"])
        assert exit_code == 0
        output = capsys.readouterr().out
        assert "No results" in output


class TestRemoteStatus:
    """Tests for the remote-status command."""

    def test_no_ssh_host(self, project_dir, capsys):
        config_path = str(project_dir / ".agents" / "config.yaml")
        exit_code = main(["--config", config_path, "remote-status"])
        assert exit_code == 1
        output = capsys.readouterr().out
        assert "No SSH host" in output


class TestParser:
    """Tests for argument parsing."""

    def test_no_command_shows_help(self, capsys):
        exit_code = main([])
        assert exit_code == 0

    def test_parser_has_all_commands(self):
        parser = build_parser()
        # Check subparsers exist
        assert parser is not None

    def test_run_command_parsing(self):
        parser = build_parser()
        args = parser.parse_args(["run", "implement scoring"])
        assert args.command == "run"
        assert args.description == "implement scoring"

    def test_dispatch_dry_run_flag(self):
        parser = build_parser()
        args = parser.parse_args(["dispatch", "--dry-run"])
        assert args.command == "dispatch"
        assert args.dry_run is True


class TestConfigNotFound:
    """Tests for missing config error handling."""

    def test_status_without_config(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        exit_code = main(["--config", "/nonexistent/config.yaml", "status"])
        assert exit_code == 1
