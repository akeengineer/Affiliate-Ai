"""Tests for the Kiro Dispatch Helper script."""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from scripts.agents.kiro_dispatch import (
    RESULT_MARKER,
    build_agent_command,
    create_result,
    execute_agent,
    main,
    parse_agent_output,
)
from scripts.agents.core.models.config import AgentConfig, ProjectConfig


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
    "dispatch": {"retry_max": 2, "parallel_max": 2},
    "ssh": {"host": "god-of-ai", "project_path": "/home/ubuntu/Affiliate-Ai", "user": "ubuntu"},
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
    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir()
    for sub in ["queue", "results", "state", "prompts"]:
        (agents_dir / sub).mkdir()
    (agents_dir / "prompts" / "claude-cli-agent.md").write_text("# Claude", encoding="utf-8")
    (agents_dir / "prompts" / "codex-cli-agent.md").write_text("# Codex", encoding="utf-8")
    config_path = agents_dir / "config.yaml"
    config_path.write_text(yaml.dump(MINIMAL_CONFIG), encoding="utf-8")
    return tmp_path


@pytest.fixture
def config(project_dir):
    return ProjectConfig.load(str(project_dir / ".agents" / "config.yaml"))


class TestBuildAgentCommand:
    """Tests for command construction."""

    def test_codex_command(self, config, project_dir):
        agent = config.get_agent("codex")
        cmd = build_agent_command(agent, "Build it", "task-123", "implementation", project_dir)
        assert cmd[0] == "codex"
        assert "-q" in cmd
        assert "--approval-mode" in cmd
        assert "TASK_ID: task-123" in cmd[-1]
        assert "Build it" in cmd[-1]

    def test_claude_command(self, config, project_dir):
        agent = config.get_agent("claude")
        cmd = build_agent_command(agent, "Design it", "task-456", "design", project_dir)
        assert cmd[0] == "claude"
        assert "-p" in cmd
        assert "--system-prompt-file" in cmd
        assert "--max-turns" in cmd
        assert "10" in cmd
        assert "TASK_ID: task-456" in cmd[-1]

    def test_prompt_includes_json_instruction(self, config, project_dir):
        agent = config.get_agent("codex")
        cmd = build_agent_command(agent, "Do X", "id", "implementation", project_dir)
        assert "Return your result as JSON" in cmd[-1]


class TestParseAgentOutput:
    """Tests for output parsing."""

    def test_parse_valid_json(self):
        output = json.dumps({"status": "success", "summary": "Done"})
        result = parse_agent_output(output)
        assert result == {"status": "success", "summary": "Done"}

    def test_parse_json_in_text(self):
        output = 'Some text\n{"status": "success"}\nMore text'
        result = parse_agent_output(output)
        assert result["status"] == "success"

    def test_parse_empty(self):
        assert parse_agent_output("") is None
        assert parse_agent_output("   ") is None

    def test_parse_invalid_json(self):
        assert parse_agent_output("not json at all") is None

    def test_parse_array_returns_none(self):
        assert parse_agent_output("[1, 2, 3]") is None


class TestCreateResult:
    """Tests for result creation from execution output."""

    def test_success_with_json(self):
        stdout = json.dumps({
            "status": "success",
            "summary": "Created file",
            "files_created": ["main.py"],
        })
        result = create_result("id-1", "codex", 0, stdout, "", 5.0)
        assert result["status"] == "success"
        assert result["summary"] == "Created file"
        assert result["files_created"] == ["main.py"]
        assert result["duration_seconds"] == 5.0

    def test_timeout(self):
        result = create_result("id-2", "codex", -1, "", "TIMEOUT: exceeded 300s", 300.0)
        assert result["status"] == "timeout"
        assert "timed out" in result["summary"]

    def test_command_not_found(self):
        result = create_result("id-3", "codex", 127, "", "not found", 0.1)
        assert result["status"] == "fail"
        assert "not found" in result["summary"]

    def test_nonzero_exit(self):
        result = create_result("id-4", "claude", 1, "", "error occurred", 2.0)
        assert result["status"] == "fail"
        assert "code 1" in result["summary"]

    def test_unstructured_output(self):
        result = create_result("id-5", "codex", 0, "I did stuff but no JSON", "", 10.0)
        assert result["status"] == "partial"
        assert "not valid JSON" in result["errors"][0]


