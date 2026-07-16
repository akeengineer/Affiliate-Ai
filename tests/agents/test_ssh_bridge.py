"""Tests for the SSH Bridge."""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest
import yaml

from scripts.agents.core.models.config import ProjectConfig, SSHConfig
from scripts.agents.core.ssh_bridge import RemoteResult, SSHBridge


MINIMAL_CONFIG = {
    "project_name": "Test",
    "package_name": "9ake-kiro-agents",
    "agents": {
        "codex": {"command": "codex", "flags": ["-q"], "task_types": ["implementation"]},
    },
    "dispatch": {"retry_max": 2, "parallel_max": 2},
    "ssh": {
        "host": "god-of-ai",
        "project_path": "/home/ubuntu/Affiliate-Ai",
        "user": "ubuntu",
    },
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
def bridge(config):
    return SSHBridge(config)


class TestSSHCommandBuilding:
    """Tests for SSH/SCP command construction."""

    def test_ssh_target(self, bridge):
        assert bridge.ssh_target == "ubuntu@god-of-ai"

    def test_build_ssh_command(self, bridge):
        cmd = bridge._build_ssh_command("ls -la")
        assert cmd == ["ssh", "ubuntu@god-of-ai", "ls -la"]

    def test_build_ssh_command_with_options(self, bridge):
        cmd = bridge._build_ssh_command("ls", options=["-o", "StrictHostKeyChecking=no"])
        assert cmd == ["ssh", "-o", "StrictHostKeyChecking=no", "ubuntu@god-of-ai", "ls"]

    def test_build_scp_push_command(self, bridge):
        cmd = bridge._build_scp_push_command("/local/file.json", "/remote/dir/")
        assert cmd == ["scp", "/local/file.json", "ubuntu@god-of-ai:/remote/dir/"]

    def test_build_scp_push_recursive(self, bridge):
        cmd = bridge._build_scp_push_command("/local/dir", "/remote/dir/", recursive=True)
        assert cmd == ["scp", "-r", "/local/dir", "ubuntu@god-of-ai:/remote/dir/"]

    def test_build_scp_pull_command(self, bridge):
        cmd = bridge._build_scp_pull_command("/remote/file.json", "/local/dir/")
        assert cmd == ["scp", "ubuntu@god-of-ai:/remote/file.json", "/local/dir/"]

    def test_build_scp_pull_recursive(self, bridge):
        cmd = bridge._build_scp_pull_command("/remote/dir", "/local/dir/", recursive=True)
        assert cmd == ["scp", "-r", "ubuntu@god-of-ai:/remote/dir", "/local/dir/"]

    def test_host_only_target(self, config):
        """Test with no user configured."""
        config.ssh.user = ""
        bridge = SSHBridge(config)
        assert bridge.ssh_target == "god-of-ai"

    def test_remote_project_path(self, bridge):
        assert bridge.remote_project_path == "/home/ubuntu/Affiliate-Ai"


class TestRunRemote:
    """Tests for remote command execution."""

    @patch("scripts.agents.core.ssh_bridge.subprocess.run")
    def test_successful_command(self, mock_run, bridge):
        mock_run.return_value = MagicMock(
            stdout="Hello from EC2\n",
            stderr="",
            returncode=0,
        )

        result = bridge.run_remote("echo Hello from EC2")
        assert result.success
        assert result.stdout == "Hello from EC2\n"
        mock_run.assert_called_once()

    @patch("scripts.agents.core.ssh_bridge.subprocess.run")
    def test_failed_command(self, mock_run, bridge):
        mock_run.return_value = MagicMock(
            stdout="",
            stderr="Permission denied",
            returncode=255,
        )

        result = bridge.run_remote("restricted-command")
        assert not result.success
        assert result.returncode == 255
        assert "Permission denied" in result.stderr

    @patch("scripts.agents.core.ssh_bridge.subprocess.run")
    def test_timeout(self, mock_run, bridge):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="ssh", timeout=120)

        result = bridge.run_remote("long-running-command")
        assert not result.success
        assert result.returncode == -1
        assert "timed out" in result.stderr

    @patch("scripts.agents.core.ssh_bridge.subprocess.run")
    def test_ssh_not_found(self, mock_run, bridge):
        mock_run.side_effect = FileNotFoundError("ssh not found")

        result = bridge.run_remote("any-command")
        assert not result.success
        assert result.returncode == -2
        assert "not found" in result.stderr

    @patch("scripts.agents.core.ssh_bridge.subprocess.run")
    def test_custom_timeout(self, mock_run, bridge):
        mock_run.return_value = MagicMock(stdout="OK", stderr="", returncode=0)

        bridge.run_remote("cmd", timeout=30)
        called_kwargs = mock_run.call_args[1]
        assert called_kwargs["timeout"] == 30


