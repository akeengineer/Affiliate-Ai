"""Tests for the ProjectConfig loader."""

import tempfile
from pathlib import Path

import pytest

from scripts.agents.core.models.config import (
    AgentConfig,
    DispatchConfig,
    PathsConfig,
    ProjectConfig,
    SSHConfig,
    ValidationConfig,
)


SAMPLE_CONFIG = """\
project_name: "Test Project"
package_name: "9ake-kiro-agents"

agents:
  claude:
    command: "claude"
    flags:
      - "-p"
      - "--dangerously-skip-permissions"
      - "--output-format"
      - "json"
    system_prompt: ".agents/prompts/claude-cli-agent.md"
    max_turns: 10
    max_budget_usd: 5.00
    task_types:
      - "reasoning"
      - "design"
      - "review"
    fallback_to: "codex"

  codex:
    command: "codex"
    flags:
      - "-q"
      - "--approval-mode"
      - "full-auto"
    system_prompt: ".agents/prompts/codex-cli-agent.md"
    task_types:
      - "implementation"
      - "test"
      - "refactor"
    fallback_to: "claude"

dispatch:
  retry_max: 3
  retry_backoff_seconds:
    - 5
    - 15
    - 30
  fallback_enabled: true
  parallel_max: 4
  default_timeout_seconds: 600

ssh:
  host: "my-server"
  project_path: "/home/user/project"
  user: "deploy"

validation:
  run_tests: true
  test_command: "python -m pytest -x"
  check_files_exist: true

paths:
  queue: ".agents/queue"
  results: ".agents/results"
  state: ".agents/state"
  reports: ".agents/reports"
  prompts: ".agents/prompts"
  schemas: ".agents/schemas"
"""


@pytest.fixture
def config_file(tmp_path):
    """Create a temporary config file."""
    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir()
    config_path = agents_dir / "config.yaml"
    config_path.write_text(SAMPLE_CONFIG, encoding="utf-8")
    return config_path