class TestExecuteAgent:
    """Tests for agent execution."""

    @patch("scripts.agents.kiro_dispatch.subprocess.run")
    def test_successful_execution(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="OK", stderr="")
        rc, stdout, stderr, dur = execute_agent(["echo", "test"], 60, ".")
        assert rc == 0
        assert stdout == "OK"

    @patch("scripts.agents.kiro_dispatch.subprocess.run")
    def test_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="test", timeout=60)
        rc, stdout, stderr, dur = execute_agent(["slow"], 60, ".")
        assert rc == -1
        assert "TIMEOUT" in stderr

    @patch("scripts.agents.kiro_dispatch.subprocess.run")
    def test_command_not_found(self, mock_run):
        mock_run.side_effect = FileNotFoundError("not found")
        rc, stdout, stderr, dur = execute_agent(["noexist"], 60, ".")
        assert rc == 127
        assert "not found" in stderr


class TestMainCLI:
    """Tests for the main CLI function."""

    @patch("scripts.agents.kiro_dispatch.execute_agent")
    def test_main_success(self, mock_exec, project_dir, capsys):
        mock_exec.return_value = (
            0,
            json.dumps({"status": "success", "summary": "Done"}),
            "",
            5.0,
        )
        config_path = str(project_dir / ".agents" / "config.yaml")
        exit_code = main([
            "--agent", "codex",
            "--type", "implementation",
            "--prompt", "Build something",
            "--config", config_path,
        ])
        assert exit_code == 0
        output = capsys.readouterr().out
        assert RESULT_MARKER in output
        # Parse result after marker
        parts = output.split(RESULT_MARKER)
        result = json.loads(parts[1].strip())
        assert result["status"] == "success"

    @patch("scripts.agents.kiro_dispatch.execute_agent")
    def test_main_failure(self, mock_exec, project_dir, capsys):
        mock_exec.return_value = (1, "", "error", 2.0)
        config_path = str(project_dir / ".agents" / "config.yaml")
        exit_code = main([
            "--agent", "codex",
            "--type", "implementation",
            "--prompt", "Bad task",
            "--config", config_path,
        ])
        assert exit_code == 1
        output = capsys.readouterr().out
        assert RESULT_MARKER in output

    @patch("scripts.agents.kiro_dispatch.execute_agent")
    def test_result_saved_to_disk(self, mock_exec, project_dir):
        mock_exec.return_value = (
            0,
            json.dumps({"status": "success", "summary": "Saved"}),
            "",
            3.0,
        )
        config_path = str(project_dir / ".agents" / "config.yaml")
        main([
            "--agent", "codex",
            "--type", "implementation",
            "--prompt", "Build",
            "--config", config_path,
            "--task-id", "test-save-id",
        ])
        result_path = project_dir / ".agents" / "results" / "test-save-id.json"
        assert result_path.exists()

    def test_remote_no_ssh_host(self, tmp_path, capsys):
        # Config without SSH host
        agents_dir = tmp_path / ".agents"
        agents_dir.mkdir()
        (agents_dir / "results").mkdir()
        no_ssh_config = dict(MINIMAL_CONFIG)
        no_ssh_config["ssh"] = {"host": "", "project_path": "", "user": ""}
        (agents_dir / "config.yaml").write_text(yaml.dump(no_ssh_config), encoding="utf-8")

        exit_code = main([
            "--agent", "codex",
            "--type", "implementation",
            "--prompt", "Remote task",
            "--remote",
            "--config", str(agents_dir / "config.yaml"),
        ])
        assert exit_code == 1
        output = capsys.readouterr().out
        assert "No SSH host" in output or "fail" in output