class TestPushFiles:
    """Tests for pushing files to remote."""

    @patch("scripts.agents.core.ssh_bridge.subprocess.run")
    def test_push_single_file(self, mock_run, bridge, project_dir):
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)

        task_file = project_dir / "task.json"
        task_file.write_text("{}", encoding="utf-8")

        result = bridge.push_files([str(task_file)])
        assert result.success
        assert mock_run.called

    @patch("scripts.agents.core.ssh_bridge.subprocess.run")
    def test_push_multiple_files(self, mock_run, bridge, project_dir):
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)

        files = []
        for i in range(3):
            f = project_dir / f"file{i}.json"
            f.write_text("{}", encoding="utf-8")
            files.append(str(f))

        result = bridge.push_files(files)
        assert result.success
        assert mock_run.call_count == 3

    @patch("scripts.agents.core.ssh_bridge.subprocess.run")
    def test_push_failure(self, mock_run, bridge, project_dir):
        mock_run.return_value = MagicMock(
            stdout="", stderr="No such file", returncode=1
        )

        task_file = project_dir / "task.json"
        task_file.write_text("{}", encoding="utf-8")

        result = bridge.push_files([str(task_file)])
        assert not result.success
        assert "Failed to push" in result.stderr

    @patch("scripts.agents.core.ssh_bridge.subprocess.run")
    def test_push_to_custom_remote_dir(self, mock_run, bridge, project_dir):
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)

        task_file = project_dir / "task.json"
        task_file.write_text("{}", encoding="utf-8")

        bridge.push_files([str(task_file)], remote_dir="/custom/path/")
        cmd = mock_run.call_args[0][0]
        assert "ubuntu@god-of-ai:/custom/path/" in cmd[-1]


class TestPullFiles:
    """Tests for pulling files from remote."""

    @patch("scripts.agents.core.ssh_bridge.subprocess.run")
    def test_pull_single_file(self, mock_run, bridge):
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)

        result = bridge.pull_files(["/remote/result.json"])
        assert result.success
        assert mock_run.called

    @patch("scripts.agents.core.ssh_bridge.subprocess.run")
    def test_pull_failure(self, mock_run, bridge):
        mock_run.return_value = MagicMock(
            stdout="", stderr="No such file", returncode=1
        )

        result = bridge.pull_files(["/remote/missing.json"])
        assert not result.success
        assert "Failed to pull" in result.stderr


class TestDispatchRemote:
    """Tests for the full remote dispatch cycle."""

    @patch("scripts.agents.core.ssh_bridge.subprocess.run")
    def test_task_file_not_found(self, mock_run, bridge):
        result = bridge.dispatch_remote("/nonexistent/task.json")
        assert not result.success
        assert result.returncode == -3
        assert "not found" in result.stderr

    @patch("scripts.agents.core.ssh_bridge.subprocess.run")
    def test_full_cycle_success(self, mock_run, bridge, project_dir):
        # All subprocess calls succeed
        mock_run.return_value = MagicMock(stdout="Dispatched OK", stderr="", returncode=0)

        task_file = project_dir / ".agents" / "queue" / "test-task-id.json"
        task_file.write_text('{"id": "test-task-id"}', encoding="utf-8")

        result = bridge.dispatch_remote(str(task_file))
        assert result.success
        # Should have called: scp push, ssh dispatch, scp pull
        assert mock_run.call_count == 3

    @patch("scripts.agents.core.ssh_bridge.subprocess.run")
    def test_push_fails_aborts(self, mock_run, bridge, project_dir):
        # First call (push) fails
        mock_run.return_value = MagicMock(stdout="", stderr="Connection refused", returncode=1)

        task_file = project_dir / ".agents" / "queue" / "test-id.json"
        task_file.write_text('{}', encoding="utf-8")

        result = bridge.dispatch_remote(str(task_file))
        assert not result.success
        assert "Failed to push" in result.stderr


class TestCheckRemoteStatus:
    """Tests for remote status checking."""

    @patch("scripts.agents.core.ssh_bridge.subprocess.run")
    def test_check_status_success(self, mock_run, bridge):
        mock_run.return_value = MagicMock(
            stdout="SSH OK\nProject dir OK\nPython 3.11.9\nclaude OK\ncodex OK\n",
            stderr="",
            returncode=0,
        )

        result = bridge.check_remote_status()
        assert result.success
        assert "SSH OK" in result.stdout

    @patch("scripts.agents.core.ssh_bridge.subprocess.run")
    def test_check_status_unreachable(self, mock_run, bridge):
        mock_run.return_value = MagicMock(
            stdout="",
            stderr="Connection timed out",
            returncode=255,
        )

        result = bridge.check_remote_status()
        assert not result.success


class TestRemoteResult:
    """Tests for the RemoteResult dataclass."""

    def test_success_property(self):
        assert RemoteResult(stdout="ok", stderr="", returncode=0).success
        assert not RemoteResult(stdout="", stderr="err", returncode=1).success
        assert not RemoteResult(stdout="", stderr="", returncode=-1).success