class TestProjectConfig:
    """Tests for ProjectConfig loading."""

    def test_load_from_file(self, config_file):
        config = ProjectConfig.load(str(config_file))
        assert config.project_name == "Test Project"
        assert config.package_name == "9ake-kiro-agents"

    def test_agents_parsed(self, config_file):
        config = ProjectConfig.load(str(config_file))
        assert "claude" in config.agents
        assert "codex" in config.agents
        assert config.agents["claude"].command == "claude"
        assert config.agents["codex"].command == "codex"

    def test_claude_config(self, config_file):
        config = ProjectConfig.load(str(config_file))
        claude = config.agents["claude"]
        assert claude.name == "claude"
        assert "-p" in claude.flags
        assert "--dangerously-skip-permissions" in claude.flags
        assert claude.max_turns == 10
        assert claude.max_budget_usd == 5.0
        assert "reasoning" in claude.task_types
        assert claude.fallback_to == "codex"

    def test_codex_config(self, config_file):
        config = ProjectConfig.load(str(config_file))
        codex = config.agents["codex"]
        assert codex.name == "codex"
        assert "-q" in codex.flags
        assert "--approval-mode" in codex.flags
        assert "implementation" in codex.task_types
        assert codex.fallback_to == "claude"

    def test_dispatch_config(self, config_file):
        config = ProjectConfig.load(str(config_file))
        assert config.dispatch.retry_max == 3
        assert config.dispatch.retry_backoff_seconds == [5, 15, 30]
        assert config.dispatch.fallback_enabled is True
        assert config.dispatch.parallel_max == 4
        assert config.dispatch.default_timeout_seconds == 600

    def test_ssh_config(self, config_file):
        config = ProjectConfig.load(str(config_file))
        assert config.ssh.host == "my-server"
        assert config.ssh.project_path == "/home/user/project"
        assert config.ssh.user == "deploy"
        assert config.ssh.ssh_target == "deploy@my-server"

    def test_validation_config(self, config_file):
        config = ProjectConfig.load(str(config_file))
        assert config.validation.run_tests is True
        assert config.validation.test_command == "python -m pytest -x"
        assert config.validation.check_files_exist is True

    def test_paths_config(self, config_file):
        config = ProjectConfig.load(str(config_file))
        assert config.paths.queue == ".agents/queue"
        assert config.paths.results == ".agents/results"

    def test_get_agent_for_task_type(self, config_file):
        config = ProjectConfig.load(str(config_file))
        agent = config.get_agent_for_task_type("implementation")
        assert agent is not None
        assert agent.name == "codex"

        agent = config.get_agent_for_task_type("reasoning")
        assert agent is not None
        assert agent.name == "claude"

    def test_get_agent_for_unknown_type(self, config_file):
        config = ProjectConfig.load(str(config_file))
        agent = config.get_agent_for_task_type("unknown_type")
        assert agent is None

    def test_get_fallback_agent(self, config_file):
        config = ProjectConfig.load(str(config_file))
        fallback = config.get_fallback_agent("claude")
        assert fallback is not None
        assert fallback.name == "codex"

        fallback = config.get_fallback_agent("codex")
        assert fallback is not None
        assert fallback.name == "claude"

    def test_get_fallback_for_unknown_agent(self, config_file):
        config = ProjectConfig.load(str(config_file))
        fallback = config.get_fallback_agent("unknown")
        assert fallback is None

    def test_missing_config_raises(self):
        with pytest.raises(FileNotFoundError):
            ProjectConfig.load("/nonexistent/path/config.yaml")

    def test_auto_discovery(self, tmp_path, monkeypatch):
        """Test that config is discovered by searching upward from CWD."""
        agents_dir = tmp_path / ".agents"
        agents_dir.mkdir()
        config_path = agents_dir / "config.yaml"
        config_path.write_text(SAMPLE_CONFIG, encoding="utf-8")

        # Change CWD to a subdirectory
        sub_dir = tmp_path / "src" / "deep"
        sub_dir.mkdir(parents=True)
        monkeypatch.chdir(sub_dir)

        config = ProjectConfig.load()
        assert config.project_name == "Test Project"

    def test_discovery_fails_when_no_config(self, tmp_path, monkeypatch):
        """Test that discovery raises when no config exists anywhere."""
        monkeypatch.chdir(tmp_path)
        with pytest.raises(FileNotFoundError, match="No .agents/config.yaml found"):
            ProjectConfig.load()

    def test_config_path_stored(self, config_file):
        config = ProjectConfig.load(str(config_file))
        assert config.config_path is not None
        assert config.config_path.name == "config.yaml"

    def test_project_root_derived(self, config_file):
        config = ProjectConfig.load(str(config_file))
        # project_root should be parent of .agents/
        assert config.project_root is not None
        assert config.project_root.name != ".agents"


class TestAgentConfig:
    """Tests for AgentConfig."""

    def test_from_dict_minimal(self):
        agent = AgentConfig.from_dict("test", {"command": "test-cli"})
        assert agent.name == "test"
        assert agent.command == "test-cli"
        assert agent.flags == []
        assert agent.task_types == []
        assert agent.fallback_to is None

    def test_from_dict_full(self):
        data = {
            "command": "claude",
            "flags": ["-p"],
            "system_prompt": "prompt.md",
            "max_turns": 5,
            "max_budget_usd": 2.0,
            "task_types": ["reasoning"],
            "fallback_to": "codex",
        }
        agent = AgentConfig.from_dict("claude", data)
        assert agent.max_turns == 5
        assert agent.max_budget_usd == 2.0
        assert agent.system_prompt == "prompt.md"


class TestDispatchConfig:
    """Tests for DispatchConfig defaults."""

    def test_defaults(self):
        config = DispatchConfig.from_dict({})
        assert config.retry_max == 2
        assert config.retry_backoff_seconds == [5, 15]
        assert config.fallback_enabled is True
        assert config.parallel_max == 2
        assert config.default_timeout_seconds == 300


class TestSSHConfig:
    """Tests for SSHConfig."""

    def test_ssh_target_with_user(self):
        ssh = SSHConfig(host="server", user="admin")
        assert ssh.ssh_target == "admin@server"

    def test_ssh_target_without_user(self):
        ssh = SSHConfig(host="server", user="")
        assert ssh.ssh_target == "server"
