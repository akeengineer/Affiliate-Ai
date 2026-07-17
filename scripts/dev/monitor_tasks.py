#!/usr/bin/env python3
"""Show Codex task state from matching branches and Git history.

Ref: codex/tasks/104-agent-task-monitoring.md
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


STATUS_DONE = "DONE"
STATUS_IN_PROGRESS = "IN PROGRESS"
STATUS_PENDING = "PENDING"
DEFAULT_REPO_ROOT = next(
    (
        parent
        for parent in Path(__file__).resolve().parents
        if (parent / ".git").exists()
    ),
    Path("/home/ubuntu/Affiliate-Ai"),
)


@dataclass(frozen=True)
class Task:
    task_id: str
    title: str
    path: Path


@dataclass(frozen=True)
class TaskState:
    task: Task
    status: str
    branch: str = "-"
    commit: str = "-"


def run_git(repo_root: Path, *args: str, check: bool = True) -> str:
    """Run a read-only Git command and return stripped stdout."""
    completed = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if check and completed.returncode != 0:
        detail = completed.stderr.strip() or "git command failed"
        raise RuntimeError(detail)
    return completed.stdout.strip()


def read_tasks(tasks_dir: Path) -> list[Task]:
    """Read task IDs and first-level headings from Markdown task files."""
    tasks: list[Task] = []
    for path in sorted(tasks_dir.glob("*.md")):
        title = path.stem
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
        except OSError:
            title = "(unreadable task file)"
        tasks.append(Task(task_id=path.stem, title=title, path=path))
    return tasks


def task_slug(task_id: str) -> str:
    """Drop the numeric queue prefix used by codex/tasks filenames."""
    return re.sub(r"^\d+-", "", task_id).lower()


def branch_slug(branch: str) -> str:
    """Return the final branch path component for local or remote refs."""
    return branch.rstrip("/").rsplit("/", 1)[-1].lower()


def matching_branch(task: Task, branches: Sequence[str], current_branch: str) -> str | None:
    """Find the best exact/suffix branch match for a task."""
    slug = task_slug(task.task_id)
    matches: list[tuple[int, str]] = []
    for branch in branches:
        if branch.endswith("/HEAD"):
            continue
        candidate = branch_slug(branch)
        if candidate == slug:
            score = 0
        elif len(slug) >= 8 and candidate.endswith(f"-{slug}"):
            score = 1
        elif len(candidate) >= 8 and slug.endswith(f"-{candidate}"):
            score = 2
        else:
            continue
        if branch == current_branch:
            score -= 10
        elif branch.startswith("origin/"):
            score += 5
        matches.append((score, branch))
    return min(matches)[1] if matches else None


def default_branch(repo_root: Path) -> str | None:
    """Select the best available stable branch for task commit comparisons."""
    for candidate in ("origin/main", "main", "origin/master", "master"):
        if run_git(repo_root, "rev-parse", "--verify", "--quiet", candidate, check=False):
            return candidate
    return None


def task_commit_evidence(
    repo_root: Path,
    task: Task,
    branch: str,
    base_branch: str | None,
) -> str | None:
    """Return a commit that changes the task file on its matching branch."""
    relative_path = task.path.relative_to(repo_root).as_posix()
    ranges: list[str] = []
    if base_branch and base_branch != branch:
        ranges.append(f"{base_branch}..{branch}")
    ranges.append(branch)

    for revision in ranges:
        evidence = run_git(
            repo_root,
            "log",
            "-1",
            "--format=%h",
            revision,
            "--",
            relative_path,
            check=False,
        )
        if not evidence:
            continue
        if revision == branch and base_branch:
            branch_tip = run_git(repo_root, "rev-parse", branch, check=False)
            base_tip = run_git(repo_root, "rev-parse", base_branch, check=False)
            if branch_tip == base_tip:
                continue
            merged = subprocess.run(
                [
                    "git",
                    "-C",
                    str(repo_root),
                    "merge-base",
                    "--is-ancestor",
                    branch,
                    base_branch,
                ],
                check=False,
                capture_output=True,
            ).returncode == 0
            if not merged:
                continue
        return evidence.splitlines()[0]
    return None


def collect_states(repo_root: Path, tasks: Sequence[Task]) -> list[TaskState]:
    """Classify tasks from branch presence and task-file commit evidence."""
    refs = run_git(
        repo_root,
        "for-each-ref",
        "--format=%(refname:short)",
        "refs/heads",
        "refs/remotes",
    ).splitlines()
    current = run_git(repo_root, "branch", "--show-current", check=False)
    base = default_branch(repo_root)
    states: list[TaskState] = []

    for task in tasks:
        branch = matching_branch(task, refs, current)
        if branch is None:
            states.append(TaskState(task=task, status=STATUS_PENDING))
            continue
        evidence = task_commit_evidence(repo_root, task, branch, base)
        if evidence:
            states.append(
                TaskState(task=task, status=STATUS_DONE, branch=branch, commit=evidence)
            )
        else:
            states.append(TaskState(task=task, status=STATUS_IN_PROGRESS, branch=branch))
    return states


def truncate(value: str, width: int) -> str:
    if len(value) <= width:
        return value
    return value[: max(1, width - 1)] + "…"


def colorize_status(status: str, enabled: bool) -> str:
    if not enabled:
        return status
    colors = {
        STATUS_DONE: "\033[32m",
        STATUS_IN_PROGRESS: "\033[33m",
        STATUS_PENDING: "\033[2m",
    }
    return f"{colors[status.strip()]}{status}\033[0m"


def format_table(states: Sequence[TaskState], color: bool) -> str:
    """Render a fixed-width table without third-party dependencies."""
    widths = {"task": 42, "status": 11, "branch": 48, "commit": 8, "title": 54}
    header = (
        f"{'TASK':<{widths['task']}}  "
        f"{'STATUS':<{widths['status']}}  "
        f"{'BRANCH':<{widths['branch']}}  "
        f"{'COMMIT':<{widths['commit']}}  TITLE"
    )
    divider = "-" * len(header)
    lines = [header, divider]
    for state in states:
        plain_status = f"{state.status:<{widths['status']}}"
        displayed_status = colorize_status(plain_status, color)
        lines.append(
            f"{truncate(state.task.task_id, widths['task']):<{widths['task']}}  "
            f"{displayed_status}  "
            f"{truncate(state.branch, widths['branch']):<{widths['branch']}}  "
            f"{state.commit:<{widths['commit']}}  "
            f"{truncate(state.task.title, widths['title'])}"
        )
    if not states:
        lines.append("(no tasks match this view)")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=DEFAULT_REPO_ROOT,
        help="repository root (default: inferred from script path)",
    )
    parser.add_argument(
        "--active-only",
        action="store_true",
        help="show only in-progress tasks; the summary still counts all tasks",
    )
    parser.add_argument("--no-color", action="store_true", help="disable ANSI colors")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = args.repo_root.resolve()
    tasks_dir = repo_root / "codex" / "tasks"
    if not tasks_dir.is_dir():
        print(f"error: task directory not found: {tasks_dir}", file=sys.stderr)
        return 2

    try:
        states = collect_states(repo_root, read_tasks(tasks_dir))
    except (OSError, RuntimeError) as exc:
        print(f"error: unable to inspect tasks: {exc}", file=sys.stderr)
        return 1

    visible = (
        [state for state in states if state.status == STATUS_IN_PROGRESS]
        if args.active_only
        else states
    )
    color = not args.no_color and (
        bool(os.environ.get("FORCE_COLOR"))
        or (sys.stdout.isatty() and not os.environ.get("NO_COLOR"))
    )
    print(format_table(visible, color=color))

    counts = {
        status: sum(state.status == status for state in states)
        for status in (STATUS_DONE, STATUS_IN_PROGRESS, STATUS_PENDING)
    }
    print(
        "Summary: "
        f"{counts[STATUS_DONE]} done, "
        f"{counts[STATUS_IN_PROGRESS]} in progress, "
        f"{counts[STATUS_PENDING]} pending"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
