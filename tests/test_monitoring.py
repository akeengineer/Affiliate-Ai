"""Tests for EC2 monitoring tools.

Ref: codex/tasks/104-agent-task-monitoring.md
"""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parents[1]
MONITOR_AGENTS = REPO_ROOT / "scripts/dev/monitor_agents.sh"
MONITOR_TASKS = REPO_ROOT / "scripts/dev/monitor_tasks.py"
TASK_FILE = REPO_ROOT / "codex/tasks/104-agent-task-monitoring.md"


def load_monitor_tasks() -> ModuleType:
    spec = importlib.util.spec_from_file_location("monitor_tasks", MONITOR_TASKS)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def commit_all(repo: Path, message: str) -> None:
    git(repo, "add", ".")
    git(repo, "commit", "-m", message)


def test_required_files_exist_and_are_executable() -> None:
    for path in (MONITOR_AGENTS, MONITOR_TASKS, TASK_FILE):
        assert path.is_file()
    assert os.access(MONITOR_AGENTS, os.X_OK)
    assert os.access(MONITOR_TASKS, os.X_OK)


def test_task_slug_and_branch_matching() -> None:
    module = load_monitor_tasks()
    task = module.Task(
        task_id="104-agent-task-monitoring",
        title="Monitor",
        path=TASK_FILE,
    )
    branches = ["main", "origin/feature/agent-task-monitoring"]

    assert module.task_slug(task.task_id) == "agent-task-monitoring"
    assert (
        module.matching_branch(task, branches, "main")
        == "origin/feature/agent-task-monitoring"
    )


def test_collect_states_uses_branch_and_task_commit_evidence(tmp_path: Path) -> None:
    module = load_monitor_tasks()
    repo = tmp_path / "repo"
    tasks_dir = repo / "codex/tasks"
    tasks_dir.mkdir(parents=True)
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "Monitor Test")
    git(repo, "config", "user.email", "monitor@example.invalid")
    (repo / "README.md").write_text("test\n", encoding="utf-8")
    commit_all(repo, "initial")

    pending = tasks_dir / "001-pending-work.md"
    pending.write_text("# Pending Work\n", encoding="utf-8")
    commit_all(repo, "add pending task")

    git(repo, "switch", "-c", "feature/active-work")
    active = tasks_dir / "002-active-work.md"
    active.write_text("# Active Work\n", encoding="utf-8")

    states = {
        state.task.task_id: state
        for state in module.collect_states(repo, module.read_tasks(tasks_dir))
    }
    assert states["001-pending-work"].status == module.STATUS_PENDING
    assert states["002-active-work"].status == module.STATUS_IN_PROGRESS

    commit_all(repo, "implement active task")
    states = {
        state.task.task_id: state
        for state in module.collect_states(repo, module.read_tasks(tasks_dir))
    }
    assert states["002-active-work"].status == module.STATUS_DONE
    assert states["002-active-work"].commit != "-"


def test_task_monitor_cli_outputs_formatted_table() -> None:
    completed = subprocess.run(
        [str(MONITOR_TASKS), "--repo-root", str(REPO_ROOT), "--no-color"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "TASK" in completed.stdout
    assert "STATUS" in completed.stdout
    assert "BRANCH" in completed.stdout
    assert "104-agent-task-monitoring" in completed.stdout
    assert "Summary:" in completed.stdout
    assert "\033[" not in completed.stdout


def test_relocated_task_monitor_falls_back_to_project_root(tmp_path: Path) -> None:
    relocated_script = tmp_path / ".tasks_script.py"
    shutil.copyfile(MONITOR_TASKS, relocated_script)

    completed = subprocess.run(
        [sys.executable, str(relocated_script), "--active-only", "--no-color"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Summary:" in completed.stdout


def test_task_table_supports_color_output() -> None:
    module = load_monitor_tasks()
    state = module.TaskState(
        task=module.Task("001-example", "Example", TASK_FILE),
        status=module.STATUS_IN_PROGRESS,
        branch="feature/example",
    )

    output = module.format_table([state], color=True)

    assert "\033[33mIN PROGRESS" in output
    assert "feature/example" in output


def test_agent_monitor_help_documents_watch_interval() -> None:
    completed = subprocess.run(
        [str(MONITOR_AGENTS), "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "--watch" in completed.stdout
    assert "10 seconds" in completed.stdout


def test_agent_monitor_source_has_required_sections() -> None:
    source = MONITOR_AGENTS.read_text(encoding="utf-8")
    for section in (
        "AI Agent Processes",
        "Task Status",
        "tmux Sessions",
        "Recent Git Commits (Last 5)",
        "Recently Modified Files (Last 10 Minutes)",
        "Last Shopee Scraper Run",
        "Cloudflare WARP Proxy",
        "Disk and Memory",
    ):
        assert section in source
    assert 'SCRIPT_PATH="${BASH_SOURCE[0]}"' in source
    assert 'watch --color --interval 10 "bash $SCRIPT_PATH"' in source
