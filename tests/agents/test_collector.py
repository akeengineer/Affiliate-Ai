"""Tests for the Result Collector."""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from scripts.agents.core.collector import Collector
from scripts.agents.core.dispatcher import DispatchCommand
from scripts.agents.core.models.config import AgentConfig, ProjectConfig
from scripts.agents.core.models.result import AgentResult, ResultStatus
from scripts.agents.core.models.task import Task, TaskStatus, TaskType


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
    "dispatch": {"retry_max": 2, "parallel_max": 2},
    "ssh": {"host": "test"},
    "validation": {
        "run_tests": True,
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
    """Create a temporary project directory."""
    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir()
    for sub in ["queue", "results", "state", "reports"]:
        (agents_dir / sub).mkdir()
    config_path = agents_dir / "config.yaml"
    config_path.write_text(yaml.dump(MINIMAL_CONFIG), encoding="utf-8")
    return tmp_path


@pytest.fixture
def config(project_dir):
    """Load config from temp project."""
    return ProjectConfig.load(str(project_dir / ".agents" / "config.yaml"))


@pytest.fixture
def collector(config):
    """Create a Collector instance."""
    return Collector(config)


def make_dispatch_cmd(task=None, agent_name="codex"):
    """Create a mock DispatchCommand."""
    if task is None:
        task = Task.create(
            title="Test task",
            task_type="implementation",
            prompt="Build something",
        )
    agent = AgentConfig(
        name=agent_name,
        command=agent_name,
        flags=["-q"],
        task_types=["implementation"],
    )
    return DispatchCommand(
        task=task,
        agent=agent,
        command=[agent_name, "-q", "prompt"],
        prompt="prompt",
    )


class TestParseAgentOutput:
    """Tests for parsing agent stdout."""

    def test_parse_valid_json(self, collector, project_dir):
        cmd = make_dispatch_cmd()
        # Create the files so validation passes
        (project_dir / "main.py").write_text("# modified", encoding="utf-8")
        (project_dir / "test_main.py").write_text("# created", encoding="utf-8")

        stdout = json.dumps({
            "status": "success",
            "summary": "Implemented the feature",
            "files_modified": ["main.py"],
            "files_created": ["test_main.py"],
            "tests_run": "pytest",
            "tests_passed": True,
            "errors": [],
            "next_steps": ["Deploy"],
        })
        process = subprocess.CompletedProcess(args=[], returncode=0, stdout=stdout, stderr="")

        result = collector.collect(cmd, process, duration_seconds=5.0)
        assert result.status == ResultStatus.SUCCESS
        assert result.summary == "Implemented the feature"
        assert result.files_modified == ["main.py"]
        assert result.files_created == ["test_main.py"]
        assert result.tests_passed is True
        assert result.duration_seconds == 5.0

    def test_parse_json_embedded_in_text(self, collector):
        """Agent might output text before/after JSON."""
        cmd = make_dispatch_cmd()
        stdout = 'Some preamble\n{"status": "success", "summary": "Done"}\nSome epilogue'
        process = subprocess.CompletedProcess(args=[], returncode=0, stdout=stdout, stderr="")

        result = collector.collect(cmd, process)
        assert result.status == ResultStatus.SUCCESS
        assert result.summary == "Done"

    def test_parse_non_json_output_returns_partial(self, collector):
        """Non-JSON output should result in 'partial' status."""
        cmd = make_dispatch_cmd()
        stdout = "I did some work but forgot to return JSON"
        process = subprocess.CompletedProcess(args=[], returncode=0, stdout=stdout, stderr="")

        result = collector.collect(cmd, process)
        assert result.status == ResultStatus.PARTIAL
        assert "not valid JSON" in result.errors[0]
        assert result.raw_output == stdout

    def test_parse_empty_output(self, collector):
        """Empty stdout should result in partial."""
        cmd = make_dispatch_cmd()
        process = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")

        result = collector.collect(cmd, process)
        assert result.status == ResultStatus.PARTIAL

    def test_parse_fail_status(self, collector):
        """Agent can explicitly report failure."""
        cmd = make_dispatch_cmd()
        stdout = json.dumps({
            "status": "fail",
            "summary": "Could not find the file",
            "errors": ["FileNotFoundError: input.md"],
        })
        process = subprocess.CompletedProcess(args=[], returncode=0, stdout=stdout, stderr="")

        result = collector.collect(cmd, process)
        assert result.status == ResultStatus.FAIL
        assert "Could not find the file" in result.summary
        assert cmd.task.status == TaskStatus.FAILED


class TestTimeoutHandling:
    """Tests for timeout scenarios."""

    def test_timeout_creates_timeout_result(self, collector):
        cmd = make_dispatch_cmd()
        process = subprocess.CompletedProcess(
            args=[],
            returncode=-1,
            stdout="",
            stderr="TIMEOUT: Task exceeded 300s limit",
        )

        result = collector.collect(cmd, process, duration_seconds=300.0)
        assert result.status == ResultStatus.TIMEOUT
        assert "timed out" in result.summary
        assert cmd.task.status == TaskStatus.FAILED


class TestNonZeroExit:
    """Tests for non-zero exit code handling."""

    def test_nonzero_exit_creates_fail_result(self, collector):
        cmd = make_dispatch_cmd()
        process = subprocess.CompletedProcess(
            args=[],
            returncode=1,
            stdout="",
            stderr="Error: something went wrong",
        )

        result = collector.collect(cmd, process)
        assert result.status == ResultStatus.FAIL
        assert "exited with code 1" in result.summary
        assert "something went wrong" in result.errors[0]

    def test_command_not_found_exit_127(self, collector):
        cmd = make_dispatch_cmd()
        process = subprocess.CompletedProcess(
            args=[],
            returncode=127,
            stdout="",
            stderr="command not found: codex",
        )

        result = collector.collect(cmd, process)
        assert result.status == ResultStatus.FAIL
        assert result.errors[0] == "command not found: codex"


class TestValidation:
    """Tests for result validation."""

    def test_validates_expected_outputs_exist(self, collector, project_dir):
        task = Task.create(
            title="With outputs",
            task_type="implementation",
            prompt="Create a file",
            expected_outputs=["nonexistent.py"],
        )
        cmd = make_dispatch_cmd(task=task)
        stdout = json.dumps({"status": "success", "summary": "Created file"})
        process = subprocess.CompletedProcess(args=[], returncode=0, stdout=stdout, stderr="")

        result = collector.collect(cmd, process)
        # Should be partial because expected file doesn't exist
        assert result.status == ResultStatus.PARTIAL
        assert any("not found" in e for e in result.errors)

    def test_validates_created_files_exist(self, collector, project_dir):
        cmd = make_dispatch_cmd()
        stdout = json.dumps({
            "status": "success",
            "summary": "Created files",
            "files_created": ["does_not_exist.py"],
        })
        process = subprocess.CompletedProcess(args=[], returncode=0, stdout=stdout, stderr="")

        result = collector.collect(cmd, process)
        assert result.status == ResultStatus.PARTIAL
        assert any("Claimed created file not found" in e for e in result.errors)

    def test_validation_passes_when_files_exist(self, collector, project_dir):
        # Create the expected file
        expected_file = project_dir / "output.py"
        expected_file.write_text("# output", encoding="utf-8")

        task = Task.create(
            title="With real output",
            task_type="implementation",
            prompt="Create output.py",
            expected_outputs=["output.py"],
        )
        cmd = make_dispatch_cmd(task=task)
        stdout = json.dumps({
            "status": "success",
            "summary": "Created output.py",
            "files_created": ["output.py"],
        })
        process = subprocess.CompletedProcess(args=[], returncode=0, stdout=stdout, stderr="")

        result = collector.collect(cmd, process)
        assert result.status == ResultStatus.SUCCESS
        assert result.errors == []


class TestPersistence:
    """Tests for saving and loading results."""

    def test_result_saved_to_results_dir(self, collector, project_dir):
        cmd = make_dispatch_cmd()
        stdout = json.dumps({"status": "success", "summary": "OK"})
        process = subprocess.CompletedProcess(args=[], returncode=0, stdout=stdout, stderr="")

        result = collector.collect(cmd, process)

        result_path = project_dir / ".agents" / "results" / f"{cmd.task.id}.json"
        assert result_path.exists()

    def test_task_state_saved(self, collector, project_dir):
        cmd = make_dispatch_cmd()
        stdout = json.dumps({"status": "success", "summary": "OK"})
        process = subprocess.CompletedProcess(args=[], returncode=0, stdout=stdout, stderr="")

        collector.collect(cmd, process)

        state_path = project_dir / ".agents" / "state" / f"{cmd.task.id}.json"
        assert state_path.exists()
        state_data = json.loads(state_path.read_text(encoding="utf-8"))
        assert state_data["status"] == "completed"

    def test_load_result_by_id(self, collector, project_dir):
        cmd = make_dispatch_cmd()
        stdout = json.dumps({"status": "success", "summary": "Loaded"})
        process = subprocess.CompletedProcess(args=[], returncode=0, stdout=stdout, stderr="")

        result = collector.collect(cmd, process)
        loaded = collector.load_result(cmd.task.id)
        assert loaded is not None
        assert loaded.task_id == result.task_id
        assert loaded.summary == "Loaded"

    def test_load_result_not_found(self, collector):
        loaded = collector.load_result("nonexistent-id")
        assert loaded is None

    def test_load_all_results(self, collector, project_dir):
        # Create two results
        for i in range(2):
            cmd = make_dispatch_cmd()
            stdout = json.dumps({"status": "success", "summary": f"Task {i}"})
            process = subprocess.CompletedProcess(args=[], returncode=0, stdout=stdout, stderr="")
            collector.collect(cmd, process)

        all_results = collector.load_all_results()
        assert len(all_results) == 2


class TestAttemptAndFallback:
    """Tests for attempt tracking and fallback flags."""

    def test_attempt_number_stored(self, collector):
        cmd = make_dispatch_cmd()
        stdout = json.dumps({"status": "success", "summary": "Retry succeeded"})
        process = subprocess.CompletedProcess(args=[], returncode=0, stdout=stdout, stderr="")

        result = collector.collect(cmd, process, attempt=3)
        assert result.attempt == 3

    def test_fallback_flag_stored(self, collector):
        cmd = make_dispatch_cmd()
        stdout = json.dumps({"status": "success", "summary": "Fallback worked"})
        process = subprocess.CompletedProcess(args=[], returncode=0, stdout=stdout, stderr="")

        result = collector.collect(cmd, process, is_fallback=True)
        assert result.is_fallback is True


class TestRunTests:
    """Tests for the test runner."""

    @patch("scripts.agents.core.collector.subprocess.run")
    def test_run_tests_success(self, mock_run, collector):
        mock_run.return_value = MagicMock(returncode=0, stdout="OK", stderr="")
        passed, output = collector.run_tests()
        assert passed is True

    @patch("scripts.agents.core.collector.subprocess.run")
    def test_run_tests_failure(self, mock_run, collector):
        mock_run.return_value = MagicMock(returncode=1, stdout="FAILED", stderr="errors")
        passed, output = collector.run_tests()
        assert passed is False

    @patch("scripts.agents.core.collector.subprocess.run")
    def test_run_tests_timeout(self, mock_run, collector):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="pytest", timeout=120)
        passed, output = collector.run_tests()
        assert passed is False
        assert "timed out" in output
